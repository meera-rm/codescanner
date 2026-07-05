"""
Billing Service - Phase 5.4
Manages subscriptions, pricing, and invoices
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time


class SubscriptionTier(str, Enum):
    """Subscription tiers"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingCycle(str, Enum):
    """Billing cycle"""
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class PricingPlan:
    """Pricing plan definition"""
    tier: SubscriptionTier
    name: str
    description: str
    monthly_price: float
    yearly_price: float
    requests_per_month: int  # -1 for unlimited
    concurrent_keys: int
    storage_gb: int
    features: List[str] = field(default_factory=list)


@dataclass
class Subscription:
    """Team subscription"""
    team_id: str
    tier: SubscriptionTier
    cycle: BillingCycle
    started_at: float = field(default_factory=time.time)
    renews_at: float = 0.0
    cancelled_at: Optional[float] = None
    payment_method: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.cancelled_at is None

    def days_until_renewal(self) -> float:
        """Days until next renewal"""
        return (self.renews_at - time.time()) / 86400


@dataclass
class Invoice:
    """Billing invoice"""
    invoice_id: str
    team_id: str
    amount: float
    currency: str = "USD"
    period_start: float = field(default_factory=time.time)
    period_end: float = 0.0
    status: str = "draft"  # "draft", "sent", "paid", "overdue"
    created_at: float = field(default_factory=time.time)
    due_at: Optional[float] = None
    paid_at: Optional[float] = None
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        if self.status == "paid":
            return False

        if self.due_at:
            return time.time() > self.due_at

        return False


