"""
Metrics Collector - Phase 5.2
Prometheus metrics collection and reporting
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Prometheus metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricLabel:
    """Metric label"""
    name: str
    value: str


@dataclass
class MetricValue:
    """Single metric value"""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """Prometheus metric"""
    name: str
    type: MetricType
    description: str
    unit: str = ""
    values: List[MetricValue] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def add_value(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Add metric value"""
        self.values.append(MetricValue(
            timestamp=time.time(),
            value=value,
            labels=labels or {}
        ))

    def get_latest(self) -> Optional[float]:
        """Get latest value"""
        if not self.values:
            return None
        return self.values[-1].value

    def get_average(self) -> float:
        """Get average value"""
        if not self.values:
            return 0.0
        return sum(v.value for v in self.values) / len(self.values)

    def get_sum(self) -> float:
        """Get sum of all values"""
        return sum(v.value for v in self.values)

    def to_prometheus_format(self) -> str:
        """Convert to Prometheus text format"""
        lines = []

        # Header
        lines.append(f"# HELP {self.name} {self.description}")
        lines.append(f"# TYPE {self.name} {self.type.value}")

        # Values
        for value in self.values:
            labels_str = ""
            if value.labels:
                label_pairs = [f'{k}="{v}"' for k, v in value.labels.items()]
                labels_str = "{" + ",".join(label_pairs) + "}"

            lines.append(f"{self.name}{labels_str} {value.value}")

        return "\n".join(lines)


class MetricsCollector:
    """Collects and manages Prometheus metrics"""

    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.start_time = time.time()

    def register_counter(
        self,
        name: str,
        description: str,
        unit: str = ""
    ) -> None:
        """Register counter metric"""
        self.metrics[name] = Metric(
            name=name,
            type=MetricType.COUNTER,
            description=description,
            unit=unit
        )

    def register_gauge(
        self,
        name: str,
        description: str,
        unit: str = ""
    ) -> None:
        """Register gauge metric"""
        self.metrics[name] = Metric(
            name=name,
            type=MetricType.GAUGE,
            description=description,
            unit=unit
        )

    def register_histogram(
        self,
        name: str,
        description: str,
        unit: str = ""
    ) -> None:
        """Register histogram metric"""
        self.metrics[name] = Metric(
            name=name,
            type=MetricType.HISTOGRAM,
            description=description,
            unit=unit
        )

    def increment_counter(
        self,
        name: str,
        amount: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment counter"""
        if name not in self.metrics:
            self.register_counter(name, f"Counter: {name}")

        metric = self.metrics[name]
        current = metric.get_latest() or 0.0
        metric.add_value(current + amount, labels)

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Set gauge value"""
        if name not in self.metrics:
            self.register_gauge(name, f"Gauge: {name}")

        metric = self.metrics[name]
        metric.add_value(value, labels)

    def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record histogram value"""
        if name not in self.metrics:
            self.register_histogram(name, f"Histogram: {name}")

        self.metrics[name].add_value(value, labels)

    def get_metric(self, name: str) -> Optional[Metric]:
        """Get metric by name"""
        return self.metrics.get(name)

    def list_metrics(self) -> List[Metric]:
        """List all metrics"""
        return list(self.metrics.values())

    def export_prometheus(self) -> str:
        """Export all metrics in Prometheus text format"""
        lines = []

        for metric in self.metrics.values():
            lines.append(metric.to_prometheus_format())
            lines.append("")  # Blank line between metrics

        return "\n".join(lines)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        return {
            "uptime_seconds": time.time() - self.start_time,
            "metrics_count": len(self.metrics),
            "metrics": {
                name: {
                    "type": metric.type.value,
                    "latest": metric.get_latest(),
                    "average": metric.get_average(),
                    "sum": metric.get_sum(),
                    "count": len(metric.values)
                }
                for name, metric in self.metrics.items()
            }
        }

    def reset(self) -> None:
        """Reset all metrics"""
        self.metrics.clear()
        self.start_time = time.time()


# Standard metrics

class StandardMetrics:
    """Standard metrics for CodePulse API"""

    @staticmethod
    def setup(collector: MetricsCollector) -> None:
        """Setup standard metrics"""
        # API metrics
        collector.register_counter("codepulse_api_requests_total", "Total API requests")
        collector.register_counter("codepulse_api_errors_total", "Total API errors")
        collector.register_gauge("codepulse_api_active_requests", "Active API requests")
        collector.register_histogram("codepulse_api_latency_seconds", "API latency in seconds")

        # Agent metrics
        collector.register_counter("codepulse_agent_executions_total", "Total agent executions")
        collector.register_counter("codepulse_agent_failures_total", "Total agent failures")
        collector.register_histogram("codepulse_agent_execution_time_seconds", "Agent execution time")

        # File modification metrics
        collector.register_counter("codepulse_file_modifications_total", "Total file modifications")
        collector.register_counter("codepulse_lines_modified_total", "Total lines modified")

        # PR metrics
        collector.register_counter("codepulse_prs_created_total", "Total PRs created")
        collector.register_counter("codepulse_prs_merged_total", "Total PRs merged")

        # Pipeline metrics
        collector.register_counter("codepulse_pipelines_started_total", "Pipelines started")
        collector.register_counter("codepulse_pipelines_completed_total", "Pipelines completed")
        collector.register_histogram("codepulse_pipeline_duration_seconds", "Pipeline duration")

        # System metrics
        collector.register_gauge("codepulse_memory_usage_bytes", "Memory usage in bytes")
        collector.register_gauge("codepulse_cpu_usage_percent", "CPU usage percentage")
        collector.register_gauge("codepulse_queue_depth", "Task queue depth")

        # Cache metrics
        collector.register_counter("codepulse_cache_hits_total", "Cache hits")
        collector.register_counter("codepulse_cache_misses_total", "Cache misses")


class RequestMetricsMiddleware:
    """Middleware for collecting request metrics"""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    async def __call__(self, request, call_next):
        """Middleware handler"""
        start_time = time.time()

        # Increment active requests
        active = self.collector.get_metric("codepulse_api_active_requests")
        current = active.get_latest() if active else 0
        self.collector.set_gauge("codepulse_api_active_requests", current + 1)

        try:
            response = await call_next(request)

            # Record request
            self.collector.increment_counter(
                "codepulse_api_requests_total",
                labels={
                    "method": request.method,
                    "path": str(request.url.path),
                    "status": str(response.status_code)
                }
            )

            # Record latency
            duration = time.time() - start_time
            self.collector.record_histogram(
                "codepulse_api_latency_seconds",
                duration,
                labels={
                    "method": request.method,
                    "path": str(request.url.path)
                }
            )

            return response

        except Exception as e:
            # Record error
            self.collector.increment_counter(
                "codepulse_api_errors_total",
                labels={
                    "method": request.method,
                    "path": str(request.url.path),
                    "error": type(e).__name__
                }
            )
            raise

        finally:
            # Decrement active requests
            active = self.collector.get_metric("codepulse_api_active_requests")
            current = active.get_latest() if active else 0
            self.collector.set_gauge("codepulse_api_active_requests", max(0, current - 1))


# Global collector instance
_global_collector = MetricsCollector()
StandardMetrics.setup(_global_collector)


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector"""
    return _global_collector
