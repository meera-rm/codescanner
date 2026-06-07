"""Integration tests for FastAPI endpoints with HTTP requests."""
import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestCAQIEndpoint:
    """Test CAQI endpoint integration."""

    def test_get_team_caqi_success(self, client):
        """Test successful CAQI retrieval."""
        response = client.get("/api/v1/analytics/teams/backend-team/caqi")

        assert response.status_code == 200
        data = response.json()
        assert data["team_id"] == "backend-team"
        assert 0 <= data["overall_caqi"] <= 500
        assert "dimensions" in data
        assert "calculated_at" in data

    def test_get_team_caqi_missing_team_id(self, client):
        """Test CAQI endpoint with missing team_id."""
        response = client.get("/api/v1/analytics/teams//caqi")

        assert response.status_code in [404, 422]

    def test_caqi_has_all_dimensions(self, client):
        """Test that CAQI response includes all dimensions."""
        response = client.get("/api/v1/analytics/teams/backend-team/caqi")

        assert response.status_code == 200
        data = response.json()
        dimensions = data.get("dimensions", {})

        required_dimensions = [
            "security",
            "complexity",
            "documentation",
            "testing",
            "dependencies",
            "maintainability",
        ]

        for dim in required_dimensions:
            assert dim in dimensions
            assert 0 <= dimensions[dim] <= 100


class TestTrendsEndpoint:
    """Test trends endpoint integration."""

    def test_get_trends_success(self, client):
        """Test successful trends retrieval."""
        response = client.get("/api/v1/analytics/teams/backend-team/trends?days=30")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_trends_days_validation(self, client):
        """Test trends days parameter validation."""
        response = client.get("/api/v1/analytics/teams/backend-team/trends?days=0")

        assert response.status_code == 422

    def test_trends_max_days(self, client):
        """Test trends with maximum days."""
        response = client.get("/api/v1/analytics/teams/backend-team/trends?days=365")

        assert response.status_code == 200

    def test_trends_exceeds_max_days(self, client):
        """Test trends with days exceeding maximum."""
        response = client.get("/api/v1/analytics/teams/backend-team/trends?days=400")

        assert response.status_code == 422


class TestAnomaliesEndpoint:
    """Test anomalies endpoint integration."""

    def test_get_anomalies_success(self, client):
        """Test successful anomalies retrieval."""
        response = client.get("/api/v1/analytics/teams/backend-team/anomalies")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_anomalies_severity_filter(self, client):
        """Test anomalies severity filtering."""
        response = client.get(
            "/api/v1/analytics/teams/backend-team/anomalies?severity=critical"
        )

        assert response.status_code == 200
        data = response.json()
        for anomaly in data:
            assert anomaly.get("severity") == "critical" or not data

    def test_anomalies_invalid_severity(self, client):
        """Test anomalies with invalid severity."""
        response = client.get(
            "/api/v1/analytics/teams/backend-team/anomalies?severity=invalid"
        )

        assert response.status_code == 422

    def test_anomalies_reviewed_filter(self, client):
        """Test anomalies reviewed filter."""
        response = client.get(
            "/api/v1/analytics/teams/backend-team/anomalies?reviewed=true"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestDevelopersEndpoint:
    """Test developers endpoint integration."""

    def test_get_developers_success(self, client):
        """Test successful developers retrieval."""
        response = client.get("/api/v1/analytics/teams/backend-team/developers?days=30")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_developers_days_validation(self, client):
        """Test developers days parameter validation."""
        response = client.get("/api/v1/analytics/teams/backend-team/developers?days=0")

        assert response.status_code == 422

    def test_developers_response_format(self, client):
        """Test developers response format."""
        response = client.get("/api/v1/analytics/teams/backend-team/developers?days=30")

        assert response.status_code == 200
        data = response.json()

        for dev in data:
            assert "developerId" in dev or "developer_id" in dev
            assert "contributions" in dev
            assert "overallContribution" in dev or "overall_contribution" in dev


class TestPeerComparisonEndpoint:
    """Test peer comparison endpoint integration."""

    def test_get_peer_comparison_success(self, client):
        """Test successful peer comparison retrieval."""
        response = client.get(
            "/api/v1/analytics/teams/backend-team/peer-comparison?dimension=security"
        )

        assert response.status_code == 200
        data = response.json()
        assert "team_id" in data
        assert "dimension" in data
        assert "score" in data
        assert "percentile" in data

    def test_peer_comparison_missing_dimension(self, client):
        """Test peer comparison without dimension."""
        response = client.get("/api/v1/analytics/teams/backend-team/peer-comparison")

        assert response.status_code == 422

    def test_peer_comparison_all_dimensions(self, client):
        """Test peer comparison for all dimensions."""
        dimensions = [
            "security",
            "complexity",
            "documentation",
            "testing",
            "dependencies",
            "maintainability",
        ]

        for dim in dimensions:
            response = client.get(
                f"/api/v1/analytics/teams/backend-team/peer-comparison?dimension={dim}"
            )
            assert response.status_code == 200


class TestAlertsEndpoint:
    """Test alerts endpoint integration."""

    def test_get_alerts_success(self, client):
        """Test successful alerts retrieval."""
        response = client.get("/api/v1/analytics/teams/backend-team/alerts")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_alerts_severity_filter(self, client):
        """Test alerts severity filtering."""
        response = client.get("/api/v1/analytics/teams/backend-team/alerts?severity=high")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestBenchmarksEndpoint:
    """Test benchmarks endpoint integration."""

    def test_get_benchmarks_success(self, client):
        """Test successful benchmarks retrieval."""
        response = client.get("/api/v1/analytics/teams/backend-team/benchmarks")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestHealthEndpoint:
    """Test health endpoint integration."""

    def test_health_check(self, client):
        """Test API health check."""
        response = client.get("/api/v1/analytics/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestEndpointIntegration:
    """Test endpoint interactions and flows."""

    def test_caqi_then_trends(self, client):
        """Test getting CAQI then trends."""
        caqi_response = client.get("/api/v1/analytics/teams/backend-team/caqi")
        assert caqi_response.status_code == 200

        trends_response = client.get("/api/v1/analytics/teams/backend-team/trends?days=30")
        assert trends_response.status_code == 200

    def test_anomalies_and_alerts(self, client):
        """Test getting anomalies and alerts together."""
        anomalies_response = client.get("/api/v1/analytics/teams/backend-team/anomalies")
        assert anomalies_response.status_code == 200

        alerts_response = client.get("/api/v1/analytics/teams/backend-team/alerts")
        assert alerts_response.status_code == 200

    def test_all_endpoints_available(self, client):
        """Test all endpoints are available."""
        endpoints = [
            "/api/v1/analytics/teams/backend-team/caqi",
            "/api/v1/analytics/teams/backend-team/trends?days=30",
            "/api/v1/analytics/teams/backend-team/anomalies",
            "/api/v1/analytics/teams/backend-team/developers?days=30",
            "/api/v1/analytics/teams/backend-team/peer-comparison?dimension=security",
            "/api/v1/analytics/teams/backend-team/alerts",
            "/api/v1/analytics/teams/backend-team/benchmarks",
            "/api/v1/analytics/health",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 422], f"Endpoint {endpoint} failed: {response.status_code}"
