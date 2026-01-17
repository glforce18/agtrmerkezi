"""
🔐 AGTR Security API
IP Whitelist/Blacklist, Brute Force Protection, Audit Log, Session Management
"""
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User, UserRole

router = APIRouter()

# ============================================================================
# DATABASE TABLES
# ============================================================================

def ensure_security_tables(db: Session):
    """Güvenlik tablolarını oluştur"""
    try:
        # IP Whitelist/Blacklist
        db.execute(text("""CREATE TABLE IF NOT EXISTS ip_rules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip_address VARCHAR(45) NOT NULL,
            rule_type ENUM('whitelist', 'blacklist') NOT NULL,
            reason VARCHAR(255),
            created_by INT,
            expires_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_ip (ip_address),
            INDEX idx_type (rule_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Login Attempts (Brute Force)
        db.execute(text("""CREATE TABLE IF NOT EXISTS login_attempts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip_address VARCHAR(45) NOT NULL,
            username VARCHAR(100),
            success BOOLEAN DEFAULT FALSE,
            user_agent TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_ip_time (ip_address, created_at),
            INDEX idx_username (username)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Audit Log
        db.execute(text("""CREATE TABLE IF NOT EXISTS audit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            username VARCHAR(100),
            action VARCHAR(100) NOT NULL,
            resource_type VARCHAR(50),
            resource_id INT,
            old_value JSON,
            new_value JSON,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user (user_id),
            INDEX idx_action (action),
            INDEX idx_time (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # User Sessions
        db.execute(text("""CREATE TABLE IF NOT EXISTS user_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            session_token VARCHAR(255) NOT NULL UNIQUE,
            ip_address VARCHAR(45),
            user_agent TEXT,
            device_info VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            INDEX idx_user (user_id),
            INDEX idx_token (session_token),
            INDEX idx_active (is_active)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Account Lockouts
        db.execute(text("""CREATE TABLE IF NOT EXISTS account_lockouts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            identifier VARCHAR(100) NOT NULL,
            identifier_type ENUM('ip', 'username') NOT NULL,
            locked_until DATETIME NOT NULL,
            reason VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_identifier (identifier, identifier_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        db.commit()
    except:
        db.rollback()


# ============================================================================
# IP WHITELIST / BLACKLIST
# ============================================================================

@router.get("/ip-rules")
async def list_ip_rules(
    rule_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 IP kurallarını listele"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_security_tables(db)
    
    q = "SELECT * FROM ip_rules WHERE 1=1"
    p = {}
    if rule_type:
        q += " AND rule_type = :rt"
        p["rt"] = rule_type
    q += " ORDER BY created_at DESC"
    
    rows = db.execute(text(q), p).fetchall()
    rules = [{
        "id": r[0], "ip_address": r[1], "rule_type": r[2],
        "reason": r[3], "expires_at": r[5].isoformat() if r[5] else None,
        "created_at": r[6].isoformat() if r[6] else None
    } for r in rows]
    
    return {"success": True, "rules": rules}


@router.post("/ip-rules")
async def add_ip_rule(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """➕ IP kuralı ekle"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_security_tables(db)
    
    ip = data.get("ip_address", "").strip()
    rule_type = data.get("rule_type", "blacklist")
    reason = data.get("reason", "")
    expires_hours = data.get("expires_hours")
    
    if not ip:
        return JSONResponse(status_code=400, content={"success": False, "detail": "IP adresi gerekli"})
    
    expires_at = None
    if expires_hours:
        expires_at = datetime.now() + timedelta(hours=int(expires_hours))
    
    db.execute(text("""
        INSERT INTO ip_rules (ip_address, rule_type, reason, created_by, expires_at)
        VALUES (:ip, :rt, :reason, :uid, :exp)
    """), {"ip": ip, "rt": rule_type, "reason": reason, "uid": current_user.id, "exp": expires_at})
    db.commit()
    
    # Audit log
    await log_audit(db, current_user.id, current_user.username, "ip_rule_add", 
                   "ip_rule", None, None, {"ip": ip, "type": rule_type})
    
    return {"success": True, "message": f"IP {rule_type} listesine eklendi"}


@router.delete("/ip-rules/{rule_id}")
async def delete_ip_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🗑️ IP kuralını sil"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    db.execute(text("DELETE FROM ip_rules WHERE id = :id"), {"id": rule_id})
    db.commit()
    
    return {"success": True, "message": "Kural silindi"}


def check_ip_allowed(db: Session, ip: str) -> tuple:
    """IP kontrolü yap"""
    ensure_security_tables(db)
    
    # Whitelist kontrolü
    wl = db.execute(text("""
        SELECT id FROM ip_rules 
        WHERE ip_address = :ip AND rule_type = 'whitelist' 
        AND (expires_at IS NULL OR expires_at > NOW())
    """), {"ip": ip}).fetchone()
    if wl:
        return (True, "whitelist")
    
    # Blacklist kontrolü
    bl = db.execute(text("""
        SELECT reason FROM ip_rules 
        WHERE ip_address = :ip AND rule_type = 'blacklist'
        AND (expires_at IS NULL OR expires_at > NOW())
    """), {"ip": ip}).fetchone()
    if bl:
        return (False, bl[0] or "Blacklisted")
    
    return (True, None)


# ============================================================================
# BRUTE FORCE PROTECTION
# ============================================================================

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 30

@router.get("/login-attempts")
async def get_login_attempts(
    ip: Optional[str] = None,
    username: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Giriş denemelerini listele"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_security_tables(db)
    
    q = "SELECT * FROM login_attempts WHERE 1=1"
    p = {"lim": limit}
    if ip:
        q += " AND ip_address = :ip"
        p["ip"] = ip
    if username:
        q += " AND username = :un"
        p["un"] = username
    q += " ORDER BY created_at DESC LIMIT :lim"
    
    rows = db.execute(text(q), p).fetchall()
    attempts = [{
        "id": r[0], "ip_address": r[1], "username": r[2],
        "success": bool(r[3]), "user_agent": r[4][:100] if r[4] else None,
        "created_at": r[5].isoformat() if r[5] else None
    } for r in rows]
    
    return {"success": True, "attempts": attempts}


def record_login_attempt(db: Session, ip: str, username: str, success: bool, user_agent: str = None):
    """Giriş denemesini kaydet"""
    ensure_security_tables(db)
    db.execute(text("""
        INSERT INTO login_attempts (ip_address, username, success, user_agent)
        VALUES (:ip, :un, :success, :ua)
    """), {"ip": ip, "un": username, "success": success, "ua": user_agent})
    db.commit()


def check_brute_force(db: Session, ip: str, username: str = None) -> tuple:
    """Brute force kontrolü"""
    ensure_security_tables(db)
    
    # IP bazlı kontrol
    lockout = db.execute(text("""
        SELECT locked_until FROM account_lockouts 
        WHERE identifier = :ip AND identifier_type = 'ip' AND locked_until > NOW()
    """), {"ip": ip}).fetchone()
    
    if lockout:
        return (False, f"IP kilitli. Bekleme: {lockout[0]}")
    
    # Son X dakikadaki başarısız denemeler
    since = datetime.now() - timedelta(minutes=LOCKOUT_MINUTES)
    failed = db.execute(text("""
        SELECT COUNT(*) FROM login_attempts 
        WHERE ip_address = :ip AND success = FALSE AND created_at > :since
    """), {"ip": ip, "since": since}).fetchone()[0]
    
    if failed >= MAX_ATTEMPTS:
        # Kilitle
        locked_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
        db.execute(text("""
            INSERT INTO account_lockouts (identifier, identifier_type, locked_until, reason)
            VALUES (:ip, 'ip', :until, :reason)
        """), {"ip": ip, "until": locked_until, "reason": f"{MAX_ATTEMPTS} başarısız deneme"})
        db.commit()
        return (False, f"Çok fazla başarısız deneme. {LOCKOUT_MINUTES} dakika bekleyin.")
    
    return (True, MAX_ATTEMPTS - failed)


@router.post("/unlock")
async def unlock_account(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔓 Hesap/IP kilidini aç"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    identifier = data.get("identifier")
    id_type = data.get("type", "ip")
    
    db.execute(text("""
        DELETE FROM account_lockouts WHERE identifier = :id AND identifier_type = :t
    """), {"id": identifier, "t": id_type})
    db.commit()
    
    return {"success": True, "message": "Kilit kaldırıldı"}


# ============================================================================
# AUDIT LOG
# ============================================================================

async def log_audit(
    db: Session, user_id: int, username: str, action: str,
    resource_type: str = None, resource_id: int = None,
    old_value: dict = None, new_value: dict = None,
    ip: str = None, user_agent: str = None
):
    """Audit log kaydı oluştur"""
    ensure_security_tables(db)
    db.execute(text("""
        INSERT INTO audit_logs (user_id, username, action, resource_type, resource_id, 
                               old_value, new_value, ip_address, user_agent)
        VALUES (:uid, :un, :action, :rt, :rid, :old, :new, :ip, :ua)
    """), {
        "uid": user_id, "un": username, "action": action,
        "rt": resource_type, "rid": resource_id,
        "old": json.dumps(old_value) if old_value else None,
        "new": json.dumps(new_value) if new_value else None,
        "ip": ip, "ua": user_agent
    })
    db.commit()


@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    days: int = 7,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Audit logları getir"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_security_tables(db)
    
    since = datetime.now() - timedelta(days=days)
    q = "SELECT * FROM audit_logs WHERE created_at > :since"
    p = {"since": since, "lim": limit}
    
    if user_id:
        q += " AND user_id = :uid"
        p["uid"] = user_id
    if action:
        q += " AND action LIKE :action"
        p["action"] = f"%{action}%"
    if resource_type:
        q += " AND resource_type = :rt"
        p["rt"] = resource_type
    
    q += " ORDER BY created_at DESC LIMIT :lim"
    
    rows = db.execute(text(q), p).fetchall()
    logs = [{
        "id": r[0], "user_id": r[1], "username": r[2], "action": r[3],
        "resource_type": r[4], "resource_id": r[5],
        "old_value": json.loads(r[6]) if r[6] else None,
        "new_value": json.loads(r[7]) if r[7] else None,
        "ip_address": r[8], "created_at": r[10].isoformat() if r[10] else None
    } for r in rows]
    
    return {"success": True, "logs": logs, "total": len(logs)}


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@router.get("/sessions")
async def get_user_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Kullanıcının aktif oturumları"""
    ensure_security_tables(db)
    
    rows = db.execute(text("""
        SELECT id, ip_address, user_agent, device_info, last_activity, created_at
        FROM user_sessions 
        WHERE user_id = :uid AND is_active = TRUE
        ORDER BY last_activity DESC
    """), {"uid": current_user.id}).fetchall()
    
    sessions = [{
        "id": r[0], "ip_address": r[1], 
        "user_agent": r[2][:100] if r[2] else None,
        "device_info": r[3],
        "last_activity": r[4].isoformat() if r[4] else None,
        "created_at": r[5].isoformat() if r[5] else None
    } for r in rows]
    
    return {"success": True, "sessions": sessions}


@router.get("/sessions/all")
async def get_all_sessions(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Tüm aktif oturumlar (Admin)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_security_tables(db)
    
    q = """SELECT s.*, u.username FROM user_sessions s 
           LEFT JOIN users u ON s.user_id = u.id
           WHERE s.is_active = TRUE"""
    p = {}
    if user_id:
        q += " AND s.user_id = :uid"
        p["uid"] = user_id
    q += " ORDER BY s.last_activity DESC LIMIT 100"
    
    rows = db.execute(text(q), p).fetchall()
    sessions = [{
        "id": r[0], "user_id": r[1], "ip_address": r[3],
        "device_info": r[5], "last_activity": r[7].isoformat() if r[7] else None,
        "username": r[11] if len(r) > 11 else None
    } for r in rows]
    
    return {"success": True, "sessions": sessions}


@router.delete("/sessions/{session_id}")
async def terminate_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔚 Oturumu sonlandır"""
    # Kendi oturumu veya admin
    session = db.execute(text(
        "SELECT user_id FROM user_sessions WHERE id = :id"
    ), {"id": session_id}).fetchone()
    
    if not session:
        raise HTTPException(404, "Oturum bulunamadı")
    
    if session[0] != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    db.execute(text("UPDATE user_sessions SET is_active = FALSE WHERE id = :id"), {"id": session_id})
    db.commit()
    
    return {"success": True, "message": "Oturum sonlandırıldı"}


@router.post("/sessions/terminate-all")
async def terminate_all_sessions(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔚 Tüm oturumları sonlandır (mevcut hariç)"""
    current_token = data.get("current_token")
    
    db.execute(text("""
        UPDATE user_sessions SET is_active = FALSE 
        WHERE user_id = :uid AND session_token != :token
    """), {"uid": current_user.id, "token": current_token or ""})
    db.commit()
    
    return {"success": True, "message": "Diğer tüm oturumlar sonlandırıldı"}


def create_session(db: Session, user_id: int, token: str, ip: str, user_agent: str):
    """Yeni oturum oluştur"""
    ensure_security_tables(db)
    
    # Cihaz bilgisi çıkar
    device = "Bilinmeyen"
    if user_agent:
        ua_lower = user_agent.lower()
        if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
            device = "Mobil"
        elif "windows" in ua_lower:
            device = "Windows"
        elif "mac" in ua_lower:
            device = "Mac"
        elif "linux" in ua_lower:
            device = "Linux"
    
    db.execute(text("""
        INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, device_info, expires_at)
        VALUES (:uid, :token, :ip, :ua, :device, DATE_ADD(NOW(), INTERVAL 7 DAY))
    """), {"uid": user_id, "token": token, "ip": ip, "ua": user_agent, "device": device})
    db.commit()


# ============================================================================
# PASSWORD POLICY
# ============================================================================

@router.get("/password-policy")
async def get_password_policy():
    """📋 Şifre politikası"""
    return {
        "success": True,
        "policy": {
            "min_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_number": True,
            "require_special": False,
            "max_age_days": 90,
            "history_count": 3
        }
    }


def validate_password(password: str) -> tuple:
    """Şifre politikası kontrolü"""
    errors = []
    
    if len(password) < 8:
        errors.append("En az 8 karakter olmalı")
    if not any(c.isupper() for c in password):
        errors.append("En az 1 büyük harf olmalı")
    if not any(c.islower() for c in password):
        errors.append("En az 1 küçük harf olmalı")
    if not any(c.isdigit() for c in password):
        errors.append("En az 1 rakam olmalı")
    
    return (len(errors) == 0, errors)


# ============================================================================
# SECURITY STATS
# ============================================================================

@router.get("/stats")
async def security_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Güvenlik istatistikleri"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_security_tables(db)
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    
    stats = {}
    
    # Bugünkü giriş denemeleri
    stats["today_attempts"] = db.execute(text(
        "SELECT COUNT(*) FROM login_attempts WHERE created_at > :today"
    ), {"today": today}).fetchone()[0]
    
    # Bugünkü başarısız denemeler
    stats["today_failed"] = db.execute(text(
        "SELECT COUNT(*) FROM login_attempts WHERE created_at > :today AND success = FALSE"
    ), {"today": today}).fetchone()[0]
    
    # Aktif kilitler
    stats["active_lockouts"] = db.execute(text(
        "SELECT COUNT(*) FROM account_lockouts WHERE locked_until > NOW()"
    )).fetchone()[0]
    
    # Blacklist sayısı
    stats["blacklisted_ips"] = db.execute(text(
        "SELECT COUNT(*) FROM ip_rules WHERE rule_type = 'blacklist'"
    )).fetchone()[0]
    
    # Aktif oturumlar
    stats["active_sessions"] = db.execute(text(
        "SELECT COUNT(*) FROM user_sessions WHERE is_active = TRUE"
    )).fetchone()[0]
    
    # Haftalık audit log
    stats["weekly_audit_count"] = db.execute(text(
        "SELECT COUNT(*) FROM audit_logs WHERE created_at > :week"
    ), {"week": week_ago}).fetchone()[0]
    
    return {"success": True, "stats": stats}
