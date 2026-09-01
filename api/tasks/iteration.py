"""Background task for Iteration Until Clean.

Runs via FastAPI's BackgroundTasks, not a task queue -- see
api/routes/iteration.py's background_tasks.add_task() call site.
"""

import uuid
import asyncio
from datetime import datetime
from api.services.iteration_clean_service import IterationCleanService
from api.services.scanner_service import ScannerService
from api.db.database import SessionLocal
from api.db.models import IterationJob, IterationHistory


def fix_until_clean_task(job_id: str,
                         directory_path: str,
                         target_grade: str = "A",
                         max_iterations: int = 10):
    """
    Background task for iteration until clean.

    Args:
        job_id: Unique job identifier
        directory_path: Path to codebase
        target_grade: Target grade
        max_iterations: Maximum iterations

    Returns:
        Job result with status and metrics
    """

    db = SessionLocal()

    try:
        # Update job status to started
        job = db.query(IterationJob).filter(IterationJob.id == job_id).first()
        if not job:
            return {"status": "failed", "error": "Job not found"}

        job.status = "processing"
        job.started_at = datetime.utcnow()
        db.commit()

        # Run iteration until clean
        service = IterationCleanService()
        result = fix_until_clean_sync(
            job_id=job_id,
            codebase_path=directory_path,
            target_grade=target_grade,
            max_iterations=max_iterations,
        )

        # Update job with results
        job.status = result["status"]
        job.final_grade = result["final_grade"]
        job.current_grade = result["final_grade"]
        job.current_iteration = result["iterations_count"]
        job.metrics = result["metrics"]
        job.completed_at = datetime.utcnow()

        # Save iteration history
        for step_data in result.get("history", []):
            history = IterationHistory(
                id=str(uuid.uuid4()),
                job_id=job_id,
                iteration_number=step_data["iteration_number"],
                grade_before=step_data["grade_before"],
                grade_after=step_data["grade_after"],
                issues_fixed=step_data["issues_fixed"],
                agent_selected=step_data["agent_selected"],
                fix_description=step_data["fix_description"],
                validation_passed=step_data["validation_passed"],
                changes=step_data.get("changes", {}),
            )
            db.add(history)

        db.commit()

        return {
            "status": "success",
            "job_id": job_id,
            "final_grade": result["final_grade"],
            "iterations": result["iterations_count"],
        }

    except Exception as e:
        # Update job with error
        job = db.query(IterationJob).filter(IterationJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()

        return {
            "status": "failed",
            "job_id": job_id,
            "error": str(e),
        }

    finally:
        db.close()


def fix_until_clean_sync(job_id: str,
                        codebase_path: str,
                        target_grade: str = "A",
                        max_iterations: int = 10) -> dict:
    """
    Synchronous version of fix_until_clean using asyncio.run().

    Calls the real IterationCleanService.fix_until_clean() and returns
    result data that can be stored in the database.

    Args:
        job_id: Unique job identifier
        codebase_path: Path to codebase to iterate
        target_grade: Target grade (A, B, C, etc)
        max_iterations: Maximum iterations before stopping

    Returns:
        Dict with status, grade info, and iteration history
    """
    try:
        # Create service with real scanner
        scanner = ScannerService()
        service = IterationCleanService(scanner_service=scanner)

        # Run async iteration loop synchronously
        result = asyncio.run(
            service.fix_until_clean(
                job_id=job_id,
                codebase_path=codebase_path,
                target_grade=target_grade,
                max_iterations=max_iterations,
            )
        )

        # Convert IterationResult dataclass to dict for database storage
        return {
            "status": result.status,
            "job_id": result.job_id,
            "start_grade": result.start_grade,
            "final_grade": result.final_grade,
            "grade_improvement": result.grade_improvement,
            "iterations_count": result.iterations_count,
            "max_iterations": result.max_iterations,
            "history": [
                {
                    "iteration_number": h.iteration_number,
                    "grade_before": h.grade_before,
                    "grade_after": h.grade_after,
                    "issues_fixed": h.issues_fixed,
                    "agent_selected": h.agent_selected,
                    "fix_description": h.fix_description,
                    "validation_passed": h.validation_passed,
                    "changes": h.changes,
                }
                for h in result.history
            ],
            "metrics": result.metrics,
        }

    except Exception as e:
        # Return error result that will be stored in database
        return {
            "status": "failed",
            "job_id": job_id,
            "start_grade": "unknown",
            "final_grade": "unknown",
            "grade_improvement": 0,
            "iterations_count": 0,
            "max_iterations": max_iterations,
            "history": [],
            "metrics": {"error": str(e)},
        }
