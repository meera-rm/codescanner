from fastapi import APIRouter, Request
from api.services.metrics_service import MetricsService

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])


@router.get("/summary")
async def get_metrics_summary(req: Request):
    """Get overall metrics summary."""
    key_id = getattr(req.state, "key_id", None)

    service = MetricsService()
    summary = service.get_summary()
    return summary


@router.get("/trends")
async def get_metrics_trends(req: Request, days: int = 30):
    """Get quality trends over time."""
    key_id = getattr(req.state, "key_id", None)

    service = MetricsService()
    trends = service.get_trends(days=days)
    return trends


@router.get("/top-issues")
async def get_top_issues(req: Request, limit: int = 10):
    """Get most common issues."""
    key_id = getattr(req.state, "key_id", None)

    service = MetricsService()
    issues = service.get_top_issues(limit=limit)
    return {"issues": issues}


@router.get("/team-stats")
async def get_team_stats(req: Request):
    """Get team-level statistics."""
    key_id = getattr(req.state, "key_id", None)

    service = MetricsService()
    stats = service.get_team_stats()
    return stats
