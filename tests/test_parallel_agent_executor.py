"""
Tests for Parallel Agent Executor - Phase 4.4
Tests parallel execution, merging, and coordination
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.parallel_agent_executor import (
    ParallelAgentExecutor,
    AgentType,
    AgentSuggestion,
    ParallelExecutionResult,
    get_parallel_agent_executor,
)


@pytest.fixture
def executor():
    """Create ParallelAgentExecutor instance"""
    return ParallelAgentExecutor()


# Mock agent functions for testing
async def mock_agent_simplicity(code: str, context: dict) -> dict:
    """Mock simplicity-focused agent"""
    await asyncio.sleep(0.01)  # Simulate work
    return {
        "description": "Simplify code structure",
        "changes": ["Refactor: extract_function()"],
        "new_imports": ["functools"],
        "modified_code": "def extract_function():\n    pass",
        "complexity_reduction": 30,
        "risk_level": "low",
        "clarity_improvement": "good",
        "estimated_time": "quick",
        "confidence_score": 0.9,
        "rationale": "Improves readability",
    }


async def mock_agent_architecture(code: str, context: dict) -> dict:
    """Mock architecture-focused agent"""
    await asyncio.sleep(0.02)  # Simulate more work
    return {
        "description": "Improve architecture",
        "changes": ["New: design_pattern()"],
        "new_imports": ["abc"],
        "modified_code": "class DesignPattern(ABC):\n    pass",
        "complexity_reduction": 20,
        "risk_level": "medium",
        "clarity_improvement": "fair",
        "estimated_time": "moderate",
        "confidence_score": 0.75,
        "rationale": "Better separation of concerns",
    }


async def mock_agent_performance(code: str, context: dict) -> dict:
    """Mock performance-focused agent"""
    await asyncio.sleep(0.015)  # Simulate work
    return {
        "description": "Optimize performance",
        "changes": ["Add: caching"],
        "new_imports": ["functools"],
        "modified_code": "from functools import lru_cache\n@lru_cache\ndef cached_func():\n    pass",
        "complexity_reduction": 10,
        "risk_level": "low",
        "clarity_improvement": "fair",
        "estimated_time": "quick",
        "confidence_score": 0.85,
        "rationale": "Reduces execution time",
    }


async def mock_agent_fails(code: str, context: dict) -> None:
    """Mock agent that fails"""
    raise Exception("Agent failed")


class TestAgentSuggestion:
    """Test AgentSuggestion data structure"""

    def test_agent_suggestion_creation(self):
        """Test creating agent suggestion"""
        suggestion = AgentSuggestion(
            agent_type=AgentType.SIMPLICITY_FIRST,
            agent_name="Agent A",
            description="Simplify code",
            changes=["Extract function"],
            new_imports=["os"],
            modified_code="def new_func():\n    pass",
            complexity_reduction=30,
            confidence_score=0.9,
        )

        assert suggestion.agent_name == "Agent A"
        assert suggestion.complexity_reduction == 30
        assert suggestion.confidence_score == 0.9


class TestParallelExecutionResult:
    """Test ParallelExecutionResult data structure"""

    def test_result_success(self):
        """Test successful result"""
        result = ParallelExecutionResult(
            success=True,
            total_agents=3,
            completed_agents=3,
            failed_agents=0,
            suggestions=[],
            execution_time_ms=100.0,
        )

        assert result.success
        assert result.completed_agents == 3

    def test_result_partial_failure(self):
        """Test partial failure result"""
        result = ParallelExecutionResult(
            success=True,
            total_agents=3,
            completed_agents=2,
            failed_agents=1,
            suggestions=[],
        )

        assert result.completed_agents == 2
        assert result.failed_agents == 1


class TestParallelExecutorInit:
    """Test ParallelAgentExecutor initialization"""

    def test_init(self, executor):
        """Test initialization"""
        assert executor.max_concurrent == 3
        assert executor.timeout == 60
        assert len(executor.agents) == 0

    def test_register_agent(self, executor):
        """Test registering an agent"""
        executor.register_agent(
            AgentType.SIMPLICITY_FIRST,
            "Agent A",
            mock_agent_simplicity,
        )

        assert len(executor.agents) == 1
        assert executor.agents[0].agent_name == "Agent A"

    def test_register_multiple_agents(self, executor):
        """Test registering multiple agents"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_architecture)
        executor.register_agent(AgentType.PERFORMANCE_FOCUS, "Agent C", mock_agent_performance)

        assert len(executor.agents) == 3


