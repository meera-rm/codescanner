"""Caching service for dashboard and analytics data."""
from typing import Optional, Any, Dict, List, Callable
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from api.db.redis_client import (
    redis_client,
    CacheKeys,
    CACHE_TTL_FILTERS,
    CACHE_TTL_SUGGESTIONS,
)
from api.services.search_service import SearchService


class CacheService:
    """Service for caching dashboard and search data."""

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
