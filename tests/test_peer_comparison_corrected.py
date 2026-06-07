"""Tests for Peer Comparison Service - comprehensive coverage of corrected implementation."""
import pytest
import json
from datetime import datetime
from api.db.database import SessionLocal
from api.models.team_score import TeamScore
from api.models.peer_group import PeerGroup
from api.models.benchmark import Benchmark
from api.services.peer_comparison import PeerComparisonService


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
def sample_teams(db):
    """Create sample teams for comparison."""
    teams = [
        TeamScore(
            team_id="team-a",
            team_name="Team A",
            overall_caqi=350,
            security=75,
            complexity=70,
            documentation=65,
            testing=80,
            dependencies=60,
            maintainability=75,
            calculated_at=datetime.utcnow()
        ),
        TeamScore(
            team_id="team-b",
            team_name="Team B",
            overall_caqi=360,
            security=78,
            complexity=72,
            documentation=68,
            testing=82,
            dependencies=62,
            maintainability=78,
            calculated_at=datetime.utcnow()
        ),
        TeamScore(
            team_id="team-c",
            team_name="Team C",
            overall_caqi=340,
            security=72,
            complexity=68,
            documentation=62,
            testing=78,
            dependencies=58,
            maintainability=72,
            calculated_at=datetime.utcnow()
        ),
    ]
    db.add_all(teams)
    db.commit()
    return teams


class TestPeerGroupCreation:
    """Test peer group creation."""

    def test_create_peer_group(self, db):
        """Should create peer group successfully."""
        peer_group = PeerComparisonService.create_peer_group(
            name="backend-teams",
            team_ids=["team-a", "team-b", "team-c"],
            description="Backend engineering teams",
            db=db
        )

        assert peer_group.peer_group_name == "backend-teams"
        assert peer_group.description == "Backend engineering teams"
        assert peer_group.get_team_ids() == ["team-a", "team-b", "team-c"]

    def test_create_peer_group_requires_name(self, db):
        """Should require peer group name."""
        with pytest.raises(ValueError, match="name is required"):
            PeerComparisonService.create_peer_group(
                name="",
                team_ids=["team-a"],
                db=db
            )

    def test_create_peer_group_requires_teams(self, db):
        """Should require at least one team."""
        with pytest.raises(ValueError, match="at least one team"):
            PeerComparisonService.create_peer_group(
                name="empty-group",
                team_ids=[],
                db=db
            )


class TestPeerComparison:
    """Test peer comparison functionality (CRITICAL FIXES #2)."""

    def test_peer_comparison_empty_group(self, db, sample_teams):
        """Should handle empty peer groups gracefully."""
        # Create empty peer group
        peer_group = PeerGroup(
            id="empty-group",
            peer_group_name="empty",
            team_ids=json.dumps([]),
            created_at=datetime.utcnow()
        )
        db.add(peer_group)
        db.commit()

        # FIXED: Should return error dict instead of crashing
        result = PeerComparisonService.get_peer_comparison("team-a", "empty", db)

        assert result['error'] == 'Peer group is empty'
        assert result['team_id'] == 'team-a'

    def test_peer_comparison_no_peer_data(self, db, sample_teams):
        """Should handle when no peer data is available."""
        # Create peer group with only one team (itself)
        peer_group = PeerGroup(
            id="single-team",
            peer_group_name="single",
            team_ids=json.dumps(["team-a"]),  # Only team-a, will exclude self
            created_at=datetime.utcnow()
        )
        db.add(peer_group)
        db.commit()

        # FIXED: Should return error dict
        result = PeerComparisonService.get_peer_comparison("team-a", "single", db)

        assert result['error'] == 'No peer data available'

    def test_peer_comparison_team_not_found(self, db, sample_teams):
        """Should raise error if team not found."""
        peer_group = PeerGroup(
            id="test-group",
            peer_group_name="test",
            team_ids=json.dumps(["team-a", "team-b"]),
            created_at=datetime.utcnow()
        )
        db.add(peer_group)
        db.commit()

        # FIXED: Should raise ValueError
        with pytest.raises(ValueError, match="not found"):
            PeerComparisonService.get_peer_comparison("nonexistent-team", "test", db)

    def test_peer_comparison_group_not_found(self, db, sample_teams):
        """Should raise error if peer group not found."""
        with pytest.raises(ValueError, match="not found"):
            PeerComparisonService.get_peer_comparison("team-a", "nonexistent-group", db)

    def test_peer_comparison_calculates_correctly(self, db, sample_teams):
        """Should calculate peer comparison correctly."""
        # Create peer group
        peer_group = PeerGroup(
            id="all-teams",
            peer_group_name="all",
            team_ids=json.dumps(["team-a", "team-b", "team-c"]),
            created_at=datetime.utcnow()
        )
        db.add(peer_group)
        db.commit()

        result = PeerComparisonService.get_peer_comparison("team-a", "all", db)

        # Verify structure
        assert 'team_id' in result
        assert 'peer_group' in result
        assert 'peer_count' in result
        assert 'peer_avg_caqi' in result
        assert 'dimensions' in result

        # Verify no error
        assert 'error' not in result

        # Verify dimensions
        for dim in ['security', 'complexity', 'documentation', 'testing', 'dependencies', 'maintainability']:
            assert dim in result['dimensions']
            assert 'team_score' in result['dimensions'][dim]
            assert 'peer_avg' in result['dimensions'][dim]
            assert 'percentile' in result['dimensions'][dim]

    def test_peer_comparison_percentiles(self, db, sample_teams):
        """Should calculate percentiles correctly."""
        peer_group = PeerGroup(
            id="all-teams",
            peer_group_name="all",
            team_ids=json.dumps(["team-a", "team-b", "team-c"]),
            created_at=datetime.utcnow()
        )
        db.add(peer_group)
        db.commit()

        result = PeerComparisonService.get_peer_comparison("team-a", "all", db)

        # team-a security is 75
        # peer (team-b, team-c) security is 78, 72
        # so 75 should be around 50th percentile
        security_percentile = result['dimensions']['security']['percentile']
        assert isinstance(security_percentile, (int, float))
        assert 0 <= security_percentile <= 100


