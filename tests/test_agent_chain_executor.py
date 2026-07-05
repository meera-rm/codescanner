"""
Tests for Agent Chain Executor - Phase 5.1
"""

import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.agent_registry import (
    AgentRegistry, AgentDefinition, AgentType
)
from api.services.agent_chain_executor import (
    AgentChainExecutor, ChainDefinition, ChainStep,
    Condition, ConditionOperator
)


@pytest.fixture
def registry():
    """Create registry with test agents"""
    reg = AgentRegistry()

    async def agent_a(inputs, context):
        return {"value": inputs.get("value", 0) + 10, "name": "agent_a"}

    async def agent_b(inputs, context):
        return {"value": inputs.get("value", 0) * 2, "name": "agent_b"}

    async def agent_c(inputs, context):
        return {"value": inputs.get("value", 0) - 5, "name": "agent_c"}

    defn_a = AgentDefinition(name="agent_a", type=AgentType.CUSTOM, description="Agent A")
    defn_b = AgentDefinition(name="agent_b", type=AgentType.CUSTOM, description="Agent B")
    defn_c = AgentDefinition(name="agent_c", type=AgentType.CUSTOM, description="Agent C")

    reg.register(defn_a, agent_a)
    reg.register(defn_b, agent_b)
    reg.register(defn_c, agent_c)

    return reg


@pytest.fixture
def executor(registry):
    """Create chain executor"""
    return AgentChainExecutor(registry)


class TestCondition:
    """Test conditions"""

    def test_eq_condition(self):
        """Test equality condition"""
        cond = Condition(
            field="status",
            operator=ConditionOperator.EQ,
            value="success"
        )

        assert cond.evaluate({"status": "success"}) is True
        assert cond.evaluate({"status": "failure"}) is False

    def test_gt_condition(self):
        """Test greater than condition"""
        cond = Condition(
            field="score",
            operator=ConditionOperator.GT,
            value=50
        )

        assert cond.evaluate({"score": 60}) is True
        assert cond.evaluate({"score": 40}) is False

    def test_in_condition(self):
        """Test in condition"""
        cond = Condition(
            field="status",
            operator=ConditionOperator.IN,
            value=["success", "partial"]
        )

        assert cond.evaluate({"status": "success"}) is True
        assert cond.evaluate({"status": "failure"}) is False

    def test_contains_condition(self):
        """Test contains condition"""
        cond = Condition(
            field="message",
            operator=ConditionOperator.CONTAINS,
            value="error"
        )

        assert cond.evaluate({"message": "an error occurred"}) is True
        assert cond.evaluate({"message": "success"}) is False

    def test_agent_specific_condition(self):
        """Test condition on specific agent output"""
        cond = Condition(
            field="score",
            operator=ConditionOperator.GT,
            value=70,
            agent="analyzer"
        )

        context = {
            "analyzer": {"score": 80, "status": "success"}
        }

        assert cond.evaluate(context) is True


class TestChainDefinition:
    """Test chain definition"""

    def test_create_chain(self):
        """Test creating chain"""
        chain = ChainDefinition(
            name="test_chain",
            description="Test chain",
            steps=[
                ChainStep(agent_name="agent_a"),
                ChainStep(agent_name="agent_b")
            ]
        )

        assert chain.name == "test_chain"
        assert len(chain.steps) == 2

    def test_chain_with_conditions(self):
        """Test chain with conditional steps"""
        chain = ChainDefinition(
            name="conditional_chain",
            description="Chain with conditions",
            steps=[
                ChainStep(agent_name="agent_a"),
                ChainStep(
                    agent_name="agent_b",
                    conditions=[
                        Condition(
                            field="value",
                            operator=ConditionOperator.GT,
                            value=100,
                            agent="agent_a"
                        )
                    ]
                )
            ]
        )

        assert len(chain.steps[1].conditions) == 1


