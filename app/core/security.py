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
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    })
    
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


def create_session(db: Session, user_id: int, token: str, request: Request) -> UserSession:
    """Kullanici oturumu olustur"""
    session = UserSession(
        user_id=user_id,
        token_hash=hash_token(token),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:500],
        expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
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
        logger.info(f"IP blacklisted: {ip} - {reason}")
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
        logger.info(f"IP unblacklisted: {ip}")
    except Exception as e:
        logger.error(f"IP unblacklist hatasi: {e}")


# ==================== RATE LIMITING ====================

def check_rate_limit(key: str, limit: int = 100, window: int = 60) -> bool:
    """Rate limit kontrolu - True ise limit asilmis"""
    try:
        count = redis_incr(f"ratelimit:{key}", window)
        return count > limit
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
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Mevcut kullaniciyi getir (opsiyonel - login olmadan da calisir)"""
    # IP kontrolu
    client_ip = request.client.host if request.client else None
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

    # Session kontrolu
    token_hash = hash_token(token)
    session = db.query(UserSession).filter(
        UserSession.token_hash == token_hash,
        UserSession.expires_at > datetime.utcnow()
    ).first()

    if not session:
        return None

    # Kullanici getir
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user or user.status != UserStatus.ACTIVE:
        return None

    return user


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Mevcut kullaniciyi getir (opsiyonel)"""
    # IP kontrolu
    client_ip = request.client.host if request.client else None
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
    
    # Session kontrolu
    token_hash = hash_token(token)
    session = db.query(UserSession).filter(
        UserSession.token_hash == token_hash,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        return None
    
    # Kullanici getir
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user or user.status != UserStatus.ACTIVE:
        return None
    
    return user


async def get_current_user_required(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """Mevcut kullaniciyi getir (zorunlu)"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Giris yapmaniz gerekiyor",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def get_current_admin(
    user: User = Depends(get_current_user_required)
) -> User:
    """Admin kullanici getir"""
    if user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu islem icin yetkiniz yok"
        )
    return user


async def get_current_moderator(
    user: User = Depends(get_current_user_required)
) -> User:
    """Moderator veya ustu kullanici getir"""
    if user.role not in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu islem icin yetkiniz yok"
        )
    return user


async def get_superadmin(
    user: User = Depends(get_current_user_required)
) -> User:
    """Superadmin kullanici getir"""
    if user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu islem icin superadmin yetkiniz gerekiyor"
        )
    return user


async def get_current_user_with_steam(
    user: User = Depends(get_current_user_required)
) -> User:
    """Steam hesabi bagli kullanici getir"""
    if not user.steam_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu ozellik icin Steam hesabi baglantisi gerekli. Profil ayarlarindan Steam hesabinizi baglayabilirsiniz."
        )
    return user


async def get_current_user_with_steam_optional(
    user: Optional[User] = Depends(get_current_user)
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
    
    # Session kontrolu
    token_hash = hash_token(token)
    session = db.query(UserSession).filter(
        UserSession.token_hash == token_hash,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        return None
    
    # Kullanici getir
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user or user.status != UserStatus.ACTIVE:
        return None
    
    return user
