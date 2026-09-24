"""Integration tests for advanced analytics API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from api.db.database import SessionLocal, engine, Base
from api.db.models import TeamScore, CAQIHistory, TeamMember


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create all tables in test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create a new database session for each test."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_team(db_session: Session):
    """Create a sample team for testing."""
    team = TeamScore(
        id=str(uuid.uuid4()),
        team_id="test-backend",
        team_name="Backend Team",
        security_score=85.0,
        complexity_score=72.0,
        documentation_score=80.0,
        testing_score=88.0,
        dependencies_score=65.0,
        maintainability_score=78.0,
        overall_caqi=385,
        personality_archetype="Pragmatic Engineer",
        member_count=4,
    )
    db_session.add(team)
    db_session.commit()
    return team


@pytest.fixture
def sample_history(db_session: Session, sample_team: TeamScore):
    """Create historical data for a team."""
    history = []
    for i in range(5):
        record = CAQIHistory(
            id=str(uuid.uuid4()),
            team_id=sample_team.team_id,
            security_score=85.0 - (i * 2),
            complexity_score=72.0 + (i * 1),
            documentation_score=80.0,
            testing_score=88.0,
            dependencies_score=65.0 + (i * 1),
            maintainability_score=78.0 - (i * 0.5),
            overall_caqi=385 - (i * 3),
            recorded_at=datetime.utcnow() - timedelta(days=i * 7),
        )
        history.append(record)
    db_session.add_all(history)
    db_session.commit()
    return history


@pytest.fixture
def sample_members(db_session: Session, sample_team: TeamScore):
    """Create team members."""
    members = [
        TeamMember(
            id=str(uuid.uuid4()),
            team_id=sample_team.team_id,
            developer_id=f"dev-{i}"
        )
        for i in range(3)
    ]
    db_session.add_all(members)
    db_session.commit()
    return members


class TestAdvancedAnalyticsAPI:
    """Test advanced analytics API endpoints."""

    def test_health_endpoint(self):
        """Test health check endpoint."""
        from api.routes.advanced_analytics import router

        # Test that health endpoint exists
        endpoints = [r.path for r in router.routes]
        assert '/api/v1/analytics/health' in endpoints

    def test_get_team_caqi(self, db_session: Session, sample_team: TeamScore):
        """Test CAQI endpoint returns correct data."""
        import asyncio
        from api.routes.advanced_analytics import get_team_caqi

        # Call endpoint directly
        response = asyncio.run(get_team_caqi(
            team_id=sample_team.team_id,
            db=db_session
        ))

        assert response['team_id'] == sample_team.team_id
        assert response['overall_caqi'] == 385
        assert response['dimensions']['security'] == 85.0
        assert response['dimensions']['complexity'] == 72.0

    def test_get_team_trends(self, db_session: Session, sample_team: TeamScore, sample_history: list):
        """Test trends endpoint returns historical data."""
        from api.routes.advanced_analytics import get_team_trends

        response = get_team_trends(
            team_id=sample_team.team_id,
            days=30,
            db=db_session
        )

        assert response['team_id'] == sample_team.team_id
        assert response['period_days'] == 30
        assert 'history' in response
        assert len(response['history']) > 0
        assert response['trend_direction'] in ['improving', 'stable', 'declining']

    def test_get_developers(self, db_session: Session, sample_team: TeamScore, sample_members: list):
        """Test developer contributions endpoint."""
        from api.routes.advanced_analytics import get_developer_contributions

        response = get_developer_contributions(
            team_id=sample_team.team_id,
            days=30,
            page=1,
            per_page=20,
            db=db_session
        )

        assert response['team_id'] == sample_team.team_id
        assert response['developer_count'] == 3
        assert 'pagination' in response
        assert response['pagination']['total'] == 3
        assert response['pagination']['page'] == 1

    def test_get_peer_comparison(self, db_session: Session, sample_team: TeamScore):
        """Test peer comparison endpoint."""
        from api.routes.advanced_analytics import get_peer_comparison

        response = get_peer_comparison(
            team_id=sample_team.team_id,
            dimension='security',
            db=db_session
        )

        assert response['team_id'] == sample_team.team_id
        assert response['dimension'] == 'security'
        assert 'team_score' in response
        assert 'peer_percentiles' in response

    def test_get_anomalies(self, db_session: Session, sample_team: TeamScore):
        """Test anomalies endpoint with pagination."""
        from api.routes.advanced_analytics import get_team_anomalies

        response = get_team_anomalies(
            team_id=sample_team.team_id,
            page=1,
            per_page=20,
            db=db_session
        )

        assert response['team_id'] == sample_team.team_id
        assert 'pagination' in response
        assert response['pagination']['page'] == 1
        assert isinstance(response['anomalies'], list)

    def test_get_alerts(self, db_session: Session, sample_team: TeamScore):
        """Test alerts endpoint with pagination."""
        from api.routes.advanced_analytics import get_team_alerts

        response = get_team_alerts(
            team_id=sample_team.team_id,
            page=1,
            per_page=10,
            db=db_session
        )

        assert response['team_id'] == sample_team.team_id
        assert 'pagination' in response
        assert response['pagination']['page'] == 1

    def test_get_benchmarks(self, db_session: Session, sample_team: TeamScore):
        """Test benchmarks endpoint."""
        from api.routes.advanced_analytics import get_team_benchmarks

        response = get_team_benchmarks(
            team_id=sample_team.team_id,
            benchmark_type='company',
            db=db_session
        )

        assert response['team_id'] == sample_team.team_id
        assert response['benchmark_type'] == 'company'
        assert 'dimensions' in response
        assert 'security' in response['dimensions']

    def test_missing_team_404(self, db_session: Session):
        """Test that missing team returns 404."""
        import asyncio
        from fastapi import HTTPException
        from api.routes.advanced_analytics import get_team_caqi

        with pytest.raises(HTTPException) as exc:
            asyncio.run(get_team_caqi(
                team_id="nonexistent-team",
                db=db_session
            ))

        assert exc.value.status_code == 404

    def test_pagination_parameters(self, db_session: Session, sample_team: TeamScore):
        """Test pagination parameters validation."""
        from api.routes.advanced_analytics import get_team_anomalies

        # Valid pagination
        response = get_team_anomalies(
            team_id=sample_team.team_id,
            page=1,
            per_page=20,
            db=db_session
        )
        assert response['pagination']['per_page'] == 20

        # Different page size
        response = get_team_anomalies(
            team_id=sample_team.team_id,
            page=2,
            per_page=50,
            db=db_session
        )
        assert response['pagination']['page'] == 2
        assert response['pagination']['per_page'] == 50
