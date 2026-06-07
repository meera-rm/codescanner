from fastapi import APIRouter, Request, HTTPException, Depends
from api.models.requests import CreateApiKeyRequest, UpdateApiKeyRequest
from api.models.responses import ApiKeyResponse, ApiKeyListResponse
from api.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1", tags=["auth"])
auth_service = AuthService()


@router.post("/keys", response_model=ApiKeyResponse)
async def create_api_key(request: CreateApiKeyRequest):
    token = auth_service.create_api_key(
        name=request.name,
        expires_at=request.expires_at,
        rate_limit=request.rate_limit,
        scopes=request.scopes,
    )

    key_id = auth_service.key_by_token[token]
    api_key = auth_service.get_api_key(key_id)

    return {
        "key_id": api_key.key_id,
        "name": api_key.name,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "rate_limit": api_key.rate_limit,
        "scopes": api_key.scopes,
    }


@router.get("/keys", response_model=ApiKeyListResponse)
async def list_api_keys():
    keys = auth_service.list_api_keys()
    return {"keys": keys}


@router.get("/keys/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(key_id: str):
    api_key = auth_service.get_api_key(key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return {
        "key_id": api_key.key_id,
        "name": api_key.name,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "rate_limit": api_key.rate_limit,
        "scopes": api_key.scopes,
    }


@router.patch("/keys/{key_id}", response_model=ApiKeyResponse)
async def update_api_key(key_id: str, request: UpdateApiKeyRequest):
    auth_service.update_api_key(
        key_id, name=request.name, rate_limit=request.rate_limit, scopes=request.scopes
    )

    api_key = auth_service.get_api_key(key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return {
        "key_id": api_key.key_id,
        "name": api_key.name,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "rate_limit": api_key.rate_limit,
        "scopes": api_key.scopes,
    }


@router.delete("/keys/{key_id}")
async def revoke_api_key(key_id: str):
    success = auth_service.revoke_api_key(key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")

    return {"message": "API key revoked"}


def get_auth_service():
    return auth_service
