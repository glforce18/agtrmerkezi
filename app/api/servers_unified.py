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
                    "ip": s.ip_address,
                    "port": s.port,
                    "game": s.game_type.value if s.game_type else "unknown",
                    "status": s.status.value if s.status else "unknown",
                    "current_players": s.current_players or 0,
                    "max_players": s.slots,
                    "map": s.current_map,
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

        if result:
            return success_response(message="Server is starting")
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
            raise NotFoundError("Server not found")

        validate_server_ownership(server, current_user)

        if server.status != ServerStatus.RUNNING:
            raise BadRequestError("Server is not running")

        control_service = ServerControlService(db)
        result = await control_service.stop_server(server_id)

        if result:
            return success_response(message="Server is stopping")
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
            raise NotFoundError("Server not found")

        validate_server_ownership(server, current_user)

        control_service = ServerControlService(db)
        result = await control_service.restart_server(server_id)

        if result:
            return success_response(message="Server is restarting")
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
            raise NotFoundError("Server not found")

        validate_server_ownership(server, current_user)

        if server.status != ServerStatus.RUNNING:
            raise BadRequestError("Server is not running")

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
                """Background task to install server"""
                from app.models.connection import SessionLocal
                from app.models.database import Notification
                from app.services.server_installation import ServerInstallationService

                task_db = SessionLocal()
                try:
                    install_service = ServerInstallationService(task_db)

                    # Create installation record
                    installation = await install_service.create_installation(
                        server_id=server.id,
                        user_id=current_user.id,
                        mod_type=server.game_type.value,
                        config={},
                    )

                    # Run installation
                    config = {
                        "hostname": server.name,
                        "rcon_password": server.rcon_password,
                        "port": server.port,
                        "maxplayers": server.slots,
                        "admins": [],
                    }

                    success, msg = await install_service.run_installation(installation.id, config)

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
                                message=f"{server.name} sunucunuz kuruldu ve başlatılmaya hazır.",
                                link=f"/servers/{server.id}",
                            )
                            task_db.add(notification)
                            task_db.commit()

                            logger.info(f"Server installation completed: {server.id}")
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

        # Trigger server installation (background task)
        async def trigger_installation():
            """Background task to install server"""
            from app.models.connection import SessionLocal
            from app.models.database import Notification
            from app.services.server_installation import ServerInstallationService

            task_db = SessionLocal()
            try:
                install_service = ServerInstallationService(task_db)

                # Create installation record
                installation = await install_service.create_installation(
                    server_id=server.id,
                    user_id=current_user.id,
                    mod_type=server.game_type.value,
                    config={},
                )

                # Run installation
                config = {
                    "hostname": server.name,
                    "rcon_password": server.rcon_password,
                    "port": server.port,
                    "maxplayers": server.slots,
                    "admins": [],
                }

                success, msg = await install_service.run_installation(installation.id, config)

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
                            message=f"{server.name} sunucunuz kuruldu ve başlatılmaya hazır.",
                            link=f"/servers/{server.id}",
                        )
                        task_db.add(notification)
                        task_db.commit()

                        logger.info(f"Server installation completed: {server.id}")
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
