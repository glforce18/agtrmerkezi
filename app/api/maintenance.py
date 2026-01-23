# ============================================
# AGTR v6.0 - Bakım Modu API
# Dosya: app/api/maintenance.py
# ============================================

import logging
from datetime import datetime

logger = logging.getLogger(__name__)
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import User

router = APIRouter()

# ============================================
# BAKIM MODU ÖZELLİKLERİ
# ============================================

MAINTENANCE_FEATURES = {
    "payments": {
        "name": "Para Yatırma",
        "description": "Kullanıcıların bakiye yüklemesi",
        "icon": "💳"
    },
    "withdrawals": {
        "name": "Para Çekme",
        "description": "Kullanıcıların para çekmesi",
        "icon": "💸"
    },
    "server_rental": {
        "name": "Sunucu Kiralama",
        "description": "Yeni sunucu kiralama işlemleri",
        "icon": "🖥️"
    },
    "shop": {
        "name": "Mağaza",
        "description": "Mağazadan alışveriş yapma",
        "icon": "🛒"
    },
    "forum": {
        "name": "Forum",
        "description": "Forum konu ve mesaj oluşturma",
        "icon": "💬"
    },
    "tournaments": {
        "name": "Turnuvalar",
        "description": "Turnuva kayıt ve işlemleri",
        "icon": "🏆"
    },
    "transfers": {
        "name": "Transferler",
        "description": "Kullanıcılar arası transfer",
        "icon": "🔄"
    },
    "registration": {
        "name": "Kayıt",
        "description": "Yeni kullanıcı kayıtları",
        "icon": "📝"
    },
    "clans": {
        "name": "Klanlar",
        "description": "Klan oluşturma ve katılma",
        "icon": "👥"
    },
    "jackpot": {
        "name": "Jackpot",
        "description": "Jackpot oyunu",
        "icon": "🎰"
    }
}


# ============================================
# DATABASE SETUP
# ============================================

