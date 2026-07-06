"""Tests for GitHub integration routes."""
import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestGitHubRoutes:
    """Test GitHub integration endpoints."""

    def test_authorize_missing_code(self, client):
        """Test authorization without code parameter."""
        response = client.get('/api/v1/github/authorize')
        assert response.status_code == 422  # Missing required parameter

    def test_authorize_invalid_code(self, client):
        """Test authorization with invalid code."""
        response = client.get(
            '/api/v1/github/authorize?code=invalid_code&state=test'
        )
        # Will fail because no real GitHub app is set up
        assert response.status_code in [400, 422]

    def test_webhook_invalid_signature(self, client):
        """Test webhook with invalid signature."""
        response = client.post(
            '/api/v1/github/webhook',
            headers={'X-Hub-Signature-256': 'sha256=invalid'},
            json={'action': 'opened'}
        )
        assert response.status_code == 401
        assert 'Invalid signature' in response.json()['detail']

    def test_webhook_missing_signature(self, client):
        """Test webhook without signature."""
        response = client.post(
            '/api/v1/github/webhook',
            json={'action': 'opened'}
        )
        assert response.status_code == 401

    def test_scan_pr_missing_parameters(self, client):
        """Test PR scan without required parameters."""
        response = client.post('/api/v1/github/scan-pr')
        assert response.status_code == 422  # Missing required parameters

    def test_scan_pr_repository_not_found(self, client):
        """Test PR scan for non-existent repository."""
        response = client.post(
            '/api/v1/github/scan-pr',
            params={
                'repo_name': 'nonexistent/repo',
                'pr_number': 123,
                'access_token': 'test_token'
            }
        )
        assert response.status_code == 404
        assert 'not found' in response.json()['detail'].lower()

    def test_installations_endpoint(self, client):
        """Test getting installations list."""
        response = client.get('/api/v1/github/installations/test-user')
        # Should return empty list initially (no installations)
        assert response.status_code == 200
        data = response.json()
        assert 'installations' in data
        assert isinstance(data['installations'], list)

    def test_repositories_endpoint(self, client):
        """Test getting repositories list."""
        # This requires a real access token, so it will fail
        response = client.post(
            '/api/v1/github/repositories',
            params={
                'installation_id': 'test-inst',
                'access_token': 'invalid_token'
            }
        )
        # May return 400 or 401 depending on GitHub's response
        assert response.status_code in [400, 401, 404]


class TestJobQueueEndpoints:
    """Test job queue management endpoints."""

    def test_create_job(self, client):
        """Test creating a new job."""
        response = client.post(
            '/api/v1/jobs?job_type=test_job&data={}',
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'created'
        assert 'job_id' in data
        assert data['job']['status'] == 'pending'

    def test_get_job(self, client):
        """Test getting job status."""
        # First create a job
        create_response = client.post(
            '/api/v1/jobs?job_type=test_job&data={}',
        )
        job_id = create_response.json()['job_id']

        # Get the job
        response = client.get(f'/api/v1/jobs/{job_id}')
        assert response.status_code == 200
        data = response.json()
        assert data['job']['id'] == job_id
        assert data['job']['status'] == 'pending'

    def test_get_nonexistent_job(self, client):
        """Test getting non-existent job."""
        response = client.get('/api/v1/jobs/nonexistent')
        assert response.status_code == 404
        assert 'not found' in response.json()['detail'].lower()

    def test_list_jobs(self, client):
        """Test listing jobs."""
        # Create a few jobs
        for i in range(3):
            client.post(
                f'/api/v1/jobs?job_type=test_job&data={{"index": {i}}}'
            )

        # List all jobs
        response = client.get('/api/v1/jobs')
        assert response.status_code == 200
        data = response.json()
        assert data['total'] >= 3
        assert isinstance(data['jobs'], list)

    def test_list_jobs_by_status(self, client):
        """Test listing jobs filtered by status."""
        response = client.get('/api/v1/jobs?status=pending')
        assert response.status_code == 200
        data = response.json()
        assert 'jobs' in data
        # All jobs should be pending
        for job in data['jobs']:
            assert job['status'] == 'pending'

    def test_list_jobs_invalid_status(self, client):
        """Test listing jobs with invalid status."""
        response = client.get('/api/v1/jobs?status=invalid_status')
        assert response.status_code == 400
        assert 'Invalid status' in response.json()['detail']

    def test_cancel_job(self, client):
        """Test cancelling a job."""
        # Create a job
        create_response = client.post(
            '/api/v1/jobs?job_type=test_job&data={}',
        )
        job_id = create_response.json()['job_id']

        # Cancel it
        response = client.delete(f'/api/v1/jobs/{job_id}')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'cancelled'
        assert data['job']['status'] == 'cancelled'

    def test_cancel_nonexistent_job(self, client):
        """Test cancelling non-existent job."""
        response = client.delete('/api/v1/jobs/nonexistent')
        assert response.status_code == 404
