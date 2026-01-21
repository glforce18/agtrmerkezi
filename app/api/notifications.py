"""
🔔 AGTR Notification System API
Push Notifications, Email Notifications, In-App Notifications
"""
import json
import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import User, UserRole
from app.services.email import email_service

router = APIRouter()

# ============================================================================
# DATABASE TABLES
# ============================================================================

def ensure_notification_tables(db: Session):
    """Bildirim tablolarını oluştur"""
    try:
        # Bildirimler
        db.execute(text("""CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT,
            notification_type ENUM('info', 'success', 'warning', 'error', 'payment', 'server', 'forum', 'system') DEFAULT 'info',
            action_url VARCHAR(500),
            action_text VARCHAR(100),
            icon VARCHAR(50),
            is_read BOOLEAN DEFAULT FALSE,
            is_archived BOOLEAN DEFAULT FALSE,
            read_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user (user_id),
            INDEX idx_read (user_id, is_read)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Push subscription'lar
        db.execute(text("""CREATE TABLE IF NOT EXISTS push_subscriptions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            endpoint TEXT NOT NULL,
            p256dh VARCHAR(500),
            auth VARCHAR(500),
            user_agent TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_used DATETIME,
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Bildirim tercihleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS notification_preferences (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            email_enabled BOOLEAN DEFAULT TRUE,
            push_enabled BOOLEAN DEFAULT TRUE,
            email_payment BOOLEAN DEFAULT TRUE,
            email_server BOOLEAN DEFAULT TRUE,
            email_forum BOOLEAN DEFAULT TRUE,
            email_marketing BOOLEAN DEFAULT FALSE,
            push_payment BOOLEAN DEFAULT TRUE,
            push_server BOOLEAN DEFAULT TRUE,
            push_forum BOOLEAN DEFAULT TRUE,
            quiet_hours_start TIME,
            quiet_hours_end TIME,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Toplu bildirimler (admin için)
        db.execute(text("""CREATE TABLE IF NOT EXISTS broadcast_notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            message TEXT,
            target_type ENUM('all', 'role', 'custom') DEFAULT 'all',
            target_value VARCHAR(255),
            sent_count INT DEFAULT 0,
            created_by INT,
            scheduled_at DATETIME,
            sent_at DATETIME,
            status ENUM('draft', 'scheduled', 'sent', 'cancelled') DEFAULT 'draft',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        db.commit()
    except Exception:
        db.rollback()


# ============================================================================
# IN-APP NOTIFICATIONS
# ============================================================================

@router.get("/")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """📋 Bildirimler"""
    ensure_notification_tables(db)
    
    q = "SELECT * FROM notifications WHERE user_id = :uid AND is_archived = FALSE"
    p = {"uid": current_user.id, "lim": limit}
    
    if unread_only:
        q += " AND is_read = FALSE"
    
    q += " ORDER BY created_at DESC LIMIT :lim"
    
    rows = db.execute(text(q), p).fetchall()
    notifications = [{
        "id": r[0], "title": r[2], "message": r[3],
        "type": r[4], "action_url": r[5], "action_text": r[6],
        "icon": r[7], "is_read": bool(r[8]),
        "created_at": r[11].isoformat() if r[11] else None
    } for r in rows]
    
    # Okunmamış sayısı
    unread_count = db.execute(text(
        "SELECT COUNT(*) FROM notifications WHERE user_id = :uid AND is_read = FALSE AND is_archived = FALSE"
    ), {"uid": current_user.id}).fetchone()[0]
    
    return {
        "success": True,
        "notifications": notifications,
        "unread_count": unread_count
    }


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """✅ Okundu işaretle"""
    db.execute(text("""
        UPDATE notifications SET is_read = TRUE, read_at = NOW()
        WHERE id = :id AND user_id = :uid
    """), {"id": notification_id, "uid": current_user.id})
    db.commit()
    
    return {"success": True}


@router.post("/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """✅ Tümünü okundu işaretle"""
    db.execute(text("""
        UPDATE notifications SET is_read = TRUE, read_at = NOW()
        WHERE user_id = :uid AND is_read = FALSE
    """), {"uid": current_user.id})
    db.commit()
    
    return {"success": True, "message": "Tüm bildirimler okundu"}


@router.delete("/{notification_id}")
async def archive_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """🗑️ Bildirimi arşivle"""
    db.execute(text("""
        UPDATE notifications SET is_archived = TRUE
        WHERE id = :id AND user_id = :uid
    """), {"id": notification_id, "uid": current_user.id})
    db.commit()

    return {"success": True}


@router.delete("/")
async def clear_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """🗑️ Tüm bildirimleri temizle"""
    ensure_notification_tables(db)

    db.execute(text("""
        UPDATE notifications SET is_archived = TRUE
        WHERE user_id = :uid AND is_archived = FALSE
    """), {"uid": current_user.id})
    db.commit()

    return {"success": True, "message": "Tüm bildirimler temizlendi"}


@router.post("/cleanup")
async def cleanup_old_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """🧹 Eski bildirimleri temizle (30 günden eski)"""
    ensure_notification_tables(db)

    # 30 günden eski bildirimleri arşivle
    result = db.execute(text("""
        UPDATE notifications SET is_archived = TRUE
        WHERE user_id = :uid
        AND is_archived = FALSE
        AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)
    """), {"uid": current_user.id})
    db.commit()

    # Okunmuş ve 7 günden eski bildirimleri de arşivle
    db.execute(text("""
        UPDATE notifications SET is_archived = TRUE
        WHERE user_id = :uid
        AND is_archived = FALSE
        AND is_read = TRUE
        AND created_at < DATE_SUB(NOW(), INTERVAL 7 DAY)
    """), {"uid": current_user.id})
    db.commit()

    return {"success": True, "message": "Eski bildirimler temizlendi"}


# ============================================================================
# CREATE NOTIFICATIONS
# ============================================================================

async def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str = None,
    notification_type: str = "info",
    action_url: str = None,
    action_text: str = None,
    icon: str = None,
    send_push: bool = True,
    send_email: bool = False
):
    """Bildirim oluştur"""
    ensure_notification_tables(db)

    # Icon belirle
    if not icon:
        icon_map = {
            "info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌",
            "payment": "💰", "server": "🖥️", "forum": "💬", "system": "🔧"
        }
        icon = icon_map.get(notification_type, "📢")

    # Veritabanına kaydet
    db.execute(text("""
        INSERT INTO notifications (user_id, title, message, notification_type, action_url, action_text, icon)
        VALUES (:uid, :title, :msg, :type, :url, :text, :icon)
    """), {
        "uid": user_id, "title": title, "msg": message,
        "type": notification_type, "url": action_url, "text": action_text, "icon": icon
    })
    db.commit()

    # Push bildirimi
    if send_push:
        await send_push_notification(db, user_id, title, message, action_url)

    # Email bildirimi - sadece kullanıcının emaili varsa gönder
    if send_email:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.email:
            try:
                await email_service.send_notification_email(
                    to=user.email,
                    username=user.username,
                    title=title,
                    message=message or "",
                    action_url=action_url,
                    action_text=action_text
                )
            except Exception:
                # Email gönderimi başarısız olsa bile bildirim oluşturulmuş durumda
                pass


async def create_notification_for_users(
    db: Session,
    user_ids: list,
    title: str,
    message: str = None,
    notification_type: str = "info",
    action_url: str = None
):
    """Birden fazla kullanıcıya bildirim"""
    for uid in user_ids:
        await create_notification(db, uid, title, message, notification_type, action_url)


# ============================================================================
# PUSH NOTIFICATIONS
# ============================================================================

@router.post("/push/subscribe")
async def subscribe_push(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """📲 Push aboneliği"""
    ensure_notification_tables(db)
    
    endpoint = data.get("endpoint")
    keys = data.get("keys", {})
    
    # Mevcut abonelik var mı?
    existing = db.execute(text("""
        SELECT id FROM push_subscriptions WHERE user_id = :uid AND endpoint = :ep
    """), {"uid": current_user.id, "ep": endpoint}).fetchone()
    
    if existing:
        db.execute(text("""
            UPDATE push_subscriptions SET 
                p256dh = :p256dh, auth = :auth, is_active = TRUE, last_used = NOW()
            WHERE id = :id
        """), {"id": existing[0], "p256dh": keys.get("p256dh"), "auth": keys.get("auth")})
    else:
        db.execute(text("""
            INSERT INTO push_subscriptions (user_id, endpoint, p256dh, auth, user_agent)
            VALUES (:uid, :ep, :p256dh, :auth, :ua)
        """), {
            "uid": current_user.id, "ep": endpoint,
            "p256dh": keys.get("p256dh"), "auth": keys.get("auth"),
            "ua": data.get("user_agent")
        })
    
    db.commit()
    return {"success": True, "message": "Push bildirimleri aktif"}


@router.delete("/push/unsubscribe")
async def unsubscribe_push(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """🔕 Push aboneliğini iptal et"""
    endpoint = data.get("endpoint")
    
    db.execute(text("""
        UPDATE push_subscriptions SET is_active = FALSE
        WHERE user_id = :uid AND endpoint = :ep
    """), {"uid": current_user.id, "ep": endpoint})
    db.commit()
    
    return {"success": True, "message": "Push bildirimleri devre dışı"}


async def send_push_notification(db: Session, user_id: int, title: str, body: str = None, url: str = None):
    """Push bildirimi gönder"""
    try:
        from pywebpush import WebPushException, webpush
        
        VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
        os.getenv("VAPID_PUBLIC_KEY", "")
        VAPID_EMAIL = os.getenv("VAPID_EMAIL", "admin@agtrmerkezi.com")
        
        if not VAPID_PRIVATE_KEY:
            return
        
        subscriptions = db.execute(text("""
            SELECT endpoint, p256dh, auth FROM push_subscriptions
            WHERE user_id = :uid AND is_active = TRUE
        """), {"uid": user_id}).fetchall()
        
        payload = json.dumps({
            "title": title,
            "body": body or "",
            "icon": "/static/images/logo.svg",
            "badge": "/static/images/badge.png",
            "url": url or "/",
            "timestamp": datetime.now().timestamp()
        })
        
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub[0],
                        "keys": {"p256dh": sub[1], "auth": sub[2]}
                    },
                    data=payload,
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": f"mailto:{VAPID_EMAIL}"}
                )
            except WebPushException as e:
                # Subscription geçersiz, sil
                if e.response and e.response.status_code in [404, 410]:
                    db.execute(text(
                        "DELETE FROM push_subscriptions WHERE endpoint = :ep"
                    ), {"ep": sub[0]})
    except ImportError:
        pass  # pywebpush yüklü değil
    except Exception as e:
        print(f"Push error: {e}")


# ============================================================================
# NOTIFICATION PREFERENCES
# ============================================================================

@router.get("/preferences")
async def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """⚙️ Bildirim tercihleri"""
    ensure_notification_tables(db)
    
    prefs = db.execute(text("""
        SELECT * FROM notification_preferences WHERE user_id = :uid
    """), {"uid": current_user.id}).fetchone()
    
    if not prefs:
        # Varsayılan oluştur
        db.execute(text("INSERT INTO notification_preferences (user_id) VALUES (:uid)"), {"uid": current_user.id})
        db.commit()
        prefs = db.execute(text("SELECT * FROM notification_preferences WHERE user_id = :uid"), {"uid": current_user.id}).fetchone()
    
    return {
        "success": True,
        "preferences": {
            "email_enabled": bool(prefs[2]),
            "push_enabled": bool(prefs[3]),
            "email_payment": bool(prefs[4]),
            "email_server": bool(prefs[5]),
            "email_forum": bool(prefs[6]),
            "email_marketing": bool(prefs[7]),
            "push_payment": bool(prefs[8]),
            "push_server": bool(prefs[9]),
            "push_forum": bool(prefs[10]),
            "quiet_hours_start": str(prefs[11]) if prefs[11] else None,
            "quiet_hours_end": str(prefs[12]) if prefs[12] else None
        }
    }


@router.put("/preferences")
async def update_preferences(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """⚙️ Bildirim tercihlerini güncelle"""
    ensure_notification_tables(db)
    
    db.execute(text("""
        INSERT INTO notification_preferences (user_id, email_enabled, push_enabled,
            email_payment, email_server, email_forum, email_marketing,
            push_payment, push_server, push_forum, quiet_hours_start, quiet_hours_end)
        VALUES (:uid, :ee, :pe, :ep, :es, :ef, :em, :pp, :ps, :pf, :qhs, :qhe)
        ON DUPLICATE KEY UPDATE
            email_enabled = :ee, push_enabled = :pe,
            email_payment = :ep, email_server = :es, email_forum = :ef, email_marketing = :em,
            push_payment = :pp, push_server = :ps, push_forum = :pf,
            quiet_hours_start = :qhs, quiet_hours_end = :qhe
    """), {
        "uid": current_user.id,
        "ee": data.get("email_enabled", True),
        "pe": data.get("push_enabled", True),
        "ep": data.get("email_payment", True),
        "es": data.get("email_server", True),
        "ef": data.get("email_forum", True),
        "em": data.get("email_marketing", False),
        "pp": data.get("push_payment", True),
        "ps": data.get("push_server", True),
        "pf": data.get("push_forum", True),
        "qhs": data.get("quiet_hours_start"),
        "qhe": data.get("quiet_hours_end")
    })
    db.commit()
    
    return {"success": True, "message": "Tercihler güncellendi"}


# ============================================================================
# BROADCAST (Admin)
# ============================================================================

@router.post("/broadcast")
async def send_broadcast(
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """📢 Toplu bildirim gönder"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_notification_tables(db)
    
    title = data.get("title")
    message = data.get("message")
    target_type = data.get("target_type", "all")
    target_value = data.get("target_value")
    
    # Broadcast kaydı
    r = db.execute(text("""
        INSERT INTO broadcast_notifications (title, message, target_type, target_value, created_by, status)
        VALUES (:title, :msg, :type, :value, :uid, 'sent')
    """), {
        "title": title, "msg": message, "type": target_type,
        "value": target_value, "uid": current_user.id
    })
    broadcast_id = r.lastrowid
    db.commit()
    
    # Background'da gönder
    background_tasks.add_task(send_broadcast_notifications, db, broadcast_id, title, message, target_type, target_value)
    
    return {"success": True, "broadcast_id": broadcast_id, "message": "Bildirimler gönderiliyor"}


async def send_broadcast_notifications(db: Session, broadcast_id: int, title: str, message: str, target_type: str, target_value: str):
    """Toplu bildirimleri gönder"""
    if target_type == "all":
        users = db.execute(text("SELECT id FROM users WHERE status = 'active'")).fetchall()
    elif target_type == "role":
        users = db.execute(text("SELECT id FROM users WHERE role = :role"), {"role": target_value}).fetchall()
    else:
        user_ids = target_value.split(",") if target_value else []
        users = [(int(uid),) for uid in user_ids]
    
    count = 0
    for user in users:
        await create_notification(db, user[0], title, message, "system", send_push=True)
        count += 1
    
    # Güncelle
    db.execute(text("""
        UPDATE broadcast_notifications SET sent_count = :count, sent_at = NOW()
        WHERE id = :id
    """), {"count": count, "id": broadcast_id})
    db.commit()


@router.get("/broadcast/history")
async def broadcast_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """📋 Toplu bildirim geçmişi"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_notification_tables(db)
    
    rows = db.execute(text("""
        SELECT * FROM broadcast_notifications ORDER BY created_at DESC LIMIT 50
    """)).fetchall()
    
    broadcasts = [{
        "id": r[0], "title": r[1], "message": r[2],
        "target_type": r[3], "sent_count": r[5],
        "status": r[9], "sent_at": r[8].isoformat() if r[8] else None
    } for r in rows]
    
    return {"success": True, "broadcasts": broadcasts}
