"""
CODEPULSE AI API Service - Phase 1 + Phase 2 + Phase 3.5C
FastAPI application for Creative Suite + Core Scanning + Onboarding + Auth + Iteration

Architecture:
- Models: api/models/ (requests, responses, auth models, iteration models)
- Services: api/services/ (scanner, onboarding, auth, config, rate limiter, iteration)
- Routes: api/routes/ (health, scanner, onboarding, auth, config, creative_suite, iteration)
- Middleware: api/middleware/ (auth validation, rate limiting)
- Tasks: api/tasks/ (celery tasks for async iteration jobs)

Phases:
- Phase 1: Creative Suite (Personality, Letter, CAQI) ✅ Complete
- Phase 2: Core Scanning + Onboarding + Authentication ✅ Complete
- Phase 3: Advanced features (AI refactoring, git analysis, webhooks) ✅ Complete
- Phase 3.5A: Agent System ✅ Complete
- Phase 3.5B: Orchestration Service ✅ Complete
- Phase 3.5C: API & Integration 🔄 In Progress
"""

import sys
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))

from api.services.auth_service import AuthService
from api.middleware.auth_middleware import AuthMiddleware
from api.routes import health, auth, scanner, onboarding, config, creative_suite, metrics, webhooks, analysis, iteration, caqi_enhanced
from api.db.database import engine, Base


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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Authentication & Authorization
# ============================================================================

auth_service = AuthService()

# Auth Middleware (set to False to disable for testing)
ENABLE_AUTH = True
if ENABLE_AUTH:
    app.add_middleware(AuthMiddleware, auth_service=auth_service)

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
app.include_router(scanner.router)
app.include_router(onboarding.router)
app.include_router(config.router)
app.include_router(metrics.router)
app.include_router(webhooks.router)
app.include_router(analysis.router)
app.include_router(iteration.router)
app.include_router(caqi_enhanced.router)  # Path I: CAQI Team Analytics

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
        "docs": "/docs",
        "openapi": "/openapi.json",
        "api_reference": "https://github.com/meera-ramesh19/codescanner",
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
