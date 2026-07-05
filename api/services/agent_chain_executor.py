"""
Agent Chain Executor - Phase 5.1
Executes sequences and conditional flows of agents
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging

from .agent_registry import AgentRegistry, get_registry


logger = logging.getLogger(__name__)


class ConditionOperator(str, Enum):
    """Condition operators"""
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"


@dataclass
class Condition:
    """Chain condition"""
    field: str  # output field to check
    operator: ConditionOperator
    value: Any
    agent: str = ""  # which agent's output to check

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition"""
        if self.agent:
            if self.agent not in context:
                return False
            actual = context[self.agent].get(self.field)
        else:
            actual = context.get(self.field)

        if actual is None:
            return False

        if self.operator == ConditionOperator.EQ:
            return actual == self.value
        elif self.operator == ConditionOperator.NE:
            return actual != self.value
        elif self.operator == ConditionOperator.GT:
            return actual > self.value
        elif self.operator == ConditionOperator.LT:
            return actual < self.value
        elif self.operator == ConditionOperator.GTE:
            return actual >= self.value
        elif self.operator == ConditionOperator.LTE:
            return actual <= self.value
        elif self.operator == ConditionOperator.IN:
            return actual in self.value
        elif self.operator == ConditionOperator.NOT_IN:
            return actual not in self.value
        elif self.operator == ConditionOperator.CONTAINS:
            return self.value in actual
        else:
            return False


@dataclass
class ChainStep:
    """Single step in chain"""
    agent_name: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    timeout: Optional[int] = None

    # Conditional execution
    conditions: List[Condition] = field(default_factory=list)

    # Error handling
    on_failure: Optional[str] = None  # next step to execute on failure
    continue_on_error: bool = False


@dataclass
class ChainDefinition:
    """Agent chain definition"""
    name: str
    description: str
    version: str = "1.0.0"
    steps: List[ChainStep] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChainExecution:
    """Execution result of a chain"""
    chain_name: str
    success: bool
    steps_executed: int
    total_steps: int
    results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    execution_time: float = 0.0


class AgentChainExecutor:
    """Execute chains of agents"""

    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry or get_registry()
        self.chains: Dict[str, ChainDefinition] = {}

    def register_chain(self, chain: ChainDefinition) -> None:
        """Register a chain"""
        if chain.name in self.chains:
            raise ValueError(f"Chain '{chain.name}' already registered")

        self.chains[chain.name] = chain

    def get_chain(self, name: str) -> Optional[ChainDefinition]:
        """Get chain by name"""
        return self.chains.get(name)

    async def execute(
        self,
        chain_name: str,
        inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ChainExecution:
        """Execute a chain"""
        chain = self.get_chain(chain_name)
        if not chain:
            raise ValueError(f"Chain '{chain_name}' not found")

        execution = ChainExecution(
            chain_name=chain_name,
            success=True,
            steps_executed=0,
            total_steps=len(chain.steps),
            results={},
            errors={}
        )

        ctx = context or {}
        current_inputs = inputs.copy()

        for i, step in enumerate(chain.steps):
            execution.steps_executed += 1

            # Check conditions
            if step.conditions:
                all_conditions_met = all(
                    cond.evaluate(ctx) for cond in step.conditions
                )
                if not all_conditions_met:
                    logger.debug(
                        f"Chain '{chain_name}': skipping step {i+1} "
                        f"({step.agent_name}) - conditions not met"
                    )
                    continue

            # Merge agent outputs into inputs for next step
            for agent_name, result in ctx.items():
                if isinstance(result, dict) and "result" in result:
                    current_inputs[agent_name] = result["result"]

            # Execute agent
            try:
                result = await self.registry.execute(
                    step.agent_name,
                    current_inputs,
                    ctx
                )

                ctx[step.agent_name] = result
                execution.results[step.agent_name] = result

                if not result.get("success", False):
                    execution.errors[step.agent_name] = result.get("error", "Unknown error")

                    if step.on_failure:
                        # Skip to on_failure step
                        logger.warning(
                            f"Chain '{chain_name}': step {i+1} failed, "
                            f"jumping to '{step.on_failure}'"
                        )
                        continue
                    elif not step.continue_on_error:
                        execution.success = False
                        return execution

            except Exception as e:
                error_msg = str(e)
                execution.errors[step.agent_name] = error_msg
                logger.error(
                    f"Chain '{chain_name}': step {i+1} exception: {error_msg}"
                )

                if not step.continue_on_error:
                    execution.success = False
                    return execution

        return execution

    async def execute_parallel(
        self,
        chains: List[str],
        inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[ChainExecution]:
        """Execute multiple chains in parallel"""
        tasks = [
            self.execute(chain_name, inputs, context)
            for chain_name in chains
        ]
        return await asyncio.gather(*tasks)

    def export_chain(self, name: str) -> Dict[str, Any]:
        """Export chain definition as dict"""
        chain = self.get_chain(name)
        if not chain:
            raise ValueError(f"Chain '{name}' not found")

        return {
            "name": chain.name,
            "description": chain.description,
            "version": chain.version,
            "steps": [
                {
                    "agent_name": step.agent_name,
                    "inputs": step.inputs,
                    "description": step.description,
                    "timeout": step.timeout,
                    "conditions": [
                        {
                            "field": c.field,
                            "operator": c.operator.value,
                            "value": c.value,
                            "agent": c.agent
                        }
                        for c in step.conditions
                    ],
                    "on_failure": step.on_failure,
                    "continue_on_error": step.continue_on_error
                }
                for step in chain.steps
            ],
            "tags": chain.tags,
            "metadata": chain.metadata
        }
