"""
Security Headers & Content Security Policy (CSP)
Production-grade security headers middleware
"""

import logging
import secrets
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class SecurityHeadersConfig:
    """Security headers configuration"""

    # Content Security Policy
    CSP_DIRECTIVES = {
        "default-src": ["'self'"],
        "script-src": [
            "'self'",
            "'unsafe-inline'",  # Vue.js inline scripts (can be removed with nonce)
            "cdn.jsdelivr.net",
            "unpkg.com"
        ],
        "style-src": [
            "'self'",
            "'unsafe-inline'",  # Required for Vue.js
            "cdn.jsdelivr.net",
            "fonts.googleapis.com"
        ],
        "font-src": [
            "'self'",
            "fonts.gstatic.com",
            "cdn.jsdelivr.net"
        ],
        "img-src": [
            "'self'",
            "data:",
            "blob:",
            "https:",  # Allow external images (avatars, etc.)
            "*.steamstatic.com",
            "cdn.discordapp.com",
            "lh3.googleusercontent.com"
        ],
        "media-src": ["'self'", "data:", "blob:"],
        "object-src": ["'none'"],
        "frame-src": [
            "'self'",
            "steamcommunity.com",
            "discord.com",
            "accounts.google.com"
        ],
        "connect-src": [
            "'self'",
            "ws:",
            "wss:",
            "api.steampowered.com",
            "discord.com",
            "accounts.google.com"
        ],
        "worker-src": ["'self'", "blob:"],
        "manifest-src": ["'self'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
        "frame-ancestors": ["'none'"],  # Prevent clickjacking
        "upgrade-insecure-requests": []  # Upgrade HTTP to HTTPS
    }

    @staticmethod
    def build_csp_header(nonce: str = None) -> str:
        """
        Build CSP header string

        Args:
            nonce: Optional nonce for script-src/style-src

        Returns:
            CSP header value
        """
        directives = []

        for directive, sources in SecurityHeadersConfig.CSP_DIRECTIVES.items():
            if not sources:
                # Directive without sources
                directives.append(directive)
            else:
                # Add nonce to script-src and style-src if provided
                if nonce and directive in ["script-src", "style-src"]:
                    sources = sources + [f"'nonce-{nonce}'"]

                sources_str = " ".join(sources)
                directives.append(f"{directive} {sources_str}")

        return "; ".join(directives)

    # Security headers
    SECURITY_HEADERS = {
        # Prevent MIME type sniffing
        "X-Content-Type-Options": "nosniff",

        # Enable XSS protection
        "X-XSS-Protection": "1; mode=block",

        # Prevent clickjacking
        "X-Frame-Options": "DENY",

        # Referrer policy
        "Referrer-Policy": "strict-origin-when-cross-origin",

        # Permissions policy (formerly Feature-Policy)
        "Permissions-Policy": (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        ),

        # HSTS (HTTP Strict Transport Security) - 1 year
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",

        # Expect-CT (Certificate Transparency)
        "Expect-CT": "max-age=86400, enforce",

        # Cross-Origin policies
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "same-origin"
    }


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    """

    def __init__(self, app, enable_csp: bool = True, enable_hsts: bool = True):
        super().__init__(app)
        self.enable_csp = enable_csp
        self.enable_hsts = enable_hsts

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate CSP nonce
        nonce = secrets.token_urlsafe(16) if self.enable_csp else None

        # Store nonce in request state for use in templates
        if nonce:
            request.state.csp_nonce = nonce

        # Call the next middleware/route
        response = await call_next(request)

        # Add security headers
        for header, value in SecurityHeadersConfig.SECURITY_HEADERS.items():
            # Skip HSTS if disabled (e.g., in development)
            if header == "Strict-Transport-Security" and not self.enable_hsts:
                continue

            response.headers[header] = value

        # Add CSP header
        if self.enable_csp:
            csp_header = SecurityHeadersConfig.build_csp_header(nonce)
            response.headers["Content-Security-Policy"] = csp_header

            # Report-Only mode for testing (uncomment to enable)
            # response.headers["Content-Security-Policy-Report-Only"] = csp_header

        # Remove server header (don't expose server info)
        response.headers.pop("Server", None)

        # Add custom server header
        response.headers["X-Powered-By"] = "AGTR Merkezi v7.0"

        # Add rate limit headers if available (set by rate limiter)
        if hasattr(request.state, "rate_limit_headers"):
            for header, value in request.state.rate_limit_headers.items():
                response.headers[header] = value

        return response


class CORSConfig:
    """CORS configuration for API endpoints"""

    # Allowed origins
    ALLOWED_ORIGINS = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "https://agtrmerkezi.com",
        "https://www.agtrmerkezi.com"
    ]

    # Allowed methods
    ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    # Allowed headers
    ALLOWED_HEADERS = [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token"
    ]

    # Exposed headers (client can access)
    EXPOSED_HEADERS = [
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "X-IP-Reputation"
    ]

    # Credentials support
    ALLOW_CREDENTIALS = True

    # Preflight cache (1 hour)
    MAX_AGE = 3600


class CSRFProtection:
    """CSRF protection utilities"""

    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def verify_csrf_token(token: str, session_token: str) -> bool:
        """
        Verify CSRF token

        Args:
            token: Token from request
            session_token: Token from session

        Returns:
            True if valid
        """
        if not token or not session_token:
            return False

        return secrets.compare_digest(token, session_token)


class SecurityUtils:
    """Security utility functions"""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        import os
        import re

        # Remove path separators
        filename = os.path.basename(filename)

        # Remove potentially dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '', filename)

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext

        return filename

    @staticmethod
    def is_safe_redirect_url(url: str, allowed_hosts: list) -> bool:
        """
        Check if redirect URL is safe (prevent open redirect)

        Args:
            url: Redirect URL
            allowed_hosts: List of allowed hosts

        Returns:
            True if safe
        """
        from urllib.parse import urlparse

        # Relative URLs are safe
        if url.startswith('/') and not url.startswith('//'):
            return True

        # Parse URL
        try:
            parsed = urlparse(url)

            # Must have allowed host
            if parsed.netloc in allowed_hosts:
                return True

            # Check if subdomain of allowed host
            for host in allowed_hosts:
                if parsed.netloc.endswith('.' + host):
                    return True

        except Exception as e:
            logger.warning(f"Invalid redirect URL: {url} - {e}")
            return False

        return False

    @staticmethod
    def generate_nonce() -> str:
        """Generate CSP nonce"""
        return secrets.token_urlsafe(16)

    @staticmethod
    def hash_password_client(password: str, salt: str) -> str:
        """
        Client-side password hashing (to prevent plaintext transmission)

        Note: This is in addition to server-side bcrypt hashing

        Args:
            password: User password
            salt: User-specific salt

        Returns:
            Hashed password
        """
        import hashlib

        # PBKDF2 with SHA-256
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations=100000
        ).hex()


class RateLimitHeaders:
    """Rate limit response headers"""

    @staticmethod
    def add_rate_limit_headers(
        response: Response,
        limit: int,
        remaining: int,
        reset_at: int
    ):
        """
        Add rate limit headers to response

        Args:
            response: Response object
            limit: Total limit
            remaining: Remaining requests
            reset_at: Reset time (seconds)
        """
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at)


# Test CSP compliance
def test_csp_compliance():
    """
    Test CSP header generation

    Run this to verify CSP configuration
    """
    csp = SecurityHeadersConfig.build_csp_header(nonce="test123")

    print("=== Content Security Policy ===")
    print(csp)
    print()

    print("=== Security Headers ===")
    for header, value in SecurityHeadersConfig.SECURITY_HEADERS.items():
        print(f"{header}: {value}")
    print()

    print("=== CORS Configuration ===")
    print(f"Allowed Origins: {CORSConfig.ALLOWED_ORIGINS}")
    print(f"Allowed Methods: {CORSConfig.ALLOWED_METHODS}")
    print(f"Allow Credentials: {CORSConfig.ALLOW_CREDENTIALS}")


if __name__ == "__main__":
    test_csp_compliance()
