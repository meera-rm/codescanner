"""IterationCleanService: Orchestrates the iteration until clean loop."""

import asyncio
from dataclasses import asdict, dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from .agents import (
    AgentA_SimplityFirst,
    AgentB_ArchitectureFocused,
    AgentC_PerformanceOptimized,
    EvaluationAgent,
    ValidatorAgent,
)
from .agents.refactoring_agent import Issue, Suggestion


@dataclass
class IterationStep:
    """Single iteration in the loop."""

    iteration_number: int
    grade_before: str
    grade_after: str
    issues_fixed: int
    agent_selected: str
    fix_description: str
    validation_passed: bool
    applied_at: datetime = field(default_factory=datetime.now)
    changes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IterationResult:
    """Final result of iteration until clean."""

    job_id: str
    status: str  # "completed", "failed", "cancelled"
    start_grade: str
    final_grade: str
    grade_improvement: int
    iterations_count: int
    max_iterations: int
    history: List[IterationStep] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class IterationCleanService:
    """
    Orchestrate iteration until clean loop.

    Coordinates:
    - 3 refactoring agents (parallel suggestions)
    - Evaluation agent (picks best)
    - Validator agent (ensures safety)
    - Scanner service (rescan after each fix)
    - Database persistence
    """

    def __init__(self, scanner_service=None):
        """Initialize service with agents."""
        # Refactoring agents
        self.agent_a = AgentA_SimplityFirst()
        self.agent_b = AgentB_ArchitectureFocused()
        self.agent_c = AgentC_PerformanceOptimized()

        # Evaluation agent
        self.evaluator = EvaluationAgent()

        # Validator agent
        self.validator = ValidatorAgent()

        # Scanner service (injected, use existing)
        self.scanner = scanner_service

    async def fix_until_clean(self,
                              job_id: str,
                              codebase_path: str,
                              target_grade: str = "A",
                              max_iterations: int = 10) -> IterationResult:
        """
        Main loop: iterate until target grade reached.

        FLOW:
        1. SCAN & ASSESS — current grade, issues
        2. GENERATE SUGGESTIONS — all 3 agents in parallel
        3. EVALUATE — pick best suggestion
        4. VALIDATE — check for errors/safety
        5. APPLY — modify files
        6. RESCAN — check new grade
        7. REPEAT — until target reached or max iterations

        Args:
            job_id: Unique job identifier
            codebase_path: Path to codebase
            target_grade: Target grade (A, B, C, etc)
            max_iterations: Maximum iterations before stopping

        Returns:
            IterationResult with full history and metrics
        """

        start_time = datetime.now()
        iteration = 0
        current_grade = None
        history: List[IterationStep] = []
        start_state: Optional[Dict] = None

        try:
            # INITIAL SCAN
            start_state = await self._scan_codebase(codebase_path)
            current_grade = start_state["grade"]

            # Main iteration loop
            while iteration < max_iterations:
                iteration += 1

                # STEP 1: SCAN & ASSESS
                scan_result = await self._scan_codebase(codebase_path)
                current_grade = scan_result["grade"]
                issues = scan_result.get("issues", [])

                # Check if target reached
                if self._grade_value(current_grade) >= self._grade_value(target_grade):
                    # Success!
                    break

                # STEP 2: GENERATE SUGGESTIONS (parallel)
                suggestions = await self._get_suggestions(
                    codebase_path, issues
                )

                if not suggestions:
                    # No suggestions available, we're done
                    break

                # STEP 3: EVALUATE & PICK BEST
                best_suggestion = self.evaluator.pick_best(suggestions)

                # STEP 4: VALIDATE
                validation = await self.validator.validate(best_suggestion)

                if not validation.approved:
                    # Validation failed, skip this suggestion and try next
                    continue

                # STEP 5: APPLY
                await self._apply_fix(codebase_path, best_suggestion)

                # STEP 6: RESCAN
                rescan_result = await self._scan_codebase(codebase_path)
                new_grade = rescan_result["grade"]

                # Track iteration
                issues_fixed = len(issues) - len(rescan_result.get("issues", []))
                history.append(
                    IterationStep(
                        iteration_number=iteration,
                        grade_before=current_grade,
                        grade_after=new_grade,
                        issues_fixed=max(0, issues_fixed),
                        agent_selected=best_suggestion.agent,
                        fix_description=best_suggestion.description,
                        validation_passed=True,
                        applied_at=datetime.now(),
                        changes={
                            "complexity_reduction": best_suggestion.complexity_reduction,
                            "risk_level": best_suggestion.risk_level,
                        }
                    )
                )

                current_grade = new_grade

            # FINAL RESULT
            return self._create_result(
                job_id=job_id,
                status="completed",
                start_state=start_state,
                final_grade=current_grade,
                iterations=iteration,
                max_iterations=max_iterations,
                history=history,
                started_at=start_time,
            )

        except Exception as e:
            # Failed execution
            return IterationResult(
                job_id=job_id,
                status="failed",
                start_grade=start_state["grade"] if start_state else "unknown",
                final_grade=current_grade or "unknown",
                grade_improvement=0,
                iterations_count=iteration,
                max_iterations=max_iterations,
                history=history,
                metrics={},
                started_at=start_time,
                completed_at=datetime.now(),
                error_message=str(e),
            )

    async def _scan_codebase(self, codebase_path: str) -> Dict[str, Any]:
        """
        Scan codebase and return current state.

        Returns: {
            "grade": "A",
            "issues": [...],
            "metrics": {...}
        }
        """
        if not self.scanner:
            # Placeholder: return mock scan result
            return {
                "grade": "B",
                "issues": [],
                "metrics": {"complexity": 15, "issues_count": 5},
            }

        # Use scanner service to scan
        scan_result = await self.scanner.scan(codebase_path)
        return scan_result

    async def _get_suggestions(
        self, codebase_path: str, issues: List[Issue]
    ) -> List[Suggestion]:
        """
        Get refactoring suggestions from all 3 agents in parallel.

        Returns: List of Suggestion objects (1-3)
        """
        suggestions = await asyncio.gather(
            self.agent_a.suggest_refactoring(codebase_path, issues),
            self.agent_b.suggest_refactoring(codebase_path, issues),
            self.agent_c.suggest_refactoring(codebase_path, issues),
        )
        # Filter out None values
        return [s for s in suggestions if s]

    async def _validate_suggestion(self, suggestion: Suggestion) -> Dict[str, Any]:
        """Validate suggestion before applying."""
        validation = await self.validator.validate(suggestion)
        return {
            "approved": validation.approved,
            "checks": [asdict(c) for c in validation.checks],
            "summary": validation.summary,
            "issues_found": validation.issues_found,
        }

    async def _apply_fix(self, codebase_path: str, suggestion: Suggestion) -> None:
        """
        Apply the refactoring to the codebase.

        NOTE: This is a placeholder. In production, would:
        1. Apply changes to files based on suggestion
        2. Format code (black, prettier, etc.)
        3. Commit or prepare diff
        """
        # Placeholder: in Phase 3.5C, implement actual file modifications
        pass

    def _create_result(
        self,
        job_id: str,
        status: str,
        start_state: Dict,
        final_grade: str,
        iterations: int,
        max_iterations: int,
        history: List[IterationStep],
        started_at: datetime,
    ) -> IterationResult:
        """Create final IterationResult from loop data."""

        start_grade = start_state["grade"] if start_state else "unknown"

        return IterationResult(
            job_id=job_id,
            status=status,
            start_grade=start_grade,
            final_grade=final_grade,
            grade_improvement=self._grade_value(final_grade) - self._grade_value(start_grade),
            iterations_count=iterations,
            max_iterations=max_iterations,
            history=history,
            metrics=self._calculate_metrics(history, start_state),
            started_at=started_at,
            completed_at=datetime.now(),
        )

    @staticmethod
    def _grade_value(grade: str) -> float:
        """Convert letter grade to numeric value for comparison."""
        grades = {
            "F": 0.0,
            "D": 1.0,
            "C": 2.0,
            "B": 3.0,
            "A": 4.0,
        }
        base = grades.get(grade[0] if grade else "F", 0)
        # Handle +/- suffixes
        modifier = 0.5 if "-" in grade else (0.3 if "+" in grade else 0)
        return base + modifier

    @staticmethod
    def _calculate_metrics(history: List[IterationStep],
                           start_state: Optional[Dict]) -> Dict[str, Any]:
        """Calculate final metrics from iteration history."""
        if not history:
            return {}

        total_issues_fixed = sum(h.issues_fixed for h in history)
        final_iter = history[-1] if history else None

        return {
            "total_iterations": len(history),
            "total_issues_fixed": total_issues_fixed,
            "final_grade": final_iter.grade_after if final_iter else "unknown",
            "complexity_reductions": [h.changes.get("complexity_reduction", 0)
                                      for h in history],
            "agents_used": list(set(h.agent_selected for h in history)),
        }
