"""Tests for CI/CD integration API routes."""
import pytest
import json
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestCIStatus:
    """Test CI status endpoint."""

    def test_ci_status_returns_healthy(self):
        """Test that CI status endpoint returns healthy."""
        response = client.get("/api/v1/ci/status")
        assert response.status_code == 200

        data = response.json()
        assert data['status'] == 'healthy'
        assert data['version'] == '3.5.0'
        assert 'scanners' in data
        assert 'formats' in data
        assert 'endpoints' in data

    def test_ci_status_available_scanners(self):
        """Test that all scanners are reported as available."""
        response = client.get("/api/v1/ci/status")
        data = response.json()

        scanners = data['scanners']
        assert 'python' in scanners
        assert 'javascript' in scanners
        assert 'sql' in scanners

        for scanner_name, scanner_info in scanners.items():
            assert scanner_info['status'] == 'available'

    def test_ci_status_supported_formats(self):
        """Test that all report formats are listed."""
        response = client.get("/api/v1/ci/status")
        data = response.json()

        formats = data['formats']
        assert 'json' in formats
        assert 'sarif' in formats
        assert 'junit' in formats
        assert 'sonarqube' in formats


class TestCIScan:
    """Test CI scan endpoint."""

    def test_scan_repository_current_directory(self):
        """Test scanning current repository."""
        payload = {
            "repository": ".",
            "branch": "main",
            "output_format": "json",
            "fail_on_critical": False,
            "fail_on_error": False,
        }

        response = client.post("/api/v1/ci/scan", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['status'] in ['completed', 'failed']
        assert 'summary' in data
        assert 'files_scanned' in data
        assert 'files_by_language' in data

    def test_scan_with_json_format(self):
        """Test scan with JSON output format."""
        payload = {
            "repository": ".",
            "output_format": "json",
        }

        response = client.post("/api/v1/ci/scan", json=payload)
        data = response.json()

        assert 'report' in data

    def test_scan_with_sarif_format(self):
        """Test scan with SARIF output format."""
        payload = {
            "repository": ".",
            "output_format": "sarif",
        }

        response = client.post("/api/v1/ci/scan", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['status'] in ['completed', 'failed']
        assert data['report'] is not None

    def test_scan_with_junit_format(self):
        """Test scan with JUnit output format."""
        payload = {
            "repository": ".",
            "output_format": "junit",
        }

        response = client.post("/api/v1/ci/scan", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['status'] in ['completed', 'failed']

    def test_scan_with_sonarqube_format(self):
        """Test scan with SonarQube output format."""
        payload = {
            "repository": ".",
            "output_format": "sonarqube",
        }

        response = client.post("/api/v1/ci/scan", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['status'] in ['completed', 'failed']
        assert data['report'] is not None

    def test_scan_fail_on_critical(self):
        """Test fail_on_critical flag."""
        payload = {
            "repository": ".",
            "fail_on_critical": True,
        }

        response = client.post("/api/v1/ci/scan", json=payload)
        data = response.json()

        # If critical issues found, exit_code should be 1
        if data['summary'].get('critical', 0) > 0:
            assert data['exit_code'] == 1
        else:
            assert data['exit_code'] == 0

    def test_scan_fail_on_error(self):
        """Test fail_on_error flag."""
        payload = {
            "repository": ".",
            "fail_on_error": True,
        }

        response = client.post("/api/v1/ci/scan", json=payload)
        data = response.json()

        # If error issues found, exit_code should be 1
        if data['summary'].get('error', 0) > 0:
            assert data['exit_code'] == 1

    def test_scan_invalid_repository(self):
        """Test scan with invalid repository path."""
        payload = {
            "repository": "/nonexistent/path/to/repo",
        }

        response = client.post("/api/v1/ci/scan", json=payload)
        assert response.status_code == 400

    def test_scan_returns_required_fields(self):
        """Test that scan response includes all required fields."""
        payload = {"repository": "."}

        response = client.post("/api/v1/ci/scan", json=payload)
        data = response.json()

        required_fields = [
            'status',
            'repository',
            'branch',
            'files_scanned',
            'files_by_language',
            'summary',
            'exit_code',
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_scan_summary_has_severity_counts(self):
        """Test that summary includes severity counts."""
        payload = {"repository": "."}

        response = client.post("/api/v1/ci/scan", json=payload)
        data = response.json()
        summary = data['summary']

        severity_fields = ['critical', 'error', 'warning', 'info', 'total']
        for field in severity_fields:
            assert field in summary, f"Missing field in summary: {field}"
            assert isinstance(summary[field], int)


class TestBatchScan:
    """Test batch scan endpoint."""

    def test_batch_scan_single_repository(self):
        """Test batch scan with single repository."""
        payload = {
            "repositories": ["."],
        }

        response = client.post("/api/v1/ci/batch-scan", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['total'] == 1
        assert data['completed'] >= 0
        assert data['failed'] >= 0
        assert len(data['results']) == 1

    def test_batch_scan_multiple_repositories(self):
        """Test batch scan with multiple repositories."""
        payload = {
            "repositories": [".", ".", "."],
        }

        response = client.post("/api/v1/ci/batch-scan", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['total'] == 3
        assert len(data['results']) == 3

    def test_batch_scan_with_output_format(self):
        """Test batch scan with specific output format."""
        payload = {
            "repositories": ["."],
            "output_format": "sarif",
        }

        response = client.post("/api/v1/ci/batch-scan", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert len(data['results']) == 1

    def test_batch_scan_returns_summary(self):
        """Test that batch scan returns correct summary."""
        payload = {
            "repositories": [".", ".", "."],
        }

        response = client.post("/api/v1/ci/batch-scan", json=payload)
        data = response.json()

        assert data['total'] == data['completed'] + data['failed']


class TestCIWebhook:
    """Test CI webhook endpoint."""

    def test_webhook_from_github(self):
        """Test webhook from GitHub Actions."""
        payload = {
            "platform": "github",
            "event": "push",
            "repository": "owner/repo",
            "branch": "main",
            "commit_hash": "abc123def456",
        }

        response = client.post("/api/v1/ci/webhook", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['status'] == 'received'
        assert 'webhook_id' in data
        assert 'scan_job_id' in data
        assert 'platform' in data
        assert data['platform'] == 'github'

    def test_webhook_from_gitlab(self):
        """Test webhook from GitLab CI."""
        payload = {
            "platform": "gitlab",
            "event": "push",
            "repository": "group/project",
            "branch": "develop",
        }

        response = client.post("/api/v1/ci/webhook", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['status'] == 'received'
        assert data['platform'] == 'gitlab'

    def test_webhook_from_jenkins(self):
        """Test webhook from Jenkins."""
        payload = {
            "platform": "jenkins",
            "event": "build_complete",
            "repository": "/job/my-job",
        }

        response = client.post("/api/v1/ci/webhook", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data['status'] == 'received'
        assert data['platform'] == 'jenkins'

    def test_webhook_missing_platform(self):
        """Test webhook without platform."""
        payload = {
            "event": "push",
            "repository": "owner/repo",
        }

        response = client.post("/api/v1/ci/webhook", json=payload)
        assert response.status_code == 400

    def test_webhook_missing_event(self):
        """Test webhook without event."""
        payload = {
            "platform": "github",
            "repository": "owner/repo",
        }

        response = client.post("/api/v1/ci/webhook", json=payload)
        assert response.status_code == 400

    def test_webhook_returns_job_id(self):
        """Test that webhook returns job ID for tracking."""
        payload = {
            "platform": "github",
            "event": "push",
            "repository": "owner/repo",
        }

        response = client.post("/api/v1/ci/webhook", json=payload)
        data = response.json()

        assert 'scan_job_id' in data
        assert data['scan_job_id'].startswith('job_')


class TestCIIntegration:
    """Integration tests for CI endpoints."""

    def test_status_then_scan(self):
        """Test checking status before scanning."""
        # Check status
        status_response = client.get("/api/v1/ci/status")
        assert status_response.status_code == 200

        # Scan
        scan_payload = {"repository": "."}
        scan_response = client.post("/api/v1/ci/scan", json=scan_payload)
        assert scan_response.status_code == 200

    def test_multiple_scan_formats(self):
        """Test scanning with different formats sequentially."""
        formats = ['json', 'sarif', 'junit', 'sonarqube']

        for fmt in formats:
            payload = {
                "repository": ".",
                "output_format": fmt,
            }

            response = client.post("/api/v1/ci/scan", json=payload)
            assert response.status_code == 200, f"Failed for format: {fmt}"

    def test_webhook_then_batch_scan(self):
        """Test receiving webhook then running batch scan."""
        # Simulate webhook
        webhook_payload = {
            "platform": "github",
            "event": "push",
            "repository": "owner/repo",
        }

        webhook_response = client.post("/api/v1/ci/webhook", json=webhook_payload)
        assert webhook_response.status_code == 200

        # Run batch scan
        batch_payload = {"repositories": ["."], }
        batch_response = client.post("/api/v1/ci/batch-scan", json=batch_payload)
        assert batch_response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
