import re
from dataclasses import dataclass
from typing import List

from scanner_rules import Finding


class JavaScriptRules:
    """Detectable patterns in JavaScript code."""

    @staticmethod
    def check_hardcoded_secrets(code: str, filepath: str) -> List[Finding]:
        """Detect common secret patterns in JavaScript."""
        findings = []
        patterns = [
            (r"const\s+api[_-]?key\s*=\s*['\"]([a-zA-Z0-9]+)['\"]", "Hardcoded API key"),
            (r"const\s+password\s*=\s*['\"]([^\s'\"]+)['\"]", "Hardcoded password"),
            (r"const\s+token\s*=\s*['\"]([a-zA-Z0-9\-_]+)['\"]", "Hardcoded token"),
            (r"const\s+aws_secret\s*=\s*['\"]([^\s'\"]+)['\"]", "Hardcoded AWS secret"),
            (r"process\.env\.[A-Z_]+\s*=\s*['\"]([^\s'\"]+)['\"]", "Hardcoded environment variable"),
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
    def check_console_statements(code: str, filepath: str) -> List[Finding]:
        """Detect console.log, console.error left in code (dev artifacts)."""
        findings = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            if re.search(r"console\.(log|error|warn|debug)\s*\(", line):
                # Skip if in comment
                if not line.strip().startswith("//"):
                    findings.append(
                        Finding(
                            file=filepath,
                            line=line_num,
                            column=0,
                            rule="console_statement",
                            message="console.log left in code (remove before shipping)",
                            severity="WARNING",
                        )
                    )
        return findings

    @staticmethod
    def check_deep_nesting(code: str, filepath: str) -> List[Finding]:
        """Detect deeply nested code (>4 levels)."""
        findings = []
        lines = code.split("\n")
        max_depth = 0
        max_depth_line = 0

        for line_num, line in enumerate(lines, 1):
            if not line.strip() or line.strip().startswith("//"):
                continue

            depth = (len(line) - len(line.lstrip())) // 2
            if depth > max_depth:
                max_depth = depth
                max_depth_line = line_num

            if depth > 4:
                findings.append(
                    Finding(
                        file=filepath,
                        line=line_num,
                        column=0,
                        rule="deep_nesting",
                        message=f"Code nesting depth {depth} exceeds threshold (max: 4)",
                        severity="WARNING",
                    )
                )

        return findings

    @staticmethod
    def check_missing_error_handling(code: str, filepath: str) -> List[Finding]:
        """Detect .then() without .catch() or async without try/catch."""
        findings = []
        lines = code.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            if ".then(" in line:
                has_catch = False
                j = i
                while j < min(i + 10, len(lines)):
                    if ".catch(" in lines[j]:
                        has_catch = True
                        break
                    j += 1

                if not has_catch and ".finally(" not in line:
                    findings.append(
                        Finding(
                            file=filepath,
                            line=i + 1,
                            column=0,
                            rule="missing_error_handling",
                            message=".then() without .catch() (promise may reject silently)",
                            severity="WARNING",
                        )
                    )

            i += 1

        return findings

    @staticmethod
    def check_unused_variables(code: str, filepath: str) -> List[Finding]:
        """Detect obvious unused variables (regex-based, heuristic)."""
        findings = []

        pattern = r"const\s+(\w+)\s*=\s*(?:require|import|new|{|\"|\d+).*?(?:\n|$)"
        matches = re.finditer(pattern, code, re.MULTILINE)

        for match in matches:
            var_name = match.group(1)
            start_pos = match.end()
            rest_of_code = code[start_pos:]

            usage_pattern = rf"\b{re.escape(var_name)}\b"
            if not re.search(usage_pattern, rest_of_code):
                line_num = code[:match.start()].count("\n") + 1
                findings.append(
                    Finding(
                        file=filepath,
                        line=line_num,
                        column=0,
                        rule="unused_variable",
                        message=f"Variable '{var_name}' appears unused",
                        severity="WARNING",
                    )
                )

        return findings
