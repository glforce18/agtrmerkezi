"""
Admin Server Approval API
Sunucu onay sistemi
"""

import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import GameServer, ServerStatus, User
from app.services.server_installation import ServerInstallationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/server-approval", tags=["Admin Server Approval"])


class ApprovalRequest(BaseModel):
    server_id: int
    approved: bool
    reason: Optional[str] = None


@router.get("/pending-servers")
async def get_pending_servers(
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """
    Onay bekleyen sunucuları listele
    """
    servers = (
        db.query(GameServer)
        .filter(GameServer.status == ServerStatus.PENDING)
        .order_by(GameServer.created_at.desc())
        .all()
    )

    return {
        "servers": [
            {
                "id": s.id,
                "name": s.name,
                "owner_id": s.owner_id,
                "game_type": s.game_type.value,
                "ip": s.ip_address,
                "port": s.port,
                "slots": s.slots,
                "monthly_price": s.monthly_price,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "package_id": s.package_id,
            }
            for s in servers
        ],
        "total": len(servers),
    }


@router.post("/approve")
async def approve_server(
    data: ApprovalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    Sunucu onaylama veya reddetme
    Onaylanırsa otomatik kurulum başlatılır
    """
    server = db.query(GameServer).filter(GameServer.id == data.server_id).first()

    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadı")

    if server.status != ServerStatus.PENDING:
        raise HTTPException(
            status_code=400, detail=f"Bu sunucu zaten işlendi. Durum: {server.status.value}"
        )

    if not data.approved:
        # RED EDİLDİ
        server.status = ServerStatus.REJECTED
        db.commit()

        logger.info(
            f"Admin {admin.username} sunucu {server.id} ({server.name}) "
            f"için onayı reddetti. Sebep: {data.reason}"
        )

        # TODO: Kullanıcıya bildirim gönder ve para iadesi yap

        return {
            "success": True,
            "message": "Sunucu reddedildi",
            "server_id": server.id,
            "status": "rejected",
        }

    # ONAYLANDI - Kurulumu başlat
    try:
        # Status'u INSTALLING yap
        server.status = ServerStatus.INSTALLING
        db.commit()

        logger.info(
            f"Admin {admin.username} sunucu {server.id} ({server.name}) "
            f"için onayı verdi. Kurulum başlatılıyor..."
        )

        # Installation servisi
        installation_service = ServerInstallationService(db)

        # Kurulum config'i hazırla
        install_config = {
            "map_name": "crossfire" if server.game_type.value == "HLDM" else "de_dust2",
            "max_players": server.slots,
            "hostname": server.name,
            "rcon_password": server.rcon_password,
            "ip": server.ip_address,
            "port": server.port,
        }

        # Installation kaydı oluştur (FIXED: doğru parametreler)
        installation = await installation_service.create_installation(
            server_id=server.id,
            user_id=server.owner_id,
            mod_type=server.game_type.value.lower(),
            config=install_config,
        )

        # Background task için config (run_installation için)
        config = {
            "mod_type": server.game_type.value.lower(),
            "map": "crossfire" if server.game_type.value == "HLDM" else "de_dust2",
            "maxplayers": server.slots,
            "hostname": server.name,
            "rcon_password": server.rcon_password,
            "ip": server.ip_address,
            "port": server.port,
        }

        # Background task ile kurulumu başlat
        background_tasks.add_task(run_installation_background, installation.id, config, db)

        return {
            "success": True,
            "message": "Sunucu onaylandı ve kurulum başlatıldı",
            "server_id": server.id,
            "installation_id": installation.id,
            "status": "installing",
        }

    except Exception as e:
        logger.error(f"Kurulum başlatma hatası: {e}", exc_info=True)
        server.status = ServerStatus.ERROR
        db.commit()

        raise HTTPException(status_code=500, detail=f"Kurulum başlatılamadı: {str(e)}")


async def run_installation_background(installation_id: int, config: dict, db: Session):
    """
    Arka planda kurulumu çalıştır
    """
    try:
        installation_service = ServerInstallationService(db)
        success, message = await installation_service.run_installation(installation_id, config)

        if success:
            logger.info(f"Installation {installation_id} başarıyla tamamlandı")
        else:
            logger.error(f"Installation {installation_id} başarısız: {message}")

    except Exception as e:
        logger.error(f"Installation background task hatası: {e}", exc_info=True)
