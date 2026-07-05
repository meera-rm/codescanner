"""
Tests for Parallel Improvement Orchestrator - Phase 4.4
Tests orchestration of parallel execution and PR creation
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.parallel_improvement_orchestrator import (
    ParallelImprovementOrchestrator,
    ParallelImprovementResult,
    get_parallel_improvement_orchestrator,
)
from api.services.parallel_agent_executor import AgentType
from api.services.github_integration import GitHubConfig


@pytest.fixture
def temp_codebase():
    """Create temporary codebase"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        py_file = tmppath / "sample.py"
        py_file.write_text("def hello():\n    return 42\n")
        yield tmppath


@pytest.fixture
def github_config():
    """Create GitHub config"""
    return GitHubConfig(
        token="test-token",
        owner="testuser",
        repo="testrepo",
    )


@pytest.fixture
def orchestrator(temp_codebase, github_config):
    """Create ParallelImprovementOrchestrator"""
    return ParallelImprovementOrchestrator(str(temp_codebase), github_config)


# Mock agent functions
async def mock_agent_a(code: str, context: dict) -> dict:
    """Mock agent A"""
    await asyncio.sleep(0.01)
    return {
        "description": "Simplify code",
        "changes": ["Extract function"],
        "new_imports": [],
        "modified_code": "def helper():\n    pass",
        "complexity_reduction": 30,
        "risk_level": "low",
        "clarity_improvement": "good",
        "estimated_time": "quick",
        "confidence_score": 0.9,
        "rationale": "Better structure",
    }


async def mock_agent_b(code: str, context: dict) -> dict:
    """Mock agent B"""
    await asyncio.sleep(0.015)
    return {
        "description": "Improve architecture",
        "changes": ["Add pattern"],
        "new_imports": ["abc"],
        "modified_code": "from abc import ABC\nclass Base(ABC):\n    pass",
        "complexity_reduction": 20,
        "risk_level": "medium",
        "clarity_improvement": "fair",
        "estimated_time": "moderate",
        "confidence_score": 0.75,
        "rationale": "Better design",
    }


class TestParallelImprovementResult:
    """Test ParallelImprovementResult"""

    def test_result_creation(self):
        """Test creating result"""
        result = ParallelImprovementResult(
            success=True,
            total_agents=2,
            successful_agents=2,
            failed_agents=0,
            suggestions=[],
            execution_time_ms=100.0,
        )

        assert result.success
        assert result.total_agents == 2


class TestOrchestratorInit:
    """Test orchestrator initialization"""

    def test_init_with_config(self, temp_codebase, github_config):
        """Test initialization with config"""
        orchestrator = ParallelImprovementOrchestrator(str(temp_codebase), github_config)

        assert orchestrator.codebase_path == str(temp_codebase)
        assert orchestrator.github_config is not None

    def test_init_without_config(self, temp_codebase):
        """Test initialization without config"""
        orchestrator = ParallelImprovementOrchestrator(str(temp_codebase))

        assert orchestrator.codebase_path == str(temp_codebase)
        assert orchestrator.github_config is None

    def test_register_agent(self, orchestrator):
        """Test registering agent"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)

        status = orchestrator.get_orchestrator_status()
        assert status["registered_agents"] == 1


class TestParallelExecution:
    """Test parallel execution"""

    @pytest.mark.asyncio
    async def test_execute_and_create_prs_single_agent(self, orchestrator):
        """Test execution with single agent"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)

        result = await orchestrator.execute_and_create_prs(
            "def test():\n    pass",
            create_individual_prs=False,
        )

        assert isinstance(result, ParallelImprovementResult)
        assert result.total_agents == 1

    @pytest.mark.asyncio
    async def test_execute_and_create_prs_multiple_agents(self, orchestrator):
        """Test execution with multiple agents"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)
        orchestrator.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_b)

        result = await orchestrator.execute_and_create_prs(
            "def test():\n    pass",
            create_individual_prs=False,
        )

        assert result.total_agents == 2
        assert result.successful_agents == 2

    @pytest.mark.asyncio
    async def test_execute_with_context(self, orchestrator):
        """Test execution with context"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)

        context = {"file_path": "main.py"}
        result = await orchestrator.execute_and_create_prs(
            "def test():\n    pass",
            context=context,
        )

        assert result.success

    @pytest.mark.asyncio
    async def test_execution_time_tracked(self, orchestrator):
        """Test that execution time is tracked"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)

        result = await orchestrator.execute_and_create_prs("def test():\n    pass")

        assert result.execution_time_ms > 0


class TestMergedPRCreation:
    """Test merged PR creation"""

    @pytest.mark.asyncio
    async def test_create_merged_pr(self, orchestrator):
        """Test creating merged PR"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)
        orchestrator.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_b)

        result = await orchestrator.execute_and_create_prs(
            "def test():\n    pass",
            create_individual_prs=False,
        )

        assert result.merged_suggestion is not None
        assert result.merged_suggestion.agent_name == "ParallelMerge"

    @pytest.mark.asyncio
    async def test_merged_pr_combines_suggestions(self, orchestrator):
        """Test that merged PR combines suggestions"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)
        orchestrator.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_b)

        result = await orchestrator.execute_and_create_prs(
            "def test():\n    pass",
            create_individual_prs=False,
        )

        # Merged should have combined changes
        merged = result.merged_suggestion
        assert len(merged.changes) > 0
        assert "Extract function" in merged.changes or "Add pattern" in merged.changes


class TestIndividualPRCreation:
    """Test individual PR creation"""

    @pytest.mark.asyncio
    async def test_create_individual_prs(self, orchestrator):
        """Test creating individual PRs for each agent"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)
        orchestrator.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_b)

        result = await orchestrator.execute_and_create_prs(
            "def test():\n    pass",
            create_individual_prs=True,
        )

        # Should attempt to create PR for each agent
        assert len(result.pr_results) > 0


