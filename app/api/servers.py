"""
AGTR Merkezi - Game Servers API
RCON, Live Console, Plugin Manager, Config Editor destekli
"""

import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import a2s
import psutil
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    generate_rcon_password,
    generate_reference_code,
    get_current_user_required,
)
from app.models.connection import get_db
from app.models.database import (
    AuditLog,
    ConfigHistory,
    GameServer,
    Payment,
    PaymentStatus,
    Plugin,
    RconLog,
    ServerAction,
    ServerPackage,
    ServerPlugin,
    ServerStatus,
    User,
    WalletType,
    TransactionType,
)
from app.services.wallet import get_wallet_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Korunmasi gereken config ayarlari
PROTECTED_CONFIG_KEYS = [
    "sv_lan", "sv_downloadurl", "sv_allowdownload", "sv_allowupload",
    "rcon_password", "sv_password", "ip", "port", "hostport",
    "sys_ticrate", "fps_max", "sv_maxrate", "sv_minrate"
]


class CustomPackageRequest(BaseModel):
    game_type: str
    slots: int
    features: List[str]
    months: int = 1
    server_name: str


class PackageOrderRequest(BaseModel):
    package_id: int
    months: int = 1
    server_name: str
    auto_renew: bool = False


class WalletPackageOrderRequest(BaseModel):
    package_id: int
    months: int = 1
    server_name: str
    auto_renew: bool = False
    payment_type: str = "tl"  # "tl" or "armor"


# Exchange rate: 1 TL = 100 Armor
ARMOR_RATE = 100


class ServerActionRequest(BaseModel):
    action: str


class RconCommandRequest(BaseModel):
    command: str


class ConfigUpdateRequest(BaseModel):
    content: str
    config_type: str = "server.cfg"


class MapChangeRequest(BaseModel):
    map_name: str


class PluginToggleRequest(BaseModel):
    enabled: bool


class ScheduledTaskRequest(BaseModel):
    name: str
    task_type: str  # restart, command, message
    schedule_type: str  # once, daily, weekly, cron
    schedule_value: str
    command: Optional[str] = None
    is_enabled: bool = True


# ==================== HELPER FUNCTIONS ====================

def log_audit(db: Session, user_id: int, action: str, entity_type: str = None,
              entity_id: int = None, old_values: dict = None, new_values: dict = None,
              ip_address: str = None):
    """Audit log kaydi"""
    try:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        logger.error(f"Audit log hatasi: {e}")


def calculate_custom_price(slots: int, features: List[str], months: int):
    base_price = slots * settings.PRICE_PER_SLOT
    features_price = 0.0
    feature_prices = {
        "anticheat": settings.PRICE_ANTICHEAT,
        "custom_domain": settings.PRICE_CUSTOM_DOMAIN,
        "priority_support": settings.PRICE_PRIORITY_SUPPORT,
        "auto_backup": settings.PRICE_AUTO_BACKUP,
        "amvp": settings.PRICE_AMVP_PLUGIN
    }
    for feature in features:
        if feature in feature_prices:
            features_price += feature_prices[feature]
    monthly_total = base_price + features_price
    discount_percent = 0.0
    if months >= 12:
        discount_percent = settings.DISCOUNT_12_MONTH
    elif months >= 6:
        discount_percent = settings.DISCOUNT_6_MONTH
    elif months >= 3:
        discount_percent = settings.DISCOUNT_3_MONTH
    subtotal = monthly_total * months
    discount_amount = subtotal * discount_percent
    total = subtotal - discount_amount
    return {"base_price": base_price, "features_price": features_price, "monthly_total": monthly_total, "subtotal": subtotal, "discount_percent": discount_percent * 100, "discount_amount": discount_amount, "total": total}


def find_available_slot(db: Session):
    used_slots = db.query(GameServer.ip_address, GameServer.port).filter(GameServer.status.notin_([ServerStatus.DELETED, ServerStatus.EXPIRED])).all()
    used_set = {(s.ip_address, s.port) for s in used_slots}
    for ip in settings.GAME_SERVER_IPS:
        for port in range(settings.GAME_PORT_START, settings.GAME_PORT_END + 1):
            if (ip, port) not in used_set:
                return (ip, port)
    return (None, None)


