"""
Monitoring & Observability - Phase 6.5
Analytics, telemetry, performance monitoring, error tracking
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
from collections import defaultdict
from statistics import mean, stdev


class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Performance metric"""
    metric_id: str
    name: str
    metric_type: MetricType
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "unit": self.unit,
        }


@dataclass
class ErrorEvent:
    """Error tracking event"""
    error_id: str
    error_type: str
    message: str
    stack_trace: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    severity: str = "error"
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "error_id": self.error_id,
            "error_type": self.error_type,
            "message": self.message,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "resolved": self.resolved,
        }


@dataclass
class SystemHealth:
    """System health status"""
    health_id: str
    timestamp: float = field(default_factory=time.time)
    api_availability: float = 99.9  # Percentage
    avg_response_time_ms: float = 0.0
    error_rate: float = 0.0  # Percentage
    cpu_usage: float = 0.0  # Percentage
    memory_usage: float = 0.0  # Percentage
    active_users: int = 0
    total_requests_24h: int = 0
    success_rate: float = 100.0  # Percentage

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "health_id": self.health_id,
            "timestamp": self.timestamp,
            "api_availability": self.api_availability,
            "avg_response_time_ms": self.avg_response_time_ms,
            "error_rate": self.error_rate,
            "success_rate": self.success_rate,
            "active_users": self.active_users,
        }


@dataclass
class Alert:
    """Alert for anomalies"""
    alert_id: str
    level: AlertLevel
    title: str
    description: str
    metric_name: Optional[str] = None
    threshold: Optional[float] = None
    current_value: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    acknowledged: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "level": self.level.value,
            "title": self.title,
            "description": self.description,
            "timestamp": self.timestamp,
            "acknowledged": self.acknowledged,
        }


