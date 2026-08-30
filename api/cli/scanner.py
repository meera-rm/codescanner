"""CodePulse CLI scanner for repository scanning."""
import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any

# Add scanner path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scanner'))

try:
    from scanner import PythonScanner, JavaScriptScanner, SQLScanner
except ImportError:
    # Fallback for testing
    class PythonScanner:
        def scan_file(self, path):
            return []

    class JavaScriptScanner:
        def scan_file(self, path):
            return []

    class SQLScanner:
        def scan_file(self, path):
            return []


class RepositoryScanner:
    """Scan a repository for code quality issues."""

    def __init__(self, repository_path: str, ignore_patterns: List[str] = None):
        self.repository_path = repository_path
        self.ignore_patterns = ignore_patterns or [
            '__pycache__', '.venv', 'node_modules', 'venv', '.git',
            'site-packages', 'tests', 'fixtures', '.github', 'dist', 'build'
        ]
        self.findings = []

    def scan(self) -> Dict[str, Any]:
        """Scan the repository and return findings."""
        print(f"🔍 Scanning repository: {self.repository_path}")

        # Get all files
        all_files = self._get_files()
        print(f"📁 Found {len(all_files)} files to scan")

        # Group files by language
        files_by_language = self._group_by_language(all_files)

        # Scan Python files
        if files_by_language['python']:
            print(f"🐍 Scanning {len(files_by_language['python'])} Python files...")
            scanner = PythonScanner()
            for file_path in files_by_language['python']:
                try:
                    findings = scanner.scan_file(file_path)
                    for finding in findings:
                        # Convert finding to dict if needed
                        if hasattr(finding, '__dict__'):
                            finding_dict = finding.__dict__.copy()
                        else:
                            finding_dict = dict(finding)
                        finding_dict['file'] = file_path
                        self.findings.append(finding_dict)
                except Exception as e:
                    pass

        # Scan JavaScript files
        if files_by_language['javascript']:
            print(f"📜 Scanning {len(files_by_language['javascript'])} JavaScript files...")
            scanner = JavaScriptScanner()
            for file_path in files_by_language['javascript']:
                try:
                    findings = scanner.scan_file(file_path)
                    for finding in findings:
                        # Convert finding to dict if needed
                        if hasattr(finding, '__dict__'):
                            finding_dict = finding.__dict__.copy()
                        else:
                            finding_dict = dict(finding)
                        finding_dict['file'] = file_path
                        self.findings.append(finding_dict)
                except Exception as e:
                    pass

        # Scan SQL files
        if files_by_language['sql']:
            print(f"🗄️  Scanning {len(files_by_language['sql'])} SQL files...")
            scanner = SQLScanner()
            for file_path in files_by_language['sql']:
                try:
                    findings = scanner.scan_file(file_path)
                    for finding in findings:
                        # Convert finding to dict if needed
                        if hasattr(finding, '__dict__'):
                            finding_dict = finding.__dict__.copy()
                        else:
                            finding_dict = dict(finding)
                        finding_dict['file'] = file_path
                        self.findings.append(finding_dict)
                except Exception as e:
                    pass

        # Summarize findings
        summary = self._summarize()

        return {
            'status': 'completed',
            'repository': self.repository_path,
            'files_scanned': len(all_files),
            'files_by_language': {
                'python': len(files_by_language['python']),
                'javascript': len(files_by_language['javascript']),
                'sql': len(files_by_language['sql']),
                'other': len(files_by_language['other']),
            },
            'findings': self.findings,
            'summary': summary,
        }

    def _get_files(self) -> List[str]:
        """Get all non-ignored files in repository."""
        files = []
        for root, dirs, filenames in os.walk(self.repository_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]

            for filename in filenames:
                file_path = os.path.join(root, filename)
                # Skip ignored patterns
                if not any(pattern in file_path for pattern in self.ignore_patterns):
                    files.append(file_path)

        return files

    def _group_by_language(self, files: List[str]) -> Dict[str, List[str]]:
        """Group files by language."""
        grouped = {
            'python': [],
            'javascript': [],
            'sql': [],
            'other': [],
        }

        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.jsx': 'javascript',
            '.tsx': 'javascript',
            '.sql': 'sql',
        }

        for file_path in files:
            ext = Path(file_path).suffix.lower()
            language = extensions.get(ext, 'other')
            grouped[language].append(file_path)

        return grouped

    def _summarize(self) -> Dict[str, int]:
        """Summarize findings by severity."""
        summary = {
            'critical': 0,
            'error': 0,
            'warning': 0,
            'info': 0,
            'total': len(self.findings),
        }

        for finding in self.findings:
            severity = finding.get('severity', 'info').lower()
            if severity in summary:
                summary[severity] += 1

        return summary


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='CodePulse CLI Scanner'
    )
    parser.add_argument(
        '--repository',
        default='.',
        help='Path to repository to scan (default: current directory)'
    )
    parser.add_argument(
        '--output-format',
        default='json',
        choices=['json'],
        help='Output format (default: json)'
    )
    parser.add_argument(
        '--output-file',
        required=True,
        help='Output file path'
    )
    parser.add_argument(
        '--fail-on-critical',
        default='false',
        choices=['true', 'false'],
        help='Exit with code 1 if critical issues found (default: false)'
    )

    args = parser.parse_args()

    # Scan repository
    scanner = RepositoryScanner(args.repository)
    result = scanner.scan()

    # Write report
    with open(args.output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)

    # Print summary
    summary = result['summary']
    print(f"\n✅ Scan Complete!")
    print(f"   Critical: {summary['critical']}")
    print(f"   Error: {summary['error']}")
    print(f"   Warning: {summary['warning']}")
    print(f"   Total: {summary['total']}")

    # Exit with appropriate code
    if args.fail_on_critical == 'true' and summary['critical'] > 0:
        print(f"\n❌ Critical issues found - failing build")
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
