"""Request models for Iteration Until Clean API."""

from pydantic import BaseModel, Field
from typing import Optional


class FixUntilCleanRequest(BaseModel):
    """Request to start iteration until clean job."""

    directory_path: str = Field(
        ..., description="Path to codebase to analyze"
    )
    target_grade: str = Field(
        default="A",
        description="Target grade (A, B-, B, B+, C, etc)",
        pattern="^[A-F][+-]?$"
    )
    max_iterations: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum iterations before stopping"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "directory_path": "/Users/meera/Documents/codescanner",
                "target_grade": "A",
                "max_iterations": 10,
            }
        }


class CancelIterationRequest(BaseModel):
    """Request to cancel a running iteration job."""

    reason: Optional[str] = Field(
        default=None,
        description="Reason for cancellation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reason": "User requested cancellation"
            }
        }
