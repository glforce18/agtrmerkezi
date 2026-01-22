"""
🎨 AGTR Profile Customization API
User profile theming and personalization
"""
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User

router = APIRouter()


# ============================================================================
# DATABASE SETUP
# ============================================================================

def ensure_customization_tables(db: Session):
    """Profil özelleştirme tablolarını oluştur"""
    try:
        # Kullanıcı özelleştirmeleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS profile_customizations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            banner_color VARCHAR(20) DEFAULT '#1e293b',
            banner_pattern VARCHAR(50),
            banner_image VARCHAR(500),
            name_color VARCHAR(20),
            name_effect VARCHAR(50),
            avatar_frame VARCHAR(50),
            avatar_effect VARCHAR(50),
            name_badge VARCHAR(50),
            bio_style VARCHAR(50),
            profile_music_url VARCHAR(500),
            custom_css TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))

        # Mevcut özelleştirme öğeleri (çerçeveler, rozetler, vb.)
        db.execute(text("""CREATE TABLE IF NOT EXISTS customization_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            item_type VARCHAR(50) NOT NULL,
            item_key VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            preview_url VARCHAR(500),
            css_class VARCHAR(100),
            css_style TEXT,
            unlock_type VARCHAR(50) DEFAULT 'free',
            unlock_value INT DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            display_order INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))

        # Kullanıcının sahip olduğu öğeler
        db.execute(text("""CREATE TABLE IF NOT EXISTS user_customization_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            item_key VARCHAR(50) NOT NULL,
            obtained_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_item (user_id, item_key),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))

        # Default öğeleri ekle
        db.execute(text("""INSERT IGNORE INTO customization_items
            (item_type, item_key, name, description, unlock_type, unlock_value, display_order) VALUES
            -- Avatar Frames
            ('frame', 'frame_default', 'Varsayılan', 'Standart çerçeve', 'free', 0, 1),
            ('frame', 'frame_gold', 'Altın', 'Altın renkli çerçeve', 'vip', 1, 2),
            ('frame', 'frame_diamond', 'Elmas', 'Elmas çerçeve', 'vip', 2, 3),
            ('frame', 'frame_fire', 'Ateş', 'Ateş efektli çerçeve', 'level', 25, 4),
            ('frame', 'frame_ice', 'Buz', 'Buz efektli çerçeve', 'level', 50, 5),
            ('frame', 'frame_lightning', 'Şimşek', 'Şimşek efektli çerçeve', 'level', 75, 6),
            ('frame', 'frame_legendary', 'Efsanevi', 'Efsanevi çerçeve', 'level', 100, 7),

            -- Name Badges
            ('badge', 'badge_none', 'Yok', 'Rozet yok', 'free', 0, 1),
            ('badge', 'badge_star', '⭐ Yıldız', 'Yıldız rozeti', 'level', 10, 2),
            ('badge', 'badge_fire', '🔥 Ateş', 'Ateş rozeti', 'level', 20, 3),
            ('badge', 'badge_crown', '👑 Taç', 'Taç rozeti', 'vip', 1, 4),
            ('badge', 'badge_diamond', '💎 Elmas', 'Elmas rozeti', 'vip', 2, 5),
            ('badge', 'badge_verified', '✓ Onaylı', 'Onaylı rozet', 'achievement', 1, 6),

            -- Banner Patterns
            ('pattern', 'pattern_none', 'Düz', 'Düz arka plan', 'free', 0, 1),
            ('pattern', 'pattern_dots', 'Noktalar', 'Nokta deseni', 'free', 0, 2),
            ('pattern', 'pattern_grid', 'Izgara', 'Izgara deseni', 'level', 5, 3),
            ('pattern', 'pattern_waves', 'Dalgalar', 'Dalga deseni', 'level', 15, 4),
            ('pattern', 'pattern_circuit', 'Devre', 'Devre deseni', 'level', 30, 5),
            ('pattern', 'pattern_gaming', 'Gaming', 'Oyun deseni', 'vip', 1, 6),

            -- Name Colors
            ('color', 'color_default', 'Varsayılan', 'Beyaz renk', 'free', 0, 1),
            ('color', 'color_orange', 'Turuncu', 'Turuncu renk', 'level', 5, 2),
            ('color', 'color_blue', 'Mavi', 'Mavi renk', 'level', 10, 3),
            ('color', 'color_green', 'Yeşil', 'Yeşil renk', 'level', 15, 4),
            ('color', 'color_purple', 'Mor', 'Mor renk', 'level', 20, 5),
            ('color', 'color_gold', 'Altın', 'Altın renk', 'vip', 1, 6),
            ('color', 'color_rainbow', 'Gökkuşağı', 'Animasyonlu renk', 'vip', 2, 7)
        """))

        db.commit()
    except Exception:
        db.rollback()


