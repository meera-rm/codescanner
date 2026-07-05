"""
Alert Rules - Phase 5.2
Alert rules and conditions for monitoring
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertConditionOperator(str, Enum):
    """Alert condition operators"""
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    IN = "in"


@dataclass
class AlertCondition:
    """Alert condition"""
    metric_name: str
    operator: AlertConditionOperator
    threshold: float
    duration_seconds: int = 60


@dataclass
class AlertRule:
    """Alert rule"""
    name: str
    description: str
    severity: AlertSeverity
    conditions: List[AlertCondition] = field(default_factory=list)
    enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)
    cooldown_seconds: int = 300  # Prevent alert spam

    def evaluate(self, metrics: Dict[str, float]) -> bool:
        """Evaluate all conditions"""
        if not self.enabled:
            return False

        for condition in self.conditions:
            if not self._evaluate_condition(condition, metrics):
                return False

        return True

    @staticmethod
    def _evaluate_condition(condition: AlertCondition, metrics: Dict[str, float]) -> bool:
        """Evaluate single condition"""
        if condition.metric_name not in metrics:
            return False

        value = metrics[condition.metric_name]

        if condition.operator == AlertConditionOperator.GREATER_THAN:
            return value > condition.threshold
        elif condition.operator == AlertConditionOperator.LESS_THAN:
            return value < condition.threshold
        elif condition.operator == AlertConditionOperator.GREATER_EQUAL:
            return value >= condition.threshold
        elif condition.operator == AlertConditionOperator.LESS_EQUAL:
            return value <= condition.threshold
        elif condition.operator == AlertConditionOperator.EQUAL:
            return value == condition.threshold
        elif condition.operator == AlertConditionOperator.NOT_EQUAL:
            return value != condition.threshold
        else:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "conditions": [
                {
                    "metric_name": c.metric_name,
                    "operator": c.operator.value,
                    "threshold": c.threshold,
                    "duration_seconds": c.duration_seconds
                }
                for c in self.conditions
            ],
            "enabled": self.enabled,
            "notification_channels": self.notification_channels,
            "cooldown_seconds": self.cooldown_seconds
        }


@dataclass
class Alert:
    """Fired alert"""
    rule: AlertRule
    timestamp: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    metric_values: Dict[str, float] = field(default_factory=dict)
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_name": self.rule.name,
            "severity": self.rule.severity.value,
            "timestamp": self.timestamp,
            "metric_values": self.metric_values,
            "message": self.message
        }


class AlertRuleManager:
    """Manages alert rules"""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.fired_alerts: List[Alert] = []
        self.last_alert_time: Dict[str, float] = {}

    def add_rule(self, rule: AlertRule) -> None:
        """Add alert rule"""
        self.rules[rule.name] = rule

    def remove_rule(self, rule_name: str) -> None:
        """Remove alert rule"""
        if rule_name in self.rules:
            del self.rules[rule_name]

    def get_rule(self, rule_name: str) -> Optional[AlertRule]:
        """Get rule by name"""
        return self.rules.get(rule_name)

    def list_rules(self, severity: Optional[AlertSeverity] = None) -> List[AlertRule]:
        """List all rules"""
        rules = list(self.rules.values())

        if severity:
            rules = [r for r in rules if r.severity == severity]

        return rules

    def evaluate_rules(self, metrics: Dict[str, float]) -> List[Alert]:
        """Evaluate all rules against metrics"""
        alerts = []

        for rule in self.rules.values():
            if rule.evaluate(metrics):
                # Check cooldown
                now = datetime.utcnow().timestamp()
                last_alert = self.last_alert_time.get(rule.name, 0)

                if now - last_alert >= rule.cooldown_seconds:
                    alert = Alert(
                        rule=rule,
                        metric_values=metrics,
                        message=f"Alert: {rule.description}"
                    )
                    alerts.append(alert)
                    self.fired_alerts.append(alert)
                    self.last_alert_time[rule.name] = now

        return alerts

    def get_active_alerts(self) -> List[Alert]:
        """Get recent alerts"""
        return self.fired_alerts[-100:]  # Last 100

    def clear_alerts(self) -> None:
        """Clear alert history"""
        self.fired_alerts.clear()
        self.last_alert_time.clear()

    def export_rules(self) -> str:
        """Export rules as JSON"""
        return json.dumps(
            [r.to_dict() for r in self.rules.values()],
            indent=2
        )


class StandardAlerts:
    """Standard alert rules"""

    @staticmethod
    def setup(manager: AlertRuleManager) -> None:
        """Setup standard alerts"""
        # API latency alert
        manager.add_rule(AlertRule(
            name="api_latency_high",
            description="API latency exceeds 2 seconds",
            severity=AlertSeverity.WARNING,
            conditions=[
                AlertCondition(
                    metric_name="codepulse_api_latency_seconds",
                    operator=AlertConditionOperator.GREATER_THAN,
                    threshold=2.0,
                    duration_seconds=60
                )
            ],
            notification_channels=["email", "slack"]
        ))

        # Error rate alert
        manager.add_rule(AlertRule(
            name="error_rate_high",
            description="Error rate exceeds 5%",
            severity=AlertSeverity.CRITICAL,
            conditions=[
                AlertCondition(
                    metric_name="codepulse_error_rate_percent",
                    operator=AlertConditionOperator.GREATER_THAN,
                    threshold=5.0,
                    duration_seconds=300
                )
            ],
            notification_channels=["email", "slack", "pagerduty"]
        ))

        # Memory alert
        manager.add_rule(AlertRule(
            name="memory_usage_high",
            description="Memory usage exceeds 80%",
            severity=AlertSeverity.WARNING,
            conditions=[
                AlertCondition(
                    metric_name="codepulse_memory_usage_percent",
                    operator=AlertConditionOperator.GREATER_THAN,
                    threshold=80.0,
                    duration_seconds=120
                )
            ],
            notification_channels=["email", "slack"]
        ))

        # Queue depth alert
        manager.add_rule(AlertRule(
            name="queue_depth_high",
            description="Task queue depth exceeds 100",
            severity=AlertSeverity.WARNING,
            conditions=[
                AlertCondition(
                    metric_name="codepulse_queue_depth",
                    operator=AlertConditionOperator.GREATER_THAN,
                    threshold=100.0,
                    duration_seconds=60
                )
            ],
            notification_channels=["email", "slack"]
        ))

        # Agent failure alert
        manager.add_rule(AlertRule(
            name="agent_failure_rate_high",
            description="Agent failure rate exceeds 10%",
            severity=AlertSeverity.CRITICAL,
            conditions=[
                AlertCondition(
                    metric_name="codepulse_agent_failure_rate_percent",
                    operator=AlertConditionOperator.GREATER_THAN,
                    threshold=10.0,
                    duration_seconds=300
                )
            ],
            notification_channels=["email", "slack", "pagerduty"]
        ))


# Global alert manager
_global_alert_manager = AlertRuleManager()
StandardAlerts.setup(_global_alert_manager)


def get_alert_manager() -> AlertRuleManager:
    """Get global alert manager"""
    return _global_alert_manager
