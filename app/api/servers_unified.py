"""
AGTR Merkezi - Unified Server Management API
Combines legacy servers.py and server_v2.py into clean, maintainable API
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.common import (
    APIError,
    BadRequestError,
    NotFoundError,
    log_api_call,
    log_api_error,
    success_response,
    validate_server_ownership,
)
from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import GameServer, ServerPackage, ServerStatus, User
from app.services import RCONService, ServerControlService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/servers", tags=["Server Management"])


# ============================================
# Response Models
# ============================================


class ServerResponse(BaseModel):
    """Standardized server response"""

    id: int
    name: str
    ip: str
    port: int
    game: str
    status: str
    current_players: int = 0
    max_players: int = 32
    map: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServerDetailResponse(ServerResponse):
    """Detailed server response"""

    rcon_password: Optional[str] = None
    ftp_username: Optional[str] = None
    unique_code: str
    owner_id: int


class RCONRequest(BaseModel):
    """RCON command request"""

    command: str = Field(..., min_length=1, max_length=500)


class RCONResponse(BaseModel):
    """RCON command response"""

    success: bool
    output: Optional[str] = None
    error: Optional[str] = None


class PlayerInfo(BaseModel):
    """Player information"""

    slot: int
    name: str
    steamid: Optional[str] = None
    time: int
    score: Optional[int] = None


# ============================================
# Server Lifecycle Endpoints
# ============================================


@router.get("/my", response_model=List[ServerResponse])
async def get_my_servers(
    current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)
):
    """Get user's servers"""
    try:
        log_api_call("get_my_servers", current_user.id)

        servers = (
            db.query(GameServer)
            .filter(GameServer.owner_id == current_user.id)
            .order_by(GameServer.created_at.desc())
            .all()
        )

        return servers

    except Exception as e:
        log_api_error("get_my_servers", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}", response_model=ServerDetailResponse)
async def get_server(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get server details"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()

        if not server:
            raise NotFoundError("Sunucu bulunamadı")

        validate_server_ownership(server, current_user)

        return server

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_server", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/start")
async def start_server(
    server_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Start server"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()

        if not server:
            raise NotFoundError("Sunucu bulunamadı")

        validate_server_ownership(server, current_user)

        if server.status == ServerStatus.RUNNING:
            raise BadRequestError("Sunucu zaten çalışıyor")

        # Use ServerControlService
        control_service = ServerControlService(db)
        result = await control_service.start_server(server)

        if result:
            return success_response(message="Sunucu başlatılıyor")
        else:
            raise HTTPException(status_code=500, detail="Sunucu başlatılamadı")

    except APIError:
        raise
    except Exception as e:
        log_api_error("start_server", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/stop")
async def stop_server(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Stop server"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()

        if not server:
            raise NotFoundError("Sunucu bulunamadı")

        validate_server_ownership(server, current_user)

        if server.status != ServerStatus.RUNNING:
            raise BadRequestError("Sunucu çalışmıyor")

        control_service = ServerControlService(db)
        result = await control_service.stop_server(server)

        if result:
            return success_response(message="Sunucu durduruluyor")
        else:
            raise HTTPException(status_code=500, detail="Sunucu durdurulamadı")

    except APIError:
        raise
    except Exception as e:
        log_api_error("stop_server", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/restart")
async def restart_server(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Restart server"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()

        if not server:
            raise NotFoundError("Sunucu bulunamadı")

        validate_server_ownership(server, current_user)

        control_service = ServerControlService(db)
        result = await control_service.restart_server(server)

        if result:
            return success_response(message="Sunucu yeniden başlatılıyor")
        else:
            raise HTTPException(status_code=500, detail="Sunucu yeniden başlatılamadı")

    except APIError:
        raise
    except Exception as e:
        log_api_error("restart_server", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# RCON Endpoints
# ============================================


@router.post("/{server_id}/rcon", response_model=RCONResponse)
async def execute_rcon_command(
    server_id: int,
    request: RCONRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Execute RCON command"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()

        if not server:
            raise NotFoundError("Sunucu bulunamadı")

        validate_server_ownership(server, current_user)

        if server.status != ServerStatus.RUNNING:
            raise BadRequestError("Sunucu çalışmıyor")

        # Use RCONService
        rcon_service = RCONService()
        result = await rcon_service.execute_command(
            server.ip, server.port, server.rcon_password, request.command
        )

        return RCONResponse(success=True, output=result)

    except APIError:
        raise
    except Exception as e:
        log_api_error("execute_rcon_command", e, current_user.id)
        return RCONResponse(success=False, error=str(e))


@router.get("/{server_id}/players", response_model=List[PlayerInfo])
async def get_server_players(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get server players via RCON"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()

        if not server:
            raise NotFoundError("Sunucu bulunamadı")

        validate_server_ownership(server, current_user)

        if server.status != ServerStatus.RUNNING:
            return []

        rcon_service = RCONService()
        players = await rcon_service.get_players(server.ip, server.port, server.rcon_password)

        return players

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_server_players", e, current_user.id)
        return []


@router.post("/{server_id}/players/{slot}/kick")
async def kick_player(
    server_id: int,
    slot: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Kick player from server"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()

        if not server:
            raise NotFoundError("Sunucu bulunamadı")

        validate_server_ownership(server, current_user)

        if server.status != ServerStatus.RUNNING:
            raise BadRequestError("Sunucu çalışmıyor")

        rcon_service = RCONService()
        result = await rcon_service.execute_command(
            server.ip, server.port, server.rcon_password, f"kick #{slot}"
        )

        return success_response(message="Oyuncu kicklendi")

    except APIError:
        raise
    except Exception as e:
        log_api_error("kick_player", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Package & Ordering Endpoints
# ============================================


@router.get("/packages", response_model=List[dict])
async def get_packages(db: Session = Depends(get_db)):
    """Get available server packages"""
    try:
        packages = (
            db.query(ServerPackage)
            .filter(ServerPackage.is_active == True)
            .order_by(ServerPackage.price_monthly)
            .all()
        )

        return [
            {
                "id": pkg.id,
                "name": pkg.name,
                "description": pkg.description,
                "price": pkg.price_monthly,
                "max_slots": pkg.slots,
                "ram_mb": 0,  # Not in model
                "disk_gb": 0,  # Not in model
                "duration": 30,  # Default monthly
                "is_popular": pkg.is_popular,
            }
            for pkg in packages
        ]

    except Exception as e:
        log_api_error("get_packages", e)
        raise HTTPException(status_code=500, detail=str(e))
