"""
Enterprise Features - Phase 6.4
API key management, usage tracking, rate limiting, billing, audit logging
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import secrets
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta


class PlanType(str, Enum):
    """Subscription plans"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class AuditAction(str, Enum):
    """Audit log actions"""
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    API_CALL = "api_call"
    ANALYSIS_RUN = "analysis_run"
    SETTINGS_CHANGED = "settings_changed"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USAGE_LIMIT_EXCEEDED = "usage_limit_exceeded"


@dataclass
class APIKey:
    """API key for authentication"""
    key_id: str
    key_hash: str  # Hashed key for storage
    key_prefix: str  # First 8 chars shown to user
    user_id: str
    name: str
    created_at: float = field(default_factory=time.time)
    last_used: Optional[float] = None
    expires_at: Optional[float] = None
    is_active: bool = True
    permissions: List[str] = field(default_factory=lambda: ["read", "write"])
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self, include_hash: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "key_id": self.key_id,
            "key_prefix": self.key_prefix,
            "name": self.name,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "expires_at": self.expires_at,
            "is_active": self.is_active,
            "permissions": self.permissions,
        }


@dataclass
class UsageMetrics:
    """User usage metrics"""
    user_id: str
    period_start: float
    period_end: float
    api_calls: int = 0
    analyses_run: int = 0
    files_processed: int = 0
    patterns_extracted: int = 0
    storage_mb: float = 0.0
    compute_hours: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "api_calls": self.api_calls,
            "analyses_run": self.analyses_run,
            "files_processed": self.files_processed,
            "patterns_extracted": self.patterns_extracted,
            "storage_mb": self.storage_mb,
            "compute_hours": self.compute_hours,
        }


@dataclass
class Subscription:
    """User subscription"""
    subscription_id: str
    user_id: str
    plan_type: PlanType
    created_at: float = field(default_factory=time.time)
    billing_cycle_start: float = field(default_factory=time.time)
    billing_cycle_end: float = field(default_factory=lambda: time.time() + 30*24*3600)
    is_active: bool = True
    auto_renew: bool = True
    price_monthly: float = 0.0
    currency: str = "USD"
    payment_method: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "subscription_id": self.subscription_id,
            "user_id": self.user_id,
            "plan_type": self.plan_type.value,
            "created_at": self.created_at,
            "billing_cycle_start": self.billing_cycle_start,
            "billing_cycle_end": self.billing_cycle_end,
            "is_active": self.is_active,
            "auto_renew": self.auto_renew,
            "price_monthly": self.price_monthly,
            "currency": self.currency,
        }


@dataclass
class AuditLog:
    """Audit log entry"""
    log_id: str
    user_id: str
    action: AuditAction
    resource_type: str  # "api_key", "analysis", "settings", etc
    resource_id: str
    status: str  # "success", "failure"
    timestamp: float = field(default_factory=time.time)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "status": self.status,
            "timestamp": self.timestamp,
            "ip_address": self.ip_address,
        }


@dataclass
class RateLimit:
    """Rate limit configuration"""
    limit_id: str
    user_id: str
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    concurrent_requests: int = 10
    storage_quota_mb: int = 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "limit_id": self.limit_id,
            "user_id": self.user_id,
            "requests_per_minute": self.requests_per_minute,
            "requests_per_hour": self.requests_per_hour,
            "requests_per_day": self.requests_per_day,
            "concurrent_requests": self.concurrent_requests,
            "storage_quota_mb": self.storage_quota_mb,
        }


