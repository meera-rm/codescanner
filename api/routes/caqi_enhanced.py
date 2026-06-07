"""REST API endpoints for Path I (CAQI Team Analytics)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.services.team_aggregation_service import TeamAggregationService
from api.services.trend_service import TrendService
from api.services.personality_mapping_service import PersonalityMappingService
from api.models.caqi_models import TeamScore, CAQITrend
from typing import List, Optional

router = APIRouter(prefix="/api/v1/caqi", tags=["caqi"])


# ===== TEAM ENDPOINTS =====

@router.get(
    "/team/{team_id}",
    response_model=TeamScore,
    summary="Get current team CAQI score",
    description="Get the current CAQI score and archetype for a team"
)
async def get_team_caqi(team_id: str, db: Session = Depends(get_db)) -> TeamScore:
    """
    Get current CAQI score for a team.

    Args:
        team_id: Unique team identifier (e.g., "backend-team")

    Returns:
        TeamScore with dimensions, overall CAQI, and archetype

    Raises:
        404: Team not found or no score data
    """
    service = TeamAggregationService(db)
    result = service.aggregate_team_scores(team_id)

    if not result:
        raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found or has no score data")

    return result


@router.get(
    "/team/{team_id}/comparison",
    response_model=List[TeamScore],
    summary="Compare multiple teams",
    description="Get CAQI scores for multiple teams to compare them side-by-side"
)
async def compare_teams(
    team_id: str,
    team_ids: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[TeamScore]:
    """
    Compare CAQI scores across multiple teams.

    Args:
        team_id: First team ID (required)
        team_ids: Comma-separated list of additional team IDs (optional)

    Returns:
        List of TeamScore objects for all requested teams

    Example:
        GET /api/v1/caqi/team/backend-team/comparison?team_ids=frontend-team,data-team
    """
    service = TeamAggregationService(db)
    team_list = [team_id]

    if team_ids:
        team_list.extend([t.strip() for t in team_ids.split(",")])

    results = []
    for tid in team_list:
        result = service.aggregate_team_scores(tid)
        if result:
            results.append(result)

    if not results:
        raise HTTPException(status_code=404, detail="No teams found")

    return results


# ===== TREND ENDPOINTS =====

@router.get(
    "/team/{team_id}/trend",
    response_model=CAQITrend,
    summary="Get team CAQI trend",
    description="Get historical CAQI trend for a team (90-day by default)"
)
async def get_team_trend(
    team_id: str,
    days: int = 90,
    db: Session = Depends(get_db)
) -> CAQITrend:
    """
    Get historical trend for a team.

    Args:
        team_id: Team identifier
        days: How many days back to look (default 90)

    Returns:
        CAQITrend with history entries and trend direction

    Raises:
        404: No trend data found
    """
    service = TrendService(db)
    trend = service.get_trend(team_id, days)

    if not trend:
        raise HTTPException(status_code=404, detail=f"No trend data found for team '{team_id}'")

    return trend


@router.get(
    "/team/{team_id}/monthly/{year}/{month}",
    response_model=dict,
    summary="Get monthly CAQI snapshot",
    description="Get CAQI snapshot for a specific month"
)
async def get_monthly_snapshot(
    team_id: str,
    year: int,
    month: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get CAQI snapshot for a specific month.

    Args:
        team_id: Team identifier
        year: Year (e.g., 2026)
        month: Month (1-12)

    Returns:
        CAQIHistoryEntry for that month

    Raises:
        400: Invalid month
        404: No data for that month
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    service = TrendService(db)
    snapshot = service.get_monthly_snapshot(team_id, year, month)

    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"No data for team '{team_id}' in {year}-{month:02d}"
        )

    return {
        "team_id": team_id,
        "month": f"{year}-{month:02d}",
        "dimensions": snapshot.dimensions.dict(),
        "overall_caqi": snapshot.overall_caqi,
        "recorded_at": snapshot.recorded_at.isoformat()
    }


@router.get(
    "/team/{team_id}/monthly-snapshots",
    response_model=dict,
    summary="Get multiple monthly snapshots",
    description="Get CAQI snapshots for multiple months"
)
async def get_monthly_snapshots(
    team_id: str,
    start_year: int,
    start_month: int,
    num_months: int = 3,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get monthly snapshots across multiple months (for trending).

    Args:
        team_id: Team identifier
        start_year: Starting year (e.g., 2026)
        start_month: Starting month (1-12)
        num_months: How many months to retrieve (default 3)

    Returns:
        List of monthly snapshots with labels

    Example:
        GET /api/v1/caqi/team/backend-team/monthly-snapshots?start_year=2026&start_month=4&num_months=3
        → Returns April, May, June 2026
    """
    service = TrendService(db)
    snapshots = service.get_monthly_snapshots(team_id, start_year, start_month, num_months)

    return {
        "team_id": team_id,
        "snapshots": [
            {
                "month": label,
                "caqi": snapshot.overall_caqi if snapshot else None,
                "dimensions": snapshot.dimensions.dict() if snapshot else None,
                "recorded_at": snapshot.recorded_at.isoformat() if snapshot else None
            }
            for label, snapshot in snapshots
        ]
    }


# ===== PERSONALITY ENDPOINTS =====

@router.get(
    "/archetype/{archetype}",
    response_model=dict,
    summary="Get archetype profile",
    description="Get personality archetype profile and characteristics"
)
async def get_archetype_profile(archetype: str) -> dict:
    """
    Get personality archetype profile and improvement suggestions.

    Args:
        archetype: Archetype name (e.g., "Reckless Optimist")

    Returns:
        Full archetype profile with description, characteristics, strengths, risks

    Raises:
        404: Unknown archetype
    """
    service = PersonalityMappingService()
    profile = service.get_archetype_profile(archetype)

    if not profile or archetype not in service.ARCHETYPES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown archetype: {archetype}. Valid options: {list(service.ARCHETYPES.keys())}"
        )

    return profile


@router.get(
    "/team/{team_id}/suggestions",
    response_model=dict,
    summary="Get improvement suggestions",
    description="Get improvement suggestions based on team's current archetype"
)
async def get_improvement_suggestions(team_id: str, db: Session = Depends(get_db)) -> dict:
    """
    Get improvement suggestions based on team's archetype and current state.

    Args:
        team_id: Team identifier

    Returns:
        Archetype profile with specific improvement suggestions

    Raises:
        404: Team not found
    """
    agg_service = TeamAggregationService(db)
    pers_service = PersonalityMappingService()

    team_score = agg_service.aggregate_team_scores(team_id)
    if not team_score:
        raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found")

    profile = pers_service.get_team_profile_summary(team_score.personality_archetype)
    suggestions = pers_service.suggest_improvements(
        team_score.personality_archetype,
        team_score.dimensions.dict()
    )

    return {
        "team_id": team_id,
        "team_name": team_score.team_name,
        "archetype": team_score.personality_archetype,
        "archetype_profile": profile,
        "suggestions": suggestions,
        "current_dimensions": team_score.dimensions.dict(),
        "overall_caqi": team_score.overall_caqi
    }


# ===== HEALTH CHECK =====

@router.get(
    "/health",
    response_model=dict,
    summary="Health check",
    description="Check if CAQI service is healthy"
)
async def health_check(db: Session = Depends(get_db)) -> dict:
    """
    Health check endpoint for monitoring.

    Returns:
        Status and timestamp
    """
    try:
        # Verify database connectivity
        from datetime import datetime
        db.execute("SELECT 1")

        return {
            "status": "healthy",
            "service": "caqi-enhanced",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
