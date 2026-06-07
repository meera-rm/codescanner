from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from api.services.auth_service import AuthService
from api.utils.rate_limiter import RateLimiter


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth_service: AuthService):
        super().__init__(app)
        self.auth_service = auth_service
        self.public_routes = ["/api/v1/health", "/api/v1/version", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in self.public_routes:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid API key")

        token = auth_header[7:]

        key_id = self.auth_service.validate_token(token)
        if not key_id:
            raise HTTPException(status_code=401, detail="Invalid or expired API key")

        rate_limiter = self.auth_service.rate_limiter
        if not rate_limiter.is_allowed(key_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(rate_limiter.get_limit(key_id)),
                    "X-RateLimit-Remaining": str(rate_limiter.get_remaining(key_id)),
                    "X-RateLimit-Reset": str(rate_limiter.get_reset_time(key_id)),
                },
            )

        request.state.key_id = key_id
        request.state.api_key = self.auth_service.get_api_key(key_id)

        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(rate_limiter.get_limit(key_id))
        response.headers["X-RateLimit-Remaining"] = str(
            rate_limiter.get_remaining(key_id)
        )
        response.headers["X-RateLimit-Reset"] = str(rate_limiter.get_reset_time(key_id))

        return response
