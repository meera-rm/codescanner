"""Tests for Alerting Service - comprehensive coverage of alert generation."""
import pytest
from datetime import datetime
from api.services.alerting_service import AlertingService, AlertSeverity, AlertType


class TestAnomalyAlertCreation:
    """Test anomaly alert creation."""

    def test_create_anomaly_alert_basic(self):
        """Should create anomaly alert with required fields."""
        alert = AlertingService.create_anomaly_alert(
            team_id="team-1",
            dimension="security",
            previous_score=75.0,
            current_score=80.0,
            severity="medium"
        )

        assert alert['id']
        assert alert['team_id'] == "team-1"
        assert alert['alert_type'] == AlertType.ANOMALY_DETECTED.value
        assert alert['severity'] == "medium"
        assert alert['triggered_at']
        assert alert['acknowledged'] is False

    def test_anomaly_alert_calculates_change_percent(self):
        """Should calculate percentage change correctly."""
        alert = AlertingService.create_anomaly_alert(
            team_id="team-1",
            dimension="security",
            previous_score=100.0,
            current_score=110.0,
            severity="low"
        )

        # 10% increase
        assert "10.0%" in alert['description']

    def test_anomaly_alert_with_custom_description(self):
        """Should use custom description if provided."""
        custom_desc = "Security score improved due to patch"
        alert = AlertingService.create_anomaly_alert(
            team_id="team-1",
            dimension="security",
            previous_score=75.0,
            current_score=80.0,
            severity="low",
            description=custom_desc
        )

        assert alert['description'] == custom_desc

    def test_anomaly_alert_negative_change(self):
        """Should handle negative changes."""
        alert = AlertingService.create_anomaly_alert(
            team_id="team-1",
            dimension="documentation",
            previous_score=80.0,
            current_score=72.0,
            severity="high"
        )

        assert "decreased" in alert['description'].lower()


class TestRegressionDetection:
    """Test regression detection."""

    def test_detects_critical_regression(self):
        """Should detect critical regressions (>20 point drop)."""
        current = {
            'security': 50,
            'complexity': 70,
            'documentation': 80,
            'testing': 75,
            'dependencies': 60,
            'maintainability': 70,
        }
        previous = {
            'security': 75,  # 25 point drop = critical
            'complexity': 70,
            'documentation': 80,
            'testing': 75,
            'dependencies': 60,
            'maintainability': 70,
        }

        alerts = AlertingService.detect_regressions(
            team_id="team-1",
            current_scores=current,
            previous_scores=previous
        )

        assert len(alerts) == 1
        assert alerts[0]['severity'] == AlertSeverity.CRITICAL.value
        assert 'security' in alerts[0]['title'].lower()

    def test_detects_high_regression(self):
        """Should detect high regressions (10-20 point drop)."""
        current = {
            'complexity': 60,
        }
        previous = {
            'complexity': 75,  # 15 point drop = high
        }

        alerts = AlertingService.detect_regressions(
            team_id="team-1",
            current_scores=current,
            previous_scores=previous
        )

        assert len(alerts) == 1
        assert alerts[0]['severity'] == AlertSeverity.HIGH.value

    def test_no_alert_for_small_drop(self):
        """Should not alert for small changes."""
        current = {
            'security': 73,
        }
        previous = {
            'security': 75,  # 2 point drop < 10 threshold
        }

        alerts = AlertingService.detect_regressions(
            team_id="team-1",
            current_scores=current,
            previous_scores=previous
        )

        assert len(alerts) == 0

    def test_multiple_regressions(self):
        """Should detect multiple regressions."""
        current = {
            'security': 50,
            'complexity': 55,
            'documentation': 85,
        }
        previous = {
            'security': 75,  # Regression
            'complexity': 70,  # Regression
            'documentation': 85,  # No change
        }

        alerts = AlertingService.detect_regressions(
            team_id="team-1",
            current_scores=current,
            previous_scores=previous
        )

        assert len(alerts) == 2


class TestTrendDetection:
    """Test trend decline detection."""

    def test_detects_declining_trend(self):
        """Should detect declining trend."""
        scores = [80.0, 78.0, 76.0, 74.0, 72.0]  # -10% decline

        alert = AlertingService.detect_trend_decline(
            team_id="team-1",
            recent_scores=scores,
            window_days=30
        )

        assert alert is not None
        assert alert['alert_type'] == AlertType.TREND_DECLINING.value
        assert alert['severity'] == AlertSeverity.MEDIUM.value

    def test_no_alert_for_stable_trend(self):
        """Should not alert for stable scores."""
        scores = [75.0, 75.1, 74.9, 75.2, 75.0]  # ~0% change

        alert = AlertingService.detect_trend_decline(
            team_id="team-1",
            recent_scores=scores,
            window_days=30
        )

        assert alert is None

    def test_no_alert_for_improving_trend(self):
        """Should not alert for improving scores."""
        scores = [70.0, 72.0, 74.0, 76.0, 78.0]  # +10% increase

        alert = AlertingService.detect_trend_decline(
            team_id="team-1",
            recent_scores=scores,
            window_days=30
        )

        assert alert is None

    def test_handles_insufficient_data(self):
        """Should handle insufficient data gracefully."""
        alert = AlertingService.detect_trend_decline(
            team_id="team-1",
            recent_scores=[75.0],
            window_days=30
        )

        assert alert is None


