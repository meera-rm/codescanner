"""Unit tests for Path I services."""

import pytest
from datetime import datetime
from api.services.team_aggregation_service import TeamAggregationService
from api.services.trend_service import TrendService
from api.services.personality_mapping_service import PersonalityMappingService
from api.db.database import SessionLocal, Base, engine
from api.db.models import TeamScore, TeamMember, CAQIHistory


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
    return SessionLocal()


class TestTeamAggregationService:
    """Tests for TeamAggregationService."""

    def test_average_dimensions_with_scores(self, db):
        """Test that dimensions are correctly averaged."""
        service = TeamAggregationService(db)

        # Create mock score objects
        class MockScore:
            def __init__(self, security, complexity, documentation, testing, dependencies, maintainability):
                self.security_score = security
                self.complexity_score = complexity
                self.documentation_score = documentation
                self.testing_score = testing
                self.dependencies_score = dependencies
                self.maintainability_score = maintainability

        scores = [
            MockScore(80, 70, 75, 85, 60, 80),
            MockScore(90, 80, 85, 95, 70, 90),
            MockScore(70, 60, 65, 75, 50, 70),
        ]

        averages = service._average_dimensions(scores)

        assert averages["security"] == 80  # (80 + 90 + 70) / 3
        assert averages["complexity"] == 70
        assert averages["documentation"] == 75
        assert averages["testing"] == 85
        assert averages["dependencies"] == 60
        assert averages["maintainability"] == 80

    def test_calculate_overall_caqi(self, db):
        """Test CAQI calculation from dimensions."""
        service = TeamAggregationService(db)

        dimensions = {
            "security": 80,
            "complexity": 70,
            "documentation": 75,
            "testing": 85,
            "dependencies": 60,
            "maintainability": 80
        }

        caqi = service._calculate_overall_caqi(dimensions)

        # Should be 0-500 range
        assert 0 <= caqi <= 500
        # Higher dimensions should result in higher CAQI
        assert caqi > 300

    def test_archetype_reckless_optimist(self, db):
        """Test Reckless Optimist archetype detection."""
        service = TeamAggregationService(db)

        dimensions = {
            "documentation": 30,
            "testing": 30,
            "complexity": 30,
            "security": 50,
            "dependencies": 50,
            "maintainability": 40
        }

        archetype = service._map_to_archetype(dimensions)
        assert archetype == "Reckless Optimist"

    def test_archetype_cautious_perfectionist(self, db):
        """Test Cautious Perfectionist archetype detection."""
        service = TeamAggregationService(db)

        dimensions = {
            "documentation": 80,
            "testing": 80,
            "complexity": 40,
            "security": 80,
            "dependencies": 30,
            "maintainability": 80
        }

        archetype = service._map_to_archetype(dimensions)
        assert archetype == "Cautious Perfectionist"

    def test_archetype_secretive_perfectionist(self, db):
        """Test Secretive Perfectionist archetype detection."""
        service = TeamAggregationService(db)

        dimensions = {
            "documentation": 30,
            "testing": 80,
            "complexity": 70,
            "security": 60,
            "dependencies": 50,
            "maintainability": 60
        }

        archetype = service._map_to_archetype(dimensions)
        assert archetype == "Secretive Perfectionist"

    def test_archetype_anxious_overthinker(self, db):
        """Test Anxious Overthinker archetype detection."""
        service = TeamAggregationService(db)

        dimensions = {
            "documentation": 80,
            "testing": 80,
            "complexity": 70,
            "security": 80,
            "dependencies": 80,
            "maintainability": 70
        }

        archetype = service._map_to_archetype(dimensions)
        assert archetype == "Anxious Overthinker"

    def test_archetype_pragmatic_engineer(self, db):
        """Test default Pragmatic Engineer archetype."""
        service = TeamAggregationService(db)

        dimensions = {
            "documentation": 60,
            "testing": 60,
            "complexity": 50,
            "security": 60,
            "dependencies": 50,
            "maintainability": 60
        }

        archetype = service._map_to_archetype(dimensions)
        assert archetype == "Pragmatic Engineer"


