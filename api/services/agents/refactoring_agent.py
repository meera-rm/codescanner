"""Base class for refactoring agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Suggestion:
    """Refactoring suggestion from an agent."""

    agent: str
    description: str
    changes: List[str]
    complexity_reduction: float  # 0-100, percentage reduction
    risk_level: str  # "low", "medium", "high"
    clarity_improvement: str  # "ok", "good", "excellent"
    estimated_time: str  # "quick", "medium", "slow"
    modified_code: Optional[str] = None
    new_imports: List[str] = None

    def __post_init__(self):
        if self.new_imports is None:
            self.new_imports = []


@dataclass
class Issue:
    """Code issue identified by scanner."""

    issue_type: str  # "complexity", "duplication", "security", etc.
    file_path: str
    line_number: int
    description: str
    severity: str  # "critical", "high", "medium", "low"
    complexity: Optional[float] = None
    affected_function: Optional[str] = None


class RefactoringAgent(ABC):
    """Base class for all refactoring agents."""

    def __init__(self):
        self.name: str = ""
        self.strategy: str = ""

    @abstractmethod
    async def suggest_refactoring(self,
                                   codebase_path: str,
                                   issues: List[Issue]) -> Optional[Suggestion]:
        """
        Generate refactoring suggestion based on issues found.

        Args:
            codebase_path: Path to codebase being analyzed
            issues: List of issues found by scanner

        Returns:
            Suggestion object or None if no suggestion can be made
        """
        pass

    def _find_most_complex_issue(self, issues: List[Issue]) -> Optional[Issue]:
        """Find the issue with highest complexity."""
        if not issues:
            return None
        return max(
            [i for i in issues if i.complexity],
            key=lambda x: x.complexity,
            default=None
        )

    def _find_issues_by_type(self, issues: List[Issue], issue_type: str) -> List[Issue]:
        """Find all issues of a specific type."""
        return [i for i in issues if i.issue_type == issue_type]

    def _find_critical_issues(self, issues: List[Issue]) -> List[Issue]:
        """Find all critical severity issues."""
        return [i for i in issues if i.severity == "critical"]
