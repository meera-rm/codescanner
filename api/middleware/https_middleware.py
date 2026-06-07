"""HTTPS enforcement middleware for production."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse


class HTTPSMiddleware(BaseHTTPMiddleware):
    """Force HTTPS in production, add security headers."""

    async def dispatch(self, request: Request, call_next):
        # Check if running in production
        is_production = request.headers.get("X-Forwarded-Proto") == "https" or request.url.scheme == "https"

        # Redirect HTTP to HTTPS in production
        if not is_production and request.url.scheme == "http":
            # Only redirect GET/HEAD requests to avoid losing data
            if request.method in ["GET", "HEAD"]:
                url = request.url.replace(scheme="https")
                return RedirectResponse(url=url, status_code=301)

        response = await call_next(request)

        # Add security headers
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"  # 1 year
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response
