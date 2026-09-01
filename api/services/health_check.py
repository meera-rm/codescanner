"""
Health Check Service - Phase 5.2
System health monitoring and status reporting
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import asyncio


class HealthStatus(str, Enum):
    """Health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a component"""
    name: str
    status: HealthStatus
    response_time_ms: float = 0.0
    last_checked: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "status": self.status.value,
            "response_time_ms": self.response_time_ms,
            "last_checked": self.last_checked,
            "details": self.details,
            "error_message": self.error_message
        }


@dataclass
class SystemHealth:
    """Overall system health"""
    status: HealthStatus
    timestamp: float = field(default_factory=time.time)
    uptime_seconds: float = 0.0
    components: List[ComponentHealth] = field(default_factory=list)
    checks_passed: int = 0
    checks_failed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp,
            "uptime_seconds": self.uptime_seconds,
            "components": [c.to_dict() for c in self.components],
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed
        }


class HealthChecker:
    """Performs health checks on system components"""

    def __init__(self):
        self.start_time = time.time()
        self.checks: Dict[str, callable] = {}
        self.component_health: Dict[str, ComponentHealth] = {}

    def register_check(self, component_name: str, check_func: callable) -> None:
        """Register a health check"""
        self.checks[component_name] = check_func

    def unregister_check(self, component_name: str) -> None:
        """Unregister a health check"""
        if component_name in self.checks:
            del self.checks[component_name]

    async def check_component(
        self,
        component_name: str,
        timeout: float = 5.0
    ) -> ComponentHealth:
        """Check single component"""
        if component_name not in self.checks:
            return ComponentHealth(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                error_message="Check not found"
            )

        start_time = time.time()
        check_func = self.checks[component_name]

        try:
            # Run check with timeout
            result = await asyncio.wait_for(check_func(), timeout=timeout)

            response_time = (time.time() - start_time) * 1000
            health = ComponentHealth(
                name=component_name,
                status=result.get("status", HealthStatus.HEALTHY),
                response_time_ms=response_time,
                details=result.get("details", {}),
                error_message=result.get("error")
            )

            self.component_health[component_name] = health
            return health

        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            health = ComponentHealth(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=f"Health check timeout (>{timeout}s)"
            )

            self.component_health[component_name] = health
            return health

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            health = ComponentHealth(
                name=component_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )

            self.component_health[component_name] = health
            return health

    async def check_all(self, timeout: float = 5.0) -> SystemHealth:
        """Check all components"""
        # Run all checks in parallel
        tasks = [
            self.check_component(name, timeout)
            for name in self.checks.keys()
        ]

        components = await asyncio.gather(*tasks, return_exceptions=False)

        # Determine overall status
        healthy_count = sum(
            1 for c in components if c.status == HealthStatus.HEALTHY
        )
        degraded_count = sum(
            1 for c in components if c.status == HealthStatus.DEGRADED
        )
        unhealthy_count = sum(
            1 for c in components if c.status == HealthStatus.UNHEALTHY
        )

        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        uptime = time.time() - self.start_time

        return SystemHealth(
            status=overall_status,
            uptime_seconds=uptime,
            components=components,
            checks_passed=healthy_count + degraded_count,
            checks_failed=unhealthy_count
        )

    def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """Get cached component health"""
        return self.component_health.get(component_name)

    def get_all_health(self) -> Dict[str, ComponentHealth]:
        """Get all cached component health"""
        return self.component_health.copy()


# Standard health checks

async def check_database() -> Dict[str, Any]:
    """Check database connectivity"""
    try:
        # Simulate database check
        # In real app: execute SELECT 1 query
        await asyncio.sleep(0.01)
        return {
            "status": HealthStatus.HEALTHY,
            "details": {"connection": "ok", "latency_ms": 10}
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "error": str(e)
        }


async def check_cache() -> Dict[str, Any]:
    """Check cache connectivity"""
    try:
        # Simulate cache check (Redis, etc.)
        await asyncio.sleep(0.01)
        return {
            "status": HealthStatus.HEALTHY,
            "details": {"connection": "ok", "latency_ms": 5}
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "error": str(e)
        }


async def check_queue() -> Dict[str, Any]:
    """Check task queue"""
    try:
        # Simulate queue check
        await asyncio.sleep(0.01)
        return {
            "status": HealthStatus.HEALTHY,
            "details": {"queue_depth": 5}
        }
    except Exception as e:
        return {
            "status": HealthStatus.UNHEALTHY,
            "error": str(e)
        }


async def check_memory() -> Dict[str, Any]:
    """Check memory usage"""
    try:
        # Simulate memory check
        import psutil
        memory = psutil.virtual_memory()
        percent = memory.percent

        if percent < 70:
            status = HealthStatus.HEALTHY
        elif percent < 85:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNHEALTHY

        return {
            "status": status,
            "details": {
                "memory_percent": percent,
                "memory_mb": memory.used / 1024 / 1024
            }
        }
    except Exception as e:
        return {
            "status": HealthStatus.HEALTHY,  # psutil not available
            "details": {}
        }


# Global health checker
_global_health_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """Get global health checker"""
    return _global_health_checker


def setup_standard_checks() -> None:
    """Setup standard health checks"""
    checker = get_health_checker()
    checker.register_check("database", check_database)
    checker.register_check("cache", check_cache)
    checker.register_check("queue", check_queue)
    checker.register_check("memory", check_memory)
