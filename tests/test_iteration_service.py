"""Tests for Phase 3.5B: Orchestration Service and Validator."""

import pytest
from api.services.iteration_clean_service import (
    IterationCleanService,
    IterationStep,
    IterationResult,
)
from api.services.agents import ValidatorAgent
from api.services.agents.refactoring_agent import Issue, Suggestion


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def validator():
    """Validator agent instance."""
    return ValidatorAgent()


@pytest.fixture
def iteration_service():
    """IterationCleanService instance."""
    return IterationCleanService()


@pytest.fixture
def sample_suggestion():
    """Sample suggestion for validation."""
    return Suggestion(
        agent="Agent A (Simplicity First)",
        description="Extract helper functions",
        changes=["New: check_syntax()", "New: check_logic()"],
        complexity_reduction=60,
        risk_level="low",
        clarity_improvement="good",
        estimated_time="quick",
        modified_code="def check_syntax():\n    pass",
        new_imports=["ast"],
    )


# ============================================================================
# Test Validator Agent
# ============================================================================

@pytest.mark.asyncio
async def test_validator_validates_good_suggestion(validator, sample_suggestion):
    """Test that validator approves good suggestions."""
    result = await validator.validate(sample_suggestion)
    assert result.approved
    assert len(result.checks) > 0
    assert all(c.passed for c in result.checks)


@pytest.mark.asyncio
async def test_validator_check_names(validator, sample_suggestion):
    """Test that all validation checks are performed."""
    result = await validator.validate(sample_suggestion)
    check_names = [c.check_name for c in result.checks]

    expected_checks = [
        "Syntax Check",
        "Import Validation",
        "Logic Preservation",
        "Test Regression",
        "Performance Impact",
    ]

    assert all(name in check_names for name in expected_checks)


@pytest.mark.asyncio
async def test_validator_detects_syntax_error(validator):
    """Test that validator catches syntax errors."""
    bad_suggestion = Suggestion(
        agent="Agent A",
        description="Bad code",
        changes=["Invalid: def broken("],
        complexity_reduction=50,
        risk_level="low",
        clarity_improvement="ok",
        estimated_time="quick",
        modified_code="def broken(",  # Invalid Python
        new_imports=[],
    )

    result = await validator.validate(bad_suggestion)
    assert not result.approved
    syntax_check = next((c for c in result.checks if c.check_name == "Syntax Check"), None)
    assert syntax_check and not syntax_check.passed


@pytest.mark.asyncio
async def test_validator_detects_missing_imports(validator):
    """Test that validator detects missing imports."""
    suggestion = Suggestion(
        agent="Agent A",
        description="Use nonexistent library",
        changes=["Import: nonexistent_lib"],
        complexity_reduction=50,
        risk_level="low",
        clarity_improvement="ok",
        estimated_time="quick",
        modified_code="def foo():\n    pass",
        new_imports=["nonexistent_module_12345"],
    )

    result = await validator.validate(suggestion)
    assert not result.approved
    import_check = next((c for c in result.checks if c.check_name == "Import Validation"), None)
    assert import_check and not import_check.passed


@pytest.mark.asyncio
async def test_validator_summary_format(validator, sample_suggestion):
    """Test that validator generates proper summary."""
    result = await validator.validate(sample_suggestion)
    assert "APPROVED" in result.summary or "REJECTED" in result.summary
    assert "/" in result.summary  # Contains "X/Y checks passed"


# ============================================================================
# Test Iteration Service
# ============================================================================

@pytest.mark.asyncio
async def test_iteration_service_init(iteration_service):
    """Test that iteration service initializes with all agents."""
    assert iteration_service.agent_a is not None
    assert iteration_service.agent_b is not None
    assert iteration_service.agent_c is not None
    assert iteration_service.evaluator is not None
    assert iteration_service.validator is not None


@pytest.mark.asyncio
async def test_grade_value_conversion(iteration_service):
    """Test grade to numeric value conversion."""
    assert iteration_service._grade_value("A") == 4.0
    assert iteration_service._grade_value("B") == 3.0
    assert iteration_service._grade_value("C") == 2.0
    assert iteration_service._grade_value("D") == 1.0
    assert iteration_service._grade_value("F") == 0.0


