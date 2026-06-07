import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict


class ArchitectureAnalyzer:
    """Analyze code architecture, dependencies, and design patterns."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.modules: Dict[str, Set[str]] = defaultdict(set)
        self.files: List[str] = []

    def analyze(self) -> Dict[str, Any]:
        """Run full architecture analysis."""
        self._discover_files()
        self._build_dependency_graph()

        circular_deps = self._detect_circular_dependencies()
        coupling = self._analyze_coupling()
        god_objects = self._find_god_objects()

        return {
            "modules": len(self.files),
            "files": len(self.files),
            "circular_dependencies": len(circular_deps),
            "circular_deps_details": circular_deps,
            "tightly_coupled_modules": coupling,
            "god_objects": god_objects,
            "recommendations": self._generate_recommendations(circular_deps, coupling, god_objects),
        }

    def _discover_files(self):
        """Find all Python files in project."""
        for py_file in self.project_path.rglob("*.py"):
            if not self._is_ignored(py_file):
                self.files.append(str(py_file.relative_to(self.project_path)))

    def _is_ignored(self, path: Path) -> bool:
        """Check if file should be ignored."""
        ignore_patterns = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".pytest_cache"}
        for pattern in ignore_patterns:
            if pattern in path.parts:
                return True
        return False

    def _build_dependency_graph(self):
        """Build import dependency graph."""
        for filepath in self.files:
            full_path = self.project_path / filepath
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module = alias.name.split(".")[0]
                            self.modules[filepath].add(module)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module = node.module.split(".")[0]
                            self.modules[filepath].add(module)
            except Exception:
                pass

    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the import graph."""
        cycles = []

        def visit(node: str, path: List[str], visited: Set[str]) -> bool:
            if node in visited:
                return False
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return True

            visited.add(node)
            path.append(node)

            for neighbor in self.modules.get(node, []):
                if visit(neighbor, path.copy(), visited):
                    pass

            return False

        for module in self.modules:
            visit(module, [], set())

        return cycles

    def _analyze_coupling(self) -> List[str]:
        """Analyze module coupling (how much modules depend on each other)."""
        coupling_scores = defaultdict(int)

        for module, imports in self.modules.items():
            coupling_scores[module] = len(imports)

        tightly_coupled = sorted(
            coupling_scores.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return [module for module, score in tightly_coupled if score > 5]

    def _find_god_objects(self) -> List[str]:
        """Find classes with too many responsibilities (God Objects)."""
        god_objects = []

        for filepath in self.files:
            full_path = self.project_path / filepath
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                        attributes = [n for n in node.body if isinstance(n, ast.Assign)]

                        if len(methods) > 20 or len(attributes) > 15:
                            god_objects.append(f"{filepath}::{node.name}")
            except Exception:
                pass

        return god_objects

    def _generate_recommendations(
        self, circular_deps: List, coupling: List[str], god_objects: List[str]
    ) -> List[str]:
        """Generate architecture recommendations."""
        recommendations = []

        if circular_deps:
            recommendations.append(
                f"Fix {len(circular_deps)} circular dependencies: {circular_deps[0] if circular_deps else 'N/A'}"
            )

        if coupling:
            recommendations.append(f"Decouple tightly coupled modules: {', '.join(coupling[:3])}")

        if god_objects:
            recommendations.append(
                f"Refactor {len(god_objects)} God Objects into smaller classes: {god_objects[0]}"
            )

        if not recommendations:
            recommendations.append("Architecture looks good! No major issues detected.")

        return recommendations
