"""
Integration Tests for Production Operations - Phase 5.2
Tests monitoring, logging, tracing, health checks, and alerts
"""

import pytest
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.metrics_collector import MetricsCollector, StandardMetrics
from api.services.structured_logger import StructuredLogger, get_logger
from api.services.distributed_tracer import get_tracer, SpanKind, SpanStatus
from api.services.health_check import HealthChecker, HealthStatus, setup_standard_checks
from api.services.alert_rules import AlertRuleManager, AlertRule, AlertCondition, AlertSeverity, StandardAlerts, AlertConditionOperator


class TestProductionOperationsIntegration:
    """Integration tests for production operations"""

    @pytest.mark.asyncio
    async def test_metrics_and_alerts_integration(self):
        """Test metrics collection triggering alerts"""
        collector = MetricsCollector()
        alert_manager = AlertRuleManager()

        # Setup metrics
        StandardMetrics.setup(collector)

        # Setup alerts
        StandardAlerts.setup(alert_manager)

        # Simulate high latency
        for _ in range(10):
            collector.record_histogram(
                "codepulse_api_latency_seconds",
                3.0  # Exceeds 2 second threshold
            )

        # Evaluate alerts
        metrics = {
            "codepulse_api_latency_seconds": 3.0
        }

        alerts = alert_manager.evaluate_rules(metrics)

        # Should trigger latency alert
        triggered = [a for a in alerts if a.rule.name == "api_latency_high"]
        assert len(triggered) > 0

    @pytest.mark.asyncio
    async def test_structured_logging_with_correlation(self):
        """Test structured logging with correlation IDs"""
        logger = get_logger("test_service")

        # Set correlation ID
        correlation_id = logger.set_correlation_id("test-123")

        assert logger.get_correlation_id() == "test-123"

        # Log messages (with correlation ID)
        logger.info("Operation started", operation="test")
        logger.info("Operation completed", operation="test", status="success")

    @pytest.mark.asyncio
    async def test_distributed_tracing(self):
        """Test distributed tracing"""
        from api.services.distributed_tracer import TraceContext

        tracer = get_tracer()

        # Start trace
        trace_id = tracer.start_trace()

        # Create spans using context manager
        with TraceContext(tracer, "api_request", SpanKind.SERVER) as span:
            span.set_attribute("method", "GET")
            span.set_attribute("path", "/api/analyze")

            with TraceContext(tracer, "agent_execution", SpanKind.INTERNAL) as agent_span:
                agent_span.set_attribute("agent", "security_auditor")
                agent_span.add_event("agent_started", {"time": "now"})

            span.add_event("agent_complete")

        # Export trace
        spans = tracer.list_spans(trace_id)
        assert len(spans) >= 1

    @pytest.mark.asyncio
    async def test_health_check_system(self):
        """Test health check system"""
        checker = HealthChecker()

        # Register checks
        async def quick_check():
            return {
                "status": HealthStatus.HEALTHY,
                "details": {"latency_ms": 10}
            }

        checker.register_check("quick_service", quick_check)

        # Run checks
        health = await checker.check_all()

        assert health.status == HealthStatus.HEALTHY
        assert len(health.components) > 0

    @pytest.mark.asyncio
    async def test_alert_cooldown(self):
        """Test alert cooldown mechanism"""
        alert_manager = AlertRuleManager()

        rule = AlertRule(
            name="test_alert",
            description="Test",
            severity=AlertSeverity.WARNING,
            conditions=[
                AlertCondition(
                    metric_name="metric",
                    operator=AlertConditionOperator.GREATER_THAN,
                    threshold=10.0
                )
            ],
            cooldown_seconds=1
        )

        alert_manager.add_rule(rule)

        metrics = {"metric": 20.0}

        # First evaluation
        alerts1 = alert_manager.evaluate_rules(metrics)
        assert len(alerts1) > 0

        # Immediate re-evaluation (should be in cooldown)
        alerts2 = alert_manager.evaluate_rules(metrics)
        assert len(alerts2) == 0

    def test_metrics_summary(self):
        """Test metrics summary export"""
        collector = MetricsCollector()
        StandardMetrics.setup(collector)

        # Simulate some metrics
        collector.increment_counter("codepulse_api_requests_total", 100.0)
        collector.set_gauge("codepulse_memory_usage_bytes", 1024000)
        collector.record_histogram("codepulse_api_latency_seconds", 0.250)

        summary = collector.get_summary()

        assert summary["metrics_count"] > 0
        assert "codepulse_api_requests_total" in summary["metrics"]
        assert summary["metrics"]["codepulse_api_requests_total"]["latest"] == 100.0

    def test_prometheus_export_format(self):
        """Test Prometheus format export"""
        collector = MetricsCollector()
        StandardMetrics.setup(collector)

        collector.increment_counter("codepulse_api_requests_total", 50.0)

        prometheus = collector.export_prometheus()

        assert "# HELP" in prometheus
        assert "# TYPE" in prometheus
        assert "codepulse_api_requests_total" in prometheus

    @pytest.mark.asyncio
    async def test_multiple_health_checks(self):
        """Test multiple health checks in parallel"""
        checker = HealthChecker()

        async def check_a():
            await asyncio.sleep(0.01)
            return {"status": HealthStatus.HEALTHY}

        async def check_b():
            await asyncio.sleep(0.02)
            return {"status": HealthStatus.HEALTHY}

        async def check_c():
            await asyncio.sleep(0.01)
            return {"status": HealthStatus.HEALTHY}

        checker.register_check("service_a", check_a)
        checker.register_check("service_b", check_b)
        checker.register_check("service_c", check_c)

        health = await checker.check_all()

        assert health.status == HealthStatus.HEALTHY
        assert health.checks_passed == 3

    def test_alert_rule_conditions(self):
        """Test alert rule condition evaluation"""
        rule = AlertRule(
            name="test",
            description="Test rule",
            severity=AlertSeverity.WARNING,
            conditions=[
                AlertCondition(
                    metric_name="cpu",
                    operator=AlertConditionOperator.GREATER_THAN,
                    threshold=80.0
                )
            ]
        )

        # Should trigger
        assert rule.evaluate({"cpu": 85.0}) is True

        # Should not trigger
        assert rule.evaluate({"cpu": 75.0}) is False

        # Missing metric
        assert rule.evaluate({}) is False

    def test_structured_logger_json_output(self):
        """Test structured logger JSON format"""
        logger = get_logger("test")

        # This tests that the logger can be called (actual JSON output is internal)
        logger.info("Test message", user_id="123", operation="test")

        # Logger should be functional
        assert logger.logger is not None


class TestPerformanceCharacteristics:
    """Test performance of monitoring services"""

    def test_metrics_throughput(self):
        """Test metrics collection throughput"""
        collector = MetricsCollector()

        # Record many metrics
        import time
        start = time.time()

        for i in range(1000):
            collector.increment_counter("requests", 1.0)
            collector.set_gauge("memory", 100 + i)

        elapsed = (time.time() - start) * 1000

        # Should handle 1000 metric updates < 500ms
        assert elapsed < 500

    def test_alert_evaluation_performance(self):
        """Test alert evaluation performance"""
        import time

        alert_manager = AlertRuleManager()
        StandardAlerts.setup(alert_manager)

        metrics = {
            "codepulse_api_latency_seconds": 1.5,
            "codepulse_error_rate_percent": 2.0,
            "codepulse_memory_usage_percent": 50.0,
            "codepulse_queue_depth": 25.0,
            "codepulse_agent_failure_rate_percent": 5.0
        }

        start = time.time()

        for _ in range(100):
            alert_manager.evaluate_rules(metrics)

        elapsed = (time.time() - start) * 1000

        # Should evaluate 100 times < 200ms
        assert elapsed < 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
