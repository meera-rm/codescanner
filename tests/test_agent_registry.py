"""
Tests for Agent Registry - Phase 5.1
"""

import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.agent_registry import (
    AgentRegistry, AgentDefinition, AgentParameter, AgentOutput,
    AgentType, ExecutionMode, AgentLoader
)


@pytest.fixture
def registry():
    """Create registry"""
    return AgentRegistry()


@pytest.fixture
async def simple_executor():
    """Simple test executor"""
    async def executor(inputs, context):
        return {"result": inputs.get("code", "") + " processed"}
    return executor


class TestAgentRegistry:
    """Test agent registry"""

    def test_register_agent(self, registry, simple_executor):
        """Test registering an agent"""
        defn = AgentDefinition(
            name="test_agent",
            type=AgentType.CUSTOM,
            description="Test agent"
        )

        registry.register(defn, simple_executor)

        assert "test_agent" in registry.agents
        assert registry.get_agent("test_agent") is not None

    def test_register_duplicate_fails(self, registry, simple_executor):
        """Test duplicate registration fails"""
        defn = AgentDefinition(
            name="test_agent",
            type=AgentType.CUSTOM,
            description="Test agent"
        )

        registry.register(defn, simple_executor)

        with pytest.raises(ValueError):
            registry.register(defn, simple_executor)

    def test_unregister_agent(self, registry, simple_executor):
        """Test unregistering agent"""
        defn = AgentDefinition(
            name="test_agent",
            type=AgentType.CUSTOM,
            description="Test agent"
        )

        registry.register(defn, simple_executor)
        registry.unregister("test_agent")

        assert registry.get_agent("test_agent") is None

    def test_unregister_nonexistent_fails(self, registry):
        """Test unregistering nonexistent agent fails"""
        with pytest.raises(ValueError):
            registry.unregister("nonexistent")

    def test_list_agents(self, registry, simple_executor):
        """Test listing agents"""
        defn1 = AgentDefinition(
            name="agent1",
            type=AgentType.CUSTOM,
            description="Agent 1"
        )
        defn2 = AgentDefinition(
            name="agent2",
            type=AgentType.CUSTOM,
            description="Agent 2"
        )

        registry.register(defn1, simple_executor)
        registry.register(defn2, simple_executor)

        agents = registry.list_agents()
        assert len(agents) == 2

    def test_get_agents_by_type(self, registry, simple_executor):
        """Test filtering agents by type"""
        sec_def = AgentDefinition(
            name="security",
            type=AgentType.SECURITY_AUDITOR,
            description="Security agent"
        )
        perf_def = AgentDefinition(
            name="performance",
            type=AgentType.PERFORMANCE_OPTIMIZER,
            description="Performance agent"
        )

        registry.register(sec_def, simple_executor)
        registry.register(perf_def, simple_executor)

        security_agents = registry.get_agents_by_type(AgentType.SECURITY_AUDITOR)
        assert len(security_agents) == 1
        assert security_agents[0].name == "security"

    def test_get_agents_by_tag(self, registry, simple_executor):
        """Test filtering agents by tag"""
        defn = AgentDefinition(
            name="tagged_agent",
            type=AgentType.CUSTOM,
            description="Tagged agent",
            tags=["security", "analysis"]
        )

        registry.register(defn, simple_executor)

        tagged = registry.get_agents_by_tag("security")
        assert len(tagged) == 1
        assert tagged[0].name == "tagged_agent"

    @pytest.mark.asyncio
    async def test_execute_agent(self, registry, simple_executor):
        """Test executing agent"""
        defn = AgentDefinition(
            name="test_agent",
            type=AgentType.CUSTOM,
            description="Test agent"
        )

        registry.register(defn, simple_executor)

        result = await registry.execute(
            "test_agent",
            {"code": "test"}
        )

        assert result["success"] is True
        assert "processed" in result["result"]["result"]

    @pytest.mark.asyncio
    async def test_execute_nonexistent_agent(self, registry):
        """Test executing nonexistent agent"""
        with pytest.raises(ValueError):
            await registry.execute("nonexistent", {})

    @pytest.mark.asyncio
    async def test_execute_timeout(self, registry):
        """Test agent timeout"""
        async def slow_executor(inputs, context):
            await asyncio.sleep(2)
            return {"result": "done"}

        defn = AgentDefinition(
            name="slow_agent",
            type=AgentType.CUSTOM,
            description="Slow agent",
            timeout=1
        )

        registry.register(defn, slow_executor)

        result = await registry.execute("slow_agent", {})

        assert result["success"] is False
        assert "timeout" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_execute_with_context(self, registry):
        """Test executing with context"""
        async def context_executor(inputs, context):
            return {"result": context.get("user", "unknown")}

        defn = AgentDefinition(
            name="context_agent",
            type=AgentType.CUSTOM,
            description="Context agent"
        )

        registry.register(defn, context_executor)

        result = await registry.execute(
            "context_agent",
            {},
            context={"user": "alice"}
        )

        assert result["result"]["result"] == "alice"

    def test_agent_parameters(self, registry, simple_executor):
        """Test agent with parameters"""
        defn = AgentDefinition(
            name="param_agent",
            type=AgentType.CUSTOM,
            description="Agent with params",
            parameters=[
                AgentParameter(
                    name="code",
                    type="string",
                    description="Code to analyze",
                    required=True
                ),
                AgentParameter(
                    name="language",
                    type="string",
                    description="Language",
                    required=False,
                    default="python",
                    enum=["python", "javascript"]
                )
            ]
        )

        registry.register(defn, simple_executor)

        agent = registry.get_agent("param_agent")
        assert len(agent.definition.parameters) == 2
        assert agent.definition.parameters[0].required is True
        assert agent.definition.parameters[1].default == "python"

    def test_agent_outputs(self, registry, simple_executor):
        """Test agent output specifications"""
        defn = AgentDefinition(
            name="output_agent",
            type=AgentType.CUSTOM,
            description="Agent with outputs",
            outputs=[
                AgentOutput(
                    name="result",
                    type="string",
                    description="Analysis result"
                ),
                AgentOutput(
                    name="score",
                    type="number",
                    description="Confidence score"
                )
            ]
        )

        registry.register(defn, simple_executor)

        agent = registry.get_agent("output_agent")
        assert len(agent.definition.outputs) == 2

    def test_export_registry(self, registry, simple_executor):
        """Test exporting registry"""
        defn = AgentDefinition(
            name="export_agent",
            type=AgentType.CUSTOM,
            description="Agent for export",
            parameters=[
                AgentParameter(
                    name="input",
                    type="string",
                    description="Input"
                )
            ]
        )

        registry.register(defn, simple_executor)

        exported = registry.to_dict()

        assert len(exported["agents"]) == 1
        assert exported["agents"][0]["name"] == "export_agent"
        assert len(exported["agents"][0]["parameters"]) == 1