# ============================================================================
# SCHEMAS
# ============================================================================

class CustomizationUpdate(BaseModel):
    banner_color: Optional[str] = None
    banner_pattern: Optional[str] = None
    banner_image: Optional[str] = None
    name_color: Optional[str] = None
    name_effect: Optional[str] = None
    avatar_frame: Optional[str] = None
    avatar_effect: Optional[str] = None
    name_badge: Optional[str] = None
    bio_style: Optional[str] = None
    profile_music_url: Optional[str] = None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("")
async def get_my_customization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🎨 Kendi profil özelleştirmemi getir"""
    ensure_customization_tables(db)

    # Mevcut özelleştirmeleri al
    custom = db.execute(text("""
        SELECT banner_color, banner_pattern, banner_image, name_color, name_effect,
               avatar_frame, avatar_effect, name_badge, bio_style, profile_music_url
        FROM profile_customizations WHERE user_id = :uid
    """), {"uid": current_user.id}).fetchone()

    if custom:
        customization = {
            "banner_color": custom[0],
            "banner_pattern": custom[1],
            "banner_image": custom[2],
            "name_color": custom[3],
            "name_effect": custom[4],
            "avatar_frame": custom[5],
            "avatar_effect": custom[6],
            "name_badge": custom[7],
            "bio_style": custom[8],
            "profile_music_url": custom[9]
        }
    else:
        customization = {
            "banner_color": "#1e293b",
            "banner_pattern": None,
            "banner_image": None,
            "name_color": None,
            "name_effect": None,
            "avatar_frame": None,
            "avatar_effect": None,
            "name_badge": None,
            "bio_style": None,
            "profile_music_url": None
        }

    # Sahip olunan öğeleri al
    owned = db.execute(text("""
        SELECT item_key FROM user_customization_items WHERE user_id = :uid
    """), {"uid": current_user.id}).fetchall()

    owned_items = [r[0] for r in owned]

    return {
        "success": True,
        "customization": customization,
        "owned_items": owned_items
    }


@router.get("/user/{user_id}")
async def get_user_customization(
    user_id: int,
    db: Session = Depends(get_db)
):
    """🎨 Kullanıcının profil özelleştirmesini getir"""
    ensure_customization_tables(db)

    custom = db.execute(text("""
        SELECT banner_color, banner_pattern, banner_image, name_color, name_effect,
               avatar_frame, avatar_effect, name_badge, bio_style
        FROM profile_customizations WHERE user_id = :uid
    """), {"uid": user_id}).fetchone()

    if custom:
        customization = {
            "banner_color": custom[0],
            "banner_pattern": custom[1],
            "banner_image": custom[2],
            "name_color": custom[3],
            "name_effect": custom[4],
            "avatar_frame": custom[5],
            "avatar_effect": custom[6],
            "name_badge": custom[7],
            "bio_style": custom[8]
        }
    else:
        customization = None

    return {"success": True, "customization": customization}


@router.put("")
async def update_customization(
    data: CustomizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """💾 Profil özelleştirmesini güncelle"""
    ensure_customization_tables(db)

    # Mevcut kayıt var mı kontrol et
    existing = db.execute(text(
        "SELECT id FROM profile_customizations WHERE user_id = :uid"
    ), {"uid": current_user.id}).fetchone()

    update_data = data.dict(exclude_unset=True, exclude_none=False)

    if existing:
        # Güncelle
        set_clauses = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
        if set_clauses:
            update_data["uid"] = current_user.id
            db.execute(text(f"""
                UPDATE profile_customizations SET {set_clauses} WHERE user_id = :uid
            """), update_data)
    else:
        # Yeni kayıt oluştur
        update_data["user_id"] = current_user.id
        columns = ", ".join(update_data.keys())
        values = ", ".join([f":{k}" for k in update_data.keys()])
        db.execute(text(f"""
            INSERT INTO profile_customizations ({columns}) VALUES ({values})
        """), update_data)

    db.commit()

    return {"success": True, "message": "Özelleştirme kaydedildi"}


@router.get("/items")
async def get_customization_items(
    item_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📦 Mevcut özelleştirme öğelerini getir"""
    ensure_customization_tables(db)

    query = """
        SELECT id, item_type, item_key, name, description, preview_url,
               css_class, unlock_type, unlock_value, display_order
        FROM customization_items WHERE is_active = TRUE
    """
    params = {}

    if item_type:
        query += " AND item_type = :type"
        params["type"] = item_type

    query += " ORDER BY item_type, display_order"

    rows = db.execute(text(query), params).fetchall()

    # Kullanıcının sahip olduğu öğeler
    owned = db.execute(text("""
        SELECT item_key FROM user_customization_items WHERE user_id = :uid
    """), {"uid": current_user.id}).fetchall()
    owned_keys = {r[0] for r in owned}

    # Kullanıcı seviyesi ve VIP durumu
    user_level = getattr(current_user, 'level', 1) or 1
    user_vip = getattr(current_user, 'vip_level', 0) or 0

    items = []
    for r in rows:
        item = {
            "id": r[0],
            "type": r[1],
            "key": r[2],
            "name": r[3],
            "description": r[4],
            "preview_url": r[5],
            "css_class": r[6],
            "unlock_type": r[7],
            "unlock_value": r[8],
            "display_order": r[9],
            "owned": r[2] in owned_keys,
            "locked": False
        }

        # Kilit durumunu kontrol et
        if r[7] == "free":
            item["locked"] = False
        elif r[7] == "level":
            item["locked"] = user_level < r[8]
        elif r[7] == "vip":
            item["locked"] = user_vip < r[8]
        else:
            item["locked"] = r[2] not in owned_keys

        items.append(item)

    # Türe göre grupla
    grouped = {}
    for item in items:
        if item["type"] not in grouped:
            grouped[item["type"]] = []
        grouped[item["type"]].append(item)

    return {"success": True, "items": grouped, "all_items": items}


