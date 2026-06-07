"""Tests for Phase 3.5A: Agent System."""

import pytest
from api.services.agents import (
    AgentA_SimplityFirst,
    AgentB_ArchitectureFocused,
    AgentC_PerformanceOptimized,
    EvaluationAgent,
)
from api.services.agents.refactoring_agent import Issue


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_issues():
    """Sample issues for testing."""
    return [
        Issue(
            issue_type="complexity",
            file_path="scanner.py",
            line_number=45,
            description="Function analyze_code() too complex",
            severity="high",
            complexity=28,
            affected_function="analyze_code"
        ),
        Issue(
            issue_type="duplication",
            file_path="scanner.py",
            line_number=100,
            description="Code duplication detected",
            severity="medium",
            complexity=15,
            affected_function="check_syntax"
        ),
        Issue(
            issue_type="security",
            file_path="auth.py",
            line_number=50,
            description="Hardcoded secret detected",
            severity="critical",
            complexity=5,
            affected_function="authenticate"
        ),
    ]


@pytest.fixture
def agent_a():
    """Agent A instance."""
    return AgentA_SimplityFirst()


@pytest.fixture
def agent_b():
    """Agent B instance."""
    return AgentB_ArchitectureFocused()


@pytest.fixture
def agent_c():
    """Agent C instance."""
    return AgentC_PerformanceOptimized()


@pytest.fixture
def evaluator():
    """Evaluator instance."""
    return EvaluationAgent()


# ============================================================================
# Test Agent A (Simplicity First)
# ============================================================================

@pytest.mark.asyncio
async def test_agent_a_returns_suggestion(agent_a, sample_issues):
    """Test that Agent A generates a suggestion."""
    suggestion = await agent_a.suggest_refactoring(
        "/code",
        sample_issues
    )
    assert suggestion is not None
    assert suggestion.agent == "Agent A (Simplicity First)"


@pytest.mark.asyncio
async def test_agent_a_suggestion_format(agent_a, sample_issues):
    """Test that Agent A suggestion has correct format."""
    suggestion = await agent_a.suggest_refactoring(
        "/code",
        sample_issues
    )
    assert hasattr(suggestion, "description")
    assert hasattr(suggestion, "changes")
    assert hasattr(suggestion, "complexity_reduction")
    assert hasattr(suggestion, "risk_level")
    assert hasattr(suggestion, "clarity_improvement")
    assert hasattr(suggestion, "estimated_time")


@pytest.mark.asyncio
async def test_agent_a_low_risk(agent_a, sample_issues):
    """Test that Agent A has low risk level."""
    suggestion = await agent_a.suggest_refactoring(
        "/code",
        sample_issues
    )
    assert suggestion.risk_level == "low"


@pytest.mark.asyncio
async def test_agent_a_no_issues(agent_a):
    """Test Agent A with no issues."""
    suggestion = await agent_a.suggest_refactoring("/code", [])
    assert suggestion is None


# ============================================================================
# Test Agent B (Architecture Focused)
# ============================================================================

@pytest.mark.asyncio
async def test_agent_b_returns_suggestion(agent_b, sample_issues):
    """Test that Agent B generates a suggestion."""
    suggestion = await agent_b.suggest_refactoring(
        "/code",
        sample_issues
    )
    assert suggestion is not None
    assert suggestion.agent == "Agent B (Architecture Focused)"


@pytest.mark.asyncio
async def test_agent_b_higher_complexity_reduction(agent_b, sample_issues):
    """Test that Agent B suggests higher complexity reduction."""
    suggestion = await agent_b.suggest_refactoring(
        "/code",
        sample_issues
    )
    assert suggestion.complexity_reduction >= 50


@pytest.mark.asyncio
async def test_agent_b_varying_risk(agent_b, sample_issues):
    """Test that Agent B may have medium to high risk."""
    suggestion = await agent_b.suggest_refactoring(
        "/code",
        sample_issues
    )
    assert suggestion.risk_level in ["medium", "low", "high"]


# ============================================================================
# Test Agent C (Performance Optimized)
# ============================================================================