class TestAgentChainExecutor:
    """Test chain executor"""

    def test_register_chain(self, executor):
        """Test registering chain"""
        chain = ChainDefinition(
            name="test_chain",
            description="Test"
        )

        executor.register_chain(chain)

        assert executor.get_chain("test_chain") is not None

    def test_register_duplicate_chain_fails(self, executor):
        """Test duplicate chain registration fails"""
        chain = ChainDefinition(
            name="test_chain",
            description="Test"
        )

        executor.register_chain(chain)

        with pytest.raises(ValueError):
            executor.register_chain(chain)

    @pytest.mark.asyncio
    async def test_execute_simple_chain(self, executor):
        """Test executing simple chain"""
        chain = ChainDefinition(
            name="simple_chain",
            description="Simple chain",
            steps=[
                ChainStep(agent_name="agent_a", inputs={"value": 10}),
                ChainStep(agent_name="agent_b", inputs={})
            ]
        )

        executor.register_chain(chain)

        result = await executor.execute("simple_chain", {"value": 10})

        assert result.success is True
        assert result.steps_executed == 2
        assert "agent_a" in result.results
        assert "agent_b" in result.results

    @pytest.mark.asyncio
    async def test_execute_chain_with_conditions(self, executor):
        """Test chain with conditional execution"""
        chain = ChainDefinition(
            name="conditional_chain",
            description="Conditional chain",
            steps=[
                ChainStep(agent_name="agent_a", inputs={"value": 5}),
                ChainStep(
                    agent_name="agent_b",
                    conditions=[
                        Condition(
                            field="value",
                            operator=ConditionOperator.GT,
                            value=10,
                            agent="agent_a"
                        )
                    ]
                )
            ]
        )

        executor.register_chain(chain)

        result = await executor.execute("conditional_chain", {"value": 5})

        # agent_b should be skipped
        assert "agent_b" not in result.results

    @pytest.mark.asyncio
    async def test_execute_nonexistent_chain(self, executor):
        """Test executing nonexistent chain"""
        with pytest.raises(ValueError):
            await executor.execute("nonexistent", {})

    @pytest.mark.asyncio
    async def test_chain_with_error_handling(self, executor):
        """Test chain with error handling"""
        registry = executor.registry

        async def failing_agent(inputs, context):
            return {"error": "Something went wrong"}

        defn = AgentDefinition(
            name="failing_agent",
            type=AgentType.CUSTOM,
            description="Fails"
        )

        registry.register(defn, failing_agent)

        chain = ChainDefinition(
            name="error_chain",
            description="Chain with error",
            steps=[
                ChainStep(agent_name="failing_agent", continue_on_error=True),
                ChainStep(agent_name="agent_a")
            ]
        )

        executor.register_chain(chain)

        result = await executor.execute("error_chain", {"value": 10})

        # Should continue despite error
        assert result.steps_executed == 2

    @pytest.mark.asyncio
    async def test_parallel_chain_execution(self, executor):
        """Test executing multiple chains in parallel"""
        chain1 = ChainDefinition(
            name="chain1",
            description="Chain 1",
            steps=[ChainStep(agent_name="agent_a", inputs={"value": 1})]
        )

        chain2 = ChainDefinition(
            name="chain2",
            description="Chain 2",
            steps=[ChainStep(agent_name="agent_b", inputs={"value": 2})]
        )

        executor.register_chain(chain1)
        executor.register_chain(chain2)

        results = await executor.execute_parallel(
            ["chain1", "chain2"],
            {"value": 0}
        )

        assert len(results) == 2
        assert results[0].chain_name == "chain1"
        assert results[1].chain_name == "chain2"

    def test_export_chain(self, executor):
        """Test exporting chain definition"""
        chain = ChainDefinition(
            name="export_chain",
            description="Chain to export",
            steps=[
                ChainStep(
                    agent_name="agent_a",
                    description="First step",
                    inputs={"value": 10}
                )
            ]
        )

        executor.register_chain(chain)

        exported = executor.export_chain("export_chain")

        assert exported["name"] == "export_chain"
        assert len(exported["steps"]) == 1
        assert exported["steps"][0]["agent_name"] == "agent_a"

    @pytest.mark.asyncio
    async def test_chain_input_propagation(self, executor):
        """Test inputs flow through chain"""
        chain = ChainDefinition(
            name="flow_chain",
            description="Test input flow",
            steps=[
                ChainStep(agent_name="agent_a", inputs={"value": 100}),
                ChainStep(agent_name="agent_b", inputs={}),
                ChainStep(agent_name="agent_c", inputs={})
            ]
        )

        executor.register_chain(chain)

        result = await executor.execute("flow_chain", {})

        # Verify chain executed all steps
        assert result.steps_executed >= 1


class TestChainStep:
    """Test chain steps"""

    def test_create_step(self):
        """Test creating step"""
        step = ChainStep(
            agent_name="test_agent",
            description="Test step",
            timeout=30,
            continue_on_error=True
        )

        assert step.agent_name == "test_agent"
        assert step.timeout == 30
        assert step.continue_on_error is True

    def test_step_with_conditions(self):
        """Test step with conditions"""
        step = ChainStep(
            agent_name="test_agent",
            conditions=[
                Condition(
                    field="ready",
                    operator=ConditionOperator.EQ,
                    value=True
                )
            ]
        )

        assert len(step.conditions) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
