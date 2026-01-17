"""
AGTR Merkezi - Authentication API
2FA, Rate Limiting, Audit Log destekli
"""

import base64
import logging
import re
import secrets
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Optional

import pyotp
import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_session,
    get_current_user,
    get_current_user_required,
    hash_password,
    invalidate_session,
    verify_password,
)
from app.models.connection import get_db
from app.models.database import AuditLog, SystemLog, User, UserRole, UserStatus
from app.services.email import email_service

logger = logging.getLogger(__name__)
router = APIRouter()


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_confirm: str
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 30:
            raise ValueError("Kullanici adi 3-30 karakter olmali")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Kullanici adi sadece harf, rakam, _ ve - icerebilir")
        return v.lower()
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f"Sifre en az {settings.PASSWORD_MIN_LENGTH} karakter olmali")
        if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', v):
            raise ValueError("Sifre en az bir buyuk harf icermeli")
        if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', v):
            raise ValueError("Sifre en az bir kucuk harf icermeli")
        if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', v):
            raise ValueError("Sifre en az bir rakam icermeli")
        if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Sifre en az bir ozel karakter icermeli")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str
    totp_code: Optional[str] = None


class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]


class TwoFactorVerifyRequest(BaseModel):
    code: str


class TwoFactorLoginRequest(BaseModel):
    user_id: int
    code: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f"Sifre en az {settings.PASSWORD_MIN_LENGTH} karakter olmali")
        if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', v):
            raise ValueError("Sifre en az bir buyuk harf icermeli")
        if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', v):
            raise ValueError("Sifre en az bir kucuk harf icermeli")
        if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', v):
            raise ValueError("Sifre en az bir rakam icermeli")
        return v


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[dict] = None
    token: Optional[str] = None
    requires_2fa: Optional[bool] = None
    temp_token: Optional[str] = None
    redirect: Optional[str] = None  # Role bazli yonlendirme


# ==================== HELPER FUNCTIONS ====================

def log_audit(db: Session, user_id: int, action: str, entity_type: str = None, 
              entity_id: int = None, old_values: dict = None, new_values: dict = None,
              ip_address: str = None, user_agent: str = None):
    """Audit log kaydi olustur"""
    try:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        logger.error(f"Audit log hatasi: {e}")


def check_login_attempts(db: Session, user: User) -> bool:
    """Login denemelerini kontrol et, kilitli mi?"""
    if user.lockout_until and user.lockout_until > datetime.utcnow():
        return False  # Hesap kilitli
    
    # Kilit suresi gectiyse sifirla
    if user.lockout_until and user.lockout_until <= datetime.utcnow():
        user.login_attempts = 0
        user.lockout_until = None
        db.commit()
    
    return True


def increment_login_attempts(db: Session, user: User):
    """Basarisiz giris denemesini kaydet"""
    user.login_attempts = (user.login_attempts or 0) + 1
    
    if user.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        user.lockout_until = datetime.utcnow() + timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
        logger.warning(f"Hesap kilitlendi: {user.username} - {user.login_attempts} basarisiz deneme")
    
    db.commit()


def reset_login_attempts(db: Session, user: User):
    """Basarili giriste denemeleri sifirla"""
    user.login_attempts = 0
    user.lockout_until = None
    db.commit()


def generate_backup_codes(count: int = 10) -> List[str]:
    """2FA backup kodlari olustur"""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def generate_2fa_qr_code(secret: str, username: str) -> str:
    """2FA QR kod olustur (base64)"""
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=username,
        issuer_name=settings.TWO_FACTOR_ISSUER
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()


def verify_2fa_code(secret: str, code: str, backup_codes: List[str] = None) -> tuple:
    """2FA kodunu dogrula, backup code kullanildiysa belirt"""
    # Normal TOTP kontrolu
    totp = pyotp.TOTP(secret)
    if totp.verify(code, valid_window=1):
        return True, False  # Basarili, backup degil
    
    # Backup code kontrolu
    if backup_codes and code.upper() in [c.upper() for c in backup_codes]:
        return True, True  # Basarili, backup kullanildi
    
    return False, False


