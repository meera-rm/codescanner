import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scanner"))

from api.tasks.celery_app import app
from api.db.database import SessionLocal
from api.db.models import ScanJob

try:
    from scanner import PythonScanner, JavaScriptScanner, SQLScanner
except ImportError:
    PythonScanner = JavaScriptScanner = SQLScanner = None


@app.task(bind=True, name="api.tasks.scanning.scan_codebase_task")
def scan_codebase_task(self, job_id, path, language="python", options=None):
    """Async scanning task - processes scans in background."""
    if options is None:
        options = {
            "security": True,
            "quality_score": True,
            "code_smells": True,
            "doc_coverage": True,
            "complexity": True,
        }

    db = SessionLocal()
    try:
        job = db.query(ScanJob).filter(ScanJob.id == job_id).first()
        if not job:
            return {"error": f"Job {job_id} not found"}

        job.status = "processing"
        job.started_at = datetime.utcnow()
        db.commit()

        self.update_state(state="PROGRESS", meta={"progress": 10})

        findings = []
        scanners = []

        if language == "python" or language == "all":
            scanners.append(("python", PythonScanner()))
        if language == "javascript" or language == "all":
            scanners.append(("javascript", JavaScriptScanner()))
        if language == "sql" or language == "all":
            scanners.append(("sql", SQLScanner()))

        for lang, scanner in scanners:
            try:
                if Path(path).is_file():
                    lang_findings = scanner.scan_file(path)
                else:
                    lang_findings = scanner.scan_directory(path)
                findings.extend(lang_findings)
            except Exception as e:
                print(f"Error scanning {lang}: {e}")

        self.update_state(state="PROGRESS", meta={"progress": 50})

        metrics = {}
        if options.get("quality_score"):
            metrics["quality_score"] = _calculate_quality_score(findings)

        if options.get("complexity"):
            metrics["complexity"] = _calculate_complexity(findings)

        metrics["total_findings"] = len(findings)
        metrics["critical_count"] = len([f for f in findings if f.get("severity") == "critical"])
        metrics["high_count"] = len([f for f in findings if f.get("severity") == "high"])

        self.update_state(state="PROGRESS", meta={"progress": 90})

        job.findings = findings
        job.metrics = metrics
        job.progress = 100
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.duration_ms = int((job.completed_at - job.started_at).total_seconds() * 1000)

        db.commit()

        return {
            "job_id": job_id,
            "status": "completed",
            "findings_count": len(findings),
            "metrics": metrics,
        }

    except Exception as e:
        job = db.query(ScanJob).filter(ScanJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()


def _calculate_quality_score(findings: list) -> float:
    """Calculate quality score from findings."""
    if not findings:
        return 100.0

    severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
    total_weight = sum(
        severity_weights.get(f.get("severity", "low"), 1) for f in findings
    )

    deduction = min(total_weight, 100)
    return max(0, 100 - deduction)


def _calculate_complexity(findings: list) -> dict:
    """Calculate complexity metrics from findings."""
    complexity_findings = [f for f in findings if "complexity" in f.get("type", "")]
    high_complexity = len([f for f in complexity_findings if f.get("severity") == "high"])

    return {
        "high_complexity_functions": high_complexity,
        "total_issues": len(complexity_findings),
        "rating": "critical" if high_complexity > 5 else "high" if high_complexity > 2 else "moderate",
    }
