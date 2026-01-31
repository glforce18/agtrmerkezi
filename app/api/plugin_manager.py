"""
AGTR Merkezi - Plugin Manager API
Kısıtlı plugin yönetimi - kullanıcılar sadece kendi pluginlerini yönetebilir
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import GameServer, User, UserRole
from app.services.plugin_manager_service import PluginManagerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/servers/{server_id}/plugins", tags=["Plugin Manager"])


# ============================================
# Pydantic Schemas
# ============================================


class PluginToggleRequest(BaseModel):
    """Plugin aç/kapa isteği"""

    enabled: bool


# ============================================
# Helper Functions
# ============================================


async def verify_server_ownership(server_id: int, current_user: User, db: Session) -> GameServer:
    """
    Sunucu sahipliğini doğrula

    Admin/Superadmin kullanıcılar tüm sunuculara erişebilir
    """
    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadı")

    # Admin bypass - admin kullanıcılar tüm sunuculara erişebilir
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        return server

    # Normal kullanıcı - sadece kendi sunucusu
    if server.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu sunucuya erişim yetkiniz yok")

    return server


# ============================================
# API Endpoints
# ============================================


@router.get("/stats")
async def get_plugin_stats(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin istatistiklerini getir

    Returns:
        Plugin statistics
    """
    await verify_server_ownership(server_id, current_user, db)

    service = PluginManagerService(db)
    return service.get_plugin_stats(server_id, current_user.id)


@router.get("/server")
async def list_server_plugins(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Server pluginlerini listele (read-only)

    Returns:
        List of server plugins
    """
    await verify_server_ownership(server_id, current_user, db)

    service = PluginManagerService(db)
    plugins = service.list_server_plugins(server_id)

    return {"success": True, "plugins": plugins}


@router.get("/my")
async def list_my_plugins(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Kendi pluginlerimi listele

    Returns:
        List of user's plugins
    """
    await verify_server_ownership(server_id, current_user, db)

    service = PluginManagerService(db)
    plugins = service.list_user_plugins(server_id, current_user.id)

    return {"success": True, "plugins": plugins}


@router.post("/upload")
async def upload_plugin(
    server_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin yükle

    Restrictions:
    - Sadece .amxx dosyaları
    - Maksimum 5 MB
    - user_uploads/user_X/ klasörüne

    Returns:
        Upload result
    """
    await verify_server_ownership(server_id, current_user, db)

    # Read file content
    content = await file.read()

    service = PluginManagerService(db)
    success, message, plugin_info = service.upload_plugin(
        server_id=server_id,
        user_id=current_user.id,
        filename=file.filename,
        content=content,
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message, "plugin": plugin_info}


@router.delete("/{filename}")
async def delete_plugin(
    server_id: int,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Kendi pluginini sil

    Args:
        server_id: Server ID
        filename: Plugin filename (e.g., "my_plugin.amxx")

    Returns:
        Delete result
    """
    await verify_server_ownership(server_id, current_user, db)

    service = PluginManagerService(db)
    success, message = service.delete_plugin(
        server_id=server_id,
        user_id=current_user.id,
        filename=filename,
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


@router.post("/{filename}/toggle")
async def toggle_plugin(
    server_id: int,
    filename: str,
    data: PluginToggleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin aç/kapa

    Args:
        server_id: Server ID
        filename: Plugin filename
        data: Toggle request (enabled: true/false)

    Returns:
        Toggle result
    """
    await verify_server_ownership(server_id, current_user, db)

    service = PluginManagerService(db)
    success, message = service.toggle_plugin(
        server_id=server_id,
        user_id=current_user.id,
        filename=filename,
        enable=data.enabled,
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message, "enabled": data.enabled}


@router.get("/all")
async def list_all_plugins(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Tüm pluginleri listele (server + user)

    Returns:
        Combined list of all plugins
    """
    await verify_server_ownership(server_id, current_user, db)

    service = PluginManagerService(db)
    server_plugins = service.list_server_plugins(server_id)
    user_plugins = service.list_user_plugins(server_id, current_user.id)
    stats = service.get_plugin_stats(server_id, current_user.id)

    return {
        "success": True,
        "server_plugins": server_plugins,
        "user_plugins": user_plugins,
        "stats": stats,
    }
