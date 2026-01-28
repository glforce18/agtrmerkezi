"""
AGTR Merkezi - Security Headers Middleware
Modern güvenlik başlıkları ekler
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers ekleyen middleware"""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # X-Frame-Options - Clickjacking koruması
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options - MIME type sniffing engelleme
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection - XSS koruması (eski tarayıcılar için)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy - Referrer bilgisi kontrolü
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy - Tarayıcı özellikleri kontrolü
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=()"
        )

        # Content-Security-Policy (CSP) - SADECE production'da
        # Development'ta JavaScript inline kullanımı için gevşek
        if not request.url.hostname in ["localhost", "127.0.0.1"]:
            # Production CSP - daha sıkı
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
                "font-src 'self' https://fonts.gstatic.com data:",
                "img-src 'self' data: https: http:",
                "connect-src 'self' wss: ws:",
                "base-uri 'self'",
                "form-action 'self'",
            ]
        else:
            # Development CSP - daha gevşek
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https: http:",
                "connect-src 'self' wss: ws: http://localhost:* http://127.0.0.1:*",
            ]

        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Strict-Transport-Security (HSTS) - SADECE HTTPS'de
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
