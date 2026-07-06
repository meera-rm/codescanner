"""Tests for CI/CD Dashboard routes and services."""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.main import app
from api.db.database import get_db, SessionLocal
from api.db.models import CIScanHistory, CITrendMetrics
from api.services.ci_history_service import CIHistoryService

client = TestClient(app)


@pytest.fixture
def db():
    """Create a test database session."""
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def sample_scans(db: Session):
    """Create sample scan history records."""
    import uuid
    scans = []
    base_time = datetime.utcnow()

    # Create 10 scans over the last 30 days
    for i in range(10):
        scan = CIScanHistory(
            id=str(uuid.uuid4()),
            repository=f"repo-{i % 3}",
            branch="main" if i % 2 == 0 else "develop",
            platform=["github", "gitlab", "jenkins"][i % 3],
            event_type="push" if i % 2 == 0 else "pull_request",
            status="success" if i % 2 == 0 else "failure",
            critical_count=i % 3,
            error_count=i % 4,
            warning_count=10 + i,
            info_count=i,
            total_findings=20 + i,
            files_scanned=100 + i * 10,
            languages={"python": 50 + i, "javascript": 30, "sql": 5},
            duration_ms=5000 + i * 1000,
            created_at=base_time - timedelta(days=i),
        )
        db.add(scan)
        scans.append(scan)

    db.commit()
    return scans


