"""Analyze git diffs and extract changed files."""
from typing import Dict, List, Optional
import subprocess
import os


class DiffAnalyzer:
    """Parse git diffs and identify changed files."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_changed_files(self, base_branch: str, head_branch: str) -> Dict[str, List[str]]:
        """
        Get files changed between two branches.

        Returns:
            {
                'added': ['new_file.py'],
                'modified': ['existing_file.py'],
                'deleted': ['removed_file.py'],
                'renamed': [('old_name.py', 'new_name.py')]
            }
        """
        try:
            os.chdir(self.repo_path)

            # Get diff statistics
            result = subprocess.run(
                ['git', 'diff', '--name-status', f'{base_branch}...{head_branch}'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return {'added': [], 'modified': [], 'deleted': [], 'renamed': []}

            files = {
                'added': [],
                'modified': [],
                'deleted': [],
                'renamed': []
            }

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                parts = line.split('\t')
                status = parts[0]

                if status == 'A':  # Added
                    files['added'].append(parts[1])
                elif status == 'M':  # Modified
                    files['modified'].append(parts[1])
                elif status == 'D':  # Deleted
                    files['deleted'].append(parts[1])
                elif status == 'R':  # Renamed
                    files['renamed'].append((parts[1], parts[2]))

            return files
        except Exception as e:
            print(f"Error getting changed files: {e}")
            return {'added': [], 'modified': [], 'deleted': [], 'renamed': []}

    def get_file_diff(self, file_path: str, base_branch: str, head_branch: str) -> Optional[str]:
        """Get unified diff for a specific file."""
        try:
            os.chdir(self.repo_path)

            result = subprocess.run(
                ['git', 'diff', f'{base_branch}...{head_branch}', '--', file_path],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return result.stdout
            return None
        except Exception as e:
            print(f"Error getting file diff: {e}")
            return None

    def get_changed_lines(self, file_path: str, base_branch: str, head_branch: str) -> Dict[int, str]:
        """
        Get line numbers and content of changed lines.

        Returns:
            {
                5: '+new line content',
                10: '-removed line content',
                15: ' unchanged line'
            }
        """
        diff = self.get_file_diff(file_path, base_branch, head_branch)
        if not diff:
            return {}

        changed_lines = {}
        current_line = 0

        for line in diff.split('\n'):
            if line.startswith('@@'):
                # Extract line number from hunk header: @@ -10,5 +10,6 @@
                try:
                    parts = line.split(' ')
                    new_range = parts[2]  # +10,6
                    start_line = int(new_range.split(',')[0].lstrip('+'))
                    current_line = start_line
                except:
                    pass
            elif line.startswith('+') and not line.startswith('+++'):
                changed_lines[current_line] = line
                current_line += 1
            elif line.startswith('-') and not line.startswith('---'):
                changed_lines[current_line] = line
            elif not line.startswith(' '):
                pass
            else:
                current_line += 1

        return changed_lines

    def filter_files_by_language(self, files: List[str], languages: List[str] = None) -> Dict[str, List[str]]:
        """
        Filter files by supported languages.

        Args:
            files: List of file paths
            languages: Supported languages (py, js, sql, go, java, etc)

        Returns:
            {
                'python': ['file.py'],
                'javascript': ['file.js'],
                'sql': ['file.sql']
            }
        """
        if languages is None:
            languages = ['py', 'js', 'ts', 'jsx', 'tsx', 'sql']

        filtered = {
            'python': [],
            'javascript': [],
            'sql': [],
            'other': []
        }

        extension_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'javascript',
            'jsx': 'javascript',
            'tsx': 'javascript',
            'sql': 'sql'
        }

        for file_path in files:
            if not file_path:
                continue

            ext = file_path.split('.')[-1].lower() if '.' in file_path else 'unknown'
            lang = extension_map.get(ext, 'other')

            if lang != 'other':
                filtered[lang].append(file_path)
            elif ext in languages:
                filtered['other'].append(file_path)

        return filtered