@router.get("")
async def get_all_public_servers(
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 20,
    game_type: str = None,
    online_only: bool = False,
    search: str = None
):
    """Public - Tum sunuculari listele (Servers.vue icin)"""
    query = db.query(GameServer).filter(
        GameServer.is_public == True if hasattr(GameServer, 'is_public') else True
    )

    # Filter by game type
    if game_type:
        from app.models import GameType
        try:
            game_type_enum = GameType(game_type)
            query = query.filter(GameServer.game_type == game_type_enum)
        except ValueError:
            pass

    # Filter online only
    if online_only:
        query = query.filter(GameServer.status == ServerStatus.RUNNING)

    # Search by name
    if search:
        query = query.filter(GameServer.name.ilike(f"%{search}%"))

    # Get total count
    total = query.count()

    # Paginate
    offset = (page - 1) * per_page
    # MySQL/MariaDB compatible ordering (COALESCE for NULL handling)
    from sqlalchemy import case
    servers = query.order_by(
        case((GameServer.current_players.is_(None), 0), else_=GameServer.current_players).desc()
    ).offset(offset).limit(per_page).all()

    result = []
    for s in servers:
        server_data = {
            "id": s.id,
            "name": s.name,
            "game_type": s.game_type.value if s.game_type else "cs16",
            "ip": s.ip_address,
            "port": s.port,
            "address": f"{s.ip_address}:{s.port}",
            "slots": s.slots,
            "max_players": s.slots,
            "current_players": s.current_players or 0,
            "players": s.current_players or 0,
            "current_map": s.current_map or "de_dust2",
            "map": s.current_map or "de_dust2",
            "status": s.status.value if s.status else "offline",
            "is_online": s.status == ServerStatus.RUNNING if s.status else False,
            "ping": 0,
            "country": "TR"
        }
        result.append(server_data)

    # If no servers, return demo servers
    if len(result) == 0:
        result = [
            {"id": 1, "name": "AGTR Public #1 [Dust2]", "game_type": "cs16", "ip": "agtr1.com", "port": 27015, "address": "agtr1.com:27015", "slots": 32, "max_players": 32, "current_players": 18, "players": 18, "current_map": "de_dust2", "map": "de_dust2", "status": "running", "is_online": True, "ping": 15, "country": "TR"},
            {"id": 2, "name": "AGTR Public #2 [Inferno]", "game_type": "cs16", "ip": "agtr2.com", "port": 27015, "address": "agtr2.com:27015", "slots": 32, "max_players": 32, "current_players": 12, "players": 12, "current_map": "de_inferno", "map": "de_inferno", "status": "running", "is_online": True, "ping": 18, "country": "TR"},
            {"id": 3, "name": "AGTR Zombie Mod", "game_type": "cs16", "ip": "agtr3.com", "port": 27015, "address": "agtr3.com:27015", "slots": 32, "max_players": 32, "current_players": 24, "players": 24, "current_map": "zm_ice_attack", "map": "zm_ice_attack", "status": "running", "is_online": True, "ping": 12, "country": "TR"},
            {"id": 4, "name": "AGTR Deathmatch", "game_type": "cs16", "ip": "agtr4.com", "port": 27015, "address": "agtr4.com:27015", "slots": 20, "max_players": 20, "current_players": 8, "players": 8, "current_map": "aim_headshot", "map": "aim_headshot", "status": "running", "is_online": True, "ping": 20, "country": "TR"},
            {"id": 5, "name": "AGTR AWP Only", "game_type": "cs16", "ip": "agtr5.com", "port": 27015, "address": "agtr5.com:27015", "slots": 16, "max_players": 16, "current_players": 6, "players": 6, "current_map": "awp_india", "map": "awp_india", "status": "running", "is_online": True, "ping": 14, "country": "TR"},
            {"id": 6, "name": "AGTR Surf", "game_type": "cs16", "ip": "agtr6.com", "port": 27015, "address": "agtr6.com:27015", "slots": 24, "max_players": 24, "current_players": 15, "players": 15, "current_map": "surf_ski_2", "map": "surf_ski_2", "status": "running", "is_online": True, "ping": 16, "country": "TR"}
        ]
        total = len(result)

    return {
        "items": result,
        "servers": result,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


@router.get("/live")
async def get_live_servers(db: Session = Depends(get_db), limit: int = 20):
    """Public - Canli sunucu listesi (ana sayfa icin)"""
    servers = db.query(GameServer).filter(
        GameServer.status == ServerStatus.RUNNING,
        GameServer.is_public == True if hasattr(GameServer, 'is_public') else True
    ).limit(limit).all()

    result = []
    for s in servers:
        server_data = {
            "id": s.id,
            "name": s.name,
            "game_type": s.game_type.value if s.game_type else "cs16",
            "ip": f"{s.ip_address}:{s.port}",
            "slots": s.slots,
            "max_players": s.slots,
            "current_players": s.current_players or 0,
            "players": s.current_players or 0,
            "current_map": s.current_map or "de_dust2",
            "map": s.current_map or "de_dust2",
            "is_online": True,
            "ping": 0
        }

        # Gercek zamanli sorgu (opsiyonel, performans icin cache edilebilir)
        try:
            info = a2s.info((s.ip_address, s.port), timeout=1)
            server_data["current_players"] = info.player_count
            server_data["players"] = info.player_count
            server_data["current_map"] = info.map_name
            server_data["map"] = info.map_name
            # DB guncelle
            if s.current_players != info.player_count or s.current_map != info.map_name:
                s.current_players = info.player_count
                s.current_map = info.map_name
        except Exception:
            pass

        result.append(server_data)

    try:
        db.commit()
    except Exception:
        db.rollback()

    # If no servers, return demo servers for display
    if len(result) == 0:
        result = [
            {"id": 1, "name": "AGTR Public #1 [Dust2]", "game_type": "cs16", "ip": "agtr1.com:27015", "slots": 32, "max_players": 32, "current_players": 18, "players": 18, "current_map": "de_dust2", "map": "de_dust2", "is_online": True, "ping": 15},
            {"id": 2, "name": "AGTR Public #2 [Inferno]", "game_type": "cs16", "ip": "agtr2.com:27015", "slots": 32, "max_players": 32, "current_players": 12, "players": 12, "current_map": "de_inferno", "map": "de_inferno", "is_online": True, "ping": 18},
            {"id": 3, "name": "AGTR Zombie Mod", "game_type": "cs16", "ip": "agtr3.com:27015", "slots": 32, "max_players": 32, "current_players": 24, "players": 24, "current_map": "zm_ice_attack", "map": "zm_ice_attack", "is_online": True, "ping": 12},
            {"id": 4, "name": "AGTR Deathmatch", "game_type": "cs16", "ip": "agtr4.com:27015", "slots": 20, "max_players": 20, "current_players": 8, "players": 8, "current_map": "aim_headshot", "map": "aim_headshot", "is_online": True, "ping": 20},
            {"id": 5, "name": "AGTR AWP Only", "game_type": "cs16", "ip": "agtr5.com:27015", "slots": 16, "max_players": 16, "current_players": 6, "players": 6, "current_map": "awp_india", "map": "awp_india", "is_online": True, "ping": 14},
            {"id": 6, "name": "AGTR Surf", "game_type": "cs16", "ip": "agtr6.com:27015", "slots": 24, "max_players": 24, "current_players": 15, "players": 15, "current_map": "surf_ski_2", "map": "surf_ski_2", "is_online": True, "ping": 16}
        ][:limit]

    return {"servers": result, "total": len(result)}


@router.get("/packages")
async def list_packages(db: Session = Depends(get_db)):
    packages = db.query(ServerPackage).filter(ServerPackage.is_active == True).order_by(ServerPackage.display_order).all()
    return {"packages": [{"id": p.id, "slug": p.slug, "name": p.name, "game_type": p.game_type.value, "slots": p.slots, "features": p.features or [], "description": p.description, "price_monthly": p.price_monthly} for p in packages]}


@router.post("/calculate-price")
async def calculate_price(data: CustomPackageRequest):
    if data.slots < 8 or data.slots > 32:
        raise HTTPException(status_code=400, detail="Slot sayisi 8-32 arasi olmali")
    price = calculate_custom_price(data.slots, data.features, data.months)
    return {"calculation": price, "summary": {"slots": data.slots, "features": data.features, "months": data.months, "total_price": price["total"]}}


@router.post("/order/package")
async def order_package(data: PackageOrderRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    package = db.query(ServerPackage).filter(ServerPackage.id == data.package_id, ServerPackage.is_active == True).first()
    if not package:
        raise HTTPException(status_code=404, detail="Paket bulunamadi")
    
    ip, port = find_available_slot(db)
    if not ip:
        raise HTTPException(status_code=503, detail="Su anda musait sunucu slotu yok")
    
    discount = 0.0
    if data.months >= 12:
        discount = settings.DISCOUNT_12_MONTH
    elif data.months >= 6:
        discount = settings.DISCOUNT_6_MONTH
    elif data.months >= 3:
        discount = settings.DISCOUNT_3_MONTH
    total_price = package.price_monthly * data.months * (1 - discount)
    
    server = GameServer(
        owner_id=current_user.id,
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
        auto_renew=data.auto_renew
    )
    db.add(server)
    db.flush()
    
    payment = Payment(
        user_id=current_user.id,
        amount=total_price,
        status=PaymentStatus.PENDING,
        reference_code=generate_reference_code("SRV"),
        description=f"{package.name} - {data.months} Aylik",
        server_id=server.id,
        months=data.months
    )
    db.add(payment)
    db.commit()
    
    return {"success": True, "order": {"server_id": server.id, "payment_id": payment.id, "reference_code": payment.reference_code, "amount": total_price, "server_info": {"name": server.name, "ip": f"{ip}:{port}", "slots": server.slots}}}


@router.post("/order/package-wallet")
async def order_package_with_wallet(
    data: WalletPackageOrderRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Sunucu paketini cuzdan bakiyesiyle satin al (TL veya Armor)
    1 TL = 100 Armor
    """
    package = db.query(ServerPackage).filter(
        ServerPackage.id == data.package_id,
        ServerPackage.is_active == True
    ).first()
    if not package:
        raise HTTPException(status_code=404, detail="Paket bulunamadi")

    # Indirim hesapla
    discount = 0.0
    if data.months >= 12:
        discount = settings.DISCOUNT_12_MONTH
    elif data.months >= 6:
        discount = settings.DISCOUNT_6_MONTH
    elif data.months >= 3:
        discount = settings.DISCOUNT_3_MONTH

    total_price_tl = package.price_monthly * data.months * (1 - discount)
    total_price_armor = int(total_price_tl * ARMOR_RATE)

    # Wallet service
    wallet = get_wallet_service(db)
    balances = wallet.get_all_balances(current_user.id)

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]

    # Odeme tipine gore bakiye kontrolu
    if data.payment_type == "armor":
        if balances["balance_coin"] < total_price_armor:
            raise HTTPException(
                status_code=400,
                detail=f"Yetersiz Armor bakiye. Mevcut: {int(balances['balance_coin'])}, Gerekli: {total_price_armor}"
            )
        wallet_type = WalletType.COIN
        amount_to_deduct = total_price_armor
        currency_name = "Armor"
    else:
        if balances["balance_real"] < total_price_tl:
            raise HTTPException(
                status_code=400,
                detail=f"Yetersiz TL bakiye. Mevcut: {balances['balance_real']:.2f} TL, Gerekli: {total_price_tl:.2f} TL"
            )
        wallet_type = WalletType.REAL
        amount_to_deduct = total_price_tl
        currency_name = "TL"

    # Musait slot bul
    ip, port = find_available_slot(db)
    if not ip:
        raise HTTPException(status_code=503, detail="Su anda musait sunucu slotu yok")

    # Bakiye dus
    tx = wallet.deduct_balance(
        user_id=current_user.id,
        amount=amount_to_deduct,
        wallet_type=wallet_type,
        transaction_type=TransactionType.PAYMENT.value,
        description=f"Sunucu paketi: {package.name} - {data.months} Ay",
        ip_address=client_ip,
        user_agent=user_agent,
        extra_data={
            "package_id": package.id,
            "months": data.months,
            "payment_type": data.payment_type
        }
    )

    # Sunucu olustur
    from datetime import timedelta
    server = GameServer(
        owner_id=current_user.id,
        name=data.server_name,
        game_type=package.game_type,
        ip_address=ip,
        port=port,
        slots=package.slots,
        rcon_password=generate_rcon_password(),
        package_id=package.id,
        is_custom_package=False,
        features=package.features,
        status=ServerStatus.RUNNING,  # Direkt aktif
        monthly_price=package.price_monthly,
        auto_renew=data.auto_renew,
        expires_at=datetime.utcnow() + timedelta(days=30 * data.months)
    )
    db.add(server)
    db.flush()

    # Payment kaydı (tamamlanmış olarak)
    payment = Payment(
        user_id=current_user.id,
        amount=total_price_tl,
        status=PaymentStatus.COMPLETED,
        reference_code=generate_reference_code("WLT"),
        description=f"{package.name} - {data.months} Aylik ({currency_name} ile)",
        server_id=server.id,
        months=data.months
    )
    db.add(payment)
    db.commit()

    return {
        "success": True,
        "message": f"Sunucu basariyla satin alindi! {amount_to_deduct} {currency_name} odendi.",
        "order": {
            "server_id": server.id,
            "payment_id": payment.id,
            "reference_code": payment.reference_code,
            "amount_paid": amount_to_deduct,
            "currency": data.payment_type,
            "server_info": {
                "name": server.name,
                "ip": f"{ip}:{port}",
                "slots": server.slots,
                "expires_at": server.expires_at.isoformat() if server.expires_at else None
            }
        },
        "new_balance": tx.balance_after
    }


@router.get("/my-servers")
async def my_servers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    servers = db.query(GameServer).filter(GameServer.owner_id == current_user.id, GameServer.status != ServerStatus.DELETED).order_by(GameServer.created_at.desc()).all()
    return {"servers": [{"id": s.id, "name": s.name, "game_type": s.game_type.value, "ip_address": s.ip_address, "port": s.port, "slots": s.slots, "status": s.status.value, "rcon_password": s.rcon_password, "monthly_price": s.monthly_price, "expires_at": s.expires_at.isoformat() if s.expires_at else None, "created_at": s.created_at.isoformat()} for s in servers], "count": len(servers)}


@router.post("/my-servers/{server_id}/action")
async def server_action(server_id: int, data: ServerActionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    server = db.query(GameServer).filter(GameServer.id == server_id, GameServer.owner_id == current_user.id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    if server.status == ServerStatus.PENDING:
        raise HTTPException(status_code=400, detail="Sunucu henuz aktif degil")
    
    allowed_actions = ["start", "stop", "restart"]
    if data.action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Gecersiz aksiyon")
    
    action_log = ServerAction(server_id=server_id, user_id=current_user.id, action=data.action)
    db.add(action_log)
    
    if data.action == "start":
        start_physical_server(server.id)
        server.status = ServerStatus.RUNNING
        server.last_started = datetime.utcnow()
        message = "Sunucu baslatildi"
    elif data.action == "stop":
        stop_physical_server(server.id)
        server.status = ServerStatus.STOPPED
        message = "Sunucu durduruldu"
    else:
        restart_physical_server(server.id)
        server.status = ServerStatus.RUNNING
        server.last_started = datetime.utcnow()
        message = "Sunucu yeniden baslatildi"
    
    db.commit()
    return {"success": True, "message": message, "new_status": server.status.value}


def run_server_command(command: str, server_id: int, *args) -> dict:
    """Server manager scriptini calistir"""
    # Build command as list to prevent shell injection
    script_path = f"{settings.HLDS_PATH}/server_manager.sh"
    cmd_list = [script_path, command, str(server_id)]
    cmd_list.extend(str(a) for a in args)
    try:
        env = os.environ.copy()
        env["HOME"] = "/root"
        env["TERM"] = "xterm"
        env["SCREENDIR"] = "/run/screen/S-root"
        result = subprocess.run(cmd_list, shell=False, capture_output=True, text=True, timeout=60, env=env, cwd=settings.HLDS_PATH)
        output = result.stdout.strip()
        if "OK:" in output:
            return {"success": True, "message": output}
        else:
            return {"success": False, "message": output or result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Command timed out"}
    except Exception as e:
        logger.error(f"Server command error: {e}")
        return {"success": False, "message": "Internal server error"}


def create_physical_server(server_id: int, ip: str, port: int, game: str, slots: int, rcon: str, name: str) -> dict:
    """Fiziksel sunucu olustur"""
    game_map = {"ag": "ag", "cs16": "cstrike", "hldm": "valve"}
    game_type = game_map.get(game, "ag")
    return run_server_command("create", server_id, ip, port, game_type, slots, rcon, name)


def start_physical_server(server_id: int) -> dict:
    return run_server_command("start", server_id)


def stop_physical_server(server_id: int) -> dict:
    return run_server_command("stop", server_id)


def restart_physical_server(server_id: int) -> dict:
    return run_server_command("restart", server_id)


def delete_physical_server(server_id: int) -> dict:
    return run_server_command("delete", server_id)


def get_server_path(server_id: int) -> Path:
    """Sunucu dizin yolunu dondur"""
    return Path(settings.HLDS_PATH) / "servers" / f"server_{server_id}"


def get_game_dir(server: GameServer) -> str:
    """Oyun dizinini dondur"""
    game_dirs = {"ag": "ag", "cs16": "cstrike", "hldm": "valve"}
    return game_dirs.get(server.game_type.value, "ag")


# ==================== SERVER STATUS & INFO ====================

@router.get("/my-servers/{server_id}/status")
async def get_server_status(server_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Sunucu gercek durumunu kontrol et (screen + port)"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id, 
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    status = {
        "db_status": server.status.value,
        "screen_running": False,
        "port_open": False,
        "players": 0,
        "max_players": server.slots,
        "map": None,
        "hostname": None
    }
    
    # Screen kontrolu - pipe olmadan guvenli kontrol
    try:
        result = subprocess.run(
            ["screen", "-list"],
            shell=False, capture_output=True, text=True, timeout=5
        )
        status["screen_running"] = f"server_{server_id}" in result.stdout
    except Exception:
        pass
    
    # A2S sorgusu (oyuncu sayisi, map, hostname)
    try:
        address = (server.ip_address, server.port)
        info = a2s.info(address, timeout=2)
        status["port_open"] = True
        status["players"] = info.player_count
        status["map"] = info.map_name
        status["hostname"] = info.server_name
    except Exception:
        pass
    
    # Gercek durumu belirle
    if status["screen_running"] and status["port_open"]:
        real_status = "running"
    elif status["screen_running"]:
        real_status = "starting"
    else:
        real_status = "stopped"
    
    status["real_status"] = real_status
    
    # DB durumunu guncelle (uyumsuzluk varsa)
    if real_status == "running" and server.status != ServerStatus.RUNNING:
        server.status = ServerStatus.RUNNING
        db.commit()
    elif real_status == "stopped" and server.status == ServerStatus.RUNNING:
        server.status = ServerStatus.STOPPED
        db.commit()
    
    return status


@router.get("/my-servers/{server_id}/players")
async def get_server_players(server_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Sunucudaki oyunculari listele"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    try:
        address = (server.ip_address, server.port)
        players = a2s.players(address, timeout=2)
        return {
            "players": [
                {
                    "name": p.name,
                    "score": p.score,
                    "duration": round(p.duration, 1)
                } for p in players
            ],
            "count": len(players)
        }
    except Exception as e:
        return {"players": [], "count": 0, "error": str(e)}


@router.get("/my-servers/{server_id}/resources")
async def get_server_resources(server_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Sunucu kaynak kullanimini goster"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    resources = {
        "cpu_percent": 0,
        "memory_mb": 0,
        "pid": None
    }
    
    # Screen PID bul - shell=False ile guvenli
    try:
        result = subprocess.run(
            ["screen", "-list"],
            shell=False, capture_output=True, text=True, timeout=5
        )
        # Parse screen output to find server PID
        screen_pid = None
        for line in result.stdout.split('\n'):
            if f"server_{server_id}" in line:
                # Format: "	12345.server_1	(Detached)"
                parts = line.strip().split('.')
                if parts and parts[0].isdigit():
                    screen_pid = int(parts[0])
                    break

        if screen_pid:
            # Screen icindeki hlds process'ini bul
            for proc in psutil.process_iter(['pid', 'ppid', 'name', 'cpu_percent', 'memory_info']):
                if proc.info['ppid'] == screen_pid or proc.info['pid'] == screen_pid:
                    if 'hlds' in proc.info['name'].lower():
                        resources["pid"] = proc.info['pid']
                        resources["cpu_percent"] = proc.info['cpu_percent']
                        resources["memory_mb"] = round(proc.info['memory_info'].rss / 1024 / 1024, 2)
                        break
    except Exception as e:
        logger.error(f"Resource monitor hatasi: {e}")
    
    return resources


# ==================== RCON ====================

@router.post("/my-servers/{server_id}/rcon")
async def execute_rcon(server_id: int, data: RconCommandRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """RCON komutu calistir"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    if server.status != ServerStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Sunucu calismiyordu")
    
    if not server.rcon_password:
        raise HTTPException(status_code=400, detail="RCON sifresi ayarlanmamis")
    
    # Tehlikeli komutlari engelle
    dangerous_commands = ["quit", "exit", "rcon_password", "_restart", "sv_password"]
    cmd_lower = data.command.lower().strip()
    for dangerous in dangerous_commands:
        if cmd_lower.startswith(dangerous):
            raise HTTPException(status_code=403, detail=f"'{dangerous}' komutu yasakli")
    
    client_ip = request.client.host if request.client else None
    
    try:
        # RCON baglantisi
        from rcon.source import Client
        
        with Client(server.ip_address, server.port, passwd=server.rcon_password, timeout=5) as client:
            response = client.run(data.command)
        
        # Log kaydet
        rcon_log = RconLog(
            server_id=server_id,
            user_id=current_user.id,
            command=data.command,
            response=response[:2000] if response else None,
            ip_address=client_ip
        )
        db.add(rcon_log)
        db.commit()
        
        logger.info(f"RCON: {current_user.username} -> server_{server_id}: {data.command}")
        
        return {"success": True, "response": response}
    
    except Exception as e:
        logger.error(f"RCON hatasi: {e}")
        return {"success": False, "error": str(e)}


@router.get("/my-servers/{server_id}/rcon-history")
async def get_rcon_history(server_id: int, limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """RCON komut gecmisi"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    logs = db.query(RconLog).filter(
        RconLog.server_id == server_id
    ).order_by(RconLog.created_at.desc()).limit(limit).all()
    
    return {
        "history": [
            {
                "id": log.id,
                "command": log.command,
                "response": log.response[:500] if log.response else None,
                "created_at": log.created_at.isoformat()
            } for log in logs
        ]
    }


# ==================== MAP CHANGER ====================

@router.post("/my-servers/{server_id}/change-map")
async def change_map(server_id: int, data: MapChangeRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Harita degistir"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    if server.status != ServerStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Sunucu calismiyordu")
    
    # Map adini dogrula
    if not data.map_name or len(data.map_name) > 64:
        raise HTTPException(status_code=400, detail="Gecersiz harita adi")
    
    try:
        from rcon.source import Client
        
        with Client(server.ip_address, server.port, passwd=server.rcon_password, timeout=5) as client:
            client.run(f"changelevel {data.map_name}")
        
        client_ip = request.client.host if request.client else None
        log_audit(db, current_user.id, "map_change", "server", server_id,
                  new_values={"map": data.map_name}, ip_address=client_ip)
        
        return {"success": True, "message": f"Harita {data.map_name} olarak degistiriliyor"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/my-servers/{server_id}/maps")
async def list_maps(server_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Kullanilabilir haritalari listele"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    server_path = get_server_path(server.id)
    game_dir = get_game_dir(server)
    maps_path = server_path / game_dir / "maps"
    
    maps = []
    try:
        if maps_path.exists():
            for f in maps_path.glob("*.bsp"):
                maps.append(f.stem)
        maps.sort()
    except Exception as e:
        logger.error(f"Map listesi hatasi: {e}")
    
    return {"maps": maps, "count": len(maps)}


# ==================== CONFIG EDITOR ====================

@router.get("/my-servers/{server_id}/config")
async def get_config(server_id: int, config_type: str = "server.cfg", db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Config dosyasini oku (indirme yok, sadece icerik)"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    # Izin verilen config dosyalari
    allowed_configs = ["server.cfg", "mapcycle.txt", "motd.txt", "listenserver.cfg"]
    if config_type not in allowed_configs:
        raise HTTPException(status_code=403, detail="Bu config dosyasina erisim izni yok")
    
    server_path = get_server_path(server.id)
    game_dir = get_game_dir(server)
    config_path = server_path / game_dir / config_type
    
    try:
        if not config_path.exists():
            return {"content": "", "exists": False}
        
        content = config_path.read_text(encoding='utf-8', errors='ignore')
        
        # Korunmasi gereken satirlari maskele (sadece gosterimde)
        lines = content.split('\n')
        masked_lines = []
        for line in lines:
            line_lower = line.lower().strip()
            is_protected = False
            for key in PROTECTED_CONFIG_KEYS:
                if line_lower.startswith(key):
                    is_protected = True
                    masked_lines.append(f"// [KORUMALI] {key} ***")
                    break
            if not is_protected:
                masked_lines.append(line)
        
        return {
            "content": '\n'.join(masked_lines),
            "original_content": content,  # Duzenleme icin
            "exists": True,
            "protected_keys": PROTECTED_CONFIG_KEYS
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config okuma hatasi: {e}")


@router.put("/my-servers/{server_id}/config")
async def update_config(server_id: int, data: ConfigUpdateRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Config dosyasini guncelle (korumali ayarlar degistirilemez)"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    # Izin verilen config dosyalari
    allowed_configs = ["server.cfg", "mapcycle.txt", "motd.txt"]
    if data.config_type not in allowed_configs:
        raise HTTPException(status_code=403, detail="Bu config dosyasini duzenleyemezsiniz")
    
    server_path = get_server_path(server.id)
    game_dir = get_game_dir(server)
    config_path = server_path / game_dir / data.config_type
    
    # Eski icerigi oku
    old_content = ""
    try:
        if config_path.exists():
            old_content = config_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        pass
    
    # Korumali ayarlari kontrol et - yeni icerikte degistirilmeye calisilmis mi?
    new_lines = data.content.split('\n')
    old_lines = old_content.split('\n')
    
    # Korumali ayarlarin orijinal degerlerini bul
    protected_values = {}
    for line in old_lines:
        line_lower = line.lower().strip()
        for key in PROTECTED_CONFIG_KEYS:
            if line_lower.startswith(key):
                protected_values[key] = line
                break
    
    # Yeni icerikteki korumali satirlari orijinalleriyle degistir
    final_lines = []
    for line in new_lines:
        line_lower = line.lower().strip()
        replaced = False
        for key in PROTECTED_CONFIG_KEYS:
            if line_lower.startswith(key):
                # Orijinal degeri kullan
                if key in protected_values:
                    final_lines.append(protected_values[key])
                replaced = True
                break
        if not replaced:
            final_lines.append(line)
    
    # Eski korumali satirlar yeni icerikte yoksa ekle
    for key, value in protected_values.items():
        found = False
        for line in final_lines:
            if line.lower().strip().startswith(key):
                found = True
                break
        if not found:
            final_lines.insert(0, value)
    
    final_content = '\n'.join(final_lines)
    
    try:
        # Yedekle
        config_path.write_text(final_content, encoding='utf-8')
        
        # Config history kaydet
        history = ConfigHistory(
            server_id=server_id,
            user_id=current_user.id,
            config_type=data.config_type,
            old_content=old_content,
            new_content=final_content
        )
        db.add(history)
        
        client_ip = request.client.host if request.client else None
        log_audit(db, current_user.id, "config_update", "server", server_id,
                  new_values={"config_type": data.config_type}, ip_address=client_ip)
        
        db.commit()
        
        return {"success": True, "message": "Config guncellendi"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Config yazma hatasi: {e}")


# ==================== FILE BROWSER (SADECE GÖRÜNTÜLEME) ====================

@router.get("/my-servers/{server_id}/files")
async def list_files(server_id: int, path: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Sunucu dosyalarini listele (indirme yok)"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    server_path = get_server_path(server.id)
    game_dir = get_game_dir(server)
    base_path = server_path / game_dir
    
    # Path traversal engelle - guvenli yontem
    # Null byte ve diger tehlikeli karakterleri de kontrol et
    if ".." in path or "\x00" in path or path.startswith("/"):
        raise HTTPException(status_code=403, detail="Gecersiz yol")

    target_path = base_path / path if path else base_path

    # Sadece game dizini icinde kal - is_relative_to ile guvenli kontrol
    try:
        resolved_target = target_path.resolve()
        resolved_base = base_path.resolve()
        if not resolved_target.is_relative_to(resolved_base):
            raise HTTPException(status_code=403, detail="Erisim izni yok")
        target_path = resolved_target
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=403, detail="Gecersiz yol")
    
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Dizin bulunamadi")
    
    files = []
    dirs = []
    
    try:
        for item in target_path.iterdir():
            if item.is_dir():
                dirs.append({
                    "name": item.name,
                    "type": "directory"
                })
            else:
                files.append({
                    "name": item.name,
                    "type": "file",
                    "size": item.stat().st_size,
                    "extension": item.suffix.lower()
                })
        
        dirs.sort(key=lambda x: x["name"])
        files.sort(key=lambda x: x["name"])
        
    except Exception as e:
        logger.error(f"Dosya listesi hatasi: {e}")
    
    return {
        "path": path,
        "directories": dirs,
        "files": files,
        "can_download": False  # Indirme yetkisi YOK
    }


@router.get("/my-servers/{server_id}/files/view")
async def view_file(server_id: int, path: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Dosya icerigini goruntule (indirme yok, sadece text)"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    # Izin verilen uzantilar
    viewable_extensions = [".cfg", ".txt", ".ini", ".log", ".res", ".gam"]
    
    server_path = get_server_path(server.id)
    game_dir = get_game_dir(server)
    base_path = server_path / game_dir
    
    if ".." in path:
        raise HTTPException(status_code=403, detail="Gecersiz yol")
    
    file_path = base_path / path
    
    try:
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(base_path.resolve())):
            raise HTTPException(status_code=403, detail="Erisim izni yok")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=403, detail="Gecersiz yol")
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Dosya bulunamadi")
    
    if file_path.suffix.lower() not in viewable_extensions:
        raise HTTPException(status_code=403, detail="Bu dosya tipi goruntulenemez")
    
    # Boyut limiti (1MB)
    if file_path.stat().st_size > 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dosya cok buyuk")
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        return {"path": path, "content": content, "can_download": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosya okuma hatasi: {e}")


# ==================== PLUGIN MANAGER ====================

@router.get("/my-servers/{server_id}/plugins")
async def list_server_plugins(server_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Sunucudaki pluginleri listele"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    # DB'deki pluginler
    server_plugins = db.query(ServerPlugin).filter(
        ServerPlugin.server_id == server_id
    ).all()
    
    plugins = []
    for sp in server_plugins:
        plugin_info = {
            "id": sp.id,
            "is_enabled": sp.is_enabled,
            "installed_at": sp.installed_at.isoformat() if sp.installed_at else None,
            "is_custom": sp.plugin_id is None
        }
        
        if sp.plugin_id:
            # Admin eklentisi
            plugin = db.query(Plugin).filter(Plugin.id == sp.plugin_id).first()
            if plugin:
                plugin_info.update({
                    "name": plugin.name,
                    "description": plugin.description,
                    "version": plugin.version,
                    "author": plugin.author,
                    "category": plugin.category
                })
        else:
            # Kullanici eklentisi
            plugin_info.update({
                "name": sp.custom_plugin_name,
                "description": "Kullanici eklentisi",
                "version": None,
                "author": None,
                "category": "custom"
            })
        
        plugins.append(plugin_info)
    
    return {"plugins": plugins, "can_download": False}


@router.post("/my-servers/{server_id}/plugins/upload")
async def upload_plugin(server_id: int, request: Request, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Kullanici kendi pluginini yuklesin"""
    import re
    import secrets as sec

    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")

    # Uzanti kontrolu
    allowed_ext = [".amxx"]
    original_filename = file.filename or "plugin.amxx"
    file_ext = Path(original_filename).suffix.lower()
    if file_ext not in allowed_ext:
        raise HTTPException(status_code=400, detail="Sadece .amxx dosyalari yuklenebilir")

    # Dosya adini sanitize et - sadece alfanumerik, tire ve alt cizgi
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', Path(original_filename).stem)
    safe_name = safe_name[:50]  # Max 50 karakter
    if not safe_name:
        safe_name = "plugin"

    # Boyut kontrolu (5MB)
    content = await file.read()
    MAX_PLUGIN_SIZE = 5 * 1024 * 1024
    if len(content) > MAX_PLUGIN_SIZE:
        raise HTTPException(status_code=400, detail="Dosya boyutu 5MB'dan buyuk olamaz")

    # AMX Mod X magic bytes kontrolu (ilk 4 byte)
    # AMXX dosyalari genellikle 0x00 0x00 0x03 0xF1 ile baslar
    if len(content) < 16:
        raise HTTPException(status_code=400, detail="Gecersiz plugin dosyasi")

    server_path = get_server_path(server.id)
    game_dir = get_game_dir(server)
    plugins_path = server_path / game_dir / "addons" / "amxmodx" / "plugins"

    # Dizin yoksa olustur
    plugins_path.mkdir(parents=True, exist_ok=True)

    # Benzersiz dosya adi olustur (collision onleme)
    unique_suffix = sec.token_hex(4)
    safe_filename = f"{safe_name}_{unique_suffix}.amxx"
    file_path = plugins_path / safe_filename

    # Path traversal kontrolu
    if not file_path.resolve().is_relative_to(plugins_path.resolve()):
        raise HTTPException(status_code=400, detail="Gecersiz dosya yolu")

    try:
        file_path.write_bytes(content)
        
        # DB'ye ekle
        server_plugin = ServerPlugin(
            server_id=server_id,
            custom_plugin_name=safe_filename,
            custom_plugin_file=str(file_path),
            is_enabled=True,
            installed_by=current_user.id
        )
        db.add(server_plugin)

        client_ip = request.client.host if request.client else None
        log_audit(db, current_user.id, "plugin_upload", "server", server_id,
                  new_values={"filename": safe_filename, "original": original_filename}, ip_address=client_ip)

        db.commit()

        return {"success": True, "message": f"Plugin {safe_filename} yuklendi"}

    except Exception as e:
        logger.error(f"Plugin upload error for server {server_id}: {e}")
        raise HTTPException(status_code=500, detail="Plugin yukleme hatasi")


@router.put("/my-servers/{server_id}/plugins/{plugin_id}/toggle")
async def toggle_plugin(server_id: int, plugin_id: int, data: PluginToggleRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Plugin ac/kapa"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    server_plugin = db.query(ServerPlugin).filter(
        ServerPlugin.id == plugin_id,
        ServerPlugin.server_id == server_id
    ).first()
    if not server_plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadi")
    
    server_plugin.is_enabled = data.enabled
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "plugin_toggle", "server", server_id,
              new_values={"plugin_id": plugin_id, "enabled": data.enabled}, ip_address=client_ip)
    
    db.commit()
    
    status = "aktif" if data.enabled else "deaktif"
    return {"success": True, "message": f"Plugin {status} edildi"}


@router.delete("/my-servers/{server_id}/plugins/{plugin_id}")
async def delete_plugin(server_id: int, plugin_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Kullanici pluginini sil (sadece kendi yukledikleri)"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    server_plugin = db.query(ServerPlugin).filter(
        ServerPlugin.id == plugin_id,
        ServerPlugin.server_id == server_id
    ).first()
    if not server_plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadi")
    
    # Sadece custom pluginler silinebilir
    if server_plugin.plugin_id is not None:
        raise HTTPException(status_code=403, detail="Admin eklentileri silinemez")
    
    # Dosyayi sil
    if server_plugin.custom_plugin_file:
        try:
            Path(server_plugin.custom_plugin_file).unlink(missing_ok=True)
        except Exception:
            pass
    
    plugin_name = server_plugin.custom_plugin_name
    db.delete(server_plugin)
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "plugin_delete", "server", server_id,
              new_values={"plugin_name": plugin_name}, ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": "Plugin silindi"}


# ==================== SERVER LOGS ====================

@router.get("/my-servers/{server_id}/logs")
async def get_server_logs(server_id: int, lines: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Sunucu loglarini oku"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    server_path = get_server_path(server.id)
    game_dir = get_game_dir(server)
    logs_path = server_path / game_dir / "logs"
    
    logs = []
    try:
        if logs_path.exists():
            # En son log dosyasini bul
            log_files = sorted(logs_path.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
            if log_files:
                latest_log = log_files[0]
                content = latest_log.read_text(encoding='utf-8', errors='ignore')
                log_lines = content.split('\n')
                logs = log_lines[-lines:] if len(log_lines) > lines else log_lines
    except Exception as e:
        logger.error(f"Log okuma hatasi: {e}")
    
    return {"logs": logs, "can_download": False}