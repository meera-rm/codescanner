import ast
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Finding:
    file: str
    line: int
    column: int
    rule: str
    message: str
    severity: str  # INFO, WARNING, ERROR, CRITICAL


class PythonRules:
    """Detectable patterns in Python AST."""

    @staticmethod
    def check_hardcoded_secrets(code: str, filepath: str) -> List[Finding]:
        """Detect common secret patterns."""
        findings = []
        patterns = [
            (r"api[_-]?key\s*=\s*['\"]([a-zA-Z0-9]+)['\"]", "Hardcoded API key"),
            (r"password\s*=\s*['\"]([^\s'\"]+)['\"]", "Hardcoded password"),
            (r"token\s*=\s*['\"]([a-zA-Z0-9\-_]+)['\"]", "Hardcoded token"),
            (r"aws_secret\s*=\s*['\"]([^\s'\"]+)['\"]", "Hardcoded AWS secret"),
        ]

        for line_num, line in enumerate(code.split("\n"), 1):
            for pattern, msg in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        Finding(
                            file=filepath,
                            line=line_num,
                            column=0,
                            rule="hardcoded_secret",
                            message=msg,
                            severity="CRITICAL",
                        )
                    )
        return findings

    @staticmethod
    def check_unused_imports(tree: ast.AST, code: str, filepath: str) -> List[Finding]:
        """Find unused imports."""
        findings = []
        imports = {}

        # Collect imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports[name] = node.lineno

        # Check usage (simple: just look for name in code)
        lines = code.split("\n")
        for name, lineno in imports.items():
            if name == "*":
                continue

            # Skip if used elsewhere
            usage_count = 0
            for i, line in enumerate(lines, 1):
                if i != lineno and re.search(rf"\b{re.escape(name)}\b", line):
                    usage_count += 1

            if usage_count == 0:
                findings.append(
                    Finding(
                        file=filepath,
                        line=lineno,
                        column=0,
                        rule="unused_import",
                        message=f"Import '{name}' is unused",
                        severity="WARNING",
                    )
                )

        return findings

    @staticmethod
    def check_complexity(tree: ast.AST, filepath: str) -> List[Finding]:
        """Detect high cyclomatic complexity in functions (excluding nested functions)."""
        findings = []

        def count_complexity(func_node):
            complexity = 1

            class ScopeWalker(ast.NodeVisitor):
                def __init__(self):
                    self.complexity = 0

                def visit_FunctionDef(self, node):
                    pass

                def visit_AsyncFunctionDef(self, node):
                    pass

                def visit_If(self, node):
                    self.complexity += 1
                    self.generic_visit(node)

                def visit_For(self, node):
                    self.complexity += 1
                    self.generic_visit(node)

                def visit_While(self, node):
                    self.complexity += 1
                    self.generic_visit(node)

                def visit_ExceptHandler(self, node):
                    self.complexity += 1
                    self.generic_visit(node)

                def visit_BoolOp(self, node):
                    self.complexity += len(node.values) - 1
                    self.generic_visit(node)

            walker = ScopeWalker()
            for child in func_node.body:
                walker.visit(child)
            return complexity + walker.complexity

        class ComplexityVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                complexity = count_complexity(node)
                if complexity > 10:
                    findings.append(
                        Finding(
                            file=filepath,
                            line=node.lineno,
                            column=0,
                            rule="high_complexity",
                            message=f"Function '{node.name}' has complexity {complexity} (threshold: 10)",
                            severity="WARNING",
                        )
                    )
                self.generic_visit(node)

            visit_AsyncFunctionDef = visit_FunctionDef

        ComplexityVisitor().visit(tree)
        return findings
