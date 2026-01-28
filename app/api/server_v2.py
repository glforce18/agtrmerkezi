"""
AGTR Merkezi v6.0 - Server Management API v2
Sunucu yasam dongusu, kontrol, RCON, admin ve config yonetimi
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import (
    GameServer,
    ServerBan,
    ServerInstallation,
    ServerQuickCommand,
    ServerStatus,
    User,
)
from app.services import (
    AMXXAdminService,
    RCONService,
    ServerConfigService,
    ServerControlService,
    ServerInstallationService,
)
from app.services.auto_update_service import auto_update_service
from app.services.ddos_protection_service import ddos_protection_service
from app.services.port_pool_manager import PortPoolManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/servers", tags=["Server Management v2"])


# ============================================
# Pydantic Schemas
# ============================================


class ServerCreateRequest(BaseModel):
    """Sunucu olusturma istegi"""

    name: str = Field(..., min_length=3, max_length=100)
    mod_type: str = Field(..., description="ag, ag_openag, cs16, hldm, valve_new")
    port: int = Field(default=27015, ge=27000, le=27999)
    maxplayers: int = Field(default=32, ge=2, le=32)
    rcon_password: Optional[str] = None
    sv_password: Optional[str] = None
    panel_password: Optional[str] = Field(None, description="Panel access password (REQUIRED)")
    admins: Optional[List[dict]] = None


class ServerResponse(BaseModel):
    """Sunucu yaniti"""

    id: int
    unique_code: Optional[str]
    name: str
    game_type: str
    mod_type: Optional[str]
    ip_address: str
    port: int
    status: str
    current_players: int
    max_players: int
    current_map: Optional[str]
    owner_steam_id: Optional[str] = None
    expires_at: Optional[str] = None
    created_at: Optional[str]
    panel_password: Optional[str] = None  # Will contain actual password for verification


class InstallationResponse(BaseModel):
    """Kurulum durumu yaniti"""

    id: int
    server_id: int
    unique_code: str
    status: str
    progress_percent: int
    current_step: Optional[str]
    total_steps: int
    error_message: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]


class ServerStatusResponse(BaseModel):
    """Sunucu durum yaniti"""

    online: bool
    status: str
    players: int
    max_players: int
    map: Optional[str]
    hostname: Optional[str]
    pid: Optional[int]
    cpu_percent: float
    memory_mb: float
    uptime_seconds: int


class RCONRequest(BaseModel):
    """RCON komut istegi"""

    command: str = Field(..., min_length=1, max_length=500)


class RCONResponse(BaseModel):
    """RCON komut yaniti"""

    success: bool
    response: Optional[str]
    error: Optional[str]
    execution_time_ms: int


class PlayerKickRequest(BaseModel):
    """Oyuncu atma istegi"""

    reason: str = Field(default="Kicked by admin", max_length=200)


class PlayerBanRequest(BaseModel):
    """Oyuncu banlama istegi"""

    steam_id: Optional[str] = None
    ip_address: Optional[str] = None
    name: Optional[str] = None
    reason: str = Field(default="Banned by admin", max_length=500)
    duration_minutes: int = Field(default=0, ge=0, description="0 = kalici")


class AdminCreateRequest(BaseModel):
    """Admin ekleme istegi"""

    steam_id: str = Field(..., min_length=10, max_length=50)
    name: Optional[str] = None
    flags: str = Field(default="abcdefghijklmnopqrstu")
    password: Optional[str] = None
    expires_at: Optional[str] = None
    notes: Optional[str] = None


class AdminUpdateRequest(BaseModel):
    """Admin guncelleme istegi"""

    flags: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[str] = None
    notes: Optional[str] = None


class ConfigUpdateRequest(BaseModel):
    """Config guncelleme istegi"""

    content: str


class MapcycleUpdateRequest(BaseModel):
    """Mapcycle guncelleme istegi"""

    maps: List[str]


class MapChangeRequest(BaseModel):
    """Harita degistirme istegi"""

    map_name: str = Field(..., min_length=1, max_length=64)


class SayRequest(BaseModel):
    """Mesaj gonderme istegi"""

    message: str = Field(..., min_length=1, max_length=200)


# ============================================
# Helper Functions
# ============================================


async def verify_server_ownership(server_id: int, user: User, db: Session) -> GameServer:
    """
    Sunucu sahipligini dogrula

    Admin/Superadmin kullanıcılar tüm sunuculara erişebilir
    """
    # Admin bypass - admin kullanıcılar tüm sunuculara erişebilir
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
        return server

    # Normal kullanıcı - sadece kendi sunucusu
    server = (
        db.query(GameServer)
        .filter(GameServer.id == server_id, GameServer.owner_id == user.id)
        .first()
    )

    if not server:
        raise HTTPException(status_code=403, detail="Bu sunucuya erisim izniniz yok")

    return server


def get_client_ip(request: Request) -> str:
    """Istemci IP adresini al"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ============================================
