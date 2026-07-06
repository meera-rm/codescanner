"""Job management endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.services.job_queue import job_queue, JobStatus

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("")
async def create_job(
    job_type: str,
    data: dict,
    db: Session = Depends(get_db),
):
    """Create a new background job."""
    try:
        job_id = job_queue.enqueue(job_type, data)
        job = job_queue.get_job(job_id)
        return {
            "status": "created",
            "job_id": job_id,
            "job": job_queue.to_dict(job) if job else None,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get job status and details."""
    try:
        job = job_queue.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "status": "found",
            "job": job_queue.to_dict(job),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{job_id}/process")
async def process_job(job_id: str, db: Session = Depends(get_db)):
    """Process a job (run it immediately)."""
    try:
        job = job_queue.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job.status != JobStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Job is {job.status.value}, not pending"
            )

        # Process the job
        success = await job_queue.process_job(job_id)

        job = job_queue.get_job(job_id)
        return {
            "status": "processed",
            "success": success,
            "job": job_queue.to_dict(job) if job else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}")
async def cancel_job(job_id: str, db: Session = Depends(get_db)):
    """Cancel a pending job."""
    try:
        success = job_queue.cancel_job(job_id)
        if not success:
            job = job_queue.get_job(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot cancel job in {job.status.value} state"
                )

        job = job_queue.get_job(job_id)
        return {
            "status": "cancelled",
            "job": job_queue.to_dict(job) if job else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_jobs(
    status: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List jobs with optional status filter."""
    try:
        if status:
            try:
                status_enum = JobStatus(status.lower())
                jobs = job_queue.get_jobs_by_status(status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status}"
                )
        else:
            jobs = list(job_queue.jobs.values())

        return {
            "status": "ok",
            "total": len(jobs),
            "jobs": [job_queue.to_dict(job) for job in jobs[-limit:]],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
