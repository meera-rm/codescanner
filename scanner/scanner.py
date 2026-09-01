#!/usr/bin/env python3
import ast
import json
import os
import sys
from pathlib import Path
from typing import List

from scanner_rules import Finding, PythonRules
from scanner_js_rules import JavaScriptRules
from scanner_sql_rules import SQLRules
from personality import (
    profile_codebase,
    generate_personality_markdown_section,
    generate_personality_html,
)
from inheritance import (
    generate_letter,
    render_letter_markdown,
    render_letter_html,
)


class PythonScanner:
    """Scans Python files for issues."""

    def __init__(self, ignore_patterns: List[str] = None):
        self.ignore_patterns = ignore_patterns or [
            "__pycache__", ".venv", "node_modules", "venv", ".git",
            "site-packages", "/test/", "/tests/", "fixtures"
        ]
        self.findings: List[Finding] = []

    def scan_file(self, filepath: str) -> List[Finding]:
        """Scan a single Python file."""
        findings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except (UnicodeDecodeError, IOError):
            return findings

        # Rule 1: Hardcoded secrets
        findings.extend(PythonRules.check_hardcoded_secrets(code, filepath))

        # Rule 2: Unused imports
        try:
            tree = ast.parse(code)
            findings.extend(PythonRules.check_unused_imports(tree, code, filepath))
            findings.extend(PythonRules.check_complexity(tree, filepath))
        except SyntaxError:
            pass  # Skip files with syntax errors

        return findings

    def scan_directory(self, directory: str) -> List[Finding]:
        """Recursively scan all Python files in a directory."""
        findings = []
        root = Path(directory)

        for py_file in root.rglob("*.py"):
            # Skip ignored directories
            if any(pattern in str(py_file) for pattern in self.ignore_patterns):
                continue

            file_findings = self.scan_file(str(py_file))
            findings.extend(file_findings)

        return findings

    def report_json(self, findings: List[Finding]) -> str:
        """Output findings as JSON."""
        return json.dumps(
            [
                {
                    "file": f.file,
                    "line": f.line,
                    "column": f.column,
                    "rule": f.rule,
                    "message": f.message,
                    "severity": f.severity,
                }
                for f in findings
            ],
            indent=2,
        )

    def report_text(self, findings: List[Finding]) -> str:
        """Output findings as readable text."""
        lines = []
        by_severity = {}

        for f in findings:
            if f.severity not in by_severity:
                by_severity[f.severity] = []
            by_severity[f.severity].append(f)

        for severity in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
            if severity in by_severity:
                lines.append(f"\n{severity}:")
                for f in by_severity[severity]:
                    lines.append(
                        f"  {f.file}:{f.line} [{f.rule}] {f.message}"
                    )

        return "\n".join(lines)


class JavaScriptScanner:
    """Scans JavaScript/React files for issues."""

    def __init__(self, ignore_patterns: List[str] = None):
        self.ignore_patterns = ignore_patterns or [
            "__pycache__", ".venv", "node_modules", "venv", ".git",
            ".next", "dist", "build", "site-packages", "/test/", "/tests/",
            "fixtures"
        ]
        self.findings: List[Finding] = []

    def scan_file(self, filepath: str) -> List[Finding]:
        """Scan a single JavaScript file."""
        findings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except (UnicodeDecodeError, IOError):
            return findings

        findings.extend(JavaScriptRules.check_hardcoded_secrets(code, filepath))
        findings.extend(JavaScriptRules.check_console_statements(code, filepath))
        findings.extend(JavaScriptRules.check_deep_nesting(code, filepath))
        findings.extend(JavaScriptRules.check_missing_error_handling(code, filepath))
        findings.extend(JavaScriptRules.check_unused_variables(code, filepath))

        return findings

    def scan_directory(self, directory: str) -> List[Finding]:
        """Recursively scan all JavaScript files in a directory."""
        findings = []
        root = Path(directory)

        for js_file in root.rglob("*.js"):
            if any(pattern in str(js_file) for pattern in self.ignore_patterns):
                continue
            findings.extend(self.scan_file(str(js_file)))

        for jsx_file in root.rglob("*.jsx"):
            if any(pattern in str(jsx_file) for pattern in self.ignore_patterns):
                continue
            findings.extend(self.scan_file(str(jsx_file)))

        for ts_file in root.rglob("*.ts"):
            if any(pattern in str(ts_file) for pattern in self.ignore_patterns):
                continue
            findings.extend(self.scan_file(str(ts_file)))

        for tsx_file in root.rglob("*.tsx"):
            if any(pattern in str(tsx_file) for pattern in self.ignore_patterns):
                continue
            findings.extend(self.scan_file(str(tsx_file)))

        return findings

    def report_json(self, findings: List[Finding]) -> str:
        """Output findings as JSON."""
        return json.dumps(
            [
                {
                    "file": f.file,
                    "line": f.line,
                    "column": f.column,
                    "rule": f.rule,
                    "message": f.message,
                    "severity": f.severity,
                }
                for f in findings
            ],
            indent=2,
        )

    def report_text(self, findings: List[Finding]) -> str:
        """Output findings as readable text."""
        lines = []
        by_severity = {}

        for f in findings:
            if f.severity not in by_severity:
                by_severity[f.severity] = []
            by_severity[f.severity].append(f)

        for severity in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
            if severity in by_severity:
                lines.append(f"\n{severity}:")
                for f in by_severity[severity]:
                    lines.append(f"  {f.file}:{f.line} [{f.rule}] {f.message}")

        return "\n".join(lines)


