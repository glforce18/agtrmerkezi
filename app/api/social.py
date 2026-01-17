"""
🎮 AGTR Social & Community API
Discord OAuth, Steam OAuth, Clan/Team System, Achievement System
"""
import hashlib
import json
import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User

router = APIRouter()

# ============================================================================
# CONFIGURATION
# ============================================================================

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "https://agtrmerkezi.com/api/social/discord/callback")

STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
STEAM_REALM = os.getenv("STEAM_REALM", "https://agtrmerkezi.com")

# ============================================================================
# DATABASE TABLES
# ============================================================================

def ensure_social_tables(db: Session):
    """Sosyal tabloları oluştur"""
    try:
        # Sosyal hesap bağlantıları
        db.execute(text("""CREATE TABLE IF NOT EXISTS social_connections (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            provider VARCHAR(50) NOT NULL,
            provider_id VARCHAR(255) NOT NULL,
            provider_username VARCHAR(255),
            provider_email VARCHAR(255),
            provider_avatar VARCHAR(500),
            access_token TEXT,
            refresh_token TEXT,
            token_expires_at DATETIME,
            raw_data JSON,
            connected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_provider (user_id, provider),
            INDEX idx_provider_id (provider, provider_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Klanlar/Takımlar
        db.execute(text("""CREATE TABLE IF NOT EXISTS clans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            tag VARCHAR(10) NOT NULL,
            description TEXT,
            logo_url VARCHAR(500),
            banner_url VARCHAR(500),
            color VARCHAR(20) DEFAULT '#ff6b00',
            owner_id INT NOT NULL,
            is_public BOOLEAN DEFAULT TRUE,
            is_recruiting BOOLEAN DEFAULT TRUE,
            max_members INT DEFAULT 50,
            member_count INT DEFAULT 1,
            wins INT DEFAULT 0,
            losses INT DEFAULT 0,
            points INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_owner (owner_id),
            INDEX idx_tag (tag)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Klan üyeleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS clan_members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            clan_id INT NOT NULL,
            user_id INT NOT NULL,
            role ENUM('owner', 'admin', 'member') DEFAULT 'member',
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_member (clan_id, user_id),
            INDEX idx_clan (clan_id),
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Klan başvuruları
        db.execute(text("""CREATE TABLE IF NOT EXISTS clan_applications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            clan_id INT NOT NULL,
            user_id INT NOT NULL,
            message TEXT,
            status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
            reviewed_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            reviewed_at DATETIME,
            INDEX idx_clan (clan_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Başarımlar
        db.execute(text("""CREATE TABLE IF NOT EXISTS achievements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            icon VARCHAR(50) DEFAULT '🏆',
            points INT DEFAULT 10,
            category VARCHAR(50),
            requirement_type VARCHAR(50),
            requirement_value INT,
            is_secret BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Kullanıcı başarımları
        db.execute(text("""CREATE TABLE IF NOT EXISTS user_achievements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            achievement_id INT NOT NULL,
            unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_achievement (user_id, achievement_id),
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Arkadaşlık
        db.execute(text("""CREATE TABLE IF NOT EXISTS friendships (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            friend_id INT NOT NULL,
            status ENUM('pending', 'accepted', 'blocked') DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            accepted_at DATETIME,
            UNIQUE KEY unique_friendship (user_id, friend_id),
            INDEX idx_user (user_id),
            INDEX idx_friend (friend_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Insert default achievements
        db.execute(text("""INSERT IGNORE INTO achievements (code, name, description, icon, points, category) VALUES
            ('first_login', 'İlk Adım', 'Siteye ilk giriş', '👋', 10, 'general'),
            ('first_server', 'Sunucu Sahibi', 'İlk sunucunu kirala', '🖥️', 50, 'server'),
            ('forum_starter', 'Forum Başlatıcı', 'İlk konu aç', '📝', 20, 'forum'),
            ('helper', 'Yardımsever', '10 konuya cevap ver', '🤝', 30, 'forum'),
            ('veteran', 'Veteran', '1 yıllık üye', '⭐', 100, 'general'),
            ('clan_founder', 'Klan Kurucusu', 'Bir klan kur', '🏰', 50, 'social'),
            ('big_spender', 'Büyük Harcamacı', '1000 TL harca', '💰', 100, 'payment'),
            ('loyal_customer', 'Sadık Müşteri', '6 ay üst üste abone', '💎', 150, 'payment'),
            ('popular', 'Popüler', '100 arkadaş edin', '👥', 75, 'social'),
            ('pro_player', 'Pro Oyuncu', '1000 saat oyna', '🎮', 200, 'gaming')
        """))
        
        db.commit()
    except:
        db.rollback()


# ============================================================================
# DISCORD OAUTH
# ============================================================================

@router.get("/discord/login")
async def discord_login(request: Request):
    """🔵 Discord ile giriş başlat"""
    if not DISCORD_CLIENT_ID:
        raise HTTPException(500, "Discord yapılandırılmamış")
    
    state = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    
    # State'i session'a kaydet (production'da Redis kullan)
    
    url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify%20email%20guilds"
        f"&state={state}"
    )
    
    return RedirectResponse(url)


@router.get("/discord/callback")
async def discord_callback(
    code: str,
    state: str = None,
    db: Session = Depends(get_db)
):
    """📥 Discord callback"""
    if not DISCORD_CLIENT_ID or not DISCORD_CLIENT_SECRET:
        raise HTTPException(500, "Discord yapılandırılmamış")
    
    ensure_social_tables(db)
    
    # Token al
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": DISCORD_CLIENT_ID,
                "client_secret": DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": DISCORD_REDIRECT_URI
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if token_resp.status_code != 200:
            raise HTTPException(400, "Discord token alınamadı")
        
        tokens = token_resp.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in", 604800)
        
        # Kullanıcı bilgisi al
        user_resp = await client.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_resp.status_code != 200:
            raise HTTPException(400, "Discord kullanıcı bilgisi alınamadı")
        
        discord_user = user_resp.json()
    
    discord_id = discord_user.get("id")
    username = discord_user.get("username")
    email = discord_user.get("email")
    avatar = discord_user.get("avatar")
    avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar}.png" if avatar else None
    
    # Mevcut bağlantı var mı?
    existing = db.execute(text("""
        SELECT user_id FROM social_connections 
        WHERE provider = 'discord' AND provider_id = :pid
    """), {"pid": discord_id}).fetchone()
    
    if existing:
        # Güncelle
        db.execute(text("""
            UPDATE social_connections SET 
                provider_username = :un, provider_email = :email, provider_avatar = :avatar,
                access_token = :at, refresh_token = :rt, 
                token_expires_at = DATE_ADD(NOW(), INTERVAL :exp SECOND),
                raw_data = :raw
            WHERE provider = 'discord' AND provider_id = :pid
        """), {
            "un": username, "email": email, "avatar": avatar_url,
            "at": access_token, "rt": refresh_token, "exp": expires_in,
            "raw": json.dumps(discord_user), "pid": discord_id
        })
        db.commit()
        
        # Login işlemi - JWT token oluştur
        return RedirectResponse(f"/auth/social-complete?provider=discord&user_id={existing[0]}")
    
    # Yeni kullanıcı veya bağlantı
    return RedirectResponse(f"/auth/social-register?provider=discord&discord_id={discord_id}&username={username}&email={email or ''}")


@router.post("/discord/connect")
async def connect_discord(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔗 Discord hesabını bağla"""
    discord_id = data.get("discord_id")
    username = data.get("username")
    access_token = data.get("access_token")
    
    ensure_social_tables(db)
    
    # Zaten bağlı mı?
    existing = db.execute(text("""
        SELECT id FROM social_connections 
        WHERE provider = 'discord' AND provider_id = :pid
    """), {"pid": discord_id}).fetchone()
    
    if existing:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Bu Discord hesabı başka bir kullanıcıya bağlı"})
    
    db.execute(text("""
        INSERT INTO social_connections (user_id, provider, provider_id, provider_username, access_token)
        VALUES (:uid, 'discord', :pid, :un, :at)
        ON DUPLICATE KEY UPDATE provider_username = :un, access_token = :at, updated_at = NOW()
    """), {"uid": current_user.id, "pid": discord_id, "un": username, "at": access_token})
    db.commit()
    
    return {"success": True, "message": "Discord hesabı bağlandı"}


# ============================================================================
# STEAM OAUTH
# ============================================================================

@router.get("/steam/login")
async def steam_login():
    """🎮 Steam ile giriş başlat"""
    if not STEAM_API_KEY:
        raise HTTPException(500, "Steam yapılandırılmamış")
    
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": f"{STEAM_REALM}/api/social/steam/callback",
        "openid.realm": STEAM_REALM,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select"
    }
    
    url = "https://steamcommunity.com/openid/login?" + "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url)


@router.get("/steam/callback")
async def steam_callback(request: Request, db: Session = Depends(get_db)):
    """📥 Steam callback"""
    params = dict(request.query_params)
    
    # Steam ID çıkar
    claimed_id = params.get("openid.claimed_id", "")
    steam_id = claimed_id.split("/")[-1] if claimed_id else None
    
    if not steam_id:
        raise HTTPException(400, "Steam ID alınamadı")
    
    ensure_social_tables(db)
    
    # Steam profil bilgisi al
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/",
            params={"key": STEAM_API_KEY, "steamids": steam_id}
        )
        
        if resp.status_code != 200:
            raise HTTPException(400, "Steam profili alınamadı")
        
        data = resp.json()
        players = data.get("response", {}).get("players", [])
        
        if not players:
            raise HTTPException(400, "Steam oyuncu bulunamadı")
        
        steam_user = players[0]
    
    username = steam_user.get("personaname")
    avatar = steam_user.get("avatarfull")
    
    # Mevcut bağlantı var mı?
    existing = db.execute(text("""
        SELECT user_id FROM social_connections 
        WHERE provider = 'steam' AND provider_id = :pid
    """), {"pid": steam_id}).fetchone()
    
    if existing:
        db.execute(text("""
            UPDATE social_connections SET 
                provider_username = :un, provider_avatar = :avatar, raw_data = :raw
            WHERE provider = 'steam' AND provider_id = :pid
        """), {"un": username, "avatar": avatar, "raw": json.dumps(steam_user), "pid": steam_id})
        db.commit()
        
        return RedirectResponse(f"/auth/social-complete?provider=steam&user_id={existing[0]}")
    
    return RedirectResponse(f"/auth/social-register?provider=steam&steam_id={steam_id}&username={username}")


# ============================================================================
# SOCIAL CONNECTIONS
# ============================================================================

@router.get("/connections")
async def get_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Bağlı hesaplar"""
    ensure_social_tables(db)
    
    rows = db.execute(text("""
        SELECT provider, provider_username, provider_avatar, connected_at
        FROM social_connections WHERE user_id = :uid
    """), {"uid": current_user.id}).fetchall()
    
    connections = [{
        "provider": r[0], "username": r[1], "avatar": r[2],
        "connected_at": r[3].isoformat() if r[3] else None
    } for r in rows]
    
    return {"success": True, "connections": connections}


@router.delete("/connections/{provider}")
async def disconnect_provider(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔗 Hesap bağlantısını kaldır"""
    db.execute(text("""
        DELETE FROM social_connections WHERE user_id = :uid AND provider = :p
    """), {"uid": current_user.id, "p": provider})
    db.commit()
    
    return {"success": True, "message": f"{provider} bağlantısı kaldırıldı"}


# ============================================================================
# CLAN SYSTEM
# ============================================================================

@router.get("/clans")
async def list_clans(
    search: Optional[str] = None,
    recruiting: bool = None,
    db: Session = Depends(get_db)
):
    """📋 Klan listesi"""
    ensure_social_tables(db)
    
    q = "SELECT * FROM clans WHERE is_public = TRUE"
    p = {}
    
    if search:
        q += " AND (name LIKE :s OR tag LIKE :s)"
        p["s"] = f"%{search}%"
    
    if recruiting is not None:
        q += " AND is_recruiting = :r"
        p["r"] = recruiting
    
    q += " ORDER BY points DESC, member_count DESC LIMIT 50"
    
    rows = db.execute(text(q), p).fetchall()
    clans = [{
        "id": r[0], "name": r[1], "tag": r[2], "description": r[3],
        "logo_url": r[4], "color": r[6], "is_recruiting": bool(r[9]),
        "member_count": r[11], "wins": r[12], "points": r[14]
    } for r in rows]
    
    return {"success": True, "clans": clans}


@router.post("/clans")
async def create_clan(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """➕ Klan oluştur"""
    ensure_social_tables(db)
    
    # Zaten klan üyesi mi?
    existing = db.execute(text(
        "SELECT clan_id FROM clan_members WHERE user_id = :uid"
    ), {"uid": current_user.id}).fetchone()
    
    if existing:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Zaten bir klana üyesiniz"})
    
    name = data.get("name", "").strip()
    tag = data.get("tag", "").upper().strip()
    description = data.get("description", "")
    
    if not name or len(name) < 3:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Klan adı en az 3 karakter olmalı"})
    
    if not tag or len(tag) < 2 or len(tag) > 5:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Klan etiketi 2-5 karakter olmalı"})
    
    try:
        r = db.execute(text("""
            INSERT INTO clans (name, tag, description, owner_id, color)
            VALUES (:name, :tag, :desc, :owner, :color)
        """), {
            "name": name, "tag": tag, "desc": description,
            "owner": current_user.id, "color": data.get("color", "#ff6b00")
        })
        clan_id = r.lastrowid
        
        # Kurucuyu üye olarak ekle
        db.execute(text("""
            INSERT INTO clan_members (clan_id, user_id, role) VALUES (:cid, :uid, 'owner')
        """), {"cid": clan_id, "uid": current_user.id})
        
        db.commit()
        
        # Başarım ver
        await grant_achievement(db, current_user.id, "clan_founder")
        
        return {"success": True, "clan_id": clan_id, "message": "Klan oluşturuldu"}
    except:
        db.rollback()
        return JSONResponse(status_code=400, content={"success": False, "detail": "Bu isim veya etiket zaten kullanılıyor"})


@router.get("/clans/{clan_id}")
async def get_clan(clan_id: int, db: Session = Depends(get_db)):
    """🔍 Klan detayı"""
    ensure_social_tables(db)
    
    clan = db.execute(text("SELECT * FROM clans WHERE id = :id"), {"id": clan_id}).fetchone()
    if not clan:
        raise HTTPException(404, "Klan bulunamadı")
    
    members = db.execute(text("""
        SELECT cm.*, u.username, u.avatar_url FROM clan_members cm
        JOIN users u ON cm.user_id = u.id
        WHERE cm.clan_id = :cid ORDER BY cm.role DESC, cm.joined_at
    """), {"cid": clan_id}).fetchall()
    
    return {
        "success": True,
        "clan": {
            "id": clan[0], "name": clan[1], "tag": clan[2], "description": clan[3],
            "logo_url": clan[4], "banner_url": clan[5], "color": clan[6],
            "is_recruiting": bool(clan[9]), "member_count": clan[11],
            "wins": clan[12], "losses": clan[13], "points": clan[14]
        },
        "members": [{
            "user_id": m[2], "role": m[3], "username": m[5], "avatar_url": m[6],
            "joined_at": m[4].isoformat() if m[4] else None
        } for m in members]
    }


@router.post("/clans/{clan_id}/apply")
async def apply_to_clan(
    clan_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📝 Klana başvur"""
    ensure_social_tables(db)
    
    # Zaten üye mi?
    existing = db.execute(text(
        "SELECT id FROM clan_members WHERE user_id = :uid"
    ), {"uid": current_user.id}).fetchone()
    
    if existing:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Zaten bir klana üyesiniz"})
    
    # Bekleyen başvuru var mı?
    pending = db.execute(text("""
        SELECT id FROM clan_applications 
        WHERE clan_id = :cid AND user_id = :uid AND status = 'pending'
    """), {"cid": clan_id, "uid": current_user.id}).fetchone()
    
    if pending:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Zaten bekleyen başvurunuz var"})
    
    db.execute(text("""
        INSERT INTO clan_applications (clan_id, user_id, message)
        VALUES (:cid, :uid, :msg)
    """), {"cid": clan_id, "uid": current_user.id, "msg": data.get("message", "")})
    db.commit()
    
    return {"success": True, "message": "Başvurunuz gönderildi"}


# ============================================================================
# ACHIEVEMENT SYSTEM
# ============================================================================

@router.get("/achievements")
async def list_achievements(db: Session = Depends(get_db)):
    """🏆 Başarım listesi"""
    ensure_social_tables(db)
    
    rows = db.execute(text("""
        SELECT * FROM achievements WHERE is_active = TRUE AND is_secret = FALSE
        ORDER BY category, points
    """)).fetchall()
    
    achievements = [{
        "id": r[0], "code": r[1], "name": r[2], "description": r[3],
        "icon": r[4], "points": r[5], "category": r[6]
    } for r in rows]
    
    return {"success": True, "achievements": achievements}


@router.get("/achievements/my")
async def my_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🏆 Kazanılan başarımlar"""
    ensure_social_tables(db)
    
    rows = db.execute(text("""
        SELECT a.*, ua.unlocked_at FROM achievements a
        JOIN user_achievements ua ON a.id = ua.achievement_id
        WHERE ua.user_id = :uid
        ORDER BY ua.unlocked_at DESC
    """), {"uid": current_user.id}).fetchall()
    
    achievements = [{
        "id": r[0], "code": r[1], "name": r[2], "description": r[3],
        "icon": r[4], "points": r[5], "category": r[6],
        "unlocked_at": r[11].isoformat() if r[11] else None
    } for r in rows]
    
    total_points = sum(a["points"] for a in achievements)
    
    return {"success": True, "achievements": achievements, "total_points": total_points}


async def grant_achievement(db: Session, user_id: int, code: str) -> bool:
    """Başarım ver"""
    ensure_social_tables(db)
    
    achievement = db.execute(text(
        "SELECT id FROM achievements WHERE code = :code"
    ), {"code": code}).fetchone()
    
    if not achievement:
        return False
    
    # Zaten var mı?
    existing = db.execute(text("""
        SELECT id FROM user_achievements WHERE user_id = :uid AND achievement_id = :aid
    """), {"uid": user_id, "aid": achievement[0]}).fetchone()
    
    if existing:
        return False
    
    db.execute(text("""
        INSERT INTO user_achievements (user_id, achievement_id) VALUES (:uid, :aid)
    """), {"uid": user_id, "aid": achievement[0]})
    db.commit()
    
    return True


# ============================================================================
# FRIENDS SYSTEM
# ============================================================================

@router.get("/friends")
async def list_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """👥 Arkadaş listesi"""
    ensure_social_tables(db)
    
    rows = db.execute(text("""
        SELECT u.id, u.username, u.avatar_url, f.created_at FROM friendships f
        JOIN users u ON (f.friend_id = u.id AND f.user_id = :uid) OR (f.user_id = u.id AND f.friend_id = :uid)
        WHERE f.status = 'accepted' AND u.id != :uid
    """), {"uid": current_user.id}).fetchall()
    
    friends = [{
        "id": r[0], "username": r[1], "avatar_url": r[2],
        "since": r[3].isoformat() if r[3] else None
    } for r in rows]
    
    return {"success": True, "friends": friends, "count": len(friends)}


@router.post("/friends/request")
async def send_friend_request(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """➕ Arkadaşlık isteği gönder"""
    ensure_social_tables(db)
    
    friend_id = data.get("user_id")
    
    if friend_id == current_user.id:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Kendinize istek gönderemezsiniz"})
    
    # Zaten arkadaş mı?
    existing = db.execute(text("""
        SELECT status FROM friendships 
        WHERE (user_id = :uid AND friend_id = :fid) OR (user_id = :fid AND friend_id = :uid)
    """), {"uid": current_user.id, "fid": friend_id}).fetchone()
    
    if existing:
        if existing[0] == "accepted":
            return JSONResponse(status_code=400, content={"success": False, "detail": "Zaten arkadaşsınız"})
        elif existing[0] == "pending":
            return JSONResponse(status_code=400, content={"success": False, "detail": "Bekleyen istek var"})
        elif existing[0] == "blocked":
            return JSONResponse(status_code=400, content={"success": False, "detail": "Bu kullanıcı engellenmiş"})
    
    db.execute(text("""
        INSERT INTO friendships (user_id, friend_id, status) VALUES (:uid, :fid, 'pending')
    """), {"uid": current_user.id, "fid": friend_id})
    db.commit()
    
    return {"success": True, "message": "Arkadaşlık isteği gönderildi"}


@router.post("/friends/accept")
async def accept_friend_request(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ Arkadaşlık isteğini kabul et"""
    friend_id = data.get("user_id")
    
    db.execute(text("""
        UPDATE friendships SET status = 'accepted', accepted_at = NOW()
        WHERE user_id = :fid AND friend_id = :uid AND status = 'pending'
    """), {"uid": current_user.id, "fid": friend_id})
    db.commit()
    
    return {"success": True, "message": "Arkadaşlık kabul edildi"}
