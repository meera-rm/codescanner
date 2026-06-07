from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path

from scanner import PythonScanner, JavaScriptScanner, SQLScanner
from scanner_rules import Finding
from smells import SmellDetector
from doc_coverage import DocCoverageDetector
from duplication import DuplicationDetector
from coupling import CouplingDetector


@dataclass
class RepoMetrics:
    """Unified repository metrics from all detectors."""
    # Complexity (from scanner)
    avg_complexity: float
    max_complexity: float

    # Security (from scanner)
    security_high_count: int
    security_medium_count: int

    # Smells (from detector)
    smell_count: int

    # Docs (from detector)
    doc_coverage_ratio: float  # 0.0 to 1.0

    # Duplication (from detector)
    duplication_percentage: float  # 0.0 to 100.0

    # Coupling (from detector)
    avg_imports_per_file: float
    has_circular_deps: bool
    circular_dep_count: int = 0  # NEW: count of circular dependencies

    # Quality scoring (NEW: for personality profiler)
    avg_quality_score: float = 0.0  # 0-100 (for perfectionism trait)
    total_logging: int = 0  # NEW: total log statements across codebase
    error_handling_density: float = 0.0  # NEW: 0-100 (error handling presence)
    total_functions: int = 0  # NEW: total functions for trait calculations

    # Metadata
    files_analyzed: int = 0
    total_lines: int = 0

    # Per-file breakdown (optional)
    per_file_metrics: Dict[str, dict] = field(default_factory=dict)