@router.post("/register", response_model=AuthResponse)
async def register(request: Request, data: RegisterRequest, db: Session = Depends(get_db)):
    """Yeni kullanici kaydi"""
    if data.password != data.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sifreler eslesmiyor")
    
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu kullanici adi zaten kullaniliyor")
    
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu e-posta adresi zaten kayitli")
    
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]
    
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        display_name=data.username,
        last_ip=client_ip,
        password_changed_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # System log
    log = SystemLog(
        level="info", 
        category="auth", 
        message=f"Yeni kullanici kaydi: {user.username}", 
        user_id=user.id, 
        ip_address=client_ip
    )
    db.add(log)
    
    # Audit log
    log_audit(
        db, user.id, "user_register", "user", user.id,
        new_values={"username": user.username, "email": user.email},
        ip_address=client_ip, user_agent=user_agent
    )
    
    token = create_access_token({"sub": str(user.id)})
    create_session(db, user.id, token, request)
    
    logger.info(f"Yeni kullanici kaydi: {user.username} - IP: {client_ip}")
    
    return AuthResponse(
        success=True,
        message="Kayit basarili!",
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "avatar": user.avatar,
            "role": user.role.value,
            "status": user.status.value,
            "balance": float(user.balance or 0),
            "balance_coin": float(user.balance_coin or 0),
            "steam_id": user.steam_id,
            "two_factor_enabled": user.two_factor_enabled,
            "email_verified": user.email_verified
        },
        token=token
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: Request, response: Response, data: LoginRequest, db: Session = Depends(get_db)):
    """Kullanici girisi - 2FA destekli"""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]
    
    user = db.query(User).filter(
        (User.username == data.username.lower()) | (User.email == data.username.lower())
    ).first()
    
    if not user:
        logger.warning(f"Basarisiz giris denemesi - kullanici bulunamadi: {data.username} - IP: {client_ip}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanici adi veya sifre hatali")
    
    # Hesap kilitli mi kontrol et
    if not check_login_attempts(db, user):
        remaining = (user.lockout_until - datetime.utcnow()).seconds // 60
        logger.warning(f"Kilitli hesaba giris denemesi: {user.username} - IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail=f"Hesabiniz gecici olarak kilitlendi. {remaining} dakika sonra tekrar deneyin."
        )
    
    # Sifre kontrolu
    if not verify_password(data.password, user.password_hash):
        increment_login_attempts(db, user)
        remaining_attempts = settings.MAX_LOGIN_ATTEMPTS - user.login_attempts
        logger.warning(f"Basarisiz giris denemesi: {user.username} - IP: {client_ip} - Kalan: {remaining_attempts}")
        
        log_audit(db, user.id, "login_failed", "user", user.id,
                  new_values={"reason": "wrong_password", "attempts": user.login_attempts},
                  ip_address=client_ip, user_agent=user_agent)
        
        if remaining_attempts > 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=f"Kullanici adi veya sifre hatali. {remaining_attempts} deneme hakkiniz kaldi."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Cok fazla basarisiz deneme. Hesabiniz {settings.LOGIN_LOCKOUT_MINUTES} dakika kilitlendi."
            )
    
    # Hesap durumu kontrolu
    if user.status == UserStatus.BANNED:
        log_audit(db, user.id, "login_blocked", "user", user.id,
                  new_values={"reason": "banned"}, ip_address=client_ip, user_agent=user_agent)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hesabiniz yasaklanmis")
    
    if user.status == UserStatus.SUSPENDED:
        log_audit(db, user.id, "login_blocked", "user", user.id,
                  new_values={"reason": "suspended"}, ip_address=client_ip, user_agent=user_agent)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hesabiniz askiya alinmis")
    
    # 2FA kontrolu
    if user.two_factor_enabled:
        if not data.totp_code:
            # 2FA kodu gerekli, temp token olustur
            temp_token = secrets.token_urlsafe(32)
            return AuthResponse(
                success=False,
                message="2FA dogrulamasi gerekli",
                requires_2fa=True,
                temp_token=temp_token,
                user={"id": user.id}
            )
        
        # 2FA kodu dogrula
        valid, is_backup = verify_2fa_code(
            user.two_factor_secret, 
            data.totp_code, 
            user.two_factor_backup_codes
        )
        
        if not valid:
            increment_login_attempts(db, user)
            log_audit(db, user.id, "2fa_failed", "user", user.id, ip_address=client_ip, user_agent=user_agent)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Gecersiz 2FA kodu")
        
        # Backup code kullanildiysa listeden cikar
        if is_backup:
            backup_codes = user.two_factor_backup_codes or []
            backup_codes = [c for c in backup_codes if c.upper() != data.totp_code.upper()]
            user.two_factor_backup_codes = backup_codes
            logger.info(f"2FA backup code kullanildi: {user.username}")
    
    # Basarili giris
    reset_login_attempts(db, user)
    
    user.last_login = datetime.utcnow()
    user.last_ip = client_ip
    db.commit()
    
    token = create_access_token({"sub": str(user.id)})
    create_session(db, user.id, token, request)
    
    response.set_cookie(
        key="access_token", 
        value=token, 
        httponly=True, 
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
        samesite="lax",
        secure=settings.SESSION_COOKIE_SECURE
    )
    
    # Audit log
    log_audit(db, user.id, "login_success", "user", user.id,
              new_values={"method": "2fa" if user.two_factor_enabled else "password"},
              ip_address=client_ip, user_agent=user_agent)
    
    logger.info(f"Basarili giris: {user.username} - IP: {client_ip}")
    
    # Role bazli redirect URL
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        redirect_url = "/admin"
    else:
        redirect_url = "/panel"
    
    return AuthResponse(
        success=True,
        message="Giris basarili!",
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "avatar": user.avatar,
            "role": user.role.value,
            "status": user.status.value,
            "balance": float(user.balance or 0),
            "balance_coin": float(user.balance_coin or 0),
            "steam_id": user.steam_id,
            "two_factor_enabled": user.two_factor_enabled,
            "email_verified": user.email_verified
        },
        token=token,
        redirect=redirect_url
    )


