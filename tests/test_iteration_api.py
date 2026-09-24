"""Tests for Phase 3.5C: Iteration API Routes."""

import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from api.db.database import SessionLocal, Base, engine
from api.db.models import IterationJob, IterationHistory
from api.routes import iteration, health
from api.services.auth_service import AuthService

# Create a minimal test app without circular imports
test_app = FastAPI(title="CODEPULSE AI API Test")
test_app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Create tables
Base.metadata.create_all(bind=engine)

# Register only iteration and health routes
test_app.include_router(health.router)
test_app.include_router(iteration.router)


# ============================================================================
# Setup & Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def setup_db():
    """Create fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI test client."""
    # TestClient expects app as positional argument
    return TestClient(test_app)


@pytest.fixture
def db():
    """Database session."""
    db = SessionLocal()
    yield db
    db.close()


# ============================================================================
# Test POST /api/v1/iteration/fix-until-clean
# ============================================================================

def test_start_fix_until_clean_success(client):
    """Test starting iteration job succeeds."""
    response = client.post(
        "/api/v1/iteration/fix-until-clean",
        json={
            "directory_path": "/test/code",
            "target_grade": "A",
            "max_iterations": 10,
        },
    )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "processing"
    assert data["message"] == "Starting iteration until A..."


def test_start_fix_until_clean_default_grade(client):
    """Test iteration job with default grade."""
    response = client.post(
        "/api/v1/iteration/fix-until-clean",
        json={
            "directory_path": "/test/code",
        },
    )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data


def test_start_fix_until_clean_creates_db_record(client, db):
    """Test that job creates database record."""
    response = client.post(
        "/api/v1/iteration/fix-until-clean",
        json={
            "directory_path": "/test/code",
            "target_grade": "A",
            "max_iterations": 5,
        },
    )

    assert response.status_code == 202
    job_id = response.json()["job_id"]

    # Verify record was created
    job = db.query(IterationJob).filter(IterationJob.id == job_id).first()
    assert job is not None
    assert job.directory_path == "/test/code"
    assert job.target_grade == "A"
    assert job.max_iterations == 5


def test_start_fix_until_clean_invalid_grade(client):
    """Test iteration with invalid grade format."""
    response = client.post(
        "/api/v1/iteration/fix-until-clean",
        json={
            "directory_path": "/test/code",
            "target_grade": "Z",  # Invalid
        },
    )

    assert response.status_code == 422


def test_start_fix_until_clean_max_iterations_too_high(client):
    """Test max_iterations validation."""
    response = client.post(
        "/api/v1/iteration/fix-until-clean",
        json={
            "directory_path": "/test/code",
            "max_iterations": 100,  # Max is 50
        },
    )

    assert response.status_code == 422


# ============================================================================
# Test GET /api/v1/iteration/{job_id}
# ============================================================================

def test_get_iteration_status_success(client, db):
    """Test getting iteration job status."""
    # Create job
    job = IterationJob(
        id="test_job_1",
        directory_path="/test/code",
        target_grade="A",
        max_iterations=10,
        status="processing",
        current_iteration=2,
        current_grade="B-",
    )
    db.add(job)
    db.commit()

    # Get status
    response = client.get("/api/v1/iteration/test_job_1")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test_job_1"
    assert data["status"] == "processing"
    assert data["current_iteration"] == 2
    assert "final_grade" in data or "current_grade" in data


def test_get_iteration_status_not_found(client):
    """Test getting non-existent job."""
    response = client.get("/api/v1/iteration/nonexistent")

    assert response.status_code == 404


def test_get_iteration_status_with_history(client, db):
    """Test getting status with iteration history."""
    # Create job
    job = IterationJob(
        id="test_job_2",
        directory_path="/test/code",
        target_grade="A",
        max_iterations=10,
        status="completed",
        current_iteration=1,
        current_grade="B",
        final_grade="B",
    )
    db.add(job)
    db.flush()

    # Add history record
    history = IterationHistory(
        id="hist_1",
        job_id="test_job_2",
        iteration_number=1,
        grade_before="C",
        grade_after="B",
        issues_fixed=5,
        agent_selected="Agent A",
        fix_description="Extract methods",
        validation_passed=True,
        changes={"complexity_reduction": 60},
    )
    db.add(history)
    db.commit()

    # Get status
    response = client.get("/api/v1/iteration/test_job_2")

    assert response.status_code == 200
    data = response.json()
    assert len(data["history"]) == 1
    assert data["history"][0]["grade_before"] == "C"
    assert data["history"][0]["grade_after"] == "B"


# ============================================================================
# Test GET /api/v1/iteration/{job_id}/progress
# ============================================================================

def test_get_iteration_progress_success(client, db):
    """Test getting lightweight progress update."""
    # Create job
    job = IterationJob(
        id="test_job_3",
        directory_path="/test/code",
        target_grade="A",
        max_iterations=10,
        status="processing",
        current_iteration=3,
        current_grade="B",
    )
    db.add(job)
    db.commit()

    # Get progress
    response = client.get("/api/v1/iteration/test_job_3/progress")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test_job_3"
    assert data["progress_percent"] == 30  # 3/10
    assert "history" not in data  # No history in progress endpoint