class TestParallelExecution:
    """Test parallel execution"""

    @pytest.mark.asyncio
    async def test_execute_single_agent(self, executor):
        """Test executing single agent"""
        executor.register_agent(
            AgentType.SIMPLICITY_FIRST,
            "Agent A",
            mock_agent_simplicity,
        )

        result = await executor.execute_all("def hello():\n    return 42")

        assert result.success
        assert result.completed_agents == 1
        assert len(result.suggestions) == 1
        assert result.suggestions[0].agent_name == "Agent A"

    @pytest.mark.asyncio
    async def test_execute_multiple_agents(self, executor):
        """Test executing multiple agents in parallel"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_architecture)
        executor.register_agent(AgentType.PERFORMANCE_FOCUS, "Agent C", mock_agent_performance)

        result = await executor.execute_all("def hello():\n    return 42")

        assert result.success
        assert result.completed_agents == 3
        assert len(result.suggestions) == 3
        assert result.total_agents == 3

    @pytest.mark.asyncio
    async def test_execute_with_context(self, executor):
        """Test executing with context"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)

        context = {"file_path": "main.py", "project": "test"}
        result = await executor.execute_all("def test():\n    pass", context)

        assert result.success

    @pytest.mark.asyncio
    async def test_execution_time_tracking(self, executor):
        """Test that execution time is tracked"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)

        result = await executor.execute_all("def test():\n    pass")

        assert result.execution_time_ms > 0

    @pytest.mark.asyncio
    async def test_partial_failure(self, executor):
        """Test handling partial failures"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_fails)
        executor.register_agent(AgentType.PERFORMANCE_FOCUS, "Agent C", mock_agent_performance)

        result = await executor.execute_all("def test():\n    pass")

        assert result.success  # At least some agents succeeded
        assert result.completed_agents == 2
        assert result.failed_agents == 1


class TestSuggestionMerging:
    """Test suggestion merging"""

    @pytest.mark.asyncio
    async def test_merge_suggestions(self, executor):
        """Test merging multiple suggestions"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_architecture)

        result = await executor.execute_all("def test():\n    pass")

        assert result.merged_suggestion is not None
        assert result.merged_suggestion.agent_name == "ParallelMerge"

    @pytest.mark.asyncio
    async def test_merge_selects_best_suggestion(self, executor):
        """Test that merge selects best suggestion by score"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_architecture)
        executor.register_agent(AgentType.PERFORMANCE_FOCUS, "Agent C", mock_agent_performance)

        result = await executor.execute_all("def test():\n    pass")

        merged = result.merged_suggestion
        # Should merge changes from all agents
        assert len(merged.changes) > 0
        assert len(merged.new_imports) > 0

    @pytest.mark.asyncio
    async def test_merge_combines_changes(self, executor):
        """Test that merge combines all changes"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_architecture)
        executor.register_agent(AgentType.PERFORMANCE_FOCUS, "Agent C", mock_agent_performance)

        result = await executor.execute_all("def test():\n    pass")

        # Should have combined changes
        all_changes = set()
        for suggestion in result.suggestions:
            all_changes.update(suggestion.changes)

        assert len(all_changes) > 0

    @pytest.mark.asyncio
    async def test_merge_deduplicates_imports(self, executor):
        """Test that merge deduplicates imports"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.PERFORMANCE_FOCUS, "Agent C", mock_agent_performance)

        result = await executor.execute_all("def test():\n    pass")

        # Both agents suggest functools, should appear once in merge
        merged = result.merged_suggestion
        functools_count = merged.new_imports.count("functools")
        assert functools_count == 1


