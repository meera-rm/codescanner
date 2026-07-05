"""
File Modifier Service - Phase 4.2
Applies real code modifications to source files based on agent suggestions
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModificationResult:
    """Result of a file modification attempt"""
    success: bool
    files_modified: List[str]
    files_failed: List[str]
    changes: Dict[str, Any]
    diff: Optional[str] = None
    validation_errors: Optional[List[str]] = None
    error_message: Optional[str] = None


class FileModifierService:
    """Apply real code modifications based on agent suggestions"""

    def __init__(self, codebase_path: str = None):
        self.codebase_path = Path(codebase_path) if codebase_path else Path.cwd()
        self.backups: Dict[str, Path] = {}  # Track backups for rollback

    async def apply_suggestion(
        self,
        codebase_path: str,
        suggestion: Dict[str, Any],
        dry_run: bool = False,
    ) -> ModificationResult:
        """
        Apply suggestion to codebase.

        Args:
            codebase_path: Path to codebase to modify
            suggestion: Agent suggestion with changes
            dry_run: If True, don't actually modify files

        Returns:
            ModificationResult with success status and details
        """
        try:
            self.codebase_path = Path(codebase_path)
            files_modified = []
            files_failed = []
            changes = {
                "files": [],
                "lines_added": 0,
                "lines_removed": 0,
                "imports_added": suggestion.get("new_imports", []),
            }

            # Parse suggestion
            suggestion_changes = suggestion.get("changes", [])
            description = suggestion.get("description", "")
            new_imports = suggestion.get("new_imports", [])
            modified_code = suggestion.get("modified_code", "")

            logger.info(f"Applying suggestion: {description}")
            logger.info(f"Changes: {suggestion_changes}")

            # Apply changes to Python files
            py_files = list(self.codebase_path.rglob("*.py"))
            for py_file in py_files[:5]:  # Limit to first 5 files for MVP
                try:
                    if await self._modify_python_file(
                        py_file, new_imports, modified_code, dry_run
                    ):
                        files_modified.append(str(py_file.relative_to(self.codebase_path)))
                except Exception as e:
                    logger.error(f"Failed to modify {py_file}: {e}")
                    files_failed.append(str(py_file.relative_to(self.codebase_path)))

            # Generate diff
            diff = await self._generate_diff(files_modified)

            # If dry run, rollback all changes
            if dry_run:
                await self._rollback_changes()
                return ModificationResult(
                    success=True,
                    files_modified=[],
                    files_failed=[],
                    changes=changes,
                    diff=diff,
                )

            # Update changes metadata
            changes["files"] = files_modified
            changes["estimate_lines_added"] = len(modified_code.split("\n"))

            logger.info(f"Modified {len(files_modified)} files")

            return ModificationResult(
                success=len(files_modified) > 0,
                files_modified=files_modified,
                files_failed=files_failed,
                changes=changes,
                diff=diff,
            )

        except Exception as e:
            logger.error(f"Error applying suggestion: {e}")
            return ModificationResult(
                success=False,
                files_modified=[],
                files_failed=[],
                changes={"error": str(e)},
                error_message=str(e),
            )

    async def _modify_python_file(
        self,
        file_path: Path,
        new_imports: List[str],
        new_code: str,
        dry_run: bool = False,
    ) -> bool:
        """
        Modify a Python file by adding imports and new code.

        Args:
            file_path: Path to Python file
            new_imports: List of import statements to add
            new_code: New code to insert
            dry_run: If True, don't actually write changes

        Returns:
            True if modification successful
        """
        try:
            # Read original file
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Create backup
            if not dry_run:
                backup_path = Path(tempfile.gettempdir()) / f"{file_path.stem}_backup.py"
                shutil.copy2(file_path, backup_path)
                self.backups[str(file_path)] = backup_path

            # Add imports at top of file
            modified_content = original_content
            if new_imports:
                import_block = "\n".join(f"import {imp}" for imp in new_imports)
                if "import" in original_content:
                    # Insert after existing imports
                    lines = modified_content.split("\n")
                    insert_idx = 0
                    for i, line in enumerate(lines):
                        if line.startswith("import ") or line.startswith("from "):
                            insert_idx = i + 1
                    lines.insert(insert_idx, import_block)
                    modified_content = "\n".join(lines)
                else:
                    # Add at top
                    modified_content = import_block + "\n\n" + modified_content

            # Add new code (append to end)
            if new_code:
                modified_content += "\n\n" + new_code

            # Write modified file (unless dry run)
            if not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(modified_content)

            logger.info(f"Successfully modified {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error modifying {file_path}: {e}")
            return False

    async def _generate_diff(self, modified_files: List[str]) -> str:
        """Generate a summary diff of changes"""
        diff_lines = []
        for file in modified_files:
            diff_lines.append(f"Modified: {file}")

        return "\n".join(diff_lines)

    async def _rollback_changes(self) -> None:
        """Rollback all modifications using backups"""
        for file_path, backup_path in self.backups.items():
            try:
                shutil.copy2(backup_path, file_path)
                logger.info(f"Rolled back {file_path}")
            except Exception as e:
                logger.error(f"Failed to rollback {file_path}: {e}")

        self.backups.clear()

    def validate_suggestion(self, suggestion: Dict[str, Any]) -> List[str]:
        """
        Validate suggestion format before applying.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not isinstance(suggestion, dict):
            errors.append("Suggestion must be a dictionary")
            return errors

        if "changes" not in suggestion:
            errors.append("Suggestion must have 'changes' field")

        if "description" not in suggestion:
            errors.append("Suggestion must have 'description' field")

        if suggestion.get("new_imports") and not isinstance(
            suggestion["new_imports"], list
        ):
            errors.append("new_imports must be a list")

        return errors


# Singleton instance
_file_modifier_service = None


def get_file_modifier_service(codebase_path: str = None) -> FileModifierService:
    """Get or create FileModifierService instance"""
    global _file_modifier_service
    if _file_modifier_service is None:
        _file_modifier_service = FileModifierService(codebase_path)
    return _file_modifier_service
