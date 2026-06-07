"""Routes for Iteration Until Clean API."""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.db.models import IterationJob, IterationHistory
from api.models.iteration_requests import FixUntilCleanRequest, CancelIterationRequest
from api.models.iteration_responses import (
    IterationJobStartedResponse,
    IterationStatusResponse,
    IterationProgressResponse,
    IterationHistoryResponse,
    IterationStepResponse,
)
from api.tasks.iteration import fix_until_clean_task

router = APIRouter(prefix="/api/v1/iteration", tags=["iteration"])


@router.post(
    "/fix-until-clean",
    response_model=IterationJobStartedResponse,
    status_code=202,
    summary="Start iteration until clean job",
    description="Start a new job to iteratively improve code until target grade is reached",
)
async def start_fix_until_clean(
    request: FixUntilCleanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Start iteration until clean job.

    Returns 202 Accepted with job_id for tracking progress.
    """

    try:
        # Generate job ID
        job_id = f"iterate_{uuid.uuid4().hex[:8]}"

        # Create job record
        job = IterationJob(
            id=job_id,
            directory_path=request.directory_path,
            target_grade=request.target_grade,
            max_iterations=request.max_iterations,
            status="queued",
            created_at=datetime.utcnow(),
        )
        db.add(job)
        db.commit()

        # Queue background task
        background_tasks.add_task(
            fix_until_clean_task,
            job_id=job_id,
            directory_path=request.directory_path,
            target_grade=request.target_grade,
            max_iterations=request.max_iterations,
        )

        return IterationJobStartedResponse(
            job_id=job_id,
            status="processing",
            message=f"Starting iteration until {request.target_grade}...",
            created_at=job.created_at,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{job_id}",
    response_model=IterationStatusResponse,
    summary="Get iteration job status",
    description="Get current status and progress of an iteration job",
)
async def get_iteration_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get iteration job status and progress.

    Returns full job details including history and metrics.
    """

    job = db.query(IterationJob).filter(IterationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Calculate progress
    progress_percent = 0
    if job.max_iterations > 0:
        progress_percent = min(100, int((job.current_iteration / job.max_iterations) * 100))

    # Build history response
    history_records = db.query(IterationHistory).filter(
        IterationHistory.job_id == job_id
    ).order_by(IterationHistory.iteration_number).all()

    history = [
        IterationStepResponse(
            iteration_number=h.iteration_number,
            grade_before=h.grade_before,
            grade_after=h.grade_after,
            issues_fixed=h.issues_fixed,
            agent_selected=h.agent_selected,
            fix_description=h.fix_description,
            validation_passed=h.validation_passed,
            applied_at=h.applied_at,
            changes=h.changes or {},
        )
        for h in history_records
    ]

    return IterationStatusResponse(
        job_id=job_id,
        status=job.status,
        start_grade=job.start_grade or "unknown",
        final_grade=job.final_grade or job.current_grade or "unknown",
        grade_improvement=job.final_grade is not None and len(history) > 0,
        iterations_count=job.current_iteration,
        max_iterations=job.max_iterations,
        current_iteration=job.current_iteration,
        target_grade=job.target_grade,
        progress_percent=progress_percent,
        history=history,
        metrics=job.metrics or {},
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
    )


@router.get(
    "/{job_id}/progress",
    response_model=IterationProgressResponse,
    summary="Get iteration job progress (lightweight)",
    description="Get lightweight progress update for a job (no history)",
)
async def get_iteration_progress(job_id: str, db: Session = Depends(get_db)):
    """
    Get lightweight progress update.

    Returns only current status, no full history.
    """

    job = db.query(IterationJob).filter(IterationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Calculate progress
    progress_percent = 0
    if job.max_iterations > 0:
        progress_percent = min(100, int((job.current_iteration / job.max_iterations) * 100))

    return IterationProgressResponse(
        job_id=job_id,
        status=job.status,
        current_iteration=job.current_iteration,
        max_iterations=job.max_iterations,
        current_grade=job.current_grade,
        target_grade=job.target_grade,
        progress_percent=progress_percent,
    )


@router.get(
    "/{job_id}/history",
    response_model=IterationHistoryResponse,
    summary="Get detailed iteration history",
    description="Get detailed history of all iterations for a job",
)
async def get_iteration_history(job_id: str, db: Session = Depends(get_db)):
    """
    Get detailed iteration history.

    Returns all iteration steps with detailed information.
    """

    job = db.query(IterationJob).filter(IterationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get history records
    history_records = db.query(IterationHistory).filter(
        IterationHistory.job_id == job_id
    ).order_by(IterationHistory.iteration_number).all()

    history = [
        IterationStepResponse(
            iteration_number=h.iteration_number,
            grade_before=h.grade_before,
            grade_after=h.grade_after,
            issues_fixed=h.issues_fixed,
            agent_selected=h.agent_selected,
            fix_description=h.fix_description,
            validation_passed=h.validation_passed,
            applied_at=h.applied_at,
            changes=h.changes or {},
        )
        for h in history_records
    ]

    # Calculate summary
    agents_used = {}
    total_issues_fixed = 0
    for h in history_records:
        agent_name = h.agent_selected
        agents_used[agent_name] = agents_used.get(agent_name, 0) + 1
        total_issues_fixed += h.issues_fixed

    summary = {
        "total_iterations": len(history_records),
        "total_issues_fixed": total_issues_fixed,
        "agents_used": agents_used,
        "final_grade": job.final_grade,
    }

    return IterationHistoryResponse(
        job_id=job_id,
        iterations=history,
        summary=summary,
    )


@router.post(
    "/{job_id}/cancel",
    status_code=202,
    summary="Cancel iteration job",
    description="Cancel a running or queued iteration job",
)
async def cancel_iteration(
    job_id: str,
    request: CancelIterationRequest,
    db: Session = Depends(get_db),
):
    """
    Cancel an iteration job.

    Returns status of cancellation request.
    """

    job = db.query(IterationJob).filter(IterationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == "completed" or job.status == "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job in {job.status} state"
        )

    job.status = "cancelled"
    job.error_message = request.reason or "Cancelled by user"
    job.completed_at = datetime.utcnow()
    db.commit()

    return {
        "job_id": job_id,
        "status": "cancelled",
        "message": "Job cancellation requested",
    }


@router.delete(
    "/{job_id}",
    status_code=204,
    summary="Delete iteration job",
    description="Delete a completed iteration job and its history",
)
async def delete_iteration_job(job_id: str, db: Session = Depends(get_db)):
    """
    Delete an iteration job and its history.

    Can only delete completed or failed jobs.
    """

    job = db.query(IterationJob).filter(IterationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete job in {job.status} state"
        )

    # Delete history first (foreign key)
    db.query(IterationHistory).filter(IterationHistory.job_id == job_id).delete()
    db.delete(job)
    db.commit()

    return None
