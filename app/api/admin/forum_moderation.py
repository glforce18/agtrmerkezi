# ============================================
# AGTR v6.0 - Forum Moderation Admin API
# Dosya: app/api/admin/forum_moderation.py
# Kara liste, uyari ve ban yonetimi
# ============================================

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.content_filter import (
    BlacklistManager,
    WarningSystem,
    get_blacklist_manager,
    get_warning_system,
)
from app.core.security import get_current_admin, get_current_moderator
from app.models.connection import get_db
from app.models.database import (
    ContentBlacklist,
    ForumBan,
    ModerationLog,
    User,
    UserRole,
    UserWarning,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/moderation", tags=["admin-forum-moderation"])


# ==================== PYDANTIC MODELS ====================

class BlacklistWordCreate(BaseModel):
    word: str
    category: str = "general"


class BlacklistBulkCreate(BaseModel):
    words: List[str]
    category: str = "general"


class WarningCreate(BaseModel):
    user_id: int
    reason: str


class BanCreate(BaseModel):
    user_id: int
    reason: str
    duration_hours: int = 24


# ==================== BLACKLIST ENDPOINTS ====================

@router.get("/blacklist")
async def get_blacklist_words(
    category: Optional[str] = None,
    active_only: bool = True,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_moderator)
):
    """Kara liste kelimelerini getir"""
    manager = get_blacklist_manager(db)
    words = manager.get_all_words(category=category, active_only=active_only)

    # Sayfalama
    total = len(words)
    start = (page - 1) * limit
    end = start + limit
    paginated_words = words[start:end]

    return {
        "words": paginated_words,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }


@router.get("/blacklist/categories")
async def get_blacklist_categories(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_moderator)
):
    """Kara liste kategorilerini getir"""
    manager = get_blacklist_manager(db)
    categories = manager.get_categories()

    return {"categories": categories}


@router.post("/blacklist", status_code=status.HTTP_201_CREATED)
async def add_blacklist_word(
    data: BlacklistWordCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Kara listeye kelime ekle"""
    if not data.word or len(data.word.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kelime en az 2 karakter olmali"
        )

    manager = get_blacklist_manager(db)

    try:
        result = manager.add_word(
            word=data.word.strip(),
            category=data.category,
            added_by=current_admin.id
        )

        # Moderasyon logla
        _log_moderation_action(
            db=db,
            action="blacklist_add",
            moderator_id=current_admin.id,
            reason=f"Kara listeye kelime eklendi: {data.word[:20]}...",
            details={"word": data.word, "category": data.category}
        )

        return {
            "message": "Kelime kara listeye eklendi",
            "result": result
        }
    except Exception as e:
        logger.error(f"Kara liste ekleme hatasi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kelime eklenirken hata olustu"
        )


@router.post("/blacklist/bulk", status_code=status.HTTP_201_CREATED)
async def add_blacklist_words_bulk(
    data: BlacklistBulkCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Toplu kara liste kelimesi ekle"""
    if not data.words:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="En az bir kelime gerekli"
        )

    manager = get_blacklist_manager(db)
    result = manager.bulk_add_words(
        words=data.words,
        category=data.category,
        added_by=current_admin.id
    )

    # Moderasyon logla
    _log_moderation_action(
        db=db,
        action="blacklist_bulk_add",
        moderator_id=current_admin.id,
        reason=f"Toplu kara liste ekleme: {result['added']} kelime",
        details={"category": data.category, "result": result}
    )

    return {
        "message": f"{result['added']} kelime eklendi, {result['skipped']} atlandı",
        "result": result
    }


@router.delete("/blacklist/{word_id}")
async def remove_blacklist_word(
    word_id: int,
    permanent: bool = False,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Kara listeden kelime kaldir"""
    manager = get_blacklist_manager(db)

    # Kelimeyi bul
    word_entry = db.query(ContentBlacklist).filter(
        ContentBlacklist.id == word_id
    ).first()

    if not word_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kelime bulunamadi"
        )

    word_text = word_entry.word

    if permanent:
        success = manager.delete_word(word_id)
    else:
        success = manager.remove_word(word_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kelime kaldirilamadi"
        )

    # Moderasyon logla
    _log_moderation_action(
        db=db,
        action="blacklist_remove",
        moderator_id=current_admin.id,
        reason=f"Kara listeden kelime kaldirildi: {word_text[:20]}...",
        details={"word_id": word_id, "word": word_text, "permanent": permanent}
    )

    return {"message": "Kelime kaldirildi"}


# ==================== WARNING ENDPOINTS ====================

@router.get("/warnings")
async def get_all_warnings(
    user_id: Optional[int] = None,
    active_only: bool = True,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_moderator)
):
    """Tum uyarilari getir"""
    query = db.query(UserWarning)

    if user_id:
        query = query.filter(UserWarning.user_id == user_id)

    if active_only:
        query = query.filter(UserWarning.expires_at > datetime.utcnow())

    total = query.count()
    warnings = query.order_by(desc(UserWarning.created_at)).offset(
        (page - 1) * limit
    ).limit(limit).all()

    result = []
    for w in warnings:
        user = db.query(User).filter(User.id == w.user_id).first()
        warned_by = db.query(User).filter(User.id == w.warned_by).first() if w.warned_by else None

        result.append({
            "id": w.id,
            "user_id": w.user_id,
            "username": user.username if user else None,
            "reason": w.reason,
            "warned_by_id": w.warned_by,
            "warned_by_username": warned_by.username if warned_by else "Sistem",
            "expires_at": w.expires_at.isoformat() if w.expires_at else None,
            "created_at": w.created_at.isoformat() if w.created_at else None,
            "is_active": w.expires_at > datetime.utcnow() if w.expires_at else False
        })

    return {
        "warnings": result,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }


@router.get("/warnings/user/{user_id}")
async def get_user_warnings(
    user_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_moderator)
):
    """Kullanicinin uyarilarini getir"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanici bulunamadi"
        )

    warning_system = get_warning_system(db)
    warnings = warning_system.get_user_warnings(user_id, active_only=active_only)

    return {
        "user_id": user_id,
        "username": user.username,
        "warnings": warnings,
        "active_count": warning_system.get_active_warning_count(user_id)
    }


