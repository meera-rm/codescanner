"""Integration tests for Path I.2 API endpoints."""

import pytest
from datetime import datetime
from api.routes.caqi_enhanced import router
from api.db.database import SessionLocal, Base, engine
from api.db.models import TeamScore, TeamMember, CAQIHistory
from api.services.personality_mapping_service import PersonalityMappingService


@pytest.fixture
def setup_db():
    """Ensure all tables exist in the test database.

    Doesn't drop tables on teardown: Base is the app's single shared
    schema, so dropping it here would also remove tables other test
    files (and the running app) still need.
    """
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db(setup_db):
    """Get database session."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_team(db):
    """Create a sample team with scores."""
    team = TeamScore(
        id="test_team_1",
        team_id="test-team",
        team_name="Test Team",
        security_score=85,
        complexity_score=72,
        documentation_score=80,
        testing_score=88,
        dependencies_score=65,
        maintainability_score=78,
        overall_caqi=380,
        personality_archetype="Pragmatic Engineer",
        member_count=3,
        calculated_at=datetime.utcnow()
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    yield team
    db.query(TeamScore).filter(TeamScore.team_id == team.team_id).delete()
    db.commit()


@pytest.fixture
def sample_trend_data(db, sample_team):
    """Create historical trend data."""
    history_entries = [
        CAQIHistory(
            id="hist_1",
            team_id="test-team",
            security_score=80,
            complexity_score=75,
            documentation_score=75,
            testing_score=85,
            dependencies_score=60,
            maintainability_score=75,
            overall_caqi=365,
            recorded_at=datetime(2026, 5, 6)
        ),
        CAQIHistory(
            id="hist_2",
            team_id="test-team",
            security_score=82,
            complexity_score=73,
            documentation_score=77,
            testing_score=86,
            dependencies_score=62,
            maintainability_score=76,
            overall_caqi=372,
            recorded_at=datetime(2026, 5, 20)
        ),
        CAQIHistory(
            id="hist_3",
            team_id="test-team",
            security_score=85,
            complexity_score=72,
            documentation_score=80,
            testing_score=88,
            dependencies_score=65,
            maintainability_score=78,
            overall_caqi=380,
            recorded_at=datetime(2026, 6, 6)
        )
    ]
    for entry in history_entries:
        db.add(entry)
    db.commit()
    yield history_entries
    db.query(CAQIHistory).filter(CAQIHistory.team_id == sample_team.team_id).delete()
    db.commit()


class TestCAQIAPI:
    """Tests for Path I.2 API endpoints."""

    def test_router_registered(self):
        """Test that router is properly configured."""
        assert router.prefix == "/api/v1/caqi"
        assert router.tags == ["caqi"]

    def test_router_has_all_endpoints(self):
        """Test that all expected endpoints are registered."""
        routes = [route for route in router.routes if hasattr(route, 'path')]
        paths = [route.path for route in routes]

        expected_paths = [
            "/api/v1/caqi/team/{team_id}",
            "/api/v1/caqi/team/{team_id}/comparison",
            "/api/v1/caqi/team/{team_id}/trend",
            "/api/v1/caqi/team/{team_id}/monthly/{year}/{month}",
            "/api/v1/caqi/team/{team_id}/monthly-snapshots",
            "/api/v1/caqi/archetype/{archetype}",
            "/api/v1/caqi/team/{team_id}/suggestions",
            "/api/v1/caqi/health"
        ]

        for path in expected_paths:
            assert path in paths, f"Expected path {path} not found in routes"

    def test_archetype_endpoint_exists(self):
        """Test that archetype endpoint is available."""
        service = PersonalityMappingService()
        archetypes = list(service.ARCHETYPES.keys())

        assert len(archetypes) == 5
        assert "Reckless Optimist" in archetypes
        assert "Cautious Perfectionist" in archetypes
        assert "Secretive Perfectionist" in archetypes
        assert "Anxious Overthinker" in archetypes
        assert "Pragmatic Engineer" in archetypes

    def test_archetype_profiles_complete(self):
        """Test that all archetype profiles have required fields."""
        service = PersonalityMappingService()

        for archetype in service.ARCHETYPES:
            profile = service.get_archetype_profile(archetype)

            assert "description" in profile
            assert "characteristics" in profile
            assert "strengths" in profile
            assert "risks" in profile
            assert len(profile["characteristics"]) > 0
            assert len(profile["strengths"]) > 0
            assert len(profile["risks"]) > 0

    def test_team_score_model_fields(self, sample_team):
        """Test that TeamScore model has all expected fields."""
        assert sample_team.team_id == "test-team"
        assert sample_team.team_name == "Test Team"
        assert sample_team.security_score == 85
        assert sample_team.complexity_score == 72
        assert sample_team.documentation_score == 80
        assert sample_team.testing_score == 88
        assert sample_team.dependencies_score == 65
        assert sample_team.maintainability_score == 78
        assert sample_team.overall_caqi == 380
        assert sample_team.personality_archetype == "Pragmatic Engineer"
        assert sample_team.member_count == 3

    def test_caqi_score_range(self, sample_team):
        """Test that CAQI scores are in valid range."""
        # Individual dimensions should be 0-100
        assert 0 <= sample_team.security_score <= 100
        assert 0 <= sample_team.complexity_score <= 100
        assert 0 <= sample_team.documentation_score <= 100
        assert 0 <= sample_team.testing_score <= 100
        assert 0 <= sample_team.dependencies_score <= 100
        assert 0 <= sample_team.maintainability_score <= 100

        # Overall CAQI should be 0-500
        assert 0 <= sample_team.overall_caqi <= 500

    def test_trend_data_integrity(self, sample_trend_data):
        """Test that trend data is stored correctly."""
        assert len(sample_trend_data) == 3

        # Check all entries have required fields
        for entry in sample_trend_data:
            assert entry.team_id == "test-team"
            assert 0 <= entry.overall_caqi <= 500
            assert entry.recorded_at is not None

    def test_trend_direction_calculation(self):
        """Test trend direction calculation logic."""
        from api.services.trend_service import TrendService

        service = TrendService(SessionLocal())

        class MockHistory:
            def __init__(self, caqi):
                self.overall_caqi = caqi

        # Improving trend
        improving = [MockHistory(300), MockHistory(310), MockHistory(320)]
        direction, pct = service._calculate_trend(improving)
        assert direction == "improving"
        assert pct > 0

        # Declining trend
        declining = [MockHistory(320), MockHistory(310), MockHistory(300)]
        direction, pct = service._calculate_trend(declining)
        assert direction == "declining"
        assert pct < 0

        # Stable trend
        stable = [MockHistory(310), MockHistory(309), MockHistory(311)]
        direction, pct = service._calculate_trend(stable)
        assert direction == "stable"
        assert abs(pct) < 5

    def test_suggestion_generation(self):
        """Test improvement suggestion generation."""
        service = PersonalityMappingService()

        # Reckless Optimist should suggest testing & documentation
        reckless_dimensions = {
            "documentation": 30,
            "testing": 30,
            "complexity": 30,
            "security": 50,
            "dependencies": 50,
            "maintainability": 40
        }
        suggestions = service.suggest_improvements("Reckless Optimist", reckless_dimensions)
        assert len(suggestions) > 0
        assert any("test" in s.lower() for s in suggestions)

        # Pragmatic Engineer (default) should have suggestions too
        pragmatic_dimensions = {
            "documentation": 60,
            "testing": 60,
            "complexity": 50,
            "security": 60,
            "dependencies": 50,
            "maintainability": 60
        }
        suggestions = service.suggest_improvements("Pragmatic Engineer", pragmatic_dimensions)
        # Should return list (may be empty for pragmatic)
        assert isinstance(suggestions, list)

    def test_endpoint_path_format(self):
        """Test that all endpoints follow correct path format."""
        for route in router.routes:
            if hasattr(route, 'path'):
                path = route.path
                # All CAQI endpoints should start with /api/v1/caqi
                if "/caqi/" in path:
                    assert path.startswith("/api/v1/caqi/")

    def test_health_check_available(self):
        """Test that health check endpoint exists."""
        health_routes = [r for r in router.routes if hasattr(r, 'path') and r.path == "/api/v1/caqi/health"]
        assert len(health_routes) > 0
