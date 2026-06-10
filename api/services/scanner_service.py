import sys
import os
import uuid
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scanner"))

from scanner import PythonScanner, JavaScriptScanner, SQLScanner


class ScannerService:
    def __init__(self):
        self.python_scanner = PythonScanner()
        self.js_scanner = JavaScriptScanner()
        self.sql_scanner = SQLScanner()
        self.scan_jobs: Dict[str, Dict[str, Any]] = {}

    def _convert_findings(self, findings: list, language: str) -> list:
        """Convert Finding objects to dictionaries."""
        converted = []
        for finding in findings:
            # Check if it's a Finding object or dictionary
            if hasattr(finding, '__dict__'):
                # It's a Finding object
                finding_dict = {
                    "file": getattr(finding, 'file', ''),
                    "line": getattr(finding, 'line', 0),
                    "column": getattr(finding, 'column', 0),
                    "type": getattr(finding, 'rule', ''),
                    "message": getattr(finding, 'message', ''),
                    "severity": getattr(finding, 'severity', 'INFO'),
                    "language": language
                }
            else:
                # It's already a dictionary
                finding_dict = finding
            converted.append(finding_dict)
        return converted

    def _resolve_path(self, path_input: str) -> str:
        """Resolve path: try exact path first, then search common locations."""
        path = Path(path_input)

        # Try exact path first
        if path.exists():
            return str(path.resolve())

        # If it's just a directory name, search common locations
        if '/' not in path_input and '\\' not in path_input:
            common_locations = [
                Path.home() / 'Documents' / path_input,
                Path.home() / 'Documents' / 'assignments' / 'pursuit' / path_input,
                Path.home() / 'Documents' / 'codescanner' / path_input,
                Path.home() / 'Documents' / 'claudeassisted' / path_input,
                Path.home() / 'Documents' / 'Bronze_to_silver' / path_input,
                Path.cwd() / path_input,
            ]
            for candidate in common_locations:
                if candidate.exists():
                    return str(candidate.resolve())

        # Not found
        return str(path.resolve())  # Return as-is, let scanners handle the error

    def scan(
        self,
        code: Optional[str] = None,
        directory_path: Optional[str] = None,
        language: str = "python",
        options: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        if options is None:
            options = {
                "security": True,
                "quality_score": True,
                "code_smells": True,
                "doc_coverage": True,
                "complexity": True,
            }

        job_id = f"scan_{uuid.uuid4().hex[:12]}"
        start_time = datetime.utcnow()

        findings = []
        metrics = {}

        try:
            # Resolve directory path if provided
            if directory_path:
                directory_path = self._resolve_path(directory_path)

            if language == "python" or language == "all":
                if code:
                    python_findings = self.python_scanner.scan_code(code)
                    findings.extend(self._convert_findings(python_findings, "python"))
                elif directory_path:
                    python_findings = self.python_scanner.scan_directory(directory_path)
                    findings.extend(self._convert_findings(python_findings, "python"))

            if language == "javascript" or language == "all":
                if code:
                    js_findings = self.js_scanner.scan_code(code)
                    findings.extend(self._convert_findings(js_findings, "javascript"))
                elif directory_path:
                    js_findings = self.js_scanner.scan_directory(directory_path)
                    findings.extend(self._convert_findings(js_findings, "javascript"))

            if language == "sql" or language == "all":
                if code:
                    sql_findings = self.sql_scanner.scan_code(code)
                    findings.extend(self._convert_findings(sql_findings, "sql"))
                elif directory_path:
                    sql_findings = self.sql_scanner.scan_directory(directory_path)
                    findings.extend(self._convert_findings(sql_findings, "sql"))

            if options.get("quality_score"):
                metrics["quality_score"] = self._calculate_quality_score(findings)

            if options.get("complexity"):
                metrics["complexity"] = self._calculate_complexity(findings)

            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            # Get list of scanned files
            scanned_files = self._get_scanned_files(directory_path, language)

            # Extract function-level metrics
            function_metrics = self._extract_function_metrics(directory_path, language)

            result = {
                "job_id": job_id,
                "status": "completed",
                "findings": findings,
                "metrics": metrics,
                "duration_ms": duration_ms,
                "timestamp": start_time.isoformat(),
                "scanned_files": scanned_files,
                "function_metrics": function_metrics,
            }

            self.scan_jobs[job_id] = result
            return result

        except Exception as e:
            return {
                "job_id": job_id,
                "status": "error",
                "error": str(e),
                "findings": [],
                "metrics": {},
            }

    def _get_scanned_files(self, directory_path: str, language: str) -> list:
        """Get list of scanned files by type with LOC count."""
        files = []
        if not directory_path:
            return files

        path = Path(directory_path)
        if not path.exists():
            return files

        if language == "python" or language == "all":
            for py_file in path.rglob("*.py"):
                if any(pattern in str(py_file) for pattern in ["__pycache__", ".venv", "node_modules", "venv", ".git"]):
                    continue
                loc = self._count_lines(py_file)
                files.append({
                    "name": py_file.name,
                    "path": str(py_file),
                    "language": "python",
                    "loc": loc
                })

        if language == "javascript" or language == "all":
            for js_file in path.rglob("*.js"):
                if any(pattern in str(js_file) for pattern in ["node_modules", ".git"]):
                    continue
                loc = self._count_lines(js_file)
                files.append({
                    "name": js_file.name,
                    "path": str(js_file),
                    "language": "javascript",
                    "loc": loc
                })

        return files[:50]  # Return first 50 files

    def _count_lines(self, file_path: Path) -> int:
        """Count lines of code in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except (UnicodeDecodeError, IOError):
            return 0

    def get_scan_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.scan_jobs.get(job_id)

    def _calculate_quality_score(self, findings: list) -> float:
        if not findings:
            return 100.0

        severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
        total_weight = sum(
            severity_weights.get(f.get("severity", "low"), 1) for f in findings
        )

        max_deduction = 100
        deduction = min(total_weight, max_deduction)
        return max(0, 100 - deduction)

    def _calculate_complexity(self, findings: list) -> Dict[str, Any]:
        complexity_findings = [f for f in findings if "complexity" in f.get("type", "")]
        high_complexity = len([f for f in complexity_findings if f.get("severity") == "high"])

        return {
            "high_complexity_functions": high_complexity,
            "total_issues": len(complexity_findings),
            "rating": "critical" if high_complexity > 5 else "high" if high_complexity > 2 else "moderate",
        }

    def _extract_function_metrics(self, directory_path: str, language: str) -> List[Dict[str, Any]]:
        """Extract function-level complexity metrics from source files."""
        functions = []
        if not directory_path:
            return functions

        path = Path(directory_path)
        if not path.exists():
            return functions

        # Extract Python function metrics
        if language == "python" or language == "all":
            for py_file in path.rglob("*.py"):
                if any(pattern in str(py_file) for pattern in self.python_scanner.ignore_patterns):
                    continue
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    tree = ast.parse(code)
                    functions.extend(self._extract_python_functions(tree, py_file))
                except (SyntaxError, UnicodeDecodeError, IOError):
                    pass

        return functions

    def _extract_python_functions(self, tree: ast.AST, filepath: Path) -> List[Dict[str, Any]]:
        """Extract function names and complexity from Python AST."""
        functions = []

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

        class FunctionVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                complexity = count_complexity(node)
                severity = 'high' if complexity > 10 else 'medium' if complexity > 5 else 'low'
                functions.append({
                    "name": f"{node.name}()",
                    "file": str(filepath),
                    "line": node.lineno,
                    "complexity": complexity,
                    "severity": severity
                })
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                complexity = count_complexity(node)
                severity = 'high' if complexity > 10 else 'medium' if complexity > 5 else 'low'
                functions.append({
                    "name": f"{node.name}()",
                    "file": str(filepath),
                    "line": node.lineno,
                    "complexity": complexity,
                    "severity": severity
                })
                self.generic_visit(node)

        visitor = FunctionVisitor()
        visitor.visit(tree)
        return functions