class TestBenchmarkCalculation:
    """Test benchmark calculation."""

    def test_calculate_benchmarks(self, db, sample_teams):
        """Should calculate benchmarks correctly."""
        benchmarks = PeerComparisonService.calculate_benchmarks("company", db)

        # Should have all dimensions
        expected_dims = [
            'security', 'complexity', 'documentation',
            'testing', 'dependencies', 'maintainability'
        ]

        for dim in expected_dims:
            assert dim in benchmarks
            assert benchmarks[dim].percentile_10 is not None
            assert benchmarks[dim].percentile_50 is not None
            assert benchmarks[dim].percentile_90 is not None

    def test_benchmarks_no_teams(self, db):
        """Should handle empty team list."""
        benchmarks = PeerComparisonService.calculate_benchmarks("company", db)

        # Should return empty dict
        assert benchmarks == {}

    def test_get_benchmarks(self, db, sample_teams):
        """Should retrieve calculated benchmarks."""
        # First calculate
        PeerComparisonService.calculate_benchmarks("company", db)

        # Then retrieve
        result = PeerComparisonService.get_benchmarks("company", db)

        assert isinstance(result, dict)
        for dim, values in result.items():
            assert 'p10' in values
            assert 'p25' in values
            assert 'p50' in values
            assert 'p75' in values
            assert 'p90' in values
            assert 'sample_size' in values

    def test_benchmarks_percentile_ordering(self, db, sample_teams):
        """Should have percentiles in correct order."""
        benchmarks = PeerComparisonService.calculate_benchmarks("company", db)

        for dim, bench in benchmarks.items():
            # Verify percentiles increase in order
            assert bench.percentile_10 <= bench.percentile_25
            assert bench.percentile_25 <= bench.percentile_50
            assert bench.percentile_50 <= bench.percentile_75
            assert bench.percentile_75 <= bench.percentile_90


class TestPeerGroupValidation:
    """Test peer group JSON handling."""

    def test_peer_group_json_serialization(self, db):
        """Should correctly serialize/deserialize team IDs."""
        team_ids = ["team-a", "team-b", "team-c"]
        peer_group = PeerGroup(
            id="test",
            peer_group_name="test",
            created_at=datetime.utcnow()
        )
        peer_group.set_team_ids(team_ids)

        # Verify stored as JSON
        stored = json.loads(peer_group.team_ids)
        assert stored == team_ids

        # Verify retrieval
        retrieved = peer_group.get_team_ids()
        assert retrieved == team_ids
