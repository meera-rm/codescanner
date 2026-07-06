"""Performance monitoring and profiling routes."""
from fastapi import APIRouter, Query
from api.services.performance_service import performance_service

router = APIRouter(prefix="/api/v1/performance", tags=["performance"])


@router.get("/summary")
async def get_performance_summary(
    minutes: int = Query(60, description="Time period in minutes"),
):
    """
    Get overall performance summary for the specified time period.

    **Parameters:**
    - `minutes`: Look back period (default: 60)

    **Response includes:**
    - Total requests processed
    - Average response time (mean)
    - Response time percentiles (p50, p95, p99)
    - Min/max response times
    - Error count and error rate

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/performance/summary?minutes=60"
    ```

    **Response:**
    ```json
    {
      "total_requests": 1245,
      "avg_response_time_ms": 145.32,
      "p50_response_time_ms": 98.5,
      "p95_response_time_ms": 450.2,
      "p99_response_time_ms": 1200.5,
      "min_response_time_ms": 5.2,
      "max_response_time_ms": 2456.8,
      "error_count": 12,
      "error_rate_percent": 0.96,
      "time_period_minutes": 60
    }
    ```
    """
    return performance_service.get_summary(minutes=minutes)


@router.get("/endpoints")
async def get_endpoint_stats(
    minutes: int = Query(60, description="Time period in minutes"),
):
    """
    Get performance statistics per endpoint.

    **Parameters:**
    - `minutes`: Look back period (default: 60)

    **Response includes per endpoint:**
    - Request count
    - Average response time
    - Min/max response times
    - Error count and error rate

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/performance/endpoints?minutes=60"
    ```

    **Response:**
    ```json
    {
      "GET /api/v1/ci-dashboard/summary": {
        "request_count": 245,
        "avg_response_time_ms": 12.5,
        "min_response_time_ms": 5.2,
        "max_response_time_ms": 45.8,
        "error_count": 0,
        "error_rate_percent": 0.0
      },
      "GET /api/v1/search/scans": {
        "request_count": 156,
        "avg_response_time_ms": 125.3,
        "min_response_time_ms": 50.2,
        "max_response_time_ms": 450.8,
        "error_count": 2,
        "error_rate_percent": 1.28
      }
    }
    ```
    """
    return performance_service.get_endpoint_stats(minutes=minutes)


@router.get("/slow-endpoints")
async def get_slow_endpoints(
    minutes: int = Query(60, description="Time period in minutes"),
    threshold_ms: int = Query(500, description="Slow threshold in milliseconds"),
    limit: int = Query(10, description="Maximum results"),
):
    """
    Get endpoints with average response time above threshold.

    **Parameters:**
    - `minutes`: Look back period (default: 60)
    - `threshold_ms`: Response time threshold (default: 500ms)
    - `limit`: Maximum endpoints to return (default: 10)

    **Response includes:**
    - Endpoint name
    - Request count
    - Average response time
    - Min/max response times
    - Error count and rate

    **Example:**
    ```bash
    # Find endpoints slower than 500ms
    curl "http://localhost:8000/api/v1/performance/slow-endpoints?threshold_ms=500"

    # Find endpoints slower than 250ms in last 24 hours
    curl "http://localhost:8000/api/v1/performance/slow-endpoints?threshold_ms=250&minutes=1440"
    ```

    **Response:**
    ```json
    [
      {
        "endpoint": "POST /api/v1/ci-dashboard/record-scan",
        "request_count": 45,
        "avg_response_time_ms": 1250.5,
        "min_response_time_ms": 800.2,
        "max_response_time_ms": 2100.8,
        "error_count": 1,
        "error_rate_percent": 2.22
      },
      {
        "endpoint": "GET /api/v1/search/scans",
        "request_count": 156,
        "avg_response_time_ms": 620.3,
        "min_response_time_ms": 450.2,
        "max_response_time_ms": 1200.8,
        "error_count": 2,
        "error_rate_percent": 1.28
      }
    ]
    ```
    """
    return performance_service.get_slow_endpoints(
        minutes=minutes,
        threshold_ms=threshold_ms,
        limit=limit,
    )


@router.get("/errors")
async def get_error_summary(
    minutes: int = Query(60, description="Time period in minutes"),
):
    """
    Get error summary by HTTP status code.

    **Parameters:**
    - `minutes`: Look back period (default: 60)

    **Response includes:**
    - Total requests
    - Total errors
    - Error rate percentage
    - Breakdown by status code

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/performance/errors?minutes=60"
    ```

    **Response:**
    ```json
    {
      "total_requests": 1245,
      "total_errors": 12,
      "error_rate_percent": 0.96,
      "errors_by_status_code": {
        "400": 2,
        "404": 3,
        "500": 7
      }
    }
    ```
    """
    return performance_service.get_error_summary(minutes=minutes)


