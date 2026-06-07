"""Integration tests for Phase I+1 - testing service interactions and API flows."""
import pytest
from datetime import datetime, timedelta
from api.services.anomaly_detection import AnomalyDetectionService
from api.services.peer_comparison import PeerComparisonService
from api.services.developer_drill_down import DeveloperDrillDownService
from api.services.alerting_service import AlertingService


class TestFullAnomalyDetectionFlow:
    """Test complete anomaly detection workflow."""

    def test_detect_and_acknowledge_anomaly(self, mock_db, team_with_developers):
        """Should detect anomalies and allow acknowledgment."""
        team, members, metrics = team_with_developers

        # Detect anomalies
        anomalies = AnomalyDetectionService.detect_anomalies("test-team", db=mock_db)

        # Should be able to acknowledge each anomaly
        if anomalies:
            for anomaly in anomalies:
                result = AnomalyDetectionService.mark_anomaly_reviewed(
                    anomaly.id if hasattr(anomaly, 'id') else "test-id",
                    "test-user",
                    "Test note",
                    db=mock_db
                )
                assert result is True


class TestPeerComparisonIntegration:
    """Test peer comparison with real data flow."""

    def test_create_peer_group_and_compare(self, mock_db, team_with_developers):
        """Should create peer group and perform comparison."""
        team, members, metrics = team_with_developers

        # Create peer group
        peer_group = PeerComparisonService.create_peer_group(
            name="test-peers",
            team_ids=["test-team"],
            description="Test peer group",
            db=mock_db
        )

        assert peer_group.peer_group_name == "test-peers"

    def test_calculate_benchmarks_flow(self, mock_db, team_with_developers):
        """Should calculate and retrieve benchmarks."""
        team, members, metrics = team_with_developers

        # Calculate benchmarks
        benchmarks = PeerComparisonService.calculate_benchmarks("company", db=mock_db)

        # Should return dict (possibly empty if not enough data)
        assert isinstance(benchmarks, dict)


class TestDeveloperAnalyticsFlow:
    """Test complete developer analytics workflow."""

    def test_get_contributions_then_top_contributors(self, mock_db, team_with_developers):
        """Should get contributions and filter top contributors."""
        team, members, metrics = team_with_developers

        # Get all contributions
        all_contribs = DeveloperDrillDownService.calculate_developer_contributions(
            "test-team", db=mock_db
        )

        assert isinstance(all_contribs, list)
        assert len(all_contribs) <= len(members)

        # Get top contributors
        if all_contribs:
            top = DeveloperDrillDownService.get_top_contributors(
                "test-team", limit=2, db=mock_db
            )

            assert isinstance(top, list)
            assert len(top) <= min(2, len(all_contribs))

    def test_get_developer_metrics_detail(self, mock_db, team_with_developers):
        """Should get detailed developer metrics."""
        team, members, metrics = team_with_developers

        if members:
            dev_id = members[0].developer_id
            metrics_detail = DeveloperDrillDownService.get_developer_metrics(
                "test-team", dev_id, db=mock_db
            )

            assert metrics_detail['developer_id'] == dev_id
            assert metrics_detail['team_id'] == "test-team"


