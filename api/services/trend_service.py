"""Trend tracking service for Path I."""

from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.db.models import CAQIHistory, TeamScore
from api.models.caqi_models import CAQITrend, CAQIHistoryEntry, CAQIDimensions
import uuid


class TrendService:
    """Track CAQI trends over time."""

    def __init__(self, db: Session):
        self.db = db

    def record_team_snapshot(
        self,
        team_id: str,
        dimensions: Dict[str, float],
        overall: int
    ) -> CAQIHistoryEntry:
        """
        Record a point-in-time snapshot of team CAQI for trend tracking.

        Called after each team aggregation to build historical record.

        Args:
            team_id: Team identifier
            dimensions: Dict with security, complexity, etc.
            overall: Overall CAQI score (0-500)

        Returns:
            CAQIHistoryEntry that was recorded
        """

        history_entry = CAQIHistory(
            id=str(uuid.uuid4()),
            team_id=team_id,
            security_score=dimensions.get("security", 50),
            complexity_score=dimensions.get("complexity", 50),
            documentation_score=dimensions.get("documentation", 50),
            testing_score=dimensions.get("testing", 50),
            dependencies_score=dimensions.get("dependencies", 50),
            maintainability_score=dimensions.get("maintainability", 50),
            overall_caqi=overall,
            recorded_at=datetime.utcnow()
        )

        self.db.add(history_entry)
        self.db.commit()

        return CAQIHistoryEntry(
            dimensions=CAQIDimensions(**dimensions),
            overall_caqi=overall,
            recorded_at=history_entry.recorded_at
        )

    def get_trend(self, team_id: str, days: int = 90) -> Optional[CAQITrend]:
        """
        Get historical trend for a team over N days.

        Args:
            team_id: Team identifier
            days: How many days back to look (default 90)

        Returns:
            CAQITrend with history entries and trend direction, or None if no data
        """

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        history = self.db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= cutoff_date
        ).order_by(CAQIHistory.recorded_at.asc()).all()

        if not history:
            return None

        # Convert to models
        entries = [
            CAQIHistoryEntry(
                dimensions=CAQIDimensions(
                    security=h.security_score,
                    complexity=h.complexity_score,
                    documentation=h.documentation_score,
                    testing=h.testing_score,
                    dependencies=h.dependencies_score,
                    maintainability=h.maintainability_score
                ),
                overall_caqi=h.overall_caqi,
                recorded_at=h.recorded_at
            )
            for h in history
        ]

        # Calculate trend
        trend_direction, change_percent = self._calculate_trend(history)

        return CAQITrend(
            team_id=team_id,
            history=entries,
            trend_direction=trend_direction,
            change_percent=change_percent
        )

    def _calculate_trend(self, history: List) -> Tuple[str, float]:
        """
        Determine if trend is improving, stable, or declining.

        Returns:
            (trend_direction, change_percent)
        """

        if len(history) < 2:
            return "stable", 0.0

        first_score = history[0].overall_caqi
        last_score = history[-1].overall_caqi

        change = last_score - first_score
        change_percent = (change / first_score * 100) if first_score > 0 else 0

        # More than 5% change = trending
        if change_percent > 5:
            trend = "improving"
        elif change_percent < -5:
            trend = "declining"
        else:
            trend = "stable"

        return trend, change_percent

    def get_monthly_snapshot(
        self,
        team_id: str,
        year: int,
        month: int
    ) -> Optional[CAQIHistoryEntry]:
        """
        Get CAQI snapshot for a specific month (e.g., January 2026).

        Returns the latest snapshot recorded in that month.

        Args:
            team_id: Team identifier
            year: Year (e.g., 2026)
            month: Month (1-12)

        Returns:
            CAQIHistoryEntry for that month, or None if no data
        """

        from_date = datetime(year, month, 1)
        to_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)

        # Get latest score in that month
        entry = self.db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= from_date,
            CAQIHistory.recorded_at < to_date
        ).order_by(CAQIHistory.recorded_at.desc()).first()

        if not entry:
            return None

        return CAQIHistoryEntry(
            dimensions=CAQIDimensions(
                security=entry.security_score,
                complexity=entry.complexity_score,
                documentation=entry.documentation_score,
                testing=entry.testing_score,
                dependencies=entry.dependencies_score,
                maintainability=entry.maintainability_score
            ),
            overall_caqi=entry.overall_caqi,
            recorded_at=entry.recorded_at
        )

    def get_monthly_snapshots(
        self,
        team_id: str,
        start_year: int,
        start_month: int,
        num_months: int
    ) -> List[Tuple[str, Optional[CAQIHistoryEntry]]]:
        """
        Get monthly snapshots across multiple months.

        Useful for displaying 3-month or 12-month trends.

        Args:
            team_id: Team identifier
            start_year: Starting year (e.g., 2026)
            start_month: Starting month (1-12)
            num_months: How many months to retrieve

        Returns:
            List of (month_label, snapshot) tuples
        """

        month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        results = []

        year = start_year
        month = start_month

        for _ in range(num_months):
            label = f"{month_labels[month - 1]} {year}"
            snapshot = self.get_monthly_snapshot(team_id, year, month)
            results.append((label, snapshot))

            # Advance to next month
            month += 1
            if month > 12:
                month = 1
                year += 1

        return results
