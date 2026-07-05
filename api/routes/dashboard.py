from fastapi import APIRouter
from datetime import datetime, timedelta
import random

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/summary",
    summary="Get Dashboard Summary",
    description="Retrieve comprehensive dashboard summary including AI insights, enterprise info, monitoring metrics, and recent activity",
    response_description="Dashboard summary object with all key metrics"
)
async def get_dashboard_summary():
    """
    Get Dashboard Summary

    Returns:
    - **summary**: Main dashboard metrics
      - **ai_insights**: Pattern analysis and complexity metrics
      - **enterprise**: Plan info and API key stats
      - **monitoring**: System health and performance
      - **activity**: Recent analyses and API activity
    - **analytics**: Historical health timeline data
    """
    return {
        "summary": {
            "ai_insights": {
                "total_patterns": 48,
                "avg_complexity": 7.2,
                "improvements_recommended": 12
            },
            "enterprise": {
                "plan": "Pro",
                "active_api_keys": 3,
                "usage_percentage": 72.34
            },
            "monitoring": {
                "health": 98.5,
                "error_rate": 0.1,
                "response_time_ms": 145,
                "active_alerts": 2
            },
            "activity": {
                "recent_analyses": 45,
                "github_prs": 12,
                "ide_plugins": 3
            }
        },
        "analytics": {
            "health_timeline": [
                {"timestamp": "Mon", "health_score": 72, "complexity": 45},
                {"timestamp": "Tue", "health_score": 75, "complexity": 42},
                {"timestamp": "Wed", "health_score": 76, "complexity": 40},
                {"timestamp": "Thu", "health_score": 78, "complexity": 35},
                {"timestamp": "Fri", "health_score": 79, "complexity": 32},
                {"timestamp": "Sat", "health_score": 77, "complexity": 38},
                {"timestamp": "Sun", "health_score": 76, "complexity": 41},
            ]
        }
    }


@router.get(
    "/widgets/ai-insights",
    summary="AI Insights Widget",
    description="Get AI learning insights including pattern analysis, code complexity, and active agents"
)
async def get_ai_insights():
    """
    Get AI Insights Widget Data

    Returns metrics on:
    - **total_patterns**: Number of patterns analyzed
    - **avg_complexity**: Average code complexity score
    - **top_agents**: List of active AI agents analyzing code
    """
    return {
        "data": {
            "total_patterns": 48,
            "avg_complexity": 7.2,
            "top_agents": ["Security Auditor", "Performance Optimizer", "Documentation Generator"]
        }
    }


@router.get(
    "/widgets/system-health",
    summary="System Health Widget",
    description="Get real-time system health metrics including availability, error rates, and response times"
)
async def get_system_health():
    """
    Get System Health Metrics

    Returns:
    - **availability**: System uptime percentage
    - **error_rate**: Percentage of failed requests
    - **response_time**: Average API response time in ms
    - **status**: Overall system health status (healthy/degraded/down)
    """
    return {
        "data": {
            "availability": 99.9,
            "error_rate": 0.1,
            "response_time": 145,
            "status": "healthy"
        }
    }


@router.get(
    "/widgets/alerts",
    summary="Active Alerts Widget",
    description="Get currently active system and code quality alerts"
)
async def get_alerts():
    """
    Get Active Alerts

    Returns array of alerts with:
    - **level**: Alert severity (critical/warning/info)
    - **message**: Alert description
    - **timestamp**: When alert was triggered
    """
    return {
        "data": {
            "alerts": [
                {"level": "critical", "message": "High memory usage detected", "timestamp": "5 mins ago"},
                {"level": "warning", "message": "API response time elevated", "timestamp": "10 mins ago"},
            ]
        }
    }


@router.get(
    "/widgets/activity",
    summary="Recent Activity Widget",
    description="Get recent code analysis, refactoring, and API activity metrics"
)
async def get_activity():
    """
    Get Recent Activity Data

    Returns:
    - **analyses_today**: Number of code analyses today
    - **github_prs**: Active GitHub pull requests analyzed
    - **api_calls**: Total API calls today
    - **errors**: Number of errors encountered
    """
    return {
        "data": {
            "analyses_today": 45,
            "github_prs": 12,
            "api_calls": 523,
            "errors": 2
        }
    }


