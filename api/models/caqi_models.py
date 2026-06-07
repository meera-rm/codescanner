"""Pydantic models for Path I (CAQI Team Analytics)."""

from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


class CAQIDimensions(BaseModel):
    """6-dimensional CAQI score breakdown (0-100 each)."""

    security: float
    complexity: float
    documentation: float
    testing: float
    dependencies: float
    maintainability: float

    class Config:
        json_schema_extra = {
            "example": {
                "security": 85,
                "complexity": 72,
                "documentation": 80,
                "testing": 88,
                "dependencies": 65,
                "maintainability": 78
            }
        }


class TeamScore(BaseModel):
    """Aggregated team CAQI score."""

    team_id: str
    team_name: str
    dimensions: CAQIDimensions
    overall_caqi: int  # 0-500
    personality_archetype: str
    member_count: int
    calculated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "backend-team",
                "team_name": "Backend Engineering",
                "dimensions": {
                    "security": 85,
                    "complexity": 72,
                    "documentation": 80,
                    "testing": 88,
                    "dependencies": 65,
                    "maintainability": 78
                },
                "overall_caqi": 380,
                "personality_archetype": "Pragmatic Engineer",
                "member_count": 4,
                "calculated_at": "2026-06-06T14:30:00"
            }
        }


class CAQIHistoryEntry(BaseModel):
    """Point in time for trend tracking."""

    dimensions: CAQIDimensions
    overall_caqi: int
    recorded_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "dimensions": {
                    "security": 85,
                    "complexity": 72,
                    "documentation": 80,
                    "testing": 88,
                    "dependencies": 65,
                    "maintainability": 78
                },
                "overall_caqi": 380,
                "recorded_at": "2026-06-06T14:30:00"
            }
        }


class CAQITrend(BaseModel):
    """Historical trend for one team."""

    team_id: str
    history: List[CAQIHistoryEntry]
    trend_direction: str  # "improving", "stable", "declining"
    change_percent: float

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "backend-team",
                "history": [
                    {
                        "dimensions": {"security": 80, "complexity": 75, "documentation": 75, "testing": 85, "dependencies": 60, "maintainability": 75},
                        "overall_caqi": 365,
                        "recorded_at": "2026-05-06T14:30:00"
                    },
                    {
                        "dimensions": {"security": 82, "complexity": 73, "documentation": 77, "testing": 86, "dependencies": 62, "maintainability": 76},
                        "overall_caqi": 372,
                        "recorded_at": "2026-05-20T14:30:00"
                    },
                    {
                        "dimensions": {"security": 85, "complexity": 72, "documentation": 80, "testing": 88, "dependencies": 65, "maintainability": 78},
                        "overall_caqi": 380,
                        "recorded_at": "2026-06-06T14:30:00"
                    }
                ],
                "trend_direction": "improving",
                "change_percent": 4.1
            }
        }
