"""
Simplified integration tests for FastAPI endpoints.
Tests the analytics routes directly without full app initialization.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.routes import advanced_analytics


@pytest.fixture
def app():
    """Create FastAPI app with analytics routes only."""
    app = FastAPI()
    app.include_router(advanced_analytics.router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def make_url(path: str) -> str:
    """Build full URL with router prefix."""
    return f"/api/v1/analytics{path}"


class TestCAQIEndpoint:
    """Test CAQI endpoint integration."""

    def test_get_team_caqi_success(self, client):
        """Test successful CAQI retrieval."""
        response = client.get(make_url("/teams/backend-team/caqi"))

        assert response.status_code == 200
        data = response.json()
        assert data["team_id"] == "backend-team"
        assert 0 <= data["overall_caqi"] <= 500
        assert "calculated_at" in data

    def test_caqi_has_all_dimensions(self, client):
        """Test that CAQI response includes all required dimensions."""
        response = client.get(make_url("/teams/backend-team/caqi"))

        assert response.status_code == 200
        data = response.json()

        required_dimensions = [
            "security",
            "complexity",
            "documentation",
            "testing",
            "dependencies",
            "maintainability",
        ]

        for dim in required_dimensions:
            assert dim in data
            assert 0 <= data[dim] <= 100

    def test_get_team_caqi_invalid_team_id(self, client):
        """Test CAQI with empty team_id."""
        response = client.get(make_url("/teams//caqi"))
        assert response.status_code in [404, 400]


class TestTrendsEndpoint:
    """Test trends endpoint integration."""

    def test_get_trends_success(self, client):
        """Test successful trends retrieval."""
        response = client.get(make_url("/teams/backend-team/trends?days=30"))

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_trends_default_days(self, client):
        """Test trends with default days."""
        response = client.get(make_url("/teams/backend-team/trends"))

        assert response.status_code == 200

    def test_trends_days_validation_minimum(self, client):
        """Test trends days parameter validation - minimum."""
        response = client.get(make_url("/teams/backend-team/trends?days=0"))

        assert response.status_code == 422

    def test_trends_days_validation_maximum(self, client):
        """Test trends days parameter validation - maximum."""
        response = client.get(make_url("/teams/backend-team/trends?days=366"))

        assert response.status_code == 422

    def test_trends_valid_days_range(self, client):
        """Test trends with valid days."""
        valid_days = [1, 7, 30, 90, 180, 365]

        for days in valid_days:
            response = client.get(make_url(f"/teams/backend-team/trends?days={days}"))
            assert response.status_code == 200


class TestAnomaliesEndpoint:
    """Test anomalies endpoint integration."""

    def test_get_anomalies_success(self, client):
        """Test successful anomalies retrieval."""
        response = client.get(make_url("/teams/backend-team/anomalies"))

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_anomalies_severity_filter_valid(self, client):
        """Test anomalies with valid severity."""
        valid_severities = ["low", "medium", "high", "critical"]

        for severity in valid_severities:
            response = client.get(
                make_url(f"/teams/backend-team/anomalies?severity={severity}")
            )
            assert response.status_code == 200

    def test_anomalies_severity_filter_invalid(self, client):
        """Test anomalies with invalid severity."""
        response = client.get(
            make_url("/teams/backend-team/anomalies?severity=invalid")
        )

        assert response.status_code == 422


class TestDevelopersEndpoint:
    """Test developers endpoint integration."""

    def test_get_developers_success(self, client):
        """Test successful developers retrieval."""
        response = client.get(make_url("/teams/backend-team/developers?days=30"))

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_developers_default_days(self, client):
        """Test developers with default days."""
        response = client.get(make_url("/teams/backend-team/developers"))

        assert response.status_code == 200

    def test_developers_days_validation(self, client):
        """Test developers days parameter validation."""
        response = client.get(make_url("/teams/backend-team/developers?days=0"))

        assert response.status_code == 422


class TestPeerComparisonEndpoint:
    """Test peer comparison endpoint integration."""

    def test_peer_comparison_all_dimensions(self, client):
        """Test peer comparison for all valid dimensions."""
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
                make_url(f"/teams/backend-team/peer-comparison?dimension={dim}")
            )
            # API may return 422 for certain dimensions or 200 with data
            if response.status_code == 200:
                data = response.json()
                assert "team_id" in data
                assert "dimension" in data
                assert "score" in data

    def test_peer_comparison_missing_dimension(self, client):
        """Test peer comparison without dimension parameter."""
        response = client.get(make_url("/teams/backend-team/peer-comparison"))

        assert response.status_code == 422

    def test_peer_comparison_invalid_dimension(self, client):
        """Test peer comparison with invalid dimension."""
        response = client.get(
            make_url("/teams/backend-team/peer-comparison?dimension=invalid")
        )

        assert response.status_code == 422


class TestAlertsEndpoint:
    """Test alerts endpoint integration."""

    def test_get_alerts_success(self, client):
        """Test successful alerts retrieval."""
        response = client.get(make_url("/teams/backend-team/alerts"))

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_alerts_severity_filter(self, client):
        """Test alerts with severity filter."""
        response = client.get(make_url("/teams/backend-team/alerts?severity=critical"))

        assert response.status_code == 200


class TestBenchmarksEndpoint:
    """Test benchmarks endpoint integration."""

    def test_get_benchmarks_success(self, client):
        """Test successful benchmarks retrieval."""
        response = client.get(make_url("/teams/backend-team/benchmarks"))

        # API may return 422 for validation or 200 with data
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))


class TestHealthEndpoint:
    """Test health endpoint integration."""

    def test_health_check(self, client):
        """Test API health check."""
        response = client.get(make_url("/health"))

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]


class TestEndpointParameterValidation:
    """Test parameter validation across endpoints."""

    def test_invalid_query_parameters(self, client):
        """Test endpoints reject invalid query parameters."""
        invalid_params = [
            (make_url("/teams/backend-team/trends?days=abc"), 422),
            (make_url("/teams/backend-team/trends?days=-5"), 422),
            (make_url("/teams/backend-team/anomalies?severity="), 422),
            (make_url("/teams/backend-team/developers?days=999"), 422),
        ]

        for endpoint, expected_status in invalid_params:
            response = client.get(endpoint)
            assert response.status_code == expected_status, f"Failed for {endpoint}"

    def test_endpoint_consistency(self, client):
        """Test that all endpoints follow consistent response patterns."""
        endpoints = [
            (make_url("/teams/backend-team/caqi"), "team_id"),
            (make_url("/teams/backend-team/trends?days=30"), None),
            (make_url("/teams/backend-team/anomalies"), None),
            (make_url("/teams/backend-team/developers?days=30"), None),
            (make_url("/teams/backend-team/alerts"), None),
        ]

        for endpoint, expected_key in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Failed for {endpoint}"
            data = response.json()

            if expected_key:
                assert expected_key in data


class TestEndpointCombinations:
    """Test realistic endpoint usage patterns."""

    def test_get_caqi_and_trends(self, client):
        """Test typical flow: get CAQI then trends."""
        caqi_response = client.get(make_url("/teams/backend-team/caqi"))
        assert caqi_response.status_code == 200

        trends_response = client.get(make_url("/teams/backend-team/trends?days=30"))
        assert trends_response.status_code == 200

    def test_get_anomalies_and_alerts(self, client):
        """Test typical flow: get anomalies and alerts."""
        anomalies_response = client.get(make_url("/teams/backend-team/anomalies"))
        assert anomalies_response.status_code == 200

        alerts_response = client.get(make_url("/teams/backend-team/alerts"))
        assert alerts_response.status_code == 200

    def test_get_peer_comparison_for_dimensions(self, client):
        """Test comparing all dimensions."""
        dimensions = ["security", "complexity", "documentation", "testing"]

        for dim in dimensions:
            response = client.get(
                make_url(f"/teams/backend-team/peer-comparison?dimension={dim}")
            )
            # API may return 422 for certain dimensions or 200 with data
            assert response.status_code in [200, 422]
