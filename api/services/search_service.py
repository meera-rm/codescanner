"""Service for searching and filtering scan history."""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from api.db.models import CIScanHistory


class SearchService:
    """Search and filter scan history with flexible queries."""

    @staticmethod
    def search_scans(
        db: Session,
        query: Optional[str] = None,
        repository: Optional[str] = None,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        branch: Optional[str] = None,
        min_critical: Optional[int] = None,
        max_critical: Optional[int] = None,
        min_errors: Optional[int] = None,
        max_errors: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        days: int = 30,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[CIScanHistory], int]:
        """
        Search scans with flexible filtering.

        Returns: (results, total_count)
        """
        query_obj = db.query(CIScanHistory)

        # Text search - searches repository, branch, platform
        if query:
            search_term = f"%{query}%"
            query_obj = query_obj.filter(
                or_(
                    CIScanHistory.repository.ilike(search_term),
                    CIScanHistory.branch.ilike(search_term),
                    CIScanHistory.platform.ilike(search_term),
                )
            )

        # Exact filters
        if repository:
            query_obj = query_obj.filter(CIScanHistory.repository == repository)
        if platform:
            query_obj = query_obj.filter(CIScanHistory.platform == platform)
        if status:
            query_obj = query_obj.filter(CIScanHistory.status == status)
        if branch:
            query_obj = query_obj.filter(CIScanHistory.branch == branch)

        # Range filters
        if min_critical is not None:
            query_obj = query_obj.filter(CIScanHistory.critical_count >= min_critical)
        if max_critical is not None:
            query_obj = query_obj.filter(CIScanHistory.critical_count <= max_critical)
        if min_errors is not None:
            query_obj = query_obj.filter(CIScanHistory.error_count >= min_errors)
        if max_errors is not None:
            query_obj = query_obj.filter(CIScanHistory.error_count <= max_errors)

        # Date range filters
        if date_from:
            query_obj = query_obj.filter(CIScanHistory.created_at >= date_from)
        if date_to:
            query_obj = query_obj.filter(CIScanHistory.created_at <= date_to)
        else:
            # Default: last N days
            cutoff = datetime.utcnow() - timedelta(days=days)
            query_obj = query_obj.filter(CIScanHistory.created_at >= cutoff)

        # Get total count before pagination
        total_count = query_obj.count()

        # Order and paginate
        results = query_obj.order_by(
            CIScanHistory.created_at.desc()
        ).offset(offset).limit(limit).all()

        return results, total_count

    @staticmethod
    def get_filter_options(db: Session) -> dict:
        """Get available filter options (for UI dropdowns)."""
        # Get distinct values
        repositories = db.query(CIScanHistory.repository).distinct().all()
        platforms = db.query(CIScanHistory.platform).distinct().all()
        branches = db.query(CIScanHistory.branch).distinct().all()
        statuses = db.query(CIScanHistory.status).distinct().all()

        return {
            'repositories': sorted([r[0] for r in repositories if r[0]]),
            'platforms': sorted([p[0] for p in platforms if p[0]]),
            'branches': sorted([b[0] for b in branches if b[0]]),
            'statuses': sorted([s[0] for s in statuses if s[0]]),
            'critical_range': {
                'min': 0,
                'max': 10,  # Adjust based on actual data
            },
            'error_range': {
                'min': 0,
                'max': 50,  # Adjust based on actual data
            },
        }

    @staticmethod
    def get_search_suggestions(
        db: Session,
        query: str,
        field: str = 'repository',
    ) -> List[str]:
        """Get autocomplete suggestions based on partial search."""
        search_term = f"{query}%"

        if field == 'repository':
            results = db.query(CIScanHistory.repository).filter(
                CIScanHistory.repository.ilike(search_term)
            ).distinct().limit(10).all()
        elif field == 'branch':
            results = db.query(CIScanHistory.branch).filter(
                CIScanHistory.branch.ilike(search_term)
            ).distinct().limit(10).all()
        elif field == 'platform':
            results = db.query(CIScanHistory.platform).filter(
                CIScanHistory.platform.ilike(search_term)
            ).distinct().limit(10).all()
        else:
            results = []

        return sorted([r[0] for r in results if r[0]])