@pytest.mark.asyncio
async def test_grade_value_with_suffix(iteration_service):
    """Test grade conversion with +/- suffix."""
    assert iteration_service._grade_value("A-") > iteration_service._grade_value("A")
    assert iteration_service._grade_value("B-") == pytest.approx(3.5)
    assert iteration_service._grade_value("A+") > iteration_service._grade_value("A")


@pytest.mark.asyncio
async def test_scan_codebase_placeholder(iteration_service):
    """Test that scan codebase returns mock data when no scanner."""
    result = await iteration_service._scan_codebase("/code")
    assert "grade" in result
    assert "issues" in result
    assert "metrics" in result


@pytest.mark.asyncio
async def test_get_suggestions_with_issues(iteration_service):
    """Test getting suggestions from all agents."""
    issues = [
        Issue(
            issue_type="complexity",
            file_path="test.py",
            line_number=10,
            description="Too complex",
            severity="high",
            complexity=25,
            affected_function="foo",
        )
    ]

    suggestions = await iteration_service._get_suggestions("/code", issues)
    assert len(suggestions) > 0
    assert len(suggestions) <= 3


@pytest.mark.asyncio
async def test_calculate_metrics_empty_history(iteration_service):
    """Test metrics calculation with empty history."""
    metrics = iteration_service._calculate_metrics([], {})
    assert metrics == {}


@pytest.mark.asyncio
async def test_calculate_metrics_with_history(iteration_service):
    """Test metrics calculation with iteration history."""
    history = [
        IterationStep(
            iteration_number=1,
            grade_before="C",
            grade_after="B",
            issues_fixed=5,
            agent_selected="Agent A",
            fix_description="Extract methods",
            validation_passed=True,
            changes={"complexity_reduction": 60},
        ),
        IterationStep(
            iteration_number=2,
            grade_before="B",
            grade_after="A",
            issues_fixed=3,
            agent_selected="Agent A",
            fix_description="Remove duplication",
            validation_passed=True,
            changes={"complexity_reduction": 45},
        ),
    ]

    metrics = iteration_service._calculate_metrics(history, {})
    assert metrics["total_iterations"] == 2
    assert metrics["total_issues_fixed"] == 8
    assert metrics["final_grade"] == "A"
    assert metrics["agents_used"] == ["Agent A"]


# ============================================================================
# Test Full Iteration Loop (Mocked)
# ============================================================================

@pytest.mark.asyncio
async def test_fix_until_clean_returns_result(iteration_service):
    """Test that fix_until_clean returns an IterationResult."""
    result = await iteration_service.fix_until_clean(
        job_id="test_job_1",
        codebase_path="/code",
        target_grade="A",
        max_iterations=5,
    )

    assert isinstance(result, IterationResult)
    assert result.job_id == "test_job_1"
    assert result.status in ["completed", "failed"]


@pytest.mark.asyncio
async def test_fix_until_clean_respects_max_iterations(iteration_service):
    """Test that iteration stops at max_iterations."""
    result = await iteration_service.fix_until_clean(
        job_id="test_job_2",
        codebase_path="/code",
        target_grade="A",
        max_iterations=3,
    )

    assert result.iterations_count <= 3
    assert result.max_iterations == 3


@pytest.mark.asyncio
async def test_fix_until_clean_has_timestamps(iteration_service):
    """Test that result includes timestamps."""
    result = await iteration_service.fix_until_clean(
        job_id="test_job_3",
        codebase_path="/code",
        target_grade="A",
        max_iterations=1,
    )

    assert result.started_at is not None
    assert result.completed_at is not None


# ============================================================================
# Test Iteration Step
# ============================================================================

def test_iteration_step_creation():
    """Test creating an iteration step."""
    step = IterationStep(
        iteration_number=1,
        grade_before="C",
        grade_after="B",
        issues_fixed=5,
        agent_selected="Agent A",
        fix_description="Extract methods",
        validation_passed=True,
    )

    assert step.iteration_number == 1
    assert step.grade_before == "C"
    assert step.grade_after == "B"
    assert step.issues_fixed == 5


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_workflow_validator_service(iteration_service, sample_suggestion):
    """Test complete workflow: service + validator."""
    # Get suggestions
    issues = []
    suggestions = await iteration_service._get_suggestions("/code", issues)

    # Validate one
    if suggestions:
        validation = await iteration_service.validator.validate(suggestions[0])
        assert "approved" in validation.approved