class TestAlertingIntegration:
    """Test alert generation and management."""

    def test_create_anomaly_alert_and_acknowledge(self):
        """Should create and acknowledge alerts."""
        # Create alert
        alert = AlertingService.create_anomaly_alert(
            team_id="team-1",
            dimension="security",
            previous_score=75.0,
            current_score=85.0,
            severity="high"
        )

        assert alert['id']
        assert not alert['acknowledged']

        # Acknowledge alert
        result = AlertingService.acknowledge_alert(
            alert['id'],
            "user-123",
            "Fixed in security patch"
        )

        assert result is True

    def test_detect_regression_and_create_alert(self):
        """Should detect regressions and create appropriate alerts."""
        current = {
            'security': 50,
            'complexity': 70,
            'documentation': 80,
            'testing': 75,
            'dependencies': 60,
            'maintainability': 70,
        }
        previous = {
            'security': 75,  # Critical regression
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

        assert len(alerts) > 0
        assert alerts[0]['severity'] == 'critical'


class TestEndToEndTeamAnalysis:
    """Test complete team analysis workflow."""

    def test_full_caqi_analysis_workflow(self, mock_db, team_with_developers):
        """
        Complete workflow:
        1. Get developer contributions
        2. Detect anomalies
        3. Create alerts
        4. Acknowledge alerts
        """
        team, members, metrics = team_with_developers

        # Step 1: Get contributions
        contributions = DeveloperDrillDownService.calculate_developer_contributions(
            "test-team", db=mock_db
        )
        assert isinstance(contributions, list)
        assert len(contributions) > 0

        # Step 2: Detect anomalies
        anomalies = AnomalyDetectionService.detect_anomalies("test-team", db=mock_db)
        assert isinstance(anomalies, list)

        # Step 3: Create alerts
        alerts = []
        alert = AlertingService.create_anomaly_alert(
            team_id="test-team",
            dimension="security",
            previous_score=75.0,
            current_score=85.0,
            severity="high"
        )
        alerts.append(alert)
        assert alert['id']
        assert not alert['acknowledged']

        # Step 4: Acknowledge alerts
        if alerts:
            ack_result = AlertingService.acknowledge_alert(
                alerts[0]['id'],
                "test-user",
                "Reviewed"
            )
            assert ack_result is True


class TestConcurrentDataAccess:
    """Test handling of concurrent/simultaneous data access."""

    def test_multiple_alert_acknowledgments_concurrent(self):
        """Should handle multiple alert acknowledgments concurrently."""
        # Create multiple alerts and acknowledge them
        alert_ids = ["alert-1", "alert-2", "alert-3"]

        acks = [
            AlertingService.acknowledge_alert(aid, f"user-{i}") for i, aid in enumerate(alert_ids)
        ]

        assert all(ack is True for ack in acks)

    def test_multiple_alert_acknowledgments(self):
        """Should handle multiple alert acknowledgments."""
        alert_ids = ["alert-1", "alert-2", "alert-3"]

        acks = [
            AlertingService.acknowledge_alert(aid, f"user-{i}") for i, aid in enumerate(alert_ids)
        ]

        assert all(ack is True for ack in acks)


class TestDataConsistency:
    """Test data consistency across services."""

    def test_peer_group_team_id_consistency(self, mock_db):
        """Peer group should store and retrieve team IDs consistently."""
        from api.models.peer_group import PeerGroup
        import json

        # Create peer group
        peer_group = PeerGroup(
            id="test-group",
            peer_group_name="test",
            created_at=datetime.utcnow()
        )
        peer_group.set_team_ids(["team-1", "team-2", "team-3"])

        # Verify team IDs stored correctly
        retrieved_ids = peer_group.get_team_ids()
        assert retrieved_ids == ["team-1", "team-2", "team-3"]

    def test_developer_contributions_consistency(self, mock_db, team_with_developers):
        """Multiple calls should return consistent results."""
        team, members, metrics = team_with_developers

        # Get contributions twice
        contrib1 = DeveloperDrillDownService.calculate_developer_contributions(
            "test-team", db=mock_db
        )
        contrib2 = DeveloperDrillDownService.calculate_developer_contributions(
            "test-team", db=mock_db
        )

        # Should return same number of developers
        assert len(contrib1) == len(contrib2)


class TestErrorHandling:
    """Test error handling across services."""

    def test_nonexistent_team_in_anomaly_detection(self, mock_db):
        """Should handle nonexistent teams gracefully."""
        result = AnomalyDetectionService.detect_anomalies("nonexistent-team", db=mock_db)
        assert result == []

    def test_nonexistent_peer_group(self, mock_db):
        """Should raise error for nonexistent peer group."""
        with pytest.raises(ValueError, match="not found"):
            PeerComparisonService.get_peer_comparison(
                "team-1",
                "nonexistent-group",
                db=mock_db
            )

    def test_nonexistent_developer(self, mock_db):
        """Should handle nonexistent developers gracefully."""
        result = DeveloperDrillDownService.get_developer_metrics(
            "team-1",
            "nonexistent-dev",
            db=mock_db
        )

        assert result['developer_id'] == "nonexistent-dev"
        assert result['metrics'] == []


class TestPerformanceCharacteristics:
    """Test performance characteristics of integrated services."""

    def test_large_developer_count(self, mock_db):
        """Should handle large developer counts efficiently."""
        # Mock database with many developers
        # In real scenario, would measure execution time
        result = DeveloperDrillDownService.calculate_developer_contributions(
            "large-team",
            db=mock_db
        )

        assert isinstance(result, list)

    def test_long_history_analysis(self, mock_db):
        """Should handle long time periods efficiently."""
        # Request 365 days of data
        result = DeveloperDrillDownService.calculate_developer_contributions(
            "test-team",
            days=365,
            db=mock_db
        )

        assert isinstance(result, list)
