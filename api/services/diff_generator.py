"""
Diff Generator Service - Phase 4.2d
Generate diffs and manage git integration for code changes
"""

import subprocess
import difflib
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DiffSummary:
    """Summary of changes in a diff"""
    files_changed: int
    lines_added: int
    lines_removed: int
    insertions: int
    deletions: int


class DiffGenerator:
    """Generate and manage diffs for code changes"""

    def generate_diff(
        self, original: str, modified: str, file_path: str = "file.py"
    ) -> str:
        """
        Generate a unified diff between original and modified code.

        Args:
            original: Original code
            modified: Modified code
            file_path: File path for diff header

        Returns:
            Unified diff as string
        """
        try:
            original_lines = original.splitlines(keepends=True)
            modified_lines = modified.splitlines(keepends=True)

            diff = difflib.unified_diff(
                original_lines,
                modified_lines,
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm="",
            )

            return "\n".join(diff)

        except Exception as e:
            logger.error(f"Error generating diff: {e}")
            return ""

    def generate_diff_for_file(
        self, file_path: str
    ) -> str:
        """
        Generate diff for a modified file in git working directory.

        Args:
            file_path: Path to file (relative to repo root)

        Returns:
            Unified diff
        """
        try:
            result = subprocess.run(
                ["git", "diff", file_path],
                capture_output=True,
                timeout=10,
                text=True,
            )

            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Error getting git diff for {file_path}")
                return ""

        except subprocess.TimeoutExpired:
            logger.error("Git diff timed out")
            return ""
        except FileNotFoundError:
            logger.error("Git not available")
            return ""
        except Exception as e:
            logger.error(f"Error generating diff for file: {e}")
            return ""

    def get_diff_summary(self, diff: str) -> DiffSummary:
        """
        Extract summary statistics from a diff.

        Args:
            diff: Unified diff text

        Returns:
            DiffSummary with change statistics
        """
        try:
            lines_added = 0
            lines_removed = 0
            files_changed = 0

            for line in diff.split("\n"):
                if line.startswith("diff --git"):
                    files_changed += 1
                elif line.startswith("+") and not line.startswith("+++"):
                    lines_added += 1
                elif line.startswith("-") and not line.startswith("---"):
                    lines_removed += 1

            return DiffSummary(
                files_changed=max(1, files_changed),
                lines_added=lines_added,
                lines_removed=lines_removed,
                insertions=lines_added,
                deletions=lines_removed,
            )

        except Exception as e:
            logger.error(f"Error getting diff summary: {e}")
            return DiffSummary(
                files_changed=0,
                lines_added=0,
                lines_removed=0,
                insertions=0,
                deletions=0,
            )

    def format_diff_for_display(self, diff: str) -> str:
        """
        Format diff for web display with syntax highlighting markers.

        Args:
            diff: Unified diff

        Returns:
            Formatted diff with HTML-friendly markers
        """
        try:
            formatted_lines = []

            for line in diff.split("\n"):
                if line.startswith("+++") or line.startswith("---"):
                    formatted_lines.append(f"<diff-meta>{line}</diff-meta>")
                elif line.startswith("@@"):
                    formatted_lines.append(f"<diff-chunk>{line}</diff-chunk>")
                elif line.startswith("+"):
                    formatted_lines.append(f"<diff-add>{line}</diff-add>")
                elif line.startswith("-"):
                    formatted_lines.append(f"<diff-remove>{line}</diff-remove>")
                else:
                    formatted_lines.append(line)

            return "\n".join(formatted_lines)

        except Exception as e:
            logger.error(f"Error formatting diff: {e}")
            return diff

    def get_file_diff_stats(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed diff stats for a specific file.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file stats
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--numstat", file_path],
                capture_output=True,
                timeout=10,
                text=True,
            )

            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split()
                if len(parts) >= 3:
                    return {
                        "file": file_path,
                        "additions": int(parts[0]),
                        "deletions": int(parts[1]),
                        "status": "modified",
                    }

            return {
                "file": file_path,
                "additions": 0,
                "deletions": 0,
                "status": "unchanged",
            }

        except Exception as e:
            logger.error(f"Error getting file diff stats: {e}")
            return {
                "file": file_path,
                "error": str(e),
            }

    def stage_files(self, files: List[str]) -> bool:
        """
        Stage files for commit with git add.

        Args:
            files: List of file paths to stage

        Returns:
            True if staging successful
        """
        try:
            for file_path in files:
                result = subprocess.run(
                    ["git", "add", file_path],
                    capture_output=True,
                    timeout=10,
                )

                if result.returncode != 0:
                    logger.error(f"Failed to stage {file_path}")
                    return False

            logger.info(f"Staged {len(files)} files")
            return True

        except subprocess.TimeoutExpired:
            logger.error("Git add timed out")
            return False
        except FileNotFoundError:
            logger.error("Git not available")
            return False
        except Exception as e:
            logger.error(f"Error staging files: {e}")
            return False

    def unstage_files(self, files: List[str]) -> bool:
        """
        Unstage files with git reset.

        Args:
            files: List of file paths to unstage

        Returns:
            True if unstaging successful
        """
        try:
            for file_path in files:
                result = subprocess.run(
                    ["git", "reset", file_path],
                    capture_output=True,
                    timeout=10,
                )

                if result.returncode != 0:
                    logger.error(f"Failed to unstage {file_path}")
                    return False

            logger.info(f"Unstaged {len(files)} files")
            return True

        except subprocess.TimeoutExpired:
            logger.error("Git reset timed out")
            return False
        except FileNotFoundError:
            logger.error("Git not available")
            return False
        except Exception as e:
            logger.error(f"Error unstaging files: {e}")
            return False

    def get_staged_changes(self) -> str:
        """
        Get unified diff of staged changes.

        Returns:
            Unified diff of staged changes
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"],
                capture_output=True,
                timeout=10,
                text=True,
            )

            if result.returncode == 0:
                return result.stdout
            else:
                logger.error("Error getting staged changes")
                return ""

        except subprocess.TimeoutExpired:
            logger.error("Git diff cached timed out")
            return ""
        except FileNotFoundError:
            logger.error("Git not available")
            return ""
        except Exception as e:
            logger.error(f"Error getting staged changes: {e}")
            return ""

    def get_unstaged_changes(self) -> str:
        """
        Get unified diff of unstaged changes.

        Returns:
            Unified diff of unstaged changes
        """
        try:
            result = subprocess.run(
                ["git", "diff"],
                capture_output=True,
                timeout=10,
                text=True,
            )

            if result.returncode == 0:
                return result.stdout
            else:
                logger.error("Error getting unstaged changes")
                return ""

        except subprocess.TimeoutExpired:
            logger.error("Git diff timed out")
            return ""
        except FileNotFoundError:
            logger.error("Git not available")
            return ""
        except Exception as e:
            logger.error(f"Error getting unstaged changes: {e}")
            return ""

    def is_git_repo(self) -> bool:
        """
        Check if current directory is a git repository.

        Returns:
            True if in a git repo
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_current_branch(self) -> Optional[str]:
        """
        Get current git branch name.

        Returns:
            Branch name or None if not in repo
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                timeout=5,
                text=True,
            )

            if result.returncode == 0:
                return result.stdout.strip()
            return None

        except Exception:
            return None

    def has_changes(self) -> bool:
        """
        Check if there are any uncommitted changes.

        Returns:
            True if there are changes
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                timeout=10,
                text=True,
            )

            if result.returncode == 0:
                return len(result.stdout.strip()) > 0
            return False

        except Exception:
            return False


# Singleton instance
_diff_generator = None


def get_diff_generator() -> DiffGenerator:
    """Get or create DiffGenerator instance"""
    global _diff_generator
    if _diff_generator is None:
        _diff_generator = DiffGenerator()
    return _diff_generator
