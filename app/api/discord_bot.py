"""
🤖 AGTR Discord Bot API
Discord Bot Management, Webhooks, Server Status Notifications
"""
import json
import os
from datetime import datetime
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User, UserRole

router = APIRouter()

# ============================================================================
# CONFIGURATION
# ============================================================================

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DISCORD_API_BASE = "https://discord.com/api/v10"

# ============================================================================
# DATABASE TABLES
# ============================================================================

def ensure_discord_tables(db: Session):
    """Discord tablolarını oluştur"""
    try:
        # Discord sunucu bağlantıları
        db.execute(text("""CREATE TABLE IF NOT EXISTS discord_guilds (
            id INT AUTO_INCREMENT PRIMARY KEY,
            guild_id VARCHAR(50) NOT NULL UNIQUE,
            guild_name VARCHAR(255),
            owner_id VARCHAR(50),
            member_count INT,
            status_channel_id VARCHAR(50),
            notification_channel_id VARCHAR(50),
            log_channel_id VARCHAR(50),
            welcome_channel_id VARCHAR(50),
            role_verified_id VARCHAR(50),
            role_vip_id VARCHAR(50),
            settings JSON,
            is_active BOOLEAN DEFAULT TRUE,
            connected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_guild (guild_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Webhook kayıtları
        db.execute(text("""CREATE TABLE IF NOT EXISTS discord_webhooks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            webhook_url VARCHAR(500) NOT NULL,
            webhook_type ENUM('server_status', 'new_user', 'payment', 'forum', 'admin', 'custom') NOT NULL,
            guild_id VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE,
            last_used DATETIME,
            created_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_type (webhook_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Webhook logları
        db.execute(text("""CREATE TABLE IF NOT EXISTS discord_webhook_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            webhook_id INT NOT NULL,
            event_type VARCHAR(50),
            payload JSON,
            response_code INT,
            response_body TEXT,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_webhook (webhook_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Discord-AGTR kullanıcı eşleştirme
        db.execute(text("""CREATE TABLE IF NOT EXISTS discord_user_links (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            discord_id VARCHAR(50) NOT NULL,
            discord_username VARCHAR(100),
            discord_discriminator VARCHAR(10),
            discord_avatar VARCHAR(255),
            verification_code VARCHAR(20),
            is_verified BOOLEAN DEFAULT FALSE,
            linked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            verified_at DATETIME,
            UNIQUE KEY unique_user (user_id),
            UNIQUE KEY unique_discord (discord_id),
            INDEX idx_code (verification_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Bot komut logları
        db.execute(text("""CREATE TABLE IF NOT EXISTS discord_command_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            guild_id VARCHAR(50),
            channel_id VARCHAR(50),
            user_id VARCHAR(50),
            command VARCHAR(50),
            args TEXT,
            response TEXT,
            executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_guild (guild_id),
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        db.commit()
    except:
        db.rollback()


# ============================================================================
# WEBHOOK MANAGEMENT
# ============================================================================

@router.get("/webhooks")
async def list_webhooks(
    webhook_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Webhook listesi"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_discord_tables(db)
    
    q = "SELECT * FROM discord_webhooks WHERE 1=1"
    p = {}
    
    if webhook_type:
        q += " AND webhook_type = :type"
        p["type"] = webhook_type
    
    q += " ORDER BY created_at DESC"
    
    rows = db.execute(text(q), p).fetchall()
    webhooks = [{
        "id": r[0], "name": r[1], "webhook_type": r[3],
        "guild_id": r[4], "is_active": bool(r[5]),
        "last_used": r[6].isoformat() if r[6] else None
    } for r in rows]
    
    return {"success": True, "webhooks": webhooks}


@router.post("/webhooks")
async def create_webhook(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """➕ Webhook ekle"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_discord_tables(db)
    
    name = data.get("name", "")
    webhook_url = data.get("webhook_url", "")
    webhook_type = data.get("webhook_type", "custom")
    guild_id = data.get("guild_id")
    
    if not webhook_url.startswith("https://discord.com/api/webhooks/"):
        return JSONResponse(status_code=400, content={"success": False, "detail": "Geçersiz webhook URL"})
    
    db.execute(text("""
        INSERT INTO discord_webhooks (name, webhook_url, webhook_type, guild_id, created_by)
        VALUES (:name, :url, :type, :guild, :uid)
    """), {"name": name, "url": webhook_url, "type": webhook_type, "guild": guild_id, "uid": current_user.id})
    db.commit()
    
    return {"success": True, "message": "Webhook eklendi"}


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🗑️ Webhook sil"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    db.execute(text("DELETE FROM discord_webhooks WHERE id = :id"), {"id": webhook_id})
    db.commit()
    
    return {"success": True, "message": "Webhook silindi"}


@router.post("/webhooks/test/{webhook_id}")
async def test_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🧪 Webhook test et"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    webhook = db.execute(text(
        "SELECT webhook_url FROM discord_webhooks WHERE id = :id"
    ), {"id": webhook_id}).fetchone()
    
    if not webhook:
        raise HTTPException(404, "Webhook bulunamadı")
    
    result = await send_discord_webhook(webhook[0], {
        "content": "🧪 **AGTR Merkezi** - Webhook test mesajı!",
        "embeds": [{
            "title": "Test Başarılı",
            "description": "Bu webhook çalışıyor!",
            "color": 0xff6b00,
            "timestamp": datetime.utcnow().isoformat()
        }]
    })
    
    return {"success": result, "message": "Test mesajı gönderildi" if result else "Gönderim başarısız"}


# ============================================================================
# WEBHOOK SENDING
# ============================================================================

async def send_discord_webhook(webhook_url: str, payload: dict, db: Session = None, webhook_id: int = None) -> bool:
    """Discord webhook'a mesaj gönder"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(webhook_url, json=payload, timeout=10)
            
            # Log kaydet
            if db and webhook_id:
                db.execute(text("""
                    INSERT INTO discord_webhook_logs (webhook_id, event_type, payload, response_code)
                    VALUES (:wid, :event, :payload, :code)
                """), {
                    "wid": webhook_id, 
                    "event": payload.get("event_type", "unknown"),
                    "payload": json.dumps(payload),
                    "code": resp.status_code
                })
                db.execute(text(
                    "UPDATE discord_webhooks SET last_used = NOW() WHERE id = :id"
                ), {"id": webhook_id})
                db.commit()
            
            return resp.status_code in [200, 204]
    except Exception as e:
        print(f"Webhook error: {e}")
        return False


async def send_server_status_notification(db: Session, server_id: int, server_name: str, status: str, player_count: int = 0):
    """Sunucu durumu bildirimi gönder"""
    ensure_discord_tables(db)
    
    webhooks = db.execute(text("""
        SELECT id, webhook_url FROM discord_webhooks 
        WHERE webhook_type = 'server_status' AND is_active = TRUE
    """)).fetchall()
    
    color = 0x00ff00 if status == "online" else 0xff0000
    status_emoji = "🟢" if status == "online" else "🔴"
    
    embed = {
        "title": f"{status_emoji} Sunucu Durumu Değişti",
        "description": f"**{server_name}** sunucusu **{status.upper()}**",
        "color": color,
        "fields": [
            {"name": "Oyuncu", "value": str(player_count), "inline": True},
            {"name": "Durum", "value": status.capitalize(), "inline": True}
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "AGTR Merkezi"}
    }
    
    for webhook in webhooks:
        await send_discord_webhook(webhook[1], {"embeds": [embed]}, db, webhook[0])


async def send_new_user_notification(db: Session, username: str, email: str = None):
    """Yeni kullanıcı bildirimi"""
    ensure_discord_tables(db)
    
    webhooks = db.execute(text("""
        SELECT id, webhook_url FROM discord_webhooks 
        WHERE webhook_type = 'new_user' AND is_active = TRUE
    """)).fetchall()
    
    embed = {
        "title": "👋 Yeni Üye Kaydı",
        "description": f"**{username}** siteye kaydoldu!",
        "color": 0x3498db,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "AGTR Merkezi"}
    }
    
    for webhook in webhooks:
        await send_discord_webhook(webhook[1], {"embeds": [embed]}, db, webhook[0])


async def send_payment_notification(db: Session, username: str, amount: float, payment_type: str):
    """Ödeme bildirimi"""
    ensure_discord_tables(db)
    
    webhooks = db.execute(text("""
        SELECT id, webhook_url FROM discord_webhooks 
        WHERE webhook_type = 'payment' AND is_active = TRUE
    """)).fetchall()
    
    embed = {
        "title": "💰 Yeni Ödeme",
        "description": f"**{username}** ödeme yaptı!",
        "color": 0x2ecc71,
        "fields": [
            {"name": "Tutar", "value": f"{amount:.2f} TL", "inline": True},
            {"name": "Yöntem", "value": payment_type, "inline": True}
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "AGTR Merkezi"}
    }
    
    for webhook in webhooks:
        await send_discord_webhook(webhook[1], {"embeds": [embed]}, db, webhook[0])


# ============================================================================
# BOT COMMANDS API (For external bot)
# ============================================================================

@router.get("/bot/servers")
async def bot_get_servers(
    api_key: str,
    db: Session = Depends(get_db)
):
    """🤖 Bot: Sunucu listesi"""
    # API key doğrulama
    if api_key != os.getenv("DISCORD_BOT_API_KEY", ""):
        raise HTTPException(401, "Geçersiz API key")
    
    rows = db.execute(text("""
        SELECT id, name, ip_address, port, game_type, status, current_players, max_players, current_map
        FROM game_servers WHERE status != 'deleted'
    """)).fetchall()
    
    servers = [{
        "id": r[0], "name": r[1], "ip": r[2], "port": r[3],
        "game": r[4], "status": r[5], "players": r[6],
        "max_players": r[7], "map": r[8]
    } for r in rows]
    
    return {"success": True, "servers": servers}


@router.get("/bot/server/{server_id}")
async def bot_get_server(
    server_id: int,
    api_key: str,
    db: Session = Depends(get_db)
):
    """🤖 Bot: Sunucu detayı"""
    if api_key != os.getenv("DISCORD_BOT_API_KEY", ""):
        raise HTTPException(401, "Geçersiz API key")
    
    server = db.execute(text("""
        SELECT * FROM game_servers WHERE id = :id
    """), {"id": server_id}).fetchone()
    
    if not server:
        raise HTTPException(404, "Sunucu bulunamadı")
    
    return {
        "success": True,
        "server": {
            "id": server[0], "name": server[2], "ip": server[3], "port": server[4],
            "game": server[5], "status": server[10], "players": server[11],
            "max_players": server[12], "map": server[13]
        }
    }


@router.get("/bot/stats")
async def bot_get_stats(
    api_key: str,
    db: Session = Depends(get_db)
):
    """🤖 Bot: Site istatistikleri"""
    if api_key != os.getenv("DISCORD_BOT_API_KEY", ""):
        raise HTTPException(401, "Geçersiz API key")
    
    stats = {}
    stats["total_users"] = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
    stats["total_servers"] = db.execute(text("SELECT COUNT(*) FROM game_servers")).fetchone()[0]
    stats["online_servers"] = db.execute(text("SELECT COUNT(*) FROM game_servers WHERE status = 'online'")).fetchone()[0]
    stats["total_players"] = db.execute(text("SELECT COALESCE(SUM(current_players), 0) FROM game_servers WHERE status = 'online'")).fetchone()[0]
    
    return {"success": True, "stats": stats}


@router.post("/bot/verify")
async def bot_verify_user(
    data: dict,
    api_key: str,
    db: Session = Depends(get_db)
):
    """🤖 Bot: Kullanıcı doğrula"""
    if api_key != os.getenv("DISCORD_BOT_API_KEY", ""):
        raise HTTPException(401, "Geçersiz API key")
    
    ensure_discord_tables(db)
    
    code = data.get("code", "").upper()
    discord_id = data.get("discord_id")
    discord_username = data.get("discord_username")
    
    # Kodu bul
    link = db.execute(text("""
        SELECT user_id FROM discord_user_links 
        WHERE verification_code = :code AND is_verified = FALSE
    """), {"code": code}).fetchone()
    
    if not link:
        return {"success": False, "message": "Geçersiz veya kullanılmış kod"}
    
    # Doğrula
    db.execute(text("""
        UPDATE discord_user_links SET 
            discord_id = :did, discord_username = :dun, 
            is_verified = TRUE, verified_at = NOW()
        WHERE verification_code = :code
    """), {"did": discord_id, "dun": discord_username, "code": code})
    db.commit()
    
    return {"success": True, "message": "Hesap doğrulandı!"}


@router.post("/bot/log-command")
async def bot_log_command(
    data: dict,
    api_key: str,
    db: Session = Depends(get_db)
):
    """🤖 Bot: Komut logla"""
    if api_key != os.getenv("DISCORD_BOT_API_KEY", ""):
        raise HTTPException(401, "Geçersiz API key")
    
    ensure_discord_tables(db)
    
    db.execute(text("""
        INSERT INTO discord_command_logs (guild_id, channel_id, user_id, command, args, response)
        VALUES (:gid, :cid, :uid, :cmd, :args, :resp)
    """), {
        "gid": data.get("guild_id"),
        "cid": data.get("channel_id"),
        "uid": data.get("user_id"),
        "cmd": data.get("command"),
        "args": data.get("args"),
        "resp": data.get("response")
    })
    db.commit()
    
    return {"success": True}


# ============================================================================
# USER DISCORD LINK
# ============================================================================

@router.post("/link/generate")
async def generate_link_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔗 Discord bağlantı kodu oluştur"""
    ensure_discord_tables(db)
    
    import random
    import string
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Mevcut kaydı güncelle veya yeni oluştur
    db.execute(text("""
        INSERT INTO discord_user_links (user_id, verification_code)
        VALUES (:uid, :code)
        ON DUPLICATE KEY UPDATE verification_code = :code, is_verified = FALSE
    """), {"uid": current_user.id, "code": code})
    db.commit()
    
    return {
        "success": True,
        "code": code,
        "message": f"Discord'da !dogrula {code} yazın"
    }


@router.get("/link/status")
async def get_link_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Discord bağlantı durumu"""
    ensure_discord_tables(db)
    
    link = db.execute(text("""
        SELECT discord_id, discord_username, is_verified, verified_at
        FROM discord_user_links WHERE user_id = :uid
    """), {"uid": current_user.id}).fetchone()
    
    if not link:
        return {"success": True, "linked": False}
    
    return {
        "success": True,
        "linked": bool(link[2]),
        "discord_id": link[0],
        "discord_username": link[1],
        "verified_at": link[3].isoformat() if link[3] else None
    }


# ============================================================================
# GUILD SETTINGS (Admin)
# ============================================================================

@router.get("/guilds")
async def list_guilds(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Bağlı Discord sunucuları"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_discord_tables(db)
    
    rows = db.execute(text("SELECT * FROM discord_guilds WHERE is_active = TRUE")).fetchall()
    guilds = [{
        "id": r[0], "guild_id": r[1], "guild_name": r[2],
        "member_count": r[4], "status_channel": r[5],
        "notification_channel": r[6]
    } for r in rows]
    
    return {"success": True, "guilds": guilds}


@router.put("/guilds/{guild_id}/settings")
async def update_guild_settings(
    guild_id: str,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """⚙️ Discord sunucu ayarları"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_discord_tables(db)
    
    db.execute(text("""
        UPDATE discord_guilds SET 
            status_channel_id = :sc, notification_channel_id = :nc,
            log_channel_id = :lc, welcome_channel_id = :wc,
            settings = :settings
        WHERE guild_id = :gid
    """), {
        "gid": guild_id,
        "sc": data.get("status_channel"),
        "nc": data.get("notification_channel"),
        "lc": data.get("log_channel"),
        "wc": data.get("welcome_channel"),
        "settings": json.dumps(data.get("settings", {}))
    })
    db.commit()
    
    return {"success": True, "message": "Ayarlar güncellendi"}
