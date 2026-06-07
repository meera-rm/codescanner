import re
from dataclasses import dataclass
from typing import List

from scanner_rules import Finding


class SQLRules:
    """Detectable patterns in SQL code."""

    @staticmethod
    def check_hardcoded_credentials(code: str, filepath: str) -> List[Finding]:
        """Detect hardcoded passwords, API keys in SQL files and connection strings."""
        findings = []
        patterns = [
            (r"password\s*=\s*['\"]([^\s'\"]+)['\"]", "Hardcoded password in connection string"),
            (r"passwd\s*=\s*['\"]([^\s'\"]+)['\"]", "Hardcoded password in connection string"),
            (r"api[_-]?key\s*=\s*['\"]([a-zA-Z0-9]+)['\"]", "Hardcoded API key"),
            (r"secret\s*=\s*['\"]([^\s'\"]+)['\"]", "Hardcoded secret"),
            (r"token\s*=\s*['\"]([a-zA-Z0-9\-_]+)['\"]", "Hardcoded token"),
            (r"USER\s+['\"]?([a-zA-Z0-9_]+)['\"]?\s+IDENTIFIED\s+BY\s+['\"]([^\s'\"]+)['\"]", "Hardcoded credentials in CREATE USER"),
        ]

        for line_num, line in enumerate(code.split("\n"), 1):
            for pattern, msg in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        Finding(
                            file=filepath,
                            line=line_num,
                            column=0,
                            rule="hardcoded_credentials",
                            message=msg,
                            severity="CRITICAL",
                        )
                    )
        return findings

    @staticmethod
    def check_select_star(code: str, filepath: str) -> List[Finding]:
        """Detect SELECT * queries (should be explicit about columns)."""
        findings = []

        pattern = r"SELECT\s+\*\s+FROM"
        for line_num, line in enumerate(code.split("\n"), 1):
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(
                    Finding(
                        file=filepath,
                        line=line_num,
                        column=0,
                        rule="select_star",
                        message="SELECT * is vague; explicitly list required columns",
                        severity="WARNING",
                    )
                )
        return findings

    @staticmethod
    def check_unprotected_delete_update(code: str, filepath: str) -> List[Finding]:
        """Detect DELETE/UPDATE without WHERE clause (dangerous bulk operations)."""
        findings = []

        lines = code.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            if re.search(r"^\s*DELETE\s+FROM", line, re.IGNORECASE):
                has_where = False
                j = i
                while j < min(i + 5, len(lines)):
                    if re.search(r"WHERE", lines[j], re.IGNORECASE):
                        has_where = True
                        break
                    if re.search(r";$", lines[j]):
                        break
                    j += 1

                if not has_where:
                    findings.append(
                        Finding(
                            file=filepath,
                            line=i + 1,
                            column=0,
                            rule="unprotected_delete",
                            message="DELETE without WHERE clause (will delete all rows!)",
                            severity="CRITICAL",
                        )
                    )

            elif re.search(r"^\s*UPDATE\s+\w+\s+SET", line, re.IGNORECASE):
                has_where = False
                j = i
                while j < min(i + 5, len(lines)):
                    if re.search(r"WHERE", lines[j], re.IGNORECASE):
                        has_where = True
                        break
                    if re.search(r";$", lines[j]):
                        break
                    j += 1

                if not has_where:
                    findings.append(
                        Finding(
                            file=filepath,
                            line=i + 1,
                            column=0,
                            rule="unprotected_update",
                            message="UPDATE without WHERE clause (will update all rows!)",
                            severity="CRITICAL",
                        )
                    )

            i += 1

        return findings

    @staticmethod
    def check_hardcoded_ip(code: str, filepath: str) -> List[Finding]:
        """Detect hardcoded IP addresses (should use config/env vars)."""
        findings = []

        pattern = r"(?:localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)"
        for line_num, line in enumerate(code.split("\n"), 1):
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(
                    Finding(
                        file=filepath,
                        line=line_num,
                        column=0,
                        rule="hardcoded_ip",
                        message="Hardcoded IP address (use environment variables)",
                        severity="WARNING",
                    )
                )
        return findings

    @staticmethod
    def check_sql_injection_risk(code: str, filepath: str) -> List[Finding]:
        """Detect potential SQL injection patterns (string concatenation with user input)."""
        findings = []

        patterns = [
            r"SELECT.*\+.*\$",  # Concatenation with variables
            r"WHERE.*\+.*\$",
            r"INSERT.*\+.*\$",
            r"UPDATE.*\+.*\$",
            r"f['\"].*\{.*\}.*['\"]",  # f-strings in SQL
            r"FROM.*\+\s*user",
            r"WHERE.*\+\s*request",
        ]

        for line_num, line in enumerate(code.split("\n"), 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        Finding(
                            file=filepath,
                            line=line_num,
                            column=0,
                            rule="sql_injection_risk",
                            message="Potential SQL injection: string concatenation detected (use parameterized queries)",
                            severity="ERROR",
                        )
                    )
                    break

        return findings

    @staticmethod
    def check_comment_with_sensitive_data(code: str, filepath: str) -> List[Finding]:
        """Detect comments containing sensitive information."""
        findings = []

        patterns = [
            (r"--.*password", "Comment contains 'password'"),
            (r"--.*secret", "Comment contains 'secret'"),
            (r"--.*api[_-]?key", "Comment contains API key reference"),
            (r"--.*TODO.*delete", "TODO comment about deletes (incomplete logic?)"),
            (r"/\*.*password.*\*/", "Block comment contains 'password'"),
        ]

        for line_num, line in enumerate(code.split("\n"), 1):
            for pattern, msg in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(
                        Finding(
                            file=filepath,
                            line=line_num,
                            column=0,
                            rule="sensitive_comment",
                            message=msg,
                            severity="WARNING",
                        )
                    )
                    break

        return findings

    @staticmethod
    def check_transaction_control(code: str, filepath: str) -> List[Finding]:
        """Detect missing transaction control (BEGIN/COMMIT)."""
        findings = []

        multi_statement_pattern = r";\s*[A-Z]"
        has_transaction = bool(
            re.search(r"BEGIN|START\s+TRANSACTION|COMMIT|ROLLBACK", code, re.IGNORECASE)
        )

        if not has_transaction:
            for line_num, line in enumerate(code.split("\n"), 1):
                if re.search(multi_statement_pattern, line):
                    findings.append(
                        Finding(
                            file=filepath,
                            line=line_num,
                            column=0,
                            rule="missing_transaction",
                            message="Multiple statements without transaction control (use BEGIN/COMMIT)",
                            severity="WARNING",
                        )
                    )
                    break

        return findings
