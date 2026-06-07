"""REST API routes for advanced analytics - CAQI analysis endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from api.db.database import get_db
from api.db.models import TeamScore, CAQIHistory, TeamMember

router = APIRouter(prefix="/api/v1/analytics", tags=["advanced_analytics"])


@router.get("/teams/{team_id}/caqi", response_model=Dict[str, Any])
async def get_team_caqi(
    team_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current CAQI score and dimensions for a team.

    Returns:
    - team_id: Team identifier
    - overall_caqi: Overall score (0-500)
    - dimensions: Individual dimension scores (0-100 each)
    - calculated_at: Timestamp of last calculation
    """
    if not team_id:
        raise HTTPException(status_code=400, detail="team_id is required")

    team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    return {
        "team_id": team.team_id,
        "overall_caqi": team.overall_caqi or 0,
        "dimensions": {
            "security": team.security_score or 0,
            "complexity": team.complexity_score or 0,
            "documentation": team.documentation_score or 0,
            "testing": team.testing_score or 0,
            "dependencies": team.dependencies_score or 0,
            "maintainability": team.maintainability_score or 0,
        },
        "calculated_at": team.calculated_at.isoformat() if team.calculated_at else datetime.utcnow().isoformat(),
    }


@router.get("/teams/{team_id}/trends", response_model=Dict[str, Any])
async def get_team_trends(
    team_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get CAQI trends for a team over a period.

    Args:
    - days: Number of days to analyze (1-365)

    Returns:
    - team_id: Team identifier
    - period_days: Number of days analyzed
    - trend_direction: "improving", "stable", or "declining"
    - change_percent: Percentage change over period
    - history: List of historical scores
    """
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="days must be between 1 and 365")

    cutoff_date = datetime.utcnow() - timedelta(days=days)
    history = db.query(CAQIHistory).filter(
        CAQIHistory.team_id == team_id,
        CAQIHistory.recorded_at >= cutoff_date
    ).order_by(CAQIHistory.recorded_at).all()

    if not history:
        raise HTTPException(status_code=404, detail=f"No history found for team {team_id}")

    scores = [h.overall_caqi for h in history if h.overall_caqi is not None]
    if len(scores) < 2:
        trend_direction = "stable"
        change_percent = 0.0
    else:
        first_score = scores[0]
        last_score = scores[-1]
        change_percent = ((last_score - first_score) / first_score * 100) if first_score != 0 else 0
        if change_percent > 5:
            trend_direction = "improving"
        elif change_percent < -5:
            trend_direction = "declining"
        else:
            trend_direction = "stable"

    return {
        "team_id": team_id,
        "period_days": days,
        "trend_direction": trend_direction,
        "change_percent": round(change_percent, 2),
        "history": [
            {
                "date": h.recorded_at.isoformat(),
                "overall_caqi": h.overall_caqi,
                "dimensions": {
                    "security": h.security_score,
                    "complexity": h.complexity_score,
                    "documentation": h.documentation_score,
                    "testing": h.testing_score,
                    "dependencies": h.dependencies_score,
                    "maintainability": h.maintainability_score,
                }
            }
            for h in history
        ],
    }


@router.get("/teams/{team_id}/anomalies", response_model=Dict[str, Any])
async def get_team_anomalies(
    team_id: str,
    reviewed: Optional[bool] = None,
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detected anomalies for a team.

    Args:
    - reviewed: Filter by review status (True/False/None for all)
    - severity: Filter by severity (low, medium, high, critical)

    Returns:
    - team_id: Team identifier
    - anomaly_count: Number of anomalies found
    - unreviewed_count: Number of unreviewed anomalies
    - anomalies: List of anomaly records
    """
    team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    # TODO: Implement Anomaly model and queries once anomaly detection engine is built
    # For now return empty results with pagination metadata
    offset = (page - 1) * per_page

    return {
        "team_id": team_id,
        "anomaly_count": 0,
        "unreviewed_count": 0,
        "anomalies": [],
        "pagination": {
            "total": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0,
        }
    }


@router.get("/teams/{team_id}/developers", response_model=Dict[str, Any])
async def get_developer_contributions(
    team_id: str,
    days: int = Query(30, ge=1, le=365),
    dimension: Optional[str] = Query(None, regex="^(security|complexity|documentation|testing|dependencies|maintainability)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get developer contribution breakdown for a team.

    Args:
    - days: Analysis period (1-365)
    - dimension: Focus on specific dimension (optional)

    Returns:
    - team_id: Team identifier
    - period_days: Period analyzed
    - developer_count: Number of developers
    - contributions: List of developer contributions sorted by impact
    """
    team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

    offset = (page - 1) * per_page
    paginated_members = members[offset:offset + per_page]

    return {
        "team_id": team_id,
        "period_days": days,
        "developer_count": len(members),
        "contributions": [
            {
                "developerId": member.developer_id,
                "impact_score": 0,  # TODO: Calculate based on commit history
                "contributions_by_dimension": {
                    "security": 0,
                    "complexity": 0,
                    "documentation": 0,
                    "testing": 0,
                    "dependencies": 0,
                    "maintainability": 0,
                }
            }
            for member in paginated_members
        ],
        "pagination": {
            "total": len(members),
            "page": page,
            "per_page": per_page,
            "total_pages": (len(members) + per_page - 1) // per_page,
        }
    }


@router.get("/teams/{team_id}/peer-comparison", response_model=Dict[str, Any])
async def get_peer_comparison(
    team_id: str,
    dimension: str = Query(..., regex="^(security|complexity|documentation|testing|dependencies|maintainability)$"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Compare team dimension score to peer group.

    Args:
    - dimension: Dimension to compare (security, complexity, documentation, testing, dependencies, maintainability)

    Returns:
    - team_id: Team identifier
    - dimension: Dimension analyzed
    - team_score: This team's dimension score
    - peer_count: Number of peers in group
    - peer_avg: Average peer dimension score
    - peer_percentiles: Percentile ranking of team vs peers
    """

    team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    peers = db.query(TeamScore).filter(TeamScore.team_id != team_id).all()

    # Get the team's score for the requested dimension
    dimension_map = {
        "security": lambda t: t.security_score,
        "complexity": lambda t: t.complexity_score,
        "documentation": lambda t: t.documentation_score,
        "testing": lambda t: t.testing_score,
        "dependencies": lambda t: t.dependencies_score,
        "maintainability": lambda t: t.maintainability_score,
    }

    get_score = dimension_map[dimension]
    team_score = get_score(team) or 0

    if not peers:
        return {
            "team_id": team_id,
            "dimension": dimension,
            "team_score": team_score,
            "peer_count": 0,
            "peer_avg": team_score,
            "peer_percentiles": {"p10": team_score, "p25": team_score, "p50": team_score, "p75": team_score, "p90": team_score},
        }

    peer_scores = sorted([get_score(p) or 0 for p in peers])
    avg_score = sum(peer_scores) / len(peer_scores) if peer_scores else 0

    # Calculate percentile (what % of peers score less than this team)
    rank = sum(1 for score in peer_scores if score <= team_score)
    percentile = round((rank / len(peer_scores)) * 100, 1) if peer_scores else 50

    return {
        "team_id": team_id,
        "dimension": dimension,
        "team_score": round(team_score, 2),
        "peer_count": len(peers),
        "peer_avg": round(avg_score, 2),
        "peer_percentile": percentile,
        "peer_percentiles": {
            "p10": round(peer_scores[max(0, int(len(peer_scores) * 0.1) - 1)], 2),
            "p25": round(peer_scores[max(0, int(len(peer_scores) * 0.25) - 1)], 2),
            "p50": round(peer_scores[max(0, int(len(peer_scores) * 0.5) - 1)], 2),
            "p75": round(peer_scores[max(0, int(len(peer_scores) * 0.75) - 1)], 2),
            "p90": round(peer_scores[max(0, int(len(peer_scores) * 0.9) - 1)], 2),
        },
    }


@router.get("/teams/{team_id}/alerts", response_model=Dict[str, Any])
async def get_team_alerts(
    team_id: str,
    acknowledged: Optional[bool] = None,
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get alerts for a team.

    Args:
    - acknowledged: Filter by acknowledgment status
    - severity: Filter by severity level
    - page: Page number (starts at 1)
    - per_page: Results per page

    Returns:
    - team_id: Team identifier
    - alert_count: Total alerts
    - unacknowledged_count: Unacknowledged alerts
    - alerts: List of alert records
    - pagination: Pagination metadata
    """
    team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    # TODO: Implement Alert model and queries once alerting engine is built
    return {
        "team_id": team_id,
        "alert_count": 0,
        "unacknowledged_count": 0,
        "alerts": [],
        "pagination": {
            "total": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0,
        }
    }


@router.get("/teams/{team_id}/benchmarks", response_model=Dict[str, Any])
async def get_team_benchmarks(
    team_id: str,
    benchmark_type: str = Query(..., regex="^(company|industry|peer_group)$"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get benchmark comparison for a team.

    Args:
    - benchmark_type: Type of benchmark (company, industry, peer_group)

    Returns:
    - team_id: Team identifier
    - benchmark_type: Type of benchmark
    - dimensions: Percentile breakdown (p10, p25, p50, p75, p90)
    - sample_size: Number of teams in benchmark
    """
    if not benchmark_type:
        raise HTTPException(status_code=400, detail="benchmark_type is required")

    team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    all_teams = db.query(TeamScore).all()
    sample_size = len(all_teams)

    def calculate_percentiles(scores: List[float]):
        if not scores:
            return {"p10": 0, "p25": 0, "p50": 0, "p75": 0, "p90": 0}
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        return {
            "p10": round(sorted_scores[max(0, int(n * 0.1) - 1)], 2),
            "p25": round(sorted_scores[max(0, int(n * 0.25) - 1)], 2),
            "p50": round(sorted_scores[max(0, int(n * 0.5) - 1)], 2),
            "p75": round(sorted_scores[max(0, int(n * 0.75) - 1)], 2),
            "p90": round(sorted_scores[max(0, int(n * 0.9) - 1)], 2),
        }

    return {
        "team_id": team_id,
        "benchmark_type": benchmark_type,
        "dimensions": {
            "security": calculate_percentiles([t.security_score or 0 for t in all_teams]),
            "complexity": calculate_percentiles([t.complexity_score or 0 for t in all_teams]),
            "documentation": calculate_percentiles([t.documentation_score or 0 for t in all_teams]),
            "testing": calculate_percentiles([t.testing_score or 0 for t in all_teams]),
            "dependencies": calculate_percentiles([t.dependencies_score or 0 for t in all_teams]),
            "maintainability": calculate_percentiles([t.maintainability_score or 0 for t in all_teams]),
        },
        "sample_size": sample_size,
    }


@router.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
    - status: "ok" if service is healthy
    - timestamp: Current timestamp
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }
