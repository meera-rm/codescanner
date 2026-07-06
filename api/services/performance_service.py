"""Service for tracking and analyzing API performance metrics."""
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from threading import Lock


class PerformanceMetric:
    """Single performance measurement."""

    def __init__(
        self,
        endpoint: str,
        method: str,
        duration_ms: float,
        status_code: int,
        timestamp: datetime,
    ):
        self.endpoint = endpoint
        self.method = method
        self.duration_ms = duration_ms
        self.status_code = status_code
        self.timestamp = timestamp


class PerformanceService:
    """Track and analyze API performance metrics."""

    def __init__(self, max_metrics: int = 10000):
        self.metrics: List[PerformanceMetric] = []
        self.max_metrics = max_metrics
        self.lock = Lock()
        self.slow_endpoint_threshold = 500  # ms

    def record_metric(
        self,
        endpoint: str,
        method: str,
        duration_ms: float,
        status_code: int,
    ) -> None:
        """Record a single API request metric."""
        with self.lock:
            metric = PerformanceMetric(
                endpoint=endpoint,
                method=method,
                duration_ms=duration_ms,
                status_code=status_code,
                timestamp=datetime.utcnow(),
            )
            self.metrics.append(metric)

            # Keep only recent metrics to prevent memory bloat
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]

    def get_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for last N minutes."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        with self.lock:
            recent = [m for m in self.metrics if m.timestamp >= cutoff]

        if not recent:
            return {
                'total_requests': 0,
                'avg_response_time_ms': 0,
                'p50_response_time_ms': 0,
                'p95_response_time_ms': 0,
                'p99_response_time_ms': 0,
                'min_response_time_ms': 0,
                'max_response_time_ms': 0,
                'error_count': 0,
                'error_rate_percent': 0,
                'time_period_minutes': minutes,
            }

        times = [m.duration_ms for m in recent]
        errors = [m for m in recent if m.status_code >= 400]

        times.sort()
        avg_time = sum(times) / len(times) if times else 0

        def percentile(data: List[float], p: int) -> float:
            if not data:
                return 0
            idx = int(len(data) * p / 100)
            return data[min(idx, len(data) - 1)]

        return {
            'total_requests': len(recent),
            'avg_response_time_ms': round(avg_time, 2),
            'p50_response_time_ms': round(percentile(times, 50), 2),
            'p95_response_time_ms': round(percentile(times, 95), 2),
            'p99_response_time_ms': round(percentile(times, 99), 2),
            'min_response_time_ms': round(min(times), 2),
            'max_response_time_ms': round(max(times), 2),
            'error_count': len(errors),
            'error_rate_percent': round(len(errors) / len(recent) * 100, 2),
            'time_period_minutes': minutes,
        }

    def get_endpoint_stats(self, minutes: int = 60) -> Dict[str, Dict[str, Any]]:
        """Get performance stats per endpoint."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        with self.lock:
            recent = [m for m in self.metrics if m.timestamp >= cutoff]

        stats_by_endpoint = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'min_time': float('inf'),
            'max_time': 0,
            'error_count': 0,
        })

        for metric in recent:
            key = f"{metric.method} {metric.endpoint}"
            stats = stats_by_endpoint[key]
            stats['count'] += 1
            stats['total_time'] += metric.duration_ms
            stats['min_time'] = min(stats['min_time'], metric.duration_ms)
            stats['max_time'] = max(stats['max_time'], metric.duration_ms)
            if metric.status_code >= 400:
                stats['error_count'] += 1

        # Calculate averages and convert to proper format
        result = {}
        for endpoint, stats in stats_by_endpoint.items():
            result[endpoint] = {
                'request_count': stats['count'],
                'avg_response_time_ms': round(stats['total_time'] / stats['count'], 2),
                'min_response_time_ms': round(stats['min_time'], 2),
                'max_response_time_ms': round(stats['max_time'], 2),
                'error_count': stats['error_count'],
                'error_rate_percent': round(stats['error_count'] / stats['count'] * 100, 2),
            }

        return dict(sorted(result.items()))

    def get_slow_endpoints(
        self,
        minutes: int = 60,
        threshold_ms: Optional[int] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get endpoints slower than threshold, sorted by avg response time."""
        threshold = threshold_ms or self.slow_endpoint_threshold
        stats = self.get_endpoint_stats(minutes)

        slow = [
            {
                'endpoint': endpoint,
                **metrics,
            }
            for endpoint, metrics in stats.items()
            if metrics['avg_response_time_ms'] >= threshold
        ]

        # Sort by avg response time descending
        slow.sort(key=lambda x: x['avg_response_time_ms'], reverse=True)

        return slow[:limit]

    def get_error_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get summary of errors by status code."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        with self.lock:
            recent = [m for m in self.metrics if m.timestamp >= cutoff]

        errors_by_code = defaultdict(int)

        for metric in recent:
            if metric.status_code >= 400:
                errors_by_code[metric.status_code] += 1

        total_errors = sum(errors_by_code.values())
        total_requests = len(recent)

        return {
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate_percent': round(total_errors / total_requests * 100, 2) if total_requests > 0 else 0,
            'errors_by_status_code': dict(sorted(errors_by_code.items())),
        }

    def get_response_time_distribution(self, minutes: int = 60) -> Dict[str, int]:
        """Get distribution of response times in buckets."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        with self.lock:
            recent = [m for m in self.metrics if m.timestamp >= cutoff]

        # Define buckets: <100ms, <250ms, <500ms, <1000ms, <2500ms, >=2500ms
        buckets = {
            '<100ms': 0,
            '<250ms': 0,
            '<500ms': 0,
            '<1000ms': 0,
            '<2500ms': 0,
            '>=2500ms': 0,
        }

        for metric in recent:
            if metric.duration_ms < 100:
                buckets['<100ms'] += 1
            elif metric.duration_ms < 250:
                buckets['<250ms'] += 1
            elif metric.duration_ms < 500:
                buckets['<500ms'] += 1
            elif metric.duration_ms < 1000:
                buckets['<1000ms'] += 1
            elif metric.duration_ms < 2500:
                buckets['<2500ms'] += 1
            else:
                buckets['>=2500ms'] += 1

        return buckets

    def get_time_series(
        self,
        minutes: int = 60,
        bucket_size_minutes: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get response time metrics over time in buckets."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)

        with self.lock:
            recent = [m for m in self.metrics if m.timestamp >= cutoff]

        # Group by time bucket
        buckets = defaultdict(list)

        for metric in recent:
            # Round down to nearest bucket
            bucket_time = metric.timestamp.replace(
                minute=(metric.timestamp.minute // bucket_size_minutes) * bucket_size_minutes,
                second=0,
                microsecond=0,
            )
            buckets[bucket_time].append(metric.duration_ms)

        # Calculate stats per bucket
        result = []
        for bucket_time in sorted(buckets.keys()):
            times = buckets[bucket_time]
            times.sort()

            result.append({
                'timestamp': bucket_time.isoformat(),
                'request_count': len(times),
                'avg_response_time_ms': round(sum(times) / len(times), 2),
                'p95_response_time_ms': round(times[int(len(times) * 0.95)] if times else 0, 2),
                'max_response_time_ms': round(max(times), 2),
            })

        return result

    def clear_old_metrics(self, older_than_minutes: int = 120) -> int:
        """Remove metrics older than specified minutes. Returns count removed."""
        cutoff = datetime.utcnow() - timedelta(minutes=older_than_minutes)

        with self.lock:
            before_count = len(self.metrics)
            self.metrics = [m for m in self.metrics if m.timestamp >= cutoff]
            removed = before_count - len(self.metrics)

        return removed

    def reset(self) -> None:
        """Clear all metrics."""
        with self.lock:
            self.metrics.clear()


# Global performance service instance
performance_service = PerformanceService()
