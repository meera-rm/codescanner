import ast
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class SmellFinding:
    file: str
    line: int
    smell_type: str  # "long_function", "deep_nesting", "long_params", "large_class"
    severity: str  # "warning" or "error"
    description: str
    code_lines: int  # Function/class size in lines


class SmellDetector:
    """Detects code smells: long functions, deep nesting, large parameters, large classes."""

    def __init__(self):
        self.findings: List[SmellFinding] = []

    def detect(self, filepath: str) -> List[SmellFinding]:
        """Scan a single Python file for code smells."""
        self.findings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except (UnicodeDecodeError, IOError):
            return self.findings

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return self.findings

        # Run all detectors
        self._detect_long_functions(tree, filepath)
        self._detect_large_classes(tree, filepath)
        self._detect_long_parameter_lists(tree, filepath)
        self._detect_deep_nesting(tree, filepath, code)

        return self.findings

    def _detect_long_functions(
        self, tree: ast.AST, filepath: str, threshold: int = 50
    ) -> None:
        """Detect functions longer than threshold lines."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Only check top-level functions and methods, not nested
                func_length = node.end_lineno - node.lineno + 1
                if func_length > threshold:
                    self.findings.append(
                        SmellFinding(
                            file=filepath,
                            line=node.lineno,
                            smell_type="long_function",
                            severity="warning",
                            description=f"Function '{node.name}' is {func_length} lines (threshold: {threshold})",
                            code_lines=func_length,
                        )
                    )

    def _detect_large_classes(
        self, tree: ast.AST, filepath: str, threshold: int = 300
    ) -> None:
        """Detect classes longer than threshold lines."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_length = node.end_lineno - node.lineno + 1
                if class_length > threshold:
                    self.findings.append(
                        SmellFinding(
                            file=filepath,
                            line=node.lineno,
                            smell_type="large_class",
                            severity="warning",
                            description=f"Class '{node.name}' is {class_length} lines (threshold: {threshold})",
                            code_lines=class_length,
                        )
                    )

    def _detect_long_parameter_lists(
        self, tree: ast.AST, filepath: str, threshold: int = 5
    ) -> None:
        """Detect functions with too many parameters."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count regular args (exclude self/cls)
                args = node.args
                param_count = len(args.args)

                # For methods, don't count 'self' or 'cls'
                if param_count > 0:
                    first_arg = args.args[0].arg
                    if first_arg in ("self", "cls"):
                        param_count -= 1

                if param_count > threshold:
                    self.findings.append(
                        SmellFinding(
                            file=filepath,
                            line=node.lineno,
                            smell_type="long_params",
                            severity="warning",
                            description=f"Function '{node.name}' has {param_count} parameters (threshold: {threshold})",
                            code_lines=param_count,
                        )
                    )

    def _detect_deep_nesting(
        self, tree: ast.AST, filepath: str, code: str, threshold: int = 4
    ) -> None:
        """Detect deeply nested code blocks."""
        lines = code.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                max_depth = self._calculate_max_nesting_depth(node)
                if max_depth > threshold:
                    self.findings.append(
                        SmellFinding(
                            file=filepath,
                            line=node.lineno,
                            smell_type="deep_nesting",
                            severity="warning",
                            description=f"Function '{node.name}' has nesting depth {max_depth} (threshold: {threshold})",
                            code_lines=max_depth,
                        )
                    )

    def _calculate_max_nesting_depth(self, node: ast.AST) -> int:
        """Calculate maximum nesting depth in a function."""
        max_depth = [0]

        def visit_with_depth(n: ast.AST, depth: int) -> None:
            # Count structural nesting (if, for, while, with, try)
            if isinstance(n, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                max_depth[0] = max(max_depth[0], depth)

            # Don't descend into nested functions/classes
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if n is not node:  # Skip if it's the root node
                    return

            for child in ast.iter_child_nodes(n):
                visit_with_depth(child, depth + 1)

        visit_with_depth(node, 0)
        return max_depth[0]

    def report(self, findings: List[SmellFinding]) -> dict:
        """Generate a report of findings."""
        by_type = {}
        for f in findings:
            if f.smell_type not in by_type:
                by_type[f.smell_type] = []
            by_type[f.smell_type].append(f)

        return {
            "total_smells": len(findings),
            "by_type": {
                smell_type: [
                    {
                        "file": f.file,
                        "line": f.line,
                        "description": f.description,
                        "severity": f.severity,
                    }
                    for f in findings
                ]
                for smell_type, findings in by_type.items()
            },
        }
