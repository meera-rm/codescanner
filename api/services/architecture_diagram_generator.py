"""
Architecture Diagram Generator - Phase 4.5
Generate visual architecture diagrams in multiple formats
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DiagramFormat:
    """Diagram format specification"""
    format_type: str  # "mermaid", "graphviz", "plantuml", "ascii"
    width: int = 1200
    height: int = 800


@dataclass
class DiagramResult:
    """Result of diagram generation"""
    success: bool
    diagram_content: Optional[str] = None
    diagram_format: Optional[str] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None


class ArchitectureDiagramGenerator:
    """Generate architecture diagrams"""

    def __init__(self):
        self.supported_formats = ["mermaid", "ascii", "graphviz", "plantuml"]

    def generate_module_diagram(
        self,
        modules: List[Any],
        dependencies: List[Any],
        format_type: str = "mermaid",
    ) -> DiagramResult:
        """
        Generate module dependency diagram.

        Args:
            modules: List of Module objects
            dependencies: List of Dependency objects
            format_type: Output format

        Returns:
            DiagramResult with diagram content
        """
        try:
            if format_type == "mermaid":
                return self._generate_mermaid_diagram(modules, dependencies)
            elif format_type == "ascii":
                return self._generate_ascii_diagram(modules, dependencies)
            elif format_type == "graphviz":
                return self._generate_graphviz_diagram(modules, dependencies)
            else:
                return DiagramResult(
                    success=False,
                    error_message=f"Unsupported format: {format_type}",
                )

        except Exception as e:
            logger.error(f"Error generating diagram: {e}")
            return DiagramResult(
                success=False,
                error_message=str(e),
            )

    def _generate_mermaid_diagram(
        self,
        modules: List[Any],
        dependencies: List[Any],
    ) -> DiagramResult:
        """Generate Mermaid diagram"""
        try:
            lines = ["graph TD"]

            # Add modules as nodes
            for module in modules:
                classes_str = ", ".join(module.classes[:3])
                if len(module.classes) > 3:
                    classes_str += f", +{len(module.classes)-3}"

                label = f"{module.name}<br/>{classes_str}"
                lines.append(f"    {module.name}[\"{label}\"]")

            # Add dependencies as edges
            for dep in dependencies:
                weight_label = f"({dep.weight})" if dep.weight > 1 else ""
                lines.append(
                    f"    {dep.source} -->|{weight_label}| {dep.target}"
                )

            diagram = "\n".join(lines)

            return DiagramResult(
                success=True,
                diagram_content=diagram,
                diagram_format="mermaid",
            )

        except Exception as e:
            logger.error(f"Error generating Mermaid diagram: {e}")
            return DiagramResult(
                success=False,
                error_message=str(e),
            )

    def _generate_ascii_diagram(
        self,
        modules: List[Any],
        dependencies: List[Any],
    ) -> DiagramResult:
        """Generate ASCII diagram"""
        try:
            lines = [
                "Architecture Diagram",
                "=" * 50,
                "",
            ]

            # List modules
            lines.append("Modules:")
            for i, module in enumerate(modules, 1):
                classes_str = f"({len(module.classes)} classes)"
                funcs_str = f"({len(module.functions)} functions)"
                lines.append(f"  {i}. {module.name} {classes_str} {funcs_str}")

            lines.append("")
            lines.append("Dependencies:")
            for dep in dependencies:
                lines.append(f"  {dep.source} ---> {dep.target} ({dep.weight})")

            diagram = "\n".join(lines)

            return DiagramResult(
                success=True,
                diagram_content=diagram,
                diagram_format="ascii",
            )

        except Exception as e:
            logger.error(f"Error generating ASCII diagram: {e}")
            return DiagramResult(
                success=False,
                error_message=str(e),
            )

    def _generate_graphviz_diagram(
        self,
        modules: List[Any],
        dependencies: List[Any],
    ) -> DiagramResult:
        """Generate Graphviz diagram"""
        try:
            lines = ["digraph Architecture {"]
            lines.append('    rankdir="LR";')
            lines.append('    node [shape=box, style=filled, fillcolor=lightblue];')

            # Add modules as nodes
            for module in modules:
                label = f"{module.name}\\n({len(module.classes)} classes)"
                lines.append(f'    "{module.name}" [label="{label}"];')

            lines.append("")

            # Add dependencies as edges
            for dep in dependencies:
                label = str(dep.weight) if dep.weight > 1 else ""
                lines.append(
                    f'    "{dep.source}" -> "{dep.target}" [label="{label}"];'
                )

            lines.append("}")

            diagram = "\n".join(lines)

            return DiagramResult(
                success=True,
                diagram_content=diagram,
                diagram_format="graphviz",
            )

        except Exception as e:
            logger.error(f"Error generating Graphviz diagram: {e}")
            return DiagramResult(
                success=False,
                error_message=str(e),
            )

    def generate_class_diagram(
        self,
        modules: List[Any],
        format_type: str = "mermaid",
    ) -> DiagramResult:
        """
        Generate class diagram.

        Args:
            modules: List of Module objects
            format_type: Output format

        Returns:
            DiagramResult with diagram content
        """
        try:
            if format_type == "mermaid":
                return self._generate_mermaid_class_diagram(modules)
            elif format_type == "ascii":
                return self._generate_ascii_class_diagram(modules)
            else:
                return DiagramResult(
                    success=False,
                    error_message=f"Unsupported format: {format_type}",
                )

        except Exception as e:
            logger.error(f"Error generating class diagram: {e}")
            return DiagramResult(
                success=False,
                error_message=str(e),
            )

    def _generate_mermaid_class_diagram(self, modules: List[Any]) -> DiagramResult:
        """Generate Mermaid class diagram"""
        try:
            lines = ["classDiagram"]

            for module in modules:
                for class_name in module.classes:
                    lines.append(f"    class {class_name}")

            diagram = "\n".join(lines)

            return DiagramResult(
                success=True,
                diagram_content=diagram,
                diagram_format="mermaid",
            )

        except Exception as e:
            logger.error(f"Error generating Mermaid class diagram: {e}")
            return DiagramResult(
                success=False,
                error_message=str(e),
            )

    def _generate_ascii_class_diagram(self, modules: List[Any]) -> DiagramResult:
        """Generate ASCII class diagram"""
        try:
            lines = [
                "Class Diagram",
                "=" * 50,
                "",
            ]

            for module in modules:
                lines.append(f"Module: {module.name}")
                for class_name in module.classes:
                    lines.append(f"  ├─ class {class_name}")
                lines.append("")

            diagram = "\n".join(lines)

            return DiagramResult(
                success=True,
                diagram_content=diagram,
                diagram_format="ascii",
            )

        except Exception as e:
            logger.error(f"Error generating ASCII class diagram: {e}")
            return DiagramResult(
                success=False,
                error_message=str(e),
            )

    def generate_metrics_diagram(
        self,
        metrics: Any,
        format_type: str = "ascii",
    ) -> DiagramResult:
        """
        Generate metrics visualization.

        Args:
            metrics: ArchitectureMetrics object
            format_type: Output format

        Returns:
            DiagramResult with diagram content
        """
        try:
            if format_type == "ascii":
                return self._generate_ascii_metrics(metrics)
            else:
                return DiagramResult(
                    success=False,
                    error_message=f"Unsupported format: {format_type}",
                )

        except Exception as e:
            logger.error(f"Error generating metrics diagram: {e}")
            return DiagramResult(
                success=False,
                error_message=str(e),
            )

    def _generate_ascii_metrics(self, metrics: Any) -> DiagramResult:
        """Generate ASCII metrics visualization"""
        try:
            lines = [
                "Architecture Metrics",
                "=" * 50,
                "",
                f"Modules:                  {metrics.total_modules}",
                f"Classes:                  {metrics.total_classes}",
                f"Functions:                {metrics.total_functions}",
                f"Lines of Code:            {metrics.total_lines_of_code}",
                f"Average Module Size:      {metrics.average_module_size:.1f} LOC",
                "",
                f"Coupling:                 {metrics.coupling:.2%} {'█' * int(metrics.coupling * 10)}",
                f"Cohesion:                 {metrics.cohesion:.2%} {'█' * int(metrics.cohesion * 10)}",
                f"Cyclomatic Complexity:    {metrics.cyclomatic_complexity:.1f}",
                f"Code Duplication:         {metrics.code_duplication_ratio:.2%}",
                "",
                "Legend:",
                "  ✓ Low coupling (<30%)    = Good modularity",
                "  ✓ High cohesion (>70%)   = Good organization",
                "  ✓ Low complexity (<5)    = Easier to maintain",
            ]

            diagram = "\n".join(lines)

            return DiagramResult(
                success=True,
                diagram_content=diagram,
                diagram_format="ascii",
            )

        except Exception as e:
            logger.error(f"Error generating metrics diagram: {e}")
            return DiagramResult(
                success=False,
                error_message=str(e),
            )

    def get_supported_formats(self) -> List[str]:
        """Get list of supported formats"""
        return self.supported_formats


# Factory function
def get_architecture_diagram_generator() -> ArchitectureDiagramGenerator:
    """Create ArchitectureDiagramGenerator instance"""
    return ArchitectureDiagramGenerator()
