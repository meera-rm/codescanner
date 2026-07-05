"""
Tests for Enterprise Features - Phase 6.4
"""

import pytest
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.enterprise import (
    EnterpriseManager,
    PlanType,
    AuditAction,
)


class TestEnterpriseManager:
    """Test enterprise features"""

    def test_create_api_key(self):
        """Test creating API key"""
        manager = EnterpriseManager()

        raw_key, api_key = manager.create_api_key(
            user_id="user123",
            name="test-key",
            expires_in_days=30,
            permissions=["read", "write"]
        )

        assert raw_key.startswith("codepulse_")
        assert api_key.key_id.startswith("key_")
        assert api_key.user_id == "user123"
        assert api_key.is_active is True

    def test_verify_api_key(self):
        """Test verifying API key"""
        manager = EnterpriseManager()

        raw_key, _ = manager.create_api_key("user123", "test-key")

        result = manager.verify_api_key(raw_key)

        assert result is not None
        user_id, api_key = result
        assert user_id == "user123"

    def test_revoke_api_key(self):
        """Test revoking API key"""
        manager = EnterpriseManager()

        raw_key, api_key = manager.create_api_key("user123", "test-key")

        success = manager.revoke_api_key(api_key.key_id, "user123")

        assert success is True
        assert api_key.is_active is False

    def test_list_api_keys(self):
        """Test listing user API keys"""
        manager = EnterpriseManager()

        manager.create_api_key("user123", "key1")
        manager.create_api_key("user123", "key2")
        manager.create_api_key("user456", "key3")

        keys = manager.list_api_keys("user123")

        assert len(keys) == 2

    def test_create_subscription(self):
        """Test creating subscription"""
        manager = EnterpriseManager()

        subscription = manager.create_subscription("user123", PlanType.PRO)

        assert subscription.user_id == "user123"
        assert subscription.plan_type == PlanType.PRO

    def test_upgrade_plan(self):
        """Test upgrading plan"""
        manager = EnterpriseManager()

        manager.create_subscription("user123", PlanType.FREE)
        success = manager.upgrade_plan("user123", PlanType.PRO)

        assert success is True
        subscription = manager.get_subscription("user123")
        assert subscription.plan_type == PlanType.PRO

    def test_track_api_call(self):
        """Test tracking API call"""
        manager = EnterpriseManager()

        manager.create_subscription("user123", PlanType.PRO)
        success = manager.track_api_call("user123")

        assert success is True
        metrics = manager.get_usage_metrics("user123")
        assert metrics.api_calls == 1

    def test_track_analysis(self):
        """Test tracking analysis"""
        manager = EnterpriseManager()

        manager.create_subscription("user123", PlanType.PRO)
        success = manager.track_analysis("user123", 5, 10, 30)

        assert success is True
        metrics = manager.get_usage_metrics("user123")
        assert metrics.analyses_run == 1
        assert metrics.files_processed == 5

    def test_rate_limiting_free_plan(self):
        """Test rate limiting on free plan"""
        manager = EnterpriseManager()

        manager.create_subscription("user123", PlanType.FREE)

        # FREE: 10 requests per minute
        for i in range(10):
            success = manager.track_api_call("user123")
            assert success is True

        # 11th should fail
        success = manager.track_api_call("user123")
        assert success is False

    def test_get_plan_limits(self):
        """Test getting plan limits"""
        manager = EnterpriseManager()

        manager.create_subscription("user123", PlanType.PRO)
        limits = manager.get_plan_limits("user123")

        assert limits["monthly_analyses"] == 5000
        assert limits["concurrent_requests"] == 5

    def test_audit_logging(self):
        """Test audit logging"""
        manager = EnterpriseManager()

        manager.create_api_key("user123", "test-key")

        logs = manager.get_audit_logs("user123")

        assert len(logs) > 0
        assert logs[0].user_id == "user123"

    def test_multiple_subscriptions(self):
        """Test multiple users with different plans"""
        manager = EnterpriseManager()

        manager.create_subscription("user1", PlanType.FREE)
        manager.create_subscription("user2", PlanType.PRO)
        manager.create_subscription("user3", PlanType.ENTERPRISE)

        limits1 = manager.get_plan_limits("user1")
        limits3 = manager.get_plan_limits("user3")

        assert limits1["concurrent_requests"] < limits3["concurrent_requests"]

    def test_enterprise_unlimited(self):
        """Test enterprise unlimited features"""
        manager = EnterpriseManager()

        manager.create_subscription("user123", PlanType.ENTERPRISE)
        limits = manager.get_plan_limits("user123")

        assert limits["monthly_analyses"] == -1
        assert limits["storage_mb"] == -1

    def test_api_key_serialization(self):
        """Test API key serialization"""
        manager = EnterpriseManager()

        raw_key, api_key = manager.create_api_key("user123", "test-key")
        key_dict = api_key.to_dict()

        assert key_dict["user_id"] == "user123"
        assert key_dict["name"] == "test-key"

    def test_subscription_serialization(self):
        """Test subscription serialization"""
        manager = EnterpriseManager()

        subscription = manager.create_subscription("user123", PlanType.PRO)
        sub_dict = subscription.to_dict()

        assert sub_dict["plan_type"] == "pro"
        assert sub_dict["is_active"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
