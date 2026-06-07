from fastapi import APIRouter
from datetime import datetime
from api.models.responses import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/version")
async def get_version():
    return {"version": "2.0.0", "api_version": "v1"}
