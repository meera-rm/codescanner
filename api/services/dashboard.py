"""
Dashboard & Analytics - Phase 7
Unified dashboard data aggregation for all CodePulse features
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import time
from datetime import datetime, timedelta

from .codebase_learner import get_codebase_intelligence
from .agent_finetuner import get_agent_finetuner
from .predictive_analyzer import get_predictive_analyzer
from .continuous_learner import get_continuous_learner
from .github_integration import get_github_integration
from .enterprise import get_enterprise_manager
from .monitoring import get_monitoring_manager
from .ide_plugins import get_ide_plugin_manager


@dataclass
class DashboardSummary:
    """High-level dashboard summary"""
    timestamp: float = field(default_factory=time.time)
    
    # AI Insights
    total_patterns: int = 0
    avg_pattern_complexity: float = 0.0
    improvements_recommended: int = 0
    
    # Enterprise
    subscription_plan: str = "free"
    api_keys_active: int = 0
    usage_percentage: float = 0.0
    
    # Monitoring
    system_health: float = 99.9
    error_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    active_alerts: int = 0
    
    # Activity
    recent_analyses: int = 0
    github_prs_scanned: int = 0
    ide_plugins_active: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "ai_insights": {
                "total_patterns": self.total_patterns,
                "avg_complexity": self.avg_pattern_complexity,
                "improvements_recommended": self.improvements_recommended,
            },
            "enterprise": {
                "plan": self.subscription_plan,
                "active_api_keys": self.api_keys_active,
                "usage_percentage": self.usage_percentage,
            },
            "monitoring": {
                "health": self.system_health,
                "error_rate": self.error_rate,
                "response_time_ms": self.avg_response_time_ms,
                "active_alerts": self.active_alerts,
            },
            "activity": {
                "recent_analyses": self.recent_analyses,
                "github_prs": self.github_prs_scanned,
                "ide_plugins": self.ide_plugins_active,
            }
        }


@dataclass
class DashboardWidget:
    """Individual dashboard widget/component"""
    widget_id: str
    name: str
    widget_type: str  # "metric", "chart", "list", "alert", "status"
    data: Dict[str, Any]
    config: Dict[str, Any] = field(default_factory=dict)
    refresh_interval_seconds: int = 60

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "widget_id": self.widget_id,
            "name": self.name,
            "type": self.widget_type,
            "data": self.data,
            "config": self.config,
            "refresh_interval": self.refresh_interval_seconds,
        }


class DashboardManager:
    """Manages unified dashboard and analytics"""

    def __init__(self):
        self.intelligence = get_codebase_intelligence()
        self.finetuner = get_agent_finetuner()
        self.analyzer = get_predictive_analyzer()
        self.learner = get_continuous_learner()
        self.github = get_github_integration()
        self.enterprise = get_enterprise_manager()
        self.monitoring = get_monitoring_manager()
        self.ide = get_ide_plugin_manager()

        # Dashboard cache
        self.summary_cache: Optional[DashboardSummary] = None
        self.summary_cache_time: float = 0
        self.cache_ttl: int = 30  # Seconds

        # Widget definitions
        self.widgets: Dict[str, DashboardWidget] = {}
        self._build_default_widgets()

    def _build_default_widgets(self) -> None:
        """Build default dashboard widgets"""
        import secrets

        # AI Insights Widget
        self.widgets["ai_insights"] = DashboardWidget(
            widget_id=f"widget_{secrets.token_hex(6)}",
            name="AI Learning Insights",
            widget_type="metric",
            data={
                "total_patterns": 0,
                "avg_complexity": 0.0,
                "improvement_potential": 0.0,
                "top_agents": []
            },
            config={"cols": 3, "rows": 2}
        )

        # System Health Widget
        self.widgets["system_health"] = DashboardWidget(
            widget_id=f"widget_{secrets.token_hex(6)}",
            name="System Health",
            widget_type="status",
            data={
                "availability": 99.9,
                "error_rate": 0.0,
                "response_time": 0.0,
                "status": "healthy"
            },
            config={"cols": 2, "rows": 2}
        )

        # Activity Widget
        self.widgets["activity"] = DashboardWidget(
            widget_id=f"widget_{secrets.token_hex(6)}",
            name="Recent Activity",
            widget_type="list",
            data={
                "analyses_today": 0,
                "github_events": 0,
                "api_calls": 0,
                "errors": 0
            },
            config={"cols": 3, "rows": 2}
        )

        # Alerts Widget
        self.widgets["alerts"] = DashboardWidget(
            widget_id=f"widget_{secrets.token_hex(6)}",
            name="Active Alerts",
            widget_type="alert",
            data={"alerts": []},
            config={"cols": 2, "rows": 3}
        )

        # Usage Widget
        self.widgets["usage"] = DashboardWidget(
            widget_id=f"widget_{secrets.token_hex(6)}",
            name="Plan Usage",
            widget_type="metric",
            data={
                "api_calls": 0,
                "analyses": 0,
                "storage_mb": 0,
                "limits": {}
            },
            config={"cols": 3, "rows": 2}
        )

    def get_dashboard_summary(self, user_id: str) -> DashboardSummary:
        """Get dashboard summary (cached)"""
        # Check cache
        if self.summary_cache and (time.time() - self.summary_cache_time) < self.cache_ttl:
            return self.summary_cache

        summary = DashboardSummary()

        # AI Insights
        patterns = list(self.intelligence.patterns.values())
        if patterns:
            summary.total_patterns = len(patterns)
            summary.avg_pattern_complexity = sum(p.complexity for p in patterns) / len(patterns)

        # Count improvement recommendations
        recommendations_count = 0
        for pattern in patterns:
            prediction = self.analyzer.predict_quality_improvement(pattern.pattern_id, pattern.language)
            if prediction and prediction.improvement_potential > 0.1:
                recommendations_count += 1
        summary.improvements_recommended = recommendations_count

        # Enterprise
        subscription = self.enterprise.get_subscription(user_id)
        if subscription:
            summary.subscription_plan = subscription.plan_type.value
            api_keys = self.enterprise.list_api_keys(user_id)
            summary.api_keys_active = len([k for k in api_keys if k.is_active])
            
            metrics = self.enterprise.get_usage_metrics(user_id)
            limits = self.enterprise.get_plan_limits(user_id)
            if metrics and limits["monthly_analyses"] > 0:
                summary.usage_percentage = (metrics.analyses_run / limits["monthly_analyses"]) * 100

        # Monitoring
        health = self.monitoring.get_system_health()
        if health:
            summary.system_health = health.api_availability
            summary.error_rate = health.error_rate
            summary.avg_response_time_ms = health.avg_response_time_ms

        active_alerts = self.monitoring.get_active_alerts()
        summary.active_alerts = len(active_alerts)

        # Activity
        summary.recent_analyses = self.learner.total_experiences
        summary.ide_plugins_active = len([s for s in self.ide.sessions.values() if s.is_active])

        # Cache
        self.summary_cache = summary
        self.summary_cache_time = time.time()

        return summary

    def get_ai_insights_widget(self) -> DashboardWidget:
        """Get AI insights widget data"""
        widget = self.widgets["ai_insights"]

        patterns = list(self.intelligence.patterns.values())
        if patterns:
            widget.data["total_patterns"] = len(patterns)
            widget.data["avg_complexity"] = sum(p.complexity for p in patterns) / len(patterns)

        # Top agents
        top_agents = []
        for agent_name, profile in self.finetuner.agent_profiles.items():
            top_agents.append({
                "name": agent_name,
                "accuracy": profile.recommendation_accuracy,
                "iterations": profile.learning_iterations
            })
        widget.data["top_agents"] = sorted(top_agents, key=lambda x: x["accuracy"], reverse=True)[:3]

        return widget

    def get_system_health_widget(self) -> DashboardWidget:
        """Get system health widget data"""
        widget = self.widgets["system_health"]

        health = self.monitoring.get_system_health()
        if health:
            widget.data["availability"] = health.api_availability
            widget.data["error_rate"] = health.error_rate
            widget.data["response_time"] = health.avg_response_time_ms
            widget.data["status"] = "healthy" if health.api_availability >= 99.0 else "degraded"

        return widget

    def get_alerts_widget(self) -> DashboardWidget:
        """Get alerts widget data"""
        widget = self.widgets["alerts"]

        alerts = self.monitoring.get_active_alerts()
        widget.data["alerts"] = [
            {
                "alert_id": a.alert_id,
                "level": a.level.value,
                "title": a.title,
                "timestamp": a.timestamp
            }
            for a in alerts[:5]
        ]

        return widget

    def get_activity_widget(self) -> DashboardWidget:
        """Get activity widget data"""
        widget = self.widgets["activity"]

        widget.data["analyses_today"] = self.learner.total_experiences
        widget.data["api_calls"] = self.monitoring.request_counts.get("total", 0)
        widget.data["errors"] = sum(self.monitoring.error_counts.values())

        return widget

    def get_usage_widget(self, user_id: str) -> DashboardWidget:
        """Get usage widget data"""
        widget = self.widgets["usage"]

        metrics = self.enterprise.get_usage_metrics(user_id)
        limits = self.enterprise.get_plan_limits(user_id)

        if metrics:
            widget.data["api_calls"] = metrics.api_calls
            widget.data["analyses"] = metrics.analyses_run
            widget.data["storage_mb"] = metrics.storage_mb
            widget.data["limits"] = limits

        return widget

    def get_all_widgets(self, user_id: str) -> List[DashboardWidget]:
        """Get all dashboard widgets"""
        all_widgets = [
            self.get_ai_insights_widget(),
            self.get_system_health_widget(),
            self.get_activity_widget(),
            self.get_alerts_widget(),
            self.get_usage_widget(user_id)
        ]

        return all_widgets

    def get_analytics_report(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get detailed analytics report"""
        cutoff_time = time.time() - (days * 24 * 3600)

        # Monitoring analytics
        monitoring_data = self.monitoring.get_analytics()

        # Performance report
        perf_report = self.monitoring.get_performance_report()

        # Learning metrics
        learning_metrics = self.learner.get_learning_metrics()

        # Error summary
        error_summary = self.monitoring.get_error_summary()

        # Audit logs
        audit_logs = self.enterprise.get_audit_logs(user_id, limit=50)

        return {
            "period_days": days,
            "timestamp": time.time(),
            "monitoring": monitoring_data,
            "performance": perf_report,
            "learning": learning_metrics,
            "errors": error_summary,
            "recent_actions": [log.to_dict() for log in audit_logs[:10]]
        }

    def get_codebase_health(self) -> Dict[str, Any]:
        """Get overall codebase health assessment"""
        patterns = list(self.intelligence.patterns.values())

        if not patterns:
            return {
                "status": "no_data",
                "message": "No patterns analyzed yet"
            }

        total_complexity = sum(p.complexity for p in patterns)
        avg_complexity = total_complexity / len(patterns)

        high_complexity = len([p for p in patterns if p.complexity > 10])
        low_complexity = len([p for p in patterns if p.complexity < 3])

        # Calculate health score
        complexity_score = max(0, 100 - (avg_complexity * 5))
        health_score = complexity_score

        return {
            "status": "healthy" if health_score > 70 else "needs_attention",
            "health_score": health_score,
            "total_patterns": len(patterns),
            "avg_complexity": avg_complexity,
            "high_complexity_count": high_complexity,
            "low_complexity_count": low_complexity,
            "recommendations": self._generate_codebase_recommendations(patterns)
        }

    def _generate_codebase_recommendations(self, patterns: List[Any]) -> List[str]:
        """Generate recommendations for codebase"""
        recommendations = []

        high_complexity = [p for p in patterns if p.complexity > 15]
        if high_complexity:
            recommendations.append(
                f"Refactor {len(high_complexity)} high-complexity patterns (complexity > 15)"
            )

        avg_complexity = sum(p.complexity for p in patterns) / len(patterns) if patterns else 0
        if avg_complexity > 8:
            recommendations.append(
                f"Overall codebase complexity is high ({avg_complexity:.1f}). Consider gradual refactoring."
            )

        return recommendations

    def get_team_overview(self) -> Dict[str, Any]:
        """Get team activity overview"""
        return {
            "total_api_keys": len([k for k in self.enterprise.api_keys.values() if k.is_active]),
            "active_sessions": len([s for s in self.ide.sessions.values() if s.is_active]),
            "total_subscriptions": len(self.enterprise.subscriptions),
            "recent_errors": self.monitoring.get_errors(limit=5),
            "active_integrations": {
                "github": len([w for w in self.github.webhooks.values()]) if hasattr(self.github, 'webhooks') else 0,
                "ide_plugins": len([s for s in self.ide.sessions.values() if s.is_active]),
                "api_keys": len([k for k in self.enterprise.api_keys.values() if k.is_active])
            }
        }


# Global instance
_global_dashboard = DashboardManager()


def get_dashboard_manager() -> DashboardManager:
    """Get global dashboard manager"""
    return _global_dashboard
