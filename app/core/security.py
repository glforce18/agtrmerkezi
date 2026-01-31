"""
AGTR Merkezi - Guvenlik ve Authentication
"""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.connection import (
    get_db,
    redis_delete,
    redis_exists,
    redis_get,
    redis_incr,
    redis_set,
)
from app.models.database import User, UserRole, UserSession, UserStatus

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer(auto_error=False)

# JWT settings
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Sifre hashle"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Sifre dogrula"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Access token olustur"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access", "iat": datetime.utcnow()})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Token decode et"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """Token hashle (veritabaninda saklamak icin)"""
    return hashlib.sha256(token.encode()).hexdigest()


def get_client_ip(request: Request) -> Optional[str]:
    """Safely extract client IP from request with full null checking"""
    if request is None:
        return None
    if request.client is None:
        return None
    if not hasattr(request.client, "host"):
        return None
    return request.client.host


def create_session(db: Session, user_id: int, token: str, request: Request) -> UserSession:
    """Kullanici oturumu olustur"""
    session = UserSession(
        user_id=user_id,
        token_hash=hash_token(token),
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", "")[:500] if request else "",
        expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    db.add(session)
    db.commit()
    return session


def invalidate_session(db: Session, token: str):
    """Oturumu sonlandir"""
    token_hash = hash_token(token)
    db.query(UserSession).filter(UserSession.token_hash == token_hash).delete()
    db.commit()


def invalidate_all_sessions(db: Session, user_id: int):
    """Kullanicinin tum oturumlarini sonlandir"""
    db.query(UserSession).filter(UserSession.user_id == user_id).delete()
    db.commit()


# ==================== IP BLACKLIST/WHITELIST ====================


def is_ip_blacklisted(ip: str) -> bool:
    """IP blacklist'te mi kontrol"""
    try:
        return redis_exists(f"blacklist:ip:{ip}")
    except Exception as e:
        logger.error(f"IP blacklist kontrol hatasi: {e}")
        return False


def is_ip_whitelisted(ip: str) -> bool:
    """IP whitelist'te mi kontrol"""
    try:
        return redis_exists(f"whitelist:ip:{ip}")
    except Exception as e:
        logger.error(f"IP whitelist kontrol hatasi: {e}")
        return False


def blacklist_ip(ip: str, reason: str = "", duration: int = 3600):
    """IP'yi blacklist'e ekle"""
    try:
        redis_set(f"blacklist:ip:{ip}", reason, duration)
        logger.warning(
            f"SECURITY_EVENT: IP blacklisted | "
            f"ip={ip} | "
            f"reason={reason} | "
            f"duration_seconds={duration}"
        )
    except Exception as e:
        logger.error(f"IP blacklist hatasi: {e}")


def whitelist_ip(ip: str):
    """IP'yi whitelist'e ekle"""
    try:
        redis_set(f"whitelist:ip:{ip}", "1")
        logger.info(f"IP whitelisted: {ip}")
    except Exception as e:
        logger.error(f"IP whitelist hatasi: {e}")


def unblacklist_ip(ip: str):
    """IP'yi blacklist'ten cikar"""
    try:
        redis_delete(f"blacklist:ip:{ip}")
        logger.info(f"SECURITY_EVENT: IP unblacklisted | " f"ip={ip}")
    except Exception as e:
        logger.error(f"IP unblacklist hatasi: {e}")


# ==================== RATE LIMITING ====================


def check_rate_limit(key: str, limit: int = 100, window: int = 60) -> bool:
    """Rate limit kontrolu - True ise limit asilmis"""
    try:
        count = redis_incr(f"ratelimit:{key}", window)
        if count > limit:
            logger.warning(
                f"SECURITY_EVENT: Rate limit exceeded | "
                f"key={key} | "
                f"count={count} | "
                f"limit={limit} | "
                f"window_seconds={window}"
            )
            return True
        return False
    except Exception as e:
        logger.error(f"Rate limit kontrol hatasi: {e}")
        return False