class TestAgentDefinition:
    """Test agent definition"""

    def test_create_definition(self):
        """Test creating agent definition"""
        defn = AgentDefinition(
            name="test",
            type=AgentType.SECURITY_AUDITOR,
            description="Test agent",
            version="1.0.0",
            timeout=60,
            tags=["security", "analysis"]
        )

        assert defn.name == "test"
        assert defn.type == AgentType.SECURITY_AUDITOR
        assert "security" in defn.tags
        assert defn.timeout == 60

    def test_definition_with_dependencies(self):
        """Test definition with dependencies"""
        defn = AgentDefinition(
            name="dependent",
            type=AgentType.CUSTOM,
            description="Dependent agent",
            dependencies=["base_agent", "analysis_agent"]
        )

        assert len(defn.dependencies) == 2
        assert "base_agent" in defn.dependencies


class TestAgentParameter:
    """Test agent parameters"""

    def test_required_parameter(self):
        """Test required parameter"""
        param = AgentParameter(
            name="code",
            type="string",
            description="Code input",
            required=True
        )

        assert param.required is True
        assert param.default is None

    def test_optional_parameter(self):
        """Test optional parameter"""
        param = AgentParameter(
            name="language",
            type="string",
            description="Language",
            required=False,
            default="python",
            enum=["python", "javascript", "go"]
        )

        assert param.required is False
        assert param.default == "python"
        assert len(param.enum) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
