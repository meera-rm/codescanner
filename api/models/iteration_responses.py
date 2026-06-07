"""Response models for Iteration Until Clean API."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class IterationStepResponse(BaseModel):
    """Single iteration step in response."""

    iteration_number: int = Field(..., description="Iteration number (1-based)")
    grade_before: str = Field(..., description="Grade before this iteration")
    grade_after: str = Field(..., description="Grade after this iteration")
    issues_fixed: int = Field(..., description="Number of issues fixed")
    agent_selected: str = Field(..., description="Which agent was selected")
    fix_description: str = Field(..., description="Description of fix applied")
    validation_passed: bool = Field(..., description="Did validation pass")
    applied_at: datetime = Field(..., description="When fix was applied")
    changes: Dict[str, Any] = Field(default_factory=dict, description="Detailed changes")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class IterationProgressResponse(BaseModel):
    """Progress update for running iteration job."""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(
        ...,
        description="Job status: processing, completed, failed, cancelled"
    )
    current_iteration: int = Field(..., description="Current iteration number")
    max_iterations: int = Field(..., description="Maximum iterations allowed")
    current_grade: Optional[str] = Field(..., description="Current code grade")
    target_grade: str = Field(..., description="Target grade")
    progress_percent: int = Field(..., description="Progress as percentage (0-100)")
    estimated_remaining: Optional[str] = Field(
        None, description="Estimated time remaining"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "iterate_abc12345",
                "status": "processing",
                "current_iteration": 2,
                "max_iterations": 10,
                "current_grade": "B",
                "target_grade": "A",
                "progress_percent": 20,
                "estimated_remaining": "~5 minutes",
            }
        }


class IterationStatusResponse(BaseModel):
    """Full status of iteration job."""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(
        ...,
        description="Job status: processing, completed, failed, cancelled"
    )
    start_grade: str = Field(..., description="Grade when job started")
    final_grade: str = Field(..., description="Current/final grade")
    grade_improvement: float = Field(..., description="Grade improvement (numeric)")
    iterations_count: int = Field(..., description="Number of iterations completed")
    max_iterations: int = Field(..., description="Maximum iterations allowed")
    current_iteration: int = Field(..., description="Current iteration number")
    target_grade: str = Field(..., description="Target grade")
    progress_percent: int = Field(..., description="Progress as percentage (0-100)")
    history: List[IterationStepResponse] = Field(
        default_factory=list,
        description="History of all iterations"
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Final metrics"
    )
    created_at: datetime = Field(..., description="When job was created")
    started_at: Optional[datetime] = Field(..., description="When job started")
    completed_at: Optional[datetime] = Field(..., description="When job completed")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "job_id": "iterate_abc12345",
                "status": "completed",
                "start_grade": "C",
                "final_grade": "A",
                "grade_improvement": 23,
                "iterations_count": 4,
                "max_iterations": 10,
                "current_iteration": 4,
                "target_grade": "A",
                "progress_percent": 100,
                "history": [],
                "metrics": {
                    "total_iterations": 4,
                    "total_issues_fixed": 23,
                    "complexity_reduction": "28 → 8 (71%)",
                },
                "created_at": "2026-06-06T14:30:00",
                "started_at": "2026-06-06T14:30:05",
                "completed_at": "2026-06-06T14:45:00",
            }
        }


class IterationHistoryResponse(BaseModel):
    """Detailed iteration history."""

    job_id: str = Field(..., description="Unique job identifier")
    iterations: List[IterationStepResponse] = Field(..., description="All iteration steps")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "iterate_abc12345",
                "iterations": [],
                "summary": {
                    "total_iterations": 4,
                    "total_issues_fixed": 23,
                    "agent_a_used": 3,
                    "agent_b_used": 1,
                    "agent_c_used": 0,
                },
            }
        }


class IterationJobStartedResponse(BaseModel):
    """Response when iteration job starts."""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(default="processing", description="Job status")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="When job was created")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "job_id": "iterate_abc12345",
                "status": "processing",
                "message": "Starting iteration until A...",
                "created_at": "2026-06-06T14:30:00",
            }
        }
