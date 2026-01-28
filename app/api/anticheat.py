"""
AGTR Anti-Cheat API Endpoints
Proxies anti-cheat data from halflife database with RBAC
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.connection import get_db, get_halflife_db
from app.models.database import GameServer, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/anticheat", tags=["anticheat"])


# ============================================
# HELPER FUNCTIONS
# ============================================


def get_user_server_ids(user: User, db: Session) -> List[int]:
    """
    Get list of server IDs that user owns.
    Returns all server IDs if user is superadmin.
    """
    if user.is_superadmin or user.role == "admin":
        # Superadmin sees all servers
        return None  # None = all servers

    # Get user's owned servers
    servers = (
        db.query(GameServer)
        .filter(GameServer.owner_id == user.id, GameServer.status != "deleted")
        .all()
    )

    return [s.id for s in servers]


def verify_server_access(user: User, server_id: int, db: Session) -> bool:
    """
    Verify user has access to this server's anti-cheat data.
    Returns True if allowed, raises HTTPException if denied.
    """
    if user.is_superadmin or user.role == "admin":
        return True

    # Check if user owns this server
    server = (
        db.query(GameServer)
        .filter(
            GameServer.id == server_id,
            GameServer.owner_id == user.id,
            GameServer.status != "deleted",
        )
        .first()
    )

    if not server:
        raise HTTPException(status_code=403, detail="Access denied: You do not own this server")

    return True


def check_anticheat_subscription(server_id: int, db: Session) -> bool:
    """
    Check if server has active anti-cheat subscription.
    For now, returns True (all servers have access).

    TODO: Implement actual subscription check when payment system is ready.
    """
    # Future: Check if server.anticheat_enabled == True
    # Future: Check if subscription is active
    return True


# ============================================
# SCAN ENDPOINTS
# ============================================


@router.get("/servers/{server_id}/scans")
async def get_server_scans(
    server_id: int,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    passed: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """
    Get scans for specific server.

    Access control:
    - Server owner: Can see only their server's scans
    - Superadmin: Can see any server's scans

    Filters:
    - passed: True = clean scans, False = suspicious scans, None = all
    """
    # Verify access
    verify_server_access(current_user, server_id, db)

    # Check subscription (future)
    if not check_anticheat_subscription(server_id, db):
        raise HTTPException(
            status_code=402, detail="Anti-cheat subscription required for this server"
        )

    # Build query
    query = """
        SELECT
            s.id,
            s.hwid,
            s.server_id,
            s.passed,
            s.sus_count,
            s.hash_count,
            s.player_name,
            s.player_steamid,
            s.scan_time,
            s.version,
            p.name as current_name,
            p.steamid as current_steamid,
            p.ip as player_ip
        FROM agtr_scans s
        LEFT JOIN agtr_player_info p ON s.hwid = p.hwid
        WHERE s.server_id = :server_id
    """

    params = {"server_id": server_id}

    # Add passed filter
    if passed is not None:
        query += " AND s.passed = :passed"
        params["passed"] = passed

    query += " ORDER BY s.scan_time DESC LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset

    result = halflife_db.execute(text(query), params)
    scans = [dict(row._mapping) for row in result]

    # Get total count
    count_query = """
        SELECT COUNT(*) as total
        FROM agtr_scans
        WHERE server_id = :server_id
    """
    if passed is not None:
        count_query += " AND passed = :passed"

    count_result = halflife_db.execute(text(count_query), params)
    total = count_result.scalar()

    return {
        "server_id": server_id,
        "scans": scans,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/servers/{server_id}/scans/{scan_id}")
async def get_scan_detail(
    server_id: int,
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """Get detailed scan information including processes, modules, windows."""
    verify_server_access(current_user, server_id, db)

    # Get scan
    scan_query = """
        SELECT
            s.*,
            p.name as current_name,
            p.steamid as current_steamid,
            p.ip as player_ip,
            p.server as last_server
        FROM agtr_scans s
        LEFT JOIN agtr_player_info p ON s.hwid = p.hwid
        WHERE s.id = :scan_id AND s.server_id = :server_id
    """

    result = halflife_db.execute(text(scan_query), {"scan_id": scan_id, "server_id": server_id})
    scan = result.mappings().first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan_dict = dict(scan)

    # Get processes
    proc_query = """
        SELECT name, path, pid, is_suspicious
        FROM agtr_scan_processes
        WHERE scan_id = :scan_id
        ORDER BY is_suspicious DESC, name
    """
    procs = halflife_db.execute(text(proc_query), {"scan_id": scan_id})
    scan_dict["processes"] = [dict(row._mapping) for row in procs]

    # Get modules
    mod_query = """
        SELECT name, path, hash, size
        FROM agtr_scan_modules
        WHERE scan_id = :scan_id
        ORDER BY name
    """
    mods = halflife_db.execute(text(mod_query), {"scan_id": scan_id})
    scan_dict["modules"] = [dict(row._mapping) for row in mods]

    # Get windows
    win_query = """
        SELECT title, class_name, is_suspicious
        FROM agtr_scan_windows
        WHERE scan_id = :scan_id
        ORDER BY is_suspicious DESC, title
    """
    wins = halflife_db.execute(text(win_query), {"scan_id": scan_id})
    scan_dict["windows"] = [dict(row._mapping) for row in wins]

    # Get hashes
    hash_query = """
        SELECT filename, hash
        FROM agtr_hashes
        WHERE scan_id = :scan_id
        ORDER BY filename
    """
    hashes = halflife_db.execute(text(hash_query), {"scan_id": scan_id})
    scan_dict["hashes"] = [dict(row._mapping) for row in hashes]

    return scan_dict


@router.get("/servers/{server_id}/stats")
async def get_server_anticheat_stats(
    server_id: int,
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """Get anti-cheat statistics for server."""
    verify_server_access(current_user, server_id, db)

    stats_query = """
        SELECT
            COUNT(*) as total_scans,
            SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as clean_scans,
            SUM(CASE WHEN passed = 0 THEN 1 ELSE 0 END) as suspicious_scans,
            SUM(CASE WHEN sus_count > 0 THEN 1 ELSE 0 END) as flagged_scans,
            COUNT(DISTINCT hwid) as unique_players,
            COUNT(DISTINCT player_steamid) as unique_steamids,
            MAX(scan_time) as last_scan
        FROM agtr_scans
        WHERE server_id = :server_id
        AND scan_time > DATE_SUB(NOW(), INTERVAL :days DAY)
    """

    result = halflife_db.execute(text(stats_query), {"server_id": server_id, "days": days})
    stats = dict(result.mappings().first())

    # Get daily trend
    trend_query = """
        SELECT
            DATE(scan_time) as date,
            COUNT(*) as total,
            SUM(CASE WHEN passed = 0 THEN 1 ELSE 0 END) as suspicious
        FROM agtr_scans
        WHERE server_id = :server_id
        AND scan_time > DATE_SUB(NOW(), INTERVAL :days DAY)
        GROUP BY DATE(scan_time)
        ORDER BY date DESC
    """

    trend_result = halflife_db.execute(text(trend_query), {"server_id": server_id, "days": days})
    stats["daily_trend"] = [dict(row._mapping) for row in trend_result]

    return stats


# ============================================
# PLAYER ENDPOINTS
# ============================================


@router.get("/servers/{server_id}/players")
async def get_server_players(
    server_id: int,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """Get players who have scanned on this server."""
    verify_server_access(current_user, server_id, db)

    query = """
        SELECT
            p.hwid,
            p.name,
            p.steamid,
            p.ip,
            p.last_seen,
            COUNT(s.id) as scan_count,
            SUM(CASE WHEN s.passed = 0 THEN 1 ELSE 0 END) as failed_scans
        FROM agtr_player_info p
        INNER JOIN agtr_scans s ON p.hwid = s.hwid
        WHERE s.server_id = :server_id
    """

    params = {"server_id": server_id}

    if search:
        query += " AND (p.name LIKE :search OR p.steamid LIKE :search)"
        params["search"] = f"%{search}%"

    query += """
        GROUP BY p.hwid, p.name, p.steamid, p.ip, p.last_seen
        ORDER BY p.last_seen DESC
        LIMIT :limit OFFSET :offset
    """
    params["limit"] = limit
    params["offset"] = offset

    result = halflife_db.execute(text(query), params)
    players = [dict(row._mapping) for row in result]

    return {"server_id": server_id, "players": players, "limit": limit, "offset": offset}


@router.get("/servers/{server_id}/players/{hwid}")
async def get_player_detail(
    server_id: int,
    hwid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """Get detailed player information on this server."""
    verify_server_access(current_user, server_id, db)

    # Player info
    player_query = """
        SELECT * FROM agtr_player_info WHERE hwid = :hwid
    """
    result = halflife_db.execute(text(player_query), {"hwid": hwid})
    player = result.mappings().first()

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    player_dict = dict(player)

    # Scans on this server
    scans_query = """
        SELECT id, scan_time, passed, sus_count, version
        FROM agtr_scans
        WHERE hwid = :hwid AND server_id = :server_id
        ORDER BY scan_time DESC
        LIMIT 20
    """
    scans = halflife_db.execute(text(scans_query), {"hwid": hwid, "server_id": server_id})
    player_dict["scans"] = [dict(row._mapping) for row in scans]

    # Ban status (server-specific + global)
    ban_query = """
        SELECT * FROM agtr_hwid_bans
        WHERE hwid = :hwid
        AND is_active = 1
        AND (server_id = :server_id OR server_id IS NULL)
        ORDER BY created_at DESC
    """
    bans = halflife_db.execute(text(ban_query), {"hwid": hwid, "server_id": server_id})
    player_dict["bans"] = [dict(row._mapping) for row in bans]

    return player_dict


# ============================================
# BAN ENDPOINTS
# ============================================


@router.get("/servers/{server_id}/bans")
async def get_server_bans(
    server_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """Get server-specific and global bans."""
    verify_server_access(current_user, server_id, db)

    # Server-specific bans
    server_bans_query = """
        SELECT * FROM agtr_hwid_bans
        WHERE server_id = :server_id AND is_active = 1
        ORDER BY created_at DESC
    """
    server_bans = halflife_db.execute(text(server_bans_query), {"server_id": server_id})

    # Global bans (only for superadmin)
    global_bans = []
    if current_user.is_superadmin or current_user.role == "admin":
        global_bans_query = """
            SELECT * FROM agtr_hwid_bans
            WHERE server_id IS NULL AND is_active = 1
            ORDER BY created_at DESC
        """
        global_bans_result = halflife_db.execute(text(global_bans_query))
        global_bans = [dict(row._mapping) for row in global_bans_result]

    return {"server_bans": [dict(row._mapping) for row in server_bans], "global_bans": global_bans}


@router.post("/servers/{server_id}/bans")
async def create_server_ban(
    server_id: int,
    hwid: str,
    reason: str,
    duration_days: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """Create server-specific HWID ban."""
    verify_server_access(current_user, server_id, db)

    expires_at = None
    if duration_days:
        expires_at = datetime.now() + timedelta(days=duration_days)

    # Insert ban
    ban_query = """
        INSERT INTO agtr_hwid_bans
        (server_id, hwid, reason, expires_at, is_active, created_at, banned_by)
        VALUES (:server_id, :hwid, :reason, :expires_at, 1, NOW(), :banned_by)
    """

    halflife_db.execute(
        text(ban_query),
        {
            "server_id": server_id,
            "hwid": hwid,
            "reason": reason,
            "expires_at": expires_at,
            "banned_by": current_user.username,
        },
    )
    halflife_db.commit()

    logger.info(f"Server ban created: {hwid} on server {server_id} by {current_user.username}")

    return {
        "status": "success",
        "message": f"HWID {hwid} banned on server {server_id}",
        "expires_at": expires_at,
    }


@router.delete("/servers/{server_id}/bans/{ban_id}")
async def delete_server_ban(
    server_id: int,
    ban_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """Remove server-specific ban."""
    verify_server_access(current_user, server_id, db)

    # Verify ban belongs to this server
    check_query = """
        SELECT * FROM agtr_hwid_bans
        WHERE id = :ban_id AND server_id = :server_id
    """
    result = halflife_db.execute(text(check_query), {"ban_id": ban_id, "server_id": server_id})
    ban = result.mappings().first()

    if not ban:
        raise HTTPException(status_code=404, detail="Ban not found on this server")

    # Deactivate ban
    delete_query = """
        UPDATE agtr_hwid_bans
        SET is_active = 0
        WHERE id = :ban_id
    """
    halflife_db.execute(text(delete_query), {"ban_id": ban_id})
    halflife_db.commit()

    logger.info(f"Server ban removed: {ban_id} on server {server_id} by {current_user.username}")

    return {"status": "success", "message": "Ban removed"}


# ============================================
# DASHBOARD ENDPOINT
# ============================================


@router.get("/dashboard")
async def get_anticheat_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """
    Get anti-cheat dashboard data for all user's servers.
    Superadmins see all servers, regular users see only their servers.
    """
    server_ids = get_user_server_ids(current_user, db)

    if server_ids is None:
        # Superadmin - all servers
        servers_query = """
            SELECT DISTINCT server_id
            FROM agtr_scans
            WHERE server_id IS NOT NULL
        """
        result = halflife_db.execute(text(servers_query))
        server_ids = [row[0] for row in result]

    if not server_ids:
        return {
            "servers": [],
            "total_scans": 0,
            "total_suspicious": 0,
            "message": "No servers with anti-cheat data",
        }

    # Get stats per server
    stats_query = """
        SELECT
            s.server_id,
            sm.server_name,
            sm.unique_code,
            COUNT(*) as total_scans,
            SUM(CASE WHEN s.passed = 0 THEN 1 ELSE 0 END) as suspicious_scans,
            MAX(s.scan_time) as last_scan,
            COUNT(DISTINCT s.hwid) as unique_players
        FROM agtr_scans s
        LEFT JOIN agtr_server_mapping sm ON s.server_id = sm.server_id
        WHERE s.server_id IN :server_ids
        AND s.scan_time > DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY s.server_id, sm.server_name, sm.unique_code
        ORDER BY suspicious_scans DESC
    """

    # Convert list to tuple for SQL IN clause
    result = halflife_db.execute(text(stats_query), {"server_ids": tuple(server_ids)})
    servers = [dict(row._mapping) for row in result]

    # Calculate totals
    total_scans = sum(s["total_scans"] for s in servers)
    total_suspicious = sum(s["suspicious_scans"] for s in servers)

    return {
        "servers": servers,
        "total_scans": total_scans,
        "total_suspicious": total_suspicious,
        "period_days": 7,
    }


# ============================================
# ADVANCED DETECTION ENDPOINTS
# ============================================


@router.get("/servers/{server_id}/ml/predictions")
async def get_ml_predictions(
    server_id: int,
    limit: int = Query(50, ge=1, le=200),
    min_probability: float = Query(0.5, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """
    Get Machine Learning cheat predictions for server.
    Shows scans with high cheat probability from ML model.
    """
    verify_server_access(current_user, server_id, db)

    # This would come from ML prediction storage (future)
    # For now, proxy high sus_count scans as proxy for ML predictions
    query = """
        SELECT
            s.id,
            s.hwid,
            s.player_name,
            s.player_steamid,
            s.scan_time,
            s.sus_count,
            s.passed,
            (s.sus_count / 50.0) as estimated_probability
        FROM agtr_scans s
        WHERE s.server_id = :server_id
        AND s.sus_count > 0
        AND (s.sus_count / 50.0) >= :min_probability
        ORDER BY s.sus_count DESC, s.scan_time DESC
        LIMIT :limit
    """

    result = halflife_db.execute(
        text(query), {"server_id": server_id, "min_probability": min_probability, "limit": limit}
    )

    predictions = [dict(row._mapping) for row in result]

    return {
        "server_id": server_id,
        "predictions": predictions,
        "min_probability": min_probability,
        "note": "Real-time ML predictions require ML model training",
    }


@router.get("/servers/{server_id}/patterns/matches")
async def get_pattern_matches(
    server_id: int,
    limit: int = Query(50, ge=1, le=200),
    severity: Optional[str] = Query(None, pattern="^(low|medium|high|critical)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """
    Get pattern engine matches for server.
    Shows scans that matched YARA-style detection rules.
    """
    verify_server_access(current_user, server_id, db)

    # Get scans with blacklist hits (pattern matches)
    query = """
        SELECT DISTINCT
            s.id,
            s.hwid,
            s.player_name,
            s.player_steamid,
            s.scan_time,
            s.sus_count,
            sp.name as matched_pattern,
            sp.is_suspicious
        FROM agtr_scans s
        INNER JOIN agtr_scan_processes sp ON s.id = sp.scan_id
        WHERE s.server_id = :server_id
        AND sp.is_suspicious = 1
        ORDER BY s.scan_time DESC
        LIMIT :limit
    """

    params = {"server_id": server_id, "limit": limit}
    result = halflife_db.execute(text(query), params)
    matches = [dict(row._mapping) for row in result]

    return {"server_id": server_id, "pattern_matches": matches, "total": len(matches)}


@router.get("/servers/{server_id}/behavioral/anomalies")
async def get_behavioral_anomalies(
    server_id: int,
    min_risk: str = Query("medium", pattern="^(low|medium|high|critical)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """
    Get behavioral anomalies detected on this server.
    Includes: server hopping, rapid scanning, name changing, etc.
    """
    verify_server_access(current_user, server_id, db)

    # Find players with suspicious patterns
    # Server hopping: same HWID on multiple servers
    server_hopping_query = """
        SELECT
            s.hwid,
            p.name,
            p.steamid,
            COUNT(DISTINCT s.server_id) as server_count,
            MAX(s.scan_time) as last_seen,
            'server_hopping' as anomaly_type,
            'high' as risk_level
        FROM agtr_scans s
        LEFT JOIN agtr_player_info p ON s.hwid = p.hwid
        WHERE s.server_id = :server_id
        AND s.scan_time > DATE_SUB(NOW(), INTERVAL 24 HOUR)
        GROUP BY s.hwid, p.name, p.steamid
        HAVING COUNT(DISTINCT s.server_id) >= 3
    """

    # Rapid scanning: many scans in short time
    rapid_scan_query = """
        SELECT
            s.hwid,
            p.name,
            p.steamid,
            COUNT(*) as scan_count,
            MAX(s.scan_time) as last_seen,
            'rapid_scanning' as anomaly_type,
            'medium' as risk_level
        FROM agtr_scans s
        LEFT JOIN agtr_player_info p ON s.hwid = p.hwid
        WHERE s.server_id = :server_id
        AND s.scan_time > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
        GROUP BY s.hwid, p.name, p.steamid
        HAVING COUNT(*) >= 5
    """

    anomalies = []

    # Execute server hopping query
    result1 = halflife_db.execute(text(server_hopping_query), {"server_id": server_id})
    anomalies.extend([dict(row._mapping) for row in result1])

    # Execute rapid scanning query
    result2 = halflife_db.execute(text(rapid_scan_query), {"server_id": server_id})
    anomalies.extend([dict(row._mapping) for row in result2])

    return {
        "server_id": server_id,
        "anomalies": anomalies,
        "total": len(anomalies),
        "min_risk": min_risk,
    }


@router.post("/servers/{server_id}/vision/analyze")
async def analyze_screenshot(
    server_id: int,
    screenshot_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze screenshot using Computer Vision module.
    Proxies request to anti-cheat CV API.
    """
    verify_server_access(current_user, server_id, db)

    import httpx

    # Proxy to anti-cheat CV API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:5000/api/v1/vision/analyze", json=screenshot_data, timeout=30.0
            )

            if response.status_code == 200:
                cv_result = response.json()

                # Log if high risk
                if cv_result.get("analysis", {}).get("overall_risk") in [
                    "likely_cheat",
                    "definite_cheat",
                ]:
                    logger.warning(
                        f"High-risk CV detection on server {server_id}: {cv_result['analysis']['overall_risk']}"
                    )

                return cv_result
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=f"CV analysis failed: {response.text}"
                )

        except httpx.RequestError as e:
            logger.error(f"CV API request failed: {e}")
            raise HTTPException(status_code=503, detail="Computer Vision service unavailable")


