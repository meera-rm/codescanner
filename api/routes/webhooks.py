from fastapi import APIRouter, Request, HTTPException
from typing import List
from api.webhooks.manager import WebhookManager

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("")
async def register_webhook(
    req: Request,
    url: str,
    event_types: List[str],
    secret: str = None,
):
    """Register a new webhook."""
    key_id = getattr(req.state, "key_id", None)
    if not key_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    manager = WebhookManager()
    result = manager.register_webhook(
        user_id=key_id,
        url=url,
        event_types=event_types,
        secret=secret,
    )
    return result


@router.get("")
async def list_webhooks(req: Request):
    """List webhooks for user."""
    key_id = getattr(req.state, "key_id", None)
    if not key_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    # For now, return empty list
    return {"webhooks": []}


@router.delete("/{webhook_id}")
async def delete_webhook(req: Request, webhook_id: str):
    """Delete a webhook."""
    key_id = getattr(req.state, "key_id", None)
    if not key_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    manager = WebhookManager()
    success = manager.unregister_webhook(webhook_id)

    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {"message": "Webhook deleted"}