@router.post("/warnings", status_code=status.HTTP_201_CREATED)
async def create_warning(
    data: WarningCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_moderator)
):
    """Kullaniciya uyari ver"""
    # Kullanici kontrolu
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanici bulunamadi"
        )

    # Admin kendine uyari veremez
    if data.user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendinize uyari veremezsiniz"
        )

    warning_system = get_warning_system(db)

    try:
        result = warning_system.add_warning(
            user_id=data.user_id,
            reason=data.reason,
            warned_by=current_admin.id,
            auto_ban=True  # Limit asilirsa otomatik ban
        )

        # Moderasyon logla
        _log_moderation_action(
            db=db,
            action="warn",
            target_user_id=data.user_id,
            moderator_id=current_admin.id,
            reason=data.reason
        )

        message = "Uyari verildi"
        if result.get("banned"):
            message = f"Uyari verildi ve kullanici banlandi (3 uyari limiti asildi)"

        return {
            "message": message,
            "result": result
        }
    except Exception as e:
        logger.error(f"Uyari verme hatasi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Uyari verilirken hata olustu"
        )


@router.delete("/warnings/{warning_id}")
async def remove_warning(
    warning_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Uyariyi kaldir"""
    warning = db.query(UserWarning).filter(UserWarning.id == warning_id).first()
    if not warning:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uyari bulunamadi"
        )

    warning_system = get_warning_system(db)
    success = warning_system.remove_warning(warning_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Uyari kaldirilamadi"
        )

    # Moderasyon logla
    _log_moderation_action(
        db=db,
        action="warning_remove",
        target_user_id=warning.user_id,
        moderator_id=current_admin.id,
        reason=f"Uyari kaldirildi: {warning.reason[:50]}..."
    )

    return {"message": "Uyari kaldirildi"}


# ==================== BAN ENDPOINTS ====================

@router.get("/bans")
async def get_all_bans(
    active_only: bool = True,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_moderator)
):
    """Tum forum banlarini getir"""
    query = db.query(ForumBan)

    if active_only:
        query = query.filter(ForumBan.expires_at > datetime.utcnow())

    total = query.count()
    bans = query.order_by(desc(ForumBan.created_at)).offset(
        (page - 1) * limit
    ).limit(limit).all()

    result = []
    for ban in bans:
        user = db.query(User).filter(User.id == ban.user_id).first()
        banned_by = db.query(User).filter(User.id == ban.banned_by).first() if ban.banned_by else None

        now = datetime.utcnow()
        remaining_hours = (ban.expires_at - now).total_seconds() / 3600 if ban.expires_at > now else 0

        result.append({
            "id": ban.id,
            "user_id": ban.user_id,
            "username": user.username if user else None,
            "reason": ban.reason,
            "banned_by_id": ban.banned_by,
            "banned_by_username": banned_by.username if banned_by else "Sistem",
            "expires_at": ban.expires_at.isoformat() if ban.expires_at else None,
            "created_at": ban.created_at.isoformat() if ban.created_at else None,
            "is_active": ban.expires_at > now if ban.expires_at else False,
            "remaining_hours": round(remaining_hours, 1)
        })

    return {
        "bans": result,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }


@router.get("/bans/user/{user_id}")
async def get_user_ban_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_moderator)
):
    """Kullanicinin ban durumunu getir"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanici bulunamadi"
        )

    warning_system = get_warning_system(db)
    is_banned, ban_info = warning_system.check_ban_status(user_id)

    return {
        "user_id": user_id,
        "username": user.username,
        "is_banned": is_banned,
        "ban_info": ban_info,
        "active_warnings": warning_system.get_active_warning_count(user_id)
    }


