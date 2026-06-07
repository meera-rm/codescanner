from fastapi import APIRouter, HTTPException
from api.models.requests import ConfigUpdateRequest
from api.models.responses import ConfigResponse
from api.services.config_service import ConfigService

router = APIRouter(prefix="/api/v1/config", tags=["configuration"])
config_service = ConfigService()


@router.get("", response_model=ConfigResponse)
async def get_current_config():
    config = config_service.get_config()
    return config


@router.get("/defaults", response_model=ConfigResponse)
async def get_default_config():
    config = config_service.get_default_config()
    return config


@router.post("", response_model=ConfigResponse)
async def update_config(request: ConfigUpdateRequest):
    update_dict = {}

    if request.ignore_patterns:
        update_dict["ignore_patterns"] = request.ignore_patterns

    if request.languages:
        update_dict["languages"] = request.languages

    if request.rules:
        update_dict["rules"] = request.rules

    if request.thresholds:
        update_dict["thresholds"] = request.thresholds

    success = config_service.update_config(update_dict)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update config")

    return config_service.get_config()


@router.post("/reset")
async def reset_config():
    success = config_service.reset_to_defaults()
    if not success:
        raise HTTPException(status_code=400, detail="Failed to reset config")

    return {"message": "Config reset to defaults", "config": config_service.get_config()}
