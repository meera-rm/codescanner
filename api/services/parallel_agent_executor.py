"""
Parallel Agent Executor - Phase 4.4
Execute multiple agents in parallel and coordinate results
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent types"""
    SIMPLICITY_FIRST = "simplicity_first"  # Agent A
    ARCHITECTURE_FOCUS = "architecture_focus"  # Agent B
    PERFORMANCE_FOCUS = "performance_focus"  # Agent C


@dataclass
class AgentSuggestion:
    """Result from a single agent"""
    agent_type: AgentType
    agent_name: str
    description: str
    changes: List[str]
    new_imports: List[str]
    modified_code: str
    complexity_reduction: int = 0
    risk_level: str = "medium"  # low, medium, high
    clarity_improvement: str = ""  # poor, fair, good, excellent
    estimated_time: str = ""  # quick, moderate, lengthy
    confidence_score: float = 0.0  # 0-1
    rationale: str = ""


@dataclass
class ParallelExecutionResult:
    """Result of parallel agent execution"""
    success: bool
    total_agents: int
    completed_agents: int
    failed_agents: int
    suggestions: List[AgentSuggestion]
    execution_time_ms: float = 0.0
    merged_suggestion: Optional[AgentSuggestion] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


@dataclass
class ConflictResolution:
    """Resolved conflict between agent suggestions"""
    conflicting_suggestions: List[AgentSuggestion]
    resolution: AgentSuggestion
    resolution_strategy: str  # "highest_confidence", "lowest_risk", "best_time"
    rationale: str


class AgentExecutor:
    """Execute a single agent"""

    def __init__(
        self,
        agent_type: AgentType,
        agent_name: str,
        agent_func: Callable,
    ):
        self.agent_type = agent_type
        self.agent_name = agent_name
        self.agent_func = agent_func

    async def execute(self, code: str, context: Dict[str, Any]) -> Optional[AgentSuggestion]:
        """
        Execute agent and return suggestion.

        Args:
            code: Source code to analyze
            context: Additional context (file path, project info, etc.)

        Returns:
            AgentSuggestion or None if failed
        """
        try:
            logger.info(f"Executing {self.agent_name}...")
            start = datetime.now()

            result = await self.agent_func(code, context)

            elapsed = (datetime.now() - start).total_seconds() * 1000
            logger.info(f"{self.agent_name} completed in {elapsed:.0f}ms")

            if isinstance(result, dict):
                return self._dict_to_suggestion(result)
            return result

        except Exception as e:
            logger.error(f"Error executing {self.agent_name}: {e}")
            return None

    def _dict_to_suggestion(self, data: Dict[str, Any]) -> AgentSuggestion:
        """Convert dict to AgentSuggestion"""
        return AgentSuggestion(
            agent_type=self.agent_type,
            agent_name=self.agent_name,
            description=data.get("description", ""),
            changes=data.get("changes", []),
            new_imports=data.get("new_imports", []),
            modified_code=data.get("modified_code", ""),
            complexity_reduction=data.get("complexity_reduction", 0),
            risk_level=data.get("risk_level", "medium"),
            clarity_improvement=data.get("clarity_improvement", ""),
            estimated_time=data.get("estimated_time", ""),
            confidence_score=data.get("confidence_score", 0.0),
            rationale=data.get("rationale", ""),
        )