class SQLScanner:
    """Scans SQL files for issues."""

    def __init__(self, ignore_patterns: List[str] = None):
        self.ignore_patterns = ignore_patterns or [
            "__pycache__", ".venv", "node_modules", "venv", ".git",
            "site-packages", "/test/", "/tests/", "fixtures", "migrations/old"
        ]
        self.findings: List[Finding] = []

    def scan_file(self, filepath: str) -> List[Finding]:
        """Scan a single SQL file."""
        findings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except (UnicodeDecodeError, IOError):
            return findings

        findings.extend(SQLRules.check_hardcoded_credentials(code, filepath))
        findings.extend(SQLRules.check_select_star(code, filepath))
        findings.extend(SQLRules.check_unprotected_delete_update(code, filepath))
        findings.extend(SQLRules.check_hardcoded_ip(code, filepath))
        findings.extend(SQLRules.check_sql_injection_risk(code, filepath))
        findings.extend(SQLRules.check_comment_with_sensitive_data(code, filepath))
        findings.extend(SQLRules.check_transaction_control(code, filepath))

        return findings

    def scan_directory(self, directory: str) -> List[Finding]:
        """Recursively scan all SQL files in a directory."""
        findings = []
        root = Path(directory)

        for sql_file in root.rglob("*.sql"):
            if any(pattern in str(sql_file) for pattern in self.ignore_patterns):
                continue
            findings.extend(self.scan_file(str(sql_file)))

        return findings

    def report_json(self, findings: List[Finding]) -> str:
        """Output findings as JSON."""
        return json.dumps(
            [
                {
                    "file": f.file,
                    "line": f.line,
                    "column": f.column,
                    "rule": f.rule,
                    "message": f.message,
                    "severity": f.severity,
                }
                for f in findings
            ],
            indent=2,
        )

    def report_text(self, findings: List[Finding]) -> str:
        """Output findings as readable text."""
        lines = []
        by_severity = {}

        for f in findings:
            if f.severity not in by_severity:
                by_severity[f.severity] = []
            by_severity[f.severity].append(f)

        for severity in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
            if severity in by_severity:
                lines.append(f"\n{severity}:")
                for f in by_severity[severity]:
                    lines.append(f"  {f.file}:{f.line} [{f.rule}] {f.message}")

        return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <files_or_directory> [--python|--js|--sql] [--json] [--personality] [--personality-html FILE]")
        print("       (When called from pre-commit, filenames are passed as arguments)")
        sys.exit(1)

    output_format = "json" if "--json" in sys.argv else "text"
    language = "all"
    include_personality = "--personality" in sys.argv
    include_inheritance = "--inheritance-letter" in sys.argv
    include_creative_suite = "--creative-suite" in sys.argv

    # Creative Suite enables all three
    if include_creative_suite:
        include_personality = True
        include_inheritance = True

    # Parse --personality-html FILE
    personality_html_file = None
    for i, arg in enumerate(sys.argv):
        if arg == "--personality-html" and i + 1 < len(sys.argv):
            personality_html_file = sys.argv[i + 1]
            break

    # Parse --inheritance-html FILE
    inheritance_html_file = None
    for i, arg in enumerate(sys.argv):
        if arg == "--inheritance-html" and i + 1 < len(sys.argv):
            inheritance_html_file = sys.argv[i + 1]
            break

    if "--python" in sys.argv:
        language = "python"
    elif "--js" in sys.argv:
        language = "javascript"
    elif "--sql" in sys.argv:
        language = "sql"

    # Get files/directories to scan (all args except flags)
    paths = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    findings = []

    # Scan each path (file or directory)
    for path in paths:
        if language in ("all", "python"):
            py_scanner = PythonScanner()
            if os.path.isfile(path):
                py_findings = py_scanner.scan_file(path)
            else:
                py_findings = py_scanner.scan_directory(path)
            findings.extend(py_findings)

        if language in ("all", "javascript"):
            js_scanner = JavaScriptScanner()
            if os.path.isfile(path):
                js_findings = js_scanner.scan_file(path)
            else:
                js_findings = js_scanner.scan_directory(path)
            findings.extend(js_findings)

        if language in ("all", "sql"):
            sql_scanner = SQLScanner()
            if os.path.isfile(path):
                sql_findings = sql_scanner.scan_file(path)
            else:
                sql_findings = sql_scanner.scan_directory(path)
            findings.extend(sql_findings)

    result = {
        "findings": [
            {
                "file": f.file,
                "line": f.line,
                "column": f.column,
                "rule": f.rule,
                "message": f.message,
                "severity": f.severity,
            }
            for f in findings
        ]
    }

    # If personality requested, add it to output
    if include_personality:
        try:
            from metrics_aggregator import MetricsAggregator
            for path in paths:
                if os.path.isdir(path):
                    aggregator = MetricsAggregator()
                    metrics = aggregator.aggregate(path)
                    # Convert RepoMetrics to dict
                    metrics_dict = {
                        "avg_complexity": metrics.avg_complexity,
                        "max_complexity": metrics.max_complexity,
                        "security_high_count": metrics.security_high_count,
                        "security_medium_count": metrics.security_medium_count,
                        "smell_count": metrics.smell_count,
                        "doc_coverage_ratio": metrics.doc_coverage_ratio,
                        "duplication_percentage": metrics.duplication_percentage,
                        "avg_imports_per_file": metrics.avg_imports_per_file,
                        "circular_dep_count": metrics.circular_dep_count,
                        "total_logging": metrics.total_logging,
                        "error_handling_density": metrics.error_handling_density,
                        "total_functions": metrics.total_functions,
                        "avg_quality_score": metrics.avg_quality_score,
                        "total_lines": metrics.total_lines,
                    }
                    result["personality"] = profile_codebase(metrics_dict)
                    break  # Use first directory
        except (ImportError, Exception):
            pass  # Personality not available, continue without it

    # If inheritance letter requested, add it to output
    if include_inheritance:
        try:
            from metrics_aggregator import MetricsAggregator
            for path in paths:
                if os.path.isdir(path):
                    aggregator = MetricsAggregator()
                    metrics = aggregator.aggregate(path)
                    # Build metrics list for inheritance.py from per_file_metrics
                    metrics_list = []
                    for filepath, file_metrics in metrics.per_file_metrics.items():
                        # Calculate per-file quality score (0-100)
                        # Based on security issues, smells, and documentation
                        security_penalty = file_metrics.get("security_issues", 0) * 20
                        smell_penalty = file_metrics.get("smells", 0) * 5
                        doc_penalty = (1 - file_metrics.get("doc_coverage", 0.5)) * 20
                        quality = max(0, 100 - security_penalty - smell_penalty - doc_penalty)

                        metrics_list.append({
                            "filepath": filepath,
                            "quality_score": quality,
                            "complexity_average": 1.0,  # Placeholder
                            "security_findings": {"high": [{"type": "issue", "line": 0}] if file_metrics.get("security_issues", 0) > 0 else []},
                            "smells_count": file_metrics.get("smells", 0),
                        })
                    letter = generate_letter(metrics_list)
                    result["inheritance_letter"] = letter
                    break  # Use first directory
        except (ImportError, AttributeError, Exception) as e:
            pass  # Inheritance letter not available, continue without it

    # If Creative Suite requested, add unified analysis
    if include_creative_suite:
        try:
            from creative_suite import CreativeSuiteOrchestrator
            import uuid
            for path in paths:
                if os.path.isdir(path):
                    orchestrator = CreativeSuiteOrchestrator()
                    job_id = f"cli_{uuid.uuid4().hex[:8]}"
                    print(f"\n🎨 Running Creative Suite analysis...", file=sys.stderr)
                    suite_result = orchestrator.analyze(path, job_id)
                    result["creative_suite"] = {
                        "personality": suite_result.personality,
                        "letter": suite_result.letter,
                        "caqi": suite_result.caqi,
                        "timestamp": suite_result.timestamp,
                        "dashboard": "creative-suite-dashboard.html",
                    }
                    print(f"✅ Creative Suite analysis complete", file=sys.stderr)
                    break  # Use first directory
        except (ImportError, AttributeError, Exception) as e:
            pass  # Creative Suite not available, continue without it

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        if result["findings"]:
            print(f"Total: {len(result['findings'])} issues found")
            for finding in result["findings"]:
                print(f"  {finding['file']}:{finding['line']} [{finding['rule']}] {finding['message']}")
        else:
            print("No issues found")
        if "personality" in result:
            arch = result["personality"]["archetype"]
            emoji = result["personality"]["emoji"]
            print(f"\nPersonality: {emoji} {arch}")
        if "inheritance_letter" in result:
            tone = result["inheritance_letter"]["tone"]
            print(f"Inheritance Letter Tone: {tone.capitalize()}")

    # Write personality HTML card if requested
    if personality_html_file and "personality" in result:
        try:
            html_content = generate_personality_html(result["personality"])
            with open(personality_html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"\n✅ Personality card written to: {personality_html_file}")
        except (IOError, OSError) as e:
            print(f"\n⚠️ Failed to write personality card: {e}", file=sys.stderr)

    # Write inheritance letter if requested
    if inheritance_html_file and "inheritance_letter" in result:
        try:
            # Render as HTML (automatically self-contained with inline CSS)
            html_content = render_letter_html(result["inheritance_letter"])
            with open(inheritance_html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"✅ Inheritance letter written to: {inheritance_html_file}")
        except (IOError, OSError) as e:
            print(f"⚠️ Failed to write inheritance letter: {e}", file=sys.stderr)

    # Exit with error if critical issues found
    if any(f.severity == "CRITICAL" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