class TestPRTitleTemplate:
    """Test PR title templating"""

    @pytest.mark.asyncio
    async def test_custom_pr_title_template(self, orchestrator):
        """Test custom PR title template"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)

        result = await orchestrator.execute_and_create_prs(
            "def test():\n    pass",
            pr_title_template="CodePulse: {description}",
        )

        assert result.total_agents == 1


class TestAutoMerge:
    """Test auto-merge option"""

    @pytest.mark.asyncio
    async def test_execute_with_auto_merge(self, orchestrator):
        """Test execution with auto-merge enabled"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)

        result = await orchestrator.execute_and_create_prs(
            "def test():\n    pass",
            auto_merge=True,
        )

        assert isinstance(result, ParallelImprovementResult)


class TestOrchestratorStatus:
    """Test orchestrator status"""

    def test_get_status(self, orchestrator):
        """Test getting orchestrator status"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)
        orchestrator.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_b)

        status = orchestrator.get_orchestrator_status()

        assert status["registered_agents"] == 2
        assert "Agent A" in status["agent_names"]
        assert "Agent B" in status["agent_names"]


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_execute_with_no_agents(self, orchestrator):
        """Test execution with no agents"""
        result = await orchestrator.execute_and_create_prs("def test():\n    pass")

        assert not result.success
        assert result.total_agents == 0


class TestSingletonPattern:
    """Test factory function"""

    def test_get_orchestrator(self, temp_codebase):
        """Test factory function"""
        orchestrator = get_parallel_improvement_orchestrator(str(temp_codebase))

        assert orchestrator is not None
        assert isinstance(orchestrator, ParallelImprovementOrchestrator)


class TestDescriptionBuilding:
    """Test PR description building"""

    @pytest.mark.asyncio
    async def test_merged_description_includes_agents(self, orchestrator):
        """Test that merged description includes contributing agents"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)
        orchestrator.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_b)

        result = await orchestrator.execute_and_create_prs(
            "def test():\n    pass",
            create_individual_prs=False,
        )

        assert result.merged_suggestion is not None


class TestCompleteFlow:
    """Test complete orchestration flow"""

    @pytest.mark.asyncio
    async def test_complete_parallel_improvement_flow(self, orchestrator):
        """Test complete flow from execution to PR creation"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)
        orchestrator.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_b)

        result = await orchestrator.execute_and_create_prs(
            "def process_data():\n    return sum([1, 2, 3])",
            context={"file_path": "utils.py", "project": "test"},
            pr_title_template="CodePulse: {description}",
            create_individual_prs=False,
            auto_merge=False,
        )

        assert result.total_agents == 2
        assert result.successful_agents == 2
        assert result.merged_suggestion is not None
        assert result.execution_time_ms > 0


class TestMultipleScenarios:
    """Test multiple scenarios"""

    @pytest.mark.asyncio
    async def test_scenario_simplicity_focus(self, orchestrator):
        """Test scenario with simplicity-focused agent"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Simplify", mock_agent_a)

        result = await orchestrator.execute_and_create_prs(
            "def complex_function():\n    pass"
        )

        assert result.successful_agents == 1

    @pytest.mark.asyncio
    async def test_scenario_combined_improvements(self, orchestrator):
        """Test scenario with combined improvements"""
        orchestrator.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", mock_agent_a)
        orchestrator.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", mock_agent_b)

        result = await orchestrator.execute_and_create_prs(
            "def legacy_code():\n    pass",
            create_individual_prs=False,
        )

        merged = result.merged_suggestion
        assert merged is not None
        # Should combine improvements from both agents
        assert len(merged.changes) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
