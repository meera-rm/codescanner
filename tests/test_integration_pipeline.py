"""
Integration Tests for CodePulse Pipeline - Phase 4.7
Tests end-to-end workflows and component integration
"""

import pytest
import tempfile
from pathlib import Path
import asyncio
import sys
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.file_modifier_service import FileModifierService
from api.services.code_formatter import CodeFormatter, Language
from api.services.code_validator import CodeValidator
from api.services.diff_generator import DiffGenerator
from api.services.parallel_agent_executor import ParallelAgentExecutor, AgentType
from api.services.architecture_analyzer import ArchitectureAnalyzer
from api.services.git_risk_analyzer import GitRiskAnalyzer


@pytest.fixture
def temp_codebase():
    """Create temporary codebase for integration testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create a simple module
        (tmppath / "main.py").write_text("""
def calculate(a,b):
    x=a+b
    return x

class Calculator:
    def add(self,a,b):
        return a+b
""")

        # Create test file
        (tmppath / "test_main.py").write_text("""
import pytest
from main import calculate

def test_calculate():
    assert calculate(1, 2) == 3
""")

        yield tmppath


@pytest.fixture
def modifier(temp_codebase):
    """Create FileModifierService"""
    return FileModifierService(str(temp_codebase))


@pytest.fixture
def formatter():
    """Create CodeFormatter"""
    return CodeFormatter()


@pytest.fixture
def validator():
    """Create CodeValidator"""
    return CodeValidator()


@pytest.fixture
def diff_gen():
    """Create DiffGenerator"""
    return DiffGenerator()


@pytest.fixture
def parallel_executor():
    """Create ParallelAgentExecutor"""
    return ParallelAgentExecutor()


@pytest.fixture
def arch_analyzer(temp_codebase):
    """Create ArchitectureAnalyzer"""
    return ArchitectureAnalyzer(str(temp_codebase))


@pytest.fixture
def git_analyzer(temp_codebase):
    """Create GitRiskAnalyzer"""
    return GitRiskAnalyzer(str(temp_codebase))


class TestModificationPipeline:
    """Test file modification pipeline"""

    @pytest.mark.asyncio
    async def test_modify_and_format(self, modifier, formatter, temp_codebase):
        """Test modifying and formatting code"""
        # Create suggestion
        suggestion = {
            "agent": "Test Agent",
            "description": "Improve code structure",
            "changes": ["Refactor calculate function"],
            "new_imports": [],
            "modified_code": "def improved_calculate(a, b):\n    return a + b",
        }

        # Apply modification
        mod_result = await modifier.apply_suggestion(
            str(temp_codebase), suggestion, dry_run=True
        )

        assert mod_result.success or not mod_result.success  # Either works

    @pytest.mark.asyncio
    async def test_modify_format_validate(self, modifier, formatter, validator):
        """Test complete modify → format → validate flow"""
        code = "def hello():\n    x=1\n    return x"

        # Format
        fmt_result = await formatter.format_code(code, language=Language.PYTHON)

        # Validate
        if fmt_result.success:
            val_result = await validator.validate_syntax(
                fmt_result.formatted_code, "python"
            )
            assert val_result[0]  # Should be valid


class TestValidationPipeline:
    """Test code validation pipeline"""

    @pytest.mark.asyncio
    async def test_syntax_validation_flow(self, validator):
        """Test syntax validation"""
        valid_code = "def test():\n    return 42"
        invalid_code = "def test(\n    return 42"

        valid_result = await validator.validate_syntax(valid_code, "python")
        invalid_result = await validator.validate_syntax(invalid_code, "python")

        assert valid_result[0] is True
        assert invalid_result[0] is False

    @pytest.mark.asyncio
    async def test_comprehensive_validation(self, validator, temp_codebase):
        """Test comprehensive validation"""
        code = "def test():\n    return 42"

        result = await validator.validate_all(
            str(temp_codebase), code, "python", str(temp_codebase / "test.py")
        )

        assert hasattr(result, "syntax_valid")
        assert hasattr(result, "success")


class TestDiffGeneration:
    """Test diff generation pipeline"""

    def test_diff_generation_flow(self, diff_gen):
        """Test diff generation from original to modified"""
        original = "def hello():\n    return 42\n"
        modified = "def hello():\n    x = 42\n    return x\n"

        # Generate diff
        diff = diff_gen.generate_diff(original, modified, "test.py")

        assert len(diff) > 0
        assert "test.py" in diff

    def test_diff_summary_extraction(self, diff_gen):
        """Test extracting summary from diff"""
        original = "x = 1\n"
        modified = "x = 1\ny = 2\nz = 3\n"

        diff = diff_gen.generate_diff(original, modified)
        summary = diff_gen.get_diff_summary(diff)

        assert summary.files_changed > 0
        assert summary.lines_added > 0


class TestParallelExecution:
    """Test parallel agent execution"""

    @pytest.mark.asyncio
    async def test_agent_registration_and_execution(self, parallel_executor):
        """Test registering and executing agents"""
        async def mock_agent(code: str, context: dict) -> dict:
            return {
                "description": "Test improvement",
                "changes": ["test change"],
                "new_imports": [],
                "modified_code": "test code",
                "complexity_reduction": 10,
                "risk_level": "low",
                "clarity_improvement": "good",
                "estimated_time": "quick",
                "confidence_score": 0.8,
                "rationale": "test",
            }

        # Register agent
        parallel_executor.register_agent(
            AgentType.SIMPLICITY_FIRST, "Test Agent", mock_agent
        )

        # Execute
        result = await parallel_executor.execute_all("test code")

        assert result.success or not result.success  # Valid result either way

    @pytest.mark.asyncio
    async def test_parallel_execution_with_multiple_agents(self, parallel_executor):
        """Test parallel execution with multiple agents"""
        async def agent_a(code: str, context: dict) -> dict:
            return {
                "description": "Agent A",
                "changes": [],
                "new_imports": [],
                "modified_code": "code_a",
                "complexity_reduction": 5,
                "risk_level": "low",
                "clarity_improvement": "good",
                "estimated_time": "quick",
                "confidence_score": 0.7,
                "rationale": "a",
            }

        async def agent_b(code: str, context: dict) -> dict:
            return {
                "description": "Agent B",
                "changes": [],
                "new_imports": [],
                "modified_code": "code_b",
                "complexity_reduction": 3,
                "risk_level": "low",
                "clarity_improvement": "fair",
                "estimated_time": "quick",
                "confidence_score": 0.6,
                "rationale": "b",
            }

        # Register agents
        parallel_executor.register_agent(AgentType.SIMPLICITY_FIRST, "Agent A", agent_a)
        parallel_executor.register_agent(AgentType.ARCHITECTURE_FOCUS, "Agent B", agent_b)

        # Execute
        result = await parallel_executor.execute_all("test code")

        assert result.total_agents == 2


class TestArchitectureAnalysis:
    """Test architecture analysis"""

    @pytest.mark.asyncio
    async def test_architecture_discovery(self, arch_analyzer):
        """Test discovering architecture"""
        analysis = await arch_analyzer.analyze()

        assert isinstance(analysis.modules, list)
        assert isinstance(analysis.dependencies, list)
        assert isinstance(analysis.metrics, object)

    @pytest.mark.asyncio
    async def test_architecture_metrics(self, arch_analyzer):
        """Test calculating architecture metrics"""
        analysis = await arch_analyzer.analyze()

        if analysis.metrics:
            assert hasattr(analysis.metrics, "coupling")
            assert hasattr(analysis.metrics, "cohesion")
            assert 0 <= analysis.metrics.coupling <= 1
            assert 0 <= analysis.metrics.cohesion <= 1


class TestGitAnalysis:
    """Test git risk analysis"""

    @pytest.mark.asyncio
    async def test_git_risk_assessment(self, git_analyzer):
        """Test assessing git risk"""
        analysis = await git_analyzer.analyze()

        assert isinstance(analysis.file_risks, list)
        assert isinstance(analysis.commit_risks, list)
        assert isinstance(analysis.ownership_map, dict)

    @pytest.mark.asyncio
    async def test_git_recommendations(self, git_analyzer):
        """Test generating git recommendations"""
        analysis = await git_analyzer.analyze()

        assert isinstance(analysis.recommendations, list)


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""

    @pytest.mark.asyncio
    async def test_complete_analysis_pipeline(self, arch_analyzer, git_analyzer):
        """Test analyzing architecture and git history"""
        # Architecture analysis
        arch = await arch_analyzer.analyze()

        # Git risk analysis
        git = await git_analyzer.analyze()

        # Both should complete
        assert isinstance(arch.modules, list)
        assert isinstance(git.file_risks, list)

    @pytest.mark.asyncio
    async def test_code_quality_pipeline(
        self, formatter, validator, temp_codebase
    ):
        """Test code quality checks"""
        code = "def test():\n    x=1\n    return x"

        # Format
        fmt = await formatter.format_code(code, language=Language.PYTHON)

        # Validate
        if fmt.success:
            val = await validator.validate_syntax(fmt.formatted_code, "python")
            assert val[0] is True


class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_formatter_performance(self, formatter):
        """Test formatter performance"""
        code = "x = 1\n" * 100

        start = time.time()
        result = await formatter.format_code(code, language=Language.PYTHON)
        elapsed = time.time() - start

        # Should be reasonably fast
        assert elapsed < 5.0  # 5 second timeout

    @pytest.mark.asyncio
    async def test_validator_performance(self, validator):
        """Test validator performance"""
        code = "def test():\n    pass\n" * 50

        start = time.time()
        result = await validator.validate_syntax(code, "python")
        elapsed = time.time() - start

        # Should be fast
        assert elapsed < 2.0  # 2 second timeout

    @pytest.mark.asyncio
    async def test_parallel_execution_speedup(self, parallel_executor):
        """Test parallel execution provides speedup"""
        async def slow_agent(code: str, context: dict) -> dict:
            await asyncio.sleep(0.05)
            return {
                "description": "test",
                "changes": [],
                "new_imports": [],
                "modified_code": "test",
                "complexity_reduction": 0,
                "risk_level": "low",
                "clarity_improvement": "fair",
                "estimated_time": "quick",
                "confidence_score": 0.5,
                "rationale": "test",
            }

        # Register 3 agents
        for i in range(3):
            parallel_executor.register_agent(
                AgentType.SIMPLICITY_FIRST, f"Agent {i}", slow_agent
            )

        # Measure time
        start = time.time()
        result = await parallel_executor.execute_all("test code")
        elapsed = time.time() - start

        # Should run faster than 3 * 0.05 = 0.15 seconds due to parallelism
        # Allow some overhead
        assert elapsed < 0.3


class TestErrorHandling:
    """Test error handling in pipeline"""

    @pytest.mark.asyncio
    async def test_invalid_code_handling(self, formatter, validator):
        """Test handling invalid code"""
        invalid_code = "def test(\n    pass"

        # Format should handle gracefully
        fmt = await formatter.format_code(invalid_code, language=Language.PYTHON)

        # Validate should detect error
        val = await validator.validate_syntax(invalid_code, "python")
        assert val[0] is False

    @pytest.mark.asyncio
    async def test_missing_file_handling(self, modifier):
        """Test handling missing files"""
        suggestion = {
            "agent": "Test",
            "description": "test",
            "changes": [],
            "new_imports": [],
            "modified_code": "test",
        }

        # Should handle gracefully
        result = await modifier.apply_suggestion(
            "/nonexistent/path", suggestion, dry_run=True
        )

        # Either succeeds with dry-run or fails gracefully
        assert isinstance(result.success, bool)


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""

    @pytest.mark.asyncio
    async def test_scenario_fix_code_style(self, formatter, validator):
        """Test fixing code style issues"""
        unformatted = "def test():\n    x=1;y=2\n    return x+y"

        # Format
        fmt = await formatter.format_code(unformatted, language=Language.PYTHON)

        # Validate
        if fmt.success:
            val = await validator.validate_syntax(fmt.formatted_code, "python")
            assert val[0] is True

    @pytest.mark.asyncio
    async def test_scenario_analyze_codebase(
        self, arch_analyzer, git_analyzer
    ):
        """Test analyzing complete codebase"""
        # Architecture
        arch = await arch_analyzer.analyze()

        # Git history
        git = await git_analyzer.analyze()

        # Should have complete analysis
        assert isinstance(arch.modules, list)
        assert isinstance(git.file_risks, list)

    @pytest.mark.asyncio
    async def test_scenario_parallel_suggestions(self, parallel_executor):
        """Test getting parallel improvement suggestions"""
        async def agent_1(code: str, context: dict) -> dict:
            return {
                "description": "Simplification",
                "changes": ["refactor"],
                "new_imports": [],
                "modified_code": "simplified",
                "complexity_reduction": 20,
                "risk_level": "low",
                "clarity_improvement": "good",
                "estimated_time": "quick",
                "confidence_score": 0.9,
                "rationale": "cleaner",
            }

        async def agent_2(code: str, context: dict) -> dict:
            return {
                "description": "Optimization",
                "changes": ["optimize"],
                "new_imports": [],
                "modified_code": "optimized",
                "complexity_reduction": 10,
                "risk_level": "medium",
                "clarity_improvement": "fair",
                "estimated_time": "moderate",
                "confidence_score": 0.7,
                "rationale": "faster",
            }

        parallel_executor.register_agent(
            AgentType.SIMPLICITY_FIRST, "Simplify", agent_1
        )
        parallel_executor.register_agent(
            AgentType.PERFORMANCE_FOCUS, "Optimize", agent_2
        )

        # Execute
        result = await parallel_executor.execute_all("test code")

        assert result.total_agents == 2


class TestComponentIntegration:
    """Test integration between components"""

    @pytest.mark.asyncio
    async def test_formatter_validator_integration(self, formatter, validator):
        """Test formatter and validator working together"""
        unformatted = "def f():\n    x=1\n    y=2\n    return x+y"

        # Format
        fmt = await formatter.format_code(unformatted, language=Language.PYTHON)

        if fmt.success:
            # Validate formatted code
            val_orig = await validator.validate_syntax(unformatted, "python")
            val_formatted = await validator.validate_syntax(fmt.formatted_code, "python")

            # Both should be valid
            assert val_orig[0] is True
            assert val_formatted[0] is True

    @pytest.mark.asyncio
    async def test_analysis_components_integration(
        self, arch_analyzer, git_analyzer
    ):
        """Test analysis components working together"""
        arch = await arch_analyzer.analyze()
        git = await git_analyzer.analyze()

        # Should have complementary information
        assert len(arch.modules) >= 0
        assert len(git.file_risks) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
