"""Caching service for dashboard and analytics data."""
from typing import Optional, Any, Dict, List, Callable
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from api.db.redis_client import (
    redis_client,
    CacheKeys,
    CACHE_TTL_SUMMARY,
    CACHE_TTL_HISTORY,
    CACHE_TTL_TRENDS,
    CACHE_TTL_FILTERS,
    CACHE_TTL_SUGGESTIONS,
)
from api.services.ci_history_service import CIHistoryService
from api.services.search_service import SearchService


class CacheService:
    """Service for caching dashboard and search data."""

    @staticmethod
    def get_dashboard_summary(
        db: Session,
        days: int = 30,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Get dashboard summary with caching.

        Returns cached data if available (< 5 min old), otherwise fetches fresh.
        """
        cache_key = CacheKeys.dashboard_summary(days)

        # Try cache first
        if not force_refresh:
            cached = redis_client.get(cache_key)
            if cached:
                cached['_cached'] = True
                cached['_cache_age_ms'] = (
                    CACHE_TTL_SUMMARY * 1000 - (redis_client.ttl(cache_key) * 1000)
                )
                return cached

        # Fetch fresh data
        summary = CIHistoryService.get_dashboard_summary(db, days)
        summary['_cached'] = False

        # Cache it
        redis_client.set(cache_key, summary, CACHE_TTL_SUMMARY)

        return summary

    @staticmethod
    def get_scan_history(
        db: Session,
        repository: Optional[str] = None,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        branch: Optional[str] = None,
        days: int = 30,
        limit: int = 100,
        force_refresh: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get scan history with caching.

        Only caches unfiltered requests to "all" repositories.
        """
        # Only cache all-repo queries
        use_cache = (
            repository is None
            and platform is None
            and status is None
            and branch is None
        )

        if use_cache and not force_refresh:
            cache_key = CacheKeys.dashboard_history("all", days, limit)
            cached = redis_client.get(cache_key)
            if cached:
                return cached

        # Fetch fresh data
        history = CIHistoryService.get_scan_history(
            db,
            repository=repository,
            platform=platform,
            status=status,
            branch=branch,
            days=days,
            limit=limit,
        )

        # Convert to dict for caching
        history_list = [
            {
                'id': h.id,
                'repository': h.repository,
                'branch': h.branch,
                'platform': h.platform,
                'event_type': h.event_type,
                'status': h.status,
                'critical_count': h.critical_count,
                'error_count': h.error_count,
                'warning_count': h.warning_count,
                'total_findings': h.total_findings,
                'files_scanned': h.files_scanned,
                'duration_ms': h.duration_ms,
                'created_at': h.created_at.isoformat() if h.created_at else None,
                'completed_at': h.completed_at.isoformat() if h.completed_at else None,
            }
            for h in history
        ]

        # Cache unfiltered results
        if use_cache:
            cache_key = CacheKeys.dashboard_history("all", days, limit)
            redis_client.set(cache_key, history_list, CACHE_TTL_HISTORY)

        return history_list

    @staticmethod
    def get_trend_metrics(
        db: Session,
        repository: str,
        force_refresh: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Get trend metrics with caching.

        TTL: 15 minutes
        """
        cache_key = CacheKeys.trend_metrics(repository)

        # Try cache
        if not force_refresh:
            cached = redis_client.get(cache_key)
            if cached:
                cached['_cached'] = True
                return cached

        # Fetch fresh data
        metrics = CIHistoryService.get_trend_metrics(db, repository)
        if not metrics:
            return None

        # Convert to dict
        metrics_dict = {
            'repository': metrics.repository,
            'last_scan_at': metrics.last_scan_at.isoformat() if metrics.last_scan_at else None,
            'total_scans': metrics.total_scans,
            'successful_scans': metrics.successful_scans,
            'failed_scans': metrics.failed_scans,
            'pass_rate': metrics.pass_rate,
            'avg_critical_per_scan': metrics.avg_critical_per_scan,
            'avg_error_per_scan': metrics.avg_error_per_scan,
            'avg_warning_per_scan': metrics.avg_warning_per_scan,
            'avg_scan_duration_ms': metrics.avg_scan_duration_ms,
            'critical_trend': metrics.critical_trend,
            'error_trend': metrics.error_trend,
            'warning_trend': metrics.warning_trend,
            'pass_rate_trend': metrics.pass_rate_trend,
            'platforms': metrics.platforms,
            '_cached': False,
        }

        # Cache
        redis_client.set(cache_key, metrics_dict, CACHE_TTL_TRENDS)

        return metrics_dict

    @staticmethod
    def get_filter_options(
        db: Session,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Get search filter options with caching.

        TTL: 1 hour (filters change infrequently)
        """
        cache_key = CacheKeys.search_filters()

        # Try cache
        if not force_refresh:
            cached = redis_client.get(cache_key)
            if cached:
                cached['_cached'] = True
                return cached

        # Fetch fresh data
        options = SearchService.get_filter_options(db)
        options['_cached'] = False

        # Cache
        redis_client.set(cache_key, options, CACHE_TTL_FILTERS)

        return options

    @staticmethod
    def get_search_suggestions(
        db: Session,
        query: str,
        field: str = 'repository',
        force_refresh: bool = False,
    ) -> List[str]:
        """
        Get search suggestions with caching.

        TTL: 1 hour
        """
        cache_key = CacheKeys.search_suggestions(field, query)

        # Try cache
        if not force_refresh:
            cached = redis_client.get(cache_key)
            if cached:
                return cached

        # Fetch fresh data
        suggestions = SearchService.get_search_suggestions(db, query, field)

        # Cache
        redis_client.set(cache_key, suggestions, CACHE_TTL_SUGGESTIONS)

        return suggestions

    @staticmethod
    def invalidate_dashboard():
        """Invalidate all dashboard caches."""
        pattern = CacheKeys.invalidate_dashboard()
        count = redis_client.delete_pattern(pattern)
        print(f"Invalidated {count} dashboard cache entries")
        return count

    @staticmethod
    def invalidate_trends(repository: Optional[str] = None):
        """Invalidate trend caches."""
        pattern = CacheKeys.invalidate_trends(repository)
        count = redis_client.delete_pattern(pattern)
        print(f"Invalidated {count} trend cache entries for {repository or 'all'}")
        return count

    @staticmethod
    def invalidate_search():
        """Invalidate search caches."""
        pattern = CacheKeys.invalidate_search()
        count = redis_client.delete_pattern(pattern)
        print(f"Invalidated {count} search cache entries")
        return count

    @staticmethod
    def invalidate_on_scan(repository: str):
        """
        Invalidate relevant caches when a scan completes.

        Called from CI history service after scan is recorded.
        """
        # Invalidate dashboard (all time periods)
        CacheService.invalidate_dashboard()

        # Invalidate trends for this repository
        CacheService.invalidate_trends(repository)

        # Invalidate search filters (new repos might appear)
        redis_client.delete(CacheKeys.search_filters())

    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """Get cache statistics."""
        if not redis_client.is_available():
            return {'status': 'disabled'}

        try:
            info = redis_client.info()
            return {
                'status': 'available',
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'keys_total': info.get('db0', {}).get('keys', 0),
                'expires_keys': info.get('db0', {}).get('expires', 0),
                'uptime_seconds': info.get('uptime_in_seconds', 0),
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    @staticmethod
    def clear_all_cache() -> bool:
        """Clear all cache (use with caution!)."""
        print("⚠️  Clearing all cache...")
        return redis_client.flush_all()