# Server Lifecycle Endpoints
# ============================================


@router.post("/create", response_model=dict)
async def create_server(
    request_data: ServerCreateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Yeni sunucu olustur ve kurulumu baslat

    Kurulum arka planda devam eder, /installation endpoint'i ile takip edilebilir
    """
    # Mod tipi kontrolu
    valid_mods = ["ag", "ag_openag", "cs16", "hldm", "valve_new"]
    if request_data.mod_type not in valid_mods:
        raise HTTPException(400, f"Gecersiz mod tipi. Gecerli: {valid_mods}")

    installation_service = ServerInstallationService(db)

    # Unique code olustur
    unique_code = installation_service.generate_unique_code()

    # Musait IP:PORT slot bul (load balancing ile)
    pool_manager = PortPoolManager(db)
    slot = pool_manager.acquire_slot()

    if not slot:
        raise HTTPException(
            status_code=507, detail="Tum sunucu slotlari dolu. Lutfen daha sonra tekrar deneyin."
        )

    allocated_ip, allocated_port = slot

    # GameServer olustur
    from app.core.security import generate_rcon_password

    server = GameServer(
        owner_id=current_user.id,
        owner_steam_id=current_user.steam_id,  # Steam ID for quick lookup
        name=request_data.name,
        game_type=(
            "HLDM"
            if request_data.mod_type in ["hldm", "valve_new"]
            else ("AG" if "ag" in request_data.mod_type else "CS16")
        ),
        ip_address=allocated_ip,  # PortPoolManager'dan alindi
        port=allocated_port,  # PortPoolManager'dan alindi
        slots=request_data.maxplayers,
        rcon_password=request_data.rcon_password or generate_rcon_password(),
        sv_password=request_data.sv_password,
        unique_code=unique_code,
        mod_type=request_data.mod_type,
        status=ServerStatus.CREATING,
        created_at=datetime.utcnow(),
    )

    db.add(server)
    db.commit()
    db.refresh(server)

    # Kurulum kaydi olustur
    installation = await installation_service.create_installation(
        server_id=server.id,
        user_id=current_user.id,
        mod_type=request_data.mod_type,
        config={
            "hostname": request_data.name,
            "ip": allocated_ip,
            "port": allocated_port,
            "maxplayers": request_data.maxplayers,
            "rcon_password": server.rcon_password,
            "sv_password": request_data.sv_password,
            "admins": request_data.admins or [],
        },
    )

    # Arka planda kurulumu baslat
    async def run_installation():
        config = {
            "hostname": request_data.name,
            "ip": allocated_ip,
            "port": allocated_port,
            "maxplayers": request_data.maxplayers,
            "rcon_password": server.rcon_password,
            "sv_password": request_data.sv_password,
            "admins": request_data.admins or [],
        }
        await installation_service.run_installation(installation.id, config)

    background_tasks.add_task(run_installation)

    return {
        "success": True,
        "server_id": server.id,
        "unique_code": unique_code,
        "installation_id": installation.id,
        "message": "Sunucu olusturuldu, kurulum baslatildi",
    }


@router.get("/my", response_model=List[ServerResponse])
async def get_my_servers(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)
):
    """Kullanicinin sunucularini listele"""
    servers = (
        db.query(GameServer)
        .filter(GameServer.owner_id == current_user.id)
        .order_by(GameServer.created_at.desc())
        .all()
    )

    return [
        ServerResponse(
            id=s.id,
            unique_code=s.unique_code,
            name=s.name,
            game_type=s.game_type.value if s.game_type else "HLDM",
            mod_type=s.mod_type,
            ip_address=s.ip_address,
            port=s.port,
            status=s.status.value if s.status else "unknown",
            current_players=s.current_players or 0,
            max_players=s.slots,
            current_map=s.current_map,
            created_at=s.created_at.isoformat() if s.created_at else None,
            panel_password=s.panel_password,  # Include for frontend check
        )
        for s in servers
    ]


@router.post("/{server_id}/verify-panel-password")
async def verify_panel_password(
    server_id: int,
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Panel şifresini doğrula"""
    server = await verify_server_ownership(server_id, current_user, db)

    # If no password set, always allow
    if not server.panel_password:
        return {"success": True}

    # Check password
    if password_data.get("password") == server.panel_password:
        return {"success": True}
    else:
        raise HTTPException(401, "Yanlış şifre")


@router.get("/search/steam/{steam_id}")
async def get_servers_by_steam_id(
    steam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Steam ID ile sunuculari ara

    Admin veya sunucu sahibi kullanabilir
    """
    # Admin kontrolu veya kendi Steam ID'si
    is_admin = current_user.role in ["admin", "superadmin"]
    is_own_steam = current_user.steam_id == steam_id

    if not is_admin and not is_own_steam:
        raise HTTPException(403, "Bu islem icin yetkiniz yok")

    servers = (
        db.query(GameServer)
        .filter(GameServer.owner_steam_id == steam_id)
        .order_by(GameServer.created_at.desc())
        .all()
    )

    # Sahip bilgisini de getir
    owner = db.query(User).filter(User.steam_id == steam_id).first()

    return {
        "steam_id": steam_id,
        "owner": (
            {
                "id": owner.id,
                "username": owner.username,
                "display_name": owner.display_name,
                "avatar": owner.avatar,
            }
            if owner
            else None
        ),
        "server_count": len(servers),
        "servers": [
            {
                "id": s.id,
                "unique_code": s.unique_code,
                "name": s.name,
                "game_type": s.game_type.value if s.game_type else "HLDM",
                "mod_type": s.mod_type,
                "ip_address": s.ip_address,
                "port": s.port,
                "status": s.status.value if s.status else "unknown",
                "current_players": s.current_players or 0,
                "max_players": s.slots,
                "current_map": s.current_map,
                "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in servers
        ],
    }


@router.get("/search/code/{unique_code}")
async def get_server_by_code(
    unique_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Unique code ile sunucu ara (AGTR-2026-XXXXX)

    Admin veya sunucu sahibi kullanabilir
    """
    server = db.query(GameServer).filter(GameServer.unique_code == unique_code).first()

    if not server:
        raise HTTPException(404, "Sunucu bulunamadi")

    # Yetki kontrolu
    is_admin = current_user.role in ["admin", "superadmin"]
    is_owner = server.owner_id == current_user.id

    if not is_admin and not is_owner:
        raise HTTPException(403, "Bu sunucuya erisim izniniz yok")

    # Sahip bilgisi
    owner = db.query(User).filter(User.id == server.owner_id).first()

    return {
        "server": {
            "id": server.id,
            "unique_code": server.unique_code,
            "name": server.name,
            "game_type": server.game_type.value if server.game_type else "HLDM",
            "mod_type": server.mod_type,
            "ip_address": server.ip_address,
            "port": server.port,
            "status": server.status.value if server.status else "unknown",
            "current_players": server.current_players or 0,
            "max_players": server.slots,
            "current_map": server.current_map,
            "rcon_password": server.rcon_password if is_admin or is_owner else None,
            "expires_at": server.expires_at.isoformat() if server.expires_at else None,
            "created_at": server.created_at.isoformat() if server.created_at else None,
        },
        "owner": (
            {
                "id": owner.id,
                "username": owner.username,
                "display_name": owner.display_name,
                "steam_id": owner.steam_id,
                "avatar": owner.avatar,
            }
            if owner
            else None
        ),
    }


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Sunucu detaylarini al"""
    server = await verify_server_ownership(server_id, current_user, db)

    return ServerResponse(
        id=server.id,
        unique_code=server.unique_code,
        name=server.name,
        game_type=server.game_type.value if server.game_type else "HLDM",
        mod_type=server.mod_type,
        ip_address=server.ip_address,
        port=server.port,
        status=server.status.value if server.status else "unknown",
        current_players=server.current_players or 0,
        max_players=server.slots,
        current_map=server.current_map,
        created_at=server.created_at.isoformat() if server.created_at else None,
    )


@router.delete("/{server_id}")
async def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Sunucuyu sil"""
    server = await verify_server_ownership(server_id, current_user, db)

    # Sunucuyu durdur
    control_service = ServerControlService(db)
    await control_service.stop_server(server_id)

    # Dosyalari sil
    installation_service = ServerInstallationService(db)
    installation_service.delete_server_files(server_id)

    # Veritabanindan sil
    db.delete(server)
    db.commit()

    return {"success": True, "message": "Sunucu silindi"}


# ============================================
# Server Control Endpoints
# ============================================


@router.post("/{server_id}/start")
async def start_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Sunucuyu baslat"""
    await verify_server_ownership(server_id, current_user, db)

    control_service = ServerControlService(db)
    result = await control_service.start_server(server_id)

    if not result["success"]:
        raise HTTPException(400, result["message"])

    return result


@router.post("/{server_id}/stop")
async def stop_server(
    server_id: int,
    graceful: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Sunucuyu durdur"""
    await verify_server_ownership(server_id, current_user, db)

    control_service = ServerControlService(db)
    result = await control_service.stop_server(server_id, graceful)

    if not result["success"]:
        raise HTTPException(400, result["message"])

    return result


@router.post("/{server_id}/restart")
async def restart_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Sunucuyu yeniden baslat"""
    await verify_server_ownership(server_id, current_user, db)

    control_service = ServerControlService(db)
    result = await control_service.restart_server(server_id)

    if not result["success"]:
        raise HTTPException(400, result["message"])

    return result


@router.get("/{server_id}/status", response_model=ServerStatusResponse)
async def get_server_status(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Sunucu durumunu al"""
    await verify_server_ownership(server_id, current_user, db)

    control_service = ServerControlService(db)
    status = await control_service.get_status(server_id)

    return ServerStatusResponse(**status)


# ============================================
# Installation Endpoints
# ============================================


@router.get("/{server_id}/installation", response_model=InstallationResponse)
async def get_installation_status(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Kurulum durumunu al"""
    await verify_server_ownership(server_id, current_user, db)

    installation = (
        db.query(ServerInstallation)
        .filter(ServerInstallation.server_id == server_id)
        .order_by(ServerInstallation.created_at.desc())
        .first()
    )

    if not installation:
        raise HTTPException(404, "Kurulum bulunamadi")

    return InstallationResponse(
        id=installation.id,
        server_id=installation.server_id,
        unique_code=installation.unique_code,
        status=installation.status.value if installation.status else "unknown",
        progress_percent=installation.progress_percent or 0,
        current_step=installation.current_step,
        total_steps=installation.total_steps or 8,
        error_message=installation.error_message,
        started_at=installation.started_at.isoformat() if installation.started_at else None,
        completed_at=installation.completed_at.isoformat() if installation.completed_at else None,
    )


# ============================================
# RCON & Console Endpoints
# ============================================


@router.post("/{server_id}/rcon", response_model=RCONResponse)
async def execute_rcon(
    server_id: int,
    request_data: RCONRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """RCON komutu calistir"""
    server = await verify_server_ownership(server_id, current_user, db)

    rcon_service = RCONService(db)
    result = await rcon_service.execute(
        server=server,
        command=request_data.command,
        user_id=current_user.id,
        ip_address=get_client_ip(request),
    )

    return RCONResponse(**result)


@router.get("/{server_id}/rcon/history")
async def get_rcon_history(
    server_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """RCON komut gecmisini al"""
    try:
        await verify_server_ownership(server_id, current_user, db)

        rcon_service = RCONService(db)
        history = rcon_service.get_command_history(server_id, limit, offset)

        return {"history": history}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RCON history error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Player Management Endpoints
# ============================================


@router.get("/{server_id}/players")
async def get_players(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Oyuncu listesini al"""
    try:
        server = await verify_server_ownership(server_id, current_user, db)

        rcon_service = RCONService(db)
        players = await rcon_service.get_players(server)

        return {"players": players}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get players error: {e}", exc_info=True)
        return {"players": [], "error": str(e)}


@router.post("/{server_id}/players/{slot}/kick")
async def kick_player(
    server_id: int,
    slot: int,
    request_data: PlayerKickRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Oyuncuyu at"""
    server = await verify_server_ownership(server_id, current_user, db)

    rcon_service = RCONService(db)
    result = await rcon_service.kick_player(
        server=server,
        player_slot=slot,
        reason=request_data.reason,
        user_id=current_user.id,
        ip_address=get_client_ip(request),
    )

    if not result["success"]:
        raise HTTPException(400, result["message"])

    return result


@router.post("/{server_id}/players/ban")
async def ban_player(
    server_id: int,
    request_data: PlayerBanRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Oyuncuyu banla"""
    server = await verify_server_ownership(server_id, current_user, db)

    if not request_data.steam_id and not request_data.ip_address:
        raise HTTPException(400, "steam_id veya ip_address gerekli")

    rcon_service = RCONService(db)
    result = await rcon_service.ban_player(
        server=server,
        steam_id=request_data.steam_id,
        ip_address=request_data.ip_address,
        player_name=request_data.name or "Unknown",
        reason=request_data.reason,
        duration_minutes=request_data.duration_minutes,
        user_id=current_user.id,
        request_ip=get_client_ip(request),
    )

    return result


# ============================================
# Ban Management Endpoints
# ============================================


@router.get("/{server_id}/bans")
async def get_bans(
    server_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Ban listesini al"""
    await verify_server_ownership(server_id, current_user, db)

    query = db.query(ServerBan).filter(ServerBan.server_id == server_id)
    if active_only:
        query = query.filter(ServerBan.is_active == True)

    bans = query.order_by(ServerBan.created_at.desc()).all()

    return {
        "bans": [
            {
                "id": b.id,
                "steam_id": b.steam_id,
                "ip_address": b.ip_address,
                "name": b.name,
                "reason": b.reason,
                "duration_minutes": b.duration_minutes,
                "expires_at": b.expires_at.isoformat() if b.expires_at else None,
                "is_active": b.is_active,
                "ban_type": b.ban_type.value if b.ban_type else None,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in bans
        ]
    }


@router.delete("/{server_id}/bans/{ban_id}")
async def unban_player(
    server_id: int,
    ban_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Bani kaldir"""
    server = await verify_server_ownership(server_id, current_user, db)

    rcon_service = RCONService(db)
    result = await rcon_service.unban_player(
        server=server, ban_id=ban_id, user_id=current_user.id, request_ip=get_client_ip(request)
    )

    if not result["success"]:
        raise HTTPException(400, result["message"])

    return result


# ============================================
# Admin Management Endpoints
# ============================================


@router.get("/{server_id}/admins")
async def get_admins(
    server_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Admin listesini al"""
    await verify_server_ownership(server_id, current_user, db)

    admin_service = AMXXAdminService(db)
    admins = admin_service.get_admins(server_id, include_inactive)

    return {"admins": admins}


@router.post("/{server_id}/admins")
async def add_admin(
    server_id: int,
    request_data: AdminCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Admin ekle"""
    await verify_server_ownership(server_id, current_user, db)

    expires_at = None
    if request_data.expires_at:
        try:
            expires_at = datetime.fromisoformat(request_data.expires_at)
        except ValueError:
            raise HTTPException(400, "Gecersiz tarih formati")

    admin_service = AMXXAdminService(db)
    admin, message = admin_service.add_admin(
        server_id=server_id,
        steam_id=request_data.steam_id,
        name=request_data.name,
        flags=request_data.flags,
        password=request_data.password,
        added_by=current_user.id,
        expires_at=expires_at,
        notes=request_data.notes,
    )

    if not admin:
        raise HTTPException(400, message)

    return {"success": True, "admin_id": admin.id, "message": message}


@router.put("/{server_id}/admins/{admin_id}")
async def update_admin(
    server_id: int,
    admin_id: int,
    request_data: AdminUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Admin guncelle"""
    await verify_server_ownership(server_id, current_user, db)

    expires_at = None
    if request_data.expires_at:
        try:
            expires_at = datetime.fromisoformat(request_data.expires_at)
        except ValueError:
            raise HTTPException(400, "Gecersiz tarih formati")

    admin_service = AMXXAdminService(db)
    success, message = admin_service.update_admin(
        admin_id=admin_id,
        flags=request_data.flags,
        password=request_data.password,
        is_active=request_data.is_active,
        expires_at=expires_at,
        notes=request_data.notes,
    )

    if not success:
        raise HTTPException(400, message)

    return {"success": True, "message": message}


@router.delete("/{server_id}/admins/{admin_id}")
async def remove_admin(
    server_id: int,
    admin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Admin sil"""
    await verify_server_ownership(server_id, current_user, db)

    admin_service = AMXXAdminService(db)
    success, message = admin_service.remove_admin(admin_id)

    if not success:
        raise HTTPException(400, message)

    return {"success": True, "message": message}


@router.post("/{server_id}/admins/sync")
async def sync_admins(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Adminleri sunucuya senkronize et"""
    server = await verify_server_ownership(server_id, current_user, db)

    admin_service = AMXXAdminService(db)
    rcon_service = RCONService(db)

    success, message = admin_service.sync_to_server(server, rcon_service)

    return {"success": success, "message": message}


@router.post("/{server_id}/admins/sync-owner")
async def sync_owner_as_admin(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Sunucu sahibini manuel olarak admin olarak ekle/senkronize et"""
    await verify_server_ownership(server_id, current_user, db)

    admin_service = AMXXAdminService(db)
    success, message = admin_service.add_owner_as_admin(server_id, current_user.id)

    return {"success": success, "message": message}


# ============================================
# Config Management Endpoints
# ============================================


@router.get("/{server_id}/config")
async def get_config(
    server_id: int,
    filename: str = "server.cfg",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Config dosyasini oku"""
    server = await verify_server_ownership(server_id, current_user, db)

    config_service = ServerConfigService(db)
    content, message = config_service.read_config(server, filename)

    if content is None:
        raise HTTPException(404, message)

    return {"filename": filename, "content": content}


@router.put("/{server_id}/config")
async def update_config(
    server_id: int,
    request_data: ConfigUpdateRequest,
    filename: str = "server.cfg",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Config dosyasini guncelle"""
    server = await verify_server_ownership(server_id, current_user, db)

    config_service = ServerConfigService(db)
    success, message = config_service.write_config(
        server, filename, request_data.content, current_user.id
    )

    if not success:
        raise HTTPException(400, message)

    return {"success": True, "message": message}


@router.get("/{server_id}/config/server.cfg")
async def get_server_cfg(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """server.cfg oku"""
    server = await verify_server_ownership(server_id, current_user, db)

    config_service = ServerConfigService(db)
    content, message = config_service.read_config(server, "server.cfg")

    if content is None:
        raise HTTPException(404, message)

    return {"content": content}


@router.post("/{server_id}/config/server.cfg")
async def update_server_cfg(
    server_id: int,
    request_data: ConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """server.cfg guncelle"""
    server = await verify_server_ownership(server_id, current_user, db)

    config_service = ServerConfigService(db)
    success, message = config_service.write_config(
        server, "server.cfg", request_data.content, current_user.id
    )

    if not success:
        raise HTTPException(400, message)

    return {"success": True, "message": message}


@router.get("/{server_id}/config/mapcycle")
async def get_mapcycle(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Mapcycle oku"""
    server = await verify_server_ownership(server_id, current_user, db)

    config_service = ServerConfigService(db)
    maps, message = config_service.read_mapcycle(server)

    if maps is None:
        raise HTTPException(404, message)

    return {"maps": maps}


@router.put("/{server_id}/config/mapcycle")
async def update_mapcycle(
    server_id: int,
    request_data: MapcycleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Mapcycle guncelle"""
    server = await verify_server_ownership(server_id, current_user, db)

    config_service = ServerConfigService(db)
    success, message = config_service.write_mapcycle(server, request_data.maps, current_user.id)

    if not success:
        raise HTTPException(400, message)

    return {"success": True, "message": message}


@router.get("/{server_id}/config/motd")
async def get_motd(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """MOTD oku"""
    server = await verify_server_ownership(server_id, current_user, db)

    config_service = ServerConfigService(db)
    content, message = config_service.read_motd(server)

    if content is None:
        raise HTTPException(404, message)

    return {"content": content}


@router.put("/{server_id}/config/motd")
async def update_motd(
    server_id: int,
    request_data: ConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """MOTD guncelle"""
    server = await verify_server_ownership(server_id, current_user, db)

    config_service = ServerConfigService(db)
    success, message = config_service.write_motd(server, request_data.content, current_user.id)

    if not success:
        raise HTTPException(400, message)

    return {"success": True, "message": message}


# ============================================
# Map Management Endpoints
# ============================================


@router.get("/{server_id}/maps")
async def get_available_maps(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Mevcut haritalari listele"""
    server = await verify_server_ownership(server_id, current_user, db)

    config_service = ServerConfigService(db)
    maps = config_service.get_available_maps(server)

    return {"maps": maps}


@router.post("/{server_id}/maps/change")
async def change_map(
    server_id: int,
    request_data: MapChangeRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Harita degistir"""
    server = await verify_server_ownership(server_id, current_user, db)

    rcon_service = RCONService(db)
    result = await rcon_service.change_map(
        server=server,
        map_name=request_data.map_name,
        user_id=current_user.id,
        request_ip=get_client_ip(request),
    )

    if not result["success"]:
        raise HTTPException(400, result["message"])

    return result


# ============================================
# Quick Actions Endpoints
# ============================================


@router.post("/{server_id}/say")
async def say_message(
    server_id: int,
    request_data: SayRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Tum oyunculara mesaj gonder"""
    server = await verify_server_ownership(server_id, current_user, db)

    rcon_service = RCONService(db)
    result = await rcon_service.say(
        server=server,
        message=request_data.message,
        user_id=current_user.id,
        request_ip=get_client_ip(request),
    )

    return result


@router.post("/{server_id}/restart-round")
async def restart_round(
    server_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Round'u yeniden baslat (CS 1.6)"""
    server = await verify_server_ownership(server_id, current_user, db)

    rcon_service = RCONService(db)
    result = await rcon_service.restart_round(
        server=server, user_id=current_user.id, request_ip=get_client_ip(request)
    )

    return result


# ============================================
# Stats Endpoints
# ============================================


@router.get("/{server_id}/stats")
async def get_server_stats(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Sunucu istatistiklerini al"""
    server = await verify_server_ownership(server_id, current_user, db)

    # Temel istatistikler
    from datetime import timedelta

    from sqlalchemy import func

    from app.models.database import ServerStatsHourly

    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    # Son 24 saat
    stats_24h = (
        db.query(
            func.avg(ServerStatsHourly.avg_players).label("avg_players"),
            func.max(ServerStatsHourly.max_players).label("max_players"),
            func.sum(ServerStatsHourly.unique_players).label("total_unique"),
        )
        .filter(
            ServerStatsHourly.server_id == server_id, ServerStatsHourly.hour_timestamp >= last_24h
        )
        .first()
    )

    # Son 7 gun
    stats_7d = (
        db.query(
            func.avg(ServerStatsHourly.avg_players).label("avg_players"),
            func.max(ServerStatsHourly.max_players).label("max_players"),
        )
        .filter(
            ServerStatsHourly.server_id == server_id, ServerStatsHourly.hour_timestamp >= last_7d
        )
        .first()
    )

    # Calculate uptime
    uptime_str = "0s"
    if server.last_started:
        uptime_delta = datetime.utcnow() - server.last_started
        hours = int(uptime_delta.total_seconds() // 3600)
        minutes = int((uptime_delta.total_seconds() % 3600) // 60)
        if hours > 0:
            uptime_str = f"{hours}h {minutes}m"
        else:
            uptime_str = f"{minutes}m"

    return {
        "uptime": uptime_str,
        "avg_players": float(stats_24h.avg_players or 0),
        "max_players": stats_24h.max_players or 0,
        "total_unique": stats_24h.total_unique or 0,
        "crash_count": server.crash_count or 0,
        "last_crash": server.last_crash.isoformat() if server.last_crash else None,
        "last_24h": {
            "avg_players": float(stats_24h.avg_players or 0),
            "max_players": stats_24h.max_players or 0,
            "total_unique": stats_24h.total_unique or 0,
        },
        "last_7d": {
            "avg_players": float(stats_7d.avg_players or 0),
            "max_players": stats_7d.max_players or 0,
        },
    }


@router.get("/{server_id}/stats/hourly")
async def get_hourly_stats(
    server_id: int,
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Saatlik istatistikleri al"""
    await verify_server_ownership(server_id, current_user, db)

    from datetime import timedelta

    from app.models.database import ServerStatsHourly

    cutoff = datetime.utcnow() - timedelta(hours=hours)

    stats = (
        db.query(ServerStatsHourly)
        .filter(
            ServerStatsHourly.server_id == server_id, ServerStatsHourly.hour_timestamp >= cutoff
        )
        .order_by(ServerStatsHourly.hour_timestamp.asc())
        .all()
    )

    return {
        "hourly": [
            {
                "hour": s.hour_timestamp.isoformat(),
                "avg_players": s.avg_players,
                "max_players": s.max_players,
                "unique_players": s.unique_players,
                "most_played_map": s.most_played_map,
            }
            for s in stats
        ]
    }


# ============================================
# Quick Commands Endpoints
# ============================================


@router.get("/{server_id}/quick-commands")
async def get_quick_commands(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Hizli komutlari al"""
    await verify_server_ownership(server_id, current_user, db)

    commands = (
        db.query(ServerQuickCommand)
        .filter(ServerQuickCommand.server_id == server_id, ServerQuickCommand.is_active == True)
        .order_by(ServerQuickCommand.display_order)
        .all()
    )

    return {
        "commands": [
            {
                "id": c.id,
                "name": c.name,
                "command": c.command,
                "description": c.description,
                "icon": c.icon,
            }
            for c in commands
        ]
    }


@router.post("/{server_id}/quick-commands/{command_id}/execute")
async def execute_quick_command(
    server_id: int,
    command_id: int,
    request: Request,
    params: dict = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Hizli komutu calistir"""
    server = await verify_server_ownership(server_id, current_user, db)

    quick_cmd = (
        db.query(ServerQuickCommand)
        .filter(ServerQuickCommand.id == command_id, ServerQuickCommand.server_id == server_id)
        .first()
    )

    if not quick_cmd:
        raise HTTPException(404, "Komut bulunamadi")

    # Parametreleri yerine koy
    command = quick_cmd.command
    if params:
        for key, value in params.items():
            command = command.replace(f"{{{key}}}", str(value))

    rcon_service = RCONService(db)
    result = await rcon_service.execute(
        server=server, command=command, user_id=current_user.id, ip_address=get_client_ip(request)
    )

    return result


# ============================================
# Visual Config Endpoints
# ============================================


class VisualConfigUpdate(BaseModel):
    """Visual config güncelleme (Minimal)"""

    # Sunucu Bilgileri
    hostname: Optional[str] = None
    sv_contact: Optional[str] = None
    # Güvenlik
    rcon_password: Optional[str] = None
    sv_password: Optional[str] = None
    # Sunucu
    sv_allowdownload: Optional[int] = None
    # AG Mod - Temel
    sv_ag_gamemode: Optional[str] = None
    sv_ag_start_health: Optional[int] = None
    sv_ag_start_armour: Optional[int] = None
    sv_ag_start_longjump: Optional[int] = None
    sv_ag_start_minplayers: Optional[int] = None
    # AG Mod - Oylama
    sv_ag_allow_vote: Optional[int] = None
    sv_ag_vote_gamemode: Optional[int] = None
    sv_ag_vote_map: Optional[int] = None


@router.get("/{server_id}/config/visual")
async def get_visual_config(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """server.cfg'den görsel düzenleyici ayarlarını al"""
    server = await verify_server_ownership(server_id, current_user, db)

    config_service = ServerConfigService(db)
    values = config_service.parse_visual_config(server)

    return values


@router.put("/{server_id}/config/visual")
async def update_visual_config(
    server_id: int,
    config: VisualConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Görsel düzenleyici ayarlarını güncelle"""
    server = await verify_server_ownership(server_id, current_user, db)

    # Sadece dolu alanları al
    values = {k: v for k, v in config.dict().items() if v is not None}

    if not values:
        raise HTTPException(400, "Güncellenecek değer bulunamadı")

    config_service = ServerConfigService(db)
    success, message = config_service.update_visual_config(server, values, current_user.id)

    if not success:
        raise HTTPException(500, message)

    return {"success": True, "message": message}


# ==================== AUTO-UPDATE SYSTEM ====================


class UpdateCheckResponse(BaseModel):
    """Auto-update check response"""

    cs16: dict
    amxmodx: dict
    last_update: Optional[str]
    auto_update_enabled: bool
    next_scheduled_update: Optional[str]


class UpdateActionRequest(BaseModel):
    """Update action request"""

    component: str = Field(..., description="cs16 or amxmodx")
    auto_restart: bool = Field(default=False, description="Auto-restart after update")


@router.get("/{server_id}/updates/status", response_model=UpdateCheckResponse)
async def get_update_status(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get update status for all components"""
    server = await verify_server_ownership(server_id, current_user, db)

    status = await auto_update_service.get_update_status(server_id, server, db)

    return status


@router.post("/{server_id}/updates/install")
async def install_update(
    server_id: int,
    request: UpdateActionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Install component update"""
    server = await verify_server_ownership(server_id, current_user, db)

    if request.component == "cs16":
        result = await auto_update_service.update_cs16(server_id, current_user.id, db)
    elif request.component == "amxmodx":
        result = await auto_update_service.update_amxmodx(server_id, current_user.id, server, db)
    else:
        raise HTTPException(400, "Invalid component. Use 'cs16' or 'amxmodx'")

    # Auto-restart if requested and update successful
    if result.get("success") and request.auto_restart:
        control_service = ServerControlService(db)
        background_tasks.add_task(control_service.restart_server, server.id, current_user.id)

    return result


@router.get("/{server_id}/updates/history")
async def get_update_history(
    server_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get update history"""
    await verify_server_ownership(server_id, current_user, db)

    history = await auto_update_service.get_update_history(db, server_id, limit)

    return {"history": history, "count": len(history)}


# ==================== DDOS PROTECTION SYSTEM ====================


class DDoSStatusResponse(BaseModel):
    """DDoS protection status response"""

    enabled: bool
    current_traffic: dict
    blocked_ips_count: int
    total_attacks_24h: int
    last_attack: Optional[dict]
    protection_level: str
    auto_mitigation: bool


class BlockIPRequest(BaseModel):
    """Block IP request"""

    ip: str = Field(..., min_length=7, max_length=45, description="IP address to block")
    reason: str = Field(..., min_length=1, max_length=200, description="Reason for blocking")
    duration: int = Field(
        default=3600, ge=0, description="Block duration in seconds (0 = permanent)"
    )


@router.get("/{server_id}/ddos/status", response_model=DDoSStatusResponse)
async def get_ddos_status(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get DDoS protection status"""
    server = await verify_server_ownership(server_id, current_user, db)

    status = await ddos_protection_service.get_protection_status(server_id, server, db)

    return status


@router.get("/{server_id}/ddos/traffic")
async def get_traffic_stats(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get real-time traffic statistics"""
    server = await verify_server_ownership(server_id, current_user, db)

    stats = await ddos_protection_service.get_traffic_stats(server_id, server)

    return stats


@router.post("/{server_id}/ddos/block-ip")
async def block_ip(
    server_id: int,
    request: BlockIPRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Block an IP address"""
    await verify_server_ownership(server_id, current_user, db)

    result = await ddos_protection_service.block_ip(
        request.ip, request.reason, request.duration, current_user.id, db
    )

    return result


@router.post("/{server_id}/ddos/unblock-ip")
async def unblock_ip(
    server_id: int,
    ip: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Unblock an IP address"""
    await verify_server_ownership(server_id, current_user, db)

    result = await ddos_protection_service.unblock_ip(ip, db)

    return result


@router.get("/{server_id}/ddos/blocked-ips")
async def get_blocked_ips(
    server_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get list of blocked IPs"""
    await verify_server_ownership(server_id, current_user, db)

    blocked_ips = await ddos_protection_service.get_blocked_ips(db, active_only)

    return {"blocked_ips": blocked_ips, "count": len(blocked_ips)}


@router.get("/{server_id}/ddos/attack-history")
async def get_attack_history(
    server_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get DDoS attack history"""
    await verify_server_ownership(server_id, current_user, db)

    history = await ddos_protection_service.get_attack_history(db, server_id, limit)

    return {"attacks": history, "count": len(history)}

    return {"success": True, "message": message}
