"""
Usage Tracker - Phase 5.4
Tracks API usage for billing and rate limiting
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import time
from datetime import datetime, timedelta


@dataclass
class UsageRecord:
    """Single usage record"""
    team_id: str
    key_id: str
    operation: str  # "format", "validate", "analyze", "pr_create", etc.
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    status: str = "success"  # "success", "error"
    cost_units: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageStats:
    """Usage statistics for period"""
    team_id: str
    period_start: float
    period_end: float
    total_requests: int
    total_cost_units: float
    requests_by_operation: Dict[str, int] = field(default_factory=dict)
    requests_by_status: Dict[str, int] = field(default_factory=dict)
    avg_duration_ms: float = 0.0
    error_count: int = 0
    success_rate: float = 0.0


class UsageTracker:
    """Tracks API usage for billing"""

    # Operation costs in units
    OPERATION_COSTS = {
        "format": 1,
        "validate": 1,
        "analyze": 5,
        "architecture_analysis": 10,
        "git_risk_analysis": 10,
        "pr_create": 20,
        "parallel_agents": 15,
    }

    def __init__(self):
        self.records: List[UsageRecord] = []
        self.usage_by_team: Dict[str, List[UsageRecord]] = defaultdict(list)
        self.usage_by_key: Dict[str, List[UsageRecord]] = defaultdict(list)

    def record_usage(
        self,
        team_id: str,
        key_id: str,
        operation: str,
        duration_ms: float = 0.0,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ) -> UsageRecord:
        """Record API usage"""
        cost_units = self.OPERATION_COSTS.get(operation, 1)

        record = UsageRecord(
            team_id=team_id,
            key_id=key_id,
            operation=operation,
            duration_ms=duration_ms,
            status=status,
            cost_units=cost_units,
            metadata=metadata or {}
        )

        self.records.append(record)
        self.usage_by_team[team_id].append(record)
        self.usage_by_key[key_id].append(record)

        return record

    def get_usage_stats(
        self,
        team_id: str,
        days: int = 30
    ) -> UsageStats:
        """Get usage statistics for team"""
        now = time.time()
        period_start = now - (days * 86400)

        records = [
            r for r in self.usage_by_team.get(team_id, [])
            if r.timestamp >= period_start
        ]

        total_requests = len(records)
        total_cost_units = sum(r.cost_units for r in records)

        requests_by_operation = defaultdict(int)
        requests_by_status = defaultdict(int)
        durations = []

        for record in records:
            requests_by_operation[record.operation] += 1
            requests_by_status[record.status] += 1
            durations.append(record.duration_ms)

        avg_duration = sum(durations) / len(durations) if durations else 0.0
        error_count = requests_by_status.get("error", 0)
        success_rate = (
            (total_requests - error_count) / total_requests * 100
            if total_requests > 0
            else 0.0
        )

        return UsageStats(
            team_id=team_id,
            period_start=period_start,
            period_end=now,
            total_requests=total_requests,
            total_cost_units=total_cost_units,
            requests_by_operation=dict(requests_by_operation),
            requests_by_status=dict(requests_by_status),
            avg_duration_ms=avg_duration,
            error_count=error_count,
            success_rate=success_rate
        )

    def get_key_usage(self, key_id: str, days: int = 30) -> UsageStats:
        """Get usage for specific key"""
        now = time.time()
        period_start = now - (days * 86400)

        records = [
            r for r in self.usage_by_key.get(key_id, [])
            if r.timestamp >= period_start
        ]

        if not records:
            return UsageStats(
                team_id="",
                period_start=period_start,
                period_end=now,
                total_requests=0,
                total_cost_units=0.0
            )

        team_id = records[0].team_id
        total_requests = len(records)
        total_cost_units = sum(r.cost_units for r in records)

        requests_by_operation = defaultdict(int)
        requests_by_status = defaultdict(int)
        durations = []

        for record in records:
            requests_by_operation[record.operation] += 1
            requests_by_status[record.status] += 1
            durations.append(record.duration_ms)

        avg_duration = sum(durations) / len(durations) if durations else 0.0

        return UsageStats(
            team_id=team_id,
            period_start=period_start,
            period_end=now,
            total_requests=total_requests,
            total_cost_units=total_cost_units,
            requests_by_operation=dict(requests_by_operation),
            requests_by_status=dict(requests_by_status),
            avg_duration_ms=avg_duration
        )

    def get_hourly_usage(self, team_id: str) -> Dict[str, int]:
        """Get usage by hour (last 24 hours)"""
        now = time.time()
        hour_ago = now - 3600

        records = [
            r for r in self.usage_by_team.get(team_id, [])
            if r.timestamp >= hour_ago
        ]

        hourly = defaultdict(int)

        for record in records:
            hour = int(record.timestamp // 3600) * 3600
            hourly[str(hour)] += 1

        return dict(hourly)

    def export_usage(self, team_id: str, days: int = 30) -> str:
        """Export usage as CSV"""
        import csv
        from io import StringIO

        now = time.time()
        period_start = now - (days * 86400)

        records = [
            r for r in self.usage_by_team.get(team_id, [])
            if r.timestamp >= period_start
        ]

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "timestamp", "operation", "duration_ms", "status", "cost_units"
        ])

        for record in records:
            writer.writerow([
                record.timestamp,
                record.operation,
                record.duration_ms,
                record.status,
                record.cost_units
            ])

        return output.getvalue()


# Global usage tracker
_global_usage_tracker = UsageTracker()


def get_usage_tracker() -> UsageTracker:
    """Get global usage tracker"""
    return _global_usage_tracker
