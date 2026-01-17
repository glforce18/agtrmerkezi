"""
AGTR Merkezi - User API
Avatar, Steam, Notification, Session, Activity destekli
"""

import logging
import re
import secrets
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import desc
from sqlalchemy.orm import Session

# Image processing (optional)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from app.core.config import settings
from app.core.security import (
    get_current_user,
    get_current_user_required,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.connection import get_db
from app.models.database import (
    AuditLog,
    GameServer,
    Notification,
    SupportTicket,
    TicketMessage,
    TicketPriority,
    TicketStatus,
    User,
    UserSession,
    UserStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== HELPER FUNCTIONS ====================

def log_audit(db: Session, user_id: int, action: str, entity_type: str = None,
              entity_id: int = None, old_values: dict = None, new_values: dict = None,
              ip_address: str = None):
    """Audit log kaydi"""
    try:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        db.add(audit)
    except Exception as e:
        logger.error(f"Audit log hatasi: {e}")


class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    
    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) < 2 or len(v) > 50:
                raise ValueError("Gorunen isim 2-50 karakter olmali")
        return v
    
    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError("Bio en fazla 500 karakter olmali")
        return v


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    
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


class TicketCreateRequest(BaseModel):
    subject: str
    message: str
    priority: str = "medium"
    server_id: Optional[int] = None
    
    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v):
        v = v.strip()
        if len(v) < 5 or len(v) > 200:
            raise ValueError("Konu 5-200 karakter olmali")
        return v
    
    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        if len(v) < 20:
            raise ValueError("Mesaj en az 20 karakter olmali")
        if len(v) > 5000:
            raise ValueError("Mesaj en fazla 5000 karakter olmali")
        return v


class TicketReplyRequest(BaseModel):
    content: str
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if len(v) < 10:
            raise ValueError("Mesaj en az 10 karakter olmali")
        if len(v) > 5000:
            raise ValueError("Mesaj en fazla 5000 karakter olmali")
        return v


class SteamLinkRequest(BaseModel):
    steam_id: str
    
    @field_validator("steam_id")
    @classmethod
    def validate_steam_id(cls, v):
        # STEAM_X:Y:Z formatı
        if not re.match(r'^STEAM_[0-5]:[01]:\d+$', v):
            raise ValueError("Gecersiz SteamID formati (STEAM_X:Y:Z)")
        return v


class NotificationSettingsRequest(BaseModel):
    email_notifications: Optional[bool] = None
    forum_notifications: Optional[bool] = None
    payment_notifications: Optional[bool] = None
    server_notifications: Optional[bool] = None


