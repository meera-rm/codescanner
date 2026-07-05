"""
Tests for Metrics Collector - Phase 5.2
"""

import pytest
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.metrics_collector import (
    MetricsCollector, Metric, MetricType, StandardMetrics
)


@pytest.fixture
def collector():
    """Create metrics collector"""
    return MetricsCollector()


class TestMetric:
    """Test individual metrics"""

    def test_create_metric(self):
        """Test creating metric"""
        metric = Metric(
            name="test_metric",
            type=MetricType.COUNTER,
            description="Test metric"
        )

        assert metric.name == "test_metric"
        assert metric.type == MetricType.COUNTER

    def test_add_value(self):
        """Test adding metric value"""
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            description="Test"
        )

        metric.add_value(42.0)

        assert metric.get_latest() == 42.0

    def test_get_average(self):
        """Test average calculation"""
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            description="Test"
        )

        metric.add_value(10.0)
        metric.add_value(20.0)
        metric.add_value(30.0)

        assert metric.get_average() == 20.0

    def test_get_sum(self):
        """Test sum calculation"""
        metric = Metric(
            name="test",
            type=MetricType.COUNTER,
            description="Test"
        )

        metric.add_value(10.0)
        metric.add_value(20.0)
        metric.add_value(15.0)

        assert metric.get_sum() == 45.0

    def test_metric_with_labels(self):
        """Test metric with labels"""
        metric = Metric(
            name="test",
            type=MetricType.GAUGE,
            description="Test"
        )

        metric.add_value(100.0, labels={"method": "GET", "path": "/api"})

        assert metric.values[0].labels["method"] == "GET"

    def test_prometheus_format(self):
        """Test Prometheus format export"""
        metric = Metric(
            name="test_metric",
            type=MetricType.COUNTER,
            description="Test metric"
        )

        metric.add_value(42.0)

        prometheus = metric.to_prometheus_format()

        assert "HELP" in prometheus
        assert "TYPE" in prometheus
        assert "test_metric" in prometheus
        assert "42.0" in prometheus


class TestMetricsCollector:
    """Test metrics collector"""

    def test_register_counter(self, collector):
        """Test registering counter"""
        collector.register_counter("requests", "Total requests")

        assert "requests" in collector.metrics
        assert collector.get_metric("requests").type == MetricType.COUNTER

    def test_register_gauge(self, collector):
        """Test registering gauge"""
        collector.register_gauge("memory", "Memory usage", unit="bytes")

        assert "memory" in collector.metrics
        assert collector.get_metric("memory").type == MetricType.GAUGE

    def test_increment_counter(self, collector):
        """Test incrementing counter"""
        collector.increment_counter("clicks", 1.0)
        collector.increment_counter("clicks", 1.0)

        metric = collector.get_metric("clicks")
        assert metric.get_latest() == 2.0

    def test_set_gauge(self, collector):
        """Test setting gauge"""
        collector.set_gauge("temperature", 25.5)

        assert collector.get_metric("temperature").get_latest() == 25.5

    def test_record_histogram(self, collector):
        """Test recording histogram"""
        collector.record_histogram("latency", 100.0)
        collector.record_histogram("latency", 150.0)
        collector.record_histogram("latency", 200.0)

        metric = collector.get_metric("latency")
        assert metric.get_average() == 150.0

    def test_list_metrics(self, collector):
        """Test listing metrics"""
        collector.register_counter("a", "Metric A")
        collector.register_counter("b", "Metric B")
        collector.register_counter("c", "Metric C")

        metrics = collector.list_metrics()
        assert len(metrics) == 3

    def test_export_prometheus(self, collector):
        """Test Prometheus export"""
        collector.register_counter("requests", "Total requests")
        collector.increment_counter("requests", 5.0)

        prometheus = collector.export_prometheus()

        assert "requests" in prometheus
        assert "HELP" in prometheus
        assert "TYPE" in prometheus

    def test_get_summary(self, collector):
        """Test summary export"""
        collector.register_counter("requests", "Total requests")
        collector.increment_counter("requests", 10.0)

        summary = collector.get_summary()

        assert "metrics_count" in summary
        assert "requests" in summary["metrics"]
        assert summary["metrics"]["requests"]["latest"] == 10.0

    def test_reset_metrics(self, collector):
        """Test resetting metrics"""
        collector.register_counter("requests", "Requests")
        collector.increment_counter("requests", 5.0)

        collector.reset()

        assert len(collector.metrics) == 0

    def test_counter_with_labels(self, collector):
        """Test counter with labels"""
        collector.increment_counter("requests", 1.0, labels={"method": "GET"})
        collector.increment_counter("requests", 1.0, labels={"method": "POST"})

        metric = collector.get_metric("requests")
        assert len(metric.values) == 2
        assert metric.values[0].labels["method"] == "GET"
        assert metric.values[1].labels["method"] == "POST"


class TestStandardMetrics:
    """Test standard metrics setup"""

    def test_setup_standard_metrics(self, collector):
        """Test setting up standard metrics"""
        StandardMetrics.setup(collector)

        # Verify standard metrics exist
        assert collector.get_metric("codepulse_api_requests_total") is not None
        assert collector.get_metric("codepulse_agent_executions_total") is not None
        assert collector.get_metric("codepulse_api_latency_seconds") is not None

    def test_api_metrics(self, collector):
        """Test API metrics"""
        StandardMetrics.setup(collector)

        collector.increment_counter("codepulse_api_requests_total", labels={"method": "GET"})
        collector.record_histogram("codepulse_api_latency_seconds", 0.150)

        requests = collector.get_metric("codepulse_api_requests_total")
        latency = collector.get_metric("codepulse_api_latency_seconds")

        assert requests.get_latest() == 1.0
        assert latency.get_latest() == 0.150

    def test_agent_metrics(self, collector):
        """Test agent metrics"""
        StandardMetrics.setup(collector)

        collector.increment_counter("codepulse_agent_executions_total")
        collector.record_histogram("codepulse_agent_execution_time_seconds", 0.500)

        executions = collector.get_metric("codepulse_agent_executions_total")
        time_metric = collector.get_metric("codepulse_agent_execution_time_seconds")

        assert executions.get_latest() == 1.0
        assert time_metric.get_latest() == 0.500

    def test_cache_metrics(self, collector):
        """Test cache metrics"""
        StandardMetrics.setup(collector)

        collector.increment_counter("codepulse_cache_hits_total", 10.0)
        collector.increment_counter("codepulse_cache_misses_total", 2.0)

        hits = collector.get_metric("codepulse_cache_hits_total")
        misses = collector.get_metric("codepulse_cache_misses_total")

        assert hits.get_latest() == 10.0
        assert misses.get_latest() == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