@router.post("/items/{item_key}/unlock")
async def unlock_item(
    item_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔓 Öğe kilidi aç"""
    ensure_customization_tables(db)

    # Öğeyi kontrol et
    item = db.execute(text("""
        SELECT id, unlock_type, unlock_value FROM customization_items
        WHERE item_key = :key AND is_active = TRUE
    """), {"key": item_key}).fetchone()

    if not item:
        return JSONResponse(status_code=404, content={"success": False, "detail": "Öğe bulunamadı"})

    # Zaten sahip mi?
    existing = db.execute(text("""
        SELECT id FROM user_customization_items WHERE user_id = :uid AND item_key = :key
    """), {"uid": current_user.id, "key": item_key}).fetchone()

    if existing:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Bu öğeye zaten sahipsiniz"})

    # Kilit açma koşullarını kontrol et
    user_level = getattr(current_user, 'level', 1) or 1
    user_vip = getattr(current_user, 'vip_level', 0) or 0

    unlock_type, unlock_value = item[1], item[2]

    if unlock_type == "level" and user_level < unlock_value:
        return JSONResponse(status_code=400, content={
            "success": False,
            "detail": f"Bu öğe için seviye {unlock_value} gerekli"
        })
    elif unlock_type == "vip" and user_vip < unlock_value:
        return JSONResponse(status_code=400, content={
            "success": False,
            "detail": f"Bu öğe için VIP seviye {unlock_value} gerekli"
        })

    # Öğeyi ver
    db.execute(text("""
        INSERT INTO user_customization_items (user_id, item_key) VALUES (:uid, :key)
    """), {"uid": current_user.id, "key": item_key})
    db.commit()

    return {"success": True, "message": "Öğe kilidi açıldı"}
