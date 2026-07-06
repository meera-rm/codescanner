"""Cache management API routes."""
from fastapi import APIRouter
from api.services.cache_service import CacheService
from api.db.redis_client import redis_client

router = APIRouter(prefix="/api/v1/cache", tags=["cache"])


@router.get("/stats")
async def get_cache_stats() -> dict:
    """
    Get cache (Redis) statistics.

    **Response:**
    - `status`: "available", "disabled", or "error"
    - `used_memory`: Redis memory usage (human readable)
    - `connected_clients`: Number of active connections
    - `keys_total`: Total number of cached keys
    - `expires_keys`: Keys with TTL
    - `uptime_seconds`: Redis uptime

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/cache/stats"
    ```
    """
    return CacheService.get_cache_stats()


@router.post("/clear")
async def clear_cache(
    scope: str = "all",
) -> dict:
    """
    Clear cache selectively or completely.

    **Parameters:**
    - `scope`: "all" (everything), "dashboard", "search", "trends"

    **WARNING:** Clearing cache will cause next requests to take longer.

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/cache/clear?scope=dashboard"
    curl -X POST "http://localhost:8000/api/v1/cache/clear?scope=all"
    ```
    """
    if scope == "all":
        success = CacheService.clear_all_cache()
        return {"status": "cleared", "scope": "all", "success": success}

    elif scope == "dashboard":
        count = CacheService.invalidate_dashboard()
        return {"status": "cleared", "scope": "dashboard", "entries_deleted": count}

    elif scope == "search":
        count = CacheService.invalidate_search()
        return {"status": "cleared", "scope": "search", "entries_deleted": count}

    elif scope == "trends":
        count = CacheService.invalidate_trends()
        return {"status": "cleared", "scope": "trends", "entries_deleted": count}

    else:
        return {"status": "error", "message": f"Unknown scope: {scope}"}


@router.get("/info")
async def get_cache_info() -> dict:
    """
    Get detailed cache information.

    **Response:**
    - Redis server version
    - Connected clients
    - Memory stats
    - Keys by database
    - Command stats (if available)

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/cache/info"
    ```
    """
    if not redis_client.is_available():
        return {"status": "unavailable", "message": "Redis is not available"}

    try:
        info = redis_client.info()
        return {
            "status": "available",
            "server": {
                "version": info.get("redis_version"),
                "process_id": info.get("process_id"),
                "uptime_seconds": info.get("uptime_in_seconds"),
            },
            "clients": {
                "connected": info.get("connected_clients"),
                "blocked": info.get("blocked_clients"),
            },
            "memory": {
                "used_bytes": info.get("used_memory"),
                "used_human": info.get("used_memory_human"),
                "peak_bytes": info.get("used_memory_peak"),
                "peak_human": info.get("used_memory_peak_human"),
            },
            "stats": {
                "total_connections_received": info.get("total_connections_received"),
                "total_commands_processed": info.get("total_commands_processed"),
            },
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/health")
async def cache_health_check() -> dict:
    """
    Check if cache (Redis) is healthy.

    **Response:**
    - `healthy`: boolean
    - `message`: Status message
    - `latency_ms`: Ping latency in milliseconds

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/cache/health"
    ```
    """
    import time

    if not redis_client.is_available():
        return {
            "healthy": False,
            "message": "Redis is not available",
            "latency_ms": None,
        }

    try:
        start = time.time()
        redis_client._client.ping()
        latency_ms = (time.time() - start) * 1000

        return {
            "healthy": True,
            "message": "Redis is healthy",
            "latency_ms": round(latency_ms, 2),
        }
    except Exception as e:
        return {
            "healthy": False,
            "message": f"Redis health check failed: {e}",
            "latency_ms": None,
        }
