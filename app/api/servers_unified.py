"""
AGTR Merkezi - Unified Server Management API
Combines legacy servers.py and server_v2.py into clean, maintainable API
"""

import logging
from datetime import datetime, timedelta
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
from app.core.config import settings
from app.core.security import (
    generate_rcon_password,
    generate_reference_code,
    get_current_user_required,
)
from app.models.connection import get_db
from app.models.database import (
    GameServer,
    Payment,
    PaymentStatus,
    ServerPackage,
    ServerStatus,
    User,
)
from app.services import RCONService, ServerControlService
from app.services.port_pool_manager import PortPoolManager

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


class OrderRequest(BaseModel):
    """Server order request"""

    package_id: int
    server_name: str = Field(..., min_length=3, max_length=50)
    location: Optional[str] = None  # Future: server location selection
    duration: int = Field(default=1, ge=1, le=12)  # months
    auto_renew: bool = False


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


@router.get("/packages", response_model=List[dict])
async def get_packages(db: Session = Depends(get_db)):
    """Get available server packages"""
    logger.info("=== get_packages called from servers_unified ===")
    try:
        logger.info("Querying ServerPackage from database")
        packages = (
            db.query(ServerPackage)
            .filter(ServerPackage.is_active.is_(True))
            .order_by(ServerPackage.price_monthly)
            .all()
        )

        logger.info(f"Found {len(packages)} packages")

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
        logger.error(f"Error in get_packages: {e}", exc_info=True)
        log_api_error("get_packages", e)
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
        await rcon_service.execute_command(
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
# NOTE: /packages endpoint moved above /{server_id} to avoid route conflict


@router.post("/order")
async def order_server(
    data: OrderRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Order a new game server"""
    try:
        log_api_call("order_server", current_user.id, {"package_id": data.package_id})

        # Validate package
        package = (
            db.query(ServerPackage)
            .filter(ServerPackage.id == data.package_id, ServerPackage.is_active.is_(True))
            .first()
        )
        if not package:
            raise NotFoundError("Paket bulunamadı")

        # Find available server slot
        pool_manager = PortPoolManager(db)
        slot = pool_manager.acquire_slot()

        if not slot:
            raise BadRequestError(
                "Şu anda müsait sunucu slotu yok. Lütfen daha sonra tekrar deneyin."
            )

        ip, port = slot

        # Calculate price with discount
        discount = 0.0
        if data.duration >= 12:
            discount = getattr(settings, "DISCOUNT_12_MONTH", 0.20)
        elif data.duration >= 6:
            discount = getattr(settings, "DISCOUNT_6_MONTH", 0.15)
        elif data.duration >= 3:
            discount = getattr(settings, "DISCOUNT_3_MONTH", 0.10)

        total_price = package.price_monthly * data.duration * (1 - discount)

        # Create server
        server = GameServer(
            owner_id=current_user.id,
            owner_steam_id=current_user.steam_id if hasattr(current_user, "steam_id") else None,
            name=data.server_name,
            game_type=package.game_type,
            ip_address=ip,
            port=port,
            slots=package.slots,
            rcon_password=generate_rcon_password(),
            package_id=package.id,
            is_custom_package=False,
            features=package.features,
            status=ServerStatus.PENDING,
            monthly_price=package.price_monthly,
            auto_renew=data.auto_renew,
            unique_code=generate_reference_code("SRV"),
            expires_at=datetime.utcnow() + timedelta(days=data.duration * 30),
        )
        db.add(server)
        db.flush()

        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            amount=total_price,
            status=PaymentStatus.PENDING,
            reference_code=generate_reference_code("PAY"),
            description=f"{package.name} - {data.duration} Aylık Sunucu",
            server_id=server.id,
            months=data.duration,
        )
        db.add(payment)
        db.commit()

        logger.info(
            f"Server order created: server_id={server.id}, "
            f"payment_id={payment.id}, user_id={current_user.id}"
        )

        return {
            "success": True,
            "server_id": server.id,
            "payment_id": payment.id,
            "reference_code": payment.reference_code,
            "amount": total_price,
            "server_info": {
                "name": server.name,
                "ip": f"{ip}:{port}",
                "slots": server.slots,
                "unique_code": server.unique_code,
            },
        }

    except APIError:
        raise
    except Exception as e:
        log_api_error("order_server", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))
