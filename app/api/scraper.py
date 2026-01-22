"""
AGTR Merkezi - Server Scraper API
Sunucu tarama ve topluluk sunucu yonetimi
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import (
    CommunityServer,
    ServerScanLog,
    GameType,
    User,
)
from app.services.server_scraper import (
    ServerScraper,
    GameTypeEnum,
    run_scraper_task,
    save_scraped_servers_to_db,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== SCHEMAS ====================

class ServerResponse(BaseModel):
    id: int
    ip: str
    port: int
    address: str
    name: str
    game_type: str
    current_map: str
    players: int
    max_players: int
    ping: int
    is_online: bool
    password_protected: bool
    country: Optional[str]
    is_featured: bool
    last_seen: Optional[str]

    class Config:
        from_attributes = True


class ScanRequest(BaseModel):
    game_types: List[str] = ["ag", "cs16", "hldm"]
    include_community: bool = True


class SingleServerQuery(BaseModel):
    ip: str
    port: int = Field(..., ge=1, le=65535)


# ==================== PUBLIC ENDPOINTS ====================

@router.get("/servers")
async def get_community_servers(
    game_type: Optional[str] = Query(None, description="Oyun turu: ag, cs16, hldm"),
    country: Optional[str] = Query(None, description="Ulke kodu: TR, US, DE"),
    online_only: bool = Query(True, description="Sadece online sunucular"),
    has_players: bool = Query(False, description="Oyunculu sunucular"),
    search: Optional[str] = Query(None, description="Sunucu adi arama"),
    sort_by: str = Query("players", description="Siralama: players, ping, name"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=10, le=100),
    db: Session = Depends(get_db)
):
    """
    Topluluk sunucularini listele (Public)
    """
    query = db.query(CommunityServer)

    # Filtreler
    if game_type:
        try:
            gt = GameType(game_type.lower())
            query = query.filter(CommunityServer.game_type == gt)
        except ValueError:
            pass

    if country:
        query = query.filter(CommunityServer.country == country.upper())

    if online_only:
        query = query.filter(CommunityServer.is_online == True)

    if has_players:
        query = query.filter(CommunityServer.current_players > 0)

    if search:
        query = query.filter(CommunityServer.name.ilike(f"%{search}%"))

    # Siralama
    if sort_by == "players":
        query = query.order_by(desc(CommunityServer.current_players))
    elif sort_by == "ping":
        query = query.order_by(CommunityServer.ping)
    elif sort_by == "name":
        query = query.order_by(CommunityServer.name)
    else:
        query = query.order_by(desc(CommunityServer.current_players))

    # Featured sunucular her zaman uste
    query = query.order_by(desc(CommunityServer.is_featured))

    # Toplam
    total = query.count()

    # Sayfalama
    offset = (page - 1) * per_page
    servers = query.offset(offset).limit(per_page).all()

    return {
        "servers": [
            {
                "id": s.id,
                "ip": s.ip_address,
                "port": s.port,
                "address": s.address,
                "name": s.name or f"Server {s.address}",
                "game_type": s.game_type.value,
                "current_map": s.current_map or "Unknown",
                "players": s.current_players,
                "max_players": s.max_players,
                "ping": s.ping,
                "is_online": s.is_online,
                "password_protected": s.password_protected,
                "country": s.country,
                "is_featured": s.is_featured,
                "last_seen": s.last_seen.isoformat() if s.last_seen else None
            }
            for s in servers
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    }


@router.get("/servers/stats")
async def get_server_stats(db: Session = Depends(get_db)):
    """
    Sunucu istatistikleri (Public)
    """
    # Toplam sunucular
    total = db.query(CommunityServer).count()
    online = db.query(CommunityServer).filter(CommunityServer.is_online == True).count()

    # Toplam oyuncular
    total_players = db.query(func.sum(CommunityServer.current_players)).filter(
        CommunityServer.is_online == True
    ).scalar() or 0

    # Oyun turune gore
    by_game = {}
    for gt in GameType:
        count = db.query(CommunityServer).filter(
            CommunityServer.game_type == gt,
            CommunityServer.is_online == True
        ).count()
        players = db.query(func.sum(CommunityServer.current_players)).filter(
            CommunityServer.game_type == gt,
            CommunityServer.is_online == True
        ).scalar() or 0
        by_game[gt.value] = {
            "servers": count,
            "players": players
        }

    # Son tarama
    last_scan = db.query(ServerScanLog).order_by(
        desc(ServerScanLog.completed_at)
    ).first()

    return {
        "total_servers": total,
        "online_servers": online,
        "total_players": total_players,
        "by_game_type": by_game,
        "last_scan": {
            "time": last_scan.completed_at.isoformat() if last_scan and last_scan.completed_at else None,
            "found": last_scan.online_found if last_scan else 0
        } if last_scan else None
    }


@router.get("/servers/{server_id}")
async def get_server_detail(
    server_id: int,
    db: Session = Depends(get_db)
):
    """
    Tek sunucu detayi + canli sorgu
    """
    server = db.query(CommunityServer).filter(CommunityServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")

    # Canli sorgu yap
    scraper = ServerScraper(timeout=2.0)
    live_data = None

    try:
        live_data = await scraper.query_server(server.ip_address, server.port)
        if live_data:
            # DB guncelle
            server.current_players = live_data.players
            server.current_map = live_data.map
            server.ping = live_data.ping
            server.is_online = True
            server.last_seen = datetime.utcnow()
            server.last_query = datetime.utcnow()
            server.total_queries += 1
            db.commit()
    except Exception as e:
        logger.warning(f"Canli sorgu hatasi: {e}")
    finally:
        await scraper.close()

    return {
        "id": server.id,
        "ip": server.ip_address,
        "port": server.port,
        "address": server.address,
        "name": server.name,
        "game_type": server.game_type.value,
        "game_dir": server.game_dir,
        "current_map": server.current_map,
        "players": server.current_players,
        "max_players": server.max_players,
        "ping": server.ping,
        "is_online": server.is_online,
        "password_protected": server.password_protected,
        "country": server.country,
        "is_featured": server.is_featured,
        "is_verified": server.is_verified,
        "uptime_percent": server.uptime_percent,
        "first_seen": server.first_seen.isoformat() if server.first_seen else None,
        "last_seen": server.last_seen.isoformat() if server.last_seen else None,
        "player_list": live_data.player_list if live_data else []
    }


@router.post("/servers/query")
async def query_single_server(
    data: SingleServerQuery,
    db: Session = Depends(get_db)
):
    """
    Tek sunucuyu canli sorgula (Public)
    """
    scraper = ServerScraper(timeout=3.0)

    try:
        result = await scraper.query_server(data.ip, data.port)
        if not result:
            raise HTTPException(status_code=404, detail="Sunucu yanitlamiyor")

        return {
            "ip": result.ip,
            "port": result.port,
            "address": result.address,
            "name": result.name,
            "map": result.map,
            "players": result.players,
            "max_players": result.max_players,
            "ping": result.ping,
            "game_type": result.game_type.value,
            "password_protected": result.password_protected,
            "player_list": result.player_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


# ==================== ADMIN ENDPOINTS ====================

@router.post("/admin/scan")
async def trigger_scan(
    data: ScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Manuel tarama baslat (Admin)
    """
    # Admin kontrolu
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Yetkisiz islem")

    # Scan log olustur
    scan_log = ServerScanLog(
        scan_type="manual",
        game_types=data.game_types,
        triggered_by=f"user:{current_user.id}"
    )
    db.add(scan_log)
    db.commit()

    # Background task olarak calistir
    async def run_scan():
        try:
            start_time = datetime.utcnow()
            result = await run_scraper_task(data.game_types, db)

            # Log guncelle
            scan_log.total_scanned = result.get("total_found", 0)
            scan_log.online_found = result.get("total_found", 0)
            scan_log.new_servers = result.get("db_stats", {}).get("added", 0)
            scan_log.updated_servers = result.get("db_stats", {}).get("updated", 0)
            scan_log.completed_at = datetime.utcnow()
            scan_log.duration_seconds = (datetime.utcnow() - start_time).total_seconds()
            db.commit()

        except Exception as e:
            logger.error(f"Scan hatasi: {e}")
            scan_log.error_count = 1
            scan_log.error_messages = [str(e)]
            scan_log.completed_at = datetime.utcnow()
            db.commit()

    background_tasks.add_task(run_scan)

    return {
        "success": True,
        "message": "Tarama baslatildi",
        "scan_id": scan_log.id
    }