# ============================================================================
# Test GET /api/v1/iteration/{job_id}/history
# ============================================================================

def test_get_iteration_history_empty(client, db):
    """Test getting history with no iterations."""
    # Create job with no history
    job = IterationJob(
        id="test_job_4",
        directory_path="/test/code",
        target_grade="A",
        max_iterations=10,
        status="processing",
    )
    db.add(job)
    db.commit()

    # Get history
    response = client.get("/api/v1/iteration/test_job_4/history")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test_job_4"
    assert len(data["iterations"]) == 0
    assert data["summary"]["total_iterations"] == 0


def test_get_iteration_history_with_steps(client, db):
    """Test getting history with multiple iterations."""
    # Create job
    job = IterationJob(
        id="test_job_5",
        directory_path="/test/code",
        target_grade="A",
        max_iterations=10,
        status="completed",
    )
    db.add(job)
    db.flush()

    # Add multiple history records
    for i in range(1, 4):
        history = IterationHistory(
            id=f"hist_{i}",
            job_id="test_job_5",
            iteration_number=i,
            grade_before="C" if i == 1 else "B-",
            grade_after="B-" if i < 3 else "B",
            issues_fixed=5,
            agent_selected="Agent A",
            fix_description=f"Fix {i}",
            validation_passed=True,
            changes={},
        )
        db.add(history)

    db.commit()

    # Get history
    response = client.get("/api/v1/iteration/test_job_5/history")

    assert response.status_code == 200
    data = response.json()
    assert len(data["iterations"]) == 3
    assert data["summary"]["total_iterations"] == 3
    assert data["summary"]["total_issues_fixed"] == 15


# ============================================================================
# Test POST /api/v1/iteration/{job_id}/cancel
# ============================================================================

def test_cancel_iteration_success(client, db):
    """Test cancelling a running job."""
    # Create job
    job = IterationJob(
        id="test_job_6",
        directory_path="/test/code",
        target_grade="A",
        max_iterations=10,
        status="processing",
    )
    db.add(job)
    db.commit()

    # Cancel job
    response = client.post(
        "/api/v1/iteration/test_job_6/cancel",
        json={"reason": "User requested"},
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "cancelled"

    # Verify database updated
    job = db.query(IterationJob).filter(IterationJob.id == "test_job_6").first()
    assert job.status == "cancelled"
    assert job.error_message == "User requested"


def test_cancel_iteration_already_complete(client, db):
    """Test cancelling a completed job (should fail)."""
    # Create completed job
    job = IterationJob(
        id="test_job_7",
        directory_path="/test/code",
        target_grade="A",
        max_iterations=10,
        status="completed",
    )
    db.add(job)
    db.commit()

    # Try to cancel
    response = client.post(
        "/api/v1/iteration/test_job_7/cancel",
        json={"reason": "Test"},
    )

    assert response.status_code == 400


def test_cancel_iteration_not_found(client):
    """Test cancelling non-existent job."""
    response = client.post(
        "/api/v1/iteration/nonexistent/cancel",
        json={"reason": "Test"},
    )

    assert response.status_code == 404


# ============================================================================
# Test DELETE /api/v1/iteration/{job_id}
# ============================================================================

def test_delete_iteration_success(client, db):
    """Test deleting a completed job."""
    # Create job
    job = IterationJob(
        id="test_job_8",
        directory_path="/test/code",
        target_grade="A",
        max_iterations=10,
        status="completed",
    )
    db.add(job)
    db.commit()

    # Delete job
    response = client.delete("/api/v1/iteration/test_job_8")

    assert response.status_code == 204

    # Verify deleted
    job = db.query(IterationJob).filter(IterationJob.id == "test_job_8").first()
    assert job is None


def test_delete_iteration_with_history(client, db):
    """Test deleting job also deletes history."""
    # Create job
    job = IterationJob(
        id="test_job_9",
        directory_path="/test/code",
        target_grade="A",
        max_iterations=10,
        status="failed",
    )
    db.add(job)
    db.flush()

    # Add history
    history = IterationHistory(
        id="hist_1",
        job_id="test_job_9",
        iteration_number=1,
        grade_before="C",
        grade_after="B",
        issues_fixed=5,
        agent_selected="Agent A",
        fix_description="Test",
        validation_passed=True,
    )
    db.add(history)
    db.commit()

    # Delete job
    response = client.delete("/api/v1/iteration/test_job_9")

    assert response.status_code == 204

    # Verify both deleted
    job = db.query(IterationJob).filter(IterationJob.id == "test_job_9").first()
    assert job is None
    history = db.query(IterationHistory).filter(
        IterationHistory.job_id == "test_job_9"
    ).first()
    assert history is None


def test_delete_iteration_processing_fails(client, db):
    """Test deleting a processing job (should fail)."""
    # Create processing job
    job = IterationJob(
        id="test_job_10",
        directory_path="/test/code",
        target_grade="A",
        max_iterations=10,
        status="processing",
    )
    db.add(job)
    db.commit()

    # Try to delete
    response = client.delete("/api/v1/iteration/test_job_10")

    assert response.status_code == 400

    # Verify not deleted
    job = db.query(IterationJob).filter(IterationJob.id == "test_job_10").first()
    assert job is not None
