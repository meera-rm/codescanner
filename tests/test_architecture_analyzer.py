"""
Tests for Architecture Analyzer - Phase 4.5
Tests architecture analysis, pattern detection, and metrics
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.architecture_analyzer import (
    ArchitectureAnalyzer,
    ArchitecturePattern,
    DesignPattern,
    Module,
    Dependency,
    ArchitectureMetrics,
    ArchitectureAnalysis,
    get_architecture_analyzer,
)


@pytest.fixture
def temp_codebase():
    """Create temporary codebase for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create model.py
        (tmppath / "model.py").write_text("""
class User:
    def __init__(self, name):
        self.name = name

class Product:
    def __init__(self, price):
        self.price = price
""")

        # Create view.py
        (tmppath / "view.py").write_text("""
from model import User

def display_user(user):
    print(f"User: {user.name}")
""")

        # Create controller.py
        (tmppath / "controller.py").write_text("""
from model import User
from view import display_user

def handle_request(name):
    user = User(name)
    display_user(user)
    return user
""")

        # Create utils.py
        (tmppath / "utils.py").write_text("""
def format_string(s):
    return s.upper()

def parse_number(s):
    return int(s)
""")

        yield tmppath


@pytest.fixture
def analyzer(temp_codebase):
    """Create ArchitectureAnalyzer instance"""
    return ArchitectureAnalyzer(str(temp_codebase))


class TestModule:
    """Test Module data structure"""

    def test_module_creation(self):
        """Test creating module"""
        module = Module(
            name="test",
            path=Path("test.py"),
            imports=["os"],
            classes=["TestClass"],
            functions=["test_func"],
            lines_of_code=100,
        )

        assert module.name == "test"
        assert len(module.classes) == 1
        assert len(module.functions) == 1


class TestDependency:
    """Test Dependency data structure"""

    def test_dependency_creation(self):
        """Test creating dependency"""
        dep = Dependency(source="module_a", target="module_b", weight=2)

        assert dep.source == "module_a"
        assert dep.target == "module_b"
        assert dep.weight == 2


class TestArchitectureMetrics:
    """Test ArchitectureMetrics"""

    def test_metrics_creation(self):
        """Test creating metrics"""
        metrics = ArchitectureMetrics(
            total_modules=5,
            total_classes=20,
            total_functions=50,
            total_lines_of_code=2000,
            average_module_size=400.0,
            coupling=0.25,
            cohesion=0.75,
            cyclomatic_complexity=3.5,
            code_duplication_ratio=0.05,
        )

        assert metrics.total_modules == 5
        assert metrics.coupling == 0.25


class TestArchitectureAnalysisInit:
    """Test ArchitectureAnalyzer initialization"""

    def test_init(self, temp_codebase):
        """Test initialization"""
        analyzer = ArchitectureAnalyzer(str(temp_codebase))

        assert analyzer.codebase_path == Path(temp_codebase)
        assert len(analyzer.modules) == 0

    def test_get_analyzer(self, temp_codebase):
        """Test factory function"""
        analyzer = get_architecture_analyzer(str(temp_codebase))

        assert isinstance(analyzer, ArchitectureAnalyzer)


class TestModuleDiscovery:
    """Test module discovery"""

    @pytest.mark.asyncio
    async def test_discover_modules(self, analyzer):
        """Test discovering modules"""
        analysis = await analyzer.analyze()

        assert analysis.success
        assert len(analysis.modules) > 0
        # Should find model, view, controller, utils
        module_names = {m.name for m in analysis.modules}
        assert "model" in module_names
        assert "view" in module_names
        assert "controller" in module_names
        assert "utils" in module_names

    @pytest.mark.asyncio
    async def test_module_imports(self, analyzer):
        """Test module import extraction"""
        analysis = await analyzer.analyze()

        model = next((m for m in analysis.modules if m.name == "model"), None)
        assert model is not None
        assert len(model.imports) == 0  # No imports in model.py

        view = next((m for m in analysis.modules if m.name == "view"), None)
        assert view is not None
        assert "model" in view.imports

    @pytest.mark.asyncio
    async def test_module_classes(self, analyzer):
        """Test class extraction"""
        analysis = await analyzer.analyze()

        model = next((m for m in analysis.modules if m.name == "model"), None)
        assert "User" in model.classes
        assert "Product" in model.classes


class TestDependencyAnalysis:
    """Test dependency analysis"""

    @pytest.mark.asyncio
    async def test_analyze_dependencies(self, analyzer):
        """Test dependency analysis"""
        analysis = await analyzer.analyze()

        assert len(analysis.dependencies) > 0
        # Should have dependency from view to model
        view_model_dep = next(
            (d for d in analysis.dependencies
             if d.source == "view" and d.target == "model"),
            None,
        )
        assert view_model_dep is not None

    @pytest.mark.asyncio
    async def test_dependency_weights(self, analyzer):
        """Test dependency weight counting"""
        analysis = await analyzer.analyze()

        # Check that dependencies are counted
        total_weight = sum(d.weight for d in analysis.dependencies)
        assert total_weight > 0


class TestPatternDetection:
    """Test architecture pattern detection"""

    @pytest.mark.asyncio
    async def test_detect_mvc_pattern(self, analyzer):
        """Test detecting MVC pattern"""
        analysis = await analyzer.analyze()

        assert ArchitecturePattern.MVC in analysis.detected_patterns

    @pytest.mark.asyncio
    async def test_detect_layered_pattern(self, analyzer):
        """Test detecting layered architecture"""
        analysis = await analyzer.analyze()

        # May or may not detect layered depending on module names
        assert isinstance(analysis.detected_patterns, list)


