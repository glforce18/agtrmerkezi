"""
AGTR Merkezi - Unified Server Management API
Combines legacy servers.py and server_v2.py into clean, maintainable API
"""

import hashlib
import logging
import os
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
