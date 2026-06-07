"""Tests for Advanced Analytics REST API endpoints."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime


# Mock FastAPI app for testing
from fastapi import FastAPI

app = FastAPI()

# Import routes
from api.routes.advanced_analytics import router
app.include_router(router)

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check_returns_ok(self):
        """Should return ok status."""
        response = client.get("/api/v1/analytics/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_check_includes_timestamp(self):
        """Should include current timestamp."""
        response = client.get("/api/v1/analytics/health")
        data = response.json()

        assert "timestamp" in data
        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(data["timestamp"])


class TestTeamCAQIEndpoint:
    """Test team CAQI score endpoint."""

    def test_get_team_caqi_success(self):
        """Should return team CAQI data."""
        response = client.get("/api/v1/analytics/teams/team-1/caqi")

        assert response.status_code == 200
        data = response.json()

        assert data["team_id"] == "team-1"
        assert "overall_caqi" in data
        assert "security" in data
        assert "complexity" in data
        assert "documentation" in data
        assert "testing" in data
        assert "dependencies" in data
        assert "maintainability" in data
        assert "calculated_at" in data

    def test_get_team_caqi_dimensions_range(self):
        """Should return dimensions in valid range."""
        response = client.get("/api/v1/analytics/teams/team-1/caqi")
        data = response.json()

        # CAQI is 0-500
        assert 0 <= data["overall_caqi"] <= 500

        # Dimensions are 0-100
        for dim in ["security", "complexity", "documentation", "testing", "dependencies", "maintainability"]:
            assert 0 <= data[dim] <= 100


class TestTeamTrendsEndpoint:
    """Test team trends endpoint."""

    def test_get_team_trends_default_days(self):
        """Should return trends with default 30 days."""
        response = client.get("/api/v1/analytics/teams/team-1/trends")

        assert response.status_code == 200
        data = response.json()

        assert data["team_id"] == "team-1"
        assert data["period_days"] == 30
        assert data["trend_direction"] in ["improving", "stable", "declining"]
        assert "change_percent" in data
        assert "history" in data

    def test_get_team_trends_custom_days(self):
        """Should accept custom day range."""
        response = client.get("/api/v1/analytics/teams/team-1/trends?days=90")

        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 90

    def test_get_team_trends_day_limits(self):
        """Should enforce day limits (1-365)."""
        # Too low
        response = client.get("/api/v1/analytics/teams/team-1/trends?days=0")
        assert response.status_code == 422

        # Too high
        response = client.get("/api/v1/analytics/teams/team-1/trends?days=400")
        assert response.status_code == 422

    def test_get_team_trends_valid_ranges(self):
        """Should accept valid day ranges."""
        for days in [1, 30, 90, 180, 365]:
            response = client.get(f"/api/v1/analytics/teams/team-1/trends?days={days}")
            assert response.status_code == 200
            assert response.json()["period_days"] == days


class TestAnomaliesEndpoint:
    """Test anomalies endpoint."""

    def test_get_anomalies_basic(self):
        """Should return anomalies list."""
        response = client.get("/api/v1/analytics/teams/team-1/anomalies")

        assert response.status_code == 200
        data = response.json()

        assert data["team_id"] == "team-1"
        assert "anomaly_count" in data
        assert "unreviewed_count" in data
        assert "anomalies" in data
        assert isinstance(data["anomalies"], list)

    def test_get_anomalies_with_severity_filter(self):
        """Should filter anomalies by severity."""
        for severity in ["low", "medium", "high", "critical"]:
            response = client.get(f"/api/v1/analytics/teams/team-1/anomalies?severity={severity}")
            assert response.status_code == 200

    def test_get_anomalies_invalid_severity(self):
        """Should reject invalid severity."""
        response = client.get("/api/v1/analytics/teams/team-1/anomalies?severity=invalid")
        assert response.status_code == 422

    def test_get_anomalies_reviewed_filter(self):
        """Should filter by reviewed status."""
        for reviewed in [True, False]:
            response = client.get(f"/api/v1/analytics/teams/team-1/anomalies?reviewed={reviewed}")
            assert response.status_code == 200


class TestDeveloperContributionsEndpoint:
    """Test developer contributions endpoint."""

    def test_get_developer_contributions_basic(self):
        """Should return developer contributions."""
        response = client.get("/api/v1/analytics/teams/team-1/developers")

        assert response.status_code == 200
        data = response.json()

        assert data["team_id"] == "team-1"
        assert "period_days" in data
        assert "developer_count" in data
        assert "contributions" in data

    def test_get_developer_contributions_custom_days(self):
        """Should accept custom analysis period."""
        response = client.get("/api/v1/analytics/teams/team-1/developers?days=60")

        assert response.status_code == 200
        assert response.json()["period_days"] == 60

    def test_get_developer_contributions_by_dimension(self):
        """Should filter by dimension."""
        for dim in ["security", "complexity", "documentation", "testing", "dependencies", "maintainability"]:
            response = client.get(f"/api/v1/analytics/teams/team-1/developers?dimension={dim}")
            assert response.status_code == 200

    def test_get_developer_contributions_invalid_dimension(self):
        """Should reject invalid dimension."""
        response = client.get("/api/v1/analytics/teams/team-1/developers?dimension=invalid")
        assert response.status_code == 422

    def test_get_developer_contributions_day_limits(self):
        """Should enforce day limits."""
        response = client.get("/api/v1/analytics/teams/team-1/developers?days=0")
        assert response.status_code == 422

        response = client.get("/api/v1/analytics/teams/team-1/developers?days=366")
        assert response.status_code == 422


class TestPeerComparisonEndpoint:
    """Test peer comparison endpoint."""

    def test_get_peer_comparison_basic(self):
        """Should return peer comparison data."""
        response = client.get("/api/v1/analytics/teams/team-1/peer-comparison?peer_group=backend")

        assert response.status_code == 200
        data = response.json()

        assert data["team_id"] == "team-1"
        assert data["peer_group"] == "backend"
        assert "peer_count" in data
        assert "peer_avg_caqi" in data
        assert "dimensions" in data

    def test_get_peer_comparison_requires_peer_group(self):
        """Should require peer_group parameter."""
        response = client.get("/api/v1/analytics/teams/team-1/peer-comparison")
        assert response.status_code == 422

    def test_get_peer_comparison_different_groups(self):
        """Should work with different peer groups."""
        for group in ["backend", "frontend", "platform", "all"]:
            response = client.get(f"/api/v1/analytics/teams/team-1/peer-comparison?peer_group={group}")
            assert response.status_code == 200
            assert response.json()["peer_group"] == group


class TestAlertsEndpoint:
    """Test alerts endpoint."""

    def test_get_alerts_basic(self):
        """Should return team alerts."""
        response = client.get("/api/v1/analytics/teams/team-1/alerts")

        assert response.status_code == 200
        data = response.json()

        assert data["team_id"] == "team-1"
        assert "alert_count" in data
        assert "unacknowledged_count" in data
        assert "alerts" in data

    def test_get_alerts_with_severity_filter(self):
        """Should filter alerts by severity."""
        for severity in ["low", "medium", "high", "critical"]:
            response = client.get(f"/api/v1/analytics/teams/team-1/alerts?severity={severity}")
            assert response.status_code == 200

    def test_get_alerts_invalid_severity(self):
        """Should reject invalid severity."""
        response = client.get("/api/v1/analytics/teams/team-1/alerts?severity=invalid")
        assert response.status_code == 422

    def test_get_alerts_acknowledged_filter(self):
        """Should filter by acknowledgment status."""
        for acked in [True, False]:
            response = client.get(f"/api/v1/analytics/teams/team-1/alerts?acknowledged={acked}")
            assert response.status_code == 200

    def test_get_alerts_limit_parameter(self):
        """Should respect limit parameter."""
        response = client.get("/api/v1/analytics/teams/team-1/alerts?limit=50")
        assert response.status_code == 200

    def test_get_alerts_limit_bounds(self):
        """Should enforce limit bounds (1-100)."""
        response = client.get("/api/v1/analytics/teams/team-1/alerts?limit=0")
        assert response.status_code == 422

        response = client.get("/api/v1/analytics/teams/team-1/alerts?limit=101")
        assert response.status_code == 422

    def test_get_alerts_default_limit(self):
        """Should use default limit of 10."""
        response = client.get("/api/v1/analytics/teams/team-1/alerts")
        assert response.status_code == 200


class TestBenchmarksEndpoint:
    """Test benchmarks endpoint."""

    def test_get_benchmarks_company(self):
        """Should return company benchmarks."""
        response = client.get("/api/v1/analytics/teams/team-1/benchmarks?benchmark_type=company")

        assert response.status_code == 200
        data = response.json()

        assert data["team_id"] == "team-1"
        assert data["benchmark_type"] == "company"
        assert "dimensions" in data
        assert "sample_size" in data

    def test_get_benchmarks_industry(self):
        """Should return industry benchmarks."""
        response = client.get("/api/v1/analytics/teams/team-1/benchmarks?benchmark_type=industry")

        assert response.status_code == 200

    def test_get_benchmarks_peer_group(self):
        """Should return peer group benchmarks."""
        response = client.get("/api/v1/analytics/teams/team-1/benchmarks?benchmark_type=peer_group")

        assert response.status_code == 200

    def test_get_benchmarks_requires_type(self):
        """Should require benchmark_type parameter."""
        response = client.get("/api/v1/analytics/teams/team-1/benchmarks")
        assert response.status_code == 422

    def test_get_benchmarks_invalid_type(self):
        """Should reject invalid benchmark type."""
        response = client.get("/api/v1/analytics/teams/team-1/benchmarks?benchmark_type=invalid")
        assert response.status_code == 422

    def test_get_benchmarks_all_types(self):
        """Should work for all benchmark types."""
        for btype in ["company", "industry", "peer_group"]:
            response = client.get(f"/api/v1/analytics/teams/team-1/benchmarks?benchmark_type={btype}")
            assert response.status_code == 200


class TestRouterMeta:
    """Test router configuration."""

    def test_router_prefix(self):
        """Should use correct prefix."""
        assert router.prefix == "/api/v1/analytics"

    def test_router_tags(self):
        """Should have correct tags."""
        assert "advanced_analytics" in router.tags

    def test_all_endpoints_are_get(self):
        """All advanced analytics endpoints should be GET."""
        for route in router.routes:
            if hasattr(route, 'methods'):
                assert 'GET' in route.methods or 'HEAD' in route.methods
