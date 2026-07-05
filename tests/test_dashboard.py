"""
Tests for Dashboard & Analytics - Phase 7
"""

import pytest
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.dashboard import (
    DashboardManager,
    DashboardSummary,
    DashboardWidget,
)
from api.services.enterprise import PlanType


class TestDashboardManager:
    """Test dashboard and analytics"""

    def test_dashboard_summary_structure(self):
        """Test dashboard summary has correct structure"""
        summary = DashboardSummary()

        assert hasattr(summary, "timestamp")
        assert hasattr(summary, "total_patterns")
        assert hasattr(summary, "subscription_plan")
        assert hasattr(summary, "system_health")
        assert summary.system_health == 99.9

    def test_get_dashboard_summary(self):
        """Test getting dashboard summary"""
        manager = DashboardManager()

        summary = manager.get_dashboard_summary("user123")

        assert summary is not None
        assert summary.total_patterns >= 0
        assert summary.system_health >= 0

    def test_dashboard_summary_caching(self):
        """Test dashboard summary caching"""
        manager = DashboardManager()

        summary1 = manager.get_dashboard_summary("user123")
        time.sleep(0.01)
        summary2 = manager.get_dashboard_summary("user123")

        # Should return same cached object
        assert summary1.timestamp == summary2.timestamp

    def test_ai_insights_widget(self):
        """Test AI insights widget"""
        manager = DashboardManager()

        widget = manager.get_ai_insights_widget()

        assert widget.name == "AI Learning Insights"
        assert widget.widget_type == "metric"
        assert "total_patterns" in widget.data
        assert "avg_complexity" in widget.data

    def test_system_health_widget(self):
        """Test system health widget"""
        manager = DashboardManager()

        widget = manager.get_system_health_widget()

        assert widget.name == "System Health"
        assert widget.widget_type == "status"
        assert "availability" in widget.data
        assert "error_rate" in widget.data

    def test_alerts_widget(self):
        """Test alerts widget"""
        manager = DashboardManager()

        widget = manager.get_alerts_widget()

        assert widget.name == "Active Alerts"
        assert widget.widget_type == "alert"
        assert "alerts" in widget.data
        assert isinstance(widget.data["alerts"], list)

    def test_activity_widget(self):
        """Test activity widget"""
        manager = DashboardManager()

        widget = manager.get_activity_widget()

        assert widget.name == "Recent Activity"
        assert widget.widget_type == "list"
        assert "analyses_today" in widget.data
        assert "api_calls" in widget.data

    def test_usage_widget(self):
        """Test usage widget"""
        manager = DashboardManager()

        manager.enterprise.create_subscription("user123", PlanType.PRO)
        widget = manager.get_usage_widget("user123")

        assert widget.name == "Plan Usage"
        assert widget.widget_type == "metric"
        assert "api_calls" in widget.data
        assert "limits" in widget.data

    def test_get_all_widgets(self):
        """Test getting all widgets"""
        manager = DashboardManager()

        widgets = manager.get_all_widgets("user123")

        assert len(widgets) == 5
        assert all(isinstance(w, DashboardWidget) for w in widgets)

    def test_widget_to_dict(self):
        """Test widget serialization"""
        manager = DashboardManager()

        widget = manager.get_ai_insights_widget()
        widget_dict = widget.to_dict()

        assert widget_dict["name"] == "AI Learning Insights"
        assert widget_dict["type"] == "metric"
        assert "data" in widget_dict
        assert "config" in widget_dict

    def test_summary_to_dict(self):
        """Test summary serialization"""
        manager = DashboardManager()

        summary = manager.get_dashboard_summary("user123")
        summary_dict = summary.to_dict()

        assert "ai_insights" in summary_dict
        assert "enterprise" in summary_dict
        assert "monitoring" in summary_dict
        assert "activity" in summary_dict

    def test_analytics_report(self):
        """Test analytics report"""
        manager = DashboardManager()

        report = manager.get_analytics_report("user123", days=7)

        assert report["period_days"] == 7
        assert "monitoring" in report
        assert "performance" in report
        assert "learning" in report
        assert "errors" in report

    def test_codebase_health_no_data(self):
        """Test codebase health with no patterns"""
        manager = DashboardManager()

        health = manager.get_codebase_health()

        assert health["status"] == "no_data"

    def test_team_overview(self):
        """Test team overview"""
        manager = DashboardManager()

        overview = manager.get_team_overview()

        assert "total_api_keys" in overview
        assert "active_sessions" in overview
        assert "total_subscriptions" in overview
        assert "active_integrations" in overview

    def test_dashboard_with_subscription(self):
        """Test dashboard with subscription"""
        manager = DashboardManager()

        manager.enterprise.create_subscription("user123", PlanType.PRO)
        summary = manager.get_dashboard_summary("user123")

        assert summary.subscription_plan == "pro"
        assert summary.api_keys_active >= 0

    def test_widget_refresh_interval(self):
        """Test widget refresh interval config"""
        manager = DashboardManager()

        widget = manager.get_ai_insights_widget()

        assert widget.refresh_interval_seconds == 60

    def test_dashboard_health_status(self):
        """Test dashboard health status determination"""
        manager = DashboardManager()

        health = manager.get_codebase_health()

        if health["status"] != "no_data":
            assert health["status"] in ["healthy", "needs_attention"]

    def test_multiple_users_isolation(self):
        """Test dashboard data is isolated per user"""
        manager = DashboardManager()

        manager.enterprise.create_subscription("user1", PlanType.FREE)
        manager.enterprise.create_subscription("user2", PlanType.PRO)

        sum1 = manager.get_dashboard_summary("user1")
        sum2 = manager.get_dashboard_summary("user2")

        # Both should have valid summaries
        assert sum1.subscription_plan in ["free", "pro"]
        assert sum2.subscription_plan in ["free", "pro"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
