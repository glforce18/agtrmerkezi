"""
🔌 AGTR Plugin Market API
Plugin/Mod Store, Auto-Install, Reviews, Updates
"""
import json
import os
import shutil
import zipfile
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User, UserRole

logger = get_logger(__name__)

router = APIRouter()

# ============================================================================
# CONFIGURATION
# ============================================================================

PLUGINS_PATH = "/var/www/agtrmerkezi/static/plugins"
SERVERS_PATH = settings.HLDS_PATH

# ============================================================================
# DATABASE TABLES
# ============================================================================

def ensure_plugin_tables(db: Session):
    """Plugin tablolarını oluştur"""
    try:
        # Plugin kategorileri
        db.execute(text("""CREATE TABLE IF NOT EXISTS plugin_categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(100) UNIQUE,
            description TEXT,
            icon VARCHAR(50),
            parent_id INT,
            sort_order INT DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            INDEX idx_parent (parent_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Pluginler
        db.execute(text("""CREATE TABLE IF NOT EXISTS plugins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(255) UNIQUE,
            description TEXT,
            long_description TEXT,
            version VARCHAR(50) NOT NULL,
            game_type VARCHAR(50) NOT NULL,
            category_id INT,
            author_id INT,
            author_name VARCHAR(100),
            file_path VARCHAR(500),
            file_size INT,
            file_hash VARCHAR(64),
            icon_url VARCHAR(500),
            banner_url VARCHAR(500),
            screenshots JSON,
            tags JSON,
            dependencies JSON,
            install_instructions TEXT,
            changelog TEXT,
            source_url VARCHAR(500),
            documentation_url VARCHAR(500),
            price DECIMAL(10,2) DEFAULT 0,
            is_free BOOLEAN DEFAULT TRUE,
            is_official BOOLEAN DEFAULT FALSE,
            is_featured BOOLEAN DEFAULT FALSE,
            status ENUM('pending', 'approved', 'rejected', 'archived') DEFAULT 'pending',
            download_count INT DEFAULT 0,
            rating_avg DECIMAL(3,2) DEFAULT 0,
            rating_count INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_game (game_type),
            INDEX idx_category (category_id),
            INDEX idx_status (status),
            INDEX idx_featured (is_featured)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Plugin versiyonları
        db.execute(text("""CREATE TABLE IF NOT EXISTS plugin_versions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plugin_id INT NOT NULL,
            version VARCHAR(50) NOT NULL,
            file_path VARCHAR(500),
            file_size INT,
            file_hash VARCHAR(64),
            changelog TEXT,
            min_game_version VARCHAR(50),
            is_stable BOOLEAN DEFAULT TRUE,
            download_count INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_plugin (plugin_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Plugin indirmeleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS plugin_downloads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plugin_id INT NOT NULL,
            version_id INT,
            user_id INT,
            server_id INT,
            ip_address VARCHAR(45),
            downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_plugin (plugin_id),
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Plugin değerlendirmeleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS plugin_reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plugin_id INT NOT NULL,
            user_id INT NOT NULL,
            rating INT NOT NULL,
            title VARCHAR(255),
            content TEXT,
            is_verified_purchase BOOLEAN DEFAULT FALSE,
            helpful_count INT DEFAULT 0,
            status ENUM('pending', 'approved', 'rejected') DEFAULT 'approved',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_review (plugin_id, user_id),
            INDEX idx_plugin (plugin_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Sunucuya yüklü pluginler
        db.execute(text("""CREATE TABLE IF NOT EXISTS server_plugins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            server_id INT NOT NULL,
            plugin_id INT NOT NULL,
            version_id INT,
            installed_version VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE,
            auto_update BOOLEAN DEFAULT TRUE,
            installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            UNIQUE KEY unique_install (server_id, plugin_id),
            INDEX idx_server (server_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Varsayılan kategoriler
        db.execute(text("""INSERT IGNORE INTO plugin_categories (id, name, slug, icon, sort_order) VALUES
            (1, 'Admin Araçları', 'admin-tools', '🔧', 1),
            (2, 'Anti-Cheat', 'anti-cheat', '🛡️', 2),
            (3, 'Oyun Modları', 'game-mods', '🎮', 3),
            (4, 'Haritalar', 'maps', '🗺️', 4),
            (5, 'Sesler', 'sounds', '🔊', 5),
            (6, 'Modeller', 'models', '👤', 6),
            (7, 'İstatistik', 'stats', '📊', 7),
            (8, 'Eğlence', 'fun', '🎉', 8),
            (9, 'Diğer', 'other', '📦', 99)
        """))
        
        db.commit()
    except Exception:
        db.rollback()


# ============================================================================
# PLUGIN LISTING
# ============================================================================

@router.get("/")
async def list_plugins(
    game_type: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    featured: bool = None,
    free_only: bool = None,
    sort: str = "popular",
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """📋 Plugin listesi"""
    ensure_plugin_tables(db)
    
    q = "SELECT p.*, c.name as category_name FROM plugins p LEFT JOIN plugin_categories c ON p.category_id = c.id WHERE p.status = 'approved'"
    p = {"offset": (page - 1) * limit, "lim": limit}
    
    if game_type:
        q += " AND p.game_type = :game"
        p["game"] = game_type
    
    if category:
        q += " AND c.slug = :cat"
        p["cat"] = category
    
    if search:
        q += " AND (p.name LIKE :search OR p.description LIKE :search)"
        p["search"] = f"%{search}%"
    
    if featured:
        q += " AND p.is_featured = TRUE"
    
    if free_only:
        q += " AND p.is_free = TRUE"
    
    # Sıralama
    sort_map = {
        "popular": "p.download_count DESC",
        "rating": "p.rating_avg DESC",
        "newest": "p.created_at DESC",
        "updated": "p.updated_at DESC",
        "name": "p.name ASC"
    }
    q += f" ORDER BY {sort_map.get(sort, 'p.download_count DESC')} LIMIT :lim OFFSET :offset"
    
    rows = db.execute(text(q), p).fetchall()
    
    plugins = [{
        "id": r[0], "name": r[1], "slug": r[2], "description": r[3],
        "version": r[5], "game_type": r[6], "category_name": r[33],
        "author_name": r[10], "icon_url": r[13], "price": float(r[22]) if r[22] else 0,
        "is_free": bool(r[23]), "is_official": bool(r[24]), "is_featured": bool(r[25]),
        "download_count": r[27], "rating_avg": float(r[28]) if r[28] else 0,
        "rating_count": r[29]
    } for r in rows]
    
    # Toplam sayı
    count_q = "SELECT COUNT(*) FROM plugins p LEFT JOIN plugin_categories c ON p.category_id = c.id WHERE p.status = 'approved'"
    # ... aynı filtreler
    
    return {
        "success": True,
        "plugins": plugins,
        "page": page,
        "limit": limit
    }


@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    """📋 Kategoriler"""
    ensure_plugin_tables(db)
    
    rows = db.execute(text("""
        SELECT c.*, COUNT(p.id) as plugin_count FROM plugin_categories c
        LEFT JOIN plugins p ON c.id = p.category_id AND p.status = 'approved'
        WHERE c.is_active = TRUE
        GROUP BY c.id ORDER BY c.sort_order
    """)).fetchall()
    
    categories = [{
        "id": r[0], "name": r[1], "slug": r[2], "description": r[3],
        "icon": r[4], "plugin_count": r[8]
    } for r in rows]
    
    return {"success": True, "categories": categories}


@router.get("/{plugin_id}")
async def get_plugin(plugin_id: int, db: Session = Depends(get_db)):
    """🔍 Plugin detayı"""
    ensure_plugin_tables(db)
    
    plugin = db.execute(text("""
        SELECT p.*, c.name as category_name, u.username as author_username
        FROM plugins p
        LEFT JOIN plugin_categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.id = :id
    """), {"id": plugin_id}).fetchone()
    
    if not plugin:
        raise HTTPException(404, "Plugin bulunamadı")
    
    # Versiyonlar
    versions = db.execute(text("""
        SELECT * FROM plugin_versions WHERE plugin_id = :pid ORDER BY created_at DESC LIMIT 10
    """), {"pid": plugin_id}).fetchall()
    
    # Son yorumlar
    reviews = db.execute(text("""
        SELECT r.*, u.username FROM plugin_reviews r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.plugin_id = :pid AND r.status = 'approved'
        ORDER BY r.created_at DESC LIMIT 10
    """), {"pid": plugin_id}).fetchall()
    
    return {
        "success": True,
        "plugin": {
            "id": plugin[0], "name": plugin[1], "slug": plugin[2],
            "description": plugin[3], "long_description": plugin[4],
            "version": plugin[5], "game_type": plugin[6],
            "category_name": plugin[33], "author_name": plugin[10] or plugin[34],
            "icon_url": plugin[13], "banner_url": plugin[14],
            "screenshots": json.loads(plugin[15]) if plugin[15] else [],
            "tags": json.loads(plugin[16]) if plugin[16] else [],
            "install_instructions": plugin[19], "changelog": plugin[20],
            "source_url": plugin[21], "documentation_url": plugin[22],
            "price": float(plugin[23]) if plugin[23] else 0, "is_free": bool(plugin[24]),
            "is_official": bool(plugin[25]), "download_count": plugin[28],
            "rating_avg": float(plugin[29]) if plugin[29] else 0, "rating_count": plugin[30]
        },
        "versions": [{
            "id": v[0], "version": v[2], "changelog": v[5],
            "is_stable": bool(v[7]), "download_count": v[8],
            "created_at": v[9].isoformat() if v[9] else None
        } for v in versions],
        "reviews": [{
            "id": r[0], "rating": r[3], "title": r[4], "content": r[5],
            "username": r[10], "helpful_count": r[7],
            "created_at": r[9].isoformat() if r[9] else None
        } for r in reviews]
    }


# ============================================================================
# DOWNLOAD & INSTALL
# ============================================================================

@router.get("/{plugin_id}/download")
async def download_plugin(
    plugin_id: int,
    version_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📥 Plugin indir"""
    ensure_plugin_tables(db)
    
    if version_id:
        version = db.execute(text("""
            SELECT v.*, p.is_free, p.price FROM plugin_versions v
            JOIN plugins p ON v.plugin_id = p.id
            WHERE v.id = :vid
        """), {"vid": version_id}).fetchone()
    else:
        version = db.execute(text("""
            SELECT v.*, p.is_free, p.price FROM plugin_versions v
            JOIN plugins p ON v.plugin_id = p.id
            WHERE v.plugin_id = :pid ORDER BY v.created_at DESC LIMIT 1
        """), {"pid": plugin_id}).fetchone()
    
    if not version:
        raise HTTPException(404, "Plugin bulunamadı")
    
    # Ücretli plugin kontrolü
    if not version[10]:  # is_free
        # Satın alma kontrolü yapılabilir
        pass
    
    # İndirme kaydı
    db.execute(text("""
        INSERT INTO plugin_downloads (plugin_id, version_id, user_id)
        VALUES (:pid, :vid, :uid)
    """), {"pid": plugin_id, "vid": version[0], "uid": current_user.id})
    
    # İndirme sayısını artır
    db.execute(text("UPDATE plugins SET download_count = download_count + 1 WHERE id = :id"), {"id": plugin_id})
    db.execute(text("UPDATE plugin_versions SET download_count = download_count + 1 WHERE id = :id"), {"id": version[0]})
    db.commit()
    
    file_path = version[3]
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(404, "Dosya bulunamadı")
    
    return FileResponse(file_path, filename=os.path.basename(file_path))


@router.post("/{plugin_id}/install/{server_id}")
async def install_plugin_to_server(
    plugin_id: int,
    server_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔧 Plugin'i sunucuya yükle"""
    ensure_plugin_tables(db)
    
    # Sunucu kontrolü
    server = db.execute(text("""
        SELECT id, user_id, server_path, game_type FROM game_servers WHERE id = :id
    """), {"id": server_id}).fetchone()
    
    if not server:
        raise HTTPException(404, "Sunucu bulunamadı")
    
    if server[1] != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    # Plugin kontrolü
    plugin = db.execute(text("""
        SELECT p.*, v.file_path, v.version FROM plugins p
        JOIN plugin_versions v ON p.id = v.plugin_id
        WHERE p.id = :pid AND p.game_type = :game
        ORDER BY v.created_at DESC LIMIT 1
    """), {"pid": plugin_id, "game": server[3]}).fetchone()
    
    if not plugin:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Bu plugin bu oyun için uygun değil"})
    
    # Kurulum kaydı
    db.execute(text("""
        INSERT INTO server_plugins (server_id, plugin_id, installed_version)
        VALUES (:sid, :pid, :ver)
        ON DUPLICATE KEY UPDATE installed_version = :ver, updated_at = NOW()
    """), {"sid": server_id, "pid": plugin_id, "ver": plugin[33]})
    db.commit()
    
    # Background'da yükle
    background_tasks.add_task(install_plugin_files, server[2], plugin[32], plugin[1])
    
    return {"success": True, "message": "Plugin yükleniyor..."}


async def install_plugin_files(server_path: str, plugin_file: str, plugin_name: str):
    """Plugin dosyalarını yükle"""
    try:
        if not plugin_file or not os.path.exists(plugin_file):
            return
        
        # Hedef dizin (AMX Mod X için)
        plugins_dir = os.path.join(server_path, "cstrike", "addons", "amxmodx", "plugins")
        os.makedirs(plugins_dir, exist_ok=True)
        
        if plugin_file.endswith(".zip"):
            # ZIP dosyası
            with zipfile.ZipFile(plugin_file, 'r') as zip_ref:
                zip_ref.extractall(plugins_dir)
        else:
            # Tek dosya
            shutil.copy(plugin_file, plugins_dir)
        
        logger.info(f"Plugin installed: {plugin_name} -> {server_path}")
    except Exception as e:
        logger.error(f"Plugin install error: {e}")


@router.delete("/{plugin_id}/uninstall/{server_id}")
async def uninstall_plugin(
    plugin_id: int,
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🗑️ Plugin'i kaldır"""
    # Yetki kontrolü
    server = db.execute(text("SELECT user_id FROM game_servers WHERE id = :id"), {"id": server_id}).fetchone()
    
    if not server or (server[0] != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]):
        raise HTTPException(403, "Yetkiniz yok")
    
    db.execute(text("""
        DELETE FROM server_plugins WHERE server_id = :sid AND plugin_id = :pid
    """), {"sid": server_id, "pid": plugin_id})
    db.commit()
    
    return {"success": True, "message": "Plugin kaldırıldı"}


@router.get("/server/{server_id}/installed")
async def get_server_plugins(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Sunucudaki pluginler"""
    ensure_plugin_tables(db)
    
    rows = db.execute(text("""
        SELECT sp.*, p.name, p.version as latest_version, p.icon_url
        FROM server_plugins sp
        JOIN plugins p ON sp.plugin_id = p.id
        WHERE sp.server_id = :sid
        ORDER BY sp.installed_at DESC
    """), {"sid": server_id}).fetchall()
    
    plugins = [{
        "plugin_id": r[2], "name": r[8], "installed_version": r[4],
        "latest_version": r[9], "icon_url": r[10],
        "is_active": bool(r[5]), "auto_update": bool(r[6]),
        "has_update": r[4] != r[9],
        "installed_at": r[7].isoformat() if r[7] else None
    } for r in rows]
    
    return {"success": True, "plugins": plugins}


# ============================================================================
# REVIEWS
# ============================================================================

@router.post("/{plugin_id}/review")
async def add_review(
    plugin_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """⭐ Değerlendirme ekle"""
    ensure_plugin_tables(db)
    
    rating = data.get("rating", 5)
    title = data.get("title", "")
    content = data.get("content", "")
    
    if rating < 1 or rating > 5:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Puan 1-5 arası olmalı"})
    
    # İndirmiş mi?
    download = db.execute(text("""
        SELECT id FROM plugin_downloads WHERE plugin_id = :pid AND user_id = :uid
    """), {"pid": plugin_id, "uid": current_user.id}).fetchone()
    
    try:
        db.execute(text("""
            INSERT INTO plugin_reviews (plugin_id, user_id, rating, title, content, is_verified_purchase)
            VALUES (:pid, :uid, :rating, :title, :content, :verified)
        """), {
            "pid": plugin_id, "uid": current_user.id, "rating": rating,
            "title": title, "content": content, "verified": download is not None
        })
        
        # Ortalama güncelle
        avg = db.execute(text("""
            SELECT AVG(rating), COUNT(*) FROM plugin_reviews WHERE plugin_id = :pid AND status = 'approved'
        """), {"pid": plugin_id}).fetchone()
        
        db.execute(text("""
            UPDATE plugins SET rating_avg = :avg, rating_count = :count WHERE id = :id
        """), {"avg": avg[0], "count": avg[1], "id": plugin_id})
        
        db.commit()
        return {"success": True, "message": "Değerlendirme eklendi"}
    except Exception:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Zaten değerlendirme yapmışsınız"})


# ============================================================================
# PLUGIN SUBMISSION (Developer)
# ============================================================================

@router.post("/submit")
async def submit_plugin(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📤 Plugin gönder"""
    ensure_plugin_tables(db)
    
    name = data.get("name", "").strip()
    slug = data.get("slug", name.lower().replace(" ", "-"))
    
    r = db.execute(text("""
        INSERT INTO plugins (name, slug, description, long_description, version, game_type,
            category_id, author_id, author_name, install_instructions, source_url, status)
        VALUES (:name, :slug, :desc, :long, :ver, :game, :cat, :uid, :author, :inst, :src, 'pending')
    """), {
        "name": name, "slug": slug, "desc": data.get("description"),
        "long": data.get("long_description"), "ver": data.get("version", "1.0.0"),
        "game": data.get("game_type", "cs16"), "cat": data.get("category_id"),
        "uid": current_user.id, "author": current_user.username,
        "inst": data.get("install_instructions"), "src": data.get("source_url")
    })
    db.commit()
    
    return {"success": True, "plugin_id": r.lastrowid, "message": "Plugin inceleme için gönderildi"}


# ============================================================================
# ADMIN
# ============================================================================

@router.get("/admin/pending")
async def get_pending_plugins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Onay bekleyen pluginler"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_plugin_tables(db)
    
    rows = db.execute(text("""
        SELECT p.*, u.username FROM plugins p
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.status = 'pending'
        ORDER BY p.created_at
    """)).fetchall()
    
    plugins = [{
        "id": r[0], "name": r[1], "version": r[5], "game_type": r[6],
        "author_name": r[33], "created_at": r[31].isoformat() if r[31] else None
    } for r in rows]
    
    return {"success": True, "plugins": plugins}


@router.post("/admin/{plugin_id}/approve")
async def approve_plugin(
    plugin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ Plugin onayla"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    db.execute(text("UPDATE plugins SET status = 'approved' WHERE id = :id"), {"id": plugin_id})
    db.commit()
    
    return {"success": True, "message": "Plugin onaylandı"}


@router.post("/admin/{plugin_id}/reject")
async def reject_plugin(
    plugin_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """❌ Plugin reddet"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    db.execute(text("UPDATE plugins SET status = 'rejected' WHERE id = :id"), {"id": plugin_id})
    db.commit()
    
    return {"success": True, "message": "Plugin reddedildi"}