@router.get("/distribution")
async def get_response_time_distribution(
    minutes: int = Query(60, description="Time period in minutes"),
):
    """
    Get distribution of response times in buckets.

    **Parameters:**
    - `minutes`: Look back period (default: 60)

    **Response includes count of requests in each time bucket:**
    - <100ms
    - <250ms
    - <500ms
    - <1000ms
    - <2500ms
    - >=2500ms

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/performance/distribution?minutes=60"
    ```

    **Response:**
    ```json
    {
      "<100ms": 450,
      "<250ms": 320,
      "<500ms": 280,
      "<1000ms": 150,
      "<2500ms": 40,
      ">=2500ms": 5
    }
    ```

    **Interpretation:**
    - Most requests complete <100ms (450/1245 = 36%)
    - Only 5 requests (0.4%) take >2.5s
    """
    return performance_service.get_response_time_distribution(minutes=minutes)


@router.get("/timeseries")
async def get_time_series(
    minutes: int = Query(60, description="Time period in minutes"),
    bucket_size_minutes: int = Query(5, description="Bucket size in minutes"),
):
    """
    Get response time metrics over time.

    **Parameters:**
    - `minutes`: Look back period (default: 60)
    - `bucket_size_minutes`: Time bucket size (default: 5 minutes)

    **Response includes per time bucket:**
    - Timestamp
    - Request count
    - Average response time
    - P95 response time
    - Max response time

    **Example:**
    ```bash
    # Get data from last hour in 5-minute buckets
    curl "http://localhost:8000/api/v1/performance/timeseries?minutes=60&bucket_size_minutes=5"

    # Get data from last 24 hours in 1-hour buckets
    curl "http://localhost:8000/api/v1/performance/timeseries?minutes=1440&bucket_size_minutes=60"
    ```

    **Response:**
    ```json
    [
      {
        "timestamp": "2026-07-06T12:00:00",
        "request_count": 48,
        "avg_response_time_ms": 120.5,
        "p95_response_time_ms": 350.2,
        "max_response_time_ms": 800.5
      },
      {
        "timestamp": "2026-07-06T12:05:00",
        "request_count": 52,
        "avg_response_time_ms": 135.2,
        "p95_response_time_ms": 420.5,
        "max_response_time_ms": 950.3
      }
    ]
    ```

    **Use cases:**
    - Identify performance degradation over time
    - Spot performance spikes
    - Correlate with deployment times
    - Track improvements after optimization
    """
    return performance_service.get_time_series(
        minutes=minutes,
        bucket_size_minutes=bucket_size_minutes,
    )


@router.get("/recommendations")
async def get_optimization_recommendations(
    minutes: int = Query(60, description="Time period in minutes"),
):
    """
    Get performance optimization recommendations based on collected metrics.

    **Parameters:**
    - `minutes`: Time period to analyze (default: 60)

    **Response includes:**
    - List of identified issues
    - Recommended optimizations
    - Expected impact estimate

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/performance/recommendations?minutes=60"
    ```

    **Response:**
    ```json
    {
      "recommendations": [
        {
          "issue": "High error rate",
          "affected_endpoint": "POST /api/v1/ci-dashboard/record-scan",
          "error_rate_percent": 5.5,
          "recommendation": "Check database connection and query performance",
          "expected_impact": "Reduce errors by 80%"
        },
        {
          "issue": "Slow endpoint",
          "affected_endpoint": "GET /api/v1/search/scans",
          "avg_response_time_ms": 850.2,
          "recommendation": "Add database indexes or enable caching",
          "expected_impact": "Reduce response time from 850ms to <200ms (4.2x speedup)"
        }
      ]
    }
    ```
    """
    summary = performance_service.get_summary(minutes=minutes)
    slow = performance_service.get_slow_endpoints(minutes=minutes, threshold_ms=200, limit=5)
    errors = performance_service.get_error_summary(minutes=minutes)

    recommendations = []

    # Check for high error rate
    if errors['error_rate_percent'] > 2:
        recommendations.append({
            'issue': 'High error rate detected',
            'current_error_rate_percent': errors['error_rate_percent'],
            'recommendation': 'Review application logs and database health',
            'expected_impact': 'Reduce error rate by 50-90%',
        })

    # Check for slow p95
    if summary['p95_response_time_ms'] > 500:
        recommendations.append({
            'issue': 'P95 response time is slow',
            'current_p95_response_time_ms': summary['p95_response_time_ms'],
            'recommendation': 'Enable caching and optimize database queries',
            'expected_impact': f"Reduce P95 from {summary['p95_response_time_ms']}ms to <200ms",
        })

    # Check for slow endpoints
    if slow:
        for endpoint in slow[:3]:
            recommendations.append({
                'issue': 'Slow endpoint detected',
                'endpoint': endpoint['endpoint'],
                'current_avg_response_time_ms': endpoint['avg_response_time_ms'],
                'recommendation': 'Add index, enable caching, or optimize queries',
                'expected_impact': f"Reduce from {endpoint['avg_response_time_ms']}ms to <200ms",
            })

    return {
        'analyzed_period_minutes': minutes,
        'recommendation_count': len(recommendations),
        'recommendations': recommendations,
    }