class EnterpriseManager:
    """Manages enterprise features"""

    def __init__(self):
        # API Key management
        self.api_keys: Dict[str, APIKey] = {}
        self.key_user_map: Dict[str, str] = {}  # key_hash -> user_id

        # Usage tracking
        self.usage_metrics: Dict[str, UsageMetrics] = {}
        self.user_api_calls: Dict[str, List[float]] = defaultdict(list)  # Track call times

        # Subscriptions and billing
        self.subscriptions: Dict[str, Subscription] = {}
        self.user_subscriptions: Dict[str, str] = {}  # user_id -> subscription_id

        # Rate limiting
        self.rate_limits: Dict[str, RateLimit] = {}
        self.request_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            "minute": 0,
            "hour": 0,
            "day": 0,
            "concurrent": 0
        })
        self.rate_reset_times: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            "minute": time.time() + 60,
            "hour": time.time() + 3600,
            "day": time.time() + 86400
        })

        # Audit logging
        self.audit_logs: Dict[str, AuditLog] = {}
        self.user_logs: Dict[str, List[str]] = defaultdict(list)  # user_id -> log_ids

        # Plan features
        self.plan_limits: Dict[PlanType, Dict[str, int]] = {
            PlanType.FREE: {
                "monthly_analyses": 100,
                "concurrent_requests": 1,
                "storage_mb": 100,
                "api_keys": 1,
                "team_members": 1,
            },
            PlanType.PRO: {
                "monthly_analyses": 5000,
                "concurrent_requests": 5,
                "storage_mb": 5000,
                "api_keys": 10,
                "team_members": 5,
            },
            PlanType.ENTERPRISE: {
                "monthly_analyses": -1,  # Unlimited
                "concurrent_requests": 50,
                "storage_mb": -1,  # Unlimited
                "api_keys": -1,
                "team_members": -1,
            },
        }

    # ============ API Key Management ============

    def create_api_key(
        self,
        user_id: str,
        name: str,
        expires_in_days: Optional[int] = None,
        permissions: Optional[List[str]] = None
    ) -> Tuple[str, APIKey]:
        """Create new API key"""
        # Generate key
        raw_key = f"codepulse_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:8]

        key_id = f"key_{secrets.token_hex(8)}"
        expires_at = None
        if expires_in_days:
            expires_at = time.time() + (expires_in_days * 24 * 3600)

        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            key_prefix=key_prefix,
            user_id=user_id,
            name=name,
            expires_at=expires_at,
            permissions=permissions or ["read", "write"]
        )

        self.api_keys[key_id] = api_key
        self.key_user_map[key_hash] = user_id

        # Audit log
        self._audit_log(user_id, AuditAction.API_KEY_CREATED, "api_key", key_id, "success")

        return raw_key, api_key

    def verify_api_key(self, key: str) -> Optional[Tuple[str, APIKey]]:
        """Verify API key and return user_id"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        user_id = self.key_user_map.get(key_hash)

        if not user_id:
            return None

        # Find key
        for key_id, api_key in self.api_keys.items():
            if api_key.key_hash == key_hash and api_key.is_active:
                # Check expiration
                if api_key.expires_at and time.time() > api_key.expires_at:
                    return None

                # Update last used
                api_key.last_used = time.time()
                return user_id, api_key

        return None

    def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """Revoke API key"""
        api_key = self.api_keys.get(key_id)
        if not api_key or api_key.user_id != user_id:
            return False

        api_key.is_active = False
        self._audit_log(user_id, AuditAction.API_KEY_REVOKED, "api_key", key_id, "success")
        return True

    def list_api_keys(self, user_id: str) -> List[APIKey]:
        """List user's API keys"""
        return [k for k in self.api_keys.values() if k.user_id == user_id]

    # ============ Usage Tracking ============

    def track_api_call(self, user_id: str) -> bool:
        """Track API call for user"""
        # Check rate limits first
        if not self._check_rate_limit(user_id):
            self._audit_log(user_id, AuditAction.USAGE_LIMIT_EXCEEDED, "api_call", user_id, "failure")
            return False

        # Record call time
        self.user_api_calls[user_id].append(time.time())

        # Update counters
        self._update_request_counts(user_id)

        # Update monthly metrics
        metrics = self._get_current_metrics(user_id)
        if metrics:
            metrics.api_calls += 1

        self._audit_log(user_id, AuditAction.API_CALL, "api_call", user_id, "success")
        return True

    def track_analysis(
        self,
        user_id: str,
        files_count: int,
        patterns_count: int,
        compute_seconds: float
    ) -> bool:
        """Track analysis run"""
        metrics = self._get_current_metrics(user_id)
        if not metrics:
            return False

        metrics.analyses_run += 1
        metrics.files_processed += files_count
        metrics.patterns_extracted += patterns_count
        metrics.compute_hours += compute_seconds / 3600

        self._audit_log(user_id, AuditAction.ANALYSIS_RUN, "analysis", user_id, "success",
                       details={
                           "files": files_count,
                           "patterns": patterns_count,
                           "compute_seconds": compute_seconds
                       })
        return True

    def get_usage_metrics(self, user_id: str) -> Optional[UsageMetrics]:
        """Get current usage metrics"""
        return self._get_current_metrics(user_id)

    # ============ Subscription Management ============

    def create_subscription(
        self,
        user_id: str,
        plan_type: PlanType,
        billing_cycle_days: int = 30
    ) -> Subscription:
        """Create subscription for user"""
        sub_id = f"sub_{secrets.token_hex(8)}"
        now = time.time()

        subscription = Subscription(
            subscription_id=sub_id,
            user_id=user_id,
            plan_type=plan_type,
            billing_cycle_start=now,
            billing_cycle_end=now + (billing_cycle_days * 24 * 3600),
            price_monthly=self._get_plan_price(plan_type),
        )

        self.subscriptions[sub_id] = subscription
        self.user_subscriptions[user_id] = sub_id

        # Create rate limit
        self._create_rate_limit(user_id, plan_type)

        self._audit_log(user_id, AuditAction.SETTINGS_CHANGED, "subscription", sub_id, "success")
        return subscription

    def get_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user subscription"""
        sub_id = self.user_subscriptions.get(user_id)
        if not sub_id:
            return None
        return self.subscriptions.get(sub_id)

    def upgrade_plan(self, user_id: str, new_plan: PlanType) -> bool:
        """Upgrade user plan"""
        subscription = self.get_subscription(user_id)
        if not subscription:
            return False

        subscription.plan_type = new_plan
        subscription.price_monthly = self._get_plan_price(new_plan)

        # Update rate limits
        self._create_rate_limit(user_id, new_plan)

        self._audit_log(user_id, AuditAction.SETTINGS_CHANGED, "subscription", subscription.subscription_id, "success")
        return True

    def get_plan_limits(self, user_id: str) -> Dict[str, int]:
        """Get plan limits for user"""
        subscription = self.get_subscription(user_id)
        if not subscription:
            return self.plan_limits[PlanType.FREE]

        return self.plan_limits[subscription.plan_type]

    # ============ Rate Limiting ============

    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limits"""
        limit = self.rate_limits.get(user_id)
        if not limit:
            return True

        counts = self.request_counts[user_id]
        resets = self.rate_reset_times[user_id]
        now = time.time()

        # Reset counters if window expired
        if now > resets["minute"]:
            counts["minute"] = 0
            resets["minute"] = now + 60

        if now > resets["hour"]:
            counts["hour"] = 0
            resets["hour"] = now + 3600

        if now > resets["day"]:
            counts["day"] = 0
            resets["day"] = now + 86400

        # Check limits
        if limit.requests_per_minute > 0 and counts["minute"] >= limit.requests_per_minute:
            return False
        if limit.requests_per_hour > 0 and counts["hour"] >= limit.requests_per_hour:
            return False
        if limit.requests_per_day > 0 and counts["day"] >= limit.requests_per_day:
            return False

        return True

    def _update_request_counts(self, user_id: str) -> None:
        """Update request counters"""
        counts = self.request_counts[user_id]
        counts["minute"] += 1
        counts["hour"] += 1
        counts["day"] += 1

    def get_rate_limit(self, user_id: str) -> Optional[RateLimit]:
        """Get rate limit for user"""
        return self.rate_limits.get(user_id)

    # ============ Audit Logging ============

    def _audit_log(
        self,
        user_id: str,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        status: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Create audit log entry"""
        log_id = f"log_{secrets.token_hex(8)}"
        log = AuditLog(
            log_id=log_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )

        self.audit_logs[log_id] = log
        self.user_logs[user_id].append(log_id)

        return log

    def get_audit_logs(
        self,
        user_id: str,
        limit: int = 100,
        action_filter: Optional[AuditAction] = None
    ) -> List[AuditLog]:
        """Get audit logs for user"""
        log_ids = self.user_logs[user_id]
        logs = [self.audit_logs[log_id] for log_id in log_ids if log_id in self.audit_logs]

        if action_filter:
            logs = [l for l in logs if l.action == action_filter]

        return sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]

    # ============ Helper Methods ============

    def _get_current_metrics(self, user_id: str) -> Optional[UsageMetrics]:
        """Get or create current month metrics"""
        now = time.time()
        subscription = self.get_subscription(user_id)

        if not subscription:
            return None

        billing_start = subscription.billing_cycle_start
        billing_end = subscription.billing_cycle_end

        key = f"{user_id}_{int(billing_start)}"
        if key not in self.usage_metrics:
            self.usage_metrics[key] = UsageMetrics(
                user_id=user_id,
                period_start=billing_start,
                period_end=billing_end
            )

        return self.usage_metrics[key]

    def _get_plan_price(self, plan_type: PlanType) -> float:
        """Get monthly price for plan"""
        prices = {
            PlanType.FREE: 0.0,
            PlanType.PRO: 99.0,
            PlanType.ENTERPRISE: 999.0,
        }
        return prices.get(plan_type, 0.0)

    def _create_rate_limit(self, user_id: str, plan_type: PlanType) -> None:
        """Create rate limit for user based on plan"""
        limits = {
            PlanType.FREE: RateLimit(
                limit_id=f"limit_{user_id}",
                user_id=user_id,
                requests_per_minute=10,
                requests_per_hour=100,
                requests_per_day=1000,
                concurrent_requests=1,
                storage_quota_mb=100
            ),
            PlanType.PRO: RateLimit(
                limit_id=f"limit_{user_id}",
                user_id=user_id,
                requests_per_minute=60,
                requests_per_hour=1000,
                requests_per_day=10000,
                concurrent_requests=5,
                storage_quota_mb=5000
            ),
            PlanType.ENTERPRISE: RateLimit(
                limit_id=f"limit_{user_id}",
                user_id=user_id,
                requests_per_minute=600,
                requests_per_hour=10000,
                requests_per_day=100000,
                concurrent_requests=50,
                storage_quota_mb=100000
            ),
        }

        self.rate_limits[user_id] = limits.get(plan_type, limits[PlanType.FREE])


# Global instance
_global_enterprise = EnterpriseManager()


def get_enterprise_manager() -> EnterpriseManager:
    """Get global enterprise manager"""
    return _global_enterprise