def ensure_maintenance_table(db: Session):
    """Bakım tablosunu oluştur"""
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS maintenance_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                feature_key VARCHAR(50) UNIQUE NOT NULL,
                is_enabled BOOLEAN DEFAULT FALSE,
                message TEXT,
                enabled_by INT,
                enabled_at DATETIME,
                estimated_end DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_feature (feature_key),
                FOREIGN KEY (enabled_by) REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """))
        db.commit()
    except Exception:
        db.rollback()


# ============================================
# SCHEMAS
# ============================================

class MaintenanceUpdate(BaseModel):
    is_enabled: bool
    message: Optional[str] = None
    estimated_end: Optional[str] = None


class MaintenanceBulkUpdate(BaseModel):
    features: List[str]
    is_enabled: bool
    message: Optional[str] = None


# ============================================
# PUBLIC ENDPOINTS
# ============================================

@router.get("/status")
async def get_maintenance_status(db: Session = Depends(get_db)):
    """🔍 Bakım durumunu kontrol et (public)"""
    ensure_maintenance_table(db)

    rows = db.execute(text("""
        SELECT feature_key, is_enabled, message, estimated_end
        FROM maintenance_settings
        WHERE is_enabled = TRUE
    """)).fetchall()

    maintenance_active = {}
    for r in rows:
        maintenance_active[r[0]] = {
            "enabled": True,
            "message": r[2] or "Bu özellik şu anda bakımdadır.",
            "estimated_end": r[3].isoformat() if r[3] else None
        }

    return {
        "success": True,
        "maintenance": maintenance_active,
        "features": list(maintenance_active.keys())
    }


@router.get("/check/{feature}")
async def check_feature_maintenance(feature: str, db: Session = Depends(get_db)):
    """🔍 Belirli bir özelliğin bakım durumunu kontrol et"""
    ensure_maintenance_table(db)

    if feature not in MAINTENANCE_FEATURES:
        return {"success": True, "in_maintenance": False}

    row = db.execute(text("""
        SELECT is_enabled, message, estimated_end
        FROM maintenance_settings
        WHERE feature_key = :feature
    """), {"feature": feature}).fetchone()

    if row and row[0]:
        return {
            "success": True,
            "in_maintenance": True,
            "message": row[1] or f"{MAINTENANCE_FEATURES[feature]['name']} şu anda bakımdadır.",
            "estimated_end": row[2].isoformat() if row[2] else None
        }

    return {"success": True, "in_maintenance": False}


# ============================================
# ADMIN ENDPOINTS
# ============================================

@router.get("/admin/list")
async def admin_list_maintenance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """📋 Tüm bakım ayarlarını listele (admin)"""
    ensure_maintenance_table(db)

    rows = db.execute(text("""
        SELECT m.feature_key, m.is_enabled, m.message, m.estimated_end,
               m.enabled_at, u.username as enabled_by
        FROM maintenance_settings m
        LEFT JOIN users u ON m.enabled_by = u.id
    """)).fetchall()

    # Mevcut ayarları dict'e çevir
    settings_map = {}
    for r in rows:
        settings_map[r[0]] = {
            "is_enabled": bool(r[1]),
            "message": r[2],
            "estimated_end": r[3].isoformat() if r[3] else None,
            "enabled_at": r[4].isoformat() if r[4] else None,
            "enabled_by": r[5]
        }

    # Tüm özellikleri listele
    features = []
    for key, info in MAINTENANCE_FEATURES.items():
        setting = settings_map.get(key, {})
        features.append({
            "key": key,
            "name": info["name"],
            "description": info["description"],
            "icon": info["icon"],
            "is_enabled": setting.get("is_enabled", False),
            "message": setting.get("message"),
            "estimated_end": setting.get("estimated_end"),
            "enabled_at": setting.get("enabled_at"),
            "enabled_by": setting.get("enabled_by")
        })

    # Aktif bakım sayısı
    active_count = sum(1 for f in features if f["is_enabled"])

    return {
        "success": True,
        "features": features,
        "active_count": active_count,
        "total_count": len(features)
    }


@router.put("/admin/{feature}")
async def admin_update_maintenance(
    feature: str,
    data: MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """🔧 Bakım durumunu güncelle (admin)"""
    ensure_maintenance_table(db)

    if feature not in MAINTENANCE_FEATURES:
        raise HTTPException(400, f"Geçersiz özellik: {feature}")

    # Estimated end parse
    estimated_end = None
    if data.estimated_end:
        try:
            estimated_end = datetime.fromisoformat(data.estimated_end.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Failed to parse estimated_end date: {e}")
            pass

    # Upsert
    existing = db.execute(text(
        "SELECT id FROM maintenance_settings WHERE feature_key = :feature"
    ), {"feature": feature}).fetchone()

    if existing:
        db.execute(text("""
            UPDATE maintenance_settings
            SET is_enabled = :enabled,
                message = :message,
                estimated_end = :end,
                enabled_by = :user_id,
                enabled_at = CASE WHEN :enabled = TRUE THEN NOW() ELSE enabled_at END
            WHERE feature_key = :feature
        """), {
            "feature": feature,
            "enabled": data.is_enabled,
            "message": data.message,
            "end": estimated_end,
            "user_id": current_user.id if data.is_enabled else None
        })
    else:
        db.execute(text("""
            INSERT INTO maintenance_settings (feature_key, is_enabled, message, estimated_end, enabled_by, enabled_at)
            VALUES (:feature, :enabled, :message, :end, :user_id, CASE WHEN :enabled = TRUE THEN NOW() ELSE NULL END)
        """), {
            "feature": feature,
            "enabled": data.is_enabled,
            "message": data.message,
            "end": estimated_end,
            "user_id": current_user.id if data.is_enabled else None
        })

    db.commit()

    # Redis cache temizle
    try:
        from app.core.redis_manager import redis_manager
        import asyncio
        asyncio.create_task(redis_manager.delete("maintenance:status"))
    except Exception as e:
        logger.warning(f"Failed to clear Redis cache: {e}")
        pass

    action = "bakıma alındı" if data.is_enabled else "bakımdan çıkarıldı"
    feature_name = MAINTENANCE_FEATURES[feature]["name"]

    return {
        "success": True,
        "message": f"{feature_name} {action}",
        "feature": feature,
        "is_enabled": data.is_enabled
    }


@router.post("/admin/bulk")
async def admin_bulk_maintenance(
    data: MaintenanceBulkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """🔧 Toplu bakım güncellemesi (admin)"""
    ensure_maintenance_table(db)

    updated = []
    for feature in data.features:
        if feature not in MAINTENANCE_FEATURES:
            continue

        existing = db.execute(text(
            "SELECT id FROM maintenance_settings WHERE feature_key = :feature"
        ), {"feature": feature}).fetchone()

        if existing:
            db.execute(text("""
                UPDATE maintenance_settings
                SET is_enabled = :enabled, message = :message,
                    enabled_by = :user_id,
                    enabled_at = CASE WHEN :enabled = TRUE THEN NOW() ELSE enabled_at END
                WHERE feature_key = :feature
            """), {
                "feature": feature,
                "enabled": data.is_enabled,
                "message": data.message,
                "user_id": current_user.id if data.is_enabled else None
            })
        else:
            db.execute(text("""
                INSERT INTO maintenance_settings (feature_key, is_enabled, message, enabled_by, enabled_at)
                VALUES (:feature, :enabled, :message, :user_id, CASE WHEN :enabled = TRUE THEN NOW() ELSE NULL END)
            """), {
                "feature": feature,
                "enabled": data.is_enabled,
                "message": data.message,
                "user_id": current_user.id if data.is_enabled else None
            })

        updated.append(feature)

    db.commit()

    action = "bakıma alındı" if data.is_enabled else "bakımdan çıkarıldı"

    return {
        "success": True,
        "message": f"{len(updated)} özellik {action}",
        "updated_features": updated
    }


@router.post("/admin/all-on")
async def admin_enable_all_maintenance(
    message: Optional[str] = "Site genel bakımdadır. Lütfen daha sonra tekrar deneyin.",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """🚨 Tüm özellikleri bakıma al (admin)"""
    ensure_maintenance_table(db)

    for feature in MAINTENANCE_FEATURES.keys():
        existing = db.execute(text(
            "SELECT id FROM maintenance_settings WHERE feature_key = :feature"
        ), {"feature": feature}).fetchone()

        if existing:
            db.execute(text("""
                UPDATE maintenance_settings
                SET is_enabled = TRUE, message = :message, enabled_by = :user_id, enabled_at = NOW()
                WHERE feature_key = :feature
            """), {"feature": feature, "message": message, "user_id": current_user.id})
        else:
            db.execute(text("""
                INSERT INTO maintenance_settings (feature_key, is_enabled, message, enabled_by, enabled_at)
                VALUES (:feature, TRUE, :message, :user_id, NOW())
            """), {"feature": feature, "message": message, "user_id": current_user.id})

    db.commit()

    return {
        "success": True,
        "message": "Tüm özellikler bakıma alındı",
        "count": len(MAINTENANCE_FEATURES)
    }


@router.post("/admin/all-off")
async def admin_disable_all_maintenance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """✅ Tüm bakımları kapat (admin)"""
    ensure_maintenance_table(db)

    db.execute(text("UPDATE maintenance_settings SET is_enabled = FALSE"))
    db.commit()

    return {
        "success": True,
        "message": "Tüm bakımlar kapatıldı"
    }
