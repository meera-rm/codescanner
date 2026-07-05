"""
Parallel Improvement Orchestrator - Phase 4.4
Coordinates parallel agent execution and PR creation
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from api.services.parallel_agent_executor import (
    ParallelAgentExecutor,
    AgentType,
    AgentSuggestion,
)
from api.services.iteration_pr_manager import IterationPRManager
from api.services.github_integration import GitHubConfig

logger = logging.getLogger(__name__)


@dataclass
class ParallelImprovementResult:
    """Result of parallel improvement orchestration"""
    success: bool
    total_agents: int
    successful_agents: int
    failed_agents: int
    suggestions: List[AgentSuggestion]
    merged_suggestion: Optional[AgentSuggestion] = None
    pr_results: Optional[List[Dict[str, Any]]] = None
    combined_pr_url: Optional[str] = None
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None


class ParallelImprovementOrchestrator:
    """Orchestrate parallel agent execution and PR creation"""

    def __init__(
        self,
        codebase_path: str,
        github_config: Optional[GitHubConfig] = None,
    ):
        self.codebase_path = codebase_path
        self.agent_executor = ParallelAgentExecutor()
        self.pr_manager = IterationPRManager(codebase_path, github_config)
        self.github_config = github_config

    def register_agent(
        self,
        agent_type: AgentType,
        agent_name: str,
        agent_func: callable,
    ) -> None:
        """Register an agent with the executor"""
        self.agent_executor.register_agent(agent_type, agent_name, agent_func)
        logger.info(f"Registered agent: {agent_name}")

    async def execute_and_create_prs(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        pr_title_template: str = "CodePulse: {description}",
        create_individual_prs: bool = False,
        auto_merge: bool = False,
    ) -> ParallelImprovementResult:
        """
        Execute agents in parallel and create PR(s).

        Args:
            code: Source code to analyze
            context: Additional context (file path, etc.)
            pr_title_template: Template for PR titles
            create_individual_prs: Create separate PR for each agent (vs. merged PR)
            auto_merge: Auto-merge PRs if validation passes

        Returns:
            ParallelImprovementResult with all details
        """
        try:
            start_time = datetime.now()

            # Step 1: Execute agents in parallel
            logger.info("Step 1: Executing agents in parallel...")
            exec_result = await self.agent_executor.execute_all(code, context)

            if not exec_result.success:
                logger.error(f"Agent execution failed: {exec_result.errors}")
                return ParallelImprovementResult(
                    success=False,
                    total_agents=exec_result.total_agents,
                    successful_agents=exec_result.completed_agents,
                    failed_agents=exec_result.failed_agents,
                    suggestions=exec_result.suggestions,
                    error_message="Agent execution failed",
                )

            logger.info(
                f"Executed {exec_result.completed_agents}/{exec_result.total_agents} agents"
            )

            # Step 2: Create PR(s)
            logger.info("Step 2: Creating PR(s)...")
            pr_results = []

            if create_individual_prs:
                # Create separate PR for each agent
                for suggestion in exec_result.suggestions:
                    pr_result = await self._create_pr_for_suggestion(
                        suggestion,
                        pr_title_template,
                        auto_merge,
                    )
                    pr_results.append(pr_result)

                combined_pr_url = None
            else:
                # Create single merged PR
                pr_result = await self._create_pr_for_merged_suggestion(
                    exec_result.merged_suggestion,
                    exec_result.suggestions,
                    pr_title_template,
                    auto_merge,
                )
                pr_results = [pr_result] if pr_result else []
                combined_pr_url = pr_result.get("pr_url") if pr_result else None

            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

            logger.info(f"Orchestration complete in {elapsed_ms:.0f}ms")

            return ParallelImprovementResult(
                success=True,
                total_agents=exec_result.total_agents,
                successful_agents=exec_result.completed_agents,
                failed_agents=exec_result.failed_agents,
                suggestions=exec_result.suggestions,
                merged_suggestion=exec_result.merged_suggestion,
                pr_results=pr_results,
                combined_pr_url=combined_pr_url,
                execution_time_ms=elapsed_ms,
            )

        except Exception as e:
            logger.error(f"Error in execute_and_create_prs: {e}")
            return ParallelImprovementResult(
                success=False,
                total_agents=0,
                successful_agents=0,
                failed_agents=0,
                suggestions=[],
                error_message=str(e),
            )

    async def _create_pr_for_suggestion(
        self,
        suggestion: AgentSuggestion,
        title_template: str,
        auto_merge: bool,
    ) -> Dict[str, Any]:
        """Create PR for a single suggestion"""
        try:
            pr_title = title_template.format(
                description=suggestion.description,
                agent=suggestion.agent_name,
            )

            pr_description = self._build_pr_description_from_suggestion(suggestion)

            # Convert suggestion to compatible format
            suggestion_dict = {
                "agent": suggestion.agent_name,
                "description": suggestion.description,
                "changes": suggestion.changes,
                "new_imports": suggestion.new_imports,
                "modified_code": suggestion.modified_code,
            }

            result = await self.pr_manager.apply_and_create_pr(
                suggestion_dict,
                pr_title=pr_title,
                pr_description=pr_description,
                auto_merge=auto_merge,
            )

            return {
                "pr_number": result.pr_number,
                "pr_url": result.pr_url,
                "branch_name": result.branch_name,
                "agent_name": suggestion.agent_name,
                "success": result.success,
                "validation_passed": result.validation_passed,
            }

        except Exception as e:
            logger.error(f"Error creating PR for {suggestion.agent_name}: {e}")
            return {
                "agent_name": suggestion.agent_name,
                "success": False,
                "error": str(e),
            }

    async def _create_pr_for_merged_suggestion(
        self,
        merged: AgentSuggestion,
        all_suggestions: List[AgentSuggestion],
        title_template: str,
        auto_merge: bool,
    ) -> Optional[Dict[str, Any]]:
        """Create PR for merged suggestion"""
        try:
            if not merged:
                logger.warning("No merged suggestion to create PR for")
                return None

            pr_title = title_template.format(
                description="Combined improvements",
                agent="Parallel",
            )

            pr_description = self._build_pr_description_merged(merged, all_suggestions)

            # Convert to compatible format
            suggestion_dict = {
                "agent": "ParallelMerge",
                "description": merged.description,
                "changes": merged.changes,
                "new_imports": merged.new_imports,
                "modified_code": merged.modified_code,
            }

            result = await self.pr_manager.apply_and_create_pr(
                suggestion_dict,
                pr_title=pr_title,
                pr_description=pr_description,
                auto_merge=auto_merge,
            )

            return {
                "pr_number": result.pr_number,
                "pr_url": result.pr_url,
                "branch_name": result.branch_name,
                "agent_name": "ParallelMerge",
                "success": result.success,
                "validation_passed": result.validation_passed,
                "contributing_agents": [s.agent_name for s in all_suggestions],
            }

        except Exception as e:
            logger.error(f"Error creating merged PR: {e}")
            return None

    def _build_pr_description_from_suggestion(self, suggestion: AgentSuggestion) -> str:
        """Build PR description from suggestion"""
        sections = [
            f"**Agent:** {suggestion.agent_name}",
            f"**Description:** {suggestion.description}",
            "",
            "## Changes",
            f"- Complexity reduction: {suggestion.complexity_reduction}%",
            f"- Risk level: {suggestion.risk_level}",
            f"- Clarity improvement: {suggestion.clarity_improvement}",
            f"- Estimated time: {suggestion.estimated_time}",
            f"- Confidence score: {suggestion.confidence_score:.1%}",
            "",
            f"## Rationale",
            suggestion.rationale,
        ]

        return "\n".join(sections)

    def _build_pr_description_merged(
        self,
        merged: AgentSuggestion,
        all_suggestions: List[AgentSuggestion],
    ) -> str:
        """Build PR description for merged suggestion"""
        sections = [
            "## Parallel Agent Improvements",
            f"Combined suggestions from {len(all_suggestions)} agents",
            "",
            "## Contributing Agents",
        ]

        for suggestion in all_suggestions:
            sections.append(
                f"- **{suggestion.agent_name}**: {suggestion.description} "
                f"(confidence: {suggestion.confidence_score:.1%})"
            )

        sections.extend([
            "",
            "## Combined Changes",
            f"- Complexity reduction: {merged.complexity_reduction}%",
            f"- Risk level: {merged.risk_level}",
            f"- Clarity improvement: {merged.clarity_improvement}",
            f"- Estimated time: {merged.estimated_time}",
            f"- Confidence score: {merged.confidence_score:.1%}",
            "",
            "## Implementation Strategy",
            merged.rationale,
        ])

        return "\n".join(sections)

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "codebase_path": self.codebase_path,
            "registered_agents": self.agent_executor.get_status()["registered_agents"],
            "agent_names": self.agent_executor.get_status()["agent_names"],
            "github_configured": self.github_config is not None,
        }


# Factory function
def get_parallel_improvement_orchestrator(
    codebase_path: str,
    github_config: Optional[GitHubConfig] = None,
) -> ParallelImprovementOrchestrator:
    """Create ParallelImprovementOrchestrator instance"""
    return ParallelImprovementOrchestrator(codebase_path, github_config)
