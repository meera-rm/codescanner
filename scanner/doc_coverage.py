import ast
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DocMetrics:
    file: str
    total_functions: int
    documented_functions: int
    total_classes: int
    documented_classes: int
    coverage_ratio: float  # 0.0 to 1.0
    has_module_docstring: bool
    details: dict  # Per-function/class breakdown


class DocCoverageDetector:
    """Analyzes docstring coverage in Python files."""

    def __init__(self):
        self.findings: List[dict] = []

    def analyze(self, filepath: str) -> Optional[DocMetrics]:
        """Analyze docstring coverage in a file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except (UnicodeDecodeError, IOError):
            return None

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return None

        return self._calculate_metrics(tree, filepath, code)

    def _calculate_metrics(
        self, tree: ast.AST, filepath: str, code: str
    ) -> DocMetrics:
        """Calculate documentation metrics from AST."""
        module_docstring = ast.get_docstring(tree)

        functions = []
        classes = []

        # Walk the tree (top-level only, not nested)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(node)
            elif isinstance(node, ast.ClassDef):
                classes.append(node)

        # Count documented functions/classes
        documented_functions = sum(
            1 for f in functions if ast.get_docstring(f) is not None
        )
        documented_classes = sum(
            1 for c in classes if ast.get_docstring(c) is not None
        )

        # Count methods inside classes (not top-level)
        class_methods = []
        documented_class_methods = 0
        for cls in classes:
            for node in cls.body:
                if isinstance(node, ast.FunctionDef):
                    class_methods.append(node)
                    if ast.get_docstring(node) is not None:
                        documented_class_methods += 1

        # Total counts: functions + class methods
        total_functions = len(functions) + len(class_methods)
        total_documented = documented_functions + documented_class_methods

        # Calculate coverage
        coverage_ratio = (
            total_documented / total_functions if total_functions > 0 else 0.0
        )

        # Build details dictionary
        details = {
            "functions": {
                "total": len(functions),
                "documented": documented_functions,
                "undocumented": [
                    {"name": f.name, "line": f.lineno}
                    for f in functions
                    if ast.get_docstring(f) is None
                ],
            },
            "classes": {
                "total": len(classes),
                "documented": documented_classes,
                "undocumented": [
                    {"name": c.name, "line": c.lineno}
                    for c in classes
                    if ast.get_docstring(c) is None
                ],
            },
            "class_methods": {
                "total": len(class_methods),
                "documented": documented_class_methods,
                "undocumented": [
                    {"name": m.name, "line": m.lineno, "parent_class": self._find_parent_class(tree, m.lineno)}
                    for m in class_methods
                    if ast.get_docstring(m) is None
                ],
            },
        }

        return DocMetrics(
            file=filepath,
            total_functions=total_functions,
            documented_functions=total_documented,
            total_classes=len(classes),
            documented_classes=documented_classes,
            coverage_ratio=coverage_ratio,
            has_module_docstring=module_docstring is not None,
            details=details,
        )

    def _find_parent_class(self, tree: ast.AST, line_num: int) -> str:
        """Find the parent class for a method at a given line."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.lineno == line_num:
                        return node.name
        return "unknown"

    def report(self, metrics: DocMetrics) -> dict:
        """Generate a human-readable report."""
        coverage_percentage = metrics.coverage_ratio * 100

        return {
            "file": metrics.file,
            "coverage_ratio": metrics.coverage_ratio,
            "coverage_percentage": coverage_percentage,
            "total_functions": metrics.total_functions,
            "documented_functions": metrics.documented_functions,
            "undocumented_functions": metrics.total_functions - metrics.documented_functions,
            "total_classes": metrics.total_classes,
            "documented_classes": metrics.documented_classes,
            "has_module_docstring": metrics.has_module_docstring,
            "details": metrics.details,
            "summary": f"{coverage_percentage:.1f}% coverage ({metrics.documented_functions}/{metrics.total_functions})",
        }
