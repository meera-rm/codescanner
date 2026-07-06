"""Integration tests for job queue system."""
import pytest
import asyncio
from api.services.job_queue import JobQueue, JobStatus


@pytest.fixture
def queue():
    """Create a fresh job queue for each test."""
    return JobQueue()


class TestJobQueue:
    """Test job queue functionality."""

    def test_enqueue_job(self, queue):
        """Test enqueuing a new job."""
        job_id = queue.enqueue('test_job', {'data': 'test'})

        assert job_id is not None
        job = queue.get_job(job_id)
        assert job is not None
        assert job.status == JobStatus.PENDING
        assert job.data == {'data': 'test'}
        assert job.progress == 0

    def test_get_nonexistent_job(self, queue):
        """Test getting a non-existent job."""
        job = queue.get_job('nonexistent')
        assert job is None

    def test_job_progress_update(self, queue):
        """Test updating job progress."""
        job_id = queue.enqueue('test_job', {})

        queue.update_job_progress(job_id, 50)
        job = queue.get_job(job_id)
        assert job.progress == 50

    def test_progress_clamping(self, queue):
        """Test that progress is clamped to 0-100."""
        job_id = queue.enqueue('test_job', {})

        queue.update_job_progress(job_id, 150)
        job = queue.get_job(job_id)
        assert job.progress == 100

        queue.update_job_progress(job_id, -50)
        job = queue.get_job(job_id)
        assert job.progress == 0

    def test_cancel_pending_job(self, queue):
        """Test cancelling a pending job."""
        job_id = queue.enqueue('test_job', {})

        success = queue.cancel_job(job_id)
        assert success is True

        job = queue.get_job(job_id)
        assert job.status == JobStatus.CANCELLED

    def test_cannot_cancel_running_job(self, queue):
        """Test that running jobs cannot be cancelled."""
        job_id = queue.enqueue('test_job', {})
        job = queue.get_job(job_id)
        job.status = JobStatus.RUNNING

        success = queue.cancel_job(job_id)
        assert success is False

    def test_get_jobs_by_status(self, queue):
        """Test filtering jobs by status."""
        job1 = queue.enqueue('job1', {})
        job2 = queue.enqueue('job2', {})

        # Mark one as running
        job = queue.get_job(job1)
        job.status = JobStatus.RUNNING

        pending = queue.get_jobs_by_status(JobStatus.PENDING)
        assert len(pending) == 1
        assert pending[0].id == job2

        running = queue.get_jobs_by_status(JobStatus.RUNNING)
        assert len(running) == 1
        assert running[0].id == job1

    @pytest.mark.asyncio
    async def test_process_job_with_handler(self, queue):
        """Test processing a job with a registered handler."""
        async def test_handler(job):
            job.progress = 50
            return {'result': 'success', 'data': job.data}

        queue.register_handler('test_job', test_handler)
        job_id = queue.enqueue('test_job', {'input': 'data'})

        success = await queue.process_job(job_id)
        assert success is True

        job = queue.get_job(job_id)
        assert job.status == JobStatus.COMPLETED
        assert job.result == {'result': 'success', 'data': {'input': 'data'}}
        assert job.progress == 100

    @pytest.mark.asyncio
    async def test_process_job_no_handler(self, queue):
        """Test processing a job with no registered handler."""
        job_id = queue.enqueue('nonexistent_job', {})

        success = await queue.process_job(job_id)
        assert success is False

        job = queue.get_job(job_id)
        assert job.status == JobStatus.FAILED
        assert 'No handler' in job.error

    @pytest.mark.asyncio
    async def test_process_job_handler_error(self, queue):
        """Test handling errors in job processing."""
        async def failing_handler(job):
            raise Exception('Test error')

        queue.register_handler('failing_job', failing_handler)
        job_id = queue.enqueue('failing_job', {})

        success = await queue.process_job(job_id)
        assert success is False

        job = queue.get_job(job_id)
        assert job.status == JobStatus.FAILED
        assert 'Test error' in job.error

    def test_job_to_dict(self, queue):
        """Test converting job to dictionary."""
        job_id = queue.enqueue('test_job', {'key': 'value'})
        job = queue.get_job(job_id)

        job_dict = queue.to_dict(job)
        assert job_dict['id'] == job_id
        assert job_dict['job_type'] == 'test_job'
        assert job_dict['status'] == 'pending'
        assert job_dict['data'] == {'key': 'value'}
        assert job_dict['progress'] == 0

    @pytest.mark.asyncio
    async def test_sync_handler(self, queue):
        """Test processing a job with a synchronous handler."""
        def sync_handler(job):
            job.progress = 75
            return {'sync': True}

        queue.register_handler('sync_job', sync_handler)
        job_id = queue.enqueue('sync_job', {})

        success = await queue.process_job(job_id)
        assert success is True

        job = queue.get_job(job_id)
        assert job.status == JobStatus.COMPLETED
        assert job.result == {'sync': True}
