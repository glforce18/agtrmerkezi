"""
AGTR Merkezi - Admin Users Management API
Kullanici yonetimi, arama, filtreleme, ban/unban
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.security import get_current_admin, hash_password
from app.models.connection import get_db
from app.models.database import (
    ForumPost,
    ForumTopic,
    GameServer,
    Payment,
    PaymentStatus,
    ServerStatus,
    User,
    UserRole,
    UserStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Admin Users"])


# ==================== PYDANTIC MODELS ====================


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    status: Optional[str] = None
    balance: Optional[float] = None
    balance_coin: Optional[float] = None
    email_verified: Optional[bool] = None
    two_factor_enabled: Optional[bool] = None


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"
    email_verified: bool = False


class BanUserRequest(BaseModel):
    reason: str
    duration_hours: Optional[int] = None  # None = permanent


# ==================== ENDPOINTS ====================


@router.get("")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    online_only: bool = False,
    steam_only: bool = False,
    sort_by: str = Query("created_at", pattern="^(created_at|last_login|username|balance)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    Kullanici listesi - pagination, arama, filtreleme

    Online Detection: last_login < 5 dakika = online
    """
    query = db.query(User)

    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                User.steam_id.ilike(search_term),
            )
        )

    # Role filter
    if role and role != "all":
        try:
            role_enum = UserRole(role)
            query = query.filter(User.role == role_enum)
        except ValueError:
            pass

    # Status filter
    if status and status != "all":
        try:
            status_enum = UserStatus(status)
            query = query.filter(User.status == status_enum)
        except ValueError:
            pass

    # Online filter (last_login within 5 minutes)
    if online_only:
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        query = query.filter(User.last_login >= five_minutes_ago)

    # Steam filter
    if steam_only:
        query = query.filter(User.steam_id.isnot(None), User.steam_id != "")

    # Total count
    total = query.count()

    # Sorting
    sort_column = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    offset = (page - 1) * limit
    users = query.offset(offset).limit(limit).all()

    # Get server counts for each user (batch query to avoid N+1)
    user_ids = [u.id for u in users]
    server_counts = {}
    if user_ids:
        server_count_query = (
            db.query(GameServer.owner_id, func.count(GameServer.id).label("count"))
            .filter(GameServer.owner_id.in_(user_ids), GameServer.status != ServerStatus.DELETED)
            .group_by(GameServer.owner_id)
            .all()
        )

        server_counts = {owner_id: count for owner_id, count in server_count_query}

    # Check online status (last 5 minutes)
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)

    # Format response
    users_data = []
    for u in users:
        is_online = u.last_login and u.last_login >= five_minutes_ago

        users_data.append(
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "avatar": u.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={u.id}",
                "role": u.role.value,
                "status": u.status.value,
                "steam_id": u.steam_id,
                "has_steam": bool(u.steam_id),
                "is_online": is_online,
                "server_count": server_counts.get(u.id, 0),
                "balance": float(u.balance or 0),
                "balance_coin": float(u.balance_coin or 0),
                "email_verified": u.email_verified,
                "two_factor_enabled": u.two_factor_enabled,
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "reputation": u.reputation or 0,
                "level": u.level or 1,
            }
        )

    return {
        "data": users_data,  # Changed from "users" to "data" for consistency
        "total": total,
        "page": page,
        "per_page": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 1,
    }


