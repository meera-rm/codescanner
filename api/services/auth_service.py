import uuid
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from api.models.auth import ApiKey
from api.utils.rate_limiter import RateLimiter


class AuthService:
    def __init__(self):
        self.api_keys: Dict[str, Dict] = {}
        self.key_by_token: Dict[str, str] = {}
        self.rate_limiter = RateLimiter()

    def create_api_key(
        self,
        name: str,
        expires_at: Optional[str] = None,
        rate_limit: int = 100,
        scopes: list = None,
    ) -> str:
        if scopes is None:
            scopes = ["scan", "onboarding", "creative-suite"]

        key_id = f"key_{uuid.uuid4().hex[:12]}"
        token = secrets.token_urlsafe(32)

        now = datetime.utcnow().isoformat()
        expires = None
        if expires_at:
            expires = expires_at
        else:
            expires = (datetime.utcnow() + timedelta(days=365)).isoformat()

        api_key = {
            "key_id": key_id,
            "token": token,
            "name": name,
            "created_at": now,
            "expires_at": expires,
            "rate_limit": rate_limit,
            "scopes": scopes,
            "last_used": None,
            "is_active": True,
        }

        self.api_keys[key_id] = api_key
        self.key_by_token[token] = key_id
        self.rate_limiter.set_limit(key_id, rate_limit)

        return token

    def validate_token(self, token: str) -> Optional[str]:
        key_id = self.key_by_token.get(token)
        if not key_id:
            return None

        api_key = self.api_keys.get(key_id)
        if not api_key or not api_key["is_active"]:
            return None

        if api_key["expires_at"]:
            expires = datetime.fromisoformat(api_key["expires_at"])
            if datetime.utcnow() > expires:
                return None

        api_key["last_used"] = datetime.utcnow().isoformat()
        return key_id

    def get_api_key(self, key_id: str) -> Optional[ApiKey]:
        key_data = self.api_keys.get(key_id)
        if not key_data:
            return None

        return ApiKey(
            key_id=key_data["key_id"],
            name=key_data["name"],
            created_at=key_data["created_at"],
            expires_at=key_data["expires_at"],
            rate_limit=key_data["rate_limit"],
            scopes=key_data["scopes"],
            last_used=key_data["last_used"],
            is_active=key_data["is_active"],
        )

    def list_api_keys(self) -> list:
        keys = []
        for key_id, key_data in self.api_keys.items():
            if key_data["is_active"]:
                keys.append(
                    ApiKey(
                        key_id=key_data["key_id"],
                        name=key_data["name"],
                        created_at=key_data["created_at"],
                        expires_at=key_data["expires_at"],
                        rate_limit=key_data["rate_limit"],
                        scopes=key_data["scopes"],
                        last_used=key_data["last_used"],
                        is_active=key_data["is_active"],
                    )
                )
        return keys

    def revoke_api_key(self, key_id: str) -> bool:
        if key_id not in self.api_keys:
            return False
        self.api_keys[key_id]["is_active"] = False
        return True

    def update_api_key(
        self, key_id: str, name: str = None, rate_limit: int = None, scopes: list = None
    ) -> bool:
        if key_id not in self.api_keys:
            return False

        if name:
            self.api_keys[key_id]["name"] = name
        if rate_limit:
            self.api_keys[key_id]["rate_limit"] = rate_limit
            self.rate_limiter.set_limit(key_id, rate_limit)
        if scopes:
            self.api_keys[key_id]["scopes"] = scopes

        return True
