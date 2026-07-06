"""Middleware for automatic performance monitoring."""
import time
from fastapi import Request
from api.services.performance_service import performance_service


async def performance_monitoring_middleware(request: Request, call_next):
    """
    Middleware that automatically tracks performance metrics for all requests.

    Measures:
    - Request endpoint and method
    - Response time in milliseconds
    - HTTP status code
    """
    # Record start time
    start_time = time.time()

    # Get request info
    endpoint = request.url.path
    method = request.method

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Extract status code
    status_code = response.status_code

    # Record metric (skip health checks and monitoring endpoints to reduce noise)
    if not endpoint.startswith('/api/v1/performance') and endpoint != '/health':
        performance_service.record_metric(
            endpoint=endpoint,
            method=method,
            duration_ms=duration_ms,
            status_code=status_code,
        )

    return response