@router.post("/logout", response_model=AuthResponse)
async def logout(request: Request, response: Response, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Cikis yap"""
    client_ip = request.client.host if request.client else None
    
    token = request.cookies.get("access_token")
    if token:
        invalidate_session(db, token)
    
    response.delete_cookie("access_token")
    
    log_audit(db, current_user.id, "logout", "user", current_user.id, ip_address=client_ip)
    logger.info(f"Cikis yapildi: {current_user.username}")
    
    return AuthResponse(success=True, message="Cikis yapildi")


@router.get("/check")
async def check_auth(current_user: Optional[User] = Depends(get_current_user)):
    """Oturum kontrolu"""
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "role": current_user.role.value,
                "two_factor_enabled": current_user.two_factor_enabled
            }
        }
    return {"authenticated": False}


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user_required)):
    """Mevcut kullanici bilgilerini getir"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "avatar": current_user.avatar,
        "role": current_user.role.value,
        "status": current_user.status.value,
        "balance": float(current_user.balance or 0),
        "balance_coin": float(current_user.balance_coin or 0),
        "steam_id": current_user.steam_id,
        "two_factor_enabled": current_user.two_factor_enabled,
        "email_verified": current_user.email_verified,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }


# ==================== 2FA ENDPOINTS ====================

@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """2FA kurulumu baslat - QR kod ve backup kodlari dondur"""
    if current_user.two_factor_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA zaten aktif")
    
    # Yeni secret olustur
    secret = pyotp.random_base32()
    backup_codes = generate_backup_codes(settings.TWO_FACTOR_BACKUP_CODES_COUNT)
    qr_code = generate_2fa_qr_code(secret, current_user.username)
    
    # Gecici olarak kaydet (dogrulama bekliyor)
    current_user.two_factor_secret = secret
    current_user.two_factor_backup_codes = backup_codes
    db.commit()
    
    logger.info(f"2FA kurulumu baslatildi: {current_user.username}")
    
    return TwoFactorSetupResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/2fa/verify")
async def verify_2fa_setup(request: Request, data: TwoFactorVerifyRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """2FA kurulumunu dogrula ve aktif et"""
    if current_user.two_factor_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA zaten aktif")
    
    if not current_user.two_factor_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Oncelikle 2FA kurulumunu baslatmasiniz")
    
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if not totp.verify(data.code, valid_window=1):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gecersiz dogrulama kodu")
    
    current_user.two_factor_enabled = True
    db.commit()
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "2fa_enabled", "user", current_user.id, ip_address=client_ip)
    logger.info(f"2FA aktif edildi: {current_user.username}")
    
    return {"success": True, "message": "2FA basariyla aktif edildi"}


@router.post("/2fa/disable")
async def disable_2fa(request: Request, data: TwoFactorVerifyRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """2FA devre disi birak"""
    if not current_user.two_factor_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA zaten kapalı")
    
    # Kodu dogrula
    valid, _ = verify_2fa_code(current_user.two_factor_secret, data.code, current_user.two_factor_backup_codes)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gecersiz dogrulama kodu")
    
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    current_user.two_factor_backup_codes = None
    db.commit()
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "2fa_disabled", "user", current_user.id, ip_address=client_ip)
    logger.info(f"2FA devre disi birakildi: {current_user.username}")
    
    return {"success": True, "message": "2FA devre disi birakildi"}


