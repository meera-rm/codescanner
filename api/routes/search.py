"""Search and filtering routes for scan history."""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.db.models import CIScanHistory
from api.services.search_service import SearchService

router = APIRouter(prefix="/api/v1/search", tags=["search"])


class ScanResult(BaseModel):
    """Scan result in search response."""
    id: str
    repository: str
    branch: str
    platform: str
    status: str
    critical_count: int
    error_count: int
    warning_count: int
    total_findings: int
    files_scanned: int
    created_at: datetime

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Search response with results and pagination."""
    results: List[ScanResult]
    total: int
    limit: int
    offset: int
    has_more: bool


class FilterOptions(BaseModel):
    """Available filter options."""
    repositories: List[str]
    platforms: List[str]
    branches: List[str]
    statuses: List[str]
    critical_range: dict
    error_range: dict


@router.get("/scans", response_model=SearchResponse)
async def search_scans(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Full-text search query"),
    repository: Optional[str] = Query(None, description="Filter by repository"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    status: Optional[str] = Query(None, description="Filter by status (success/failure/warning)"),
    branch: Optional[str] = Query(None, description="Filter by branch"),
    min_critical: Optional[int] = Query(None, description="Minimum critical count"),
    max_critical: Optional[int] = Query(None, description="Maximum critical count"),
    min_errors: Optional[int] = Query(None, description="Minimum error count"),
    max_errors: Optional[int] = Query(None, description="Maximum error count"),
    days: int = Query(30, description="Look back period in days"),
    limit: int = Query(20, description="Results per page"),
    offset: int = Query(0, description="Pagination offset"),
) -> SearchResponse:
    """
    Search scans with flexible filtering.

    **Parameters:**
    - `q`: Full-text search (searches repository, branch, platform)
    - `repository`: Filter by exact repository name
    - `platform`: Filter by platform (github, gitlab, jenkins)
    - `status`: Filter by status (success, failure, warning)
    - `branch`: Filter by git branch
    - `min_critical`/`max_critical`: Filter by critical count range
    - `min_errors`/`max_errors`: Filter by error count range
    - `days`: Look back period (default 30)
    - `limit`: Results per page (default 20)
    - `offset`: Pagination offset (default 0)

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/search/scans?q=my-repo&status=failure&min_critical=1"
    curl "http://localhost:8000/api/v1/search/scans?platform=github&min_errors=5&limit=50"
    ```
    """
    results, total = SearchService.search_scans(
        db,
        query=q,
        repository=repository,
        platform=platform,
        status=status,
        branch=branch,
        min_critical=min_critical,
        max_critical=max_critical,
        min_errors=min_errors,
        max_errors=max_errors,
        days=days,
        limit=limit,
        offset=offset,
    )

    return SearchResponse(
        results=results,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )


@router.get("/filters", response_model=FilterOptions)
async def get_filter_options(
    db: Session = Depends(get_db),
) -> FilterOptions:
    """
    Get available filter options for UI dropdowns.

    **Response:**
    Lists of available repositories, platforms, branches, statuses, and ranges.

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/search/filters"
    ```
    """
    options = SearchService.get_filter_options(db)
    return FilterOptions(**options)


@router.get("/suggestions")
async def get_suggestions(
    db: Session = Depends(get_db),
    q: str = Query(..., description="Search query prefix"),
    field: str = Query("repository", description="Field to search (repository, branch, platform)"),
) -> dict:
    """
    Get autocomplete suggestions for search fields.

    **Parameters:**
    - `q`: Partial search term
    - `field`: Which field to search (repository, branch, platform)

    **Response:**
    List of matching values for autocomplete.

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/search/suggestions?q=my&field=repository"
    ```
    """
    suggestions = SearchService.get_search_suggestions(db, q, field)
    return {
        'field': field,
        'query': q,
        'suggestions': suggestions,
        'count': len(suggestions),
    }