class ParallelAgentExecutor:
    """Execute multiple agents in parallel"""

    def __init__(self):
        self.agents: List[AgentExecutor] = []
        self.max_concurrent = 3  # Limit concurrent execution
        self.timeout = 60  # seconds per agent

    def register_agent(
        self,
        agent_type: AgentType,
        agent_name: str,
        agent_func: Callable,
    ) -> None:
        """Register an agent"""
        executor = AgentExecutor(agent_type, agent_name, agent_func)
        self.agents.append(executor)
        logger.info(f"Registered agent: {agent_name}")

    async def execute_all(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ParallelExecutionResult:
        """
        Execute all registered agents in parallel.

        Args:
            code: Source code to analyze
            context: Additional context

        Returns:
            ParallelExecutionResult with all suggestions
        """
        context = context or {}
        start_time = datetime.now()

        try:
            logger.info(f"Starting parallel execution of {len(self.agents)} agents")

            # Execute agents with concurrency limit
            tasks = [
                asyncio.wait_for(agent.execute(code, context), timeout=self.timeout)
                for agent in self.agents
            ]

            # Use semaphore to limit concurrent execution
            semaphore = asyncio.Semaphore(self.max_concurrent)

            async def execute_with_semaphore(task):
                async with semaphore:
                    return await task

            results = await asyncio.gather(
                *[execute_with_semaphore(task) for task in tasks],
                return_exceptions=True,
            )

            # Process results
            suggestions = []
            failed_count = 0

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Agent {self.agents[i].agent_name} failed: {result}")
                    failed_count += 1
                elif result is None:
                    failed_count += 1
                else:
                    suggestions.append(result)

            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

            logger.info(
                f"Parallel execution complete: {len(suggestions)} successful, "
                f"{failed_count} failed in {elapsed_ms:.0f}ms"
            )

            # Try to merge suggestions
            merged = self._merge_suggestions(suggestions) if suggestions else None

            return ParallelExecutionResult(
                success=len(suggestions) > 0,
                total_agents=len(self.agents),
                completed_agents=len(suggestions),
                failed_agents=failed_count,
                suggestions=suggestions,
                execution_time_ms=elapsed_ms,
                merged_suggestion=merged,
            )

        except Exception as e:
            logger.error(f"Error in execute_all: {e}")
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return ParallelExecutionResult(
                success=False,
                total_agents=len(self.agents),
                completed_agents=0,
                failed_agents=len(self.agents),
                suggestions=[],
                execution_time_ms=elapsed_ms,
                errors=[str(e)],
            )

    def _merge_suggestions(
        self,
        suggestions: List[AgentSuggestion],
    ) -> AgentSuggestion:
        """
        Merge multiple suggestions into one.

        Strategy: Select suggestion with highest confidence and lowest risk
        """
        if not suggestions:
            return None

        if len(suggestions) == 1:
            return suggestions[0]

        # Score each suggestion
        best_score = -1
        best_suggestion = None

        for suggestion in suggestions:
            # Score: confidence + (1 - risk_level) - time_penalty
            risk_score = {"low": 1.0, "medium": 0.5, "high": 0.0}.get(
                suggestion.risk_level, 0.5
            )
            time_score = {"quick": 1.0, "moderate": 0.5, "lengthy": 0.0}.get(
                suggestion.estimated_time, 0.5
            )

            score = (
                suggestion.confidence_score * 0.5
                + risk_score * 0.3
                + time_score * 0.2
            )

            logger.info(
                f"{suggestion.agent_name} score: {score:.2f} "
                f"(confidence={suggestion.confidence_score:.2f}, "
                f"risk={suggestion.risk_level}, time={suggestion.estimated_time})"
            )

            if score > best_score:
                best_score = score
                best_suggestion = suggestion

        # Create merged suggestion
        merged = AgentSuggestion(
            agent_type=AgentType.SIMPLICITY_FIRST,  # Meta agent
            agent_name="ParallelMerge",
            description=f"Merged from {len(suggestions)} agents",
            changes=self._merge_changes(suggestions),
            new_imports=self._merge_imports(suggestions),
            modified_code=best_suggestion.modified_code,
            complexity_reduction=max(s.complexity_reduction for s in suggestions),
            risk_level=best_suggestion.risk_level,
            clarity_improvement=best_suggestion.clarity_improvement,
            estimated_time=best_suggestion.estimated_time,
            confidence_score=best_score,
            rationale=f"Best suggestion from {best_suggestion.agent_name} "
            f"(score={best_score:.2f})",
        )

        logger.info(f"Merged suggestion selected from {best_suggestion.agent_name}")
        return merged

    def _merge_changes(self, suggestions: List[AgentSuggestion]) -> List[str]:
        """Merge change lists"""
        seen = set()
        merged = []

        for suggestion in suggestions:
            for change in suggestion.changes:
                if change not in seen:
                    merged.append(change)
                    seen.add(change)

        return merged

    def _merge_imports(self, suggestions: List[AgentSuggestion]) -> List[str]:
        """Merge import lists"""
        seen = set()
        merged = []

        for suggestion in suggestions:
            for imp in suggestion.new_imports:
                if imp not in seen:
                    merged.append(imp)
                    seen.add(imp)

        return merged

    async def execute_with_fallback(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        min_successful_agents: int = 1,
    ) -> ParallelExecutionResult:
        """
        Execute agents with fallback behavior.

        If minimum agents succeed, return success even if others fail.

        Args:
            code: Source code
            context: Additional context
            min_successful_agents: Minimum agents needed for success

        Returns:
            ParallelExecutionResult
        """
        result = await self.execute_all(code, context)

        if result.completed_agents >= min_successful_agents:
            result.success = True
        else:
            result.success = False
            if not result.errors:
                result.errors.append(
                    f"Only {result.completed_agents} agents succeeded, "
                    f"needed {min_successful_agents}"
                )

        return result

    def get_status(self) -> Dict[str, Any]:
        """Get executor status"""
        return {
            "registered_agents": len(self.agents),
            "agent_names": [agent.agent_name for agent in self.agents],
            "max_concurrent": self.max_concurrent,
            "timeout_seconds": self.timeout,
        }


# Factory function
def get_parallel_agent_executor() -> ParallelAgentExecutor:
    """Create ParallelAgentExecutor instance"""
    return ParallelAgentExecutor()
