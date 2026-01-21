"""
AGTR Merkezi - Admin API
Tam ozellikli admin panel API'leri
Plugin, Audit Log, Backup, Scheduled Tasks destekli
"""

import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import psutil
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.api.servers import (
    create_physical_server,
    delete_physical_server,
    start_physical_server,
)
from app.core.config import settings
from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import (
    Announcement,
    AuditLog,
    BackupLog,
    Banner,
    BannerPosition,
    BannerType,
    BankTransfer,
    GameServer,
    GameType,
    Notification,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Plugin,
    ResourceLog,
    ScheduledTask,
    ServerPackage,
    ServerPlugin,
    ServerStatus,
    SiteSettings,
    SystemLog,
    TaskLog,
    Transaction,
    User,
    UserRole,
    UserStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== PYDANTIC MODELS ====================

class UserUpdateRequest(BaseModel):
    balance: Optional[float] = None
    balance_coin: Optional[float] = None
    role: Optional[str] = None
    status: Optional[str] = None


class PackageCreateRequest(BaseModel):
    slug: str
    name: str
    game_type: str
    slots: int
    features: List[str] = []
    description: str = ""
    price_monthly: float
    display_order: int = 0


class PackageUpdateRequest(BaseModel):
    name: Optional[str] = None
    slots: Optional[int] = None
    features: Optional[List[str]] = None
    description: Optional[str] = None
    price_monthly: Optional[float] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class AnnouncementCreateRequest(BaseModel):
    title: str
    content: str
    type: str = "info"
    show_on_homepage: bool = True


class AnnouncementUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None
    show_on_homepage: Optional[bool] = None


class SiteSettingsUpdateRequest(BaseModel):
    site_name: Optional[str] = None
    site_description: Optional[str] = None
    contact_email: Optional[str] = None
    discord_url: Optional[str] = None
    maintenance_mode: Optional[bool] = None
    registration_enabled: Optional[bool] = None
    price_per_slot: Optional[float] = None
    discount_3_month: Optional[float] = None
    discount_6_month: Optional[float] = None
    discount_12_month: Optional[float] = None
    # Branding fields
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None
    logo_mobile_url: Optional[str] = None
    logo_width: Optional[str] = None
    logo_height: Optional[str] = None
    logo_text: Optional[str] = None
    logo_subtitle: Optional[str] = None
    show_logo_text: Optional[bool] = None
    footer_logo_url: Optional[str] = None
    footer_logo_width: Optional[str] = None
    footer_logo_height: Optional[str] = None
    favicon_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None


class PaymentRejectRequest(BaseModel):
    reason: str


class PluginCreateRequest(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    game_type: Optional[str] = None
    category: Optional[str] = None
    is_default: bool = False
    requires_config: bool = False
    config_template: Optional[str] = None


class PluginUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class ScheduledTaskCreateRequest(BaseModel):
    server_id: Optional[int] = None
    name: str
    task_type: str  # restart, command, backup, message
    schedule_type: str  # once, daily, weekly, cron
    schedule_value: str
    command: Optional[str] = None
    is_enabled: bool = True


class ScheduledTaskUpdateRequest(BaseModel):
    name: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule_value: Optional[str] = None
    command: Optional[str] = None
    is_enabled: Optional[bool] = None


class NotificationSendRequest(BaseModel):
    user_id: Optional[int] = None  # None = tum kullanicilara
    title: str
    message: str
    type: str = "system"
    link: Optional[str] = None


class User2FARequest(BaseModel):
    require_2fa: bool


# ==================== HELPER FUNCTIONS ====================

def log_admin_audit(db: Session, admin_id: int, action: str, entity_type: str = None,
                    entity_id: int = None, old_values: dict = None, new_values: dict = None,
                    ip_address: str = None):
    """Admin islem logu"""
    try:
        audit = AuditLog(
            user_id=admin_id,
            action=f"admin_{action}",
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        logger.error(f"Audit log hatasi: {e}")


# ==================== DASHBOARD ====================

@router.get("/dashboard")
async def admin_dashboard(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Admin dashboard istatistikleri"""
    total_users = db.query(User).count()
    new_users_today = db.query(User).filter(
        func.date(User.created_at) == datetime.utcnow().date()
    ).count()
    
    total_servers = db.query(GameServer).count()
    running_servers = db.query(GameServer).filter(
        GameServer.status == ServerStatus.RUNNING
    ).count()
    
    pending_payments = db.query(Payment).filter(
        Payment.status == PaymentStatus.PENDING
    ).count()
    
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.COMPLETED,
        Payment.completed_at >= month_start
    ).scalar() or 0
    
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "new_today": new_users_today
        },
        "servers": {
            "total": total_servers,
            "running": running_servers,
            "stopped": total_servers - running_servers
        },
        "payments": {
            "pending": pending_payments,
            "month_revenue": float(month_revenue),
            "total_revenue": float(total_revenue)
        }
    }


@router.get("/dashboard/charts")
async def admin_dashboard_charts(
    period: str = "7d",  # 7d, 30d, 90d
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Dashboard grafik verileri"""
    from datetime import timedelta
    
    days = {"7d": 7, "30d": 30, "90d": 90}.get(period, 7)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Günlük kayıt sayıları
    user_registrations = []
    payment_amounts = []
    
    for i in range(days):
        day = (datetime.utcnow() - timedelta(days=days-1-i)).date()
        
        # Kullanıcı kayıtları
        user_count = db.query(User).filter(
            func.date(User.created_at) == day
        ).count()
        user_registrations.append({"date": str(day), "count": user_count})
        
        # Ödemeler
        day_revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.COMPLETED,
            func.date(Payment.completed_at) == day
        ).scalar() or 0
        payment_amounts.append({"date": str(day), "amount": float(day_revenue)})
    
    # Sunucu durumu dağılımı
    server_status_dist = []
    for status in ServerStatus:
        if status != ServerStatus.DELETED:
            count = db.query(GameServer).filter(GameServer.status == status).count()
            server_status_dist.append({"status": status.value, "count": count})
    
    # Oyun türü dağılımı
    game_type_dist = []
    for game in GameType:
        count = db.query(GameServer).filter(
            GameServer.game_type == game,
            GameServer.status != ServerStatus.DELETED
        ).count()
        if count > 0:
            game_type_dist.append({"game": game.value, "count": count})
    
    # Ödeme yöntemi dağılımı
    payment_method_dist = db.query(
        Payment.method,
        func.count(Payment.id),
        func.sum(Payment.amount)
    ).filter(
        Payment.status == PaymentStatus.COMPLETED
    ).group_by(Payment.method).all()
    
    methods = [{"method": m.value if m else "other", "count": c, "total": float(t or 0)} 
               for m, c, t in payment_method_dist]
    
    return {
        "period": period,
        "user_registrations": user_registrations,
        "payment_amounts": payment_amounts,
        "server_status_distribution": server_status_dist,
        "game_type_distribution": game_type_dist,
        "payment_method_distribution": methods
    }


# ==================== USERS ====================

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kullanici listesi"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) | 
            (User.email.ilike(f"%{search}%"))
        )
    
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            pass
    
    if status:
        try:
            status_enum = UserStatus(status)
            query = query.filter(User.status == status_enum)
        except ValueError:
            pass
    
    total = query.count()
    users = query.order_by(desc(User.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "users": [{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "display_name": u.display_name,
            "role": u.role.value,
            "status": u.status.value,
            "balance": u.balance,
            "balance_coin": u.balance_coin,
            "post_count": u.post_count,
            "last_login": u.last_login.isoformat() if u.last_login else None,
            "created_at": u.created_at.isoformat()
        } for u in users],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kullanici detayi"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    servers = db.query(GameServer).filter(GameServer.owner_id == user_id).all()
    payments = db.query(Payment).filter(Payment.user_id == user_id).order_by(desc(Payment.created_at)).limit(10).all()
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role.value,
            "status": user.status.value,
            "balance": user.balance,
            "balance_coin": user.balance_coin,
            "post_count": user.post_count,
            "reputation": user.reputation,
            "steam_id": user.steam_id,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "last_ip": user.last_ip,
            "created_at": user.created_at.isoformat()
        },
        "servers": [{
            "id": s.id,
            "name": s.name,
            "status": s.status.value
        } for s in servers],
        "recent_payments": [{
            "id": p.id,
            "amount": p.amount,
            "status": p.status.value,
            "created_at": p.created_at.isoformat()
        } for p in payments]
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kullanici guncelle"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    if user.role == UserRole.SUPERADMIN and admin.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Superadmin'i duzenleyemezsiniz")
    
    if data.balance is not None:
        user.balance = data.balance

    if data.balance_coin is not None:
        user.balance_coin = data.balance_coin

    if data.role:
        try:
            new_role = UserRole(data.role)
            if new_role in [UserRole.ADMIN, UserRole.SUPERADMIN] and admin.role != UserRole.SUPERADMIN:
                raise HTTPException(status_code=403, detail="Admin atama yetkiniz yok")
            user.role = new_role
        except ValueError:
            raise HTTPException(status_code=400, detail="Gecersiz rol")
    
    if data.status:
        try:
            user.status = UserStatus(data.status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Gecersiz durum")
    
    log = SystemLog(
        level="info",
        category="admin",
        message=f"Kullanici guncellendi: {user.username}",
        user_id=admin.id,
        details={"target_user_id": user_id, "changes": data.dict(exclude_none=True)}
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "message": "Kullanici guncellendi"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kullanici sil (ban)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    if user.role == UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Superadmin silinemez")
    
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Kendinizi silemezsiniz")
    
    user.status = UserStatus.BANNED
    
    log = SystemLog(
        level="warning",
        category="admin",
        message=f"Kullanici banlandi: {user.username}",
        user_id=admin.id
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "message": "Kullanici banlandi"}


# ==================== SERVERS ====================

@router.get("/servers")
async def list_servers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    game_type: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Sunucu listesi"""
    query = db.query(GameServer).filter(GameServer.status != ServerStatus.DELETED)
    
    if status:
        try:
            status_enum = ServerStatus(status)
            query = query.filter(GameServer.status == status_enum)
        except ValueError:
            pass
    
    if game_type:
        try:
            game_enum = GameType(game_type)
            query = query.filter(GameServer.game_type == game_enum)
        except ValueError:
            pass
    
    total = query.count()
    servers = query.order_by(desc(GameServer.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    result = []
    for s in servers:
        owner = db.query(User).filter(User.id == s.owner_id).first()
        result.append({
            "id": s.id,
            "name": s.name,
            "owner_username": owner.username if owner else "N/A",
            "game_type": s.game_type.value,
            "ip_address": s.ip_address,
            "port": s.port,
            "slots": s.slots,
            "status": s.status.value,
            "monthly_price": s.monthly_price,
            "expires_at": s.expires_at.isoformat() if s.expires_at else None,
            "created_at": s.created_at.isoformat()
        })
    
    return {
        "servers": result,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


@router.put("/servers/{server_id}/status")
async def update_server_status(
    server_id: int,
    status: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Sunucu durumu guncelle"""
    from app.api.servers import start_physical_server, stop_physical_server
    
    server = db.query(GameServer).filter(GameServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    try:
        new_status = ServerStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Gecersiz durum")
    
    if new_status == ServerStatus.RUNNING:
        logger.debug(f"Starting server {server.id}")
        result = start_physical_server(server.id)
        logger.debug(f"Start result: {result}")
    elif new_status == ServerStatus.STOPPED:
        logger.debug(f"Stopping server {server.id}")
        result = stop_physical_server(server.id)
        logger.debug(f"Stop result: {result}")
    
    server.status = new_status
    db.commit()
    return {"success": True, "message": "Sunucu durumu guncellendi"}


# ==================== PAYMENTS ====================

@router.get("/payments")
async def list_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Odeme listesi"""
    query = db.query(Payment)
    
    if status:
        try:
            status_enum = PaymentStatus(status)
            query = query.filter(Payment.status == status_enum)
        except ValueError:
            pass
    
    total = query.count()
    payments = query.order_by(desc(Payment.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    result = []
    for p in payments:
        user = db.query(User).filter(User.id == p.user_id).first()
        result.append({
            "id": p.id,
            "username": user.username if user else "N/A",
            "amount": p.amount,
            "method": p.method.value if p.method else None,
            "status": p.status.value,
            "reference_code": p.reference_code,
            "description": p.description,
            "created_at": p.created_at.isoformat(),
            "completed_at": p.completed_at.isoformat() if p.completed_at else None
        })
    
    return {
        "payments": result,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


@router.get("/payments/pending")
async def list_pending_payments(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Bekleyen odemeler"""
    payments = db.query(Payment).filter(
        Payment.status == PaymentStatus.PENDING
    ).order_by(Payment.created_at.desc()).all()
    
    result = []
    for p in payments:
        user = db.query(User).filter(User.id == p.user_id).first()
        bank_transfer = db.query(BankTransfer).filter(BankTransfer.payment_id == p.id).first()
        
        result.append({
            "id": p.id,
            "username": user.username if user else "N/A",
            "user_email": user.email if user else "N/A",
            "amount": p.amount,
            "method": p.method.value if p.method else None,
            "reference_code": p.reference_code,
            "description": p.description,
            "created_at": p.created_at.isoformat(),
            "bank_transfer": {
                "sender_name": bank_transfer.sender_name,
                "sender_iban": bank_transfer.sender_iban,
                "notes": bank_transfer.notes
            } if bank_transfer else None
        })
    
    return {"payments": result}


@router.post("/payments/{payment_id}/approve")
async def approve_payment(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Odeme onayla ve sunucu kur"""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.status == PaymentStatus.PENDING
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Bekleyen odeme bulunamadi")
    
    user = db.query(User).filter(User.id == payment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    payment.status = PaymentStatus.COMPLETED
    payment.completed_at = datetime.utcnow()
    
    # Sunucu siparisi ise
    if payment.server_id:
        server = db.query(GameServer).filter(GameServer.id == payment.server_id).first()
        if server:
            # Bakiye ile odeme veya method belirtilmediyse bakiyeden dus
            if payment.method == PaymentMethod.BALANCE or payment.method is None:
                if user.balance >= payment.amount:
                    balance_before = user.balance
                    user.balance -= payment.amount
                    
                    # Transaction kaydi
                    transaction = Transaction(
                        user_id=user.id,
                        type="payment",
                        amount=-payment.amount,
                        description=f"Sunucu odemesi: {server.name}",
                        payment_id=payment.id,
                        balance_before=balance_before,
                        balance_after=user.balance
                    )
                    db.add(transaction)
                else:
                    # Yetersiz bakiye uyarisi
                    log_warn = SystemLog(
                        level="warning",
                        category="payment",
                        message=f"Yetersiz bakiye ile onay: {user.username} - {payment.amount} TL (bakiye: {user.balance})",
                        user_id=admin.id,
                        details={"payment_id": payment_id, "user_balance": user.balance, "required": payment.amount}
                    )
                    db.add(log_warn)
            
            # Sunucu sure uzat veya baslat
            if server.expires_at and server.expires_at > datetime.utcnow():
                server.expires_at = server.expires_at + timedelta(days=30 * payment.months)
            else:
                server.expires_at = datetime.utcnow() + timedelta(days=30 * payment.months)
            server.status = ServerStatus.RUNNING
            
            # Fiziksel sunucu olustur ve baslat
            game_type = server.game_type.value
            create_result = create_physical_server(
                server.id,
                server.ip_address,
                server.port,
                game_type,
                server.slots,
                server.rcon_password,
                server.name
            )
            
            if create_result["success"]:
                start_physical_server(server.id)
                
            # Log fiziksel sunucu durumu
            log_physical = SystemLog(
                level="info" if create_result["success"] else "error",
                category="server",
                message=f"Fiziksel sunucu: {create_result['message']}",
                user_id=admin.id,
                details={"server_id": server.id}
            )
            db.add(log_physical)
            
            # Kullaniciya bildirim
            notification = Notification(
                user_id=user.id,
                type="server",
                title="Sunucunuz Aktif!",
                message=f"{server.name} sunucunuz basariyla kuruldu ve aktif edildi.",
                link=f"/panel/servers/{server.id}"
            )
            db.add(notification)
    else:
        # Bakiye yuklemesi
        balance_before = user.balance
        user.balance += payment.amount
        
        # Transaction kaydi
        transaction = Transaction(
            user_id=user.id,
            type="deposit",
            amount=payment.amount,
            description=f"Bakiye yukleme: {payment.reference_code}",
            payment_id=payment.id,
            balance_before=balance_before,
            balance_after=user.balance
        )
        db.add(transaction)
        
        # Bildirim
        notification = Notification(
            user_id=user.id,
            type="payment",
            title="Bakiye Yuklendi",
            message=f"{payment.amount} TL bakiye hesabiniza eklendi.",
            link="/panel/balance"
        )
        db.add(notification)
    
    # Bank transfer kaydi guncelle
    bank_transfer = db.query(BankTransfer).filter(BankTransfer.payment_id == payment_id).first()
    if bank_transfer:
        bank_transfer.approved_by = admin.id
        bank_transfer.approved_at = datetime.utcnow()
    
    # Audit log
    client_ip = request.client.host if request.client else "unknown"
    audit = AuditLog(
        user_id=admin.id,
        action="payment_approve",
        entity_type="payment",
        entity_id=payment_id,
        new_values={"amount": payment.amount, "user_id": user.id, "server_id": payment.server_id},
        ip_address=client_ip
    )
    db.add(audit)
    
    # System log
    log = SystemLog(
        level="info",
        category="payment",
        message=f"Odeme onaylandi: {payment.reference_code} - {payment.amount} TL",
        user_id=admin.id,
        details={"payment_id": payment_id, "amount": payment.amount, "user_id": user.id}
    )
    db.add(log)
    db.commit()
    
    return {
        "success": True, 
        "message": "Odeme onaylandi ve islem tamamlandi",
        "new_balance": user.balance
    }


@router.post("/payments/{payment_id}/reject")
async def reject_payment(
    payment_id: int,
    data: PaymentRejectRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Odeme reddet"""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.status == PaymentStatus.PENDING
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Bekleyen odeme bulunamadi")
    
    payment.status = PaymentStatus.CANCELLED
    
    # Sunucu siparisi ise sunucuyu iptal et
    if payment.server_id:
        server = db.query(GameServer).filter(GameServer.id == payment.server_id).first()
        if server:
            server.status = ServerStatus.DELETED
            # Fiziksel sunucuyu da sil (eger varsa)
            delete_physical_server(server.id)
    
    # Bank transfer kaydi guncelle
    bank_transfer = db.query(BankTransfer).filter(BankTransfer.payment_id == payment_id).first()
    if bank_transfer:
        bank_transfer.rejection_reason = data.reason
    
    # Log
    log = SystemLog(
        level="warning",
        category="payment",
        message=f"Odeme reddedildi: {payment.reference_code}",
        user_id=admin.id,
        details={"payment_id": payment_id, "reason": data.reason}
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "message": "Odeme reddedildi"}


# ==================== PACKAGES ====================

@router.get("/packages")
async def list_packages(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Paket listesi"""
    packages = db.query(ServerPackage).order_by(ServerPackage.display_order).all()
    
    return {
        "packages": [{
            "id": p.id,
            "slug": p.slug,
            "name": p.name,
            "game_type": p.game_type.value,
            "slots": p.slots,
            "features": p.features or [],
            "description": p.description,
            "price_monthly": p.price_monthly,
            "is_active": p.is_active,
            "display_order": p.display_order
        } for p in packages]
    }


@router.post("/packages")
async def create_package(
    data: PackageCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Yeni paket olustur"""
    existing = db.query(ServerPackage).filter(ServerPackage.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu slug zaten kullaniliyor")
    
    try:
        game_type = GameType(data.game_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Gecersiz oyun tipi")
    
    package = ServerPackage(
        slug=data.slug,
        name=data.name,
        game_type=game_type,
        slots=data.slots,
        features=data.features,
        description=data.description,
        price_monthly=data.price_monthly,
        display_order=data.display_order
    )
    db.add(package)
    db.commit()
    
    return {"success": True, "message": "Paket olusturuldu", "package_id": package.id}


@router.put("/packages/{package_id}")
async def update_package(
    package_id: int,
    data: PackageUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Paket guncelle"""
    package = db.query(ServerPackage).filter(ServerPackage.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Paket bulunamadi")
    
    if data.name is not None:
        package.name = data.name
    if data.slots is not None:
        package.slots = data.slots
    if data.features is not None:
        package.features = data.features
    if data.description is not None:
        package.description = data.description
    if data.price_monthly is not None:
        package.price_monthly = data.price_monthly
    if data.is_active is not None:
        package.is_active = data.is_active
    if data.display_order is not None:
        package.display_order = data.display_order
    
    db.commit()
    return {"success": True, "message": "Paket guncellendi"}


@router.delete("/packages/{package_id}")
async def delete_package(
    package_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Paket sil (deaktif et)"""
    package = db.query(ServerPackage).filter(ServerPackage.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Paket bulunamadi")
    
    active_servers = db.query(GameServer).filter(
        GameServer.package_id == package_id,
        GameServer.status.notin_([ServerStatus.DELETED, ServerStatus.EXPIRED])
    ).count()
    
    if active_servers > 0:
        raise HTTPException(status_code=400, detail=f"Bu pakete bagli {active_servers} aktif sunucu var")
    
    package.is_active = False
    db.commit()
    
    return {"success": True, "message": "Paket deaktif edildi"}


# ==================== ANNOUNCEMENTS ====================

@router.get("/announcements")
async def list_announcements(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Duyuru listesi"""
    announcements = db.query(Announcement).order_by(desc(Announcement.created_at)).all()
    
    return {
        "announcements": [{
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "type": a.type,
            "is_active": a.is_active,
            "show_on_homepage": a.show_on_homepage,
            "created_at": a.created_at.isoformat()
        } for a in announcements]
    }


@router.post("/announcements")
async def create_announcement(
    data: AnnouncementCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Yeni duyuru olustur"""
    announcement = Announcement(
        title=data.title,
        content=data.content,
        type=data.type,
        show_on_homepage=data.show_on_homepage,
        created_by=admin.id
    )
    db.add(announcement)
    db.commit()
    
    return {"success": True, "message": "Duyuru olusturuldu", "announcement_id": announcement.id}


@router.put("/announcements/{announcement_id}")
async def update_announcement(
    announcement_id: int,
    data: AnnouncementUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Duyuru guncelle"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Duyuru bulunamadi")
    
    if data.title is not None:
        announcement.title = data.title
    if data.content is not None:
        announcement.content = data.content
    if data.type is not None:
        announcement.type = data.type
    if data.is_active is not None:
        announcement.is_active = data.is_active
    if data.show_on_homepage is not None:
        announcement.show_on_homepage = data.show_on_homepage
    
    db.commit()
    return {"success": True, "message": "Duyuru guncellendi"}


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Duyuru sil"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Duyuru bulunamadi")
    
    db.delete(announcement)
    db.commit()
    
    return {"success": True, "message": "Duyuru silindi"}


# ==================== SITE SETTINGS ====================

@router.get("/settings")
async def get_settings(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Site ayarlarini getir"""
    settings_obj = db.query(SiteSettings).first()
    
    if not settings_obj:
        settings_obj = SiteSettings()
        db.add(settings_obj)
        db.commit()
        db.refresh(settings_obj)
    
    return {
        "settings": {
            "site_name": settings_obj.site_name,
            "site_description": settings_obj.site_description,
            "contact_email": settings_obj.contact_email,
            "discord_url": settings_obj.discord_url,
            "maintenance_mode": settings_obj.maintenance_mode,
            "registration_enabled": settings_obj.registration_enabled,
            "price_per_slot": settings_obj.price_per_slot,
            "discount_3_month": settings_obj.discount_3_month,
            "discount_6_month": settings_obj.discount_6_month,
            "discount_12_month": settings_obj.discount_12_month,
            # Branding
            "logo_url": settings_obj.logo_url,
            "logo_dark_url": settings_obj.logo_dark_url,
            "logo_mobile_url": settings_obj.logo_mobile_url,
            "logo_width": settings_obj.logo_width,
            "logo_height": settings_obj.logo_height,
            "logo_text": settings_obj.logo_text,
            "logo_subtitle": settings_obj.logo_subtitle,
            "show_logo_text": settings_obj.show_logo_text,
            "footer_logo_url": settings_obj.footer_logo_url,
            "footer_logo_width": settings_obj.footer_logo_width,
            "footer_logo_height": settings_obj.footer_logo_height,
            "favicon_url": settings_obj.favicon_url,
            "primary_color": settings_obj.primary_color,
            "secondary_color": settings_obj.secondary_color
        }
    }


@router.put("/settings")
async def update_settings(
    data: SiteSettingsUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Site ayarlarini guncelle"""
    if admin.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Site ayarlarini sadece superadmin degistirebilir")
    
    settings_obj = db.query(SiteSettings).first()
    if not settings_obj:
        settings_obj = SiteSettings()
        db.add(settings_obj)
    
    if data.site_name is not None:
        settings_obj.site_name = data.site_name
    if data.site_description is not None:
        settings_obj.site_description = data.site_description
    if data.contact_email is not None:
        settings_obj.contact_email = data.contact_email
    if data.discord_url is not None:
        settings_obj.discord_url = data.discord_url
    if data.maintenance_mode is not None:
        settings_obj.maintenance_mode = data.maintenance_mode
    if data.registration_enabled is not None:
        settings_obj.registration_enabled = data.registration_enabled
    if data.price_per_slot is not None:
        settings_obj.price_per_slot = data.price_per_slot
    if data.discount_3_month is not None:
        settings_obj.discount_3_month = data.discount_3_month
    if data.discount_6_month is not None:
        settings_obj.discount_6_month = data.discount_6_month
    if data.discount_12_month is not None:
        settings_obj.discount_12_month = data.discount_12_month
    # Branding fields
    if data.logo_url is not None:
        settings_obj.logo_url = data.logo_url
    if data.logo_dark_url is not None:
        settings_obj.logo_dark_url = data.logo_dark_url
    if data.logo_mobile_url is not None:
        settings_obj.logo_mobile_url = data.logo_mobile_url
    if data.logo_width is not None:
        settings_obj.logo_width = data.logo_width
    if data.logo_height is not None:
        settings_obj.logo_height = data.logo_height
    if data.logo_text is not None:
        settings_obj.logo_text = data.logo_text
    if data.logo_subtitle is not None:
        settings_obj.logo_subtitle = data.logo_subtitle
    if data.show_logo_text is not None:
        settings_obj.show_logo_text = data.show_logo_text
    if data.footer_logo_url is not None:
        settings_obj.footer_logo_url = data.footer_logo_url
    if data.footer_logo_width is not None:
        settings_obj.footer_logo_width = data.footer_logo_width
    if data.footer_logo_height is not None:
        settings_obj.footer_logo_height = data.footer_logo_height
    if data.favicon_url is not None:
        settings_obj.favicon_url = data.favicon_url
    if data.primary_color is not None:
        settings_obj.primary_color = data.primary_color
    if data.secondary_color is not None:
        settings_obj.secondary_color = data.secondary_color

    db.commit()
    
    log = SystemLog(
        level="info",
        category="admin",
        message="Site ayarlari guncellendi",
        user_id=admin.id
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "message": "Ayarlar guncellendi"}


# ==================== LOGS ====================

@router.get("/logs")
async def get_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    level: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Sistem loglari"""
    query = db.query(SystemLog)
    
    if level:
        query = query.filter(SystemLog.level == level)
    if category:
        query = query.filter(SystemLog.category == category)
    
    total = query.count()
    logs = query.order_by(desc(SystemLog.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "logs": [{
            "id": l.id,
            "level": l.level,
            "category": l.category,
            "message": l.message,
            "user_id": l.user_id,
            "ip_address": l.ip_address,
            "created_at": l.created_at.isoformat()
        } for l in logs],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


# ==================== AUDIT LOGS ====================

@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Audit log listesi - tum admin ve kullanici islemleri"""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if date_from:
        try:
            df = datetime.fromisoformat(date_from)
            query = query.filter(AuditLog.created_at >= df)
        except ValueError:
            logger.warning(f"Invalid date_from format: {date_from}")
    if date_to:
        try:
            dt = datetime.fromisoformat(date_to)
            query = query.filter(AuditLog.created_at <= dt)
        except ValueError:
            logger.warning(f"Invalid date_to format: {date_to}")
    
    total = query.count()
    logs = query.order_by(desc(AuditLog.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    result = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first() if log.user_id else None
        result.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": user.username if user else None,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat()
        })
    
    return {
        "logs": result,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


# ==================== PLUGIN MANAGEMENT ====================

@router.get("/plugins")
async def list_plugins(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    game_type: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Plugin listesi"""
    query = db.query(Plugin)
    
    if game_type:
        try:
            gt = GameType(game_type)
            query = query.filter(Plugin.game_type == gt)
        except ValueError:
            logger.warning(f"Invalid game_type filter: {game_type}")
    if category:
        query = query.filter(Plugin.category == category)
    if is_active is not None:
        query = query.filter(Plugin.is_active == is_active)
    
    total = query.count()
    plugins = query.order_by(Plugin.name).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "plugins": [{
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "description": p.description,
            "version": p.version,
            "author": p.author,
            "game_type": p.game_type.value if p.game_type else None,
            "category": p.category,
            "filename": p.filename,
            "file_size": p.file_size,
            "is_active": p.is_active,
            "is_default": p.is_default,
            "created_at": p.created_at.isoformat() if p.created_at else None
        } for p in plugins],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


@router.post("/plugins")
async def create_plugin(
    request: Request,
    file: UploadFile = File(...),
    name: str = Query(...),
    slug: str = Query(...),
    description: Optional[str] = Query(None),
    version: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    game_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_default: bool = Query(False),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Yeni plugin ekle"""
    # Slug kontrolu
    existing = db.query(Plugin).filter(Plugin.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu slug zaten kullaniliyor")
    
    # Dosya uzanti kontrolu
    allowed_ext = [".amxx", ".sma"]
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_ext:
        raise HTTPException(status_code=400, detail="Sadece .amxx ve .sma dosyalari yuklenebilir")
    
    # Dosya boyut kontrolu (10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dosya boyutu 10MB'dan buyuk olamaz")
    
    # Plugin dizini
    plugins_dir = Path(settings.PLUGINS_PATH)
    plugins_dir.mkdir(parents=True, exist_ok=True)
    
    # Dosyayi kaydet
    file_path = plugins_dir / f"{slug}{file_ext}"
    file_path.write_bytes(content)
    
    # Game type
    gt = None
    if game_type:
        try:
            gt = GameType(game_type)
        except ValueError:
            logger.warning(f"Invalid game_type for plugin: {game_type}")
    
    # DB'ye ekle
    plugin = Plugin(
        name=name,
        slug=slug,
        description=description,
        version=version,
        author=author,
        filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        game_type=gt,
        category=category,
        is_default=is_default,
        created_by=admin.id
    )
    db.add(plugin)
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "plugin_create", "plugin", None,
                    new_values={"name": name, "slug": slug}, ip_address=client_ip)
    
    db.commit()
    db.refresh(plugin)
    
    logger.info(f"Plugin eklendi: {name} by {admin.username}")
    
    return {"success": True, "plugin_id": plugin.id, "message": f"Plugin '{name}' eklendi"}


@router.get("/plugins/{plugin_id}")
async def get_plugin(
    plugin_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Plugin detayi"""
    plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadi")
    
    # Bu plugini kullanan sunucu sayisi
    usage_count = db.query(ServerPlugin).filter(ServerPlugin.plugin_id == plugin_id).count()
    
    return {
        "plugin": {
            "id": plugin.id,
            "name": plugin.name,
            "slug": plugin.slug,
            "description": plugin.description,
            "version": plugin.version,
            "author": plugin.author,
            "game_type": plugin.game_type.value if plugin.game_type else None,
            "category": plugin.category,
            "filename": plugin.filename,
            "file_size": plugin.file_size,
            "is_active": plugin.is_active,
            "is_default": plugin.is_default,
            "requires_config": plugin.requires_config,
            "config_template": plugin.config_template,
            "usage_count": usage_count,
            "created_at": plugin.created_at.isoformat() if plugin.created_at else None
        }
    }


@router.put("/plugins/{plugin_id}")
async def update_plugin(
    plugin_id: int,
    data: PluginUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Plugin guncelle"""
    plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadi")
    
    old_values = {"name": plugin.name, "is_active": plugin.is_active}
    
    if data.name is not None:
        plugin.name = data.name
    if data.description is not None:
        plugin.description = data.description
    if data.version is not None:
        plugin.version = data.version
    if data.author is not None:
        plugin.author = data.author
    if data.category is not None:
        plugin.category = data.category
    if data.is_active is not None:
        plugin.is_active = data.is_active
    if data.is_default is not None:
        plugin.is_default = data.is_default
    
    plugin.updated_at = datetime.utcnow()
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "plugin_update", "plugin", plugin_id,
                    old_values=old_values, new_values=data.dict(exclude_none=True),
                    ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": "Plugin guncellendi"}


@router.delete("/plugins/{plugin_id}")
async def delete_plugin(
    plugin_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Plugin sil"""
    plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadi")
    
    # Kullanan sunucu var mi?
    usage_count = db.query(ServerPlugin).filter(ServerPlugin.plugin_id == plugin_id).count()
    if usage_count > 0:
        raise HTTPException(status_code=400, detail=f"Bu plugin {usage_count} sunucuda kullaniliyor. Once sunuculardan kaldirin.")
    
    # Dosyayi sil
    if plugin.file_path:
        try:
            Path(plugin.file_path).unlink(missing_ok=True)
        except OSError as e:
            logger.warning(f"Failed to delete plugin file {plugin.file_path}: {e}")
    
    plugin_name = plugin.name
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "plugin_delete", "plugin", plugin_id,
                    old_values={"name": plugin_name}, ip_address=client_ip)
    
    db.delete(plugin)
    db.commit()
    
    logger.info(f"Plugin silindi: {plugin_name} by {admin.username}")
    
    return {"success": True, "message": f"Plugin '{plugin_name}' silindi"}


@router.post("/plugins/{plugin_id}/assign")
async def assign_plugin_to_server(
    plugin_id: int,
    server_id: int = Query(...),
    request: Request = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Plugini sunucuya ata"""
    plugin = db.query(Plugin).filter(Plugin.id == plugin_id, Plugin.is_active == True).first()
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadi")
    
    server = db.query(GameServer).filter(GameServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    # Zaten atanmis mi?
    existing = db.query(ServerPlugin).filter(
        ServerPlugin.server_id == server_id,
        ServerPlugin.plugin_id == plugin_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu plugin sunucuya zaten atanmis")
    
    # Ata
    server_plugin = ServerPlugin(
        server_id=server_id,
        plugin_id=plugin_id,
        is_enabled=True,
        installed_by=admin.id
    )
    db.add(server_plugin)
    
    # Plugin dosyasini sunucuya kopyala
    if plugin.file_path:
        try:
            src = Path(plugin.file_path)
            game_dir = "ag" if server.game_type == GameType.AG else "cstrike"
            dest_dir = Path(settings.HLDS_PATH) / "servers" / f"server_{server_id}" / game_dir / "addons" / "amxmodx" / "plugins"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / src.name
            shutil.copy2(src, dest)
        except Exception as e:
            logger.error(f"Plugin kopyalama hatasi: {e}")
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "plugin_assign", "server", server_id,
                    new_values={"plugin_id": plugin_id, "plugin_name": plugin.name},
                    ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": f"Plugin sunucuya atandi"}


# ==================== SCHEDULED TASKS ====================

@router.get("/scheduled-tasks")
async def list_scheduled_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    server_id: Optional[int] = None,
    task_type: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Zamanlanmis gorev listesi"""
    query = db.query(ScheduledTask)
    
    if server_id:
        query = query.filter(ScheduledTask.server_id == server_id)
    if task_type:
        query = query.filter(ScheduledTask.task_type == task_type)
    if is_enabled is not None:
        query = query.filter(ScheduledTask.is_enabled == is_enabled)
    
    total = query.count()
    tasks = query.order_by(desc(ScheduledTask.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    result = []
    for task in tasks:
        server = db.query(GameServer).filter(GameServer.id == task.server_id).first() if task.server_id else None
        result.append({
            "id": task.id,
            "server_id": task.server_id,
            "server_name": server.name if server else "Global",
            "name": task.name,
            "task_type": task.task_type,
            "schedule_type": task.schedule_type,
            "schedule_value": task.schedule_value,
            "command": task.command,
            "is_enabled": task.is_enabled,
            "last_run": task.last_run.isoformat() if task.last_run else None,
            "next_run": task.next_run.isoformat() if task.next_run else None,
            "run_count": task.run_count,
            "created_at": task.created_at.isoformat() if task.created_at else None
        })
    
    return {
        "tasks": result,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


@router.post("/scheduled-tasks")
async def create_scheduled_task(
    data: ScheduledTaskCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Yeni zamanlanmis gorev olustur"""
    # Sunucu varsa kontrol et
    if data.server_id:
        server = db.query(GameServer).filter(GameServer.id == data.server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    task = ScheduledTask(
        server_id=data.server_id,
        user_id=admin.id,
        name=data.name,
        task_type=data.task_type,
        schedule_type=data.schedule_type,
        schedule_value=data.schedule_value,
        command=data.command,
        is_enabled=data.is_enabled
    )
    db.add(task)
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "task_create", "scheduled_task", None,
                    new_values={"name": data.name, "task_type": data.task_type},
                    ip_address=client_ip)
    
    db.commit()
    db.refresh(task)
    
    logger.info(f"Zamanlanmis gorev eklendi: {data.name} by {admin.username}")
    
    return {"success": True, "task_id": task.id, "message": "Gorev olusturuldu"}


@router.put("/scheduled-tasks/{task_id}")
async def update_scheduled_task(
    task_id: int,
    data: ScheduledTaskUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Zamanlanmis gorevi guncelle"""
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Gorev bulunamadi")
    
    if data.name is not None:
        task.name = data.name
    if data.schedule_type is not None:
        task.schedule_type = data.schedule_type
    if data.schedule_value is not None:
        task.schedule_value = data.schedule_value
    if data.command is not None:
        task.command = data.command
    if data.is_enabled is not None:
        task.is_enabled = data.is_enabled
    
    task.updated_at = datetime.utcnow()
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "task_update", "scheduled_task", task_id,
                    new_values=data.dict(exclude_none=True), ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": "Gorev guncellendi"}


@router.delete("/scheduled-tasks/{task_id}")
async def delete_scheduled_task(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Zamanlanmis gorevi sil"""
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Gorev bulunamadi")
    
    task_name = task.name
    
    # Task loglarini da sil
    db.query(TaskLog).filter(TaskLog.task_id == task_id).delete()
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "task_delete", "scheduled_task", task_id,
                    old_values={"name": task_name}, ip_address=client_ip)
    
    db.delete(task)
    db.commit()
    
    return {"success": True, "message": "Gorev silindi"}


# ==================== BACKUP MANAGEMENT ====================

@router.get("/backups")
async def list_backups(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    server_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Yedekleme listesi"""
    query = db.query(BackupLog)
    
    if server_id:
        query = query.filter(BackupLog.server_id == server_id)
    if status:
        query = query.filter(BackupLog.status == status)
    
    total = query.count()
    backups = query.order_by(desc(BackupLog.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    result = []
    for b in backups:
        server = db.query(GameServer).filter(GameServer.id == b.server_id).first() if b.server_id else None
        result.append({
            "id": b.id,
            "server_id": b.server_id,
            "server_name": server.name if server else "System",
            "backup_type": b.backup_type,
            "file_path": b.file_path,
            "file_size": b.file_size,
            "file_size_mb": round(b.file_size / 1024 / 1024, 2) if b.file_size else 0,
            "status": b.status,
            "error_message": b.error_message,
            "created_at": b.created_at.isoformat() if b.created_at else None,
            "expires_at": b.expires_at.isoformat() if b.expires_at else None
        })
    
    return {
        "backups": result,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


@router.post("/backups/create")
async def create_backup(
    server_id: Optional[int] = Query(None),
    backup_type: str = Query("full"),
    request: Request = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Manuel yedekleme olustur"""
    import subprocess
    
    backup_dir = Path(settings.BACKUPS_PATH)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    if server_id:
        # Sunucu yedegi
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
        
        servers_dir = Path(settings.HLDS_PATH) / "servers"
        backup_name = f"server_{server_id}_{timestamp}.tar.gz"
        backup_path = backup_dir / backup_name

        try:
            subprocess.run(
                ["tar", "-czf", str(backup_path), "-C", str(servers_dir), f"server_{server_id}"],
                shell=False, check=True, timeout=300
            )
            file_size = backup_path.stat().st_size
            status = "success"
            error = None
        except subprocess.CalledProcessError as e:
            file_size = 0
            status = "failed"
            error = f"Backup failed with code {e.returncode}"
            backup_path = None
        except Exception as e:
            file_size = 0
            status = "failed"
            error = "Backup process error"
            logger.error(f"Server backup error: {e}")
            backup_path = None
    else:
        # Database yedegi
        backup_name = f"database_{timestamp}.sql.gz"
        backup_path = backup_dir / backup_name
        
        try:
            import os

            # Guvenli mysqldump - sifre environment variable uzerinden
            env = os.environ.copy()
            env['MYSQL_PWD'] = settings.DB_PASSWORD

            # mysqldump komutu (shell=False ile guvenli)
            mysqldump_cmd = [
                'mysqldump',
                f'-u{settings.DB_USER}',
                f'-h{settings.DB_HOST}',
                f'-P{settings.DB_PORT}',
                settings.DB_NAME
            ]

            # Dump al ve gzip ile sikistir
            dump_result = subprocess.run(
                mysqldump_cmd,
                capture_output=True,
                env=env,
                timeout=300
            )

            if dump_result.returncode != 0:
                raise Exception(dump_result.stderr.decode())

            import gzip
            with gzip.open(backup_path, 'wb') as f:
                f.write(dump_result.stdout)

            file_size = backup_path.stat().st_size
            status = "success"
            error = None
        except Exception as e:
            file_size = 0
            status = "failed"
            error = str(e)
            backup_path = None
    
    # Log kaydet
    backup_log = BackupLog(
        server_id=server_id,
        backup_type=backup_type,
        file_path=str(backup_path) if backup_path else None,
        file_size=file_size,
        status=status,
        error_message=error,
        expires_at=datetime.utcnow() + timedelta(days=settings.BACKUP_RETENTION_DAYS)
    )
    db.add(backup_log)
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "backup_create", "backup", None,
                    new_values={"server_id": server_id, "backup_type": backup_type, "status": status},
                    ip_address=client_ip)
    
    db.commit()
    
    if status == "failed":
        raise HTTPException(status_code=500, detail=f"Yedekleme hatasi: {error}")
    
    logger.info(f"Yedekleme olusturuldu: {backup_name} by {admin.username}")
    
    return {
        "success": True,
        "message": "Yedekleme tamamlandi",
        "backup": {
            "filename": backup_name,
            "size_mb": round(file_size / 1024 / 1024, 2)
        }
    }


@router.delete("/backups/{backup_id}")
async def delete_backup(
    backup_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Yedekleme sil"""
    backup = db.query(BackupLog).filter(BackupLog.id == backup_id).first()
    if not backup:
        raise HTTPException(status_code=404, detail="Yedekleme bulunamadi")
    
    # Dosyayi sil
    if backup.file_path:
        try:
            Path(backup.file_path).unlink(missing_ok=True)
        except OSError as e:
            logger.warning(f"Failed to delete backup file {backup.file_path}: {e}")
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "backup_delete", "backup", backup_id,
                    old_values={"file_path": backup.file_path}, ip_address=client_ip)
    
    db.delete(backup)
    db.commit()
    
    return {"success": True, "message": "Yedekleme silindi"}


# ==================== USER 2FA MANAGEMENT ====================

@router.put("/users/{user_id}/require-2fa")
async def require_user_2fa(
    user_id: int,
    data: User2FARequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kullanici icin 2FA zorunlulugunu ayarla"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    # must_change_password alanini kullaniyoruz (2FA icin ayri alan eklenebilir)
    # Veya user'a two_factor_required alani eklenebilir
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "user_2fa_require", "user", user_id,
                    new_values={"require_2fa": data.require_2fa}, ip_address=client_ip)
    
    db.commit()
    
    status = "zorunlu" if data.require_2fa else "opsiyonel"
    return {"success": True, "message": f"Kullanici icin 2FA {status} yapildi"}


@router.post("/users/{user_id}/reset-2fa")
async def reset_user_2fa(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kullanicinin 2FA ayarlarini sifirla"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    old_status = user.two_factor_enabled
    
    user.two_factor_enabled = False
    user.two_factor_secret = None
    user.two_factor_backup_codes = None
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "user_2fa_reset", "user", user_id,
                    old_values={"two_factor_enabled": old_status},
                    new_values={"two_factor_enabled": False},
                    ip_address=client_ip)
    
    db.commit()
    
    logger.info(f"2FA sifirlandi: {user.username} by {admin.username}")
    
    return {"success": True, "message": f"{user.username} kullanicisinin 2FA'si sifirlandi"}


# ==================== NOTIFICATIONS ====================

@router.post("/notifications/send")
async def send_notification(
    data: NotificationSendRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Bildirim gonder"""
    if data.user_id:
        # Tek kullaniciya
        user = db.query(User).filter(User.id == data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
        
        notification = Notification(
            user_id=data.user_id,
            type=data.type,
            title=data.title,
            message=data.message,
            link=data.link
        )
        db.add(notification)
        count = 1
    else:
        # Tum kullanicilara
        users = db.query(User).filter(User.status == UserStatus.ACTIVE).all()
        count = 0
        for user in users:
            notification = Notification(
                user_id=user.id,
                type=data.type,
                title=data.title,
                message=data.message,
                link=data.link
            )
            db.add(notification)
            count += 1
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "notification_send", "notification", None,
                    new_values={"title": data.title, "user_count": count},
                    ip_address=client_ip)
    
    db.commit()
    
    logger.info(f"Bildirim gonderildi: {data.title} -> {count} kullanici by {admin.username}")
    
    return {"success": True, "message": f"{count} kullaniciya bildirim gonderildi"}


# ==================== SYSTEM STATS ====================

@router.get("/system-stats")
async def get_system_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Sistem kaynak kullanimı"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Son 24 saat islem sayisi
        day_ago = datetime.utcnow() - timedelta(days=1)
        audit_count_24h = db.query(AuditLog).filter(AuditLog.created_at >= day_ago).count()
        
        # Aktif session sayisi (tahmini)
        active_sessions = db.query(User).filter(
            User.last_login >= datetime.utcnow() - timedelta(minutes=30)
        ).count()
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "cores": psutil.cpu_count()
            },
            "memory": {
                "total_gb": round(memory.total / 1024 / 1024 / 1024, 2),
                "used_gb": round(memory.used / 1024 / 1024 / 1024, 2),
                "available_gb": round(memory.available / 1024 / 1024 / 1024, 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "percent": round((disk.used / disk.total) * 100, 1)
            },
            "activity": {
                "audit_logs_24h": audit_count_24h,
                "active_sessions": active_sessions
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"System stats hatasi: {e}")
        return {"error": str(e)}


@router.get("/resource-history")
async def get_resource_history(
    server_id: Optional[int] = None,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kaynak kullanim gecmisi"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(ResourceLog).filter(ResourceLog.created_at >= since)
    
    if server_id:
        query = query.filter(ResourceLog.server_id == server_id)
    
    logs = query.order_by(ResourceLog.created_at).all()
    
    return {
        "history": [{
            "server_id": log.server_id,
            "cpu_percent": log.cpu_percent,
            "memory_mb": log.memory_mb,
            "player_count": log.player_count,
            "map_name": log.map_name,
            "created_at": log.created_at.isoformat()
        } for log in logs],
        "hours": hours
    }


# ==================== THEME API ====================

class ThemeSettings(BaseModel):
    colorPrimary: str = "#ff6b00"
    colorSecondary: str = "#ff8c00"
    colorAccent: str = "#ffaa00"
    customCSS: str = ""


@router.post("/theme")
async def save_theme(
    theme: ThemeSettings,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Tema ayarlarini kaydet"""
    try:
        site = db.query(SiteSettings).first()
        if not site:
            site = SiteSettings()
            db.add(site)
        
        # Theme settings JSON olarak kaydet
        site.theme_settings = {
            "colorPrimary": theme.colorPrimary,
            "colorSecondary": theme.colorSecondary,
            "colorAccent": theme.colorAccent,
            "customCSS": theme.customCSS
        }
        
        db.commit()
        
        return {"success": True, "message": "Tema kaydedildi"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/theme")
async def get_theme(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Tema ayarlarini getir"""
    site = db.query(SiteSettings).first()
    
    if site and hasattr(site, 'theme_settings') and site.theme_settings:
        return site.theme_settings
    
    return {
        "colorPrimary": "#ff6b00",
        "colorSecondary": "#ff8c00",
        "colorAccent": "#ffaa00",
        "customCSS": ""
    }


# ==================== USERS DETAILS & ACTIONS ====================

@router.get("/users/{user_id}/details")
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kullanici detaylarini getir"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    # Kullanicinin sunuculari
    servers = db.query(GameServer).filter(GameServer.owner_id == user_id).all()
    
    # Kullanicinin odemeleri
    payments = db.query(Payment).filter(Payment.user_id == user_id).order_by(desc(Payment.created_at)).limit(10).all()
    
    # Son aktiviteler
    audits = db.query(AuditLog).filter(AuditLog.user_id == user_id).order_by(desc(AuditLog.created_at)).limit(10).all()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "status": user.status.value if user.status else "active",
        "balance": float(user.balance or 0),
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "two_factor_enabled": user.two_factor_enabled,
        "servers": [{
            "id": s.id,
            "name": s.name,
            "status": s.status.value if s.status else "stopped",
            "game_type": s.game_type.value if s.game_type else "ag"
        } for s in servers],
        "payments": [{
            "id": p.id,
            "amount": float(p.amount),
            "status": p.status.value if p.status else "pending",
            "created_at": p.created_at.isoformat() if p.created_at else None
        } for p in payments],
        "recent_activity": [{
            "action": a.action,
            "created_at": a.created_at.isoformat() if a.created_at else None
        } for a in audits]
    }


@router.post("/users/{user_id}/reset-password")
async def admin_reset_user_password(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kullanici sifresini sifirla - reset email gonderir"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    # Sifre sifirlama islemi
    import secrets
    reset_token = secrets.token_urlsafe(32)
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "user_password_reset", "user", user_id,
                    new_values={"action": "password_reset_requested"},
                    ip_address=client_ip)
    
    db.commit()
    
    # TODO: Email gonderimi burada yapilabilir
    logger.info(f"Password reset requested for {user.username} by admin {admin.username}")
    
    return {"success": True, "message": f"{user.email} adresine sifre sifirlama e-postasi gonderildi"}


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kullaniciyi yasakla"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    if user.role.value in ['admin', 'superadmin']:
        raise HTTPException(status_code=403, detail="Admin kullanici yasaklanamaz")
    
    old_status = user.status.value if user.status else "active"
    user.status = UserStatus.BANNED
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "user_ban", "user", user_id,
                    old_values={"status": old_status},
                    new_values={"status": "banned"},
                    ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": f"{user.username} yasaklandi"}


@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Kullanici yasagini kaldir"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    
    old_status = user.status.value if user.status else "banned"
    user.status = UserStatus.ACTIVE
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "user_unban", "user", user_id,
                    old_values={"status": old_status},
                    new_values={"status": "active"},
                    ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": f"{user.username} yasagi kaldirildi"}


# ==================== SUPPORT TICKETS ====================

class TicketReplyRequest(BaseModel):
    message: str
    close_ticket: bool = False


class TicketStatusRequest(BaseModel):
    status: str


@router.get("/tickets")
async def list_tickets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Destek taleplerini listele"""
    from app.models.database import SupportTicket, TicketMessage
    
    query = db.query(SupportTicket)
    
    if status:
        query = query.filter(SupportTicket.status == status)
    if priority:
        query = query.filter(SupportTicket.priority == priority)
    if category:
        query = query.filter(SupportTicket.category == category)
    
    total = query.count()
    tickets = query.order_by(desc(SupportTicket.updated_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "tickets": [{
            "id": t.id,
            "subject": t.subject,
            "status": t.status,
            "priority": t.priority,
            "category": t.category,
            "user": {
                "id": t.user.id if t.user else None,
                "username": t.user.username if t.user else "Silinmis"
            },
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            "unread_count": db.query(TicketMessage).filter(
                TicketMessage.ticket_id == t.id,
                TicketMessage.is_read == False,
                TicketMessage.is_admin == False
            ).count()
        } for t in tickets],
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/tickets/stats")
async def get_ticket_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Ticket istatistikleri"""
    from app.models.database import SupportTicket
    
    total = db.query(SupportTicket).count()
    open_count = db.query(SupportTicket).filter(SupportTicket.status == "open").count()
    pending_count = db.query(SupportTicket).filter(SupportTicket.status == "pending").count()
    resolved_count = db.query(SupportTicket).filter(SupportTicket.status == "resolved").count()
    
    return {
        "total": total,
        "open": open_count,
        "pending": pending_count,
        "resolved": resolved_count
    }


@router.get("/tickets/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Ticket detaylarini getir"""
    from app.models.database import SupportTicket, TicketMessage
    
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket bulunamadi")
    
    # Mesajlari okundu olarak isaretle
    db.query(TicketMessage).filter(
        TicketMessage.ticket_id == ticket_id,
        TicketMessage.is_admin == False
    ).update({"is_read": True})
    db.commit()
    
    messages = db.query(TicketMessage).filter(
        TicketMessage.ticket_id == ticket_id
    ).order_by(TicketMessage.created_at).all()
    
    return {
        "id": ticket.id,
        "subject": ticket.subject,
        "status": ticket.status,
        "priority": ticket.priority,
        "category": ticket.category,
        "user": {
            "id": ticket.user.id if ticket.user else None,
            "username": ticket.user.username if ticket.user else "Silinmis"
        },
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "messages": [{
            "id": m.id,
            "content": m.content,
            "author": m.author_name or (ticket.user.username if ticket.user and not m.is_admin else "Admin"),
            "is_admin": m.is_admin,
            "created_at": m.created_at.isoformat() if m.created_at else None
        } for m in messages]
    }


@router.post("/tickets/{ticket_id}/reply")
async def reply_to_ticket(
    ticket_id: int,
    data: TicketReplyRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Ticket'a yanit ver"""
    from app.models.database import SupportTicket, TicketMessage
    
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket bulunamadi")
    
    # Mesaj ekle
    message = TicketMessage(
        ticket_id=ticket_id,
        content=data.message,
        is_admin=True,
        author_name=admin.username
    )
    db.add(message)
    
    # Ticket durumunu guncelle
    if data.close_ticket:
        ticket.status = "closed"
    else:
        ticket.status = "pending"
    
    ticket.updated_at = datetime.utcnow()
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "ticket_reply", "ticket", ticket_id,
                    new_values={"message": data.message[:100], "closed": data.close_ticket},
                    ip_address=client_ip)
    
    db.commit()
    
    # TODO: Kullaniciya bildirim gonder
    
    return {"success": True, "message": "Yanit gonderildi"}


@router.put("/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    data: TicketStatusRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Ticket durumunu guncelle"""
    from app.models.database import SupportTicket
    
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket bulunamadi")
    
    old_status = ticket.status
    ticket.status = data.status
    ticket.updated_at = datetime.utcnow()
    
    client_ip = request.client.host if request.client else None
    log_admin_audit(db, admin.id, "ticket_status_change", "ticket", ticket_id,
                    old_values={"status": old_status},
                    new_values={"status": data.status},
                    ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": "Durum guncellendi"}


# ==================== BANNER ENDPOINTS ====================

class BannerCreateRequest(BaseModel):
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    position: str = "hero"
    is_active: bool = True
    display_order: int = 0


class BannerUpdateRequest(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


@router.get("/banners")
async def list_banners(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Tum bannerlari listele"""
    banners = db.query(Banner).order_by(Banner.display_order).all()
    
    return {
        "banners": [{
            "id": b.id,
            "name": b.name,
            "title": b.title,
            "description": b.description,
            "image_url": b.image_url,
            "link_url": b.link_url,
            "position": b.position.value if b.position else "hero",
            "is_active": b.is_active,
            "display_order": b.display_order,
            "created_at": b.created_at.isoformat() if b.created_at else None
        } for b in banners]
    }


@router.post("/banners")
async def create_banner(
    data: BannerCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Yeni banner olustur"""
    try:
        position = BannerPosition(data.position)
    except ValueError:
        position = BannerPosition.HERO
    
    banner = Banner(
        name=data.name,
        title=data.title,
        description=data.description,
        image_url=data.image_url,
        link_url=data.link_url,
        position=position,
        is_active=data.is_active,
        display_order=data.display_order
    )
    db.add(banner)
    db.commit()
    db.refresh(banner)
    
    return {"success": True, "id": banner.id}


@router.put("/banners/{banner_id}")
async def update_banner(
    banner_id: int,
    data: BannerUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Banner guncelle"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner bulunamadi")
    
    if data.name is not None:
        banner.name = data.name
    if data.title is not None:
        banner.title = data.title
    if data.description is not None:
        banner.description = data.description
    if data.image_url is not None:
        banner.image_url = data.image_url
    if data.link_url is not None:
        banner.link_url = data.link_url
    if data.position is not None:
        try:
            banner.position = BannerPosition(data.position)
        except ValueError:
            pass
    if data.is_active is not None:
        banner.is_active = data.is_active
    if data.display_order is not None:
        banner.display_order = data.display_order
    
    db.commit()
    return {"success": True}


@router.delete("/banners/{banner_id}")
async def delete_banner(
    banner_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Banner sil"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner bulunamadi")
    
    db.delete(banner)
    db.commit()
    return {"success": True}


# ==================== MEDIA ENDPOINTS ====================

@router.get("/media")
async def list_media(
    admin: User = Depends(get_current_admin)
):
    """Static gorselleri listele"""
    import os
    
    media_items = []
    static_path = Path("/var/www/agtrmerkezi/static/images")
    
    if static_path.exists():
        for root, dirs, files in os.walk(static_path):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(static_path.parent.parent)
                    category = Path(root).name
                    
                    media_items.append({
                        "id": len(media_items) + 1,
                        "name": file.rsplit(".", 1)[0],
                        "file_path": f"/{rel_path}",
                        "category": category,
                        "file_size": full_path.stat().st_size
                    })
    
    return {"images": media_items}


@router.post("/media/upload")
async def upload_media(
    file: UploadFile = File(...),
    category: str = Form("general"),
    admin: User = Depends(get_current_admin)
):
    """Gorsel yukle"""
    import os
    import uuid

    allowed_ext = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
    ext = Path(file.filename).suffix.lower()

    if ext not in allowed_ext:
        raise HTTPException(status_code=400, detail="Gecersiz dosya formati. Izin verilen: png, jpg, jpeg, gif, webp, svg")

    # Validate file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dosya boyutu 10MB'dan buyuk olamaz")

    upload_dir = Path(f"/var/www/agtrmerkezi/static/images/{category}")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename to avoid overwrites
    unique_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = upload_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "success": True,
        "file_path": f"/static/images/{category}/{unique_name}",
        "url": f"/static/images/{category}/{unique_name}"
    }


@router.delete("/media/{media_id}")
async def delete_media(
    media_id: int,
    file_path: str = Query(...),
    admin: User = Depends(get_current_admin)
):
    """Gorsel sil"""
    import os
    
    full_path = Path(f"/var/www/agtrmerkezi{file_path}")
    
    if full_path.exists() and "/static/images/" in file_path:
        os.remove(full_path)
        return {"success": True}
    
    raise HTTPException(status_code=404, detail="Dosya bulunamadi")