def get_rate_limit_count(key: str) -> int:
    """Rate limit sayacini getir"""
    try:
        val = redis_get(f"ratelimit:{key}")
        return int(val) if val else 0
    except Exception as e:
        logger.error(f"Rate limit count hatasi: {e}")
        return 0


# ==================== AUTHENTICATION ====================


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Mevcut kullaniciyi getir (opsiyonel - login olmadan da calisir)"""
    # IP kontrolu - full null safety
    client_ip = get_client_ip(request)
    if client_ip and is_ip_blacklisted(client_ip) and not is_ip_whitelisted(client_ip):
        raise HTTPException(status_code=403, detail="IP adresiniz engellenmis")

    token = None

    # Header'dan token al
    if credentials:
        token = credentials.credentials

    # Cookie'den token al
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        return None

    # Token decode et
    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    # Check if this is a panel token (format: "panel_<server_id>")
    token_type = payload.get("type")
    if token_type == "panel" or (isinstance(user_id, str) and user_id.startswith("panel_")):
        # Panel tokens don't have user sessions, return None (panel routes don't need user)
        # Panel authentication is handled separately in panel routes
        return None

    # Type-safe user_id conversion
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid user_id in token: {user_id} - {e}")
        return None

    # Session kontrolu with proper time comparison
    token_hash = hash_token(token)
    current_time = datetime.utcnow()
    session = (
        db.query(UserSession)
        .filter(UserSession.token_hash == token_hash, UserSession.expires_at > current_time)
        .first()
    )

    if not session:
        return None

    # Extra validation: ensure expires_at is in the future
    if session.expires_at and session.expires_at <= current_time:
        logger.warning(f"Session expired for user_id: {user_id_int}")
        return None

    # Kullanici getir
    user = db.query(User).filter(User.id == user_id_int).first()

    if not user or user.status != UserStatus.ACTIVE:
        return None

    return user


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Mevcut kullaniciyi getir (opsiyonel)"""
    # IP kontrolu - full null safety
    client_ip = get_client_ip(request)
    if client_ip and is_ip_blacklisted(client_ip) and not is_ip_whitelisted(client_ip):
        logger.warning(f"Blacklisted IP attempt: {client_ip}")
        raise HTTPException(status_code=403, detail="IP adresiniz engellenmis")

    token = None

    # Header'dan token al
    if credentials:
        token = credentials.credentials

    # Cookie'den token al
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        return None

    # Token decode et
    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    # Check if this is a panel token (format: "panel_<server_id>")
    token_type = payload.get("type")
    if token_type == "panel" or (isinstance(user_id, str) and user_id.startswith("panel_")):
        # Panel tokens don't have user sessions, return None (panel routes don't need user)
        # Panel authentication is handled separately in panel routes
        return None

    # Type-safe user_id conversion
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid user_id in token: {user_id} - {e}")
        return None

    # Session kontrolu with proper time comparison
    token_hash = hash_token(token)
    current_time = datetime.utcnow()
    session = (
        db.query(UserSession)
        .filter(UserSession.token_hash == token_hash, UserSession.expires_at > current_time)
        .first()
    )

    if not session:
        return None

    # Extra validation: ensure expires_at is in the future
    if session.expires_at and session.expires_at <= current_time:
        logger.warning(f"Session expired for user_id: {user_id_int}")
        return None

    # Kullanici getir
    user = db.query(User).filter(User.id == user_id_int).first()

    if not user or user.status != UserStatus.ACTIVE:
        return None

    return user