class TestCIDashboardRoutes:
    """Test CI/CD Dashboard API routes."""

    def test_get_scan_history(self, db: Session, sample_scans):
        """Test fetching scan history."""
        response = client.get("/api/v1/ci-dashboard/history")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_scan_history_with_filters(self, db: Session, sample_scans):
        """Test scan history with filters."""
        response = client.get("/api/v1/ci-dashboard/history?platform=github&days=30")
        assert response.status_code == 200

        data = response.json()
        assert all(scan["platform"] == "github" for scan in data)

    def test_get_scan_history_limit(self, db: Session, sample_scans):
        """Test scan history with limit."""
        response = client.get("/api/v1/ci-dashboard/history?limit=5")
        assert response.status_code == 200

        data = response.json()
        assert len(data) <= 5

    def test_get_dashboard_summary(self, db: Session, sample_scans):
        """Test getting dashboard summary."""
        response = client.get("/api/v1/ci-dashboard/summary")
        assert response.status_code == 200

        data = response.json()
        assert "total_scans" in data
        assert "successful_scans" in data
        assert "failed_scans" in data
        assert "pass_rate" in data
        assert "repositories" in data
        assert "platforms" in data

    def test_get_dashboard_summary_calculations(self, db: Session, sample_scans):
        """Test that summary calculations are correct."""
        response = client.get("/api/v1/ci-dashboard/summary")
        data = response.json()

        # Verify calculations
        assert data["total_scans"] == data["successful_scans"] + data["failed_scans"]
        assert data["pass_rate"] == (data["successful_scans"] / data["total_scans"] * 100)

    def test_get_latest_scans(self, db: Session, sample_scans):
        """Test getting latest scans."""
        response = client.get("/api/v1/ci-dashboard/latest-scans?limit=5")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_latest_scans_ordering(self, db: Session, sample_scans):
        """Test that latest scans are in correct order."""
        response = client.get("/api/v1/ci-dashboard/latest-scans?limit=10")
        data = response.json()

        # Verify descending order
        timestamps = [scan["timestamp"] for scan in data]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_get_repository_stats(self, db: Session, sample_scans):
        """Test getting repository statistics."""
        response = client.get("/api/v1/ci-dashboard/repository-stats/repo-0")
        assert response.status_code == 200

        data = response.json()
        assert data["repository"] == "repo-0"
        assert "total_scans" in data
        assert "pass_rate" in data
        assert "by_platform" in data

    def test_get_repository_stats_not_found(self, db: Session):
        """Test getting stats for non-existent repository."""
        response = client.get("/api/v1/ci-dashboard/repository-stats/nonexistent")
        assert response.status_code == 404

    def test_record_scan(self, db: Session):
        """Test recording a new scan."""
        response = client.post(
            "/api/v1/ci-dashboard/record-scan",
            params={
                "repository": "test-repo",
                "branch": "main",
                "platform": "github",
                "event_type": "push",
                "status": "success",
                "critical_count": 0,
                "error_count": 2,
                "warning_count": 15,
                "info_count": 5,
                "files_scanned": 150,
                "duration_ms": 5000,
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "recorded"
        assert "test-repo" in data["message"]

        # Verify it was actually saved
        history = client.get("/api/v1/ci-dashboard/history?repository=test-repo")
        assert len(history.json()) > 0

    def test_cleanup_old_scans(self, db: Session, sample_scans):
        """Test cleanup of old scans."""
        import uuid
        # Add a very old scan
        old_scan = CIScanHistory(
            id=str(uuid.uuid4()),
            repository="old-repo",
            branch="main",
            platform="github",
            event_type="push",
            status="success",
            critical_count=0,
            error_count=0,
            warning_count=0,
            info_count=0,
            files_scanned=100,
            created_at=datetime.utcnow() - timedelta(days=100),
        )
        db.add(old_scan)
        db.commit()

        response = client.delete("/api/v1/ci-dashboard/cleanup-old-scans?days=90")
        assert response.status_code == 200

        data = response.json()
        assert data["deleted"] >= 1


class TestCIHistoryService:
    """Test CI history service functionality."""

    def test_record_scan_creates_entry(self, db: Session):
        """Test that recording a scan creates a database entry."""
        scan = CIHistoryService.record_scan(
            db,
            repository="test-repo",
            branch="main",
            platform="github",
            event_type="push",
            status="success",
            critical_count=0,
            error_count=2,
            warning_count=15,
            info_count=5,
            files_scanned=100,
            languages={"python": 50, "javascript": 30},
            duration_ms=5000,
        )

        assert scan.id is not None
        assert scan.repository == "test-repo"
        assert scan.status == "success"

    def test_get_scan_history_filters(self, db: Session, sample_scans):
        """Test scan history filtering."""
        history = CIHistoryService.get_scan_history(
            db,
            repository="repo-0",
            platform="github",
        )

        assert all(s.repository == "repo-0" for s in history)
        assert all(s.platform == "github" for s in history)

    def test_update_trend_metrics(self, db: Session, sample_scans):
        """Test updating trend metrics."""
        metrics = CIHistoryService.update_trend_metrics(db, "repo-0")

        assert metrics is not None
        assert metrics.repository == "repo-0"
        assert metrics.total_scans > 0
        assert metrics.pass_rate >= 0

    def test_get_trend_metrics(self, db: Session, sample_scans):
        """Test getting trend metrics."""
        # First update them
        CIHistoryService.update_trend_metrics(db, "repo-0")

        metrics = CIHistoryService.get_trend_metrics(db, "repo-0")
        assert metrics is not None
        assert "critical_trend" in metrics.__dict__
        assert "error_trend" in metrics.__dict__

    def test_get_dashboard_summary_empty(self, db: Session):
        """Test dashboard summary returns valid structure even with minimal data."""
        summary = CIHistoryService.get_dashboard_summary(db)

        # Should return a valid structure with expected keys
        assert "total_scans" in summary
        assert "pass_rate" in summary
        assert "repositories" in summary
        assert isinstance(summary["total_scans"], int)
        assert isinstance(summary["pass_rate"], float)

    def test_get_dashboard_summary_with_data(self, db: Session, sample_scans):
        """Test dashboard summary with sample data."""
        summary = CIHistoryService.get_dashboard_summary(db)

        assert summary["total_scans"] > 0
        assert "repositories" in summary
        assert "platforms" in summary
        assert len(summary["repositories"]) > 0

    def test_delete_old_scans(self, db: Session, sample_scans):
        """Test deleting old scans."""
        import uuid
        # Add a very old scan
        old_scan = CIScanHistory(
            id=str(uuid.uuid4()),
            repository="old-repo",
            branch="main",
            platform="github",
            event_type="push",
            status="success",
            critical_count=0,
            error_count=0,
            warning_count=0,
            info_count=0,
            files_scanned=100,
            created_at=datetime.utcnow() - timedelta(days=100),
        )
        db.add(old_scan)
        db.commit()

        # Delete scans older than 90 days
        count = CIHistoryService.delete_old_scans(db, days=90)
        assert count >= 1

    def test_trend_metrics_calculations(self, db: Session, sample_scans):
        """Test that trend metrics are calculated correctly."""
        metrics = CIHistoryService.update_trend_metrics(db, "repo-0")

        # Verify trend data structure
        assert isinstance(metrics.critical_trend, list)
        assert isinstance(metrics.error_trend, list)
        assert isinstance(metrics.warning_trend, list)
        assert isinstance(metrics.pass_rate_trend, list)

        # Verify trend entries have correct structure
        for entry in metrics.critical_trend:
            assert "date" in entry
            assert "count" in entry


class TestCIDashboardIntegration:
    """Integration tests for CI Dashboard."""

    def test_full_workflow(self, db: Session):
        """Test complete workflow: record scan → update metrics → fetch summary."""
        # Record a scan
        scan = CIHistoryService.record_scan(
            db,
            repository="my-repo",
            branch="main",
            platform="github",
            event_type="push",
            status="success",
            critical_count=0,
            error_count=1,
            warning_count=10,
            info_count=5,
            files_scanned=100,
            languages={"python": 50},
            duration_ms=5000,
        )

        # Get summary
        summary = CIHistoryService.get_dashboard_summary(db)

        assert summary["total_scans"] >= 1
        assert summary["total_error"] >= 1
        assert summary["total_warning"] >= 10

    def test_api_and_service_consistency(self, db: Session, sample_scans):
        """Test that API and service return consistent data."""
        # Get from service
        service_history = CIHistoryService.get_scan_history(db, limit=5)

        # Get from API
        api_response = client.get("/api/v1/ci-dashboard/history?limit=5")
        api_history = api_response.json()

        # They should have same length
        assert len(service_history) == len(api_history)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
