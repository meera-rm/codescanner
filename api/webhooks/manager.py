import json
import hmac
import hashlib
import requests
from datetime import datetime
from typing import Dict, Any, List
from api.db.database import SessionLocal
from api.db.models import Webhook


class WebhookManager:
    """Manage webhook subscriptions and event firing."""

    def __init__(self):
        self.db = SessionLocal()

    def register_webhook(
        self, user_id: str, url: str, event_types: List[str], secret: str = None
    ) -> Dict[str, Any]:
        """Register a new webhook."""
        webhook = Webhook(
            id=f"webhook_{self._generate_id()}",
            user_id=user_id,
            url=url,
            event_types=event_types,
            secret=secret,
            is_active=True,
        )
        self.db.add(webhook)
        self.db.commit()

        return {
            "id": webhook.id,
            "url": webhook.url,
            "event_types": webhook.event_types,
            "created_at": webhook.created_at.isoformat(),
        }

    def unregister_webhook(self, webhook_id: str) -> bool:
        """Disable a webhook."""
        webhook = self.db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if webhook:
            webhook.is_active = False
            self.db.commit()
            return True
        return False

    def fire_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, int]:
        """Fire an event and notify all registered webhooks."""
        webhooks = self.db.query(Webhook).filter(
            Webhook.is_active == True,
            Webhook.event_types.contains(event_type),
        ).all()

        results = {"success": 0, "failed": 0, "skipped": 0}

        for webhook in webhooks:
            try:
                self._send_webhook(webhook, event_type, data)
                results["success"] += 1
            except Exception as e:
                self._handle_webhook_failure(webhook, e)
                results["failed"] += 1

        return results

    def _send_webhook(self, webhook: Webhook, event_type: str, data: Dict[str, Any]):
        """Send webhook notification with signature."""
        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        headers = {"Content-Type": "application/json"}

        if webhook.secret:
            signature = self._create_signature(webhook.secret, json.dumps(payload))
            headers["X-Webhook-Signature"] = signature

        response = requests.post(
            webhook.url,
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code >= 400:
            raise Exception(f"Webhook returned {response.status_code}")

    def _create_signature(self, secret: str, payload: str) -> str:
        """Create HMAC signature for webhook."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _handle_webhook_failure(self, webhook: Webhook, error: Exception):
        """Handle webhook failure with retry logic."""
        webhook.retry_count += 1

        if webhook.retry_count >= webhook.max_retries:
            webhook.is_active = False

        self.db.commit()

    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return uuid.uuid4().hex[:12]

    def __del__(self):
        """Close database connection."""
        if self.db:
            self.db.close()
