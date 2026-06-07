import sys
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scanner"))

from scanner import PythonScanner, JavaScriptScanner, SQLScanner


class ScannerService:
    def __init__(self):
        self.python_scanner = PythonScanner()
        self.js_scanner = JavaScriptScanner()
        self.sql_scanner = SQLScanner()
        self.scan_jobs: Dict[str, Dict[str, Any]] = {}

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
            if language == "python" or language == "all":
                if code:
                    findings.extend(self.python_scanner.scan_code(code))
                elif directory_path:
                    findings.extend(self.python_scanner.scan_directory(directory_path))

            if language == "javascript" or language == "all":
                if code:
                    findings.extend(self.js_scanner.scan_code(code))
                elif directory_path:
                    findings.extend(self.js_scanner.scan_directory(directory_path))

            if language == "sql" or language == "all":
                if code:
                    findings.extend(self.sql_scanner.scan_code(code))
                elif directory_path:
                    findings.extend(self.sql_scanner.scan_directory(directory_path))

            if options.get("quality_score"):
                metrics["quality_score"] = self._calculate_quality_score(findings)

            if options.get("complexity"):
                metrics["complexity"] = self._calculate_complexity(findings)

            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            result = {
                "job_id": job_id,
                "status": "completed",
                "findings": findings,
                "metrics": metrics,
                "duration_ms": duration_ms,
                "timestamp": start_time.isoformat(),
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