async def get_current_user_required(user: Optional[User] = Depends(get_current_user)) -> User:
    """Mevcut kullaniciyi getir (zorunlu)"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Giris yapmaniz gerekiyor",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_admin(user: User = Depends(get_current_user_required)) -> User:
    """Admin kullanici getir"""
    if user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Bu islem icin yetkiniz yok"
        )
    return user


async def get_current_moderator(user: User = Depends(get_current_user_required)) -> User:
    """Moderator veya ustu kullanici getir"""
    if user.role not in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Bu islem icin yetkiniz yok"
        )
    return user


async def get_superadmin(user: User = Depends(get_current_user_required)) -> User:
    """Superadmin kullanici getir"""
    if user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu islem icin superadmin yetkiniz gerekiyor",
        )
    return user


async def get_current_user_with_steam(user: User = Depends(get_current_user_required)) -> User:
    """Steam hesabi bagli kullanici getir"""
    if not user.steam_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Bu ozellik icin Steam hesabi baglantisi gerekli. "
                "Profil ayarlarindan Steam hesabinizi baglayabilirsiniz."
            ),
        )
    return user


async def get_current_user_with_steam_optional(
    user: Optional[User] = Depends(get_current_user),
) -> Optional[User]:
    """Steam hesabi bagli kullanici getir (opsiyonel - steam yoksa None doner)"""
    if user and not user.steam_id:
        return None
    return user


def generate_reference_code(prefix: str = "PAY") -> str:
    """Referans kodu olustur"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_part = secrets.token_hex(4).upper()
    return f"{prefix}-{timestamp}-{random_part}"


def generate_rcon_password(length: int = 16) -> str:
    """RCON sifresi olustur"""
    return secrets.token_urlsafe(length)


def generate_server_password(length: int = 8) -> str:
    """Sunucu sifresi olustur"""
    return secrets.token_urlsafe(length)


def get_current_user_from_token(db: Session, token: str) -> Optional[User]:
    """Token'dan kullanıcıyı getir (middleware için senkron versiyon)"""
    if not token:
        return None

    # Token decode et
    payload = decode_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    # Type-safe user_id conversion
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid user_id in token (sync): {user_id} - {e}")
        return None

    # Session kontrolu with proper time comparison
    token_hash = hash_token(token)
    current_time = datetime.utcnow()
    session = (
        db.query(UserSession)
        .filter(UserSession.token_hash == token_hash, UserSession.expires_at > current_time)
        .first()
    )

    if not session:
        return None

    # Extra validation: ensure expires_at is in the future
    if session.expires_at and session.expires_at <= current_time:
        logger.warning(f"Session expired for user_id (sync): {user_id_int}")
        return None

    # Kullanici getir
    user = db.query(User).filter(User.id == user_id_int).first()

    if not user or user.status != UserStatus.ACTIVE:
        return None

    return user


async def get_panel_server_id(
    request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[int]:
    """
    Extract server_id from panel token
    Returns server_id if panel token is valid, None otherwise
    """
    token = None

    # Get token from header
    if credentials:
        token = credentials.credentials
        logger.info(f"[PANEL_AUTH] Token from header: {token[:20]}...")

    # Get token from cookie
    if not token:
        token = request.cookies.get("access_token")
        if token:
            logger.info(f"[PANEL_AUTH] Token from cookie: {token[:20]}...")

    if not token:
        logger.warning("[PANEL_AUTH] No token found in request")
        return None

    # Decode token
    payload = decode_token(token)
    if not payload:
        logger.warning("[PANEL_AUTH] Token decode failed")
        return None

    logger.info(
        "[PANEL_AUTH] Token payload: type=%s, sub=%s, server_id=%s",
        payload.get("type"),
        payload.get("sub"),
        payload.get("server_id"),
    )

    # Check if this is a panel token
    token_type = payload.get("type")
    user_id = payload.get("sub")

    if token_type == "panel" or (isinstance(user_id, str) and user_id.startswith("panel_")):
        # Extract server_id from panel token
        server_id = payload.get("server_id")
        if server_id:
            logger.info(f"[PANEL_AUTH] Panel token validated for server {server_id}")
            return int(server_id)
        else:
            logger.warning("[PANEL_AUTH] Panel token missing server_id")

    else:
        logger.info("[PANEL_AUTH] Not a panel token")

    return None


async def get_current_user_or_panel(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> tuple[Optional[User], Optional[int]]:
    """
    Get either current user OR panel server_id
    Returns (user, None) if Steam auth, or (None, server_id) if panel auth
    """
    # Try panel auth first
    panel_server_id = await get_panel_server_id(request, credentials)
    if panel_server_id:
        return (None, panel_server_id)

    # Try regular user auth
    user = await get_current_user(request, credentials, db)
    return (user, None)
