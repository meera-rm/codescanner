"""
Agent Registry System - Phase 5.1
Manages custom agent definitions, loading, and execution
"""

from typing import Dict, List, Optional, Callable, Any, Coroutine
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio
from pathlib import Path
import yaml


class AgentType(str, Enum):
    """Built-in agent types"""
    SECURITY_AUDITOR = "security_auditor"
    PERFORMANCE_OPTIMIZER = "performance_optimizer"
    DOCUMENTATION_GENERATOR = "documentation_generator"
    CUSTOM = "custom"


class ExecutionMode(str, Enum):
    """Agent execution mode"""
    ASYNC = "async"
    SYNC = "sync"


@dataclass
class AgentParameter:
    """Parameter definition for an agent"""
    name: str
    type: str  # "string", "number", "boolean", "array"
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None


@dataclass
class AgentOutput:
    """Output specification for an agent"""
    name: str
    type: str
    description: str


@dataclass
class AgentDefinition:
    """Agent configuration"""
    name: str
    type: AgentType
    description: str
    version: str = "1.0.0"

    parameters: List[AgentParameter] = field(default_factory=list)
    outputs: List[AgentOutput] = field(default_factory=list)

    timeout: int = 60  # seconds
    max_retries: int = 3
    execution_mode: ExecutionMode = ExecutionMode.ASYNC

    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentInstance:
    """Registered agent instance"""
    definition: AgentDefinition
    executor: Callable[[Dict[str, Any], Dict[str, Any]], Coroutine]
    context: Dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """Registry for managing agents"""

    def __init__(self):
        self.agents: Dict[str, AgentInstance] = {}
        self.definitions: Dict[str, AgentDefinition] = {}

    def register(
        self,
        definition: AgentDefinition,
        executor: Callable[[Dict[str, Any], Dict[str, Any]], Coroutine]
    ) -> None:
        """Register a new agent"""
        if definition.name in self.agents:
            raise ValueError(f"Agent '{definition.name}' already registered")

        self.agents[definition.name] = AgentInstance(
            definition=definition,
            executor=executor
        )
        self.definitions[definition.name] = definition

    def unregister(self, name: str) -> None:
        """Unregister an agent"""
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' not found")

        del self.agents[name]
        del self.definitions[name]

    def get_agent(self, name: str) -> Optional[AgentInstance]:
        """Get agent by name"""
        return self.agents.get(name)

    def list_agents(self) -> List[AgentDefinition]:
        """List all registered agents"""
        return list(self.definitions.values())

    def get_agents_by_type(self, agent_type: AgentType) -> List[AgentDefinition]:
        """Get agents by type"""
        return [
            defn for defn in self.definitions.values()
            if defn.type == agent_type
        ]

    def get_agents_by_tag(self, tag: str) -> List[AgentDefinition]:
        """Get agents by tag"""
        return [
            defn for defn in self.definitions.values()
            if tag in defn.tags
        ]

    async def execute(
        self,
        agent_name: str,
        inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute an agent"""
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")

        ctx = {**agent.context, **(context or {})}

        try:
            if agent.definition.execution_mode == ExecutionMode.ASYNC:
                result = await asyncio.wait_for(
                    agent.executor(inputs, ctx),
                    timeout=agent.definition.timeout
                )
            else:
                result = agent.executor(inputs, ctx)

            return {
                "success": True,
                "agent": agent_name,
                "result": result,
                "metadata": {
                    "version": agent.definition.version,
                    "type": agent.definition.type.value
                }
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "agent": agent_name,
                "error": f"Agent execution timeout ({agent.definition.timeout}s)",
                "error_code": "TIMEOUT"
            }
        except Exception as e:
            return {
                "success": False,
                "agent": agent_name,
                "error": str(e),
                "error_code": "EXECUTION_ERROR"
            }

    def to_dict(self) -> Dict[str, Any]:
        """Export registry as dictionary"""
        return {
            "agents": [
                {
                    "name": defn.name,
                    "type": defn.type.value,
                    "description": defn.description,
                    "version": defn.version,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.type,
                            "description": p.description,
                            "required": p.required,
                            "default": p.default
                        }
                        for p in defn.parameters
                    ],
                    "outputs": [
                        {
                            "name": o.name,
                            "type": o.type,
                            "description": o.description
                        }
                        for o in defn.outputs
                    ]
                }
                for defn in self.definitions.values()
            ]
        }


class AgentLoader:
    """Load agents from YAML/JSON configuration"""

    @staticmethod
    def load_from_yaml(path: str) -> Dict[str, AgentDefinition]:
        """Load agent definitions from YAML"""
        with open(path) as f:
            data = yaml.safe_load(f)

        agents = {}
        for agent_data in data.get("agents", []):
            defn = AgentLoader._parse_definition(agent_data)
            agents[defn.name] = defn

        return agents

    @staticmethod
    def load_from_json(path: str) -> Dict[str, AgentDefinition]:
        """Load agent definitions from JSON"""
        with open(path) as f:
            data = json.load(f)

        agents = {}
        for agent_data in data.get("agents", []):
            defn = AgentLoader._parse_definition(agent_data)
            agents[defn.name] = defn

        return agents

    @staticmethod
    def _parse_definition(data: Dict[str, Any]) -> AgentDefinition:
        """Parse agent definition from dict"""
        parameters = [
            AgentParameter(
                name=p["name"],
                type=p["type"],
                description=p["description"],
                required=p.get("required", True),
                default=p.get("default"),
                enum=p.get("enum")
            )
            for p in data.get("parameters", [])
        ]

        outputs = [
            AgentOutput(
                name=o["name"],
                type=o["type"],
                description=o["description"]
            )
            for o in data.get("outputs", [])
        ]

        return AgentDefinition(
            name=data["name"],
            type=AgentType(data.get("type", "custom")),
            description=data["description"],
            version=data.get("version", "1.0.0"),
            parameters=parameters,
            outputs=outputs,
            timeout=data.get("timeout", 60),
            max_retries=data.get("max_retries", 3),
            execution_mode=ExecutionMode(data.get("execution_mode", "async")),
            dependencies=data.get("dependencies", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )


# Global registry instance
_global_registry = AgentRegistry()


def get_registry() -> AgentRegistry:
    """Get global registry"""
    return _global_registry