class TestAlertAcknowledgment:
    """Test alert acknowledgment workflow."""

    def test_acknowledge_alert(self):
        """Should acknowledge alert successfully."""
        result = AlertingService.acknowledge_alert(
            alert_id="alert-123",
            acknowledged_by="user-456",
            notes="Fixed in deployment"
        )

        assert result is True

    def test_acknowledge_without_notes(self):
        """Should acknowledge alert without notes."""
        result = AlertingService.acknowledge_alert(
            alert_id="alert-123",
            acknowledged_by="user-456"
        )

        assert result is True


class TestAlertRetrieval:
    """Test alert retrieval and filtering."""

    def test_get_unacknowledged_alerts(self):
        """Should retrieve unacknowledged alerts."""
        alerts = AlertingService.get_unacknowledged_alerts(
            team_id="team-1",
            limit=10
        )

        assert isinstance(alerts, list)

    def test_get_alert_history(self):
        """Should retrieve alert history."""
        history = AlertingService.get_alert_history(
            team_id="team-1",
            days=30
        )

        assert isinstance(history, list)

    def test_get_alert_history_with_severity_filter(self):
        """Should filter history by severity."""
        history = AlertingService.get_alert_history(
            team_id="team-1",
            days=30,
            severity="critical"
        )

        assert isinstance(history, list)


class TestAlertNotification:
    """Test alert notification sending."""

    def test_send_alert_notification_default_channels(self):
        """Should send notification using default channels."""
        alert = {
            'id': 'alert-123',
            'severity': 'critical',
            'channels': ['in_app']
        }

        result = AlertingService.send_alert_notification(alert)

        assert result is True

    def test_send_alert_notification_multiple_channels(self):
        """Should send to multiple channels."""
        alert = {
            'id': 'alert-123',
            'severity': 'high',
            'channels': ['in_app', 'email', 'slack']
        }

        result = AlertingService.send_alert_notification(
            alert=alert,
            channels=['email', 'slack']
        )

        assert result is True

    def test_send_alert_with_custom_channels(self):
        """Should override alert's channels."""
        alert = {
            'id': 'alert-123',
            'severity': 'high',
        }

        result = AlertingService.send_alert_notification(
            alert=alert,
            channels=['webhook']
        )

        assert result is True


class TestSeverityThresholds:
    """Test severity threshold definitions."""

    def test_severity_thresholds_are_defined(self):
        """Should have severity thresholds configured."""
        thresholds = AlertingService.SEVERITY_THRESHOLDS

        assert 'low' in thresholds
        assert 'medium' in thresholds
        assert 'high' in thresholds
        assert 'critical' in thresholds

    def test_thresholds_are_progressive(self):
        """Thresholds should increase with severity."""
        thresholds = AlertingService.SEVERITY_THRESHOLDS

        assert thresholds['low'] < thresholds['medium']
        assert thresholds['medium'] < thresholds['high']
        assert thresholds['high'] < thresholds['critical']

    def test_regression_threshold_defined(self):
        """Should have regression threshold."""
        assert AlertingService.REGRESSION_THRESHOLD > 0

    def test_trend_decline_threshold_defined(self):
        """Should have trend decline threshold."""
        assert AlertingService.TREND_DECLINE_THRESHOLD < 0


class TestAlertEnums:
    """Test alert enumeration values."""

    def test_alert_severity_enum(self):
        """Should have all severity values."""
        assert AlertSeverity.LOW.value == "low"
        assert AlertSeverity.MEDIUM.value == "medium"
        assert AlertSeverity.HIGH.value == "high"
        assert AlertSeverity.CRITICAL.value == "critical"

    def test_alert_type_enum(self):
        """Should have all alert type values."""
        assert AlertType.ANOMALY_DETECTED.value == "anomaly_detected"
        assert AlertType.THRESHOLD_BREACHED.value == "threshold_breached"
        assert AlertType.TREND_DECLINING.value == "trend_declining"
        assert AlertType.REGRESSION_DETECTED.value == "regression_detected"