@router.get(
    "/widgets/usage",
    summary="Plan Usage Widget",
    description="Get current subscription plan usage and limits"
)
async def get_usage():
    """
    Get Plan Usage Data

    Returns:
    - **api_calls**: Current API call count
    - **analyses**: Code analyses performed
    - **storage_mb**: Storage used in MB
    - **limits**: Plan limits and quotas
    """
    return {
        "data": {
            "api_calls": 7234,
            "analyses": 450,
            "storage_mb": 2340,
            "limits": {
                "monthly_analyses": 1000
            }
        }
    }


@router.get(
    "/widgets/quality-trends",
    summary="Code Quality Trends Widget",
    description="Get historical code quality trends and improvements"
)
async def get_quality_trends():
    """
    Get Quality Trends Data

    Returns:
    - **current_score**: Current code quality score (0-100)
    - **previous_score**: Previous period score for comparison
    - **trend**: Trend direction (up/down/stable)
    - **improvement_percentage**: Percentage improvement
    - **issues_resolved**: Number of issues fixed
    """
    return {
        "data": {
            "current_score": 78.5,
            "previous_score": 75.2,
            "trend": "up",
            "improvement_percentage": 4.4,
            "issues_resolved": 12
        }
    }


@router.get(
    "/analytics",
    summary="Analytics Panel Data",
    description="Get comprehensive analytics including request metrics, performance profiling, and ML learning data"
)
async def get_analytics():
    """
    Get Analytics Data

    Returns:
    - **monitoring**: Request and error metrics
    - **performance**: Response time statistics (min/max/p95/p99)
    - **learning**: AI agent learning and improvement metrics
    """
    return {
        "monitoring": {
            "total_requests": 15234,
            "total_errors": 12,
            "error_rate": 0.08,
            "avg_response_time_ms": 145
        },
        "performance": {
            "min_ms": 45,
            "max_ms": 890,
            "avg_ms": 145,
            "p95_ms": 420,
            "p99_ms": 780
        },
        "learning": {
            "total_experiences": 234,
            "avg_improvement": 3.2
        }
    }


@router.get(
    "/security",
    summary="Security Dashboard Data",
    description="Get comprehensive security vulnerability report with severity classification and recommendations"
)
async def get_security():
    """
    Get Security Dashboard Data

    Returns array of security issues with:
    - **type**: Vulnerability type (SQL Injection, XSS, Hardcoded Secret, etc.)
    - **severity**: Severity level (critical/high/medium/low)
    - **message**: Detailed description
    - **file**: Source file path
    - **line**: Line number where issue was found
    - **count**: Number of occurrences

    Severity Levels:
    - CRITICAL: Immediate action required, high impact exploits
    - HIGH: Significant risk, likely to be exploited
    - MEDIUM: Moderate risk, should be addressed soon
    - LOW: Minor risk, best practice violation
    """
    return {
        "issues": [
            {
                "id": "1",
                "type": "SQL Injection",
                "severity": "critical",
                "message": "Unescaped SQL query detected",
                "file": "auth.py",
                "line": 42,
                "count": 2
            },
            {
                "id": "2",
                "type": "Hardcoded Secret",
                "severity": "high",
                "message": "API key hardcoded in source",
                "file": "config.js",
                "line": 15,
                "count": 1
            },
            {
                "id": "3",
                "type": "XSS Vulnerability",
                "severity": "high",
                "message": "Unsanitized user input in HTML",
                "file": "dashboard.tsx",
                "line": 89,
                "count": 3
            },
            {
                "id": "4",
                "type": "Command Injection",
                "severity": "medium",
                "message": "Shell command with user input",
                "file": "utils.py",
                "line": 156,
                "count": 1
            },
            {
                "id": "5",
                "type": "Weak Cryptography",
                "severity": "medium",
                "message": "MD5 hash detected",
                "file": "security.py",
                "line": 78,
                "count": 2
            }
        ]
    }
