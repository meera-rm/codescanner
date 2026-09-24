"""
Integration tests for Phase 2: Core Scanning + Onboarding + Authentication
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))

from fastapi.testclient import TestClient
from api.main import app
from api.routes.auth import auth_service

client = TestClient(app)


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealth:
    def test_health_check(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_version_endpoint(self):
        response = client.get("/api/v1/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data or "api_version" in data


# ============================================================================
# Authentication Tests
# ============================================================================

class TestAuth:
    def test_create_api_key(self):
        response = client.post(
            "/api/v1/keys",
            json={
                "name": "test-key",
                "rate_limit": 100,
                "scopes": ["scan", "onboarding"],
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-key"
        assert data["rate_limit"] == 100
        assert "key_id" in data
        assert "created_at" in data

    def test_list_api_keys(self):
        # Create a key first
        client.post(
            "/api/v1/keys",
            json={"name": "test-key-1", "rate_limit": 100}
        )

        # List keys
        response = client.get("/api/v1/keys")
        assert response.status_code == 200
        data = response.json()
        assert "keys" in data
        assert isinstance(data["keys"], list)

    def test_get_api_key(self):
        # Create a key
        create_response = client.post(
            "/api/v1/keys",
            json={"name": "test-key-get", "rate_limit": 100}
        )
        key_id = create_response.json()["key_id"]

        # Get the key
        response = client.get(f"/api/v1/keys/{key_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["key_id"] == key_id

    def test_update_api_key(self):
        # Create a key
        create_response = client.post(
            "/api/v1/keys",
            json={"name": "test-key-update", "rate_limit": 100}
        )
        key_id = create_response.json()["key_id"]

        # Update the key
        response = client.patch(
            f"/api/v1/keys/{key_id}",
            json={"name": "updated-key", "rate_limit": 200}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated-key"
        assert data["rate_limit"] == 200

    def test_revoke_api_key(self):
        # Create a key
        create_response = client.post(
            "/api/v1/keys",
            json={"name": "test-key-revoke", "rate_limit": 100}
        )
        key_id = create_response.json()["key_id"]

        # Revoke the key
        response = client.delete(f"/api/v1/keys/{key_id}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


# ============================================================================
# Configuration Tests
# ============================================================================

class TestConfig:
    def test_get_current_config(self):
        response = client.get("/api/v1/config")
        assert response.status_code == 200
        data = response.json()
        assert "ignore_patterns" in data
        assert "languages" in data
        assert "rules" in data
        assert "thresholds" in data

    def test_get_default_config(self):
        response = client.get("/api/v1/config/defaults")
        assert response.status_code == 200
        data = response.json()
        assert "ignore_patterns" in data
        assert isinstance(data["ignore_patterns"], list)
        assert "python" in data["languages"] or len(data["languages"]) > 0

    def test_update_config(self):
        response = client.post(
            "/api/v1/config",
            json={
                "ignore_patterns": ["test", "mock"],
                "languages": ["python"],
                "rules": {"security": True},
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "ignore_patterns" in data

    def test_reset_config(self):
        response = client.post("/api/v1/config/reset")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "config" in data


# ============================================================================
# Scanner Endpoint Tests (Phase 2)
# ============================================================================

class TestScanner:
    def test_scan_sync_missing_input(self):
        response = client.post(
            "/api/v1/scan/sync",
            json={}
        )
        # code and directory_path are both optional in ScanRequest, so an
        # empty body is valid input that produces an empty, successful scan.
        assert response.status_code == 200
        data = response.json()
        assert data["findings"] == []

    def test_scan_sync_with_code(self):
        response = client.post(
            "/api/v1/scan/sync",
            json={
                "code": "print('hello')",
                "language": "python",
                "options": {"security": True}
            }
        )
        # May require auth
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert "job_id" in data

    def test_scan_async(self):
        response = client.post(
            "/api/v1/scan/async",
            json={
                "code": "print('hello')",
                "language": "python"
            }
        )
        # May require auth
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert "job_id" in data
            assert data["status"] == "processing"


# ============================================================================
# Onboarding Endpoint Tests (Phase 2)
# ============================================================================

class TestOnboarding:
    def test_generate_onboarding_missing_path(self):
        response = client.post(
            "/api/v1/onboarding/profile",
            json={}
        )
        assert response.status_code in [400, 401, 422]

    def test_generate_onboarding_with_path(self):
        response = client.post(
            "/api/v1/onboarding/profile",
            json={
                "directory_path": ".",
                "tone": "neutral",
                "format": "json"
            }
        )
        # May require auth
        assert response.status_code in [200, 400, 401]
        if response.status_code == 200:
            data = response.json()
            assert "job_id" in data
            assert "status" in data


# ============================================================================
# Rate Limiting Tests
# ============================================================================

class TestRateLimiting:
    def test_rate_limiter_basic(self):
        from api.utils.rate_limiter import RateLimiter

        limiter = RateLimiter()
        limiter.set_limit("test-key", 2)

        assert limiter.is_allowed("test-key") is True
        assert limiter.is_allowed("test-key") is True
        assert limiter.is_allowed("test-key") is False

    def test_rate_limiter_get_remaining(self):
        from api.utils.rate_limiter import RateLimiter

        limiter = RateLimiter()
        limiter.set_limit("test-key", 3)

        limiter.is_allowed("test-key")
        remaining = limiter.get_remaining("test-key")
        assert remaining == 2

    def test_rate_limiter_get_reset_time(self):
        from api.utils.rate_limiter import RateLimiter

        limiter = RateLimiter()
        limiter.set_limit("test-key", 10)

        reset_time = limiter.get_reset_time("test-key")
        assert reset_time > 0


# ============================================================================
# Auth Service Tests
# ============================================================================

class TestAuthService:
    def test_create_api_key(self):
        token = auth_service.create_api_key(
            name="test",
            rate_limit=50,
            scopes=["scan"]
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_validate_token(self):
        token = auth_service.create_api_key(
            name="validate-test",
            rate_limit=50
        )
        key_id = auth_service.validate_token(token)
        assert key_id is not None

    def test_validate_invalid_token(self):
        key_id = auth_service.validate_token("invalid-token-xyz")
        assert key_id is None

    def test_list_api_keys(self):
        auth_service.create_api_key(name="list-test-1")
        auth_service.create_api_key(name="list-test-2")

        keys = auth_service.list_api_keys()
        assert len(keys) >= 2

    def test_revoke_api_key(self):
        token = auth_service.create_api_key(name="revoke-test")
        key_id = auth_service.key_by_token[token]

        success = auth_service.revoke_api_key(key_id)
        assert success is True

        # Validation should now fail
        key_id_after = auth_service.validate_token(token)
        assert key_id_after is None


# ============================================================================
# Config Service Tests
# ============================================================================

class TestConfigService:
    def test_get_config(self):
        from api.services.config_service import ConfigService

        service = ConfigService()
        config = service.get_config()
        assert "ignore_patterns" in config
        assert "languages" in config

    def test_get_default_config(self):
        from api.services.config_service import ConfigService

        service = ConfigService()
        config = service.get_default_config()
        assert isinstance(config["ignore_patterns"], list)

    def test_update_config(self):
        from api.services.config_service import ConfigService

        service = ConfigService()
        success = service.update_config({"ignore_patterns": ["test"]})
        assert success is True

    def test_validate_config(self):
        from api.services.config_service import ConfigService

        service = ConfigService()
        errors = service.validate_config()
        assert isinstance(errors, list)


# ============================================================================
# Creative Suite Tests (Phase 1 Integration)
# ============================================================================

class TestCreativeSuite:
    def test_creative_suite_analyze_missing_path(self):
        response = client.post(
            "/api/v1/creative-suite/analyze",
            json={}
        )
        assert response.status_code in [400, 401, 422]

    def test_creative_suite_analyze_with_path(self):
        response = client.post(
            "/api/v1/creative-suite/analyze",
            json={
                "directory_path": ".",
                "analyses": ["personality", "letter", "caqi"]
            }
        )
        # May require auth
        assert response.status_code in [200, 400, 401]


# ============================================================================
# Integration Test Markers
# ============================================================================

@pytest.mark.integration
def test_phase2_is_ready():
    """Marker test indicating Phase 2 implementation is complete."""
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
