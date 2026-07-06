"""Redis client configuration and connection pool."""
import redis
import os
from typing import Optional, Any
import json

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'

# Cache TTLs (in seconds)
CACHE_TTL_SUMMARY = 300  # 5 minutes
CACHE_TTL_HISTORY = 600  # 10 minutes
CACHE_TTL_TRENDS = 900  # 15 minutes
CACHE_TTL_FILTERS = 3600  # 1 hour
CACHE_TTL_SUGGESTIONS = 3600  # 1 hour


class RedisClient:
    """Wrapper for Redis operations with automatic connection pooling."""

    _instance = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize Redis connection pool."""
        if not REDIS_ENABLED:
            print("⚠️  Redis disabled - caching will be skipped")
            self._client = None
            return

        try:
            self._client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
            )
            # Test connection
            self._client.ping()
            print(f"✓ Redis connected: {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            print(f"✗ Redis connection failed: {e}")
            print("  Continuing without cache...")
            self._client = None

    def is_available(self) -> bool:
        """Check if Redis is available."""
        if not REDIS_ENABLED or self._client is None:
            return False
        try:
            self._client.ping()
            return True
        except Exception:
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.is_available():
            return None
        try:
            value = self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error ({key}): {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL."""
        if not self.is_available():
            return False
        try:
            self._client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            print(f"Redis set error ({key}): {e}")
            return False

    def delete(self, *keys: str) -> bool:
        """Delete keys from cache."""
        if not self.is_available():
            return False
        try:
            self._client.delete(*keys)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.is_available():
            return 0
        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis delete pattern error ({pattern}): {e}")
            return 0

    def incr(self, key: str, amount: int = 1) -> int:
        """Increment counter value."""
        if not self.is_available():
            return 0
        try:
            return self._client.incrby(key, amount)
        except Exception as e:
            print(f"Redis incr error ({key}): {e}")
            return 0

    def decr(self, key: str, amount: int = 1) -> int:
        """Decrement counter value."""
        if not self.is_available():
            return 0
        try:
            return self._client.decrby(key, amount)
        except Exception as e:
            print(f"Redis decr error ({key}): {e}")
            return 0

    def ttl(self, key: str) -> int:
        """Get TTL of key in seconds."""
        if not self.is_available():
            return -1
        try:
            return self._client.ttl(key)
        except Exception as e:
            print(f"Redis ttl error ({key}): {e}")
            return -1

    def flush_all(self) -> bool:
        """Flush all cache (use with caution!)."""
        if not self.is_available():
            return False
        try:
            self._client.flushdb()
            return True
        except Exception as e:
            print(f"Redis flush error: {e}")
            return False

    def info(self) -> dict:
        """Get Redis info."""
        if not self.is_available():
            return {}
        try:
            return self._client.info()
        except Exception as e:
            print(f"Redis info error: {e}")
            return {}


# Global Redis client instance
redis_client = RedisClient()


# Cache key builders
class CacheKeys:
    """Cache key naming conventions."""

    # Dashboard
    @staticmethod
    def dashboard_summary(days: int = 30) -> str:
        return f"dashboard:summary:{days}d"

    @staticmethod
    def dashboard_history(repository: str = "all", days: int = 30, limit: int = 100) -> str:
        return f"dashboard:history:{repository}:{days}d:{limit}"

    # Search
    @staticmethod
    def search_filters() -> str:
        return "search:filters"

    @staticmethod
    def search_suggestions(field: str, query: str) -> str:
        return f"search:suggestions:{field}:{query}"

    # Trends
    @staticmethod
    def trend_metrics(repository: str) -> str:
        return f"trends:{repository}"

    # Repository Stats
    @staticmethod
    def repo_stats(repository: str, days: int = 30) -> str:
        return f"repo:stats:{repository}:{days}d"

    # Cache invalidation patterns
    @staticmethod
    def invalidate_dashboard():
        """Pattern to invalidate all dashboard caches."""
        return "dashboard:*"

    @staticmethod
    def invalidate_trends(repository: str = None):
        """Pattern to invalidate trend caches."""
        if repository:
            return f"trends:{repository}"
        return "trends:*"

    @staticmethod
    def invalidate_search():
        """Pattern to invalidate search caches."""
        return "search:*"

    @staticmethod
    def invalidate_repo_stats(repository: str = None):
        """Pattern to invalidate repo stats caches."""
        if repository:
            return f"repo:stats:{repository}:*"
        return "repo:stats:*"
