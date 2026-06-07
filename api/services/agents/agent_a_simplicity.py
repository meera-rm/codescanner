"""Agent A: Simplicity First refactoring strategy."""

from typing import List, Optional
from .refactoring_agent import RefactoringAgent, Suggestion, Issue


class AgentA_SimplityFirst(RefactoringAgent):
    """
    Simplicity-first refactoring strategy.

    Philosophy: Minimal changes, maximum clarity, low risk.
    Best for: First iterations, conservative teams, basic cleanup.
    """

    def __init__(self):
        super().__init__()
        self.name = "Agent A"
        self.strategy = "Simplicity First"

    async def suggest_refactoring(self,
                                   codebase_path: str,
                                   issues: List[Issue]) -> Optional[Suggestion]:
        """
        Suggest refactoring focused on simplicity and low risk.

        Strategy:
        1. Find most complex function
        2. Suggest extracting helper functions
        3. Keep changes minimal and clear
        """

        if not issues:
            return None

        # Find most complex issue
        target_issue = self._find_most_complex_issue(issues)
        if not target_issue:
            return None

        # Find duplication issues (simplest to fix)
        duplication_issues = self._find_issues_by_type(issues, "duplication")
        if duplication_issues:
            return self._suggest_deduplication(duplication_issues[0])

        # Find complexity issues
        complexity_issues = self._find_issues_by_type(issues, "complexity")
        if complexity_issues:
            return self._suggest_extraction(complexity_issues[0])

        # Find security issues (simple fixes)
        security_issues = self._find_issues_by_type(issues, "security")
        if security_issues:
            return self._suggest_security_fix(security_issues[0])

        return None

    def _suggest_extraction(self, issue: Issue) -> Suggestion:
        """Suggest extracting methods from complex function."""
        return Suggestion(
            agent=f"{self.name} ({self.strategy})",
            description=f"Extract helper functions from {issue.affected_function}()",
            changes=[
                f"New: check_syntax() - validates syntax only",
                f"New: check_security() - checks security issues",
                f"New: check_complexity() - checks code complexity",
                f"Modified: {issue.affected_function}() - orchestrates above"
            ],
            complexity_reduction=60,
            risk_level="low",
            clarity_improvement="good",
            estimated_time="quick"
        )

    def _suggest_deduplication(self, issue: Issue) -> Suggestion:
        """Suggest removing code duplication."""
        return Suggestion(
            agent=f"{self.name} ({self.strategy})",
            description="Remove code duplication with shared utility",
            changes=[
                "New: shared_utils.py - common functions",
                f"Modified: {issue.file_path} - use shared utilities",
                "Removed: duplicate code blocks"
            ],
            complexity_reduction=45,
            risk_level="low",
            clarity_improvement="excellent",
            estimated_time="quick"
        )

    def _suggest_security_fix(self, issue: Issue) -> Suggestion:
        """Suggest fixing security issue."""
        return Suggestion(
            agent=f"{self.name} ({self.strategy})",
            description="Fix security issue with minimal changes",
            changes=[
                f"Modified: {issue.file_path} - {issue.description}",
                "Added: input validation",
                "Added: error handling"
            ],
            complexity_reduction=20,
            risk_level="low",
            clarity_improvement="good",
            estimated_time="quick"
        )
