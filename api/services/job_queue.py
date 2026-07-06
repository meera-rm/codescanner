"""Simple async job queue service for background scanning."""
import uuid
import asyncio
from typing import Dict, Optional, Callable, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import json


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Represents a background job."""
    id: str
    job_type: str  # 'pr_scan', 'repo_scan', etc.
    status: JobStatus
    data: Dict[str, Any]  # Job parameters
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: int = 0  # 0-100
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class JobQueue:
    """Simple in-memory job queue with async support."""

    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.handlers: Dict[str, Callable] = {}
        self.running = False

    def register_handler(self, job_type: str, handler: Callable):
        """Register a handler for a job type."""
        self.handlers[job_type] = handler

    def enqueue(self, job_type: str, data: Dict[str, Any]) -> str:
        """
        Enqueue a new job.

        Args:
            job_type: Type of job (e.g., 'pr_scan')
            data: Job data/parameters

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            job_type=job_type,
            status=JobStatus.PENDING,
            data=data
        )
        self.jobs[job_id] = job
        return job_id

    async def process_job(self, job_id: str) -> bool:
        """
        Process a job.

        Args:
            job_id: Job ID to process

        Returns:
            True if successful, False otherwise
        """
        job = self.jobs.get(job_id)
        if not job:
            return False

        # Check if handler exists
        handler = self.handlers.get(job.job_type)
        if not handler:
            job.status = JobStatus.FAILED
            job.error = f"No handler for job type: {job.job_type}"
            job.completed_at = datetime.utcnow()
            return False

        try:
            # Update status
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.progress = 10

            # Execute handler
            if asyncio.iscoroutinefunction(handler):
                result = await handler(job)
            else:
                # Run sync handler in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, handler, job)

            # Update job with result
            job.status = JobStatus.COMPLETED
            job.result = result
            job.progress = 100
            job.completed_at = datetime.utcnow()
            return True

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.progress = 0
            job.completed_at = datetime.utcnow()
            return False

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return self.jobs.get(job_id)

    def update_job_progress(self, job_id: str, progress: int):
        """Update job progress (0-100)."""
        job = self.jobs.get(job_id)
        if job:
            job.progress = min(100, max(0, progress))

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        job = self.jobs.get(job_id)
        if job and job.status == JobStatus.PENDING:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            return True
        return False

    def get_jobs_by_status(self, status: JobStatus) -> list:
        """Get all jobs with a specific status."""
        return [job for job in self.jobs.values() if job.status == status]

    def to_dict(self, job: Job) -> Dict[str, Any]:
        """Convert job to dictionary."""
        return {
            'id': job.id,
            'job_type': job.job_type,
            'status': job.status.value,
            'progress': job.progress,
            'data': job.data,
            'result': job.result,
            'error': job.error,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
        }


# Global job queue instance
job_queue = JobQueue()
