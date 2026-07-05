"""
Rate Limiter - Phase 5.4
Rate limiting based on subscription tier
"""

from typing import Dict, Optional, Tuple
from collections import defaultdict
import time

from .billing_service import SubscriptionTier, get_billing_service


class RateLimiter:
    """Rate limiter with tier-based limits"""

    # Rate limits per tier (requests per minute)
    TIER_LIMITS = {
        SubscriptionTier.FREE: 10,
        SubscriptionTier.STARTER: 100,
        SubscriptionTier.PRO: 1000,
        SubscriptionTier.ENTERPRISE: -1,  # Unlimited
    }

    def __init__(self):
        self.request_counts: Dict[str, list] = defaultdict(list)
        self.billing = get_billing_service()

    def get_tier_limit(self, tier: SubscriptionTier) -> int:
        """Get rate limit for tier"""
        return self.TIER_LIMITS.get(tier, 10)

    def is_allowed(self, key_id: str, team_id: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is allowed

        Returns: (allowed, info_dict)
        """
        now = time.time()
        minute_ago = now - 60

        # Get team subscription
        sub = self.billing.get_subscription(team_id)

        if not sub:
            # No subscription - use free limits
            limit = self.get_tier_limit(SubscriptionTier.FREE)
        else:
            limit = self.get_tier_limit(sub.tier)

        # Unlimited
        if limit == -1:
            return True, {
                "allowed": True,
                "remaining": -1,
                "limit": -1,
                "reset_in": 0
            }

        # Clean old requests (older than 1 minute)
        self.request_counts[key_id] = [
            t for t in self.request_counts[key_id]
            if t > minute_ago
        ]

        current_count = len(self.request_counts[key_id])
        remaining = max(0, limit - current_count)

        # Calculate next reset time
        if self.request_counts[key_id]:
            oldest = min(self.request_counts[key_id])
            reset_in = max(0, 60 - (now - oldest))
        else:
            reset_in = 0

        allowed = current_count < limit

        return allowed, {
            "allowed": allowed,
            "current": current_count,
            "limit": limit,
            "remaining": remaining,
            "reset_in": reset_in
        }

    def record_request(self, key_id: str) -> None:
        """Record API request"""
        self.request_counts[key_id].append(time.time())

    def get_stats(self, key_id: str) -> Dict[str, any]:
        """Get rate limit stats for key"""
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.request_counts[key_id] = [
            t for t in self.request_counts[key_id]
            if t > minute_ago
        ]

        current_count = len(self.request_counts[key_id])

        return {
            "key_id": key_id,
            "current_requests": current_count,
            "requests_last_minute": current_count,
            "window_start": minute_ago,
            "window_end": now
        }

    def reset_limits(self, key_id: str) -> None:
        """Reset rate limit counter"""
        self.request_counts[key_id] = []

    def get_team_limits(self, team_id: str) -> Dict[str, any]:
        """Get rate limits for team"""
        sub = self.billing.get_subscription(team_id)

        if not sub:
            tier = SubscriptionTier.FREE
        else:
            tier = sub.tier

        limit = self.get_tier_limit(tier)

        return {
            "team_id": team_id,
            "tier": tier.value,
            "requests_per_minute": limit,
            "requests_per_hour": limit * 60 if limit > 0 else -1,
            "requests_per_day": limit * 1440 if limit > 0 else -1,
        }


# Global rate limiter
_global_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter"""
    return _global_rate_limiter
