"""
Architecture Analyzer - Phase 4.5
Analyze codebase architecture and identify patterns
"""

import logging
import ast
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ArchitecturePattern(Enum):
    """Detected architecture patterns"""
    MVC = "mvc"  # Model-View-Controller
    MVVM = "mvvm"  # Model-View-ViewModel
    LAYERED = "layered"  # Layered architecture
    MICROSERVICES = "microservices"  # Microservices
    MONOLITH = "monolith"  # Monolithic
    PLUGIN = "plugin"  # Plugin-based
    EVENT_DRIVEN = "event_driven"  # Event-driven
    UNKNOWN = "unknown"


class DesignPattern(Enum):
    """Detected design patterns"""
    SINGLETON = "singleton"
    FACTORY = "factory"
    OBSERVER = "observer"
    DECORATOR = "decorator"
    STRATEGY = "strategy"
    ADAPTER = "adapter"
    BUILDER = "builder"
    PROXY = "proxy"
    CHAIN_OF_RESPONSIBILITY = "chain_of_responsibility"
    COMMAND = "command"
    STATE = "state"
    TEMPLATE_METHOD = "template_method"
    UNKNOWN = "unknown"


@dataclass
class Module:
    """Code module"""
    name: str
    path: Path
    imports: List[str]
    classes: List[str]
    functions: List[str]
    lines_of_code: int
    complexity: float = 0.0


@dataclass
class Dependency:
    """Dependency between modules"""
    source: str
    target: str
    weight: int = 1  # Number of imports


@dataclass
class ArchitectureMetrics:
    """Architecture metrics"""
    total_modules: int
    total_classes: int
    total_functions: int
    total_lines_of_code: int
    average_module_size: float
    coupling: float  # 0-1, lower is better
    cohesion: float  # 0-1, higher is better
    cyclomatic_complexity: float
    code_duplication_ratio: float


@dataclass
class ArchitectureAnalysis:
    """Result of architecture analysis"""
    success: bool
    codebase_path: str
    modules: List[Module]
    dependencies: List[Dependency]
    detected_patterns: List[ArchitecturePattern]
    detected_design_patterns: List[DesignPattern]
    metrics: Optional[ArchitectureMetrics] = None
    issues: List[str] = None
    recommendations: List[str] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.recommendations is None:
            self.recommendations = []


