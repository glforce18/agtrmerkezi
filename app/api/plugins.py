"""
AGTR Merkezi v6.0 - Plugin Manager API
AMXModX plugin yönetimi API endpoint'leri
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import GameServer, ServerPlugin, User
from app.services.plugin_manager import PluginManagerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/servers/{server_id}/plugins", tags=["Plugin Manager"])


# ==================== REQUEST/RESPONSE MODELS ====================


class PluginToggleRequest(BaseModel):
    """Plugin toggle request"""

    enabled: bool


class PluginConfigRequest(BaseModel):
    """Plugin config update request"""

    config_content: str


# Helper function
async def verify_server_ownership(server_id: int, user: User, db: Session) -> GameServer:
    """
    Verify server ownership

    Admin/Superadmin kullanıcılar tüm sunuculara erişebilir
    """
    from app.models.database import UserRole

    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadı")

    # Admin bypass - admin kullanıcılar tüm sunuculara erişebilir
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        return server

    # Normal kullanıcı - sadece kendi sunucusu
    if server.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Bu sunucuya erişim izniniz yok")

    return server


@router.get("/list")
async def list_plugins(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Yüklü pluginleri listele

    Returns:
        List[Dict]: Plugin listesi (id, filename, name, version, author, size, modified, enabled, status)
    """
    server = await verify_server_ownership(server_id, current_user, db)

    plugin_manager = PluginManagerService()
    plugins = plugin_manager.list_installed_plugins(server_id, server)

    # Get ServerPlugin records from DB to add ID and status
    server_plugins = db.query(ServerPlugin).filter(ServerPlugin.server_id == server_id).all()

    # Create mapping from filename to ServerPlugin
    sp_map = {}
    for sp in server_plugins:
        filename = sp.custom_plugin_file or (sp.plugin.filename if sp.plugin else None)
        if filename:
            sp_map[filename] = sp

    # Enhance plugin data with DB info
    for plugin in plugins:
        sp = sp_map.get(plugin["filename"])
        if sp:
            plugin["id"] = sp.id
            plugin["status"] = sp.status or ("active" if plugin.get("enabled") else "inactive")
            plugin["last_error"] = sp.last_error
            plugin["last_checked"] = sp.last_checked.isoformat() if sp.last_checked else None
        else:
            # Plugin exists in filesystem but not in DB - create placeholder
            plugin["id"] = None
            plugin["status"] = "active" if plugin.get("enabled") else "inactive"
            plugin["last_error"] = None
            plugin["last_checked"] = None

    return plugins


@router.post("/{filename}/enable")
async def enable_plugin(
    server_id: int,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin'i aktif et (plugins.ini'ye ekle)

    Args:
        server_id: Sunucu ID
        filename: Plugin dosya adı (.amxx)

    Returns:
        Dict: success, message
    """
    server = await verify_server_ownership(server_id, current_user, db)

    plugin_manager = PluginManagerService()
    success, message = plugin_manager.enable_plugin(server_id, filename, current_user.id, server)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


@router.post("/{filename}/disable")
async def disable_plugin(
    server_id: int,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin'i devre dışı bırak (plugins.ini'de yorum satırı yap)

    Args:
        server_id: Sunucu ID
        filename: Plugin dosya adı (.amxx)

    Returns:
        Dict: success, message
    """
    server = await verify_server_ownership(server_id, current_user, db)

    plugin_manager = PluginManagerService()
    success, message = plugin_manager.disable_plugin(server_id, filename, current_user.id, server)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