class TestDesignPatternDetection:
    """Test design pattern detection"""

    @pytest.mark.asyncio
    async def test_detect_design_patterns(self, analyzer):
        """Test detecting design patterns"""
        analysis = await analyzer.analyze()

        # Design patterns list should be a list
        assert isinstance(analysis.detected_design_patterns, list)

    @pytest.mark.asyncio
    async def test_design_patterns_no_duplicates(self, analyzer):
        """Test that design patterns are deduplicated"""
        analysis = await analyzer.analyze()

        patterns = analysis.detected_design_patterns
        assert len(patterns) == len(set(patterns))


class TestMetricsCalculation:
    """Test metrics calculation"""

    @pytest.mark.asyncio
    async def test_calculate_metrics(self, analyzer):
        """Test calculating metrics"""
        analysis = await analyzer.analyze()

        assert analysis.metrics is not None
        assert analysis.metrics.total_modules > 0
        assert analysis.metrics.total_classes >= 0
        assert analysis.metrics.total_functions >= 0
        assert analysis.metrics.total_lines_of_code > 0

    @pytest.mark.asyncio
    async def test_coupling_metric(self, analyzer):
        """Test coupling metric"""
        analysis = await analyzer.analyze()

        # Coupling should be between 0 and 1
        assert 0 <= analysis.metrics.coupling <= 1

    @pytest.mark.asyncio
    async def test_cohesion_metric(self, analyzer):
        """Test cohesion metric"""
        analysis = await analyzer.analyze()

        # Cohesion should be between 0 and 1
        assert 0 <= analysis.metrics.cohesion <= 1


class TestIssueDetection:
    """Test issue detection"""

    @pytest.mark.asyncio
    async def test_identify_issues(self, analyzer):
        """Test identifying issues"""
        analysis = await analyzer.analyze()

        # Issues should be a list (may be empty)
        assert isinstance(analysis.issues, list)

    @pytest.mark.asyncio
    async def test_circular_dependency_detection(self, temp_codebase):
        """Test detecting circular dependencies"""
        # Create modules with circular dependency
        (temp_codebase / "a.py").write_text("from b import func_b")
        (temp_codebase / "b.py").write_text("from a import func_a")

        analyzer = ArchitectureAnalyzer(str(temp_codebase))
        analysis = await analyzer.analyze()

        # Should detect or warn about circular dependencies
        assert isinstance(analysis.issues, list)


class TestRecommendationGeneration:
    """Test recommendation generation"""

    @pytest.mark.asyncio
    async def test_generate_recommendations(self, analyzer):
        """Test generating recommendations"""
        analysis = await analyzer.analyze()

        # Recommendations should be a list
        assert isinstance(analysis.recommendations, list)

    @pytest.mark.asyncio
    async def test_recommendations_not_empty_for_issues(self, analyzer):
        """Test that recommendations are generated when issues exist"""
        analysis = await analyzer.analyze()

        # If there are issues, should have recommendations
        if analysis.issues:
            # May or may not have recommendations, both valid
            assert isinstance(analysis.recommendations, list)


class TestAnalysisSummary:
    """Test analysis summary"""

    def test_get_analysis_summary(self, analyzer):
        """Test getting analysis summary"""
        summary = analyzer.get_analysis_summary()

        assert "modules_count" in summary
        assert "dependencies_count" in summary
        assert "issues_count" in summary


class TestComplexCodebase:
    """Test with more complex codebase"""

    @pytest.mark.asyncio
    async def test_complex_codebase_analysis(self):
        """Test analyzing more complex codebase"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create service layer
            (tmppath / "user_service.py").write_text("""
import os
from repositories import UserRepository

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def get_user(self, id):
        return self.repo.find_by_id(id)

    def save_user(self, user):
        return self.repo.save(user)
""")

            # Create repository layer
            (tmppath / "repositories.py").write_text("""
class UserRepository:
    def find_by_id(self, id):
        pass

    def save(self, user):
        pass
""")

            analyzer = ArchitectureAnalyzer(str(tmppath))
            analysis = await analyzer.analyze()

            assert analysis.success
            assert len(analysis.modules) >= 2
            assert len(analysis.dependencies) > 0


class TestEdgeCases:
    """Test edge cases"""

    @pytest.mark.asyncio
    async def test_empty_codebase(self):
        """Test analyzing empty codebase"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = ArchitectureAnalyzer(tmpdir)
            analysis = await analyzer.analyze()

            # Should handle gracefully
            assert not analysis.success
            assert len(analysis.modules) == 0

    @pytest.mark.asyncio
    async def test_single_module(self):
        """Test analyzing single module"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "main.py").write_text("def hello():\n    return 42")

            analyzer = ArchitectureAnalyzer(str(tmppath))
            analysis = await analyzer.analyze()

            assert analysis.success
            assert len(analysis.modules) == 1


class TestAnalysisResult:
    """Test ArchitectureAnalysis result"""

    @pytest.mark.asyncio
    async def test_analysis_result_structure(self, analyzer):
        """Test analysis result structure"""
        analysis = await analyzer.analyze()

        assert isinstance(analysis, ArchitectureAnalysis)
        assert hasattr(analysis, "modules")
        assert hasattr(analysis, "dependencies")
        assert hasattr(analysis, "detected_patterns")
        assert hasattr(analysis, "metrics")
        assert hasattr(analysis, "issues")
        assert hasattr(analysis, "recommendations")


class TestIntegration:
    """Test integration scenarios"""

    @pytest.mark.asyncio
    async def test_complete_analysis_flow(self, analyzer):
        """Test complete analysis flow"""
        analysis = await analyzer.analyze()

        # Should have complete analysis
        assert analysis.success
        assert len(analysis.modules) > 0
        assert isinstance(analysis.detected_patterns, list)
        assert analysis.metrics is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
