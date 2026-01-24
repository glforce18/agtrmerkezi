"""
AGTR Merkezi - CSRF Protection Middleware
Cross-Site Request Forgery koruması
"""

import logging
import secrets

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF koruma middleware'i"""

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    CSRF_COOKIE_NAME = "csrf_token"
    CSRF_HEADER_NAME = "X-CSRF-Token"
    CSRF_FORM_FIELD = "csrf_token"

    def __init__(self, app, exempt_paths: list = None):
        super().__init__(app)
        # SECURITY NOTE: Media upload paths exempt from CSRF but protected by auth middleware
        # Webhook paths must be exempt as they come from external services
        self.exempt_paths = exempt_paths or [
            "/api/auth/login",
            "/api/auth/register",
            "/api/webhooks",  # External webhooks
            "/api/payments/callback",  # Payment gateway callbacks
            "/api/media",  # Protected by auth middleware
            "/api/smart-media",  # Protected by auth middleware
            "/api/admin/media",  # Admin media upload - protected by admin auth
            "/api/notifications",  # Notification actions
            "/api/user/avatar",  # Avatar upload
            "/api/maintenance",  # Maintenance admin - protected by admin auth
            "/api/forum",  # Forum API - protected by JWT auth
            "/api/jackpot",  # Jackpot API - protected by JWT auth
            "/api/tournaments",  # Tournament API - protected by JWT auth
            "/api/clans",  # Clans API - protected by JWT auth
            "/api/leaderboard",  # Leaderboard API - protected by JWT auth
            "/api/errors",  # Error reporting
            "/ws",  # WebSocket connections
        ]

    async def dispatch(self, request: Request, call_next):
        # Safe metodlar için token kontrolü yok
        if request.method in self.SAFE_METHODS:
            response = await call_next(request)
            return await self._set_csrf_cookie(request, response)

        # Exempt paths kontrolü
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)

        # API dışı istekler için tam koruma
        if not request.url.path.startswith("/api/"):
            response = await call_next(request)
            return await self._set_csrf_cookie(request, response)

        # CSRF token doğrulama
        cookie_token = request.cookies.get(self.CSRF_COOKIE_NAME)

        # Header'dan veya form'dan token al
        header_token = request.headers.get(self.CSRF_HEADER_NAME)

        if not header_token:
            # Form verisinden kontrol et (multipart için)
            content_type = request.headers.get("content-type", "")
            if (
                "application/x-www-form-urlencoded" in content_type
                or "multipart/form-data" in content_type
            ):
                try:
                    form = await request.form()
                    header_token = form.get(self.CSRF_FORM_FIELD)
                except Exception as e:
                    logger.warning(f"CSRF form parse error: {e}")

        # Token kontrolü
        if not cookie_token or not header_token or cookie_token != header_token:
            logger.warning(
                f"CSRF token hatasi: {request.url.path} - IP: {request.client.host if request.client else 'unknown'}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token geçersiz veya eksik"
            )

        response = await call_next(request)
        return await self._set_csrf_cookie(request, response)

    async def _set_csrf_cookie(self, request: Request, response: Response) -> Response:
        """CSRF token cookie'si oluştur veya yenile"""
        if not request.cookies.get(self.CSRF_COOKIE_NAME):
            token = secrets.token_urlsafe(32)
            response.set_cookie(
                key=self.CSRF_COOKIE_NAME,
                value=token,
                httponly=False,  # JavaScript'ten okunabilmeli
                samesite="strict",
                secure=True,
                path="/",  # Tum site icin gecerli
                max_age=86400,  # 24 saat
            )
        return response


def generate_csrf_token() -> str:
    """Yeni CSRF token oluştur"""
    return secrets.token_urlsafe(32)


def get_csrf_token(request: Request) -> str:
    """Request'ten CSRF token al veya yeni oluştur"""
    token = request.cookies.get("csrf_token")
    if not token:
        token = generate_csrf_token()
    return token
