"""
AGTR Merkezi - Admin Servers Management API
Sunucu yonetimi, control, istatistikler
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import GameServer, GameType, ServerMetrics, ServerStatus, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/servers", tags=["Admin Servers"])


# ==================== PYDANTIC MODELS ====================


class ServerActionRequest(BaseModel):
    action: str  # start, stop, restart, delete


# ==================== ENDPOINTS ====================


@router.get("")
async def get_servers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    owner_id: Optional[int] = None,
    game_type: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|name|status)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    Sunucu listesi - pagination, arama, filtreleme
    """
    query = db.query(GameServer).filter(GameServer.status != ServerStatus.DELETED)

    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(GameServer.name.ilike(search_term), GameServer.ip_address.ilike(search_term))
        )

    # Status filter
    if status_filter and status_filter != "all":
        try:
            status_enum = ServerStatus(status_filter)
            query = query.filter(GameServer.status == status_enum)
        except ValueError:
            pass

    # Owner filter
    if owner_id:
        query = query.filter(GameServer.owner_id == owner_id)

    # Game type filter
    if game_type and game_type != "all":
        try:
            game_enum = GameType(game_type)
            query = query.filter(GameServer.game_type == game_enum)
        except ValueError:
            pass

    # Total count
    total = query.count()

    # Sorting
    sort_column = getattr(GameServer, sort_by, GameServer.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    offset = (page - 1) * limit
    servers = query.offset(offset).limit(limit).all()

    # Get owners (batch query to avoid N+1)
    owner_ids = list(set([s.owner_id for s in servers if s.owner_id]))
    owners_map = {}
    if owner_ids:
        owners = db.query(User).filter(User.id.in_(owner_ids)).all()
        owners_map = {u.id: u for u in owners}

    # Get latest metrics (batch query)
    server_ids = [s.id for s in servers]
    metrics_map = {}
    if server_ids:
        # Get latest metric for each server
        latest_metrics = (
            db.query(ServerMetrics)
            .filter(ServerMetrics.server_id.in_(server_ids))
            .order_by(ServerMetrics.timestamp.desc())
            .all()
        )

        # Group by server_id, keep only latest
        for metric in latest_metrics:
            if metric.server_id not in metrics_map:
                metrics_map[metric.server_id] = metric

    # Format response
    servers_data = []
    for s in servers:
        owner = owners_map.get(s.owner_id)
        metric = metrics_map.get(s.id)

        # Calculate uptime
        uptime_str = "N/A"
        if s.status == ServerStatus.RUNNING and s.last_started:
            uptime_delta = datetime.utcnow() - s.last_started
            days = uptime_delta.days
            hours = uptime_delta.seconds // 3600
            if days > 0:
                uptime_str = f"{days}d {hours}h"
            else:
                uptime_str = f"{hours}h"

        servers_data.append(
            {
                "id": s.id,
                "name": s.name,
                "owner_id": s.owner_id,
                "owner_username": owner.username if owner else "Unknown",
                "ip_address": s.ip_address,
                "port": s.port,
                "game_type": s.game_type.value if s.game_type else None,
                "current_map": s.current_map,
                "current_players": metric.player_count if metric else 0,
                "max_players": s.max_players,
                "cpu_usage": metric.cpu_usage if metric else 0,
                "ram_usage": metric.ram_usage if metric else 0,
                "status": s.status.value,
                "uptime": uptime_str,
                "last_started": s.last_started.isoformat() if s.last_started else None,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
        )

    return {
        "servers": servers_data,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 1,
    }


@router.get("/stats")
async def get_server_stats(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Sunucu istatistikleri ozeti"""
    # Total servers
    total_servers = (
        db.query(func.count(GameServer.id))
        .filter(GameServer.status != ServerStatus.DELETED)
        .scalar()
        or 0
    )

    # Running servers
    running_servers = (
        db.query(func.count(GameServer.id))
        .filter(GameServer.status == ServerStatus.RUNNING)
        .scalar()
        or 0
    )

    # Stopped servers
    stopped_servers = (
        db.query(func.count(GameServer.id))
        .filter(GameServer.status == ServerStatus.STOPPED)
        .scalar()
        or 0
    )

    # Error servers
    error_servers = (
        db.query(func.count(GameServer.id)).filter(GameServer.status == ServerStatus.ERROR).scalar()
        or 0
    )

    # Total players online (sum of all running servers)
    latest_metrics = (
        db.query(ServerMetrics.server_id, ServerMetrics.player_count)
        .filter(
            ServerMetrics.server_id.in_(
                db.query(GameServer.id).filter(GameServer.status == ServerStatus.RUNNING)
            )
        )
        .order_by(ServerMetrics.timestamp.desc())
        .all()
    )

    # Get unique server metrics (latest per server)
    server_player_counts = {}
    for metric in latest_metrics:
        if metric.server_id not in server_player_counts:
            server_player_counts[metric.server_id] = metric.player_count

    total_players = sum(server_player_counts.values())

    # Servers by game type
    game_type_dist = (
        db.query(GameServer.game_type, func.count(GameServer.id))
        .filter(GameServer.status != ServerStatus.DELETED)
        .group_by(GameServer.game_type)
        .all()
    )

    game_types = {gt.value: count for gt, count in game_type_dist if gt}

    # New servers (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_servers_week = (
        db.query(func.count(GameServer.id)).filter(GameServer.created_at >= week_ago).scalar() or 0
    )

    return {
        "total_servers": total_servers,
        "running_servers": running_servers,
        "stopped_servers": stopped_servers,
        "error_servers": error_servers,
        "total_players_online": total_players,
        "game_type_distribution": game_types,
        "new_servers_this_week": new_servers_week,
        "uptime_percentage": (
            round((running_servers / total_servers * 100), 1) if total_servers > 0 else 0
        ),
    }


@router.get("/{server_id}")
async def get_server_detail(
    server_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """Sunucu detayli bilgiler"""
    server = db.query(GameServer).filter(GameServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")

    # Owner info
    owner = db.query(User).filter(User.id == server.owner_id).first()

    # Latest metrics
    latest_metric = (
        db.query(ServerMetrics)
        .filter(ServerMetrics.server_id == server_id)
        .order_by(ServerMetrics.timestamp.desc())
        .first()
    )

    # Uptime
    uptime_str = "N/A"
    if server.status == ServerStatus.RUNNING and server.last_started:
        uptime_delta = datetime.utcnow() - server.last_started
        days = uptime_delta.days
        hours = uptime_delta.seconds // 3600
        minutes = (uptime_delta.seconds % 3600) // 60
        uptime_str = f"{days}d {hours}h {minutes}m"

    return {
        "id": server.id,
        "name": server.name,
        "owner": {
            "id": owner.id if owner else None,
            "username": owner.username if owner else "Unknown",
            "email": owner.email if owner else None,
        },
        "ip_address": server.ip_address,
        "port": server.port,
        "game_type": server.game_type.value if server.game_type else None,
        "current_map": server.current_map,
        "max_players": server.max_players,
        "status": server.status.value,
        "rcon_password": server.rcon_password,
        "server_cfg": server.server_cfg,
        "uptime": uptime_str,
        "last_started": server.last_started.isoformat() if server.last_started else None,
        "created_at": server.created_at.isoformat() if server.created_at else None,
        "updated_at": server.updated_at.isoformat() if server.updated_at else None,
        "metrics": (
            {
                "player_count": latest_metric.player_count if latest_metric else 0,
                "cpu_usage": latest_metric.cpu_usage if latest_metric else 0,
                "ram_usage": latest_metric.ram_usage if latest_metric else 0,
                "network_in": latest_metric.network_in if latest_metric else 0,
                "network_out": latest_metric.network_out if latest_metric else 0,
            }
            if latest_metric
            else None
        ),
    }


@router.post("/{server_id}/action")
async def server_action(
    server_id: int,
    data: ServerActionRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Sunucu kontrolu - start/stop/restart/delete"""
    server = db.query(GameServer).filter(GameServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")

    action = data.action.lower()

    if action == "start":
        if server.status == ServerStatus.RUNNING:
            raise HTTPException(status_code=400, detail="Sunucu zaten calisiyor")

        server.status = ServerStatus.RUNNING
        server.last_started = datetime.utcnow()
        logger.info(f"Admin {admin.username} started server {server.name} (ID: {server_id})")
        message = "Sunucu baslatildi"

    elif action == "stop":
        if server.status == ServerStatus.STOPPED:
            raise HTTPException(status_code=400, detail="Sunucu zaten durdurulmus")

        server.status = ServerStatus.STOPPED
        logger.info(f"Admin {admin.username} stopped server {server.name} (ID: {server_id})")
        message = "Sunucu durduruldu"

    elif action == "restart":
        server.status = ServerStatus.RUNNING
        server.last_started = datetime.utcnow()
        logger.info(f"Admin {admin.username} restarted server {server.name} (ID: {server_id})")
        message = "Sunucu yeniden baslatildi"

    elif action == "delete":
        server.status = ServerStatus.DELETED
        logger.warning(f"Admin {admin.username} deleted server {server.name} (ID: {server_id})")
        message = "Sunucu silindi"

    else:
        raise HTTPException(status_code=400, detail="Gecersiz islem")

    server.updated_at = datetime.utcnow()
    db.commit()

    return {"message": message}


@router.delete("/{server_id}")
async def delete_server(
    server_id: int,
    permanent: bool = False,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Sunucuyu sil"""
    server = db.query(GameServer).filter(GameServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")

    if permanent:
        # Permanent delete
        db.delete(server)
        logger.warning(
            f"Admin {admin.username} permanently deleted server {server.name} (ID: {server_id})"
        )
        message = "Sunucu kalici olarak silindi"
    else:
        # Soft delete
        server.status = ServerStatus.DELETED
        server.updated_at = datetime.utcnow()
        logger.info(f"Admin {admin.username} soft deleted server {server.name} (ID: {server_id})")
        message = "Sunucu silindi"

    db.commit()

    return {"message": message}