@router.post("/2fa/regenerate-backup-codes")
async def regenerate_backup_codes(request: Request, data: TwoFactorVerifyRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Yeni backup kodlari olustur"""
    if not current_user.two_factor_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA aktif degil")
    
    # Kodu dogrula
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if not totp.verify(data.code, valid_window=1):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gecersiz dogrulama kodu")
    
    new_codes = generate_backup_codes(settings.TWO_FACTOR_BACKUP_CODES_COUNT)
    current_user.two_factor_backup_codes = new_codes
    db.commit()
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "2fa_backup_regenerated", "user", current_user.id, ip_address=client_ip)
    
    return {"success": True, "backup_codes": new_codes}


# ==================== PASSWORD MANAGEMENT ====================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    new_password_confirm: str
    
    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f"Sifre en az {settings.PASSWORD_MIN_LENGTH} karakter olmali")
        return v


@router.post("/forgot-password")
async def forgot_password(request: Request, data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Sifre sifirlama istegi"""
    user = db.query(User).filter(User.email == data.email).first()
    
    # Kullanici yoksa bile ayni mesaji ver (guvenlik)
    if not user:
        logger.info(f"Sifre sifirlama istegi: bilinmeyen email {data.email}")
        return {"success": True, "message": "E-posta adresinize sifirlama linki gonderildi"}
    
    # Sifirlama token'i olustur
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    # Email gonder
    reset_url = f"{settings.SITE_URL}/reset-password?token={reset_token}"
    try:
        await email_service.send_password_reset(
            to=user.email,
            username=user.display_name or user.username,
            reset_url=reset_url
        )
        logger.info(f"Sifre sifirlama emaili gonderildi: {user.username}")
    except Exception as e:
        logger.error(f"Email gonderim hatasi: {e}")
        # Email hatasi olsa bile kullaniciya hata gosterme (guvenlik)
    
    client_ip = request.client.host if request.client else None
    log_audit(db, user.id, "password_reset_requested", "user", user.id, ip_address=client_ip)
    
    return {"success": True, "message": "E-posta adresinize sifirlama linki gonderildi"}


@router.post("/reset-password")
async def reset_password(request: Request, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Sifre sifirla"""
    if data.new_password != data.new_password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sifreler eslesmiyor")
    
    user = db.query(User).filter(
        User.reset_token == data.token,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gecersiz veya suresi dolmus token")
    
    user.password_hash = hash_password(data.new_password)
    user.password_changed_at = datetime.utcnow()
    user.reset_token = None
    user.reset_token_expires = None
    user.login_attempts = 0
    user.lockout_until = None
    db.commit()
    
    client_ip = request.client.host if request.client else None
    log_audit(db, user.id, "password_reset_completed", "user", user.id, ip_address=client_ip)
    logger.info(f"Sifre sifirlandi: {user.username}")
    
    return {"success": True, "message": "Sifreniz basariyla sifirlandi. Giris yapabilirsiniz."}


@router.get("/validate-reset-token")
async def validate_reset_token(token: str, db: Session = Depends(get_db)):
    """Reset token gecerli mi kontrol et"""
    user = db.query(User).filter(
        User.reset_token == token,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        return {"valid": False}
    
    return {"valid": True, "username": user.username}


@router.post("/change-password")
async def change_password(request: Request, data: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Sifre degistir"""
    if data.new_password != data.new_password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Yeni sifreler eslesmiyor")
    
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mevcut sifre hatali")
    
    if data.current_password == data.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Yeni sifre eskisiyle ayni olamaz")
    
    current_user.password_hash = hash_password(data.new_password)
    current_user.password_changed_at = datetime.utcnow()
    current_user.must_change_password = False
    db.commit()
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "password_changed", "user", current_user.id, ip_address=client_ip)
    logger.info(f"Sifre degistirildi: {current_user.username}")
    
    return {"success": True, "message": "Sifreniz basariyla degistirildi"}


# ==================== ADMIN 2FA REQUIREMENT ====================

@router.post("/2fa/login", response_model=AuthResponse)
async def login_with_2fa(request: Request, response: Response, data: TwoFactorLoginRequest, db: Session = Depends(get_db)):
    """2FA ile giriş tamamla"""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]
    
    # Kullanıcıyı bul
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Gecersiz kullanici")
    
    # 2FA aktif mi kontrol
    if not user.two_factor_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA bu hesapta aktif degil")
    
    # 2FA kodu dogrula
    valid, is_backup = verify_2fa_code(
        user.two_factor_secret, 
        data.code, 
        user.two_factor_backup_codes
    )
    
    if not valid:
        increment_login_attempts(db, user)
        log_audit(db, user.id, "2fa_login_failed", "user", user.id, ip_address=client_ip, user_agent=user_agent)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Gecersiz 2FA kodu")
    
    # Backup code kullanıldıysa listeden çıkar
    if is_backup:
        backup_codes = user.two_factor_backup_codes or []
        backup_codes = [c for c in backup_codes if c.upper() != data.code.upper()]
        user.two_factor_backup_codes = backup_codes
        logger.info(f"2FA backup code kullanildi: {user.username}")
    
    # Başarılı giriş
    reset_login_attempts(db, user)
    
    user.last_login = datetime.utcnow()
    user.last_ip = client_ip
    db.commit()
    
    token = create_access_token({"sub": str(user.id)})
    create_session(db, user.id, token, request)
    
    response.set_cookie(
        key="access_token", 
        value=token, 
        httponly=True, 
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60, 
        samesite="lax",
        secure=settings.SESSION_COOKIE_SECURE
    )
    
    # Audit log
    log_audit(db, user.id, "login_success", "user", user.id,
              new_values={"method": "2fa"},
              ip_address=client_ip, user_agent=user_agent)
    
    logger.info(f"2FA girisi basarili: {user.username} - IP: {client_ip}")
    
    # Role bazlı redirect URL
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        redirect_url = "/admin"
    else:
        redirect_url = "/panel"
    
    return AuthResponse(
        success=True,
        message="Giris basarili!",
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "avatar": user.avatar,
            "role": user.role.value,
            "status": user.status.value,
            "balance": float(user.balance or 0),
            "balance_coin": float(user.balance_coin or 0),
            "steam_id": user.steam_id,
            "two_factor_enabled": user.two_factor_enabled,
            "email_verified": user.email_verified
        },
        token=token,
        redirect=redirect_url
    )


