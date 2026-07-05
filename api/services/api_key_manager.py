"""
API Key Manager - Phase 5.4
Manages API keys and access tokens
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import secrets
import hashlib
from datetime import datetime, timedelta
import time


class KeyStatus(str, Enum):
    """API key status"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class KeyScope(str, Enum):
    """API key permissions"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


@dataclass
class ApiKey:
    """API key record"""
    key_id: str
    name: str
    team_id: str
    key_hash: str  # SHA256 hash of actual key
    scopes: List[KeyScope] = field(default_factory=list)
    status: KeyStatus = KeyStatus.ACTIVE
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    last_used: Optional[float] = None
    last_ip: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if key is valid"""
        if self.status != KeyStatus.ACTIVE:
            return False

        if self.expires_at and time.time() > self.expires_at:
            return False

        return True

    def has_scope(self, scope: KeyScope) -> bool:
        """Check if key has scope"""
        if KeyScope.ADMIN in self.scopes:
            return True
        return scope in self.scopes

    def to_dict(self, include_hash: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "key_id": self.key_id,
            "name": self.name,
            "scopes": [s.value for s in self.scopes],
            "status": self.status.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "last_used": self.last_used,
            "metadata": self.metadata,
        }

        if include_hash:
            data["key_hash"] = self.key_hash

        return data


class ApiKeyManager:
    """Manages API keys for teams"""

    KEY_PREFIX = "sk_"
    KEY_LENGTH = 32

    def __init__(self):
        self.keys: Dict[str, ApiKey] = {}
        self.key_hash_map: Dict[str, str] = {}  # hash -> key_id

    @staticmethod
    def generate_key() -> str:
        """Generate new API key"""
        return ApiKeyManager.KEY_PREFIX + secrets.token_urlsafe(ApiKeyManager.KEY_LENGTH)

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()

    def create_key(
        self,
        team_id: str,
        name: str,
        scopes: List[KeyScope],
        expires_in_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[str, ApiKey]:
        """
        Create new API key

        Returns: (actual_key, key_record)
        """
        key = self.generate_key()
        key_hash = self.hash_key(key)
        key_id = f"key_{secrets.token_hex(8)}"

        expires_at = None
        if expires_in_days:
            expires_at = time.time() + (expires_in_days * 86400)

        api_key = ApiKey(
            key_id=key_id,
            name=name,
            team_id=team_id,
            key_hash=key_hash,
            scopes=scopes,
            expires_at=expires_at,
            metadata=metadata or {}
        )

        self.keys[key_id] = api_key
        self.key_hash_map[key_hash] = key_id

        return key, api_key

    def validate_key(self, key: str) -> tuple[bool, Optional[ApiKey]]:
        """Validate API key"""
        key_hash = self.hash_key(key)

        if key_hash not in self.key_hash_map:
            return False, None

        key_id = self.key_hash_map[key_hash]
        api_key = self.keys.get(key_id)

        if not api_key:
            return False, None

        if not api_key.is_valid():
            return False, None

        return True, api_key

    def get_key(self, key_id: str) -> Optional[ApiKey]:
        """Get key by ID"""
        return self.keys.get(key_id)

    def list_keys(self, team_id: str, include_expired: bool = False) -> List[ApiKey]:
        """List keys for team"""
        keys = [k for k in self.keys.values() if k.team_id == team_id]

        if not include_expired:
            keys = [k for k in keys if k.is_valid()]

        return keys

    def revoke_key(self, key_id: str) -> bool:
        """Revoke API key"""
        if key_id not in self.keys:
            return False

        self.keys[key_id].status = KeyStatus.REVOKED
        return True

    def update_last_used(self, key_id: str, ip: Optional[str] = None) -> None:
        """Update last used timestamp"""
        if key_id in self.keys:
            self.keys[key_id].last_used = time.time()
            if ip:
                self.keys[key_id].last_ip = ip

    def check_scope(
        self,
        key: str,
        required_scope: KeyScope
    ) -> bool:
        """Check if key has required scope"""
        valid, api_key = self.validate_key(key)

        if not valid or not api_key:
            return False

        return api_key.has_scope(required_scope)

    def get_stats(self, key_id: str) -> Dict[str, Any]:
        """Get key statistics"""
        key = self.get_key(key_id)

        if not key:
            return {}

        return {
            "key_id": key_id,
            "name": key.name,
            "created_at": key.created_at,
            "last_used": key.last_used,
            "age_days": (time.time() - key.created_at) / 86400,
            "status": key.status.value,
            "scopes": [s.value for s in key.scopes],
        }

    def export_keys(self, team_id: str) -> str:
        """Export keys as JSON"""
        import json

        keys = self.list_keys(team_id, include_expired=True)
        return json.dumps([k.to_dict() for k in keys], indent=2)


# Global API key manager
_global_api_key_manager = ApiKeyManager()


def get_api_key_manager() -> ApiKeyManager:
    """Get global API key manager"""
    return _global_api_key_manager