class MonitoringManager:
    """Manages monitoring and observability"""

    def __init__(self):
        # Metrics storage
        self.metrics: Dict[str, Metric] = {}
        self.metric_history: Dict[str, List[Metric]] = defaultdict(list)

        # Error tracking
        self.errors: Dict[str, ErrorEvent] = {}
        self.error_counts: Dict[str, int] = defaultdict(int)

        # Alerts
        self.alerts: Dict[str, Alert] = {}
        self.active_alerts: List[str] = []

        # System health
        self.health_snapshots: Dict[str, SystemHealth] = {}
        self.current_health: Optional[SystemHealth] = None

        # Performance data
        self.response_times: List[float] = []
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.error_rates: Dict[str, float] = {}

        # Telemetry
        self.telemetry_events: Dict[str, Any] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}

        # Thresholds for alerts
        self.alert_thresholds = {
            "response_time_ms": 1000,
            "error_rate": 5.0,
            "api_availability": 99.0,
            "cpu_usage": 80.0,
        }

    # ============ Metrics Recording ============

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        tags: Optional[Dict[str, str]] = None,
        unit: str = ""
    ) -> Metric:
        """Record a performance metric"""
        import secrets

        metric_id = f"metric_{secrets.token_hex(8)}"
        metric = Metric(
            metric_id=metric_id,
            name=name,
            metric_type=metric_type,
            value=value,
            tags=tags or {},
            unit=unit
        )

        self.metrics[metric_id] = metric
        self.metric_history[name].append(metric)

        # Trim history to last 1000 entries per metric
        if len(self.metric_history[name]) > 1000:
            self.metric_history[name] = self.metric_history[name][-1000:]

        return metric

    def record_response_time(self, duration_ms: float, endpoint: str) -> None:
        """Record API response time"""
        self.response_times.append(duration_ms)
        self.record_metric(
            f"response_time_{endpoint}",
            duration_ms,
            MetricType.HISTOGRAM,
            tags={"endpoint": endpoint},
            unit="ms"
        )

        # Trim response times to last 10000
        if len(self.response_times) > 10000:
            self.response_times = self.response_times[-10000:]

    def record_request(self, user_id: str, endpoint: str, success: bool) -> None:
        """Record request"""
        self.request_counts[user_id] += 1
        self.request_counts[f"{endpoint}_total"] += 1

        if not success:
            self.error_counts[endpoint] += 1

    def get_metrics(self, metric_name: Optional[str] = None) -> List[Metric]:
        """Get recorded metrics"""
        if metric_name:
            return self.metric_history.get(metric_name, [])

        all_metrics = []
        for metrics_list in self.metric_history.values():
            all_metrics.extend(metrics_list[-10:])  # Last 10 of each metric

        return sorted(all_metrics, key=lambda x: x.timestamp, reverse=True)[:100]

    # ============ Error Tracking ============

    def record_error(
        self,
        error_type: str,
        message: str,
        user_id: Optional[str] = None,
        stack_trace: Optional[str] = None,
        request_id: Optional[str] = None,
        severity: str = "error"
    ) -> ErrorEvent:
        """Record an error event"""
        import secrets

        error_id = f"err_{secrets.token_hex(8)}"
        error = ErrorEvent(
            error_id=error_id,
            error_type=error_type,
            message=message,
            user_id=user_id,
            stack_trace=stack_trace,
            request_id=request_id,
            severity=severity
        )

        self.errors[error_id] = error
        self.error_counts[error_type] += 1

        # Trigger alert if critical
        if severity == "critical":
            self._create_alert(
                AlertLevel.CRITICAL,
                f"Critical Error: {error_type}",
                f"{message}",
                metadata={"error_id": error_id}
            )

        return error

    def get_errors(
        self,
        error_type: Optional[str] = None,
        limit: int = 100,
        resolved: bool = False
    ) -> List[ErrorEvent]:
        """Get errors"""
        errors = [e for e in self.errors.values() if e.resolved == resolved]

        if error_type:
            errors = [e for e in errors if e.error_type == error_type]

        return sorted(errors, key=lambda x: x.timestamp, reverse=True)[:limit]

    def resolve_error(self, error_id: str) -> bool:
        """Mark error as resolved"""
        error = self.errors.get(error_id)
        if error:
            error.resolved = True
            return True
        return False

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        total_errors = len(self.errors)
        unresolved = len([e for e in self.errors.values() if not e.resolved])

        return {
            "total_errors": total_errors,
            "unresolved_errors": unresolved,
            "error_types": dict(sorted(
                self.error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
        }

    # ============ Alerting ============

    def _create_alert(
        self,
        level: AlertLevel,
        title: str,
        description: str,
        metric_name: Optional[str] = None,
        threshold: Optional[float] = None,
        current_value: Optional[float] = None
    ) -> Alert:
        """Create an alert"""
        import secrets

        alert_id = f"alert_{secrets.token_hex(8)}"
        alert = Alert(
            alert_id=alert_id,
            level=level,
            title=title,
            description=description,
            metric_name=metric_name,
            threshold=threshold,
            current_value=current_value
        )

        self.alerts[alert_id] = alert
        self.active_alerts.append(alert_id)

        return alert

    def get_active_alerts(self, level: Optional[AlertLevel] = None) -> List[Alert]:
        """Get active alerts"""
        active = [
            self.alerts[aid] for aid in self.active_alerts
            if aid in self.alerts and not self.alerts[aid].acknowledged
        ]

        if level:
            active = [a for a in active if a.level == level]

        return sorted(active, key=lambda x: x.timestamp, reverse=True)

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            if alert_id in self.active_alerts:
                self.active_alerts.remove(alert_id)
            return True
        return False

    def check_thresholds(self) -> List[Alert]:
        """Check metrics against thresholds and create alerts"""
        new_alerts = []

        # Check response time
        if self.response_times:
            avg_response = mean(self.response_times[-100:])
            if avg_response > self.alert_thresholds["response_time_ms"]:
                alert = self._create_alert(
                    AlertLevel.WARNING,
                    "High Response Time",
                    f"Average response time is {avg_response:.0f}ms",
                    metric_name="response_time",
                    threshold=self.alert_thresholds["response_time_ms"],
                    current_value=avg_response
                )
                new_alerts.append(alert)

        # Check error rate
        if self.request_counts:
            total_requests = sum(self.request_counts.values())
            total_errors = sum(self.error_counts.values())
            if total_requests > 0:
                error_rate = (total_errors / total_requests) * 100
                if error_rate > self.alert_thresholds["error_rate"]:
                    alert = self._create_alert(
                        AlertLevel.CRITICAL,
                        "High Error Rate",
                        f"Error rate is {error_rate:.2f}%",
                        metric_name="error_rate",
                        threshold=self.alert_thresholds["error_rate"],
                        current_value=error_rate
                    )
                    new_alerts.append(alert)

        return new_alerts

    # ============ System Health ============

    def update_system_health(
        self,
        api_availability: float = 99.9,
        avg_response_time_ms: float = 0.0,
        error_rate: float = 0.0,
        cpu_usage: float = 0.0,
        memory_usage: float = 0.0,
        active_users: int = 0,
        total_requests_24h: int = 0
    ) -> SystemHealth:
        """Update system health"""
        import secrets

        health_id = f"health_{secrets.token_hex(8)}"

        # Calculate success rate
        success_rate = 100.0 - error_rate

        health = SystemHealth(
            health_id=health_id,
            api_availability=api_availability,
            avg_response_time_ms=avg_response_time_ms,
            error_rate=error_rate,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_users=active_users,
            total_requests_24h=total_requests_24h,
            success_rate=success_rate
        )

        self.health_snapshots[health_id] = health
        self.current_health = health

        return health

    def get_system_health(self) -> Optional[SystemHealth]:
        """Get current system health"""
        return self.current_health

    def get_health_history(self, hours: int = 24) -> List[SystemHealth]:
        """Get health history"""
        cutoff = time.time() - (hours * 3600)
        return [
            h for h in self.health_snapshots.values()
            if h.timestamp >= cutoff
        ]

    # ============ Analytics & Reporting ============

    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics summary"""
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())

        error_rate = 0.0
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100

        avg_response_time = 0.0
        if self.response_times:
            avg_response_time = mean(self.response_times)

        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": error_rate,
            "success_rate": 100.0 - error_rate,
            "avg_response_time_ms": avg_response_time,
            "active_alerts": len(self.active_alerts),
            "system_health": self.current_health.to_dict() if self.current_health else None,
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""
        if not self.response_times:
            return {
                "error": "No performance data available"
            }

        times = self.response_times[-1000:]  # Last 1000 requests
        sorted_times = sorted(times)

        return {
            "requests_analyzed": len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "avg_ms": mean(times),
            "median_ms": sorted_times[len(sorted_times) // 2],
            "p95_ms": sorted_times[int(len(times) * 0.95)],
            "p99_ms": sorted_times[int(len(times) * 0.99)],
            "stddev_ms": stdev(times) if len(times) > 1 else 0,
        }

    # ============ Telemetry ============

    def record_telemetry_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record telemetry event"""
        self.telemetry_events[f"{event_name}_{time.time()}"] = {
            "event_name": event_name,
            "user_id": user_id,
            "timestamp": time.time(),
            "properties": properties or {}
        }

    def start_user_session(self, user_id: str) -> None:
        """Start user session tracking"""
        self.user_sessions[user_id] = {
            "start_time": time.time(),
            "events": [],
            "is_active": True
        }

    def end_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """End user session tracking"""
        session = self.user_sessions.get(user_id)
        if session:
            session["is_active"] = False
            session["end_time"] = time.time()
            session["duration_seconds"] = session["end_time"] - session["start_time"]
            return session
        return None


# Global instance
_global_monitoring = MonitoringManager()


def get_monitoring_manager() -> MonitoringManager:
    """Get global monitoring manager"""
    return _global_monitoring
