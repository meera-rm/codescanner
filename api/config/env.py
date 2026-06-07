"""Environment configuration and validation."""
import os
from typing import Optional


class EnvConfig:
    """Load and validate environment variables."""

    @staticmethod
    def get_required(key: str) -> str:
        """Get required environment variable, raise if missing."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' not set")
        return value

    @staticmethod
    def get_optional(key: str, default: str = "") -> str:
        """Get optional environment variable with default."""
        return os.getenv(key, default)

    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """Get integer environment variable."""
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')


# API Configuration
API_HOST = EnvConfig.get_optional("API_HOST", "0.0.0.0")
API_PORT = EnvConfig.get_int("API_PORT", 8000)
LOG_LEVEL = EnvConfig.get_optional("LOG_LEVEL", "info")
DEBUG = EnvConfig.get_bool("DEBUG", False)

# Database
DATABASE_URL = EnvConfig.get_optional(
    "DATABASE_URL",
    "sqlite:///./codepulse.db"
)

# Security
SECRET_KEY = EnvConfig.get_optional(
    "SECRET_KEY",
    "dev-secret-key-change-in-production"
)

# CORS
CORS_ORIGINS = [
    origin.strip()
    for origin in EnvConfig.get_optional("CORS_ORIGINS", "http://localhost:3000").split(",")
]

# External Services (Optional)
SENTRY_DSN = EnvConfig.get_optional("SENTRY_DSN", "")
DATADOG_API_KEY = EnvConfig.get_optional("DATADOG_API_KEY", "")

# Validate critical configuration
def validate_config():
    """Validate required configuration."""
    errors = []

    if not DATABASE_URL:
        errors.append("DATABASE_URL must be configured")

    if DEBUG and not SECRET_KEY:
        errors.append("SECRET_KEY must be set (especially in production)")

    if not CORS_ORIGINS or CORS_ORIGINS == ['']:
        errors.append("CORS_ORIGINS must be configured")

    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))


# Validate on import
validate_config()
