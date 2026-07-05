from fastapi import APIRouter
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_dashboard_summary():
    """Get dashboard summary with mock data"""
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


@router.get("/widgets/ai-insights")
async def get_ai_insights():
    """Get AI insights widget data"""
    return {
        "data": {
            "total_patterns": 48,
            "avg_complexity": 7.2,
            "top_agents": ["Security Auditor", "Performance Optimizer", "Documentation Generator"]
        }
    }


@router.get("/widgets/system-health")
async def get_system_health():
    """Get system health widget data"""
    return {
        "data": {
            "availability": 99.9,
            "error_rate": 0.1,
            "response_time": 145,
            "status": "healthy"
        }
    }


@router.get("/widgets/alerts")
async def get_alerts():
    """Get alerts widget data"""
    return {
        "data": {
            "alerts": [
                {"level": "critical", "message": "High memory usage detected", "timestamp": "5 mins ago"},
                {"level": "warning", "message": "API response time elevated", "timestamp": "10 mins ago"},
            ]
        }
    }


@router.get("/widgets/activity")
async def get_activity():
    """Get recent activity widget data"""
    return {
        "data": {
            "analyses_today": 45,
            "github_prs": 12,
            "api_calls": 523,
            "errors": 2
        }
    }


@router.get("/widgets/usage")
async def get_usage():
    """Get plan usage widget data"""
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


@router.get("/widgets/quality-trends")
async def get_quality_trends():
    """Get code quality trends widget data"""
    return {
        "data": {
            "current_score": 78.5,
            "previous_score": 75.2,
            "trend": "up",
            "improvement_percentage": 4.4,
            "issues_resolved": 12
        }
    }


@router.get("/analytics")
async def get_analytics():
    """Get analytics panel data"""
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