@pytest.mark.asyncio
async def test_agent_c_returns_suggestion(agent_c, sample_issues):
    """Test that Agent C generates a suggestion."""
    suggestion = await agent_c.suggest_refactoring(
        "/code",
        sample_issues
    )
    assert suggestion is not None
    assert suggestion.agent == "Agent C (Performance Optimized)"


@pytest.mark.asyncio
async def test_agent_c_low_risk(agent_c, sample_issues):
    """Test that Agent C has low risk level."""
    suggestion = await agent_c.suggest_refactoring(
        "/code",
        sample_issues
    )
    assert suggestion.risk_level == "low"


# ============================================================================
# Test Evaluation Agent
# ============================================================================

@pytest.mark.asyncio
async def test_evaluator_picks_best(evaluator, agent_a, agent_b, agent_c, sample_issues):
    """Test that evaluator can pick best suggestion."""
    suggestions = [
        await agent_a.suggest_refactoring("/code", sample_issues),
        await agent_b.suggest_refactoring("/code", sample_issues),
        await agent_c.suggest_refactoring("/code", sample_issues),
    ]
    suggestions = [s for s in suggestions if s]  # Remove None values

    best = evaluator.pick_best(suggestions)
    assert best is not None
    assert best in suggestions


def test_evaluator_risk_scoring():
    """Test risk level scoring."""
    evaluator = EvaluationAgent()
    assert evaluator._risk_to_score("low") == 100
    assert evaluator._risk_to_score("medium") == 60
    assert evaluator._risk_to_score("high") == 20


def test_evaluator_clarity_scoring():
    """Test clarity level scoring."""
    evaluator = EvaluationAgent()
    assert evaluator._clarity_to_score("excellent") == 100
    assert evaluator._clarity_to_score("good") == 75
    assert evaluator._clarity_to_score("ok") == 50


def test_evaluator_time_scoring():
    """Test time estimate scoring."""
    evaluator = EvaluationAgent()
    assert evaluator._time_to_score("quick") == 100
    assert evaluator._time_to_score("medium") == 75
    assert evaluator._time_to_score("slow") == 50


@pytest.mark.asyncio
async def test_evaluator_score_all(evaluator, agent_a, agent_b, agent_c, sample_issues):
    """Test evaluator can score all suggestions."""
    suggestions = [
        await agent_a.suggest_refactoring("/code", sample_issues),
        await agent_b.suggest_refactoring("/code", sample_issues),
        await agent_c.suggest_refactoring("/code", sample_issues),
    ]
    suggestions = [s for s in suggestions if s]

    scored = evaluator.score_all(suggestions)
    assert len(scored) == len(suggestions)
    assert all(hasattr(s, "score") for s in scored)
    assert all(s.score >= 0 for s in scored)


def test_evaluator_weights_sum_to_one():
    """Test that evaluator weights sum to 1.0."""
    evaluator = EvaluationAgent()
    total = sum(evaluator.WEIGHTS.values())
    assert abs(total - 1.0) < 0.001


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_all_agents_work(sample_issues):
    """Test that all 3 agents can generate suggestions."""
    agents = [
        AgentA_SimplityFirst(),
        AgentB_ArchitectureFocused(),
        AgentC_PerformanceOptimized(),
    ]

    for agent in agents:
        suggestion = await agent.suggest_refactoring("/code", sample_issues)
        assert suggestion is not None
        assert suggestion.agent != ""
        assert suggestion.description != ""
        assert len(suggestion.changes) > 0


@pytest.mark.asyncio
async def test_evaluation_workflow(sample_issues):
    """Test complete evaluation workflow."""
    agents = [
        AgentA_SimplityFirst(),
        AgentB_ArchitectureFocused(),
        AgentC_PerformanceOptimized(),
    ]
    evaluator = EvaluationAgent()

    # Get suggestions from all agents
    suggestions = [
        await agent.suggest_refactoring("/code", sample_issues)
        for agent in agents
    ]
    suggestions = [s for s in suggestions if s]

    # Evaluate and pick best
    best = evaluator.pick_best(suggestions)
    assert best is not None
    assert best.agent in [s.agent for s in suggestions]