class MetricsAggregator:
    """Aggregates metrics from all detectors into unified repository metrics."""

    def __init__(self):
        self.py_scanner = PythonScanner()
        self.js_scanner = JavaScriptScanner()
        self.sql_scanner = SQLScanner()
        self.smell_detector = SmellDetector()
        self.doc_detector = DocCoverageDetector()
        self.duplication_detector = DuplicationDetector()
        self.coupling_detector = CouplingDetector()

    def aggregate(self, directory: str) -> RepoMetrics:
        """
        Aggregate all metrics from a directory.

        Args:
            directory: Path to analyze

        Returns:
            RepoMetrics with all combined metrics
        """
        # Step 1: Run scanner to get complexity and security
        print("📊 Running scanner for complexity and security...")
        scanner_findings = self._run_scanner(directory)
        complexity_metrics = self._extract_complexity_metrics(scanner_findings)
        security_metrics = self._extract_security_metrics(scanner_findings)

        # Step 2: Run smell detector
        print("👃 Analyzing code smells...")
        smell_count = self._run_smell_detector(directory)

        # Step 3: Run docs detector
        print("📝 Analyzing documentation coverage...")
        doc_coverage = self._run_docs_detector(directory)

        # Step 4: Run duplication detector
        print("🔄 Analyzing code duplication...")
        duplication_pct = self._run_duplication_detector(directory)

        # Step 5: Run coupling detector
        print("🔗 Analyzing module coupling...")
        coupling_metrics = self._run_coupling_detector(directory)

        # Step 6: Count files and lines
        file_count, total_lines = self._count_files_and_lines(directory)

        # Step 7: Build per-file metrics
        print("📋 Building per-file metrics...")
        per_file = self._build_per_file_metrics(directory, scanner_findings)

        # Step 8: Extract logging and function metrics (for personality profiler)
        logging_metrics = self._extract_logging_metrics(directory)
        quality_score = self._calculate_quality_score(
            complexity_metrics, security_metrics, smell_count, doc_coverage, duplication_pct
        )
        error_handling = self._calculate_error_handling_density(scanner_findings)
        total_funcs = self._count_total_functions(directory)

        return RepoMetrics(
            avg_complexity=complexity_metrics["avg"],
            max_complexity=complexity_metrics["max"],
            security_high_count=security_metrics["high"],
            security_medium_count=security_metrics["medium"],
            smell_count=smell_count,
            doc_coverage_ratio=doc_coverage,
            duplication_percentage=duplication_pct,
            avg_imports_per_file=coupling_metrics["avg_imports"],
            has_circular_deps=coupling_metrics["has_circular"],
            circular_dep_count=coupling_metrics.get("circular_count", 0),
            avg_quality_score=quality_score,
            total_logging=logging_metrics["total"],
            error_handling_density=error_handling,
            total_functions=total_funcs,
            files_analyzed=file_count,
            total_lines=total_lines,
            per_file_metrics=per_file,
        )

    def _run_scanner(self, directory: str) -> List[Finding]:
        """Run all scanners and collect findings."""
        findings = []

        # Only scan Python for now (most complexity/security metrics)
        findings.extend(self.py_scanner.scan_directory(directory))

        return findings

    def _extract_complexity_metrics(self, findings: List[Finding]) -> dict:
        """Extract complexity metrics from scanner findings."""
        complexity_findings = [
            f for f in findings if f.rule == "cyclomatic_complexity"
        ]

        if not complexity_findings:
            return {"avg": 0.0, "max": 0.0}

        # Parse complexity values from message (e.g., "Cyclomatic complexity: 8")
        complexities = []
        for f in complexity_findings:
            try:
                # Message format: "Cyclomatic complexity: X"
                value = float(f.message.split(":")[-1].strip())
                complexities.append(value)
            except (ValueError, IndexError):
                pass

        if not complexities:
            return {"avg": 0.0, "max": 0.0}

        return {
            "avg": sum(complexities) / len(complexities),
            "max": max(complexities),
        }

    def _extract_security_metrics(self, findings: List[Finding]) -> dict:
        """Extract security metrics from scanner findings."""
        high_count = sum(
            1 for f in findings if f.severity in ("CRITICAL", "ERROR")
        )
        medium_count = sum(1 for f in findings if f.severity == "WARNING")

        return {"high": high_count, "medium": medium_count}

    def _run_smell_detector(self, directory: str) -> int:
        """Run smell detector and count smells."""
        py_files = list(Path(directory).rglob("*.py"))
        skip_patterns = ["test", "tests", "fixtures", "__pycache__", ".venv"]
        py_files = [
            f for f in py_files
            if not any(pattern in str(f) for pattern in skip_patterns)
        ]

        total_smells = 0
        for py_file in py_files:
            findings = self.smell_detector.detect(str(py_file))
            total_smells += len(findings)

        return total_smells

    def _run_docs_detector(self, directory: str) -> float:
        """Run docs detector and calculate coverage ratio."""
        py_files = list(Path(directory).rglob("*.py"))
        skip_patterns = ["test", "tests", "fixtures", "__pycache__", ".venv"]
        py_files = [
            f for f in py_files
            if not any(pattern in str(f) for pattern in skip_patterns)
        ]

        total_functions = 0
        documented_functions = 0

        for py_file in py_files:
            metrics = self.doc_detector.analyze(str(py_file))
            if metrics:
                total_functions += metrics.total_functions
                documented_functions += metrics.documented_functions

        if total_functions == 0:
            return 1.0  # If no functions, assume 100% coverage

        return documented_functions / total_functions

    def _run_duplication_detector(self, directory: str) -> float:
        """Run duplication detector and return percentage."""
        metrics = self.duplication_detector.analyze_directory(directory)
        return metrics.duplication_percentage

    def _run_coupling_detector(self, directory: str) -> dict:
        """Run coupling detector and extract metrics."""
        metrics = self.coupling_detector.analyze_directory(directory)
        return {
            "avg_imports": metrics.avg_imports_per_file,
            "has_circular": metrics.has_circular_deps,
        }

    def _count_files_and_lines(self, directory: str) -> tuple:
        """Count Python files and total lines of code."""
        py_files = list(Path(directory).rglob("*.py"))
        skip_patterns = ["test", "tests", "fixtures", "__pycache__", ".venv"]
        py_files = [
            f for f in py_files
            if not any(pattern in str(f) for pattern in skip_patterns)
        ]

        total_lines = 0
        for py_file in py_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    total_lines += len(f.readlines())
            except (UnicodeDecodeError, IOError):
                pass

        return len(py_files), total_lines

    def _build_per_file_metrics(
        self, directory: str, scanner_findings: List[Finding]
    ) -> Dict[str, dict]:
        """Build per-file metrics breakdown."""
        per_file = {}
        py_files = list(Path(directory).rglob("*.py"))
        skip_patterns = ["test", "tests", "fixtures", "__pycache__", ".venv"]
        py_files = [
            f for f in py_files
            if not any(pattern in str(f) for pattern in skip_patterns)
        ]

        for py_file in py_files:
            filepath = str(py_file)
            relative_path = str(py_file.relative_to(directory))

            # Get scanner findings for this file
            file_findings = [f for f in scanner_findings if f.file == filepath]

            # Get smells for this file
            smell_findings = self.smell_detector.detect(filepath)

            # Get docs for this file
            doc_metrics = self.doc_detector.analyze(filepath)

            # Get line count
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    line_count = len(f.readlines())
            except (UnicodeDecodeError, IOError):
                line_count = 0

            per_file[relative_path] = {
                "lines": line_count,
                "security_issues": len([f for f in file_findings if f.severity in ("CRITICAL", "ERROR")]),
                "warnings": len([f for f in file_findings if f.severity == "WARNING"]),
                "smells": len(smell_findings),
                "doc_coverage": doc_metrics.coverage_ratio if doc_metrics else 0.0,
                "functions": doc_metrics.total_functions if doc_metrics else 0,
                "documented_functions": doc_metrics.documented_functions if doc_metrics else 0,
            }

        return per_file

    def _extract_logging_metrics(self, directory: str) -> dict:
        """Extract logging count from Python files."""
        total_logging = 0
        py_files = list(Path(directory).rglob("*.py"))
        skip_patterns = ["test", "tests", "fixtures", "__pycache__", ".venv"]
        py_files = [
            f for f in py_files
            if not any(pattern in str(f) for pattern in skip_patterns)
        ]

        import re
        logging_pattern = re.compile(r'(logging\.|print\(|logger\.)', re.IGNORECASE)

        for py_file in py_files:
            try:
                with open(str(py_file), "r", encoding="utf-8") as f:
                    content = f.read()
                    total_logging += len(logging_pattern.findall(content))
            except (UnicodeDecodeError, IOError):
                pass

        return {"total": total_logging}

    def _calculate_quality_score(
        self, complexity: dict, security: dict, smells: int, docs: float, duplication: float
    ) -> float:
        """Calculate overall quality score (0-100)."""
        # Quality inversely related to complexity, security issues, smells, and duplication
        # Directly related to documentation
        complexity_penalty = min(100, complexity.get("avg", 0) * 10)
        security_penalty = min(100, (security.get("high", 0) * 40 + security.get("medium", 0) * 20))
        smell_penalty = min(100, smells * 5)
        duplication_penalty = min(100, duplication)

        doc_bonus = docs * 100  # 0-100

        # Weighted calculation
        quality = 100 - (
            complexity_penalty * 0.25 +
            security_penalty * 0.35 +
            smell_penalty * 0.15 +
            duplication_penalty * 0.15
        ) + (doc_bonus * 0.10)

        return max(0, min(100, quality))

    def _calculate_error_handling_density(self, findings: List[Finding]) -> float:
        """Calculate error handling density (presence of try/except, etc)."""
        error_handling = sum(1 for f in findings if "error" in f.rule.lower())
        try_except = sum(1 for f in findings if "exception" in f.message.lower())

        # Normalize to 0-100 scale (higher = more error handling)
        density = (error_handling + try_except) * 5
        return min(100, density)

    def _count_total_functions(self, directory: str) -> int:
        """Count total functions in codebase."""
        total = 0
        py_files = list(Path(directory).rglob("*.py"))
        skip_patterns = ["test", "tests", "fixtures", "__pycache__", ".venv"]
        py_files = [
            f for f in py_files
            if not any(pattern in str(f) for pattern in skip_patterns)
        ]

        import ast
        for py_file in py_files:
            try:
                with open(str(py_file), "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                    total += sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            except (SyntaxError, UnicodeDecodeError, IOError):
                pass

        return total

    def report(self, metrics: RepoMetrics) -> dict:
        """Generate a summary report."""
        return {
            "summary": {
                "files": metrics.files_analyzed,
                "lines": metrics.total_lines,
                "complexity_avg": metrics.avg_complexity,
                "complexity_max": metrics.avg_complexity,
                "security_high": metrics.security_high_count,
                "security_medium": metrics.security_medium_count,
                "smells": metrics.smell_count,
                "doc_coverage": metrics.doc_coverage_ratio,
                "duplication": metrics.duplication_percentage,
                "avg_imports": metrics.avg_imports_per_file,
                "circular_deps": metrics.has_circular_deps,
                "quality_score": metrics.avg_quality_score,
                "total_logging": metrics.total_logging,
                "error_handling_density": metrics.error_handling_density,
            },
            "per_file": metrics.per_file_metrics,
        }
