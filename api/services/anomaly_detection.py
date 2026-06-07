"""Anomaly Detection Service - detects unexpected changes in team CAQI scores."""
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from api.db.database import SessionLocal
from api.models.anomaly import Anomaly
from api.models.team_score import TeamScore
from api.models.caqi_history import CAQIHistory

logger = logging.getLogger(__name__)


class AnomalyDetectionService:
    """Detect unexpected changes in team CAQI scores."""

    # CRITICAL: Minimum history points required for meaningful detection
    MIN_HISTORY_POINTS = 3
    HISTORY_WINDOW_DAYS = 7

    # Anomaly severity thresholds (percent change)
    ANOMALY_THRESHOLDS = {
        'low': 5,        # 5% change
        'medium': 10,    # 10% change
        'high': 15,      # 15% change
        'critical': 20   # 20% change
    }

    @staticmethod
    def detect_anomalies(team_id: str, db: SessionLocal) -> List[Anomaly]:
        """
        Detect anomalies by comparing current score to 7-day average.

        CRITICAL FIXES:
        - Requires minimum 3 data points (was causing false anomalies with sparse data)
        - Validates metric ranges (0-100)
        - Returns empty list if insufficient history

        Args:
            team_id: Team to analyze
            db: Database session

        Returns:
            List of detected Anomaly objects
        """
        # Get current score
        current = db.query(TeamScore).filter(
            TeamScore.team_id == team_id
        ).first()

        if not current:
            logger.warning(f"Team {team_id} not found")
            return []

        # Get history
        cutoff_date = datetime.utcnow() - timedelta(days=AnomalyDetectionService.HISTORY_WINDOW_DAYS)
        history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= cutoff_date
        ).order_by(CAQIHistory.recorded_at).all()

        # FIXED: Check minimum data points
        if len(history) < AnomalyDetectionService.MIN_HISTORY_POINTS:
            logger.debug(
                f"Insufficient history for team {team_id}: "
                f"{len(history)} points (need {AnomalyDetectionService.MIN_HISTORY_POINTS})"
            )
            return []

        anomalies = []
        dimensions = ['security', 'complexity', 'documentation', 'testing', 'dependencies', 'maintainability']

        for dimension in dimensions:
            try:
                current_val = getattr(current, dimension)

                # FIXED: Validate current value
                AnomalyDetectionService._validate_metric_range(dimension, current_val)

                # Calculate average from history
                historical_values = [getattr(h, dimension) for h in history]
                avg_historical = sum(historical_values) / len(historical_values)

                # Calculate change percent
                if avg_historical == 0:
                    change_percent = 0 if current_val == 0 else 100
                else:
                    change_percent = ((current_val - avg_historical) / avg_historical) * 100

                # Check if anomaly
                abs_change = abs(change_percent)
                if abs_change > AnomalyDetectionService.ANOMALY_THRESHOLDS['low']:
                    # Determine severity
                    severity = AnomalyDetectionService._get_severity(abs_change)

                    # Create anomaly record
                    anomaly = Anomaly(
                        id=str(uuid.uuid4()),
                        team_id=team_id,
                        dimension=dimension,
                        previous_score=avg_historical,
                        current_score=current_val,
                        change_percent=change_percent,
                        severity=severity,
                        detected_at=datetime.utcnow()
                    )
                    db.add(anomaly)
                    anomalies.append(anomaly)

                    logger.info(
                        f"Anomaly detected: {team_id}/{dimension} "
                        f"changed {change_percent:+.1f}% ({severity})"
                    )

            except ValueError as e:
                logger.error(f"Validation error for {team_id}/{dimension}: {e}")
                continue

        db.commit()
        return anomalies

    @staticmethod
    def _validate_metric_range(dimension: str, score: float) -> None:
        """
        Validate metric is in valid range.

        Args:
            dimension: Dimension name
            score: Score value

        Raises:
            ValueError: If score is outside valid range
        """
        if not isinstance(score, (int, float)):
            raise ValueError(f"{dimension} must be numeric, got {type(score).__name__}")

        if not 0 <= score <= 100:
            raise ValueError(f"{dimension} out of range: {score} (must be 0-100)")

    @staticmethod
    def _get_severity(change_percent: float) -> str:
        """
        Determine anomaly severity based on change percent.

        Args:
            change_percent: Absolute change percentage

        Returns:
            Severity level: 'low', 'medium', 'high', or 'critical'
        """
        if change_percent > AnomalyDetectionService.ANOMALY_THRESHOLDS['critical']:
            return 'critical'
        elif change_percent > AnomalyDetectionService.ANOMALY_THRESHOLDS['high']:
            return 'high'
        elif change_percent > AnomalyDetectionService.ANOMALY_THRESHOLDS['medium']:
            return 'medium'
        else:
            return 'low'

    @staticmethod
    def get_unreviewed_anomalies(team_id: str, db: SessionLocal) -> List[Anomaly]:
        """
        Get anomalies that haven't been reviewed yet.

        Args:
            team_id: Team to query
            db: Database session

        Returns:
            List of unreviewed anomalies
        """
        return db.query(Anomaly).filter(
            Anomaly.team_id == team_id,
            Anomaly.reviewed == False
        ).order_by(Anomaly.detected_at.desc()).all()

    @staticmethod
    def mark_anomaly_reviewed(
        anomaly_id: str,
        reviewed_by: str,
        notes: Optional[str] = None,
        db: SessionLocal = None
    ) -> bool:
        """
        Mark anomaly as reviewed by team lead.

        Args:
            anomaly_id: Anomaly to mark
            reviewed_by: User ID of reviewer
            notes: Optional notes from reviewer
            db: Database session

        Returns:
            True if successful
        """
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()

        if not anomaly:
            logger.warning(f"Anomaly {anomaly_id} not found")
            return False

        anomaly.reviewed = True
        anomaly.reviewed_by = reviewed_by
        anomaly.reviewed_at = datetime.utcnow()
        anomaly.notes = notes
        db.commit()

        logger.info(f"Anomaly {anomaly_id} marked reviewed by {reviewed_by}")
        return True

    @staticmethod
    def calculate_percentile(value: float, values: List[float]) -> Optional[float]:
        """
        Calculate percentile rank (0-100) of value in values list.

        Args:
            value: Value to rank
            values: List of comparison values

        Returns:
            Percentile rank (0-100) or None if empty
        """
        if not values:
            return None

        if len(values) == 1:
            return 50.0

        sorted_values = sorted(values)
        rank = sum(1 for v in sorted_values if v <= value)
        percentile = (rank / len(sorted_values)) * 100

        return round(percentile, 2)