@router.post("/bans", status_code=status.HTTP_201_CREATED)
async def create_ban(
    data: BanCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_moderator)
):
    """Kullaniciyi banla"""
    # Kullanici kontrolu
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanici bulunamadi"
        )

    # Admin kendini banlayamaz
    if data.user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendinizi banlayamazsiniz"
        )

    # Admin'ler banlanamaz (sadece superadmin banlayabilir)
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        if current_admin.role != UserRole.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Adminleri banlamak icin superadmin yetkiniz olmali"
            )

    warning_system = get_warning_system(db)

    try:
        result = warning_system.ban_user(
            user_id=data.user_id,
            reason=data.reason,
            banned_by=current_admin.id,
            duration_hours=data.duration_hours
        )

        # Moderasyon logla
        _log_moderation_action(
            db=db,
            action="ban",
            target_user_id=data.user_id,
            moderator_id=current_admin.id,
            reason=data.reason,
            details={"duration_hours": data.duration_hours}
        )

        return {
            "message": f"Kullanici {data.duration_hours} saat forumdan banlandi",
            "result": result
        }
    except Exception as e:
        logger.error(f"Ban verme hatasi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ban verilirken hata olustu"
        )


@router.delete("/bans/user/{user_id}")
async def unban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_moderator)
):
    """Kullanicinin banini kaldir"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanici bulunamadi"
        )

    warning_system = get_warning_system(db)
    success = warning_system.unban_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aktif ban bulunamadi"
        )

    # Moderasyon logla
    _log_moderation_action(
        db=db,
        action="unban",
        target_user_id=user_id,
        moderator_id=current_admin.id,
        reason="Ban kaldirildi"
    )

    return {"message": "Ban kaldirildi"}


# ==================== MODERATION LOGS ====================

@router.get("/logs")
async def get_moderation_logs(
    action: Optional[str] = None,
    target_user_id: Optional[int] = None,
    moderator_id: Optional[int] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Moderasyon loglarini getir"""
    query = db.query(ModerationLog)

    if action:
        query = query.filter(ModerationLog.action == action)
    if target_user_id:
        query = query.filter(ModerationLog.target_user_id == target_user_id)
    if moderator_id:
        query = query.filter(ModerationLog.moderator_id == moderator_id)

    total = query.count()
    logs = query.order_by(desc(ModerationLog.created_at)).offset(
        (page - 1) * limit
    ).limit(limit).all()

    result = []
    for log in logs:
        target_user = db.query(User).filter(User.id == log.target_user_id).first() if log.target_user_id else None
        moderator = db.query(User).filter(User.id == log.moderator_id).first() if log.moderator_id else None

        result.append({
            "id": log.id,
            "action": log.action,
            "target_user_id": log.target_user_id,
            "target_username": target_user.username if target_user else None,
            "moderator_id": log.moderator_id,
            "moderator_username": moderator.username if moderator else "Sistem",
            "reason": log.reason,
            "details": log.details,
            "content_type": log.content_type,
            "content_id": log.content_id,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None
        })

    return {
        "logs": result,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }


# ==================== STATS ====================

@router.get("/stats")
async def get_moderation_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_moderator)
):
    """Moderasyon istatistikleri"""
    now = datetime.utcnow()

    # Toplam kara liste kelimesi
    blacklist_count = db.query(func.count(ContentBlacklist.id)).filter(
        ContentBlacklist.is_active == True
    ).scalar() or 0

    # Aktif uyari sayisi
    active_warnings = db.query(func.count(UserWarning.id)).filter(
        UserWarning.expires_at > now
    ).scalar() or 0

    # Aktif ban sayisi
    active_bans = db.query(func.count(ForumBan.id)).filter(
        ForumBan.expires_at > now
    ).scalar() or 0

    # Son 24 saatte verilen uyarilar
    one_day_ago = now - timedelta(days=1)
    warnings_last_24h = db.query(func.count(UserWarning.id)).filter(
        UserWarning.created_at >= one_day_ago
    ).scalar() or 0

    # Son 24 saatte verilen banlar
    bans_last_24h = db.query(func.count(ForumBan.id)).filter(
        ForumBan.created_at >= one_day_ago
    ).scalar() or 0

    # Son 7 gunde moderasyon islemleri
    one_week_ago = now - timedelta(days=7)
    actions_last_week = db.query(func.count(ModerationLog.id)).filter(
        ModerationLog.created_at >= one_week_ago
    ).scalar() or 0

    return {
        "blacklist_words": blacklist_count,
        "active_warnings": active_warnings,
        "active_bans": active_bans,
        "warnings_last_24h": warnings_last_24h,
        "bans_last_24h": bans_last_24h,
        "actions_last_week": actions_last_week
    }


# ==================== HELPER FUNCTIONS ====================

def _log_moderation_action(
    db: Session,
    action: str,
    moderator_id: int,
    reason: str,
    target_user_id: int = None,
    content_type: str = None,
    content_id: int = None,
    details: dict = None,
    ip_address: str = None
):
    """Moderasyon islemini logla"""
    try:
        log = ModerationLog(
            action=action,
            target_user_id=target_user_id,
            moderator_id=moderator_id,
            reason=reason,
            content_type=content_type,
            content_id=content_id,
            details=details,
            ip_address=ip_address
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Moderasyon log hatasi: {e}")
        db.rollback()
