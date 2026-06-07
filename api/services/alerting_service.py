"""Alerting Service - anomaly detection and alert generation for teams."""
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts that can be generated."""
    ANOMALY_DETECTED = "anomaly_detected"
    THRESHOLD_BREACHED = "threshold_breached"
    TREND_DECLINING = "trend_declining"
    REGRESSION_DETECTED = "regression_detected"


class AlertingService:
    """Generate and manage alerts for CAQI anomalies and regressions."""

    # Alert thresholds
    SEVERITY_THRESHOLDS = {
        'low': 5,          # 5% change = low
        'medium': 10,      # 10% change = medium
        'high': 15,        # 15% change = high
        'critical': 20,    # 20% change = critical
    }

    TREND_DECLINE_THRESHOLD = -2.0  # -2% over period = declining trend
    REGRESSION_THRESHOLD = 10       # Drop of 10+ points = regression

    @staticmethod
    def create_anomaly_alert(
        team_id: str,
        dimension: str,
        previous_score: float,
        current_score: float,
        severity: str,
        description: Optional[str] = None,
        db=None
    ) -> Dict:
        """
        Create an alert for a detected anomaly.

        Args:
            team_id: Team ID
            dimension: CAQI dimension (security, complexity, etc)
            previous_score: Score before change
            current_score: Current score
            severity: Alert severity (low, medium, high, critical)
            description: Optional custom description
            db: Database session

        Returns:
            Alert record dictionary
        """
        change_percent = ((current_score - previous_score) / previous_score * 100) if previous_score else 0

        if not description:
            direction = "increased" if change_percent > 0 else "decreased"
            description = (
                f"{dimension.title()} score {direction} from {previous_score:.1f} "
                f"to {current_score:.1f} ({abs(change_percent):.1f}%)"
            )

        alert = {
            'id': str(uuid.uuid4()),
            'team_id': team_id,
            'alert_type': AlertType.ANOMALY_DETECTED.value,
            'title': f"{dimension.title()} Anomaly Detected",
            'description': description,
            'severity': severity,
            'triggered_at': datetime.utcnow().isoformat(),
            'acknowledged': False,
            'acknowledged_by': None,
            'acknowledged_at': None,
            'notification_sent_at': None,
            'channels': ['in_app']  # Default channels
        }

        logger.info(
            f"Created {severity} alert for team {team_id}: {dimension} changed {change_percent:.1f}%"
        )

        return alert

    @staticmethod
    def detect_regressions(
        team_id: str,
        current_scores: Dict[str, float],
        previous_scores: Dict[str, float],
        db=None
    ) -> List[Dict]:
        """
        Detect regressions (significant drops in scores).

        Args:
            team_id: Team ID
            current_scores: Current dimension scores
            previous_scores: Previous dimension scores
            db: Database session

        Returns:
            List of regression alerts
        """
        alerts = []

        for dimension, current in current_scores.items():
            previous = previous_scores.get(dimension, current)

            drop = previous - current
            if drop >= AlertingService.REGRESSION_THRESHOLD:
                severity = AlertSeverity.CRITICAL if drop >= 20 else AlertSeverity.HIGH

                alert = AlertingService.create_anomaly_alert(
                    team_id=team_id,
                    dimension=dimension,
                    previous_score=previous,
                    current_score=current,
                    severity=severity.value,
                    description=f"Regression detected: {dimension} dropped {drop:.1f} points",
                    db=db
                )
                alerts.append(alert)

        return alerts

    @staticmethod
    def detect_trend_decline(
        team_id: str,
        recent_scores: List[float],
        window_days: int = 30,
        db=None
    ) -> Optional[Dict]:
        """
        Detect declining trends over a period.

        Args:
            team_id: Team ID
            recent_scores: List of recent scores in chronological order
            window_days: Period to analyze
            db: Database session

        Returns:
            Trend alert if decline detected, None otherwise
        """
        if len(recent_scores) < 2:
            return None

        # Calculate trend: (last - first) / first * 100
        trend_percent = ((recent_scores[-1] - recent_scores[0]) / recent_scores[0] * 100) if recent_scores[0] else 0

        if trend_percent <= AlertingService.TREND_DECLINE_THRESHOLD:
            return {
                'id': str(uuid.uuid4()),
                'team_id': team_id,
                'alert_type': AlertType.TREND_DECLINING.value,
                'title': f'Declining Trend ({window_days} days)',
                'description': f'Team CAQI declining {abs(trend_percent):.1f}% over the last {window_days} days',
                'severity': AlertSeverity.MEDIUM.value,
                'triggered_at': datetime.utcnow().isoformat(),
                'acknowledged': False,
            }

        return None

    @staticmethod
    def acknowledge_alert(
        alert_id: str,
        acknowledged_by: str,
        notes: Optional[str] = None,
        db=None
    ) -> bool:
        """
        Mark an alert as acknowledged.

        Args:
            alert_id: Alert ID
            acknowledged_by: User ID acknowledging
            notes: Optional notes
            db: Database session

        Returns:
            True if successful
        """
        logger.info(f"Acknowledged alert {alert_id} by {acknowledged_by}")

        # In a real implementation, would update database
        # For now just return True
        return True

    @staticmethod
    def get_unacknowledged_alerts(
        team_id: str,
        limit: int = 10,
        db=None
    ) -> List[Dict]:
        """
        Get unacknowledged alerts for a team.

        Args:
            team_id: Team ID
            limit: Max alerts to return
            db: Database session

        Returns:
            List of unacknowledged alerts
        """
        # In a real implementation, would query database
        logger.debug(f"Fetching unacknowledged alerts for team {team_id}")
        return []

    @staticmethod
    def send_alert_notification(
        alert: Dict,
        channels: List[str] = None,
        db=None
    ) -> bool:
        """
        Send alert notification through specified channels.

        Args:
            alert: Alert dictionary
            channels: Notification channels (email, slack, webhook)
            db: Database session

        Returns:
            True if sent successfully
        """
        if channels is None:
            channels = alert.get('channels', ['in_app'])

        logger.info(
            f"Sending {alert['severity']} alert {alert['id']} via {', '.join(channels)}"
        )

        # Implementation would handle:
        # - Email notifications
        # - Slack messages
        # - Webhook callbacks
        # - In-app notifications

        return True

    @staticmethod
    def get_alert_history(
        team_id: str,
        days: int = 30,
        severity: Optional[str] = None,
        db=None
    ) -> List[Dict]:
        """
        Get alert history for a team.

        Args:
            team_id: Team ID
            days: Look back period
            severity: Filter by severity
            db: Database session

        Returns:
            List of alerts
        """
        logger.debug(f"Fetching {days}-day alert history for team {team_id}")

        # In a real implementation, would query database
        return []