@router.get("/online")
async def get_online_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Online kullanici sayisi ve listesi"""
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)

    online_users = db.query(User).filter(User.last_login >= five_minutes_ago).all()

    return {
        "online_count": len(online_users),
        "online_users": [
            {
                "id": u.id,
                "username": u.username,
                "avatar": u.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={u.id}",
                "last_login": u.last_login.isoformat() if u.last_login else None,
            }
            for u in online_users
        ],
    }


@router.get("/{user_id}")
async def get_user_detail(
    user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """Kullanici detayli bilgiler"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")

    # Server count
    server_count = (
        db.query(func.count(GameServer.id))
        .filter(GameServer.owner_id == user_id, GameServer.status != ServerStatus.DELETED)
        .scalar()
        or 0
    )

    # Payment stats
    total_spent = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.user_id == user_id, Payment.status == PaymentStatus.COMPLETED)
        .scalar()
        or 0
    )

    payment_count = (
        db.query(func.count(Payment.id))
        .filter(Payment.user_id == user_id, Payment.status == PaymentStatus.COMPLETED)
        .scalar()
        or 0
    )

    # Forum stats
    topic_count = (
        db.query(func.count(ForumTopic.id)).filter(ForumTopic.author_id == user_id).scalar() or 0
    )

    post_count = (
        db.query(func.count(ForumPost.id)).filter(ForumPost.author_id == user_id).scalar() or 0
    )

    # Online status
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    is_online = user.last_login and user.last_login >= five_minutes_ago

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.id}",
        "role": user.role.value,
        "status": user.status.value,
        "steam_id": user.steam_id,
        "discord_id": user.discord_id,
        "has_steam": bool(user.steam_id),
        "has_discord": bool(user.discord_id),
        "is_online": is_online,
        "balance": float(user.balance or 0),
        "balance_coin": float(user.balance_coin or 0),
        "email_verified": user.email_verified,
        "two_factor_enabled": user.two_factor_enabled,
        "reputation": user.reputation or 0,
        "level": user.level or 1,
        "bio": user.bio,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "stats": {
            "server_count": server_count,
            "total_spent": float(total_spent),
            "payment_count": payment_count,
            "topic_count": topic_count,
            "post_count": post_count,
        },
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreateRequest, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """Yeni kullanici olustur"""
    # Check if username exists
    existing_username = db.query(User).filter(User.username == data.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username zaten kullanilmakta")

    # Check if email exists
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email zaten kayitli")

    # Validate role
    try:
        role_enum = UserRole(data.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Gecersiz rol")

    # Create user
    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role=role_enum,
        status=UserStatus.ACTIVE,
        email_verified=data.email_verified,
        balance=0,
        balance_coin=0,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Admin {admin.username} created user {new_user.username} (ID: {new_user.id})")

    return {
        "message": "Kullanici olusturuldu",
        "user_id": new_user.id,
        "username": new_user.username,
    }


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Kullanici bilgilerini guncelle"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")

    # Prevent admin from demoting themselves
    if user_id == admin.id and data.role and data.role != admin.role.value:
        raise HTTPException(status_code=400, detail="Kendi rolunuzu degistiremezsiniz")

    # Update fields
    if data.username:
        # Check duplicate
        existing = db.query(User).filter(User.username == data.username, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username zaten kullanilmakta")
        user.username = data.username

    if data.email:
        # Check duplicate
        existing = db.query(User).filter(User.email == data.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email zaten kayitli")
        user.email = data.email

    if data.role:
        try:
            user.role = UserRole(data.role)
        except ValueError:
            raise HTTPException(status_code=400, detail="Gecersiz rol")

    if data.status:
        try:
            user.status = UserStatus(data.status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Gecersiz durum")

    if data.balance is not None:
        user.balance = data.balance

    if data.balance_coin is not None:
        user.balance_coin = data.balance_coin

    if data.email_verified is not None:
        user.email_verified = data.email_verified

    if data.two_factor_enabled is not None:
        user.two_factor_enabled = data.two_factor_enabled

    user.updated_at = datetime.utcnow()

    db.commit()

    logger.info(f"Admin {admin.username} updated user {user.username} (ID: {user_id})")

    return {"message": "Kullanici guncellendi"}


@router.post("/{user_id}/ban")
async def ban_user(
    user_id: int,
    data: BanUserRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Kullaniciyi banla"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")

    # Cannot ban yourself
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Kendinizi banlayamazsiniz")

    # Cannot ban other admins unless superadmin
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        if admin.role != UserRole.SUPERADMIN:
            raise HTTPException(
                status_code=403, detail="Adminleri banlamak icin superadmin yetkiniz olmali"
            )

    user.status = UserStatus.BANNED
    user.updated_at = datetime.utcnow()

    db.commit()

    logger.warning(
        f"Admin {admin.username} banned user {user.username} (ID: {user_id}). Reason: {data.reason}"
    )

    return {"message": "Kullanici banlandi"}


@router.post("/{user_id}/unban")
async def unban_user(
    user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """Kullanicinin banini kaldir"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")

    if user.status != UserStatus.BANNED:
        raise HTTPException(status_code=400, detail="Kullanici zaten banli degil")

    user.status = UserStatus.ACTIVE
    user.updated_at = datetime.utcnow()

    db.commit()

    logger.info(f"Admin {admin.username} unbanned user {user.username} (ID: {user_id})")

    return {"message": "Ban kaldirildi"}


@router.delete("/{user_id}")
async def delete_user(
    user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """Kullaniciyi sil (dikkatli!)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")

    # Cannot delete yourself
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Kendinizi silemezsiniz")

    # Cannot delete other admins unless superadmin
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        if admin.role != UserRole.SUPERADMIN:
            raise HTTPException(
                status_code=403, detail="Adminleri silmek icin superadmin yetkiniz olmali"
            )

    # Check if user has active servers
    active_servers = (
        db.query(func.count(GameServer.id))
        .filter(
            GameServer.owner_id == user_id,
            GameServer.status.in_([ServerStatus.RUNNING, ServerStatus.STOPPED]),
        )
        .scalar()
        or 0
    )

    if active_servers > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Kullanicinin {active_servers} aktif sunucusu var. Once sunuculari silin.",
        )

    # Soft delete - mark as deleted
    user.status = UserStatus.DELETED
    user.updated_at = datetime.utcnow()

    db.commit()

    logger.warning(f"Admin {admin.username} deleted user {user.username} (ID: {user_id})")

    return {"message": "Kullanici silindi"}


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Kullanicinin sifresini sifirla"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")

    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Sifre en az 8 karakter olmali")

    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.utcnow()

    db.commit()

    logger.info(f"Admin {admin.username} reset password for user {user.username} (ID: {user_id})")

    return {"message": "Sifre sifirlandi"}