@router.post("/upload")
async def upload_plugin(
    server_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin dosyası yükle (.amxx)

    Args:
        server_id: Sunucu ID
        file: Plugin dosyası (max 10MB, sadece .amxx)

    Returns:
        Dict: success, message
    """
    server = await verify_server_ownership(server_id, current_user, db)

    plugin_manager = PluginManagerService()
    success, message = plugin_manager.upload_plugin(server_id, file, current_user.id, server)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message, "filename": file.filename}


@router.delete("/{filename}")
async def delete_plugin(
    server_id: int,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin'i sil (yedek oluşturulur)

    Args:
        server_id: Sunucu ID
        filename: Plugin dosya adı (.amxx)

    Returns:
        Dict: success, message
    """
    server = await verify_server_ownership(server_id, current_user, db)

    plugin_manager = PluginManagerService()
    success, message = plugin_manager.delete_plugin(server_id, filename, current_user.id, server)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


@router.post("/compile/{sma_filename}")
async def compile_plugin(
    server_id: int,
    sma_filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    .sma kaynak dosyasını .amxx'e derle

    Args:
        server_id: Sunucu ID
        sma_filename: Kaynak dosya adı (.sma)

    Returns:
        Dict: success, message (derlenen .amxx dosya adı)
    """
    server = await verify_server_ownership(server_id, current_user, db)

    plugin_manager = PluginManagerService()
    success, message = plugin_manager.compile_plugin(
        server_id, sma_filename, current_user.id, server
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


@router.get("/marketplace")
async def get_marketplace_plugins(
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin market listesini getir

    Returns:
        List[Dict]: Popüler plugin listesi (name, filename, description, category, download_url)
    """
    plugin_manager = PluginManagerService()
    marketplace_plugins = plugin_manager.get_marketplace_plugins()

    return marketplace_plugins


# ==================== NEW ENDPOINTS FOR ENHANCED PLUGIN MANAGEMENT ====================


@router.put("/{plugin_id}/toggle")
async def toggle_plugin(
    server_id: int,
    plugin_id: int,
    data: PluginToggleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Tek endpoint ile plugin aç/kapat (Toggle)

    Args:
        plugin_id: ServerPlugin.id (NOT filename!)
        data: {"enabled": true/false}

    Returns:
        {
            "success": bool,
            "message": str,
            "plugin": {
                "id": int,
                "is_enabled": bool,
                "status": str
            }
        }
    """
    await verify_server_ownership(server_id, current_user, db)

    # ServerPlugin kaydını bul
    server_plugin = (
        db.query(ServerPlugin)
        .filter(ServerPlugin.id == plugin_id, ServerPlugin.server_id == server_id)
        .first()
    )

    if not server_plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadı")

    # Plugin filename belirle
    filename = server_plugin.custom_plugin_file or (
        server_plugin.plugin.filename if server_plugin.plugin else None
    )

    if not filename:
        raise HTTPException(status_code=400, detail="Plugin dosya adı bulunamadı")

    # Plugin manager servisini kullan
    plugin_manager = PluginManagerService()

    if data.enabled:
        success, message = plugin_manager.enable_plugin(server_id, filename, current_user.id)
    else:
        success, message = plugin_manager.disable_plugin(server_id, filename, current_user.id)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Database'i güncelle
    server_plugin.is_enabled = data.enabled
    server_plugin.status = "active" if data.enabled else "inactive"
    server_plugin.last_checked = datetime.utcnow()
    server_plugin.last_error = None if success else message
    db.commit()
    db.refresh(server_plugin)

    logger.info(
        f"Plugin {filename} {'enabled' if data.enabled else 'disabled'} "
        f"for server {server_id} by user {current_user.id}"
    )

    return {
        "success": True,
        "message": message,
        "plugin": {
            "id": server_plugin.id,
            "is_enabled": data.enabled,
            "status": server_plugin.status,
        },
    }


@router.get("/{plugin_id}/status")
async def get_plugin_status(
    server_id: int,
    plugin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin durum kontrolü

    Returns:
        {
            "id": int,
            "filename": str,
            "is_enabled": bool,
            "is_enabled_ini": bool,
            "file_exists": bool,
            "is_running": bool,
            "last_error": str | None,
            "last_checked": datetime
        }
    """
    server = await verify_server_ownership(server_id, current_user, db)

    # ServerPlugin kaydını bul
    server_plugin = (
        db.query(ServerPlugin)
        .filter(ServerPlugin.id == plugin_id, ServerPlugin.server_id == server_id)
        .first()
    )

    if not server_plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadı")

    # Plugin filename belirle
    filename = server_plugin.custom_plugin_file or (
        server_plugin.plugin.filename if server_plugin.plugin else None
    )

    if not filename:
        raise HTTPException(status_code=400, detail="Plugin dosya adı bulunamadı")

    # Plugin manager servisinden status bilgisi al
    plugin_manager = PluginManagerService()
    status = plugin_manager.get_plugin_status(server_id, filename, server)

    # Database'i güncelle
    server_plugin.last_checked = datetime.utcnow()
    if status["last_error"]:
        server_plugin.last_error = status["last_error"]
        server_plugin.status = "error"
        server_plugin.error_count = (server_plugin.error_count or 0) + 1
    else:
        server_plugin.status = "active" if status["is_enabled_ini"] else "inactive"
        server_plugin.last_error = None
    db.commit()

    return {
        "id": server_plugin.id,
        "filename": filename,
        "is_enabled": server_plugin.is_enabled,
        "is_enabled_ini": status["is_enabled_ini"],
        "file_exists": status["file_exists"],
        "is_running": status["is_running"],
        "last_error": status["last_error"],
        "last_checked": server_plugin.last_checked,
    }


@router.get("/{plugin_id}/logs")
async def get_plugin_logs(
    server_id: int,
    plugin_id: int,
    limit: int = Query(50, ge=1, le=500),
    level: str = Query("all", pattern="^(all|error|warning|info)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin hata loglarını getir

    Args:
        limit: Maksimum log sayısı (1-500)
        level: Log seviyesi (all, error, warning, info)

    Returns:
        {
            "logs": [
                {
                    "timestamp": str,
                    "level": str,
                    "message": str,
                    "source": str
                }
            ],
            "total": int
        }
    """
    server = await verify_server_ownership(server_id, current_user, db)

    # ServerPlugin kaydını bul
    server_plugin = (
        db.query(ServerPlugin)
        .filter(ServerPlugin.id == plugin_id, ServerPlugin.server_id == server_id)
        .first()
    )

    if not server_plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadı")

    # Plugin filename belirle
    filename = server_plugin.custom_plugin_file or (
        server_plugin.plugin.filename if server_plugin.plugin else None
    )

    if not filename:
        raise HTTPException(status_code=400, detail="Plugin dosya adı bulunamadı")

    # Plugin manager servisinden logları al
    plugin_manager = PluginManagerService()
    logs = plugin_manager.get_plugin_logs(
        server_id, filename, limit=limit, level=level, server=server
    )

    return {"logs": logs, "total": len(logs)}


@router.get("/{plugin_id}/config")
async def get_plugin_config(
    server_id: int,
    plugin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin config dosyasını getir

    Returns:
        {
            "plugin_id": int,
            "config_file": str,
            "config_content": str,
            "cvars": []
        }
    """
    await verify_server_ownership(server_id, current_user, db)

    # ServerPlugin kaydını bul
    server_plugin = (
        db.query(ServerPlugin)
        .filter(ServerPlugin.id == plugin_id, ServerPlugin.server_id == server_id)
        .first()
    )

    if not server_plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadı")

    # Config values from DB
    config_values = server_plugin.config_values or {}

    return {
        "plugin_id": server_plugin.id,
        "config_file": f"{server_plugin.custom_plugin_name or 'plugin'}.cfg",
        "config_content": "",  # TODO: Read actual config file if exists
        "cvars": [
            {"name": key, "value": value, "type": "string"} for key, value in config_values.items()
        ],
    }


@router.put("/{plugin_id}/config")
async def update_plugin_config(
    server_id: int,
    plugin_id: int,
    data: PluginConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Plugin config dosyasını güncelle

    Args:
        data: {"config_content": "..."}

    Returns:
        {"success": bool, "message": str}
    """
    await verify_server_ownership(server_id, current_user, db)

    # ServerPlugin kaydını bul
    server_plugin = (
        db.query(ServerPlugin)
        .filter(ServerPlugin.id == plugin_id, ServerPlugin.server_id == server_id)
        .first()
    )

    if not server_plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadı")

    # TODO: Write config to actual file
    # For now just parse and store in config_values JSON

    # Parse config content (basic cvar extraction)
    cvars = {}
    for line in data.config_content.splitlines():
        line = line.strip()
        if line and not line.startswith("//"):
            parts = line.split(None, 1)
            if len(parts) == 2:
                cvars[parts[0]] = parts[1].strip('"')

    server_plugin.config_values = cvars
    db.commit()

    logger.info(
        f"Plugin config updated for plugin {plugin_id}, server {server_id} "
        f"by user {current_user.id}"
    )

    return {"success": True, "message": "Plugin ayarları kaydedildi"}