@router.get("/2fa/status")
async def get_2fa_status(current_user: User = Depends(get_current_user_required)):
    """2FA durumunu kontrol et"""
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
    requires_2fa = is_admin and settings.TWO_FACTOR_REQUIRED_FOR_ADMIN and not current_user.two_factor_enabled
    
    return {
        "enabled": current_user.two_factor_enabled,
        "required": requires_2fa,
        "backup_codes_remaining": len(current_user.two_factor_backup_codes) if current_user.two_factor_backup_codes else 0
    }


# ==================== OAUTH / SOCIAL LOGIN ====================

from app.core.oauth import SteamOAuth2Provider, DiscordOAuth2Provider, GoogleOAuth2Provider
from app.models.database import OAuthAccount
from fastapi.responses import RedirectResponse

# OAuth provider instances
steam_provider = SteamOAuth2Provider()
discord_provider = DiscordOAuth2Provider()
google_provider = GoogleOAuth2Provider()


def get_oauth_provider(provider: str):
    """Get OAuth provider by name"""
    providers = {
        "steam": steam_provider,
        "discord": discord_provider,
        "google": google_provider
    }
    if provider not in providers:
        raise HTTPException(status_code=400, detail=f"Desteklenmeyen OAuth provider: {provider}")
    return providers[provider]


