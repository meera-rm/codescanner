"""
CODEPULSE AI API Service - Phase 1 + Phase 2 + Phase 3.5C
FastAPI application for Creative Suite + Core Scanning + Onboarding + Auth + Iteration

Architecture:
- Models: api/models/ (requests, responses, auth models, iteration models)
- Services: api/services/ (scanner, onboarding, auth, config, rate limiter, iteration)
- Routes: api/routes/ (health, scanner, onboarding, auth, config, creative_suite, iteration)
- Middleware: api/middleware/ (auth validation, rate limiting)
- Tasks: api/tasks/ (background tasks for async iteration jobs)

Phases:
- Phase 1: Creative Suite (Personality, Letter, CAQI) ✅ Complete
- Phase 2: Core Scanning + Onboarding + Authentication ✅ Complete
- Phase 3: Advanced features (AI refactoring, git analysis, webhooks) ✅ Complete
- Phase 3.5A: Agent System ✅ Complete
- Phase 3.5B: Orchestration Service ✅ Complete
- Phase 3.5C: API & Integration 🔄 In Progress
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Set up path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scanner"))
os.chdir(str(project_root))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Auth disabled for local development
from api.routes import health, auth, creative_suite, config, caqi_enhanced, scanner, onboarding, iteration, dashboard, metrics, webhooks, analysis, advanced_analytics, github, jobs, alerts, search, websocket, performance
from api.tasks import job_queue
from api.db.database import engine, Base
from api.middleware.performance_middleware import performance_monitoring_middleware


# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="CODEPULSE AI API",
    description="Unified API for code intelligence analysis (Phase 1 + Phase 2 + Phase 3.5)",
    version="3.5.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS Middleware (allow all for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance monitoring middleware
app.middleware("http")(performance_monitoring_middleware)

# ============================================================================
# Database Initialization
# ============================================================================

Base.metadata.create_all(bind=engine)

# ============================================================================
# Include Route Modules
# ============================================================================

app.include_router(health.router)
app.include_router(creative_suite.router)
app.include_router(auth.router)
app.include_router(caqi_enhanced.router)  # Path I: CAQI Team Analytics
app.include_router(scanner.router)  # Path K: Code Scanner
app.include_router(onboarding.router)  # Path J: Onboarding Profiles
app.include_router(iteration.router)  # Phase 3.5: Iteration Until Clean
app.include_router(dashboard.router)  # Dashboard endpoints
app.include_router(config.router)
app.include_router(metrics.router)  # Metrics & monitoring
app.include_router(webhooks.router)  # Webhook management
app.include_router(analysis.router)  # Code analysis (architecture, git, refactoring)
app.include_router(advanced_analytics.router)  # Path I+1: Advanced Analytics
app.include_router(github.router)  # Phase 12: GitHub Integration
app.include_router(jobs.router)  # Phase 12.4: Job queue management
app.include_router(alerts.router)  # Phase 15.A.1: Alerts & Notifications
app.include_router(search.router)  # Phase 15.A.5: Search & Advanced Filtering
app.include_router(websocket.router)  # Phase 15.A.3: Real-time WebSocket Updates
app.include_router(performance.router)  # Phase 15.A.6: Performance Profiling

# ============================================================================
# Root & Documentation Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root - provides entry point and documentation links."""
    return {
        "message": "CODEPULSE AI API - Code Intelligence Platform",
        "version": "3.5.0",
        "phase": "Phase 1 + Phase 2 + Phase 3.5",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "api_reference": "https://github.com/meera-rm/codescanner",
        "endpoints": {
            "creative_suite": "/api/v1/creative-suite",
            "caqi": "/api/v1/caqi",
            "scanner": "/api/v1/scanner",
            "onboarding": "/api/v1/onboarding",
            "analytics": "/api/v1/analytics",
            "analysis": "/api/v1/analysis",
            "iteration": "/api/v1/iteration",
            "health": "/api/v1/health",
            "auth": "/api/v1/auth",
            "config": "/api/v1/config",
            "metrics": "/api/v1/metrics",
            "webhooks": "/api/v1/webhooks"
        },
        "paths": {
            "g_personality": "/api/v1/creative-suite/analyze",
            "h_letter": "/api/v1/creative-suite/analyze",
            "i_caqi": "/api/v1/caqi/team",
            "k_scanner": "/api/v1/scanner/scan",
            "j_onboarding": "/api/v1/onboarding/profile",
            "i_plus_1_analytics": "/api/v1/analytics"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/docs", response_class=HTMLResponse)
async def swagger_ui():
    """Swagger UI documentation."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CODEPULSE AI - API Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
        <script>
        window.onload = function() {
            SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: '#swagger-ui',
                presets: [
                    window.SwaggerUIBundle.presets.apis,
                    window.SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout"
            })
        }
        </script>
    </body>
    </html>
    """


# ============================================================================
# Startup & Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("🚀 CODEPULSE AI API v3.5.0 - Starting up...")
    print("📝 API Documentation: http://localhost:8000/docs")
    print("🔑 Create API key first: POST /api/v1/keys")
    print("🔄 Start iteration job: POST /api/v1/iteration/fix-until-clean")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("🛑 CODEPULSE AI API - Shutting down...")


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
