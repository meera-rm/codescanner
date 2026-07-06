"""CI/CD Dashboard routes for scan history and analytics."""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.db.models import CIScanHistory, CITrendMetrics
from api.services.ci_history_service import CIHistoryService

router = APIRouter(prefix="/api/v1/ci-dashboard", tags=["ci-dashboard"])


# Pydantic models for responses
from pydantic import BaseModel


class ScanHistoryItem(BaseModel):
    """Scan history item."""
    id: str
    repository: str
    branch: str
    platform: str
    event_type: str
    status: str
    critical_count: int
    error_count: int
    warning_count: int
    total_findings: int
    files_scanned: int
    duration_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrendMetricsResponse(BaseModel):
    """Trend metrics response."""
    repository: str
    last_scan_at: Optional[datetime] = None
    total_scans: int
    successful_scans: int
    failed_scans: int
    pass_rate: float
    avg_critical_per_scan: float
    avg_error_per_scan: float
    avg_warning_per_scan: float
    avg_scan_duration_ms: int
    critical_trend: list
    error_trend: list
    warning_trend: list
    pass_rate_trend: list
    platforms: dict

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    """Dashboard summary statistics."""
    total_scans: int
    successful_scans: int
    failed_scans: int
    pass_rate: float
    total_critical: int
    total_error: int
    total_warning: int
    repositories: list
    platforms: dict


@router.get("/history", response_model=List[ScanHistoryItem])
async def get_scan_history(
    db: Session = Depends(get_db),
    repository: Optional[str] = Query(None, description="Filter by repository"),
    platform: Optional[str] = Query(None, description="Filter by platform (github, gitlab, jenkins)"),
    status: Optional[str] = Query(None, description="Filter by status (success, failure, warning)"),
    branch: Optional[str] = Query(None, description="Filter by branch"),
    days: int = Query(30, description="Number of days to look back"),
    limit: int = Query(100, description="Maximum results to return"),
) -> List[ScanHistoryItem]:
    """
    Get CI/CD scan history with optional filters.

    **Parameters:**
    - `repository`: Filter by repository path/name
    - `platform`: Filter by CI platform
    - `status`: Filter by scan status
    - `branch`: Filter by git branch
    - `days`: Look back period (default: 30 days)
    - `limit`: Maximum results (default: 100)

    **Response:**
    Array of scan history records sorted by most recent first.

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/ci-dashboard/history?repository=my-repo&days=7"
    ```
    """
    scans = CIHistoryService.get_scan_history(
        db,
        repository=repository,
        platform=platform,
        status=status,
        branch=branch,
        days=days,
        limit=limit,
    )
    return scans


@router.get("/trends/{repository}", response_model=TrendMetricsResponse)
async def get_repository_trends(
    repository: str,
    db: Session = Depends(get_db),
) -> TrendMetricsResponse:
    """
    Get trend metrics for a specific repository.

    **Returns:**
    - Pass rate (0-100)
    - Critical/error/warning trends over time
    - Platform breakdown
    - Average metrics per scan

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/ci-dashboard/trends/my-repo"
    ```
    """
    metrics = CIHistoryService.get_trend_metrics(db, repository)

    if not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"No metrics found for repository: {repository}"
        )

    return metrics


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    days: int = Query(30, description="Number of days to summarize"),
) -> DashboardSummary:
    """
    Get overall dashboard summary for all repositories.

    **Returns:**
    - Total scans and pass rate
    - Critical/error/warning counts
    - Per-repository statistics
    - Platform usage breakdown

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/ci-dashboard/summary?days=7"
    ```
    """
    summary = CIHistoryService.get_dashboard_summary(db, days=days)
    return DashboardSummary(**summary)


