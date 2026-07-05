"""
Tests for Monitoring & Observability - Phase 6.5
"""

import pytest
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.monitoring import (
    MonitoringManager,
    MetricType,
    AlertLevel,
)


class TestMonitoringManager:
    """Test monitoring and observability"""

    def test_record_metric(self):
        """Test recording metric"""
        manager = MonitoringManager()

        metric = manager.record_metric(
            name="cpu_usage",
            value=45.5,
            metric_type=MetricType.GAUGE,
            tags={"host": "server1"},
            unit="%"
        )

        assert metric.metric_id.startswith("metric_")
        assert metric.name == "cpu_usage"
        assert metric.value == 45.5
        assert metric.unit == "%"

    def test_record_response_time(self):
        """Test recording response time"""
        manager = MonitoringManager()

        manager.record_response_time(250.5, "/api/analyze")

        assert len(manager.response_times) == 1
        assert manager.response_times[0] == 250.5

    def test_record_request(self):
        """Test recording request"""
        manager = MonitoringManager()

        manager.record_request("user123", "/api/analyze", True)
        manager.record_request("user123", "/api/analyze", False)

        assert manager.request_counts["user123"] == 2
        assert manager.error_counts["/api/analyze"] == 1

    def test_get_metrics(self):
        """Test getting metrics"""
        manager = MonitoringManager()

        manager.record_metric("cpu", 50.0)
        manager.record_metric("memory", 60.0)

        metrics = manager.get_metrics()

        assert len(metrics) > 0

    def test_record_error(self):
        """Test recording error"""
        manager = MonitoringManager()

        error = manager.record_error(
            error_type="ValueError",
            message="Invalid input",
            user_id="user123",
            severity="error"
        )

        assert error.error_id.startswith("err_")
        assert error.error_type == "ValueError"
        assert error.message == "Invalid input"

    def test_get_errors(self):
        """Test getting errors"""
        manager = MonitoringManager()

        manager.record_error("ValueError", "Error 1")
        manager.record_error("TypeError", "Error 2")
        manager.record_error("ValueError", "Error 3")

        errors = manager.get_errors()

        assert len(errors) == 3

    def test_filter_errors_by_type(self):
        """Test filtering errors by type"""
        manager = MonitoringManager()

        manager.record_error("ValueError", "Error 1")
        manager.record_error("TypeError", "Error 2")

        value_errors = manager.get_errors(error_type="ValueError")

        assert len(value_errors) == 1
        assert value_errors[0].error_type == "ValueError"

    def test_resolve_error(self):
        """Test resolving error"""
        manager = MonitoringManager()

        error = manager.record_error("ValueError", "Test error")

        success = manager.resolve_error(error.error_id)

        assert success is True
        assert error.resolved is True

    def test_error_summary(self):
        """Test error summary"""
        manager = MonitoringManager()

        manager.record_error("ValueError", "Error 1")
        manager.record_error("ValueError", "Error 2")
        manager.record_error("TypeError", "Error 3")

        summary = manager.get_error_summary()

        assert summary["total_errors"] == 3
        assert summary["error_types"]["ValueError"] == 2

    def test_create_alert(self):
        """Test creating alert"""
        manager = MonitoringManager()

        alert = manager._create_alert(
            AlertLevel.CRITICAL,
            "High CPU Usage",
            "CPU usage exceeded 80%",
            metric_name="cpu_usage",
            threshold=80.0,
            current_value=95.0
        )

        assert alert.alert_id.startswith("alert_")
        assert alert.level == AlertLevel.CRITICAL
        assert alert.acknowledged is False

    def test_get_active_alerts(self):
        """Test getting active alerts"""
        manager = MonitoringManager()

        manager._create_alert(AlertLevel.WARNING, "Alert 1", "Description 1")
        manager._create_alert(AlertLevel.CRITICAL, "Alert 2", "Description 2")

        alerts = manager.get_active_alerts()

        assert len(alerts) == 2

    def test_acknowledge_alert(self):
        """Test acknowledging alert"""
        manager = MonitoringManager()

        alert = manager._create_alert(AlertLevel.WARNING, "Test Alert", "Description")

        success = manager.acknowledge_alert(alert.alert_id)

        assert success is True
        assert alert.acknowledged is True

    def test_check_thresholds_response_time(self):
        """Test threshold checking for response time"""
        manager = MonitoringManager()
        manager.alert_thresholds["response_time_ms"] = 500

        # Add slow requests
        for _ in range(10):
            manager.response_times.append(600.0)

        alerts = manager.check_thresholds()

        assert len(alerts) > 0
        assert any(a.title == "High Response Time" for a in alerts)

    def test_check_thresholds_error_rate(self):
        """Test threshold checking for error rate"""
        manager = MonitoringManager()
        manager.alert_thresholds["error_rate"] = 5.0

        # Manually set request/error counts
        manager.request_counts["total"] = 100
        manager.error_counts["api"] = 10  # 10% error rate

        alerts = manager.check_thresholds()

        # Should trigger high error rate alert
        assert any(a.title == "High Error Rate" for a in alerts)

    def test_update_system_health(self):
        """Test updating system health"""
        manager = MonitoringManager()

        health = manager.update_system_health(
            api_availability=99.5,
            avg_response_time_ms=150,
            error_rate=2.0,
            cpu_usage=45.0,
            memory_usage=60.0,
            active_users=250
        )

        assert health.api_availability == 99.5
        assert health.success_rate == 98.0
        assert health.active_users == 250

    def test_get_system_health(self):
        """Test getting system health"""
        manager = MonitoringManager()

        manager.update_system_health(api_availability=99.9)

        health = manager.get_system_health()

        assert health is not None
        assert health.api_availability == 99.9

    def test_get_health_history(self):
        """Test getting health history"""
        manager = MonitoringManager()

        manager.update_system_health()
        time.sleep(0.1)
        manager.update_system_health()

        history = manager.get_health_history(hours=1)

        assert len(history) == 2

    def test_get_analytics(self):
        """Test analytics"""
        manager = MonitoringManager()

        manager.request_counts["total"] = 2
        manager.error_counts["api"] = 1
        manager.update_system_health()

        analytics = manager.get_analytics()

        assert analytics["total_requests"] >= 2
        assert analytics["total_errors"] == 1

    def test_get_performance_report(self):
        """Test performance report"""
        manager = MonitoringManager()

        for i in range(20):
            manager.response_times.append(100 + i * 10)

        report = manager.get_performance_report()

        assert "min_ms" in report
        assert "max_ms" in report
        assert "avg_ms" in report
        assert "p95_ms" in report

    def test_record_telemetry_event(self):
        """Test recording telemetry event"""
        manager = MonitoringManager()

        manager.record_telemetry_event(
            "code_analyzed",
            user_id="user123",
            properties={"files": 5, "language": "python"}
        )

        assert len(manager.telemetry_events) > 0

    def test_user_session_tracking(self):
        """Test user session tracking"""
        manager = MonitoringManager()

        manager.start_user_session("user123")
        assert "user123" in manager.user_sessions

        time.sleep(0.1)
        session = manager.end_user_session("user123")

        assert session is not None
        assert session["is_active"] is False
        assert session["duration_seconds"] > 0

    def test_metric_history_limit(self):
        """Test metric history is trimmed"""
        manager = MonitoringManager()

        # Add many metrics
        for i in range(1100):
            manager.record_metric("test_metric", float(i))

        history = manager.metric_history["test_metric"]

        # Should keep only last 1000
        assert len(history) <= 1000

    def test_response_time_trimming(self):
        """Test response time data trimming"""
        manager = MonitoringManager()

        # Use record_response_time which trims
        for i in range(10100):
            manager.record_response_time(float(i), "/test")

        # Should keep only last 10000 (trimming happens in record_response_time)
        assert len(manager.response_times) <= 10000

    def test_metric_serialization(self):
        """Test metric to dict"""
        manager = MonitoringManager()

        metric = manager.record_metric(
            "cpu",
            50.0,
            tags={"host": "server1"},
            unit="%"
        )

        metric_dict = metric.to_dict()

        assert metric_dict["name"] == "cpu"
        assert metric_dict["value"] == 50.0
        assert metric_dict["unit"] == "%"

    def test_error_serialization(self):
        """Test error to dict"""
        manager = MonitoringManager()

        error = manager.record_error(
            "ValueError",
            "Invalid value",
            user_id="user123"
        )

        error_dict = error.to_dict()

        assert error_dict["error_type"] == "ValueError"
        assert error_dict["user_id"] == "user123"

    def test_alert_serialization(self):
        """Test alert to dict"""
        manager = MonitoringManager()

        alert = manager._create_alert(
            AlertLevel.CRITICAL,
            "Test Alert",
            "Test description"
        )

        alert_dict = alert.to_dict()

        assert alert_dict["level"] == "critical"
        assert alert_dict["acknowledged"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
