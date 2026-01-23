"""
📊 AGTR Analytics & Dashboard API
Dashboard Charts, Player Stats, Revenue Reports, Export
"""
import csv
import io
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User, UserRole
from app.core.redis_manager import redis_manager

router = APIRouter()

# Cache TTL constants
DASHBOARD_CACHE_TTL = 60  # 1 minute for dashboard
CHARTS_CACHE_TTL = 300  # 5 minutes for charts
PLAYERS_CACHE_TTL = 120  # 2 minutes for player stats
PAGE_VIEWS_CACHE_TTL = 180  # 3 minutes for page views


async def get_cached_or_compute(cache_key: str, ttl: int, compute_func):
    """Generic cache helper - returns cached data or computes and caches it"""
    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass  # Cache miss or error, continue to compute

    # Compute the result
    result = compute_func()

    # Cache the result
    try:
        await redis_manager.set(cache_key, json.dumps(result, default=str), expire=ttl)
    except Exception:
        pass  # Cache write error, not critical

    return result

# ============================================================================
# DATABASE TABLES
# ============================================================================

def ensure_analytics_tables(db: Session):
    """Analytics tablolarını oluştur"""
    try:
        # Oyuncu istatistikleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS player_stats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            steam_id VARCHAR(50),
            username VARCHAR(100),
            server_id INT,
            kills INT DEFAULT 0,
            deaths INT DEFAULT 0,
            headshots INT DEFAULT 0,
            playtime_minutes INT DEFAULT 0,
            score INT DEFAULT 0,
            last_seen DATETIME,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_player_server (steam_id, server_id),
            INDEX idx_server (server_id),
            INDEX idx_steam (steam_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Günlük istatistikler
        db.execute(text("""CREATE TABLE IF NOT EXISTS daily_stats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            stat_date DATE NOT NULL,
            stat_type VARCHAR(50) NOT NULL,
            stat_key VARCHAR(100),
            stat_value DECIMAL(15,2) DEFAULT 0,
            UNIQUE KEY unique_stat (stat_date, stat_type, stat_key),
            INDEX idx_date (stat_date),
            INDEX idx_type (stat_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Sayfa görüntüleme
        db.execute(text("""CREATE TABLE IF NOT EXISTS page_views (
            id INT AUTO_INCREMENT PRIMARY KEY,
            page_path VARCHAR(255),
            user_id INT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            referrer VARCHAR(500),
            viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_path (page_path),
            INDEX idx_date (viewed_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        db.commit()
    except Exception:
        db.rollback()


# ============================================================================
# DASHBOARD
# ============================================================================

@router.get("/dashboard")
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Dashboard verileri - Redis cached (1 dakika)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")

    ensure_analytics_tables(db)

    cache_key = "analytics:dashboard"

    def compute_dashboard():
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        dashboard = {}

        # Kullanıcı sayıları
        dashboard["total_users"] = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
        dashboard["new_users_today"] = db.execute(text(
            "SELECT COUNT(*) FROM users WHERE created_at > :today"
        ), {"today": today}).fetchone()[0]
        dashboard["new_users_week"] = db.execute(text(
            "SELECT COUNT(*) FROM users WHERE created_at > :week"
        ), {"week": week_ago}).fetchone()[0]

        # Sunucu sayıları
        dashboard["total_servers"] = db.execute(text("SELECT COUNT(*) FROM game_servers")).fetchone()[0]
        dashboard["online_servers"] = db.execute(text(
            "SELECT COUNT(*) FROM game_servers WHERE status = 'online'"
        )).fetchone()[0]

        # Gelir (varsa payment_transactions tablosu)
        try:
            dashboard["revenue_today"] = float(db.execute(text("""
                SELECT COALESCE(SUM(amount), 0) FROM payment_transactions
                WHERE status = 'success' AND completed_at > :today
            """), {"today": today}).fetchone()[0])

            dashboard["revenue_month"] = float(db.execute(text("""
                SELECT COALESCE(SUM(amount), 0) FROM payment_transactions
                WHERE status = 'success' AND completed_at > :month
            """), {"month": month_ago}).fetchone()[0])
        except Exception:
            dashboard["revenue_today"] = 0
            dashboard["revenue_month"] = 0

        # Forum aktivitesi
        try:
            dashboard["forum_topics_today"] = db.execute(text(
                "SELECT COUNT(*) FROM forum_topics WHERE created_at > :today"
            ), {"today": today}).fetchone()[0]

            dashboard["forum_posts_today"] = db.execute(text(
                "SELECT COUNT(*) FROM forum_replies WHERE created_at > :today"
            ), {"today": today}).fetchone()[0]
        except Exception:
            dashboard["forum_topics_today"] = 0
            dashboard["forum_posts_today"] = 0

        # Aktif oyuncu sayısı
        try:
            dashboard["active_players"] = db.execute(text(
                "SELECT COALESCE(SUM(current_players), 0) FROM game_servers WHERE status = 'online'"
            )).fetchone()[0]
        except Exception:
            dashboard["active_players"] = 0

        return {"success": True, "dashboard": dashboard}

    return await get_cached_or_compute(cache_key, DASHBOARD_CACHE_TTL, compute_dashboard)


@router.get("/dashboard/charts")
async def get_dashboard_charts(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📈 Dashboard grafikleri - Redis cached (5 dakika)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")

    # Limit days parameter to prevent expensive queries
    days = min(days, 90)

    ensure_analytics_tables(db)

    cache_key = f"analytics:charts:{days}"

    def compute_charts():
        since = datetime.now() - timedelta(days=days)
        charts = {}

        # Günlük yeni kullanıcılar
        rows = db.execute(text("""
            SELECT DATE(created_at) as day, COUNT(*) as count
            FROM users WHERE created_at > :since
            GROUP BY DATE(created_at) ORDER BY day
        """), {"since": since}).fetchall()
        charts["users_by_day"] = [{"date": str(r[0]), "count": r[1]} for r in rows]

        # Günlük gelir
        try:
            rows = db.execute(text("""
                SELECT DATE(completed_at) as day, SUM(amount) as total
                FROM payment_transactions
                WHERE status = 'success' AND completed_at > :since
                GROUP BY DATE(completed_at) ORDER BY day
            """), {"since": since}).fetchall()
            charts["revenue_by_day"] = [{"date": str(r[0]), "amount": float(r[1])} for r in rows]
        except Exception:
            charts["revenue_by_day"] = []

        # Sunucu durumu dağılımı
        rows = db.execute(text("""
            SELECT status, COUNT(*) as count FROM game_servers GROUP BY status
        """)).fetchall()
        charts["server_status"] = [{"status": r[0], "count": r[1]} for r in rows]

        # Oyun türü dağılımı
        rows = db.execute(text("""
            SELECT game_type, COUNT(*) as count FROM game_servers GROUP BY game_type
        """)).fetchall()
        charts["servers_by_game"] = [{"game": r[0], "count": r[1]} for r in rows]

        # En aktif sunucular
        rows = db.execute(text("""
            SELECT id, name, current_players, max_players FROM game_servers
            WHERE status = 'online' ORDER BY current_players DESC LIMIT 10
        """)).fetchall()
        charts["top_servers"] = [{"id": r[0], "name": r[1], "players": r[2], "max": r[3]} for r in rows]

        return {"success": True, "charts": charts}

    return await get_cached_or_compute(cache_key, CHARTS_CACHE_TTL, compute_charts)


# ============================================================================
# PLAYER STATISTICS
# ============================================================================

@router.get("/players")
async def get_player_stats(
    server_id: Optional[int] = None,
    sort: str = "score",
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """🎮 Oyuncu istatistikleri - Redis cached (2 dakika)"""
    ensure_analytics_tables(db)

    # Limit the limit parameter to prevent large result sets
    limit = min(limit, 500)

    # Set query timeout (5 seconds) for analytics queries
    db.execute(text("SET SESSION MAX_EXECUTION_TIME = 5000"))

    # Use whitelist for sort parameter to prevent SQL injection
    sort_whitelist = {"score", "kills", "kd", "playtime", "recent"}
    if sort not in sort_whitelist:
        sort = "score"

    # Cache key based on parameters
    cache_key = f"analytics:players:{server_id or 'all'}:{sort}:{limit}"

    # Check cache
    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    p = {"lim": limit}

    # Build query with parameterized values only
    if server_id:
        p["sid"] = server_id
        if sort == "kd":
            rows = db.execute(text(
                "SELECT * FROM player_stats WHERE server_id = :sid ORDER BY (kills / GREATEST(deaths, 1)) DESC LIMIT :lim"
            ), p).fetchall()
        elif sort == "kills":
            rows = db.execute(text(
                "SELECT * FROM player_stats WHERE server_id = :sid ORDER BY kills DESC LIMIT :lim"
            ), p).fetchall()
        elif sort == "playtime":
            rows = db.execute(text(
                "SELECT * FROM player_stats WHERE server_id = :sid ORDER BY playtime_minutes DESC LIMIT :lim"
            ), p).fetchall()
        elif sort == "recent":
            rows = db.execute(text(
                "SELECT * FROM player_stats WHERE server_id = :sid ORDER BY last_seen DESC LIMIT :lim"
            ), p).fetchall()
        else:  # default: score
            rows = db.execute(text(
                "SELECT * FROM player_stats WHERE server_id = :sid ORDER BY score DESC LIMIT :lim"
            ), p).fetchall()
    else:
        if sort == "kd":
            rows = db.execute(text(
                "SELECT * FROM player_stats ORDER BY (kills / GREATEST(deaths, 1)) DESC LIMIT :lim"
            ), p).fetchall()
        elif sort == "kills":
            rows = db.execute(text(
                "SELECT * FROM player_stats ORDER BY kills DESC LIMIT :lim"
            ), p).fetchall()
        elif sort == "playtime":
            rows = db.execute(text(
                "SELECT * FROM player_stats ORDER BY playtime_minutes DESC LIMIT :lim"
            ), p).fetchall()
        elif sort == "recent":
            rows = db.execute(text(
                "SELECT * FROM player_stats ORDER BY last_seen DESC LIMIT :lim"
            ), p).fetchall()
        else:  # default: score
            rows = db.execute(text(
                "SELECT * FROM player_stats ORDER BY score DESC LIMIT :lim"
            ), p).fetchall()
    
    players = [{
        "id": r[0], "steam_id": r[1], "username": r[2], "server_id": r[3],
        "kills": r[4], "deaths": r[5], "headshots": r[6],
        "playtime_hours": round(r[7] / 60, 1) if r[7] else 0,
        "score": r[8], "kd_ratio": round(r[4] / max(r[5], 1), 2),
        "last_seen": r[9].isoformat() if r[9] else None
    } for r in rows]

    result = {"success": True, "players": players}

    # Cache the result
    try:
        await redis_manager.set(cache_key, json.dumps(result), expire=PLAYERS_CACHE_TTL)
    except Exception:
        pass

    return result


@router.get("/players/{steam_id}")
async def get_player_detail(steam_id: str, db: Session = Depends(get_db)):
    """🔍 Oyuncu detayı"""
    ensure_analytics_tables(db)
    
    rows = db.execute(text("""
        SELECT ps.*, gs.name as server_name FROM player_stats ps
        LEFT JOIN game_servers gs ON ps.server_id = gs.id
        WHERE ps.steam_id = :sid ORDER BY ps.score DESC
    """), {"sid": steam_id}).fetchall()
    
    if not rows:
        raise HTTPException(404, "Oyuncu bulunamadı")
    
    # Toplam istatistikler
    total_kills = sum(r[4] for r in rows)
    total_deaths = sum(r[5] for r in rows)
    total_playtime = sum(r[7] for r in rows)
    total_score = sum(r[8] for r in rows)
    
    servers = [{
        "server_id": r[3], "server_name": r[12],
        "kills": r[4], "deaths": r[5], "score": r[8],
        "playtime_hours": round(r[7] / 60, 1) if r[7] else 0
    } for r in rows]
    
    return {
        "success": True,
        "player": {
            "steam_id": steam_id,
            "username": rows[0][2],
            "total_kills": total_kills,
            "total_deaths": total_deaths,
            "total_score": total_score,
            "total_playtime_hours": round(total_playtime / 60, 1),
            "kd_ratio": round(total_kills / max(total_deaths, 1), 2),
            "servers_played": len(rows),
            "first_seen": rows[0][10].isoformat() if rows[0][10] else None,
            "last_seen": max(r[9] for r in rows if r[9]).isoformat() if any(r[9] for r in rows) else None
        },
        "servers": servers
    }


# ============================================================================
# REVENUE REPORTS
# ============================================================================

@router.get("/revenue")
async def get_revenue_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    group_by: str = "day",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """💰 Gelir raporu"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")

    # Tarih aralığı
    if not start_date:
        start = datetime.now() - timedelta(days=30)
    else:
        start = datetime.strptime(start_date, "%Y-%m-%d")

    if not end_date:
        end = datetime.now()
    else:
        end = datetime.strptime(end_date, "%Y-%m-%d")

    try:
        # Grup bazında - SQL injection'a karşı whitelist kullan
        allowed_group_by = {"day", "week", "month"}
        if group_by not in allowed_group_by:
            group_by = "day"

        # Set query timeout (5 seconds) for long-running queries
        db.execute(text("SET SESSION MAX_EXECUTION_TIME = 5000"))

        # Parameterized query - group_sql is from whitelist, not user input
        if group_by == "day":
            rows = db.execute(text("""
                SELECT DATE(completed_at) as period,
                       COUNT(*) as transaction_count,
                       SUM(amount) as total,
                       AVG(amount) as average,
                       gateway
                FROM payment_transactions
                WHERE status = 'success' AND completed_at BETWEEN :start AND :end
                GROUP BY DATE(completed_at), gateway
                ORDER BY period
            """), {"start": start, "end": end}).fetchall()
        elif group_by == "week":
            rows = db.execute(text("""
                SELECT YEARWEEK(completed_at) as period,
                       COUNT(*) as transaction_count,
                       SUM(amount) as total,
                       AVG(amount) as average,
                       gateway
                FROM payment_transactions
                WHERE status = 'success' AND completed_at BETWEEN :start AND :end
                GROUP BY YEARWEEK(completed_at), gateway
                ORDER BY period
            """), {"start": start, "end": end}).fetchall()
        else:
            rows = db.execute(text("""
                SELECT DATE_FORMAT(completed_at, '%Y-%m') as period,
                       COUNT(*) as transaction_count,
                       SUM(amount) as total,
                       AVG(amount) as average,
                       gateway
                FROM payment_transactions
                WHERE status = 'success' AND completed_at BETWEEN :start AND :end
                GROUP BY DATE_FORMAT(completed_at, '%Y-%m'), gateway
                ORDER BY period
            """), {"start": start, "end": end}).fetchall()
        
        report = [{
            "period": str(r[0]), "transactions": r[1],
            "total": float(r[2]), "average": float(r[3]), "gateway": r[4]
        } for r in rows]
        
        # Toplam
        totals = db.execute(text("""
            SELECT COUNT(*), SUM(amount), AVG(amount)
            FROM payment_transactions 
            WHERE status = 'success' AND completed_at BETWEEN :start AND :end
        """), {"start": start, "end": end}).fetchone()
        
        return {
            "success": True,
            "report": report,
            "totals": {
                "transactions": totals[0],
                "revenue": float(totals[1]) if totals[1] else 0,
                "average": float(totals[2]) if totals[2] else 0
            },
            "period": {"start": start.isoformat(), "end": end.isoformat()}
        }
    except Exception as e:
        return {"success": True, "report": [], "totals": {"transactions": 0, "revenue": 0}, "error": str(e)}


# ============================================================================
# EXPORT
# ============================================================================

@router.get("/export/users")
async def export_users(
    format: str = "csv",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📥 Kullanıcı listesi export"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(403, "Sadece süper admin")
    
    rows = db.execute(text("""
        SELECT id, username, email, role, status, created_at, last_login
        FROM users ORDER BY id
    """)).fetchall()
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Kullanıcı Adı", "Email", "Rol", "Durum", "Kayıt Tarihi", "Son Giriş"])
        for r in rows:
            writer.writerow([r[0], r[1], r[2], r[3].value if r[3] else "", r[4].value if r[4] else "", r[5], r[6]])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=users_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    elif format == "json":
        data = [{
            "id": r[0], "username": r[1], "email": r[2],
            "role": r[3].value if r[3] else None, "status": r[4].value if r[4] else None,
            "created_at": r[5].isoformat() if r[5] else None,
            "last_login": r[6].isoformat() if r[6] else None
        } for r in rows]
        
        return StreamingResponse(
            iter([json.dumps(data, indent=2)]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=users_{datetime.now().strftime('%Y%m%d')}.json"}
        )


@router.get("/export/revenue")
async def export_revenue(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "csv",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📥 Gelir raporu export"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    if not start_date:
        start = datetime.now() - timedelta(days=30)
    else:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    
    if not end_date:
        end = datetime.now()
    else:
        end = datetime.strptime(end_date, "%Y-%m-%d")
    
    try:
        rows = db.execute(text("""
            SELECT pt.*, u.username FROM payment_transactions pt
            LEFT JOIN users u ON pt.user_id = u.id
            WHERE pt.status = 'success' AND pt.completed_at BETWEEN :start AND :end
            ORDER BY pt.completed_at DESC
        """), {"start": start, "end": end}).fetchall()
    except Exception:
        rows = []
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Kullanıcı", "Tutar", "Ödeme Yöntemi", "Tarih"])
        for r in rows:
            writer.writerow([r[0], r[14] if len(r) > 14 else "", r[4], r[2], r[12]])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=revenue_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    return {"success": True, "message": "Export tamamlandı"}


# ============================================================================
# PAGE TRACKING
# ============================================================================

@router.post("/track")
async def track_page_view(
    data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """📊 Sayfa görüntüleme kaydet"""
    ensure_analytics_tables(db)
    
    db.execute(text("""
        INSERT INTO page_views (page_path, user_id, ip_address, user_agent, referrer)
        VALUES (:path, :uid, :ip, :ua, :ref)
    """), {
        "path": data.get("path", "/"),
        "uid": data.get("user_id"),
        "ip": request.client.host if hasattr(request, 'client') else None,
        "ua": data.get("user_agent", "")[:500],
        "ref": data.get("referrer", "")[:500]
    })
    db.commit()
    
    return {"success": True}


@router.get("/page-views")
async def get_page_views(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Sayfa görüntüleme istatistikleri - Redis cached (3 dakika)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")

    # Limit days parameter
    days = min(days, 30)

    ensure_analytics_tables(db)

    cache_key = f"analytics:page_views:{days}"

    def compute_page_views():
        since = datetime.now() - timedelta(days=days)

        # En çok görüntülenen sayfalar
        rows = db.execute(text("""
            SELECT page_path, COUNT(*) as views FROM page_views
            WHERE viewed_at > :since
            GROUP BY page_path ORDER BY views DESC LIMIT 20
        """), {"since": since}).fetchall()

        top_pages = [{"path": r[0], "views": r[1]} for r in rows]

        # Günlük toplam
        rows = db.execute(text("""
            SELECT DATE(viewed_at) as day, COUNT(*) as views FROM page_views
            WHERE viewed_at > :since
            GROUP BY DATE(viewed_at) ORDER BY day
        """), {"since": since}).fetchall()

        daily = [{"date": str(r[0]), "views": r[1]} for r in rows]

        return {"success": True, "top_pages": top_pages, "daily": daily}

    return await get_cached_or_compute(cache_key, PAGE_VIEWS_CACHE_TTL, compute_page_views)
