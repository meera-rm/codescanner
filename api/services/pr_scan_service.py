"""Service for scanning GitHub PRs."""
import uuid
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import subprocess
from sqlalchemy.orm import Session

from api.db.models import PRScan, GitHubRepository
from api.services.diff_analyzer import DiffAnalyzer
from api.services.github_service import GitHubService

# Import scanners from scanner module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scanner'))
try:
    from scanner import PythonScanner, JavaScriptScanner, SQLScanner
except ImportError:
    # Fallback: mock scanners if real ones not available
    class PythonScanner:
        def scan_file(self, path):
            return []

    class JavaScriptScanner:
        def scan_file(self, path):
            return []

    class SQLScanner:
        def scan_file(self, path):
            return []


class PRScanService:
    """Scan PR changes and generate findings."""

    def __init__(self, repo_path: str, repo_id: str):
        self.repo_path = repo_path
        self.repo_id = repo_id
        self.diff_analyzer = DiffAnalyzer(repo_path)
        self.github_service = GitHubService()

    def scan_pr(
        self,
        base_branch: str,
        head_branch: str,
        pr_number: int,
        repo_name: str,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Scan a PR for code issues.

        Returns:
            {
                'pr_number': 123,
                'status': 'success',
                'files_scanned': 5,
                'files_skipped': 2,
                'findings': [...],
                'summary': {
                    'critical': 1,
                    'error': 2,
                    'warning': 5
                }
            }
        """
        try:
            # Get changed files
            changed_files = self.diff_analyzer.get_changed_files(base_branch, head_branch)

            # Filter files by language
            filtered_files = self.diff_analyzer.filter_files_by_language(
                changed_files['added'] + changed_files['modified']
            )

            # Scan files
            findings = []
            files_scanned = 0
            files_skipped = 0

            # Scan Python files
            for file_path in filtered_files.get('python', []):
                try:
                    scanner = PythonScanner()
                    file_findings = scanner.scan_file(os.path.join(self.repo_path, file_path))

                    # Add file info to each finding
                    for finding in file_findings:
                        finding['file'] = file_path
                        finding['pr_number'] = pr_number

                    findings.extend(file_findings)
                    files_scanned += 1
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")
                    files_skipped += 1

            # Scan JavaScript files
            for file_path in filtered_files.get('javascript', []):
                try:
                    scanner = JavaScriptScanner()
                    file_findings = scanner.scan_file(os.path.join(self.repo_path, file_path))

                    for finding in file_findings:
                        finding['file'] = file_path
                        finding['pr_number'] = pr_number

                    findings.extend(file_findings)
                    files_scanned += 1
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")
                    files_skipped += 1

            # Scan SQL files
            for file_path in filtered_files.get('sql', []):
                try:
                    scanner = SQLScanner()
                    file_findings = scanner.scan_file(os.path.join(self.repo_path, file_path))

                    for finding in file_findings:
                        finding['file'] = file_path
                        finding['pr_number'] = pr_number

                    findings.extend(file_findings)
                    files_scanned += 1
                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")
                    files_skipped += 1

            # Summarize findings
            summary = self._summarize_findings(findings)

            result = {
                'pr_number': pr_number,
                'status': 'success',
                'repository': repo_name,
                'files_scanned': files_scanned,
                'files_skipped': files_skipped,
                'files_changed': {
                    'added': len(changed_files['added']),
                    'modified': len(changed_files['modified']),
                    'deleted': len(changed_files['deleted'])
                },
                'findings': findings,
                'summary': summary,
                'scanned_at': datetime.utcnow().isoformat()
            }

            # Save to database if session provided
            if db:
                self._save_scan_result(db, pr_number, findings, summary)

            return result

        except Exception as e:
            print(f"Error scanning PR: {e}")
            return {
                'pr_number': pr_number,
                'status': 'error',
                'error': str(e),
                'findings': [],
                'summary': {'critical': 0, 'error': 0, 'warning': 0, 'info': 0}
            }

    def _summarize_findings(self, findings: List[Dict]) -> Dict[str, int]:
        """Count findings by severity."""
        summary = {'critical': 0, 'error': 0, 'warning': 0, 'info': 0}

        for finding in findings:
            severity = finding.get('severity', 'info').lower()
            if severity in summary:
                summary[severity] += 1

        return summary

    def _save_scan_result(
        self,
        db: Session,
        pr_number: int,
        findings: List[Dict],
        summary: Dict[str, int]
    ):
        """Save PR scan result to database."""
        try:
            pr_scan = PRScan(
                id=str(uuid.uuid4()),
                repository_id=self.repo_id,
                pr_number=pr_number,
                findings=findings,
                status='completed',
                critical_count=summary.get('critical', 0),
                error_count=summary.get('error', 0),
                warning_count=summary.get('warning', 0),
                completed_at=datetime.utcnow()
            )

            db.add(pr_scan)
            db.commit()
        except Exception as e:
            print(f"Error saving scan result: {e}")
            db.rollback()

    def generate_review_comment(self, findings: List[Dict], pr_number: int) -> str:
        """
        Generate a GitHub review comment from findings.

        Returns formatted markdown comment.
        """
        if not findings:
            return f"✅ **Code Review**: No issues found in PR #{pr_number}"

        # Group findings by severity
        by_severity = {}
        for finding in findings:
            severity = finding.get('severity', 'info').upper()
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(finding)

        # Build comment
        comment = f"## 🔍 CodePulse Review - PR #{pr_number}\n\n"

        severity_emoji = {
            'CRITICAL': '🔴',
            'ERROR': '🟠',
            'WARNING': '🟡',
            'INFO': '🔵'
        }

        # Sort by severity
        for severity in ['CRITICAL', 'ERROR', 'WARNING', 'INFO']:
            if severity not in by_severity:
                continue

            findings_list = by_severity[severity]
            emoji = severity_emoji.get(severity, '•')

            comment += f"\n### {emoji} {severity} ({len(findings_list)} issues)\n\n"

            # Group by file
            by_file = {}
            for finding in findings_list:
                file_path = finding.get('file', 'unknown')
                if file_path not in by_file:
                    by_file[file_path] = []
                by_file[file_path].append(finding)

            # Add findings for each file
            for file_path, file_findings in sorted(by_file.items()):
                comment += f"**{file_path}**\n"

                for finding in file_findings:
                    rule = finding.get('rule', 'unknown rule')
                    line = finding.get('line', 'unknown line')
                    message = finding.get('message', 'No message')

                    comment += f"- Line {line}: `{rule}` - {message}\n"

                comment += "\n"

        # Add summary
        total = len(findings)
        comment += f"\n---\n**Summary**: {total} issue(s) found | "
        comment += f"Critical: {len(by_severity.get('CRITICAL', []))} | "
        comment += f"Error: {len(by_severity.get('ERROR', []))} | "
        comment += f"Warning: {len(by_severity.get('WARNING', []))}\n"

        return comment

    def should_block_pr(self, findings: List[Dict], fail_on_critical: bool, fail_on_error: bool) -> bool:
        """
        Determine if PR should be blocked based on findings.

        Returns:
            True if PR should be blocked, False otherwise
        """
        for finding in findings:
            severity = finding.get('severity', 'info').upper()

            if fail_on_critical and severity == 'CRITICAL':
                return True

            if fail_on_error and severity == 'ERROR':
                return True

        return False