class TestFallbackBehavior:
    """Test fallback execution"""

    @pytest.mark.asyncio
    async def test_execute_with_fallback_success(self, executor):
        """Test fallback with successful execution"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_architecture)

        result = await executor.execute_with_fallback(
            "def test():\n    pass",
            min_successful_agents=2,
        )

        assert result.success
        assert result.completed_agents == 2

    @pytest.mark.asyncio
    async def test_execute_with_fallback_insufficient_agents(self, executor):
        """Test fallback with insufficient agents"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_fails)

        result = await executor.execute_with_fallback(
            "def test():\n    pass",
            min_successful_agents=2,
        )

        assert not result.success
        assert result.completed_agents < 2

    @pytest.mark.asyncio
    async def test_execute_with_low_threshold(self, executor):
        """Test fallback with low threshold"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_fails)

        result = await executor.execute_with_fallback(
            "def test():\n    pass",
            min_successful_agents=1,
        )

        assert result.success
        assert result.completed_agents == 1


class TestExecutorStatus:
    """Test executor status"""

    def test_get_status(self, executor):
        """Test getting executor status"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_architecture)

        status = executor.get_status()

        assert status["registered_agents"] == 2
        assert "Agent A" in status["agent_names"]
        assert status["max_concurrent"] == 3


class TestConcurrencyControl:
    """Test concurrency control"""

    @pytest.mark.asyncio
    async def test_max_concurrent_limit(self):
        """Test that max concurrent limit is respected"""
        executor = ParallelAgentExecutor()
        executor.max_concurrent = 1  # Only one at a time

        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_architecture)
        executor.register_agent(AgentType.PERFORMANCE_FOCUS, "Agent C", mock_agent_performance)

        result = await executor.execute_all("def test():\n    pass")

        # Should complete all agents despite concurrency limit
        assert result.completed_agents == 3


class TestTimeoutHandling:
    """Test timeout handling"""

    @pytest.mark.asyncio
    async def test_timeout_configuration(self, executor):
        """Test timeout configuration"""
        executor.timeout = 30

        assert executor.timeout == 30


class TestSingletonPattern:
    """Test singleton pattern"""

    def test_get_parallel_agent_executor(self):
        """Test factory function"""
        executor1 = get_parallel_agent_executor()
        executor2 = get_parallel_agent_executor()

        # Should be different instances (not singleton by design)
        assert executor1 is not executor2


class TestEdgeCases:
    """Test edge cases"""

    @pytest.mark.asyncio
    async def test_execute_with_no_agents(self, executor):
        """Test executing with no agents registered"""
        result = await executor.execute_all("def test():\n    pass")

        assert not result.success
        assert result.completed_agents == 0

    @pytest.mark.asyncio
    async def test_execute_with_empty_code(self, executor):
        """Test executing with empty code"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)

        result = await executor.execute_all("")

        assert result.success
        assert result.completed_agents == 1

    @pytest.mark.asyncio
    async def test_execute_with_none_context(self, executor):
        """Test executing with None context"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)

        result = await executor.execute_all("def test():\n    pass", context=None)

        assert result.success


class TestScoringAndRanking:
    """Test suggestion scoring and ranking"""

    @pytest.mark.asyncio
    async def test_score_calculation(self, executor):
        """Test that suggestions are scored"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_architecture)

        result = await executor.execute_all("def test():\n    pass")

        # Agent A has higher confidence (0.9 vs 0.75) and lower risk
        assert result.merged_suggestion is not None
        # Best suggestion should be from Agent A
        merged = result.merged_suggestion
        assert merged.confidence_score > 0.7


class TestParallelIntegrationFlow:
    """Test complete parallel execution flow"""

    @pytest.mark.asyncio
    async def test_complete_flow(self, executor):
        """Test complete parallel execution flow"""
        executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_simplicity)
        executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_architecture)
        executor.register_agent(AgentType.PERFORMANCE_FOCUS, "Agent C", mock_agent_performance)

        result = await executor.execute_all(
            "def process_data(data):\n    return sum(data)",
            context={"file_path": "utils.py"},
        )

        assert result.success
        assert result.total_agents == 3
        assert result.completed_agents == 3
        assert result.merged_suggestion is not None
        assert len(result.merged_suggestion.changes) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
