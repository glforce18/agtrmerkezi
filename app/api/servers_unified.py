"""
AGTR Merkezi - Unified Server Management API
Combines legacy servers.py and server_v2.py into clean, maintainable API
"""

import hashlib
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.common import (
    APIError,
    BadRequestError,
    ForbiddenError,
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
    get_current_user_or_panel,
    get_current_user_required,
)
from app.models.connection import get_db
from app.models.database import (
    CommandType,
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

    package_id: int = Field(..., gt=0, description="Package ID must be positive")
    server_name: str = Field(..., min_length=3, max_length=50, description="Server name")
    duration: int = Field(default=1, ge=1, le=12, description="Duration in months (1-12)")
    auto_renew: bool = Field(default=False, description="Auto-renew subscription")


class WalletOrderRequest(BaseModel):
    """Server order with wallet payment"""

    package_id: int = Field(..., gt=0, description="Package ID must be positive")
    server_name: str = Field(..., min_length=3, max_length=50, description="Server name")
    months: int = Field(default=1, ge=1, le=12, description="Duration in months (1-12)")
    payment_type: str = Field(
        default="TL", pattern="^(TL|coin)$", description="Payment type: TL or coin"
    )
    auto_renew: bool = Field(default=True, description="Auto-renew subscription")


# ============================================
# Server Lifecycle Endpoints
# ============================================


@router.get("/my-servers")
async def get_my_servers(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get user's servers with pagination"""
    try:
        log_api_call("get_my_servers", current_user.id)

        # Get total count
        total = db.query(GameServer).filter(GameServer.owner_id == current_user.id).count()

        # Get paginated servers
        servers = (
            db.query(GameServer)
            .filter(GameServer.owner_id == current_user.id)
            .order_by(GameServer.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return {
            "servers": [
                {
                    "id": s.id,
                    "name": s.name,
                    "ip_address": s.ip_address,
                    "port": s.port,
                    "game_type": s.game_type.value if s.game_type else "unknown",
                    "status": s.status.value if s.status else "unknown",
                    "current_players": s.current_players or 0,
                    "slots": s.slots,
                    "map": s.current_map or "N/A",
                    "created_at": s.created_at,
                    "expires_at": s.expires_at,
                }
                for s in servers
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page if total > 0 else 0,
            },
        }

    except Exception as e:
        log_api_error("get_my_servers", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/packages")
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

        return {
            "data": [
                {
                    "id": pkg.id,
                    "name": pkg.name,
                    "description": pkg.description,
                    "price": pkg.price_monthly,
                    "max_slots": pkg.slots,
                    "ram_mb": pkg.ram_mb,
                    "disk_gb": pkg.disk_gb,
                    "duration": 30,  # Default monthly
                    "is_popular": pkg.is_popular,
                }
                for pkg in packages
            ]
        }

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
            raise NotFoundError("Server not found")

        validate_server_ownership(server, current_user)

        # Map database fields to response model
        return {
            "id": server.id,
            "name": server.name,
            "ip": server.ip_address,
            "port": server.port,
            "game": server.game_type.value if server.game_type else "unknown",
            "status": server.status.value if server.status else "unknown",
            "current_players": server.current_players or 0,
            "max_players": server.slots,
            "map": server.current_map,
            "created_at": server.created_at,
            "expires_at": server.expires_at,
            "rcon_password": server.rcon_password,
            "ftp_username": None,  # TODO: FTP username generation
            "unique_code": server.unique_code or "",
            "owner_id": server.owner_id,
        }

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
            raise NotFoundError("Server not found")

        validate_server_ownership(server, current_user)

        if server.status == ServerStatus.RUNNING:
            raise BadRequestError("Server is already running")

        # Use ServerControlService
        control_service = ServerControlService(db)
        result = await control_service.start_server(server_id)

        if result.get("success"):
            return success_response(message="Server is starting")
        else:
            error_msg = result.get("message", "Sunucu başlatılamadı")
            raise HTTPException(status_code=500, detail=error_msg)

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
            raise NotFoundError("Server not found")

        validate_server_ownership(server, current_user)

        if server.status != ServerStatus.RUNNING:
            raise BadRequestError("Server is not running")

        control_service = ServerControlService(db)
        result = await control_service.stop_server(server_id)

        if result.get("success"):
            return success_response(message="Server is stopping")
        else:
            error_msg = result.get("message", "Sunucu durdurulamadı")
            raise HTTPException(status_code=500, detail=error_msg)

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
            raise NotFoundError("Server not found")

        validate_server_ownership(server, current_user)

        control_service = ServerControlService(db)
        result = await control_service.restart_server(server_id)

        if result.get("success"):
            return success_response(message="Server is restarting")
        else:
            error_msg = result.get("message", "Sunucu yeniden başlatılamadı")
            raise HTTPException(status_code=500, detail=error_msg)

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
    auth: tuple = Depends(get_current_user_or_panel),
    db: Session = Depends(get_db),
):
    """Execute RCON command"""
    try:
        current_user, panel_server_id = auth

        # Panel authentication
        if panel_server_id:
            if server_id != panel_server_id:
                raise HTTPException(status_code=403, detail="Panel token is for a different server")
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
            if not server:
                raise NotFoundError("Server not found")

        # Steam authentication
        elif current_user:
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
            if not server:
                raise NotFoundError("Server not found")
            validate_server_ownership(server, current_user)

        else:
            raise HTTPException(status_code=401, detail="Authentication required")

        if server.status != ServerStatus.RUNNING:
            raise BadRequestError("Server is not running")

        # Use RCONService
        rcon_service = RCONService(db)
        # For panel auth, user_id is None (panel users are not in users table)
        user_id = current_user.id if current_user else None

        result = await rcon_service.execute(
            server=server,
            command=request.command,
            user_id=user_id,
            command_type=CommandType.RCON,
            ip_address=None,
        )

        if result["success"]:
            return RCONResponse(success=True, output=result["response"])
        else:
            return RCONResponse(success=False, error=result["error"])

    except APIError:
        raise
    except Exception as e:
        user_id = current_user.id if current_user else panel_server_id
        log_api_error("execute_rcon_command", e, user_id)
        return RCONResponse(success=False, error=str(e))


@router.get("/{server_id}/live-chat")
async def get_live_chat(
    server_id: int,
    since_line: int = 0,
    auth: tuple = Depends(get_current_user_or_panel),
    db: Session = Depends(get_db),
):
    """Get live chat messages from monster log files"""
    try:
        import os
        import re
        from glob import glob

        current_user, panel_server_id = auth

        # Authenticate
        if panel_server_id:
            if server_id != panel_server_id:
                raise HTTPException(status_code=403, detail="Panel token is for a different server")
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
        elif current_user:
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
            if not server:
                raise NotFoundError("Server not found")
            validate_server_ownership(server, current_user)
        else:
            raise HTTPException(status_code=401, detail="Authentication required")

        if not server:
            raise NotFoundError("Server not found")

        # Find monster log files in AMX Mod X logs directory
        server_dir = f"/home/gameservers/servers/server_{server_id}/valve/addons/amxmodx/logs"
        if not os.path.exists(server_dir):
            return {"messages": [], "last_line": 0}

        # Get all monster*.log files, sorted by modification time (newest first)
        monster_logs = glob(f"{server_dir}/monster*.log")
        if not monster_logs:
            return {"messages": [], "last_line": 0}

        # Get the most recent monster log
        latest_log = max(monster_logs, key=os.path.getmtime)

        # Read chat messages from the log
        messages = []
        try:
            with open(latest_log, "r", errors="ignore") as f:
                lines = f.readlines()

                # Start from since_line
                new_lines = lines[since_line:]
                current_line = since_line

                for line in new_lines:
                    current_line += 1

                    # Parse monster log format from AMX Mod X
                    # Example format:
                    # L 01/14/2026 - 00:44:58: [00:44:58] <Player><ID>: message
                    match = re.match(
                        r"L\s+(\d{2}/\d{2}/\d{4}\s+-\s+\d{2}:\d{2}:\d{2}):"
                        r"\s+\[(\d{2}:\d{2}:\d{2})\]\s+<(.+?)><.+?>:\s+(.+)",
                        line,
                    )
                    if match:
                        full_timestamp, time_only, player, message = match.groups()

                        # Strip color codes from player name (^0-^9)
                        player_clean = re.sub(r"\^\d", "", player)

                        # Generate color based on player name (consistent color per player)
                        player_hash = int(
                            hashlib.md5(player_clean.encode(), usedforsecurity=False).hexdigest()[
                                :6
                            ],
                            16,
                        )
                        colors = [
                            "#58a6ff",
                            "#3fb950",
                            "#d29922",
                            "#f85149",
                            "#a371f7",
                            "#bc8cff",
                            "#f78166",
                        ]
                        color = colors[player_hash % len(colors)]

                        messages.append(
                            {
                                "time": time_only,
                                "player": player_clean,
                                "message": message.strip(),
                                "color": color,
                            }
                        )

                return {"messages": messages, "last_line": current_line}

        except Exception as e:
            logger.error(f"Error reading monster log: {e}")
            return {"messages": [], "last_line": since_line}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Live chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch live chat")


@router.get("/{server_id}/players")
async def get_server_players(
    server_id: int,
    auth: tuple = Depends(get_current_user_or_panel),
    db: Session = Depends(get_db),
):
    """Get online players list by parsing RCON status command"""
    try:
        current_user, panel_server_id = auth

        # Authenticate
        if panel_server_id:
            if server_id != panel_server_id:
                raise HTTPException(status_code=403, detail="Panel token is for a different server")
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
        elif current_user:
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
            if not server:
                raise NotFoundError("Server not found")
            validate_server_ownership(server, current_user)
        else:
            raise HTTPException(status_code=401, detail="Authentication required")

        if not server:
            raise NotFoundError("Server not found")

        if server.status != ServerStatus.RUNNING:
            return {"success": True, "players": []}

        # Execute status command via RCON
        rcon_service = RCONService(db)
        user_id = current_user.id if current_user else None

        result = await rcon_service.execute(
            server=server,
            command="status",
            user_id=user_id,
            command_type=CommandType.RCON,
            ip_address=None,
        )

        if not result["success"]:
            return {"success": False, "players": [], "error": result["error"]}

        # Parse status output to extract player info
        players = []
        output = result["response"]

        # Status format (multi-line):
        # # 1 "Player Name" 6 STEAM_0:1:12345   0 00:38   33    0
        # 212.252.141.208:8140

        import re

        lines = output.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            # Match player line: # ID "Name" userid STEAMID frag time ping loss
            match = re.match(
                r'#\s+(\d+)\s+"(.+?)"\s+(\d+)\s+(STEAM_\d+:\d+:\d+)\s+'
                r"(-?\d+)\s+([\d:]+)\s+(\d+)\s+\d+",
                line,
            )
            if match:
                player_id, name, userid, uniqueid, frag, time, ping = match.groups()

                # Get IP from next line
                addr = ""
                if i + 1 < len(lines):
                    addr = lines[i + 1].strip()

                # Strip color codes from name (^0-^9)
                name_clean = re.sub(r"\^\d", "", name)

                players.append(
                    {
                        "id": int(player_id),
                        "name": name_clean,
                        "userid": int(userid),
                        "uniqueid": uniqueid,
                        "frag": int(frag),
                        "time": time,
                        "ping": int(ping),
                        "address": addr,
                    }
                )
                i += 2  # Skip the address line
            else:
                i += 1

        return {"success": True, "players": players}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get players error: {e}")
        return {"success": False, "players": [], "error": str(e)}


@router.get("/{server_id}/logs")
async def get_server_logs(
    server_id: int,
    type: str = "plugin",  # plugin, error, chat
    lines: int = 200,
    auth: tuple = Depends(get_current_user_or_panel),
    db: Session = Depends(get_db),
):
    """Get server log files"""
    try:
        current_user, panel_server_id = auth

        # Authenticate
        if panel_server_id:
            if server_id != panel_server_id:
                raise HTTPException(status_code=403, detail="Panel token is for a different server")
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
        elif current_user:
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
            if not server:
                raise NotFoundError("Server not found")
            validate_server_ownership(server, current_user)
        else:
            raise HTTPException(status_code=401, detail="Authentication required")

        if not server:
            raise NotFoundError("Server not found")

        # Determine log directory and pattern based on type
        if type == "plugin":
            log_dir = f"/home/gameservers/servers/server_{server_id}/valve/logs"
            pattern = "L*.log"
        elif type == "error":
            log_dir = f"/home/gameservers/servers/server_{server_id}/valve/addons/amxmodx/logs"
            pattern = "error*.log"
        elif type == "chat":
            log_dir = f"/home/gameservers/servers/server_{server_id}/valve/addons/amxmodx/logs"
            pattern = "monster*.log"
        else:
            raise HTTPException(status_code=400, detail="Invalid log type")

        if not os.path.exists(log_dir):
            return {"success": True, "lines": []}

        # Get log files matching pattern
        from glob import glob as glob_files

        log_files = glob_files(f"{log_dir}/{pattern}")

        if not log_files:
            return {"success": True, "lines": []}

        # Get the most recent log file
        latest_log = max(log_files, key=os.path.getmtime)

        # Read last N lines
        log_lines = []
        try:
            with open(latest_log, "r", errors="ignore") as f:
                all_lines = f.readlines()
                # Get last N lines
                log_lines = [line.rstrip("\n") for line in all_lines[-lines:]]
        except Exception as e:
            logger.error(f"Error reading log file {latest_log}: {e}")

        return {
            "success": True,
            "lines": log_lines,
            "file": os.path.basename(latest_log),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get logs error: {e}")
        return {"success": False, "lines": [], "error": str(e)}


@router.get("/{server_id}/players_old", response_model=List[PlayerInfo])
async def get_server_players_old(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get server players via RCON"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()

        if not server:
            raise NotFoundError("Server not found")

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
            raise NotFoundError("Server not found")

        validate_server_ownership(server, current_user)

        if server.status != ServerStatus.RUNNING:
            raise BadRequestError("Server is not running")

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
    background_tasks: BackgroundTasks,
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
            raise NotFoundError("Package not found")

        # Find available server slot
        pool_manager = PortPoolManager(db)
        slot = pool_manager.acquire_slot()

        if not slot:
            raise BadRequestError(
                "No available server slots at the moment. Please try again later."
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
            mod_type=package.game_type,
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

        # Auto-pay with balance if user has enough
        if current_user.balance >= total_price:
            logger.info(
                f"Auto-paying with balance: user_id={current_user.id}, amount={total_price}"
            )

            # Deduct balance
            from app.models.database import Transaction

            balance_before = current_user.balance
            current_user.balance -= total_price

            # Create transaction record
            from app.models.database import WalletType

            transaction = Transaction(
                user_id=current_user.id,
                wallet_type=WalletType.REAL,
                type="payment",
                amount=-total_price,
                description=f"Sunucu ödemesi: {server.name}",
                reference_id=str(payment.id),
                reference_type="payment",
                balance_before=balance_before,
                balance_after=current_user.balance,
            )
            db.add(transaction)

            # Mark payment as completed
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.utcnow()
            db.commit()

            # Trigger server installation (background task)
            async def trigger_installation():
                """Background task to install server - SHARED INSTALLATION"""
                from app.models.connection import SessionLocal
                from app.models.database import Notification
                from app.services.shared_installation_service import (
                    SharedInstallationService,
                )

                task_db = SessionLocal()
                try:
                    shared_service = SharedInstallationService(task_db)

                    # Map game_type to mod_type
                    mod_type_map = {
                        "ag": "ag",
                        "hldm": "hldm",
                        "cs16": "cs16",
                    }
                    mod_type = mod_type_map.get(server.game_type.value, "hldm")

                    logger.info(
                        f"Creating server {server.id} with SHARED installation (disk optimized)"
                    )

                    # Run shared installation
                    success, msg = await shared_service.create_server_with_symlinks(
                        server_id=server.id,
                        mod_type=mod_type,
                        hostname=server.name,
                        rcon_password=server.rcon_password,
                        port=server.port,
                        maxplayers=server.slots,
                    )

                    # Update server status
                    if success:
                        server_obj = (
                            task_db.query(GameServer).filter(GameServer.id == server.id).first()
                        )
                        if server_obj:
                            server_obj.status = ServerStatus.STOPPED
                            task_db.commit()

                            # Send success notification
                            notification = Notification(
                                user_id=current_user.id,
                                type="server",
                                title="Sunucu Hazır!",
                                message=(
                                    f"{server.name} sunucunuz kuruldu ve başlatılmaya hazır "
                                    "(58 MB disk optimized)."
                                ),
                                link=f"/servers/{server.id}",
                            )
                            task_db.add(notification)
                            task_db.commit()

                            logger.info(f"Server {server.id} SHARED installation completed: {msg}")
                    else:
                        logger.error(f"Server installation failed: {server.id} - {msg}")
                        server_obj = (
                            task_db.query(GameServer).filter(GameServer.id == server.id).first()
                        )
                        if server_obj:
                            server_obj.status = ServerStatus.SUSPENDED
                            task_db.commit()
                except Exception as e:
                    logger.error(f"Installation task error: {e}")
                finally:
                    task_db.close()

            # Add background task
            background_tasks.add_task(trigger_installation)

            logger.info(f"Installation triggered for server_id={server.id}")

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
        db.rollback()
        log_api_error("order_server", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/order/package-wallet")
async def order_server_with_wallet(
    data: WalletOrderRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Order a new game server with wallet payment"""
    try:
        log_api_call("order_server_with_wallet", current_user.id, {"package_id": data.package_id})

        # Validate package
        package = (
            db.query(ServerPackage)
            .filter(ServerPackage.id == data.package_id, ServerPackage.is_active.is_(True))
            .first()
        )
        if not package:
            raise NotFoundError("Package not found")

        # Calculate price
        total_price = package.price_monthly * data.months

        # Check balance
        from app.models.database import WalletType

        if data.payment_type.upper() == "TL" or data.payment_type == "real":
            if current_user.balance < total_price:
                raise BadRequestError(
                    f"Yetersiz TL bakiye. Mevcut: {current_user.balance:.2f} TL, "
                    f"Gerekli: {total_price:.2f} TL"
                )
            wallet_type = WalletType.REAL
        else:
            if current_user.balance_coin < total_price:
                raise BadRequestError(
                    f"Yetersiz Armor bakiye. Mevcut: {current_user.balance_coin:.2f}, "
                    f"Gerekli: {total_price:.2f}"
                )
            wallet_type = WalletType.COIN

        # Find available server slot
        pool_manager = PortPoolManager(db)
        slot = pool_manager.acquire_slot()

        if not slot:
            raise BadRequestError(
                "No available server slots at the moment. Please try again later."
            )

        ip, port = slot

        # Deduct balance
        if wallet_type == WalletType.REAL:
            balance_before = current_user.balance
            current_user.balance -= total_price
            balance_after = current_user.balance
        else:
            balance_before = current_user.balance_coin
            current_user.balance_coin -= total_price
            balance_after = current_user.balance_coin

        # Create server
        server = GameServer(
            owner_id=current_user.id,
            owner_steam_id=current_user.steam_id if hasattr(current_user, "steam_id") else None,
            name=data.server_name,
            game_type=package.game_type,
            mod_type=package.game_type,
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
            expires_at=datetime.utcnow() + timedelta(days=data.months * 30),
        )
        db.add(server)
        db.flush()

        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            amount=total_price,
            status=PaymentStatus.COMPLETED,
            reference_code=generate_reference_code("PAY"),
            description=f"{package.name} - {data.months} Aylık Sunucu (Wallet)",
            server_id=server.id,
            months=data.months,
        )
        db.add(payment)
        db.flush()

        # Create transaction
        from app.models.database import Transaction

        transaction = Transaction(
            user_id=current_user.id,
            wallet_type=wallet_type,
            type="payment",
            amount=-total_price,
            description=f"Sunucu ödemesi: {server.name}",
            reference_id=str(payment.id),
            reference_type="payment",
            balance_before=balance_before,
            balance_after=balance_after,
        )
        db.add(transaction)

        # Create subscription
        from app.models.database import BillingPeriod
        from app.services.subscription_service import SubscriptionService

        billing_period = BillingPeriod.MONTHLY
        if data.months >= 12:
            billing_period = BillingPeriod.ANNUAL
        elif data.months >= 6:
            billing_period = BillingPeriod.BIANNUAL
        elif data.months >= 3:
            billing_period = BillingPeriod.QUARTERLY

        subscription_service = SubscriptionService(db)
        subscription = subscription_service.create_subscription(
            game_server_id=server.id,
            user_id=current_user.id,
            billing_period=billing_period,
            auto_renew_enabled=data.auto_renew,
            payment_method=wallet_type,
            monthly_amount=package.price_monthly,
            initial_expiry_date=server.expires_at,
        )

        db.commit()

        logger.info(
            f"Server ordered with wallet: server_id={server.id}, "
            f"payment_id={payment.id}, user_id={current_user.id}, wallet={wallet_type.value}"
        )

        # Trigger server installation (background task) - SHARED INSTALLATION
        async def trigger_installation():
            """Background task to install server - SHARED INSTALLATION"""
            from app.models.connection import SessionLocal
            from app.models.database import Notification
            from app.services.shared_installation_service import (
                SharedInstallationService,
            )

            task_db = SessionLocal()
            try:
                shared_service = SharedInstallationService(task_db)

                # Map game_type to mod_type
                mod_type_map = {
                    "ag": "ag",
                    "hldm": "hldm",
                    "cs16": "cs16",
                }
                mod_type = mod_type_map.get(server.game_type.value, "hldm")

                logger.info(
                    f"Creating server {server.id} with SHARED installation (disk optimized)"
                )

                # Run shared installation
                success, msg = await shared_service.create_server_with_symlinks(
                    server_id=server.id,
                    mod_type=mod_type,
                    hostname=server.name,
                    rcon_password=server.rcon_password,
                    port=server.port,
                    maxplayers=server.slots,
                )

                # Update server status
                if success:
                    server_obj = (
                        task_db.query(GameServer).filter(GameServer.id == server.id).first()
                    )
                    if server_obj:
                        server_obj.status = ServerStatus.STOPPED
                        task_db.commit()

                        # Send success notification
                        notification = Notification(
                            user_id=current_user.id,
                            type="server",
                            title="Sunucu Hazır!",
                            message=(
                                f"{server.name} sunucunuz kuruldu ve başlatılmaya hazır "
                                "(58 MB disk optimized)."
                            ),
                            link=f"/servers/{server.id}",
                        )
                        task_db.add(notification)
                        task_db.commit()

                        logger.info(f"Server {server.id} SHARED installation completed: {msg}")
                else:
                    logger.error(f"Server installation failed: {server.id} - {msg}")
                    server_obj = (
                        task_db.query(GameServer).filter(GameServer.id == server.id).first()
                    )
                    if server_obj:
                        server_obj.status = ServerStatus.SUSPENDED
                        task_db.commit()
            except Exception as e:
                logger.error(f"Installation task error: {e}")
            finally:
                task_db.close()

        # Add background task
        background_tasks.add_task(trigger_installation)

        logger.info(f"Installation triggered for server_id={server.id}")

        return {
            "success": True,
            "message": "Sunucu siparişiniz alındı! Kurulum başlatılıyor...",
            "order": {
                "server_id": server.id,
                "payment_id": payment.id,
                "subscription_id": subscription.id,
                "reference_code": payment.reference_code,
                "amount_paid": total_price,
                "currency": data.payment_type,
                "server_info": {
                    "name": server.name,
                    "ip": f"{ip}:{port}",
                    "slots": server.slots,
                    "unique_code": server.unique_code,
                    "status": "pending",
                    "expires_at": server.expires_at.isoformat() if server.expires_at else None,
                    "auto_renew_enabled": subscription.auto_renew_enabled,
                },
            },
            "new_balance": balance_after,
        }

    except APIError:
        raise
    except Exception as e:
        db.rollback()
        log_api_error("order_server_with_wallet", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# WebPanel Endpoints (Faz 1)
# ============================================


class ServerSettingsUpdate(BaseModel):
    """Server settings update request"""

    hostname: Optional[str] = Field(None, max_length=128)
    rcon_password: Optional[str] = Field(None, min_length=8, max_length=32)
    sv_password: Optional[str] = Field(None, max_length=32)
    max_players: Optional[int] = Field(None, ge=2, le=32)


@router.get("/{server_id}/webpanel/status")
async def get_server_webpanel_status(
    server_id: int,
    auth: tuple = Depends(get_current_user_or_panel),
    db: Session = Depends(get_db),
):
    """
    Get real-time server status for webpanel dashboard

    Returns:
        - is_online: Server running status
        - current_players: Active player count
        - max_players: Server slot limit
        - current_map: Active map
        - uptime_seconds: Server uptime
        - server_name: Hostname from RCON
        - ping: Server response time
    Works with both Steam auth and panel token
    """
    try:
        current_user, panel_server_id = auth

        # Verify ownership (either user owns it or panel token matches)
        if panel_server_id:
            # Panel auth - verify server_id matches
            if server_id != panel_server_id:
                raise HTTPException(status_code=403, detail="Panel token is for a different server")
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
            if not server:
                raise HTTPException(status_code=404, detail="Sunucu bulunamadı")
            user_id_for_logging = None
        elif current_user:
            # Steam auth - verify ownership
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
            if not server:
                raise HTTPException(status_code=404, detail="Sunucu bulunamadı")
            validate_server_ownership(server, current_user)
            user_id_for_logging = current_user.id
        else:
            raise HTTPException(status_code=401, detail="Giriş yapmanız gerekiyor")

        # Check if server is running
        control_service = ServerControlService(db)
        is_running = await control_service.is_running(server_id)

        if not is_running:
            return {
                "is_online": False,
                "current_players": 0,
                "max_players": server.slots,
                "current_map": None,
                "uptime_seconds": 0,
                "server_name": server.name,
                "ping": 0,
            }

        # Get status via RCON
        rcon_service = RCONService(db)
        status = await rcon_service.get_status(server)

        if "error" in status:
            # Server running but RCON failed
            return {
                "is_online": True,
                "current_players": server.current_players or 0,
                "max_players": server.slots,
                "current_map": server.current_map,
                "uptime_seconds": 0,
                "server_name": server.name,
                "ping": 0,
                "rcon_error": status["error"],
            }

        # Parse player count from status response
        players_str = status.get("players", "0 active")
        try:
            current_players = int(players_str.split()[0])
        except Exception:
            current_players = server.current_players or 0

        return {
            "is_online": True,
            "current_players": current_players,
            "max_players": server.slots,
            "current_map": status.get("map") or server.current_map,
            "uptime_seconds": 0,  # TODO: Calculate from last_heartbeat
            "server_name": status.get("hostname") or server.name,
            "ping": 0,  # TODO: Implement ping measurement
        }

    except APIError:
        raise
    except Exception as e:
        log_api_error(
            "get_server_webpanel_status",
            e,
            user_id_for_logging if "user_id_for_logging" in locals() else None,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/webpanel/info")
async def get_server_webpanel_info(
    server_id: int,
    auth: tuple = Depends(get_current_user_or_panel),
    db: Session = Depends(get_db),
):
    """
    Get server information for webpanel

    Returns basic server details and configuration
    Works with both Steam auth and panel token
    """
    try:
        current_user, panel_server_id = auth

        # Verify ownership (either user owns it or panel token matches)
        user_id_for_logging = None
        if panel_server_id:
            # Panel auth - verify server_id matches
            if server_id != panel_server_id:
                raise HTTPException(status_code=403, detail="Panel token is for a different server")
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
            if not server:
                raise HTTPException(status_code=404, detail="Sunucu bulunamadı")
        elif current_user:
            # Steam auth - verify ownership
            server = db.query(GameServer).filter(GameServer.id == server_id).first()
            if not server:
                raise HTTPException(status_code=404, detail="Sunucu bulunamadı")
            validate_server_ownership(server, current_user)
            user_id_for_logging = current_user.id
        else:
            raise HTTPException(status_code=401, detail="Giriş yapmanız gerekiyor")

        # Check if running
        control_service = ServerControlService(db)
        is_running = await control_service.is_running(server_id)

        return {
            "id": server.id,
            "name": server.name,
            "unique_code": server.unique_code,
            "ip_address": server.ip_address,
            "port": server.port,
            "game_type": server.game_type.value if server.game_type else "unknown",
            "status": server.status.value if server.status else "unknown",
            "is_running": is_running,
            "slots": server.slots,
            "current_players": server.current_players or 0,
            "current_map": server.current_map,
            "rcon_password": server.rcon_password,
            "created_at": server.created_at.isoformat() if server.created_at else None,
            "expires_at": server.expires_at.isoformat() if server.expires_at else None,
            "auto_restart": server.auto_restart,
        }

    except APIError:
        raise
    except Exception as e:
        log_api_error(
            "get_server_webpanel_info",
            e,
            user_id_for_logging if "user_id_for_logging" in locals() else None,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{server_id}/webpanel/settings")
async def update_server_webpanel_settings(
    server_id: int,
    data: ServerSettingsUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Update server settings via RCON

    Supports:
        - hostname: Server name
        - rcon_password: RCON password (updates DB + server.cfg)
        - sv_password: Join password (via RCON)
        - max_players: Slot count (requires restart)
    """
    try:
        # Get server and verify ownership
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        # Check if server is running
        control_service = ServerControlService(db)
        is_running = await control_service.is_running(server_id)

        if not is_running:
            raise BadRequestError("Sunucu çalışmıyor. Ayarları değiştirmek için sunucuyu başlatın.")

        rcon_service = RCONService(db)
        updates_applied = []

        # Update hostname
        if data.hostname is not None:
            result = await rcon_service.execute(
                server, f'hostname "{data.hostname}"', current_user.id
            )
            if result["success"]:
                server.name = data.hostname
                updates_applied.append("hostname")

        # Update sv_password
        if data.sv_password is not None:
            result = await rcon_service.set_server_password(
                server, data.sv_password, current_user.id, db
            )
            if result["success"]:
                updates_applied.append("sv_password")

        # Update RCON password (requires server.cfg edit + restart)
        if data.rcon_password is not None:
            server.rcon_password = data.rcon_password
            updates_applied.append("rcon_password (restart required)")

        # Update max_players (requires restart)
        if data.max_players is not None:
            server.slots = data.max_players
            updates_applied.append("max_players (restart required)")

        # Save DB changes
        db.commit()

        return success_response(
            message=f"Ayarlar güncellendi: {', '.join(updates_applied)}",
            data={
                "updates": updates_applied,
                "restart_required": "rcon_password" in str(updates_applied)
                or "max_players" in str(updates_applied),
            },
        )

    except APIError:
        raise
    except Exception as e:
        db.rollback()
        log_api_error("update_server_webpanel_settings", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Plugin Management Endpoints
# ============================================


class PluginUploadRequest(BaseModel):
    """Plugin upload request"""

    filename: str
    content_base64: str  # Base64 encoded .amxx file


@router.get("/{server_id}/plugins/all")
async def get_all_plugins(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get all plugins (server plugins + user plugins)

    Returns:
        - server_plugins: List of server plugins (read-only)
        - user_plugins: List of user's uploaded plugins
        - stats: Plugin statistics
    """
    try:
        # Get server and verify ownership
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from app.services.plugin_manager_service import PluginManagerService

        plugin_service = PluginManagerService(db)

        server_plugins = plugin_service.list_server_plugins(server_id)
        user_plugins = plugin_service.list_user_plugins(server_id, current_user.id)
        stats = plugin_service.get_plugin_stats(server_id, current_user.id)

        return success_response(
            data={
                "server_plugins": server_plugins,
                "user_plugins": user_plugins,
                "stats": stats,
            }
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_all_plugins", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/plugins/upload")
async def upload_plugin(
    server_id: int,
    request: PluginUploadRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Upload a plugin file (.amxx)

    Args:
        filename: Plugin filename (must end with .amxx)
        content_base64: Base64 encoded file content

    Returns:
        Success message and plugin info
    """
    try:
        # Get server and verify ownership
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        # Decode base64 content
        import base64

        try:
            content = base64.b64decode(request.content_base64)
        except Exception:
            raise BadRequestError("Geçersiz dosya içeriği (base64 decode hatası)")

        from app.services.plugin_manager_service import PluginManagerService

        plugin_service = PluginManagerService(db)

        success, message, plugin_info = plugin_service.upload_plugin(
            server_id, current_user.id, request.filename, content
        )

        if not success:
            raise BadRequestError(message)

        return success_response(message=message, data={"plugin": plugin_info})

    except APIError:
        raise
    except Exception as e:
        log_api_error("upload_plugin", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{server_id}/plugins/{filename}")
async def delete_plugin(
    server_id: int,
    filename: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Delete a user's plugin

    Args:
        filename: Plugin filename to delete

    Returns:
        Success message
    """
    try:
        # Get server and verify ownership
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from app.services.plugin_manager_service import PluginManagerService

        plugin_service = PluginManagerService(db)

        success, message = plugin_service.delete_plugin(server_id, current_user.id, filename)

        if not success:
            raise BadRequestError(message)

        return success_response(message=message)

    except APIError:
        raise
    except Exception as e:
        log_api_error("delete_plugin", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/plugins/{filename}/toggle")
async def toggle_plugin(
    server_id: int,
    filename: str,
    enable: bool,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Enable or disable a plugin

    Args:
        filename: Plugin filename
        enable: True to enable, False to disable

    Returns:
        Success message
    """
    try:
        # Get server and verify ownership
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from app.services.plugin_manager_service import PluginManagerService

        plugin_service = PluginManagerService(db)

        success, message = plugin_service.toggle_plugin(
            server_id, current_user.id, filename, enable
        )

        if not success:
            raise BadRequestError(message)

        return success_response(message=message)

    except APIError:
        raise
    except Exception as e:
        log_api_error("toggle_plugin", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Config Management Endpoints
# ============================================


class CvarUpdate(BaseModel):
    """CVAR update request"""

    cvars: dict  # Dict of cvar_name -> value


@router.get("/{server_id}/config/server")
async def get_server_config(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get server.cfg parsed into CVARs

    Returns:
        - cvars: Dict of CVAR name -> value
        - categorized: CVARs grouped by category
    """
    try:
        # Get server and verify ownership
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.config_service import ConfigService

        config_service = ConfigService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        cvars = config_service.parse_server_cfg(server_path)

        # Categorize CVARs for better UI
        categorized = categorize_cvars(cvars)

        return success_response(
            data={"cvars": cvars, "categorized": categorized, "total": len(cvars)}
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_server_config", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{server_id}/config/server")
async def update_server_config(
    server_id: int,
    request: CvarUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Update server.cfg CVARs

    Args:
        cvars: Dict of CVAR name -> value to update

    Returns:
        Success message
    """
    try:
        # Get server and verify ownership
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.config_service import ConfigService

        config_service = ConfigService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        # Update CVARs (with automatic backup)
        success = config_service.update_server_cfg(server_path, request.cvars, backup=True)

        if not success:
            raise BadRequestError("Config güncellenemedi")

        return success_response(
            message=f"{len(request.cvars)} CVAR başarıyla güncellendi",
            data={"updated_count": len(request.cvars), "restart_required": True},
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("update_server_config", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/config/mapcycle")
async def get_mapcycle(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get mapcycle.txt map list"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.config_service import ConfigService

        config_service = ConfigService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        maps = config_service.get_mapcycle(server_path)

        return success_response(data={"maps": maps, "count": len(maps)})

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_mapcycle", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{server_id}/config/mapcycle")
async def update_mapcycle(
    server_id: int,
    maps: List[str],
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Update mapcycle.txt map list"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.config_service import ConfigService

        config_service = ConfigService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        success = config_service.update_mapcycle(server_path, maps)

        if not success:
            raise BadRequestError("Mapcycle güncellenemedi")

        return success_response(
            message=f"Mapcycle güncellendi ({len(maps)} map)", data={"count": len(maps)}
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("update_mapcycle", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


def categorize_cvars(cvars: dict) -> dict:
    """
    Categorize CVARs for better UI organization

    Returns:
        Dict of category -> list of {name, value, description}
    """
    categories = {
        "server": {"name": "Server Settings", "cvars": []},
        "game": {"name": "Game Settings", "cvars": []},
        "network": {"name": "Network Settings", "cvars": []},
        "security": {"name": "Security", "cvars": []},
        "other": {"name": "Other", "cvars": []},
    }

    # CVAR definitions with categories
    cvar_metadata = {
        "hostname": {
            "category": "server",
            "description": "Server name (appears in browser)",
            "type": "string",
        },
        "rcon_password": {
            "category": "security",
            "description": "RCON password for remote control",
            "type": "password",
        },
        "sv_password": {
            "category": "security",
            "description": "Join password (empty = no password)",
            "type": "password",
        },
        "maxplayers": {
            "category": "server",
            "description": "Maximum player slots",
            "type": "number",
            "min": 2,
            "max": 32,
        },
        "sv_lan": {
            "category": "network",
            "description": "LAN mode (0=Internet, 1=LAN)",
            "type": "boolean",
        },
        "sv_region": {
            "category": "network",
            "description": (
                "Server region (0=US East, 1=US West, 2=South America, "
                "3=Europe, 4=Asia, 5=Australia, 6=Middle East, "
                "7=Africa, 255=World)"
            ),
            "type": "number",
        },
        "sv_contact": {"category": "server", "description": "Admin contact", "type": "string"},
        "mp_timelimit": {
            "category": "game",
            "description": "Map time limit (minutes)",
            "type": "number",
        },
        "mp_fraglimit": {
            "category": "game",
            "description": "Frag limit to win",
            "type": "number",
        },
        "mp_friendlyfire": {
            "category": "game",
            "description": "Friendly fire (0=off, 1=on)",
            "type": "boolean",
        },
        "sv_gravity": {
            "category": "game",
            "description": "Gravity value (default: 800)",
            "type": "number",
        },
        "sv_airaccelerate": {
            "category": "game",
            "description": "Air acceleration",
            "type": "number",
        },
        "sv_maxspeed": {
            "category": "game",
            "description": "Maximum player speed",
            "type": "number",
        },
        "sv_cheats": {
            "category": "security",
            "description": "Enable cheats (0=off, 1=on)",
            "type": "boolean",
        },
        "sv_allowdownload": {
            "category": "network",
            "description": "Allow client downloads (0=off, 1=on)",
            "type": "boolean",
        },
        "sv_allowupload": {
            "category": "network",
            "description": "Allow client uploads (0=off, 1=on)",
            "type": "boolean",
        },
        "sv_logblocks": {
            "category": "server",
            "description": "Log blocked commands (0=off, 1=on)",
            "type": "boolean",
        },
    }

    # Categorize each CVAR
    for cvar_name, cvar_value in cvars.items():
        metadata = cvar_metadata.get(cvar_name, {})
        category = metadata.get("category", "other")

        categories[category]["cvars"].append(
            {
                "name": cvar_name,
                "value": cvar_value,
                "description": metadata.get("description", ""),
                "type": metadata.get("type", "string"),
                "min": metadata.get("min"),
                "max": metadata.get("max"),
            }
        )

    # Remove empty categories
    return {k: v for k, v in categories.items() if len(v["cvars"]) > 0}


# ============================================
# File Browser Endpoints
# ============================================


class FileOperationRequest(BaseModel):
    """File operation request"""

    path: str


@router.get("/{server_id}/files/browse")
async def browse_files(
    server_id: int,
    path: str = "",
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Browse server files with tree structure

    Args:
        path: Relative path from server root (e.g., "valve/addons")

    Returns:
        - files: List of files/directories
        - current_path: Current directory path
    """
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        server_root = Path(f"/home/gameservers/servers/server_{server_id}")

        # Validate and resolve path (prevent path traversal)
        if path:
            requested_path = (server_root / path).resolve()
            if not str(requested_path).startswith(str(server_root)):
                raise BadRequestError("Geçersiz path")
        else:
            requested_path = server_root

        if not requested_path.exists():
            raise NotFoundError("Dizin bulunamadı")

        # List directory contents
        items = []
        try:
            for item in sorted(requested_path.iterdir()):
                try:
                    stat = item.stat()
                    relative_path = str(item.relative_to(server_root))

                    items.append(
                        {
                            "name": item.name,
                            "path": relative_path,
                            "type": "directory" if item.is_dir() else "file",
                            "size": stat.st_size if item.is_file() else 0,
                            "modified": stat.st_mtime,
                            "is_symlink": item.is_symlink(),
                        }
                    )
                except Exception:
                    continue  # Skip inaccessible items
        except PermissionError:
            raise BadRequestError("Dizine erişim izni yok")

        return success_response(
            data={
                "files": items,
                "current_path": path,
                "parent_path": (
                    str(requested_path.parent.relative_to(server_root))
                    if requested_path != server_root
                    else None
                ),
            }
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("browse_files", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Admin Management Endpoints
# ============================================


class AdminAddRequest(BaseModel):
    """Add admin request"""

    steam_id: str
    flags: str = "abcdefghijklmnopqrstu"
    password: str = ""
    connection_flags: str = "ce"


class BanAddRequest(BaseModel):
    """Add ban request"""

    ban_type: str  # "ip" or "steam_id"
    value: str
    duration: int = 0  # 0 = permanent


@router.get("/{server_id}/admin/users")
async def get_admin_users(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get admin users from users.ini"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        admins = admin_service.parse_users_ini(server_path)

        return success_response(data={"admins": admins, "count": len(admins)})

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_admin_users", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/admin/users")
async def add_admin_user(
    server_id: int,
    request: AdminAddRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Add admin to users.ini"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        success = admin_service.add_admin(
            server_path,
            request.steam_id,
            request.flags,
            request.password,
            request.connection_flags,
        )

        if not success:
            raise BadRequestError("Admin eklenemedi (zaten mevcut olabilir)")

        # Log action
        admin_service.log_action(
            server_id=server_id,
            admin_id=current_user.id,
            action_type="admin_add",
            target_steam_id=request.steam_id,
            reason=f"Flags: {request.flags}",
        )

        return success_response(message=f"Admin eklendi: {request.steam_id}")

    except APIError:
        raise
    except Exception as e:
        log_api_error("add_admin_user", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{server_id}/admin/users/{steam_id}")
async def remove_admin_user(
    server_id: int,
    steam_id: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Remove admin from users.ini"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        success = admin_service.remove_admin(server_path, steam_id)

        if not success:
            raise BadRequestError("Admin silinemedi (bulunamadı)")

        # Log action
        admin_service.log_action(
            server_id=server_id,
            admin_id=current_user.id,
            action_type="admin_remove",
            target_steam_id=steam_id,
        )

        return success_response(message=f"Admin silindi: {steam_id}")

    except APIError:
        raise
    except Exception as e:
        log_api_error("remove_admin_user", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/admin/bans")
async def get_bans(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get ban list from banned.cfg"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        bans = admin_service.parse_banned_cfg(server_path)

        return success_response(data={"bans": bans, "count": len(bans)})

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_bans", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/admin/bans")
async def add_ban(
    server_id: int,
    request: BanAddRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Add ban to banned.cfg"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        if request.ban_type not in ["ip", "steam_id"]:
            raise BadRequestError("Geçersiz ban tipi (ip veya steam_id olmalı)")

        from pathlib import Path

        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        success = admin_service.add_ban(
            server_path, request.ban_type, request.value, request.duration
        )

        if not success:
            raise BadRequestError("Ban eklenemedi (zaten mevcut olabilir)")

        # Log action
        admin_service.log_action(
            server_id=server_id,
            admin_id=current_user.id,
            action_type="ban",
            target_steam_id=request.value if request.ban_type == "steam_id" else None,
            reason=f"{request.ban_type}: {request.value}",
            duration_minutes=request.duration,
        )

        return success_response(
            message=f"Ban eklendi: {request.value} ({request.duration or 'kalıcı'})"
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("add_ban", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{server_id}/admin/bans/{ban_type}/{value}")
async def remove_ban(
    server_id: int,
    ban_type: str,
    value: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Remove ban from banned.cfg"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        success = admin_service.remove_ban(server_path, ban_type, value)

        if not success:
            raise BadRequestError("Ban silinemedi (bulunamadı)")

        # Log action
        admin_service.log_action(
            server_id=server_id,
            admin_id=current_user.id,
            action_type="unban",
            target_steam_id=value if ban_type == "steam_id" else None,
            reason=f"{ban_type}: {value}",
        )

        return success_response(message=f"Ban kaldırıldı: {value}")

    except APIError:
        raise
    except Exception as e:
        log_api_error("remove_ban", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Player Actions Endpoints (Kick/Slay via RCON)
# ============================================


class PlayerActionRequest(BaseModel):
    """Player action request"""

    slot: int
    reason: Optional[str] = ""


@router.post("/{server_id}/players/{slot}/kick")
async def kick_player_rcon(
    server_id: int,
    slot: int,
    request: PlayerActionRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Kick a player via RCON"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        rcon_service = RCONService(db)

        # Execute kick command
        result = await rcon_service.execute(
            server, f"kick #{slot} {request.reason}", current_user.id
        )

        if not result["success"]:
            raise BadRequestError(result.get("error", "Kick komutu başarısız"))

        # Log action

        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        admin_service.log_action(
            server_id=server_id,
            admin_id=current_user.id,
            action_type="kick",
            target_name=f"Slot {slot}",
            reason=request.reason,
        )

        return success_response(message=f"Oyuncu kicklendi (Slot: {slot})")

    except APIError:
        raise
    except Exception as e:
        log_api_error("kick_player_rcon", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/players/{slot}/slay")
async def slay_player_rcon(
    server_id: int,
    slot: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Slay a player via RCON"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        rcon_service = RCONService(db)

        # Execute slay command
        result = await rcon_service.execute(server, f"amx_slay #{slot}", current_user.id)

        if not result["success"]:
            raise BadRequestError(result.get("error", "Slay komutu başarısız"))

        # Log action

        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        admin_service.log_action(
            server_id=server_id,
            admin_id=current_user.id,
            action_type="slay",
            target_name=f"Slot {slot}",
        )

        return success_response(message=f"Oyuncu öldürüldü (Slot: {slot})")

    except APIError:
        raise
    except Exception as e:
        log_api_error("slay_player_rcon", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Map Management Endpoints
# ============================================


class MapcycleUpdateRequest(BaseModel):
    """Mapcycle update request"""

    maps: List[str]


@router.get("/{server_id}/maps/library")
async def get_map_library(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get all available maps (base + custom)

    Returns:
        - maps: List of all maps with metadata
        - base_count: Number of base maps
        - custom_count: Number of custom maps
    """
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        server_path = Path(f"/home/gameservers/servers/server_{server_id}")
        maps_path = server_path / "valve" / "maps"

        all_maps = []
        base_count = 0
        custom_count = 0

        if maps_path.exists():
            # Get custom maps from database
            from app.models.database import CustomMap

            custom_maps_db = db.query(CustomMap).filter_by(server_id=server_id).all()
            custom_map_names = {m.map_name for m in custom_maps_db}

            # Scan .bsp files
            for bsp_file in maps_path.glob("*.bsp"):
                map_name = bsp_file.stem
                is_custom = map_name in custom_map_names

                # Get custom map details if available
                custom_map = None
                if is_custom:
                    custom_map = next((m for m in custom_maps_db if m.map_name == map_name), None)

                map_info = {
                    "name": map_name,
                    "display_name": custom_map.display_name if custom_map else map_name,
                    "is_custom": is_custom,
                    "file_size": bsp_file.stat().st_size,
                    "is_symlink": bsp_file.is_symlink(),
                }

                # Add custom map metadata if available
                if custom_map:
                    map_info.update(
                        {
                            "thumbnail_url": custom_map.thumbnail_url,
                            "description": custom_map.description,
                            "author": custom_map.author,
                            "play_count": custom_map.play_count,
                        }
                    )
                    custom_count += 1
                else:
                    base_count += 1

                all_maps.append(map_info)

        # Sort alphabetically
        all_maps.sort(key=lambda x: x["name"])

        return success_response(
            data={
                "maps": all_maps,
                "total": len(all_maps),
                "base_count": base_count,
                "custom_count": custom_count,
            }
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_map_library", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/maps/mapcycle")
async def get_mapcycle_maps(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get current mapcycle"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.config_service import ConfigService

        config_service = ConfigService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        maps = config_service.get_mapcycle(server_path)

        return success_response(data={"maps": maps, "count": len(maps)})

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_mapcycle_maps", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{server_id}/maps/mapcycle")
async def update_mapcycle_maps(
    server_id: int,
    request: MapcycleUpdateRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Update mapcycle with drag-drop reordered maps"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.services.config_service import ConfigService

        config_service = ConfigService(db)
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        success = config_service.update_mapcycle(server_path, request.maps)

        if not success:
            raise BadRequestError("Mapcycle güncellenemedi")

        return success_response(
            message=f"Mapcycle güncellendi ({len(request.maps)} map)",
            data={"count": len(request.maps)},
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("update_mapcycle_maps", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# BACKUP MANAGEMENT
# ============================================


@router.get("/{server_id}/backups")
async def list_server_backups(
    server_id: int,
    backup_type: Optional[str] = Query(None, description="Filter: config, full, database"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """List all backups for server"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from app.tasks.backup import backup_manager

        all_backups = backup_manager.list_backups(backup_type=backup_type)

        # Filter server-specific backups
        server_backups = [
            b
            for b in all_backups
            if f"server_{server_id}_" in b["filename"]
            or (backup_type == "database" and b["type"] == "database")
        ]

        return success_response(
            data={
                "backups": server_backups,
                "count": len(server_backups),
                "total_size": sum(b["size"] for b in server_backups),
            }
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("list_server_backups", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/backups/create")
async def create_server_backup(
    server_id: int,
    backup_type: str = Query(..., description="Type: config or full"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Create manual backup (config or full)"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        if backup_type not in ["config", "full"]:
            raise BadRequestError("Geçersiz yedek tipi (config veya full)")

        from pathlib import Path

        from app.tasks.backup import backup_manager

        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        if not server_path.exists():
            raise NotFoundError("Sunucu dizini bulunamadı")

        if backup_type == "config":
            result = await backup_manager.backup_server_configs(server_id, str(server_path))
        else:
            result = await backup_manager.backup_full_server(server_id, str(server_path))

        if not result["success"]:
            raise BadRequestError(result.get("error", "Yedekleme başarısız"))

        # Log action
        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        await admin_service.log_action(
            server_id=server_id,
            user_id=current_user.id,
            action_type="backup_create",
            details={"backup_type": backup_type, "filename": result["filename"]},
        )

        return success_response(
            message=f"{backup_type.capitalize()} yedek oluşturuldu",
            data={"backup": result},
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("create_server_backup", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/backups/{filename}/restore")
async def restore_server_backup(
    server_id: int,
    filename: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Restore server from backup"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.tasks.backup import BACKUP_DIR

        backup_path = Path(BACKUP_DIR) / filename

        if not backup_path.exists():
            raise NotFoundError("Yedek dosyası bulunamadı")

        # Verify file belongs to this server
        if f"server_{server_id}_" not in filename:
            raise ForbiddenError("Bu yedek bu sunucuya ait değil")

        # Extract backup
        import tarfile

        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        # Safe extraction helper
        def safe_extract(tar, path):
            """Extract tar safely, filtering dangerous members"""
            for member in tar.getmembers():
                # Prevent path traversal
                if member.name.startswith("/") or ".." in member.name:
                    continue
                tar.extract(member, path)

        if "_config_" in filename:
            # Restore configs only
            with tarfile.open(backup_path, "r:gz") as tar:
                safe_extract(tar, server_path / "valve" / "addons" / "amxmodx" / "configs")
                safe_extract(tar, server_path / "valve")

            restore_type = "config"

        elif "_full_" in filename:
            # Full restore - extract to temp then move
            import shutil
            import tempfile

            with tempfile.TemporaryDirectory() as tmpdir:
                with tarfile.open(backup_path, "r:gz") as tar:
                    safe_extract(tar, tmpdir)

                # Move extracted files
                extracted_dir = Path(tmpdir) / f"server_{server_id}"
                if extracted_dir.exists():
                    shutil.copytree(extracted_dir, server_path, dirs_exist_ok=True)

            restore_type = "full"
        else:
            raise BadRequestError("Geçersiz yedek tipi")

        # Log action
        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        await admin_service.log_action(
            server_id=server_id,
            user_id=current_user.id,
            action_type="backup_restore",
            details={"filename": filename, "restore_type": restore_type},
        )

        return success_response(
            message=f"{restore_type.capitalize()} yedek geri yüklendi",
            data={"filename": filename},
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("restore_server_backup", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{server_id}/backups/{filename}")
async def delete_server_backup(
    server_id: int,
    filename: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Delete a backup file"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        from app.tasks.backup import BACKUP_DIR

        backup_path = Path(BACKUP_DIR) / filename

        if not backup_path.exists():
            raise NotFoundError("Yedek dosyası bulunamadı")

        # Verify file belongs to this server (unless database backup)
        if "db_backup" not in filename and f"server_{server_id}_" not in filename:
            raise ForbiddenError("Bu yedek bu sunucuya ait değil")

        # Delete file
        file_size = backup_path.stat().st_size
        backup_path.unlink()

        # Log action
        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        await admin_service.log_action(
            server_id=server_id,
            user_id=current_user.id,
            action_type="backup_delete",
            details={"filename": filename},
        )

        return success_response(
            message="Yedek silindi",
            data={"filename": filename, "size": file_size},
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("delete_server_backup", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/backups/schedule")
async def get_backup_schedule(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get backup schedule settings"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        # For now return default schedule (can be made configurable later)
        schedule = {
            "enabled": True,
            "config_backup": {"interval": "daily", "time": "03:00", "retention_days": 30},
            "full_backup": {
                "interval": "weekly",
                "day": "sunday",
                "time": "04:00",
                "retention_days": 90,
            },
        }

        return success_response(data={"schedule": schedule})

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_backup_schedule", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PLUGIN COMPILER (Phase 2 - Feature #11)
# ============================================


class CompilePluginRequest(BaseModel):
    """Plugin compilation request"""

    source_code: str = Field(..., description=".sma source code")
    plugin_name: str = Field(..., min_length=1, max_length=50, description="Plugin name")


@router.post("/{server_id}/plugins/compile")
async def compile_plugin(
    server_id: int,
    request: CompilePluginRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Compile .sma plugin to .amxx"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from app.services.plugin_compiler_service import PluginCompilerService

        compiler = PluginCompilerService()

        if not compiler.is_compiler_available():
            raise BadRequestError(
                "AMXModX compiler sunucuda kurulu değil. " "Lütfen yönetici ile iletişime geçin."
            )

        # Compile
        result = compiler.compile_plugin(request.source_code, request.plugin_name)

        if not result["success"]:
            return success_response(
                message="Derleme başarısız",
                data={
                    "success": False,
                    "error": result["error"],
                    "warnings": result.get("warnings", []),
                },
            )

        # Convert binary to base64 for JSON transfer
        import base64

        compiled_base64 = base64.b64encode(result["compiled_data"]).decode("utf-8")

        # Log compilation
        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        await admin_service.log_action(
            server_id=server_id,
            user_id=current_user.id,
            action_type="plugin_compile",
            details={"plugin_name": request.plugin_name},
        )

        return success_response(
            message="Plugin başarıyla derlendi",
            data={
                "success": True,
                "compiled_data": compiled_base64,
                "filename": f"{request.plugin_name}.amxx",
                "warnings": result.get("warnings", []),
                "output": result.get("output", ""),
            },
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("compile_plugin", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/plugins/validate")
async def validate_plugin_syntax(
    server_id: int,
    request: CompilePluginRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Validate plugin syntax without compiling"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from app.services.plugin_compiler_service import PluginCompilerService

        compiler = PluginCompilerService()

        if not compiler.is_compiler_available():
            raise BadRequestError("AMXModX compiler sunucuda kurulu değil")

        # Validate
        result = compiler.validate_syntax(request.source_code)

        return success_response(
            message="Syntax kontrolü tamamlandı",
            data={
                "valid": result["valid"],
                "errors": result["errors"],
                "warnings": result["warnings"],
            },
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("validate_plugin_syntax", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/plugins/compiler-info")
async def get_compiler_info(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get compiler availability and version"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from app.services.plugin_compiler_service import PluginCompilerService

        compiler = PluginCompilerService()

        return success_response(
            data={
                "available": compiler.is_compiler_available(),
                "version": compiler.get_compiler_version(),
                "compiler_path": str(compiler.compiler_path),
            }
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_compiler_info", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PLUGIN CONFIG EDITOR (Phase 2 - Feature #12)
# ============================================


@router.get("/{server_id}/plugins/configs/list")
async def list_plugin_configs(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """List all available plugin config files"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        server_path = Path(f"/home/gameservers/servers/server_{server_id}")
        configs_path = server_path / "valve" / "addons" / "amxmodx" / "configs"

        if not configs_path.exists():
            return success_response(data={"configs": []})

        # List .ini and .cfg files
        config_files = []
        for ext in ["*.ini", "*.cfg"]:
            for file in configs_path.glob(ext):
                # Skip some system files
                if file.name in ["core.ini", "sql.ini", "modules.ini"]:
                    continue

                config_files.append(
                    {
                        "name": file.name,
                        "path": str(file.relative_to(server_path)),
                        "size": file.stat().st_size,
                        "modified": file.stat().st_mtime,
                    }
                )

        # Sort by name
        config_files.sort(key=lambda x: x["name"])

        return success_response(data={"configs": config_files, "count": len(config_files)})

    except APIError:
        raise
    except Exception as e:
        log_api_error("list_plugin_configs", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/plugins/configs/{filename}")
async def get_plugin_config(
    server_id: int,
    filename: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get plugin config file content"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        server_path = Path(f"/home/gameservers/servers/server_{server_id}")
        config_path = server_path / "valve" / "addons" / "amxmodx" / "configs" / filename

        # Validate path (prevent traversal)
        config_path = config_path.resolve()
        if not str(config_path).startswith(
            str(server_path / "valve" / "addons" / "amxmodx" / "configs")
        ):
            raise ForbiddenError("Path traversal detected")

        if not config_path.exists():
            raise NotFoundError("Config dosyası bulunamadı")

        # Read file
        with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Parse as key-value if .ini
        parsed_data = None
        if filename.endswith(".ini"):
            parsed_data = parse_ini_content(content)

        return success_response(
            data={
                "filename": filename,
                "content": content,
                "parsed": parsed_data,
                "size": config_path.stat().st_size,
            }
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_plugin_config", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


class UpdatePluginConfigRequest(BaseModel):
    """Update plugin config request"""

    content: str = Field(..., description="New config content")


@router.put("/{server_id}/plugins/configs/{filename}")
async def update_plugin_config(
    server_id: int,
    filename: str,
    request: UpdatePluginConfigRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Update plugin config file"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        server_path = Path(f"/home/gameservers/servers/server_{server_id}")
        config_path = server_path / "valve" / "addons" / "amxmodx" / "configs" / filename

        # Validate path
        config_path = config_path.resolve()
        if not str(config_path).startswith(
            str(server_path / "valve" / "addons" / "amxmodx" / "configs")
        ):
            raise ForbiddenError("Path traversal detected")

        if not config_path.exists():
            raise NotFoundError("Config dosyası bulunamadı")

        # Backup original
        import shutil

        backup_path = config_path.with_suffix(config_path.suffix + ".backup")
        shutil.copy2(config_path, backup_path)

        # Write new content
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(request.content)

        # Log action
        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        await admin_service.log_action(
            server_id=server_id,
            user_id=current_user.id,
            action_type="plugin_config_update",
            details={"filename": filename},
        )

        return success_response(
            message=f"{filename} güncellendi",
            data={"filename": filename, "backup": str(backup_path)},
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("update_plugin_config", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


def parse_ini_content(content: str) -> dict:
    """Parse INI content into key-value pairs"""
    parsed = {"sections": {}, "globals": []}
    current_section = None

    for line in content.split("\n"):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith(";") or line.startswith("#"):
            continue

        # Section header
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            parsed["sections"][current_section] = []
            continue

        # Key-value pair
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"')

            entry = {"key": key, "value": value, "line": line}

            if current_section:
                parsed["sections"][current_section].append(entry)
            else:
                parsed["globals"].append(entry)

    return parsed


# ============================================
# PLUGIN LOGS VIEWER (Phase 2 - Feature #13)
# ============================================


@router.get("/{server_id}/plugins/logs/list")
async def list_plugin_logs(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """List available plugin log files"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        server_path = Path(f"/home/gameservers/servers/server_{server_id}")
        logs_path = server_path / "valve" / "addons" / "amxmodx" / "logs"

        if not logs_path.exists():
            return success_response(data={"logs": []})

        # List log files
        log_files = []
        for file in logs_path.glob("*.log"):
            log_files.append(
                {
                    "name": file.name,
                    "path": str(file.relative_to(server_path)),
                    "size": file.stat().st_size,
                    "modified": file.stat().st_mtime,
                }
            )

        # Sort by modified time (newest first)
        log_files.sort(key=lambda x: x["modified"], reverse=True)

        return success_response(data={"logs": log_files, "count": len(log_files)})

    except APIError:
        raise
    except Exception as e:
        log_api_error("list_plugin_logs", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/plugins/logs/{filename}")
async def get_plugin_log(
    server_id: int,
    filename: str,
    lines: int = Query(500, ge=1, le=5000, description="Number of lines to read"),
    level: Optional[str] = Query(None, description="Filter by level (error, warning, info)"),
    search: Optional[str] = Query(None, description="Search term"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get plugin log content with filtering"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        server_path = Path(f"/home/gameservers/servers/server_{server_id}")
        log_path = server_path / "valve" / "addons" / "amxmodx" / "logs" / filename

        # Validate path
        log_path = log_path.resolve()
        if not str(log_path).startswith(str(server_path / "valve" / "addons" / "amxmodx" / "logs")):
            raise ForbiddenError("Path traversal detected")

        if not log_path.exists():
            raise NotFoundError("Log dosyası bulunamadı")

        # Read file (last N lines)
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()

        # Get last N lines
        log_lines = all_lines[-lines:]

        # Parse log entries
        entries = []
        for line in log_lines:
            parsed = parse_log_line(line)
            if parsed:
                # Filter by level
                if level and parsed["level"].lower() != level.lower():
                    continue

                # Filter by search term
                if search and search.lower() not in parsed["message"].lower():
                    continue

                entries.append(parsed)

        return success_response(
            data={
                "filename": filename,
                "entries": entries,
                "total_lines": len(all_lines),
                "filtered_lines": len(entries),
            }
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("get_plugin_log", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{server_id}/plugins/logs/{filename}")
async def delete_plugin_log(
    server_id: int,
    filename: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Delete a plugin log file"""
    try:
        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise NotFoundError("Sunucu bulunamadı")
        validate_server_ownership(server, current_user)

        from pathlib import Path

        server_path = Path(f"/home/gameservers/servers/server_{server_id}")
        log_path = server_path / "valve" / "addons" / "amxmodx" / "logs" / filename

        # Validate path
        log_path = log_path.resolve()
        if not str(log_path).startswith(str(server_path / "valve" / "addons" / "amxmodx" / "logs")):
            raise ForbiddenError("Path traversal detected")

        if not log_path.exists():
            raise NotFoundError("Log dosyası bulunamadı")

        # Delete file
        file_size = log_path.stat().st_size
        log_path.unlink()

        # Log action
        from app.services.admin_service import AdminService

        admin_service = AdminService(db)
        await admin_service.log_action(
            server_id=server_id,
            user_id=current_user.id,
            action_type="plugin_log_delete",
            details={"filename": filename},
        )

        return success_response(
            message="Log dosyası silindi", data={"filename": filename, "size": file_size}
        )

    except APIError:
        raise
    except Exception as e:
        log_api_error("delete_plugin_log", e, current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


def parse_log_line(line: str) -> Optional[dict]:
    """Parse AMXModX log line into structured format"""
    import re
    from datetime import datetime

    line = line.strip()
    if not line:
        return None

    # AMXModX log format: L 01/31/2026 - 12:34:56: [MODULE] Message
    # Or: L 01/31/2026 - 12:34:56: Message
    pattern = r"L (\d{2}/\d{2}/\d{4}) - (\d{2}:\d{2}:\d{2}): (?:\[([^\]]+)\] )?(.*)"
    match = re.match(pattern, line)

    if not match:
        # Not a standard log line, return as raw
        return {"timestamp": None, "level": "info", "module": None, "message": line, "raw": line}

    date_str, time_str, module, message = match.groups()

    # Determine log level from message
    level = "info"
    if any(keyword in message.lower() for keyword in ["error", "fatal", "failed"]):
        level = "error"
    elif any(keyword in message.lower() for keyword in ["warning", "warn"]):
        level = "warning"

    # Parse timestamp
    try:
        timestamp_str = f"{date_str} {time_str}"
        timestamp = datetime.strptime(timestamp_str, "%m/%d/%Y %H:%M:%S")
    except Exception:
        timestamp = None

    return {
        "timestamp": timestamp.isoformat() if timestamp else None,
        "level": level,
        "module": module,
        "message": message.strip(),
        "raw": line,
    }
