"""
Tests for Enterprise Features - Phase 5.4
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.api_key_manager import (
    ApiKeyManager, KeyStatus, KeyScope, get_api_key_manager
)
from api.services.usage_tracker import UsageTracker, get_usage_tracker
from api.services.billing_service import (
    BillingService, SubscriptionTier, BillingCycle, get_billing_service
)
from api.services.rate_limiter import RateLimiter, get_rate_limiter
from api.services.audit_logger import (
    AuditLogger, AuditAction, AuditSeverity, get_audit_logger
)


class TestApiKeyManager:
    """Test API key management"""

    def test_generate_key(self):
        """Test key generation"""
        key = ApiKeyManager.generate_key()

        assert key.startswith("sk_")
        assert len(key) > 20

    def test_hash_key(self):
        """Test key hashing"""
        key = "test_key_123"
        hash1 = ApiKeyManager.hash_key(key)
        hash2 = ApiKeyManager.hash_key(key)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex

    def test_create_api_key(self):
        """Test creating API key"""
        manager = ApiKeyManager()

        key, record = manager.create_key(
            team_id="team_1",
            name="Test Key",
            scopes=[KeyScope.READ, KeyScope.WRITE]
        )

        assert key.startswith("sk_")
        assert record.name == "Test Key"
        assert KeyScope.READ in record.scopes

    def test_validate_key(self):
        """Test validating API key"""
        manager = ApiKeyManager()

        key, _ = manager.create_key(
            team_id="team_1",
            name="Test",
            scopes=[KeyScope.READ]
        )

        valid, record = manager.validate_key(key)

        assert valid is True
        assert record.name == "Test"

    def test_validate_invalid_key(self):
        """Test invalid key validation"""
        manager = ApiKeyManager()

        valid, record = manager.validate_key("sk_invalid")

        assert valid is False
        assert record is None

    def test_revoke_key(self):
        """Test revoking key"""
        manager = ApiKeyManager()

        key, record = manager.create_key(
            team_id="team_1",
            name="Test",
            scopes=[KeyScope.READ]
        )

        manager.revoke_key(record.key_id)

        valid, _ = manager.validate_key(key)

        assert valid is False

    def test_check_scope(self):
        """Test checking key scope"""
        manager = ApiKeyManager()

        key, _ = manager.create_key(
            team_id="team_1",
            name="Test",
            scopes=[KeyScope.READ]
        )

        assert manager.check_scope(key, KeyScope.READ) is True
        assert manager.check_scope(key, KeyScope.ADMIN) is False

    def test_admin_scope_override(self):
        """Test admin scope grants all permissions"""
        manager = ApiKeyManager()

        key, _ = manager.create_key(
            team_id="team_1",
            name="Admin",
            scopes=[KeyScope.ADMIN]
        )

        assert manager.check_scope(key, KeyScope.READ) is True
        assert manager.check_scope(key, KeyScope.WRITE) is True
        assert manager.check_scope(key, KeyScope.ADMIN) is True


class TestUsageTracker:
    """Test usage tracking"""

    def test_record_usage(self):
        """Test recording usage"""
        tracker = UsageTracker()

        record = tracker.record_usage(
            team_id="team_1",
            key_id="key_1",
            operation="format",
            duration_ms=100.0
        )

        assert record.team_id == "team_1"
        assert record.operation == "format"
        assert record.status == "success"

    def test_operation_costs(self):
        """Test operation costs"""
        tracker = UsageTracker()

        format_record = tracker.record_usage(
            "team_1", "key_1", "format"
        )
        analyze_record = tracker.record_usage(
            "team_1", "key_1", "analyze"
        )

        assert format_record.cost_units == 1
        assert analyze_record.cost_units == 5

    def test_get_usage_stats(self):
        """Test usage statistics"""
        tracker = UsageTracker()

        tracker.record_usage("team_1", "key_1", "format")
        tracker.record_usage("team_1", "key_1", "format")
        tracker.record_usage("team_1", "key_1", "analyze")

        stats = tracker.get_usage_stats("team_1")

        assert stats.total_requests == 3
        assert stats.total_cost_units == 7  # 1 + 1 + 5
        assert stats.requests_by_operation["format"] == 2

    def test_hourly_usage(self):
        """Test hourly usage tracking"""
        tracker = UsageTracker()

        tracker.record_usage("team_1", "key_1", "format")
        tracker.record_usage("team_1", "key_1", "validate")

        hourly = tracker.get_hourly_usage("team_1")

        assert len(hourly) >= 1


class TestBillingService:
    """Test billing service"""

    def test_get_pricing_plan(self):
        """Test getting pricing plan"""
        service = BillingService()

        plan = service.get_pricing_plan(SubscriptionTier.STARTER)

        assert plan.name == "Starter"
        assert plan.monthly_price == 29.0
        assert plan.requests_per_month == 50000

    def test_create_subscription(self):
        """Test creating subscription"""
        service = BillingService()

        sub = service.create_subscription(
            team_id="team_1",
            tier=SubscriptionTier.STARTER,
            cycle=BillingCycle.MONTHLY
        )

        assert sub.team_id == "team_1"
        assert sub.tier == SubscriptionTier.STARTER
        assert sub.is_active() is True

    def test_upgrade_subscription(self):
        """Test upgrading subscription"""
        service = BillingService()

        service.create_subscription(
            "team_1",
            SubscriptionTier.STARTER,
            BillingCycle.MONTHLY
        )

        service.upgrade_subscription("team_1", SubscriptionTier.PRO)

        sub = service.get_subscription("team_1")

        assert sub.tier == SubscriptionTier.PRO

    def test_cancel_subscription(self):
        """Test cancelling subscription"""
        service = BillingService()

        service.create_subscription(
            "team_1",
            SubscriptionTier.STARTER,
            BillingCycle.MONTHLY
        )

        service.cancel_subscription("team_1")

        sub = service.get_subscription("team_1")

        assert sub.is_active() is False

    def test_create_invoice(self):
        """Test creating invoice"""
        service = BillingService()

        invoice = service.create_invoice("team_1", 99.0)

        assert invoice.team_id == "team_1"
        assert invoice.amount == 99.0
        assert invoice.status == "draft"

    def test_mark_invoice_paid(self):
        """Test marking invoice as paid"""
        service = BillingService()

        invoice = service.create_invoice("team_1", 99.0)

        service.mark_invoice_paid(invoice.invoice_id)

        invoice = service.get_invoice(invoice.invoice_id)

        assert invoice.status == "paid"

    def test_estimate_cost(self):
        """Test cost estimation"""
        service = BillingService()

        # Free tier
        cost = service.estimate_cost(SubscriptionTier.FREE, 1000)
        assert cost == 0.0

        # Starter with no overage
        cost = service.estimate_cost(SubscriptionTier.STARTER, 10000)
        assert cost == 29.0

        # Starter with overage
        cost = service.estimate_cost(SubscriptionTier.STARTER, 60000)
        assert cost > 29.0


class TestRateLimiter:
    """Test rate limiting"""

    def test_tier_limits(self):
        """Test rate limits per tier"""
        limiter = RateLimiter()

        free_limit = limiter.get_tier_limit(SubscriptionTier.FREE)
        starter_limit = limiter.get_tier_limit(SubscriptionTier.STARTER)
        pro_limit = limiter.get_tier_limit(SubscriptionTier.PRO)
        enterprise_limit = limiter.get_tier_limit(SubscriptionTier.ENTERPRISE)

        assert free_limit == 10
        assert starter_limit == 100
        assert pro_limit == 1000
        assert enterprise_limit == -1  # Unlimited

    def test_is_allowed(self):
        """Test rate limit check"""
        limiter = RateLimiter()

        # Create free tier subscription
        billing = limiter.billing
        billing.create_subscription("team_1", SubscriptionTier.FREE, BillingCycle.MONTHLY)

        allowed, info = limiter.is_allowed("key_1", "team_1")

        assert allowed is True
        assert info["limit"] == 10

    def test_rate_limit_exceeded(self):
        """Test exceeding rate limit"""
        limiter = RateLimiter()

        billing = limiter.billing
        billing.create_subscription("team_1", SubscriptionTier.FREE, BillingCycle.MONTHLY)

        # Record 10 requests
        for _ in range(10):
            allowed, info = limiter.is_allowed("key_1", "team_1")
            if allowed:
                limiter.record_request("key_1")

        # 11th request should be denied
        allowed, info = limiter.is_allowed("key_1", "team_1")

        assert allowed is False

    def test_unlimited_tier(self):
        """Test unlimited rate for enterprise"""
        limiter = RateLimiter()

        billing = limiter.billing
        billing.create_subscription("team_1", SubscriptionTier.ENTERPRISE, BillingCycle.YEARLY)

        allowed, info = limiter.is_allowed("key_1", "team_1")

        assert allowed is True
        assert info["limit"] == -1


class TestAuditLogger:
    """Test audit logging"""

    def test_log_action(self):
        """Test logging action"""
        logger = AuditLogger()

        entry = logger.log_action(
            team_id="team_1",
            action=AuditAction.API_KEY_CREATED,
            actor="user_123",
            resource="key_1"
        )

        assert entry.team_id == "team_1"
        assert entry.action == AuditAction.API_KEY_CREATED
        assert entry.resource == "key_1"

    def test_get_entries(self):
        """Test retrieving audit entries"""
        logger = AuditLogger()

        logger.log_action("team_1", AuditAction.API_KEY_CREATED, "user_1")
        logger.log_action("team_1", AuditAction.API_KEY_REVOKED, "user_1")
        logger.log_action("team_2", AuditAction.API_KEY_CREATED, "user_2")

        team1_entries = logger.get_entries("team_1")

        assert len(team1_entries) == 2

    def test_filter_by_action(self):
        """Test filtering entries by action"""
        logger = AuditLogger()

        logger.log_action("team_1", AuditAction.API_KEY_CREATED, "user_1")
        logger.log_action("team_1", AuditAction.API_KEY_REVOKED, "user_1")

        created = logger.get_entries("team_1", action=AuditAction.API_KEY_CREATED)

        assert len(created) == 1

    def test_critical_events(self):
        """Test getting critical events"""
        logger = AuditLogger()

        logger.log_action(
            "team_1",
            AuditAction.SUBSCRIPTION_CANCELLED,
            "user_1",
            severity=AuditSeverity.CRITICAL
        )

        critical = logger.get_critical_events("team_1")

        assert len(critical) == 1

    def test_failed_actions(self):
        """Test getting failed actions"""
        logger = AuditLogger()

        logger.log_action(
            "team_1",
            AuditAction.INVOICE_PAID,
            "system",
            status="failure"
        )

        failed = logger.get_failed_actions("team_1")

        assert len(failed) == 1


class TestEnterpriseIntegration:
    """Integration tests for enterprise features"""

    def test_full_billing_workflow(self):
        """Test complete billing workflow"""
        billing = BillingService()
        usage = UsageTracker()
        audit = AuditLogger()

        # Create subscription
        billing.create_subscription("team_1", SubscriptionTier.STARTER, BillingCycle.MONTHLY)
        audit.log_action("team_1", AuditAction.SUBSCRIPTION_CREATED, "user_1")

        # Record usage
        usage.record_usage("team_1", "key_1", "format")
        usage.record_usage("team_1", "key_1", "analyze")

        # Create invoice
        stats = usage.get_usage_stats("team_1")
        invoice = billing.create_invoice("team_1", stats.total_cost_units * 0.10)

        audit.log_action("team_1", AuditAction.INVOICE_CREATED, "system")

        # Verify
        assert invoice.amount > 0
        assert len(audit.get_entries("team_1")) == 2

    def test_rate_limiting_workflow(self):
        """Test rate limiting in action"""
        api_keys = ApiKeyManager()
        limiter = RateLimiter()

        # Create key
        key, key_record = api_keys.create_key("team_1", "Test", [KeyScope.READ])

        # Create subscription in limiter's billing service
        limiter.billing.create_subscription("team_1", SubscriptionTier.FREE, BillingCycle.MONTHLY)

        # Test that free tier has proper limits
        limits = limiter.get_team_limits("team_1")
        assert limits["requests_per_minute"] == 10

        # Simulate requests up to the limit
        for _ in range(10):
            limiter.record_request(key_record.key_id)

        allowed, info = limiter.is_allowed(key_record.key_id, "team_1")
        # After 10 requests, the next should show remaining = 0
        assert info["remaining"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