@router.get("/profile")
async def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Kullanici profili"""
    # Aktif sunucu sayisi
    server_count = db.query(GameServer).filter(
        GameServer.owner_id == current_user.id,
        GameServer.status.notin_([ServerStatus.DELETED, ServerStatus.EXPIRED])
    ).count() if hasattr(GameServer, 'status') else 0
    
    # Okunmamis bildirim sayisi
    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    # Acik destek talebi sayisi
    open_tickets = db.query(SupportTicket).filter(
        SupportTicket.user_id == current_user.id,
        SupportTicket.status.in_([TicketStatus.OPEN, TicketStatus.WAITING, TicketStatus.ANSWERED])
    ).count()
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "avatar": current_user.avatar,
        "bio": current_user.bio,
        "steam_id": current_user.steam_id,
        "role": current_user.role.value,
        "status": current_user.status.value,
        "balance": current_user.balance,
        "post_count": current_user.post_count,
        "reputation": current_user.reputation,
        "two_factor_enabled": current_user.two_factor_enabled,
        "email_verified": current_user.email_verified,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        "created_at": current_user.created_at.isoformat(),
        "stats": {
            "server_count": server_count,
            "unread_notifications": unread_notifications,
            "open_tickets": open_tickets
        }
    }


# Burada GameServer.status kontrolü için import gerekebilir
from app.models.database import ServerStatus


@router.put("/profile")
async def update_profile(data: ProfileUpdateRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Profil guncelle"""
    old_values = {}
    new_values = {}
    
    if data.display_name and data.display_name != current_user.display_name:
        old_values["display_name"] = current_user.display_name
        new_values["display_name"] = data.display_name
        current_user.display_name = data.display_name
    
    if data.email and data.email != current_user.email:
        existing = db.query(User).filter(User.email == data.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu e-posta adresi kullaniliyor")
        old_values["email"] = current_user.email
        new_values["email"] = data.email
        current_user.email = data.email
        current_user.email_verified = False  # Yeni email dogrulanmali
    
    if data.bio is not None:
        old_values["bio"] = current_user.bio
        new_values["bio"] = data.bio
        current_user.bio = data.bio
    
    if new_values:
        client_ip = request.client.host if request.client else None
        log_audit(db, current_user.id, "profile_update", "user", current_user.id,
                  old_values=old_values, new_values=new_values, ip_address=client_ip)
    
    db.commit()
    
    logger.info(f"Profil guncellendi: {current_user.username}")
    
    return {"success": True, "message": "Profil guncellendi"}


@router.post("/change-password")
async def change_password(data: PasswordChangeRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Sifre degistir"""
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Mevcut sifre hatali")
    
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Yeni sifreler eslesmiyor")
    
    if data.current_password == data.new_password:
        raise HTTPException(status_code=400, detail="Yeni sifre eskisiyle ayni olamaz")
    
    current_user.password_hash = hash_password(data.new_password)
    current_user.password_changed_at = datetime.utcnow()
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "password_change", "user", current_user.id,
              ip_address=client_ip)
    
    db.commit()
    
    logger.info(f"Sifre degistirildi: {current_user.username}")
    
    return {"success": True, "message": "Sifre degistirildi"}


@router.get("/tickets")
async def my_tickets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    tickets = db.query(SupportTicket).filter(SupportTicket.user_id == current_user.id).order_by(SupportTicket.updated_at.desc()).all()
    return {"tickets": [{"id": t.id, "subject": t.subject, "status": t.status.value, "priority": t.priority.value, "created_at": t.created_at.isoformat(), "updated_at": t.updated_at.isoformat()} for t in tickets]}


@router.post("/tickets")
async def create_ticket(data: TicketCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    if len(data.subject) < 5:
        raise HTTPException(status_code=400, detail="Konu en az 5 karakter olmali")
    if len(data.message) < 20:
        raise HTTPException(status_code=400, detail="Mesaj en az 20 karakter olmali")
    
    try:
        priority = TicketPriority(data.priority)
    except ValueError:
        priority = TicketPriority.MEDIUM
    
    ticket = SupportTicket(user_id=current_user.id, subject=data.subject, priority=priority)
    db.add(ticket)
    db.flush()
    
    message = TicketMessage(ticket_id=ticket.id, user_id=current_user.id, content=data.message)
    db.add(message)
    db.commit()
    
    return {"success": True, "ticket_id": ticket.id, "message": "Destek talebi olusturuldu"}


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id, SupportTicket.user_id == current_user.id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Destek talebi bulunamadi")
    
    messages = db.query(TicketMessage).filter(TicketMessage.ticket_id == ticket_id).order_by(TicketMessage.created_at).all()
    
    return {
        "ticket": {
            "id": ticket.id,
            "subject": ticket.subject,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat()
        },
        "messages": [{
            "id": m.id,
            "content": m.content,
            "is_staff_reply": m.is_staff_reply,
            "created_at": m.created_at.isoformat()
        } for m in messages]
    }


@router.post("/tickets/{ticket_id}/reply")
async def reply_ticket(ticket_id: int, data: TicketReplyRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Destek talebine yanit ver"""
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id, SupportTicket.user_id == current_user.id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Destek talebi bulunamadi")
    
    if ticket.status == TicketStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Bu talep kapatilmis")
    
    message = TicketMessage(ticket_id=ticket_id, user_id=current_user.id, content=data.content, is_staff_reply=False)
    db.add(message)
    
    ticket.status = TicketStatus.WAITING
    ticket.updated_at = datetime.utcnow()
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "ticket_reply", "support_ticket", ticket_id,
              ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": "Yanit gonderildi"}


@router.post("/tickets/{ticket_id}/close")
async def close_ticket(ticket_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Destek talebini kapat"""
    ticket = db.query(SupportTicket).filter(
        SupportTicket.id == ticket_id,
        SupportTicket.user_id == current_user.id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Destek talebi bulunamadi")
    
    if ticket.status == TicketStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Bu talep zaten kapali")
    
    ticket.status = TicketStatus.CLOSED
    ticket.closed_at = datetime.utcnow()
    ticket.updated_at = datetime.utcnow()
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "ticket_close", "support_ticket", ticket_id,
              ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": "Destek talebi kapatildi"}


# ==================== AVATAR ====================

@router.post("/avatar")
async def upload_avatar(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Avatar yukle - Smart Media sistemiyle entegre"""
    # Dosya tipi kontrolu
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Sadece JPEG, PNG, GIF ve WebP dosyalari yuklenebilir")

    # Boyut kontrolu (5MB raw, resize sonrasi kucuk olacak)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dosya boyutu 5MB'dan buyuk olamaz")

    # Static images klasorune kaydet (Smart Media uyumlu)
    avatar_dir = Path("/var/www/agtrmerkezi/static/images/avatars")
    avatar_dir.mkdir(parents=True, exist_ok=True)

    # Hem PNG hem WebP olustur (Smart Media uyumlu)
    base_filename = f"user_{current_user.id}_{secrets.token_hex(8)}"
    png_path = avatar_dir / f"{base_filename}.png"
    webp_path = avatar_dir / f"{base_filename}.webp"

    # Resmi isle (200x200, kaliteli)
    if PIL_AVAILABLE:
        try:
            img = Image.open(BytesIO(content))
            # RGBA'ya cevir (transparanlik icin)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Kare yap (ortadan kes)
            width, height = img.size
            min_dim = min(width, height)
            left = (width - min_dim) // 2
            top = (height - min_dim) // 2
            img = img.crop((left, top, left + min_dim, top + min_dim))

            # 200x200 resize
            img = img.resize((200, 200), Image.Resampling.LANCZOS)

            # PNG kaydet
            img.save(png_path, 'PNG', optimize=True, compress_level=9)

            # WebP kaydet (daha kucuk)
            img.save(webp_path, 'WEBP', quality=85, method=6)

            logger.info(f"Avatar resized and saved: {base_filename}")
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise HTTPException(status_code=500, detail="Gorsel isleme hatasi")
    else:
        raise HTTPException(status_code=500, detail="Gorsel isleme destegi yok (PIL gerekli)")

    # Eski avatarlari sil
    if current_user.avatar:
        # Eski format (/uploads/avatars/...)
        old_upload_path = Path(settings.UPLOAD_PATH) / current_user.avatar
        if old_upload_path.exists():
            try:
                old_upload_path.unlink()
            except:
                pass

        # Yeni format (/static/images/avatars/...)
        if current_user.avatar.startswith("avatars/"):
            old_static_path = Path("/var/www/agtrmerkezi/static/images") / current_user.avatar
            if old_static_path.exists():
                try:
                    old_static_path.unlink()
                except:
                    pass

    # DB'ye kaydet (static/images'e gore relative path)
    current_user.avatar = f"avatars/{base_filename}.png"

    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "avatar_upload", "user", current_user.id,
              new_values={"avatar": current_user.avatar}, ip_address=client_ip)

    db.commit()

    logger.info(f"Avatar yuklendi: {current_user.username}")

    return {
        "success": True,
        "avatar": f"/static/images/{current_user.avatar}",
        "avatar_webp": f"/static/images/avatars/{base_filename}.webp"
    }


@router.delete("/avatar")
async def delete_avatar(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Avatar sil"""
    if not current_user.avatar:
        raise HTTPException(status_code=400, detail="Avatar bulunamadi")

    # Hem eski hem yeni formattaki dosyalari sil
    # Eski format: /uploads/avatars/...
    old_upload_path = Path(settings.UPLOAD_PATH) / current_user.avatar
    if old_upload_path.exists():
        try:
            old_upload_path.unlink()
        except:
            pass

    # Yeni format: /static/images/avatars/...
    if current_user.avatar.startswith("avatars/"):
        static_path = Path("/var/www/agtrmerkezi/static/images") / current_user.avatar
        if static_path.exists():
            try:
                # PNG ve WebP versiyonlarini sil
                static_path.unlink()
                webp_path = static_path.with_suffix('.webp')
                if webp_path.exists():
                    webp_path.unlink()
            except:
                pass

    old_avatar = current_user.avatar
    current_user.avatar = None

    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "avatar_delete", "user", current_user.id,
              old_values={"avatar": old_avatar}, ip_address=client_ip)

    db.commit()

    return {"success": True, "message": "Avatar silindi"}


# ==================== STEAM ====================

@router.post("/link-steam")
async def link_steam(data: SteamLinkRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Steam hesabi bagla"""
    # Baska kullanici kullanıyor mu?
    existing = db.query(User).filter(
        User.steam_id == data.steam_id,
        User.id != current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Bu SteamID baska bir hesaba bagli")
    
    old_steam = current_user.steam_id
    current_user.steam_id = data.steam_id
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "steam_link", "user", current_user.id,
              old_values={"steam_id": old_steam},
              new_values={"steam_id": data.steam_id},
              ip_address=client_ip)
    
    db.commit()
    
    logger.info(f"Steam baglandi: {current_user.username} -> {data.steam_id}")
    
    return {"success": True, "message": "Steam hesabi baglandi", "steam_id": data.steam_id}


@router.delete("/unlink-steam")
async def unlink_steam(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Steam hesabi baglantisini kaldir"""
    if not current_user.steam_id:
        raise HTTPException(status_code=400, detail="Steam hesabi bagli degil")
    
    old_steam = current_user.steam_id
    current_user.steam_id = None
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "steam_unlink", "user", current_user.id,
              old_values={"steam_id": old_steam}, ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": "Steam baglantisi kaldirildi"}


# ==================== NOTIFICATIONS ====================

@router.get("/notifications")
async def get_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Bildirimler"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    total = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    notifications = query.order_by(desc(Notification.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "notifications": [{
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "message": n.message,
            "link": n.link,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        } for n in notifications],
        "unread_count": unread_count,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Bildirimi okundu isaretle"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Bildirim bulunamadi")
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return {"success": True}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Tum bildirimleri okundu isaretle"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    
    db.commit()
    
    return {"success": True, "message": "Tum bildirimler okundu olarak isaretlendi"}


@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Bildirimi sil"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Bildirim bulunamadi")
    
    db.delete(notification)
    db.commit()
    
    return {"success": True}


# ==================== SESSIONS ====================

@router.get("/sessions")
async def get_sessions(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Aktif oturumlar"""
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).order_by(desc(UserSession.last_activity)).all()
    
    # Mevcut oturumun token'ini al
    current_token = request.cookies.get("access_token")
    
    return {
        "sessions": [{
            "id": s.id,
            "ip_address": s.ip_address,
            "user_agent": s.user_agent[:100] if s.user_agent else None,
            "device_type": s.device_type,
            "location": s.location,
            "created_at": s.created_at.isoformat(),
            "last_activity": s.last_activity.isoformat() if s.last_activity else None,
            "is_current": current_token and s.token_hash == hash_token(current_token)
        } for s in sessions]
    }


@router.delete("/sessions/{session_id}")
async def revoke_session(session_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Oturumu sonlandir"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Oturum bulunamadi")
    
    session.is_active = False
    session.revoked_at = datetime.utcnow()
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "session_revoke", "user_session", session_id,
              ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": "Oturum sonlandirildi"}


@router.delete("/sessions")
async def revoke_all_sessions(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Diger tum oturumlari sonlandir"""
    # Mevcut session haric tumunu kapat
    current_token = request.cookies.get("access_token")
    current_token_hash = hash_token(current_token) if current_token else None
    
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True,
        UserSession.token_hash != current_token_hash
    ).update({"is_active": False, "revoked_at": datetime.utcnow()})
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "sessions_revoke_all", "user", current_user.id,
              ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": "Diger tum oturumlar sonlandirildi"}


# ==================== PUBLIC PROFILE ====================

@router.get("/users/{username}")
async def get_public_profile(username: str, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    """Public profil goruntule"""
    user = db.query(User).filter(User.username == username.lower()).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    if user.status == UserStatus.BANNED:
        return {
            "id": user.id,
            "username": user.username,
            "display_name": "Yasakli Kullanici",
            "status": "banned",
            "message": "Bu kullanici yasaklanmis"
        }
    
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar": user.avatar,
        "bio": user.bio,
        "role": user.role.value,
        "post_count": user.post_count,
        "reputation": user.reputation,
        "created_at": user.created_at.isoformat(),
        "last_seen": user.last_login.isoformat() if user.last_login else None
    }


# ==================== ACTIVITY LOG ====================

@router.get("/activity")
async def get_activity(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Hesap aktivite gecmisi"""
    query = db.query(AuditLog).filter(AuditLog.user_id == current_user.id)
    
    total = query.count()
    activities = query.order_by(desc(AuditLog.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "activities": [{
            "id": a.id,
            "action": a.action,
            "entity_type": a.entity_type,
            "ip_address": a.ip_address,
            "created_at": a.created_at.isoformat()
        } for a in activities],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }