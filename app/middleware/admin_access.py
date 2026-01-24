"""
AGTR Merkezi - Admin Access Control Middleware
Tüm admin sayfaları için merkezi erişim kontrolü
"""

import logging

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import get_current_user_from_token
from app.models.connection import SessionLocal

logger = logging.getLogger(__name__)


class AdminAccessMiddleware(BaseHTTPMiddleware):
    """Admin sayfalarına erişim kontrolü middleware'i

    ÖNEMLI: Admin paneline SADECE superadmin erişebilir.
    Admin ve moderator rolleri kısıtlayıcıdır ve panel erişimi yoktur.
    """

    ADMIN_PATHS = [
        "/admin",
        "/admin/",
        "/admin/users",
        "/admin/servers",
        "/admin/payments",
        "/admin/packages",
        "/admin/announcements",
        "/admin/settings",
        "/admin/theme",
        "/admin/content",
        "/admin/coupons",
        "/admin/forum",
        "/admin/reports",
        "/admin/security",
        "/admin/stats",
        "/admin/media",
        "/admin/pages",
        "/admin/banners",
        "/admin/maintenance",
        "/admin/game-assets",
        "/admin/health",
    ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Admin path kontrolü
        is_admin_path = any(path == p or path.startswith(p + "/") for p in self.ADMIN_PATHS)

        if is_admin_path:
            # Token'dan kullanıcıyı al
            token = request.cookies.get("access_token")

            if not token:
                logger.warning(f"Admin erişim denemesi - Token yok: {path}")
                return RedirectResponse(url="/login?redirect=" + path, status_code=302)

            # Kullanıcıyı doğrula
            db = SessionLocal()
            try:
                user = get_current_user_from_token(db, token)

                if not user:
                    logger.warning(f"Admin erişim denemesi - Geçersiz token: {path}")
                    return RedirectResponse(url="/login?redirect=" + path, status_code=302)

                # SADECE SUPERADMIN admin paneline erişebilir
                if user.role.value != "superadmin":
                    logger.warning(
                        f"Admin panel erişim denemesi - Yetkisiz (sadece superadmin): {user.username} ({user.role.value}) -> {path}"
                    )
                    return RedirectResponse(url="/panel", status_code=302)

            except Exception as e:
                logger.error(f"Admin middleware hatası: {e}")
                return RedirectResponse(url="/login", status_code=302)
            finally:
                db.close()

        return await call_next(request)


def require_admin(func):
    """
    Admin panel gerektiren route'lar için decorator.
    SADECE superadmin erişebilir.
    """

    async def wrapper(request: Request, *args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/login", status_code=302)

        from app.models.connection import SessionLocal

        db = SessionLocal()
        try:
            user = get_current_user_from_token(db, token)
            # Sadece superadmin admin paneline erişebilir
            if not user or user.role.value != "superadmin":
                logger.warning(
                    f"Admin decorator - Yetkisiz erişim: {user.username if user else 'unknown'}"
                )
                return RedirectResponse(url="/panel", status_code=302)
        finally:
            db.close()

        return await func(request, *args, **kwargs)

    return wrapper


def require_superadmin(func):
    """Superadmin gerektiren route'lar için decorator (require_admin ile aynı)"""

    async def wrapper(request: Request, *args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/login", status_code=302)

        from app.models.connection import SessionLocal

        db = SessionLocal()
        try:
            user = get_current_user_from_token(db, token)
            if not user or user.role.value != "superadmin":
                logger.warning(
                    f"Superadmin decorator - Yetkisiz erişim: {user.username if user else 'unknown'}"
                )
                return RedirectResponse(url="/panel", status_code=302)
        finally:
            db.close()

        return await func(request, *args, **kwargs)

    return wrapper


def require_moderator(func):
    """
    Moderasyon yetkisi gerektiren route'lar için decorator.
    moderator, admin ve superadmin erişebilir.
    """

    async def wrapper(request: Request, *args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/login", status_code=302)

        from app.models.connection import SessionLocal

        db = SessionLocal()
        try:
            user = get_current_user_from_token(db, token)
            # Moderator, admin veya superadmin
            if not user or user.role.value not in ["moderator", "admin", "superadmin"]:
                logger.warning(
                    f"Moderator decorator - Yetkisiz erişim: {user.username if user else 'unknown'}"
                )
                return RedirectResponse(url="/panel", status_code=302)
        finally:
            db.close()

        return await func(request, *args, **kwargs)

    return wrapper
