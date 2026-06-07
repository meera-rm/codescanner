"""Agent B: Architecture Focused refactoring strategy."""

from typing import List, Optional
from .refactoring_agent import RefactoringAgent, Suggestion, Issue


class AgentB_ArchitectureFocused(RefactoringAgent):
    """
    Architecture-focused refactoring strategy.

    Philosophy: Long-term structure, optimization, maintainability.
    Best for: Growing codebases, architectural issues, design patterns.
    """

    def __init__(self):
        super().__init__()
        self.name = "Agent B"
        self.strategy = "Architecture Focused"

    async def suggest_refactoring(self,
                                   codebase_path: str,
                                   issues: List[Issue]) -> Optional[Suggestion]:
        """
        Suggest refactoring focused on architecture and structure.

        Strategy:
        1. Identify architectural issues
        2. Suggest design patterns
        3. Focus on long-term maintainability
        """

        if not issues:
            return None

        # Find god object issues (architectural)
        god_objects = self._find_issues_by_type(issues, "god_object")
        if god_objects:
            return self._suggest_plugin_architecture(god_objects[0])

        # Find coupling issues (architectural)
        coupling_issues = self._find_issues_by_type(issues, "coupling")
        if coupling_issues:
            return self._suggest_modularization(coupling_issues[0])

        # Find complexity issues (architectural redesign)
        complexity_issues = self._find_issues_by_type(issues, "complexity")
        if complexity_issues:
            return self._suggest_architectural_redesign(complexity_issues[0])

        # Find general structural issues
        target_issue = self._find_most_complex_issue(issues)
        if target_issue:
            return self._suggest_restructuring(target_issue)

        return None

    def _suggest_plugin_architecture(self, issue: Issue) -> Suggestion:
        """Suggest converting to plugin-based architecture."""
        return Suggestion(
            agent=f"{self.name} ({self.strategy})",
            description="Refactor into plugin-based architecture",
            changes=[
                "New: base/analyzer.py - BaseAnalyzer class (plugin interface)",
                "New: plugins/syntax_analyzer.py - SyntaxAnalyzer plugin",
                "New: plugins/security_analyzer.py - SecurityAnalyzer plugin",
                "New: plugins/complexity_analyzer.py - ComplexityAnalyzer plugin",
                "Modified: main coordinator - uses plugins"
            ],
            complexity_reduction=70,
            risk_level="medium",
            clarity_improvement="excellent",
            estimated_time="medium"
        )

    def _suggest_modularization(self, issue: Issue) -> Suggestion:
        """Suggest breaking monolithic module into focused modules."""
        return Suggestion(
            agent=f"{self.name} ({self.strategy})",
            description="Modularize tightly coupled components",
            changes=[
                "New: auth/ - authentication module",
                "New: validation/ - validation module",
                "New: processing/ - data processing module",
                "Modified: imports - use new modules",
                "Removed: monolithic file"
            ],
            complexity_reduction=65,
            risk_level="medium",
            clarity_improvement="excellent",
            estimated_time="medium"
        )

    def _suggest_architectural_redesign(self, issue: Issue) -> Suggestion:
        """Suggest comprehensive architectural redesign."""
        return Suggestion(
            agent=f"{self.name} ({self.strategy})",
            description="Redesign architecture for better separation of concerns",
            changes=[
                "New: models/ - data models",
                "New: services/ - business logic",
                "New: handlers/ - request handlers",
                "Modified: layer structure - enforce SoC",
                "Added: interfaces - define contracts"
            ],
            complexity_reduction=75,
            risk_level="high",
            clarity_improvement="excellent",
            estimated_time="slow"
        )

    def _suggest_restructuring(self, issue: Issue) -> Suggestion:
        """Suggest general structural improvements."""
        return Suggestion(
            agent=f"{self.name} ({self.strategy})",
            description="Restructure for better maintainability",
            changes=[
                "Modified: file organization - group related modules",
                "New: __init__.py files - better imports",
                "Modified: class hierarchies - apply design patterns",
                "Added: interfaces - define abstractions"
            ],
            complexity_reduction=50,
            risk_level="medium",
            clarity_improvement="good",
            estimated_time="medium"
        )
