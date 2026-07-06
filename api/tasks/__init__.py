"""Background tasks for CodePulse AI."""
from api.services.job_queue import job_queue
from api.tasks.pr_scan_task import scan_pr_task

# Initialize job queue handlers
job_queue.register_handler('pr_scan', scan_pr_task)

__all__ = ["job_queue"]
