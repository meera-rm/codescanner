"""
Iteration PR Manager - Phase 4.3
Orchestrates file modifications, validation, and GitHub PR creation
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from api.services.file_modifier_service import FileModifierService, ModificationResult
from api.services.code_formatter import CodeFormatter
from api.services.code_validator import CodeValidator
from api.services.diff_generator import DiffGenerator
from api.services.github_pr_actions import (
    GitHubPRActions as GitHubIntegration,
    GitHubConfig,
    PRResult,
)

logger = logging.getLogger(__name__)


@dataclass
class IterationPRResult:
    """Result of iteration PR creation"""
    success: bool
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    branch_name: Optional[str] = None
    files_modified: int = 0
    files_failed: int = 0
    validation_passed: bool = False
    syntax_valid: bool = False
    linting_passed: bool = False
    tests_passed: bool = False
    diff_summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class IterationPRManager:
    """Orchestrate file modifications and PR creation for iterations"""

    def __init__(
        self,
        codebase_path: str,
        github_config: Optional[GitHubConfig] = None,
    ):
        self.codebase_path = codebase_path
        self.modifier = FileModifierService(codebase_path)
        self.formatter = CodeFormatter()
        self.validator = CodeValidator()
        self.diff_gen = DiffGenerator()
        self.github = GitHubIntegration(github_config)

    async def apply_and_create_pr(
        self,
        suggestion: Dict[str, Any],
        pr_title: str,
        pr_description: str,
        branch_name: Optional[str] = None,
        auto_merge: bool = False,
    ) -> IterationPRResult:
        """
        Apply code suggestion and create GitHub PR.

        Args:
            suggestion: Agent suggestion with changes
            pr_title: PR title
            pr_description: PR description
            branch_name: Custom branch name
            auto_merge: Auto-merge if validation passes

        Returns:
            IterationPRResult with PR details
        """
        try:
            # Step 1: Apply modification
            logger.info("Step 1: Applying code modification...")
            mod_result = await self.modifier.apply_suggestion(
                self.codebase_path,
                suggestion,
                dry_run=False,
            )

            if not mod_result.success:
                logger.error("Modification failed")
                return IterationPRResult(
                    success=False,
                    files_modified=len(mod_result.files_modified),
                    files_failed=len(mod_result.files_failed),
                    error_message="Failed to apply modification",
                )

            # Step 2: Format code
            logger.info("Step 2: Formatting modified code...")
            # (Code formatting done implicitly through file modification)

            # Step 3: Validate changes
            logger.info("Step 3: Validating changes...")
            modified_code = suggestion.get("modified_code", "")
            language = "python"  # Default to Python

            val_result = await self.validator.validate_all(
                self.codebase_path,
                modified_code,
                language,
                self.codebase_path,
            )

            # Step 4: Generate diff
            logger.info("Step 4: Generating diff...")
            diff = self.diff_gen.get_staged_changes()
            diff_summary = {
                "lines_added": 0,
                "lines_removed": 0,
            }

            if diff:
                summary = self.diff_gen.get_diff_summary(diff)
                diff_summary = {
                    "files_changed": summary.files_changed,
                    "lines_added": summary.lines_added,
                    "lines_removed": summary.lines_removed,
                }

            # Step 5: Stage changes
            logger.info("Step 5: Staging changes...")
            self.diff_gen.stage_files(mod_result.files_modified)

            # Step 6: Create branch and PR
            logger.info("Step 6: Creating GitHub PR...")
            if branch_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                branch_name = f"codepulse/iteration-{timestamp}"

            # Generate enhanced PR description
            enhanced_description = self._build_pr_description(
                pr_description,
                mod_result,
                val_result,
                diff_summary,
            )

            pr_result = self.github.create_pr(
                branch_name=branch_name,
                title=pr_title,
                description=enhanced_description,
            )

            if not pr_result.success:
                logger.error(f"PR creation failed: {pr_result.error_message}")
                return IterationPRResult(
                    success=False,
                    files_modified=len(mod_result.files_modified),
                    files_failed=len(mod_result.files_failed),
                    error_message=pr_result.error_message,
                )

            # Step 7: Post additional details as comments
            if pr_result.pr_number:
                logger.info("Step 7: Posting review details...")
                self._post_pr_details(
                    pr_result.pr_number,
                    mod_result,
                    val_result,
                    diff,
                )

            # Step 8: Optionally auto-merge
            if auto_merge and val_result.success:
                logger.info("Step 8: Auto-merging PR...")
                self.github.merge_pr(
                    pr_result.pr_number,
                    merge_method="squash",
                )

            logger.info(f"Successfully created PR #{pr_result.pr_number}")

            return IterationPRResult(
                success=True,
                pr_number=pr_result.pr_number,
                pr_url=pr_result.pr_url,
                branch_name=branch_name,
                files_modified=len(mod_result.files_modified),
                files_failed=len(mod_result.files_failed),
                validation_passed=val_result.success,
                syntax_valid=val_result.syntax_valid,
                linting_passed=val_result.linting_passed,
                tests_passed=val_result.tests_passed,
                diff_summary=diff_summary,
            )

        except Exception as e:
            logger.error(f"Error in apply_and_create_pr: {e}")
            return IterationPRResult(
                success=False,
                error_message=str(e),
            )

    def _build_pr_description(
        self,
        base_description: str,
        mod_result: ModificationResult,
        val_result: Any,
        diff_summary: Dict[str, Any],
    ) -> str:
        """Build enhanced PR description with validation details"""
        sections = [base_description, ""]

        # Files modified
        sections.append("## Files Modified")
        if mod_result.files_modified:
            for file in mod_result.files_modified:
                sections.append(f"- {file}")
        else:
            sections.append("- (no files modified)")

        # Diff summary
        sections.append("")
        sections.append("## Changes")
        sections.append(f"- Files changed: {diff_summary.get('files_changed', 0)}")
        sections.append(f"- Lines added: {diff_summary.get('lines_added', 0)}")
        sections.append(f"- Lines removed: {diff_summary.get('lines_removed', 0)}")

        # Validation status
        sections.append("")
        sections.append("## Validation")
        sections.append(
            f"- Syntax valid: {'✓' if val_result.syntax_valid else '✗'}"
        )
        sections.append(
            f"- Linting passed: {'✓' if val_result.linting_passed else '✗'}"
        )
        sections.append(f"- Tests passed: {'✓' if val_result.tests_passed else '✗'}")

        # Errors/warnings
        if val_result.syntax_errors:
            sections.append("")
            sections.append("## Syntax Errors")
            for error in val_result.syntax_errors:
                sections.append(f"- {error}")

        if val_result.linting_errors:
            sections.append("")
            sections.append("## Linting Issues")
            for error in val_result.linting_errors[:5]:
                sections.append(f"- {error}")

        sections.append("")
        sections.append("---")
        sections.append("Created by CodePulse AI")

        return "\n".join(sections)

    def _post_pr_details(
        self,
        pr_number: int,
        mod_result: ModificationResult,
        val_result: Any,
        diff: str,
    ) -> None:
        """Post validation details and diff as PR comments"""
        try:
            # Post validation summary
            if not val_result.success:
                errors = []
                if val_result.syntax_errors:
                    errors.extend(val_result.syntax_errors)
                if val_result.linting_errors:
                    errors.extend(val_result.linting_errors[:3])

                if errors:
                    comment = "## ⚠️ Validation Issues\n\n"
                    for error in errors:
                        comment += f"- {error}\n"

                    self.github.post_pr_comment(pr_number, comment)

            # Post diff summary if available
            if diff:
                diff_comment = f"## Diff Preview\n\n```diff\n{diff[:1000]}\n...\n```"
                self.github.post_pr_comment(pr_number, diff_comment)

        except Exception as e:
            logger.error(f"Error posting PR details: {e}")

    def get_pr_status(self, pr_number: int) -> Optional[Dict[str, Any]]:
        """Get status of a PR"""
        try:
            status = self.github.get_pr_status(pr_number)

            if status:
                return {
                    "pr_number": status.pr_number,
                    "state": status.state,
                    "title": status.title,
                    "author": status.author,
                    "approved": status.approved,
                    "review_count": status.review_count,
                    "merge_status": status.merge_status,
                }
            return None

        except Exception as e:
            logger.error(f"Error getting PR status: {e}")
            return None

    def request_review(self, pr_number: int, reviewers: list) -> bool:
        """Request review on a PR"""
        try:
            return self.github.request_review(pr_number, reviewers)
        except Exception as e:
            logger.error(f"Error requesting review: {e}")
            return False

    def add_labels(self, pr_number: int, labels: list) -> bool:
        """Add labels to a PR"""
        try:
            return self.github.add_labels(pr_number, labels)
        except Exception as e:
            logger.error(f"Error adding labels: {e}")
            return False


# Factory function
def get_iteration_pr_manager(
    codebase_path: str,
    github_config: Optional[GitHubConfig] = None,
) -> IterationPRManager:
    """Create IterationPRManager instance"""
    return IterationPRManager(codebase_path, github_config)