@router.get("/repository-stats/{repository}")
async def get_repository_stats(
    repository: str,
    db: Session = Depends(get_db),
    days: int = Query(30, description="Number of days to include"),
) -> dict:
    """
    Get detailed statistics for a specific repository.

    **Returns:**
    - Last scan timestamp and status
    - Total scans in period
    - Critical issues trend
    - Success/failure breakdown by platform
    - Average scan duration

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/ci-dashboard/repository-stats/my-repo"
    ```
    """
    cutoff = datetime.utcnow() - timedelta(days=days)
    scans = db.query(CIScanHistory).filter(
        CIScanHistory.repository == repository,
        CIScanHistory.created_at >= cutoff,
    ).all()

    if not scans:
        raise HTTPException(
            status_code=404,
            detail=f"No scans found for repository: {repository}"
        )

    # Platform breakdown
    by_platform = {}
    for scan in scans:
        if scan.platform not in by_platform:
            by_platform[scan.platform] = {'success': 0, 'failure': 0, 'warning': 0}
        by_platform[scan.platform][scan.status] = by_platform[scan.platform].get(scan.status, 0) + 1

    # Status breakdown
    success_count = len([s for s in scans if s.status == 'success'])
    failure_count = len([s for s in scans if s.status == 'failure'])
    warning_count = len([s for s in scans if s.status == 'warning'])

    return {
        'repository': repository,
        'total_scans': len(scans),
        'successful': success_count,
        'failed': failure_count,
        'warnings': warning_count,
        'pass_rate': (success_count / len(scans) * 100) if scans else 0,
        'last_scan': {
            'timestamp': scans[0].created_at,
            'status': scans[0].status,
            'critical': scans[0].critical_count,
            'errors': scans[0].error_count,
        },
        'total_issues': {
            'critical': sum(s.critical_count for s in scans),
            'error': sum(s.error_count for s in scans),
            'warning': sum(s.warning_count for s in scans),
        },
        'avg_duration_ms': int(sum(s.duration_ms or 0 for s in scans) / len(scans)),
        'by_platform': by_platform,
        'languages': {
            'python': sum(s.languages.get('python', 0) for s in scans),
            'javascript': sum(s.languages.get('javascript', 0) for s in scans),
            'sql': sum(s.languages.get('sql', 0) for s in scans),
        },
    }


@router.get("/latest-scans")
async def get_latest_scans(
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Number of scans to return"),
) -> List[dict]:
    """
    Get the latest scans across all repositories.

    **Returns:**
    Most recent scans, useful for activity feed.

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/ci-dashboard/latest-scans?limit=5"
    ```
    """
    scans = db.query(CIScanHistory).order_by(
        CIScanHistory.created_at.desc()
    ).limit(limit).all()

    return [
        {
            'id': s.id,
            'repository': s.repository,
            'branch': s.branch,
            'platform': s.platform,
            'status': s.status,
            'critical': s.critical_count,
            'errors': s.error_count,
            'timestamp': s.created_at,
        }
        for s in scans
    ]


@router.post("/record-scan")
async def record_scan(
    db: Session = Depends(get_db),
    repository: str = Query(..., description="Repository path/name"),
    branch: str = Query("main", description="Branch name"),
    platform: str = Query(..., description="CI platform"),
    event_type: str = Query(..., description="Event type (push, pull_request, schedule)"),
    status: str = Query(..., description="Scan status"),
    critical_count: int = Query(0),
    error_count: int = Query(0),
    warning_count: int = Query(0),
    info_count: int = Query(0),
    files_scanned: int = Query(0),
    duration_ms: int = Query(0),
) -> dict:
    """
    Record a new CI scan execution in dashboard.

    This endpoint is called by the CI scan API to track results.

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/ci-dashboard/record-scan" \\
      -d "repository=my-repo&branch=main&platform=github&event_type=push&status=success&critical_count=0&error_count=2&warning_count=15&files_scanned=150&duration_ms=5000"
    ```
    """
    scan = CIHistoryService.record_scan(
        db,
        repository=repository,
        branch=branch,
        platform=platform,
        event_type=event_type,
        status=status,
        critical_count=critical_count,
        error_count=error_count,
        warning_count=warning_count,
        info_count=info_count,
        files_scanned=files_scanned,
        languages={},
        duration_ms=duration_ms,
    )

    return {
        'id': scan.id,
        'status': 'recorded',
        'message': f"Scan recorded for {repository} on {platform}",
    }


@router.delete("/cleanup-old-scans")
async def cleanup_old_scans(
    db: Session = Depends(get_db),
    days: int = Query(90, description="Delete scans older than N days"),
) -> dict:
    """
    Delete scan history older than specified number of days.

    **Warning:** This operation is irreversible.

    **Example:**
    ```bash
    curl -X DELETE "http://localhost:8000/api/v1/ci-dashboard/cleanup-old-scans?days=90"
    ```
    """
    count = CIHistoryService.delete_old_scans(db, days=days)
    return {
        'deleted': count,
        'message': f"Deleted {count} scans older than {days} days",
    }