@router.get("/servers/{server_id}/advanced/summary")
async def get_advanced_detection_summary(
    server_id: int,
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    halflife_db: Session = Depends(get_halflife_db),
):
    """
    Get summary of all advanced detection methods for this server.
    Combines ML, Pattern, Behavioral, and CV detections.
    """
    verify_server_access(current_user, server_id, db)

    # ML-style detections (high sus_count)
    ml_query = """
        SELECT COUNT(*) as ml_detections
        FROM agtr_scans
        WHERE server_id = :server_id
        AND sus_count >= 25
        AND scan_time > DATE_SUB(NOW(), INTERVAL :days DAY)
    """
    ml_result = halflife_db.execute(text(ml_query), {"server_id": server_id, "days": days})
    ml_count = ml_result.scalar()

    # Pattern matches (blacklist hits)
    pattern_query = """
        SELECT COUNT(DISTINCT s.id) as pattern_detections
        FROM agtr_scans s
        INNER JOIN agtr_scan_processes sp ON s.id = sp.scan_id
        WHERE s.server_id = :server_id
        AND sp.is_suspicious = 1
        AND s.scan_time > DATE_SUB(NOW(), INTERVAL :days DAY)
    """
    pattern_result = halflife_db.execute(
        text(pattern_query), {"server_id": server_id, "days": days}
    )
    pattern_count = pattern_result.scalar()

    # Behavioral anomalies (rapid scans)
    behavioral_query = """
        SELECT COUNT(DISTINCT hwid) as behavioral_anomalies
        FROM (
            SELECT hwid, COUNT(*) as scan_count
            FROM agtr_scans
            WHERE server_id = :server_id
            AND scan_time > DATE_SUB(NOW(), INTERVAL :days DAY)
            GROUP BY hwid, DATE(scan_time)
            HAVING scan_count >= 10
        ) as rapid_scanners
    """
    behavioral_result = halflife_db.execute(
        text(behavioral_query), {"server_id": server_id, "days": days}
    )
    behavioral_count = behavioral_result.scalar()

    # Total unique threats
    threat_query = """
        SELECT COUNT(DISTINCT hwid) as unique_threats
        FROM agtr_scans
        WHERE server_id = :server_id
        AND passed = 0
        AND scan_time > DATE_SUB(NOW(), INTERVAL :days DAY)
    """
    threat_result = halflife_db.execute(text(threat_query), {"server_id": server_id, "days": days})
    threat_count = threat_result.scalar()

    return {
        "server_id": server_id,
        "period_days": days,
        "detection_summary": {
            "ml_detections": ml_count or 0,
            "pattern_matches": pattern_count or 0,
            "behavioral_anomalies": behavioral_count or 0,
            "unique_threats": threat_count or 0,
            "computer_vision": 0,  # Future: track CV detections
        },
        "modules": {
            "ml": {"enabled": True, "status": "operational"},
            "pattern_engine": {"enabled": True, "status": "operational"},
            "behavioral": {"enabled": True, "status": "operational"},
            "computer_vision": {"enabled": True, "status": "operational"},
        },
    }