@router.get("/admin/scan-history")
async def get_scan_history(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Tarama gecmisi (Admin)
    """
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Yetkisiz islem")

    logs = db.query(ServerScanLog).order_by(
        desc(ServerScanLog.started_at)
    ).limit(limit).all()

    return {
        "scans": [
            {
                "id": log.id,
                "type": log.scan_type,
                "game_types": log.game_types,
                "total_scanned": log.total_scanned,
                "online_found": log.online_found,
                "new_servers": log.new_servers,
                "updated_servers": log.updated_servers,
                "duration": log.duration_seconds,
                "triggered_by": log.triggered_by,
                "started_at": log.started_at.isoformat() if log.started_at else None,
                "completed_at": log.completed_at.isoformat() if log.completed_at else None
            }
            for log in logs
        ]
    }


@router.put("/admin/servers/{server_id}")
async def update_server(
    server_id: int,
    is_featured: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Sunucu bilgilerini guncelle (Admin)
    """
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Yetkisiz islem")

    server = db.query(CommunityServer).filter(CommunityServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")

    if is_featured is not None:
        server.is_featured = is_featured
    if is_verified is not None:
        server.is_verified = is_verified
    if country is not None:
        server.country = country.upper()[:3]

    db.commit()

    return {"success": True, "message": "Sunucu guncellendi"}


@router.delete("/admin/servers/{server_id}")
async def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Sunucuyu sil (Admin)
    """
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Yetkisiz islem")

    server = db.query(CommunityServer).filter(CommunityServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")

    db.delete(server)
    db.commit()

    return {"success": True, "message": "Sunucu silindi"}


@router.post("/admin/servers/add")
async def add_server_manually(
    ip: str,
    port: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Manuel sunucu ekle (Admin)
    """
    if not check_admin_role(current_user):
        raise HTTPException(status_code=403, detail="Yetkisiz islem")

    # Mevcut kontrol
    existing = db.query(CommunityServer).filter(
        CommunityServer.ip_address == ip,
        CommunityServer.port == port
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Sunucu zaten mevcut")

    # Sunucuyu sorgula
    scraper = ServerScraper(timeout=3.0)
    try:
        result = await scraper.query_server(ip, port)
        if not result:
            raise HTTPException(status_code=400, detail="Sunucu yanitlamiyor")

        # Oyun turunu belirle
        game_type_map = {
            GameTypeEnum.AG: GameType.AG,
            GameTypeEnum.CS16: GameType.CS16,
            GameTypeEnum.HLDM: GameType.HLDM,
        }
        game_type = game_type_map.get(result.game_type, GameType.HLDM)

        # Veritabanina ekle
        server = CommunityServer(
            ip_address=ip,
            port=port,
            name=result.name,
            game_type=game_type,
            game_dir=result.game_dir,
            current_map=result.map,
            current_players=result.players,
            max_players=result.max_players,
            ping=result.ping,
            password_protected=result.password_protected,
            source="manual",
            is_verified=True
        )
        db.add(server)
        db.commit()

        return {
            "success": True,
            "message": "Sunucu eklendi",
            "server_id": server.id
        }

    finally:
        await scraper.close()


# ==================== SCHEDULED TASK HELPER ====================

async def scheduled_scan_task(db: Session):
    """
    Zamanlanmis tarama gorevi - scheduler'dan cagrilir
    """
    logger.info("Zamanlanmis sunucu taramasi basliyor...")

    scan_log = ServerScanLog(
        scan_type="scheduled",
        game_types=["ag", "cs16", "hldm"],
        triggered_by="scheduler"
    )
    db.add(scan_log)
    db.commit()

    try:
        start_time = datetime.utcnow()
        result = await run_scraper_task(["ag", "cs16", "hldm"], db)

        scan_log.total_scanned = result.get("total_found", 0)
        scan_log.online_found = result.get("total_found", 0)
        scan_log.new_servers = result.get("db_stats", {}).get("added", 0)
        scan_log.updated_servers = result.get("db_stats", {}).get("updated", 0)
        scan_log.completed_at = datetime.utcnow()
        scan_log.duration_seconds = (datetime.utcnow() - start_time).total_seconds()
        db.commit()

        logger.info(f"Tarama tamamlandi: {scan_log.online_found} sunucu bulundu")

    except Exception as e:
        logger.error(f"Zamanlanmis tarama hatasi: {e}")
        scan_log.error_count = 1
        scan_log.error_messages = [str(e)]
        scan_log.completed_at = datetime.utcnow()
        db.commit()


# ==================== UTILITY FUNCTIONS ====================

def check_admin_role(user: User) -> bool:
    """Admin yetkisi kontrol"""
    from app.models.database import UserRole
    return user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]
