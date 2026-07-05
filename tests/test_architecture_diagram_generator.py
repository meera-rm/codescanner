"""
Tests for Architecture Diagram Generator - Phase 4.5
Tests diagram generation in multiple formats
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.architecture_diagram_generator import (
    ArchitectureDiagramGenerator,
    DiagramFormat,
    DiagramResult,
    get_architecture_diagram_generator,
)
from api.services.architecture_analyzer import Module, Dependency, ArchitectureMetrics


@pytest.fixture
def generator():
    """Create ArchitectureDiagramGenerator instance"""
    return ArchitectureDiagramGenerator()


@pytest.fixture
def sample_modules():
    """Create sample modules for testing"""
    return [
        Module(
            name="model",
            path=Path("model.py"),
            imports=[],
            classes=["User", "Product"],
            functions=["create_user"],
            lines_of_code=100,
        ),
        Module(
            name="service",
            path=Path("service.py"),
            imports=["model"],
            classes=["UserService"],
            functions=["get_user", "save_user"],
            lines_of_code=150,
        ),
        Module(
            name="api",
            path=Path("api.py"),
            imports=["service"],
            classes=["UserAPI"],
            functions=["handle_request"],
            lines_of_code=200,
        ),
    ]


@pytest.fixture
def sample_dependencies():
    """Create sample dependencies"""
    return [
        Dependency(source="service", target="model", weight=2),
        Dependency(source="api", target="service", weight=1),
    ]


@pytest.fixture
def sample_metrics():
    """Create sample metrics"""
    return ArchitectureMetrics(
        total_modules=3,
        total_classes=4,
        total_functions=5,
        total_lines_of_code=450,
        average_module_size=150.0,
        coupling=0.33,
        cohesion=0.85,
        cyclomatic_complexity=2.5,
        code_duplication_ratio=0.02,
    )


class TestDiagramFormat:
    """Test DiagramFormat"""

    def test_diagram_format_creation(self):
        """Test creating diagram format"""
        fmt = DiagramFormat(format_type="mermaid", width=1200, height=800)

        assert fmt.format_type == "mermaid"
        assert fmt.width == 1200


class TestDiagramResult:
    """Test DiagramResult"""

    def test_result_success(self):
        """Test successful result"""
        result = DiagramResult(
            success=True,
            diagram_content="diagram content",
            diagram_format="mermaid",
        )

        assert result.success
        assert result.diagram_content is not None

    def test_result_failure(self):
        """Test failed result"""
        result = DiagramResult(
            success=False,
            error_message="Error message",
        )

        assert not result.success
        assert result.error_message is not None


class TestGeneratorInit:
    """Test generator initialization"""

    def test_init(self, generator):
        """Test initialization"""
        assert len(generator.supported_formats) > 0
        assert "mermaid" in generator.supported_formats

    def test_get_generator(self):
        """Test factory function"""
        gen = get_architecture_diagram_generator()

        assert isinstance(gen, ArchitectureDiagramGenerator)


class TestModuleDiagramGeneration:
    """Test module diagram generation"""

    def test_generate_mermaid_diagram(self, generator, sample_modules, sample_dependencies):
        """Test generating Mermaid diagram"""
        result = generator.generate_module_diagram(
            sample_modules,
            sample_dependencies,
            format_type="mermaid",
        )

        assert result.success
        assert result.diagram_content is not None
        assert "graph" in result.diagram_content.lower()

    def test_generate_ascii_diagram(self, generator, sample_modules, sample_dependencies):
        """Test generating ASCII diagram"""
        result = generator.generate_module_diagram(
            sample_modules,
            sample_dependencies,
            format_type="ascii",
        )

        assert result.success
        assert result.diagram_content is not None
        assert "Modules:" in result.diagram_content

    def test_generate_graphviz_diagram(self, generator, sample_modules, sample_dependencies):
        """Test generating Graphviz diagram"""
        result = generator.generate_module_diagram(
            sample_modules,
            sample_dependencies,
            format_type="graphviz",
        )

        assert result.success
        assert result.diagram_content is not None
        assert "digraph" in result.diagram_content.lower()

    def test_unsupported_format(self, generator, sample_modules, sample_dependencies):
        """Test unsupported format"""
        result = generator.generate_module_diagram(
            sample_modules,
            sample_dependencies,
            format_type="unsupported",
        )

        assert not result.success
        assert "unsupported" in result.error_message.lower()


class TestClassDiagramGeneration:
    """Test class diagram generation"""

    def test_generate_mermaid_class_diagram(self, generator, sample_modules):
        """Test generating Mermaid class diagram"""
        result = generator.generate_class_diagram(
            sample_modules,
            format_type="mermaid",
        )

        assert result.success
        assert result.diagram_content is not None
        assert "classDiagram" in result.diagram_content

    def test_generate_ascii_class_diagram(self, generator, sample_modules):
        """Test generating ASCII class diagram"""
        result = generator.generate_class_diagram(
            sample_modules,
            format_type="ascii",
        )

        assert result.success
        assert result.diagram_content is not None
        assert "Module:" in result.diagram_content


class TestMetricsDiagramGeneration:
    """Test metrics diagram generation"""

    def test_generate_metrics_diagram(self, generator, sample_metrics):
        """Test generating metrics diagram"""
        result = generator.generate_metrics_diagram(sample_metrics)

        assert result.success
        assert result.diagram_content is not None
        assert "Metrics" in result.diagram_content

    def test_metrics_includes_coupling(self, generator, sample_metrics):
        """Test that metrics diagram includes coupling"""
        result = generator.generate_metrics_diagram(sample_metrics)

        assert "Coupling:" in result.diagram_content

    def test_metrics_includes_cohesion(self, generator, sample_metrics):
        """Test that metrics diagram includes cohesion"""
        result = generator.generate_metrics_diagram(sample_metrics)

        assert "Cohesion:" in result.diagram_content


class TestDiagramContent:
    """Test diagram content quality"""

    def test_mermaid_has_module_nodes(self, generator, sample_modules, sample_dependencies):
        """Test that Mermaid diagram has module nodes"""
        result = generator.generate_module_diagram(
            sample_modules,
            sample_dependencies,
            format_type="mermaid",
        )

        content = result.diagram_content
        assert "model" in content.lower()
        assert "service" in content.lower()
        assert "api" in content.lower()

    def test_mermaid_has_dependencies(self, generator, sample_modules, sample_dependencies):
        """Test that Mermaid diagram has dependencies"""
        result = generator.generate_module_diagram(
            sample_modules,
            sample_dependencies,
            format_type="mermaid",
        )

        content = result.diagram_content
        # Should have arrows indicating dependencies
        assert "-->" in content

    def test_ascii_has_dependencies_listed(self, generator, sample_modules, sample_dependencies):
        """Test that ASCII diagram lists dependencies"""
        result = generator.generate_module_diagram(
            sample_modules,
            sample_dependencies,
            format_type="ascii",
        )

        content = result.diagram_content
        assert "Dependencies:" in content
        assert "--->" in content

    def test_graphviz_has_edges(self, generator, sample_modules, sample_dependencies):
        """Test that Graphviz diagram has edges"""
        result = generator.generate_module_diagram(
            sample_modules,
            sample_dependencies,
            format_type="graphviz",
        )

        content = result.diagram_content
        assert "->" in content


class TestEmptyInput:
    """Test with empty input"""

    def test_empty_modules(self, generator):
        """Test with no modules"""
        result = generator.generate_module_diagram([], [], format_type="mermaid")

        assert result.success
        assert result.diagram_content is not None

    def test_no_dependencies(self, generator, sample_modules):
        """Test with modules but no dependencies"""
        result = generator.generate_module_diagram(
            sample_modules,
            [],
            format_type="ascii",
        )

        assert result.success
        assert "Modules:" in result.diagram_content


class TestSupportedFormats:
    """Test supported formats"""

    def test_get_supported_formats(self, generator):
        """Test getting supported formats"""
        formats = generator.get_supported_formats()

        assert isinstance(formats, list)
        assert len(formats) > 0
        assert "mermaid" in formats
        assert "ascii" in formats


class TestDiagramVariations:
    """Test different diagram variations"""

    def test_single_module_diagram(self, generator):
        """Test diagram with single module"""
        modules = [
            Module(
                name="main",
                path=Path("main.py"),
                imports=[],
                classes=["Main"],
                functions=["run"],
                lines_of_code=50,
            )
        ]

        result = generator.generate_module_diagram(modules, [])

        assert result.success

    def test_complex_dependency_graph(self, generator):
        """Test diagram with complex dependencies"""
        modules = [
            Module(
                name=f"module{i}",
                path=Path(f"module{i}.py"),
                imports=[],
                classes=[f"Class{i}"],
                functions=[],
                lines_of_code=100,
            )
            for i in range(5)
        ]

        dependencies = [
            Dependency(source=f"module{i}", target=f"module{i+1}", weight=1)
            for i in range(4)
        ]

        result = generator.generate_module_diagram(modules, dependencies)

        assert result.success
        assert len(result.diagram_content) > 0


class TestErrorHandling:
    """Test error handling"""

    def test_invalid_format_module_diagram(self, generator, sample_modules):
        """Test invalid format in module diagram"""
        result = generator.generate_module_diagram(
            sample_modules,
            [],
            format_type="invalid_format",
        )

        assert not result.success
        assert result.error_message is not None

    def test_invalid_format_class_diagram(self, generator, sample_modules):
        """Test invalid format in class diagram"""
        result = generator.generate_class_diagram(
            sample_modules,
            format_type="invalid_format",
        )

        assert not result.success


class TestIntegration:
    """Test integration scenarios"""

    def test_all_formats_for_module_diagram(self, generator, sample_modules, sample_dependencies):
        """Test generating module diagrams in all supported formats"""
        for fmt in ["mermaid", "ascii", "graphviz"]:
            result = generator.generate_module_diagram(
                sample_modules,
                sample_dependencies,
                format_type=fmt,
            )

            assert result.success
            assert result.diagram_format == fmt

    def test_complete_diagram_suite(self, generator, sample_modules, sample_dependencies, sample_metrics):
        """Test generating complete diagram suite"""
        # Module diagram
        module_result = generator.generate_module_diagram(
            sample_modules,
            sample_dependencies,
            format_type="mermaid",
        )

        # Class diagram
        class_result = generator.generate_class_diagram(
            sample_modules,
            format_type="mermaid",
        )

        # Metrics diagram
        metrics_result = generator.generate_metrics_diagram(sample_metrics)

        assert module_result.success
        assert class_result.success
        assert metrics_result.success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