class TestTrendService:
    """Tests for TrendService."""

    def test_calculate_trend_improving(self, db):
        """Test trend calculation for improving trend."""
        service = TrendService(db)

        class MockHistory:
            def __init__(self, overall_caqi):
                self.overall_caqi = overall_caqi

        history = [
            MockHistory(300),
            MockHistory(320),
            MockHistory(340)
        ]

        trend, change_pct = service._calculate_trend(history)
        assert trend == "improving"
        assert change_pct > 0
        assert change_pct == pytest.approx(13.33, abs=0.5)

    def test_calculate_trend_declining(self, db):
        """Test trend calculation for declining trend."""
        service = TrendService(db)

        class MockHistory:
            def __init__(self, overall_caqi):
                self.overall_caqi = overall_caqi

        history = [
            MockHistory(340),
            MockHistory(320),
            MockHistory(300)
        ]

        trend, change_pct = service._calculate_trend(history)
        assert trend == "declining"
        assert change_pct < 0

    def test_calculate_trend_stable(self, db):
        """Test trend calculation for stable trend."""
        service = TrendService(db)

        class MockHistory:
            def __init__(self, overall_caqi):
                self.overall_caqi = overall_caqi

        history = [
            MockHistory(320),
            MockHistory(319),
            MockHistory(321)
        ]

        trend, change_pct = service._calculate_trend(history)
        assert trend == "stable"
        assert abs(change_pct) < 5


class TestPersonalityMappingService:
    """Tests for PersonalityMappingService."""

    def test_get_archetype_profile(self):
        """Test retrieving archetype profile."""
        service = PersonalityMappingService()

        profile = service.get_archetype_profile("Reckless Optimist")
        assert "description" in profile
        assert "characteristics" in profile
        assert "strengths" in profile
        assert "risks" in profile

    def test_get_archetype_description(self):
        """Test getting archetype description."""
        service = PersonalityMappingService()

        desc = service.get_archetype_description("Cautious Perfectionist")
        assert "High quality" in desc or "Thorough" in desc

    def test_suggest_improvements_reckless(self):
        """Test improvement suggestions for Reckless Optimist."""
        service = PersonalityMappingService()

        dimensions = {"testing": 30, "documentation": 35, "complexity": 40}
        suggestions = service.suggest_improvements("Reckless Optimist", dimensions)

        assert len(suggestions) > 0
        assert any("test" in s.lower() for s in suggestions)

    def test_suggest_improvements_secretive(self):
        """Test improvement suggestions for Secretive Perfectionist."""
        service = PersonalityMappingService()

        dimensions = {"documentation": 25, "testing": 85, "complexity": 75}
        suggestions = service.suggest_improvements("Secretive Perfectionist", dimensions)

        assert len(suggestions) > 0
        assert any("document" in s.lower() for s in suggestions)

    def test_compare_archetypes(self):
        """Test archetype comparison."""
        service = PersonalityMappingService()

        comparison = service.compare_archetypes("Reckless Optimist", "Cautious Perfectionist")
        assert "Reckless Optimist" in comparison
        assert "Cautious Perfectionist" in comparison
        assert "strengths" in comparison["Reckless Optimist"]
        assert "risks" in comparison["Cautious Perfectionist"]

    def test_all_archetypes_defined(self):
        """Test that all expected archetypes are defined."""
        service = PersonalityMappingService()

        expected = [
            "Reckless Optimist",
            "Cautious Perfectionist",
            "Secretive Perfectionist",
            "Anxious Overthinker",
            "Pragmatic Engineer"
        ]

        for archetype in expected:
            profile = service.get_archetype_profile(archetype)
            assert profile is not None
            assert "description" in profile
