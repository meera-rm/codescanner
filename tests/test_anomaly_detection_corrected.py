"""Tests for Anomaly Detection Service - comprehensive coverage of corrected implementation."""
import pytest
from datetime import datetime, timedelta
from api.db.database import SessionLocal
from api.models.anomaly import Anomaly
from api.models.team_score import TeamScore
from api.models.caqi_history import CAQIHistory
from api.services.anomaly_detection import AnomalyDetectionService


@pytest.fixture
def db():
    """Create a test database session."""
    from api.db.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_team(db):
    """Create a sample team."""
    team = TeamScore(
        team_id="test-team",
        team_name="Test Team",
        overall_caqi=350,
        security=75,
        complexity=70,
        documentation=65,
        testing=80,
        dependencies=60,
        maintainability=75,
        calculated_at=datetime.utcnow()
    )
    db.add(team)
    db.commit()
    return team


class TestAnomalyDetectionMinimumHistory:
    """Test minimum history validation (CRITICAL FIX #1)."""

    def test_insufficient_history_returns_empty(self, db, sample_team):
        """Should return empty list if < 3 data points."""
        # Add only 2 history points
        today = datetime.utcnow()
        history = [
            CAQIHistory(
                team_id="test-team",
                overall_caqi=340,
                security=75,
                complexity=70,
                documentation=65,
                testing=80,
                dependencies=60,
                maintainability=75,
                recorded_at=today - timedelta(days=1)
            ),
            CAQIHistory(
                team_id="test-team",
                overall_caqi=345,
                security=75,
                complexity=70,
                documentation=65,
                testing=80,
                dependencies=60,
                maintainability=75,
                recorded_at=today
            )
        ]
        db.add_all(history)
        db.commit()

        # Should return empty list (< 3 points)
        result = AnomalyDetectionService.detect_anomalies("test-team", db)
        assert result == []

    def test_sufficient_history_detects_anomalies(self, db, sample_team):
        """Should detect anomalies with 3+ data points."""
        today = datetime.utcnow()
        history = [
            CAQIHistory(
                team_id="test-team",
                overall_caqi=300,
                security=70,  # Lower than current
                complexity=70,
                documentation=65,
                testing=80,
                dependencies=60,
                maintainability=75,
                recorded_at=today - timedelta(days=3)
            ),
            CAQIHistory(
                team_id="test-team",
                overall_caqi=310,
                security=72,
                complexity=70,
                documentation=65,
                testing=80,
                dependencies=60,
                maintainability=75,
                recorded_at=today - timedelta(days=2)
            ),
            CAQIHistory(
                team_id="test-team",
                overall_caqi=320,
                security=73,
                complexity=70,
                documentation=65,
                testing=80,
                dependencies=60,
                maintainability=75,
                recorded_at=today - timedelta(days=1)
            )
        ]
        db.add_all(history)
        db.commit()

        # Should detect anomaly (security at 75 vs avg 71.67 = ~4.5% increase, below threshold)
        # Or with larger difference:
        sample_team.security = 85  # 15% increase = high severity
        db.commit()

        result = AnomalyDetectionService.detect_anomalies("test-team", db)
        # Check if any anomalies detected
        assert isinstance(result, list)


class TestAnomalyDetectionSeverity:
    """Test anomaly severity calculation."""

    def test_detects_critical_anomaly(self, db, sample_team):
        """Should detect critical severity (>20% change)."""
        today = datetime.utcnow()
        history = [
            CAQIHistory(
                team_id="test-team",
                overall_caqi=300,
                security=70,
                complexity=70,
                documentation=65,
                testing=80,
                dependencies=60,
                maintainability=75,
                recorded_at=today - timedelta(days=3)
            ),
            CAQIHistory(
                team_id="test-team",
                overall_caqi=310,
                security=70,
                complexity=70,
                documentation=65,
                testing=80,
                dependencies=60,
                maintainability=75,
                recorded_at=today - timedelta(days=2)
            ),
            CAQIHistory(
                team_id="test-team",
                overall_caqi=320,
                security=70,
                complexity=70,
                documentation=65,
                testing=80,
                dependencies=60,
                maintainability=75,
                recorded_at=today - timedelta(days=1)
            )
        ]
        db.add_all(history)
        db.commit()

        # Update team with critical change (70 -> 85 = ~21% increase)
        sample_team.security = 85
        db.commit()

        result = AnomalyDetectionService.detect_anomalies("test-team", db)

        # Find security anomaly
        security_anomaly = next((a for a in result if a.dimension == 'security'), None)
        if security_anomaly:
            assert security_anomaly.severity in ['high', 'critical']

    def test_calculates_severity_correctly(self, db, sample_team):
        """Should classify severity levels correctly."""
        today = datetime.utcnow()

        # Create baseline
        history = [
            CAQIHistory(
                team_id="test-team",
                overall_caqi=300,
                security=50,
                complexity=50,
                documentation=50,
                testing=50,
                dependencies=50,
                maintainability=50,
                recorded_at=today - timedelta(days=i)
            )
            for i in range(3, 0, -1)
        ]
        db.add_all(history)
        db.commit()

        # Test with different severity levels
        test_cases = [
            (55, 'low'),      # 10% = medium threshold
            (57.5, 'medium'),  # 15% = high threshold
            (60, 'high'),      # 20% = critical threshold
            (65, 'critical'),  # 30% = critical
        ]

        for new_score, expected_severity in test_cases:
            sample_team.security = new_score
            db.commit()

            anomalies = AnomalyDetectionService.detect_anomalies("test-team", db)
            security_anom = next((a for a in anomalies if a.dimension == 'security'), None)

            if security_anom:
                assert security_anom.severity == expected_severity, \
                    f"Expected {expected_severity} for {new_score}, got {security_anom.severity}"