class ArchitectureAnalyzer:
    """Analyze codebase architecture"""

    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        self.modules: Dict[str, Module] = {}
        self.dependencies: List[Dependency] = []

    async def analyze(self) -> ArchitectureAnalysis:
        """
        Analyze codebase architecture.

        Returns:
            ArchitectureAnalysis with modules, patterns, metrics
        """
        try:
            logger.info(f"Analyzing architecture of {self.codebase_path}")

            # Step 1: Discover modules
            modules = self._discover_modules()
            self.modules = {m.name: m for m in modules}

            if not modules:
                logger.warning("No Python modules found")
                return ArchitectureAnalysis(
                    success=False,
                    codebase_path=str(self.codebase_path),
                    modules=[],
                    dependencies=[],
                    detected_patterns=[],
                    detected_design_patterns=[],
                    issues=["No Python modules found"],
                )

            # Step 2: Analyze dependencies
            self._analyze_dependencies(modules)

            # Step 3: Detect patterns
            patterns = self._detect_patterns()
            design_patterns = self._detect_design_patterns()

            # Step 4: Calculate metrics
            metrics = self._calculate_metrics(modules)

            # Step 5: Identify issues
            issues = self._identify_issues(modules)

            # Step 6: Generate recommendations
            recommendations = self._generate_recommendations(
                modules, patterns, issues
            )

            logger.info(f"Architecture analysis complete: {len(modules)} modules")

            return ArchitectureAnalysis(
                success=True,
                codebase_path=str(self.codebase_path),
                modules=modules,
                dependencies=self.dependencies,
                detected_patterns=patterns,
                detected_design_patterns=design_patterns,
                metrics=metrics,
                issues=issues,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Error analyzing architecture: {e}")
            return ArchitectureAnalysis(
                success=False,
                codebase_path=str(self.codebase_path),
                modules=[],
                dependencies=[],
                detected_patterns=[],
                detected_design_patterns=[],
                issues=[str(e)],
            )

    def _discover_modules(self) -> List[Module]:
        """Discover Python modules in codebase"""
        modules = []

        for py_file in self.codebase_path.rglob("*.py"):
            # Skip __pycache__ and venv
            if "__pycache__" in py_file.parts or "venv" in py_file.parts:
                continue

            try:
                module = self._analyze_module(py_file)
                if module:
                    modules.append(module)
            except Exception as e:
                logger.warning(f"Error analyzing {py_file}: {e}")

        return modules

    def _analyze_module(self, py_file: Path) -> Optional[Module]:
        """Analyze a single Python module"""
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            lines = len(content.split("\n"))

            # Extract imports
            imports = self._extract_imports(tree)

            # Extract classes and functions
            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef) and not any(
                    isinstance(parent, ast.ClassDef)
                    for parent in ast.walk(tree)
                    if hasattr(parent, "body") and node in parent.body
                ):
                    functions.append(node.name)

            module_name = py_file.stem
            return Module(
                name=module_name,
                path=py_file,
                imports=imports,
                classes=classes,
                functions=functions,
                lines_of_code=lines,
                complexity=self._calculate_complexity(tree),
            )

        except Exception as e:
            logger.warning(f"Error analyzing module {py_file}: {e}")
            return None

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract imports from AST"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return list(set(imports))  # Deduplicate

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity"""
        complexity = 1

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += 1

        return complexity

    def _analyze_dependencies(self, modules: List[Module]) -> None:
        """Analyze module dependencies"""
        module_names = {m.name for m in modules}

        for module in modules:
            for imp in module.imports:
                # Check if import is from another local module
                imp_name = imp.split(".")[0]
                if imp_name in module_names and imp_name != module.name:
                    # Check if dependency already exists
                    existing = next(
                        (d for d in self.dependencies
                         if d.source == module.name and d.target == imp_name),
                        None,
                    )
                    if existing:
                        existing.weight += 1
                    else:
                        self.dependencies.append(
                            Dependency(source=module.name, target=imp_name, weight=1)
                        )

    def _detect_patterns(self) -> List[ArchitecturePattern]:
        """Detect architecture patterns"""
        patterns = []

        # Check for MVC pattern
        if self._has_mvc_structure():
            patterns.append(ArchitecturePattern.MVC)

        # Check for layered architecture
        if self._has_layered_structure():
            patterns.append(ArchitecturePattern.LAYERED)

        # Check for microservices
        if self._has_microservices_structure():
            patterns.append(ArchitecturePattern.MICROSERVICES)

        # Default to monolith if no patterns detected
        if not patterns:
            patterns.append(ArchitecturePattern.MONOLITH)

        return patterns

    def _has_mvc_structure(self) -> bool:
        """Check if codebase has MVC structure"""
        module_names = set(self.modules.keys())
        mvc_indicators = {"model", "view", "controller"}
        return len(mvc_indicators & module_names) >= 2

    def _has_layered_structure(self) -> bool:
        """Check if codebase has layered architecture"""
        module_names = set(self.modules.keys())
        layer_indicators = {"api", "service", "repository", "model", "utils"}
        return len(layer_indicators & module_names) >= 3

    def _has_microservices_structure(self) -> bool:
        """Check if codebase has microservices structure"""
        # Check for multiple independent service modules
        module_names = set(self.modules.keys())
        service_modules = {m for m in module_names if "service" in m}
        return len(service_modules) >= 3 and self._low_coupling()

    def _low_coupling(self) -> bool:
        """Check if modules have low coupling"""
        if not self.modules:
            return False

        total_deps = len(self.dependencies)
        max_possible_deps = len(self.modules) * (len(self.modules) - 1)

        coupling = total_deps / max_possible_deps if max_possible_deps > 0 else 0
        return coupling < 0.3

    def _detect_design_patterns(self) -> List[DesignPattern]:
        """Detect design patterns in code"""
        patterns = []

        for module in self.modules.values():
            # Look for singleton pattern
            if any("singleton" in c.lower() for c in module.classes):
                patterns.append(DesignPattern.SINGLETON)

            # Look for factory pattern
            if any("factory" in c.lower() or "factory" in f.lower()
                   for c in module.classes for f in module.functions):
                patterns.append(DesignPattern.FACTORY)

            # Look for observer pattern
            if any("observer" in c.lower() or "listener" in c.lower()
                   for c in module.classes):
                patterns.append(DesignPattern.OBSERVER)

            # Look for decorator pattern
            if any("decorator" in c.lower() for c in module.classes):
                patterns.append(DesignPattern.DECORATOR)

            # Look for strategy pattern
            if any("strategy" in c.lower() for c in module.classes):
                patterns.append(DesignPattern.STRATEGY)

        return list(set(patterns))  # Deduplicate

    def _calculate_metrics(self, modules: List[Module]) -> ArchitectureMetrics:
        """Calculate architecture metrics"""
        total_classes = sum(len(m.classes) for m in modules)
        total_functions = sum(len(m.functions) for m in modules)
        total_loc = sum(m.lines_of_code for m in modules)
        avg_module_size = total_loc / len(modules) if modules else 0

        # Calculate coupling
        max_deps = len(modules) * (len(modules) - 1)
        coupling = len(self.dependencies) / max_deps if max_deps > 0 else 0

        # Calculate cohesion (intra-module functions per class)
        cohesion = sum(len(m.functions) / max(len(m.classes), 1)
                      for m in modules) / len(modules) if modules else 0
        cohesion = min(cohesion / 10, 1.0)  # Normalize to 0-1

        # Average cyclomatic complexity
        avg_complexity = sum(m.complexity for m in modules) / len(modules) if modules else 0

        return ArchitectureMetrics(
            total_modules=len(modules),
            total_classes=total_classes,
            total_functions=total_functions,
            total_lines_of_code=total_loc,
            average_module_size=avg_module_size,
            coupling=coupling,
            cohesion=cohesion,
            cyclomatic_complexity=avg_complexity,
            code_duplication_ratio=0.0,  # Placeholder
        )

    def _identify_issues(self, modules: List[Module]) -> List[str]:
        """Identify architectural issues"""
        issues = []

        # Check for high coupling
        if len(self.dependencies) > len(modules) * 2:
            issues.append(
                f"High coupling detected: {len(self.dependencies)} dependencies "
                f"for {len(modules)} modules"
            )

        # Check for circular dependencies
        circular_deps = self._find_circular_dependencies()
        if circular_deps:
            issues.append(f"Circular dependencies detected: {circular_deps}")

        # Check for large modules
        large_modules = [m for m in modules if m.lines_of_code > 500]
        if large_modules:
            issues.append(
                f"Large modules detected ({len(large_modules)}): "
                f"{', '.join(m.name for m in large_modules)}"
            )

        # Check for modules with many classes
        heavy_modules = [m for m in modules if len(m.classes) > 10]
        if heavy_modules:
            issues.append(
                f"Modules with many classes ({len(heavy_modules)}): "
                f"{', '.join(m.name for m in heavy_modules)}"
            )

        return issues

    def _find_circular_dependencies(self) -> List[Tuple[str, str]]:
        """Find circular dependencies"""
        circular = []

        for dep in self.dependencies:
            reverse = next(
                (d for d in self.dependencies
                 if d.source == dep.target and d.target == dep.source),
                None,
            )
            if reverse and dep.source < dep.target:  # Avoid duplicates
                circular.append((dep.source, dep.target))

        return circular

    def _generate_recommendations(
        self,
        modules: List[Module],
        patterns: List[ArchitecturePattern],
        issues: List[str],
    ) -> List[str]:
        """Generate architectural recommendations"""
        recommendations = []

        # Recommend layered architecture if monolith with high coupling
        if (ArchitecturePattern.MONOLITH in patterns and
                len(self.dependencies) > len(modules) * 2):
            recommendations.append(
                "Consider adopting a layered architecture to reduce coupling"
            )

        # Recommend breaking up large modules
        large_modules = [m for m in modules if m.lines_of_code > 500]
        if large_modules:
            recommendations.append(
                f"Consider breaking up large modules: {', '.join(m.name for m in large_modules)}"
            )

        # Recommend removing circular dependencies
        if any("Circular" in issue for issue in issues):
            recommendations.append("Refactor code to eliminate circular dependencies")

        # Recommend design patterns
        if len([m for m in modules if m.classes]) > 5:
            recommendations.append("Consider applying design patterns to improve code organization")

        return recommendations

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of analysis"""
        return {
            "modules_count": len(self.modules),
            "dependencies_count": len(self.dependencies),
            "issues_count": len(self._identify_issues(list(self.modules.values()))),
            "last_analyzed": "now",
        }


# Factory function
def get_architecture_analyzer(codebase_path: str) -> ArchitectureAnalyzer:
    """Create ArchitectureAnalyzer instance"""
    return ArchitectureAnalyzer(codebase_path)