@router.get("/oauth/{provider}")
async def oauth_login(provider: str, request: Request, db: Session = Depends(get_db)):
    """OAuth login baslat - Provider'a yonlendir"""
    oauth = get_oauth_provider(provider)

    # State token olustur (CSRF koruma)
    state = secrets.token_urlsafe(32)

    # State'i Redis'e kaydet (10 dakika)
    try:
        from app.core.redis_manager import redis_manager
        await redis_manager.set(f"oauth_state:{state}", provider, ex=settings.OAUTH_STATE_EXPIRE_MINUTES * 60)
    except Exception as e:
        logger.warning(f"Redis state kayit hatasi: {e}")

    # Callback URL
    callback_url = f"{settings.BASE_URL}/api/auth/oauth/{provider}/callback"

    # Provider'a yonlendir
    auth_url = oauth.get_authorization_url(callback_url, state)
    return RedirectResponse(url=auth_url)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """OAuth callback - Provider'dan donen veriyi isle"""
    oauth = get_oauth_provider(provider)
    params = dict(request.query_params)

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]

    logger.info(f"OAuth callback started for {provider}")
    logger.info(f"Callback params: {list(params.keys())}")

    try:
        if provider == "steam":
            # Steam OpenID verification
            steam_id = await oauth.verify_openid_response(params)
            if not steam_id:
                logger.error("Steam OpenID dogrulama basarisiz")
                return RedirectResponse(url="/login?error=steam_verification_failed")

            # Steam kullanici bilgilerini al
            user_info = await oauth.get_user_info(steam_id)
            normalized = oauth.normalize_user_data(user_info)
            normalized["provider_id"] = steam_id

        else:
            # Discord/Google OAuth2 flow
            code = params.get("code")
            if not code:
                logger.error(f"{provider} OAuth code eksik")
                return RedirectResponse(url=f"/login?error={provider}_no_code")

            callback_url = f"{settings.BASE_URL}/api/auth/oauth/{provider}/callback"
            token_data = await oauth.exchange_code(code, callback_url)
            access_token = token_data.get("access_token")

            if not access_token:
                logger.error(f"{provider} access token alinamadi")
                return RedirectResponse(url=f"/login?error={provider}_token_failed")

            user_info = await oauth.get_user_info(access_token)
            normalized = oauth.normalize_user_data(user_info)

        # Mevcut OAuth hesabi kontrol et
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_id == normalized["provider_id"]
        ).first()

        if oauth_account:
            # Mevcut hesap - giris yap
            user = oauth_account.user
            oauth_account.last_used_at = datetime.utcnow()
            oauth_account.provider_avatar = normalized.get("avatar")
            db.commit()
        else:
            # Yeni kullanici olustur veya mevcut kullaniciya bagla
            username_base = normalized.get("username", f"{provider}_user")
            # Remove quotes if present (Steam sometimes returns quoted names)
            username_base = username_base.strip('"\'')
            username = username_base.lower().replace(" ", "_")[:20]

            # Benzersiz kullanici adi
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                username = f"{username}_{secrets.token_hex(4)}"

            # Steam email'i vermez, placeholder olustur
            email = normalized.get("email")
            if not email and provider == "steam":
                steam_id = normalized["provider_id"]
                email = f"steam_{steam_id}@steam.local"

            # Display name'den de quotes temizle
            display_name = normalized.get("display_name", username)
            if isinstance(display_name, str):
                display_name = display_name.strip('"\'')

            # Yeni kullanici
            user = User(
                username=username,
                email=email,
                display_name=display_name,
                avatar=normalized.get("avatar"),
                password_hash=hash_password(secrets.token_urlsafe(32)),  # Random password
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                steam_id=normalized["provider_id"] if provider == "steam" else None
            )
            db.add(user)
            db.flush()

            # OAuth hesabi olustur
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_id=normalized["provider_id"],
                provider_username=normalized.get("username"),
                provider_email=normalized.get("email"),
                provider_avatar=normalized.get("avatar")
            )
            db.add(oauth_account)
            db.commit()

            logger.info(f"Yeni {provider} kullanicisi: {user.username}")

        # Hesap kontrolu
        if user.status == UserStatus.BANNED:
            return RedirectResponse(url="/login?error=account_banned")

        if user.status == UserStatus.SUSPENDED:
            return RedirectResponse(url="/login?error=account_suspended")

        # Basarili giris
        user.last_login = datetime.utcnow()
        user.last_ip = client_ip
        db.commit()

        token = create_access_token({"sub": str(user.id)})
        create_session(db, user.id, token, request)

        # Frontend'e token'i iletmek icin ozel URL ile redirect
        # Frontend bu token'i localStorage'a kaydedecek
        redirect_response = RedirectResponse(
            url=f"/oauth-callback?token={token}&provider={provider}",
            status_code=302
        )

        # Cookie da set et (opsiyonel, API istekleri icin)
        redirect_response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=settings.SESSION_COOKIE_SECURE
        )

        # Audit log
        log_audit(db, user.id, "oauth_login", "user", user.id,
                  new_values={"provider": provider},
                  ip_address=client_ip, user_agent=user_agent)

        logger.info(f"{provider} girisi basarili: {user.username} - IP: {client_ip}")

        return redirect_response

    except HTTPException as e:
        logger.error(f"OAuth callback HTTPException ({provider}): {e.detail}")
        return RedirectResponse(url=f"/login?error={provider}_failed")
    except Exception as e:
        import traceback
        logger.error(f"OAuth callback hatasi ({provider}): {type(e).__name__}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return RedirectResponse(url=f"/login?error={provider}_failed")