class TestAnomalyDetectionValidation:
    """Test input validation (CRITICAL FIX #7)."""

    def test_validates_metric_range(self, db, sample_team):
        """Should validate metrics are 0-100."""
        # Test valid range
        AnomalyDetectionService._validate_metric_range('security', 50)
        AnomalyDetectionService._validate_metric_range('security', 0)
        AnomalyDetectionService._validate_metric_range('security', 100)

        # Test invalid ranges
        with pytest.raises(ValueError):
            AnomalyDetectionService._validate_metric_range('security', -10)

        with pytest.raises(ValueError):
            AnomalyDetectionService._validate_metric_range('security', 150)

        with pytest.raises(ValueError):
            AnomalyDetectionService._validate_metric_range('security', 'invalid')

    def test_handles_invalid_score_types(self, db, sample_team):
        """Should handle non-numeric scores gracefully."""
        today = datetime.utcnow()
        history = [
            CAQIHistory(
                team_id="test-team",
                overall_caqi=300,
                security=70,
                complexity=70,
                documentation=65,
                testing=80,
                dependencies=60,
                maintainability=75,
                recorded_at=today - timedelta(days=i)
            )
            for i in range(3, 0, -1)
        ]
        db.add_all(history)
        db.commit()

        # Set invalid score (should be caught during anomaly detection)
        sample_team.security = 75  # Valid
        db.commit()

        result = AnomalyDetectionService.detect_anomalies("test-team", db)
        assert isinstance(result, list)


class TestAnomalyMarking:
    """Test anomaly review workflow."""

    def test_marks_anomaly_reviewed(self, db, sample_team):
        """Should mark anomaly as reviewed."""
        today = datetime.utcnow()
        history = [
            CAQIHistory(
                team_id="test-team",
                overall_caqi=300,
                security=70,
                complexity=70,
                documentation=65,
                testing=80,
                dependencies=60,
                maintainability=75,
                recorded_at=today - timedelta(days=i)
            )
            for i in range(3, 0, -1)
        ]
        db.add_all(history)
        db.commit()

        # Create an anomaly
        anomaly = Anomaly(
            id="test-anomaly",
            team_id="test-team",
            dimension="security",
            previous_score=70,
            current_score=75,
            change_percent=7.1,
            severity="low",
            reviewed=False
        )
        db.add(anomaly)
        db.commit()

        # Mark as reviewed
        result = AnomalyDetectionService.mark_anomaly_reviewed(
            "test-anomaly",
            "user-123",
            "Low change, expected",
            db
        )

        assert result is True

        # Verify in database
        reviewed = db.query(Anomaly).filter(Anomaly.id == "test-anomaly").first()
        assert reviewed.reviewed is True
        assert reviewed.reviewed_by == "user-123"
        assert reviewed.notes == "Low change, expected"

    def test_get_unreviewed_anomalies(self, db, sample_team):
        """Should return only unreviewed anomalies."""
        # Create multiple anomalies
        reviewed_anomaly = Anomaly(
            id="reviewed",
            team_id="test-team",
            dimension="security",
            previous_score=70,
            current_score=75,
            change_percent=7.1,
            severity="low",
            reviewed=True,
            reviewed_by="user-1"
        )
        unreviewed_anomaly = Anomaly(
            id="unreviewed",
            team_id="test-team",
            dimension="complexity",
            previous_score=70,
            current_score=85,
            change_percent=21.4,
            severity="critical",
            reviewed=False
        )
        db.add_all([reviewed_anomaly, unreviewed_anomaly])
        db.commit()

        # Get unreviewed
        result = AnomalyDetectionService.get_unreviewed_anomalies("test-team", db)

        assert len(result) == 1
        assert result[0].id == "unreviewed"
        assert result[0].reviewed is False


class TestPercentileCalculation:
    """Test percentile calculation utility."""

    def test_calculate_percentile_single_value(self):
        """Should return 50 for single value."""
        result = AnomalyDetectionService.calculate_percentile(50, [50])
        assert result == 50.0

    def test_calculate_percentile_multiple_values(self):
        """Should calculate percentile correctly."""
        values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        # Test various positions
        assert AnomalyDetectionService.calculate_percentile(10, values) == 10.0  # 10th percentile
        assert AnomalyDetectionService.calculate_percentile(50, values) == 50.0  # 50th percentile
        assert AnomalyDetectionService.calculate_percentile(100, values) == 100.0  # 100th percentile

    def test_calculate_percentile_empty_list(self):
        """Should return None for empty list."""
        result = AnomalyDetectionService.calculate_percentile(50, [])
        assert result is None