class BillingService:
    """Manages billing and subscriptions"""

    # Standard pricing plans
    PRICING_PLANS = {
        SubscriptionTier.FREE: PricingPlan(
            tier=SubscriptionTier.FREE,
            name="Free",
            description="Free plan for development",
            monthly_price=0.0,
            yearly_price=0.0,
            requests_per_month=1000,
            concurrent_keys=1,
            storage_gb=1,
            features=["Basic analysis", "Single API key", "Community support"]
        ),
        SubscriptionTier.STARTER: PricingPlan(
            tier=SubscriptionTier.STARTER,
            name="Starter",
            description="For individuals and small teams",
            monthly_price=29.0,
            yearly_price=290.0,
            requests_per_month=50000,
            concurrent_keys=5,
            storage_gb=10,
            features=["Advanced analysis", "Multiple API keys", "Email support"]
        ),
        SubscriptionTier.PRO: PricingPlan(
            tier=SubscriptionTier.PRO,
            name="Pro",
            description="For growing teams",
            monthly_price=99.0,
            yearly_price=990.0,
            requests_per_month=500000,
            concurrent_keys=25,
            storage_gb=100,
            features=["Full suite", "Team management", "Priority support"]
        ),
        SubscriptionTier.ENTERPRISE: PricingPlan(
            tier=SubscriptionTier.ENTERPRISE,
            name="Enterprise",
            description="Custom solution for enterprises",
            monthly_price=0.0,  # Custom pricing
            yearly_price=0.0,
            requests_per_month=-1,  # Unlimited
            concurrent_keys=-1,
            storage_gb=-1,
            features=["Everything", "Custom features", "Dedicated support"]
        ),
    }

    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.invoices: Dict[str, Invoice] = {}

    def get_pricing_plan(self, tier: SubscriptionTier) -> Optional[PricingPlan]:
        """Get pricing plan"""
        return self.PRICING_PLANS.get(tier)

    def create_subscription(
        self,
        team_id: str,
        tier: SubscriptionTier,
        cycle: BillingCycle
    ) -> Subscription:
        """Create subscription"""
        if cycle == BillingCycle.MONTHLY:
            renews_at = time.time() + (30 * 86400)
        else:
            renews_at = time.time() + (365 * 86400)

        subscription = Subscription(
            team_id=team_id,
            tier=tier,
            cycle=cycle,
            renews_at=renews_at
        )

        self.subscriptions[team_id] = subscription
        return subscription

    def get_subscription(self, team_id: str) -> Optional[Subscription]:
        """Get team subscription"""
        return self.subscriptions.get(team_id)

    def upgrade_subscription(
        self,
        team_id: str,
        new_tier: SubscriptionTier
    ) -> Optional[Subscription]:
        """Upgrade subscription"""
        sub = self.get_subscription(team_id)

        if not sub:
            return None

        sub.tier = new_tier
        return sub

    def cancel_subscription(self, team_id: str) -> bool:
        """Cancel subscription"""
        sub = self.get_subscription(team_id)

        if not sub:
            return False

        sub.cancelled_at = time.time()
        return True

    def create_invoice(
        self,
        team_id: str,
        amount: float,
        line_items: Optional[List[Dict[str, Any]]] = None
    ) -> Invoice:
        """Create invoice"""
        import secrets

        invoice_id = f"inv_{secrets.token_hex(8)}"
        due_at = time.time() + (30 * 86400)  # 30 days

        invoice = Invoice(
            invoice_id=invoice_id,
            team_id=team_id,
            amount=amount,
            due_at=due_at,
            line_items=line_items or []
        )

        self.invoices[invoice_id] = invoice
        return invoice

    def list_invoices(self, team_id: str) -> List[Invoice]:
        """List invoices for team"""
        return [i for i in self.invoices.values() if i.team_id == team_id]

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice"""
        return self.invoices.get(invoice_id)

    def mark_invoice_paid(self, invoice_id: str) -> bool:
        """Mark invoice as paid"""
        invoice = self.get_invoice(invoice_id)

        if not invoice:
            return False

        invoice.status = "paid"
        invoice.paid_at = time.time()
        return True

    def calculate_usage_cost(
        self,
        team_id: str,
        usage_stats: Dict[str, Any]
    ) -> float:
        """Calculate cost based on usage"""
        # Free tier - no charge
        sub = self.get_subscription(team_id)
        if not sub or sub.tier == SubscriptionTier.FREE:
            return 0.0

        # Starter/Pro - included requests, then $0.10 per additional 1000
        included = self.get_pricing_plan(sub.tier).requests_per_month

        if included == -1:  # Unlimited
            return 0.0

        overage = max(0, usage_stats.get("total_requests", 0) - included)
        overage_cost = (overage / 1000) * 0.10

        return overage_cost

    def estimate_cost(
        self,
        tier: SubscriptionTier,
        requests: int
    ) -> float:
        """Estimate cost for tier and usage"""
        plan = self.get_pricing_plan(tier)

        if not plan or tier == SubscriptionTier.FREE:
            return 0.0

        if plan.requests_per_month == -1:  # Unlimited
            return plan.monthly_price

        if requests <= plan.requests_per_month:
            return plan.monthly_price

        overage = requests - plan.requests_per_month
        overage_cost = (overage / 1000) * 0.10

        return plan.monthly_price + overage_cost

    def get_team_billing_summary(self, team_id: str) -> Dict[str, Any]:
        """Get billing summary for team"""
        sub = self.get_subscription(team_id)
        plan = self.get_pricing_plan(sub.tier) if sub else None
        invoices = self.list_invoices(team_id)

        total_paid = sum(
            i.amount for i in invoices if i.status == "paid"
        )

        overdue = [i for i in invoices if i.is_overdue()]

        return {
            "team_id": team_id,
            "tier": sub.tier.value if sub else None,
            "monthly_price": plan.monthly_price if plan else 0.0,
            "yearly_price": plan.yearly_price if plan else 0.0,
            "total_paid": total_paid,
            "total_invoices": len(invoices),
            "overdue_invoices": len(overdue),
            "days_until_renewal": sub.days_until_renewal() if sub else None,
        }


# Global billing service
_global_billing_service = BillingService()


def get_billing_service() -> BillingService:
    """Get global billing service"""
    return _global_billing_service
