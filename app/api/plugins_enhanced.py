"""
AGTR Merkezi v6.2 - Enhanced Plugin API
1-click install, version management, auto-updates
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import GameServer, User
from app.services.plugin_service import PluginService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/plugins", tags=["Plugin Management"])


# ============================================
# Request/Response Models
# ============================================


class PluginInstallRequest(BaseModel):
    """Plugin installation request"""

    server_id: int
    plugin_id: int


class PluginToggleRequest(BaseModel):
    """Plugin enable/disable request"""

    server_id: int
    plugin_id: int
    enabled: bool


class PluginResponse(BaseModel):
    """Single plugin info"""

    id: int
    name: str
    slug: str
    description: str | None
    version: str | None
    author: str | None
    category: str | None
    game_type: str | None
    file_size: int | None
    is_default: bool
    requires_config: bool


class ServerPluginResponse(BaseModel):
    """Installed plugin info"""

    server_plugin_id: int
    plugin_id: int
    name: str
    slug: str
    version: str | None
    category: str | None
    is_enabled: bool
    installed_at: str | None


class PluginOperationResponse(BaseModel):
    """Plugin operation result"""

    success: bool
    message: str


class PluginListResponse(BaseModel):
    """List of plugins"""

    plugins: List[Dict]
    total: int


class PluginStatsResponse(BaseModel):
    """Plugin statistics"""

    total_plugins: int
    active_plugins: int
    total_installations: int
    most_popular: List[Dict]


class PluginUpdateInfo(BaseModel):
    """Plugin update information"""

    plugin_id: int
    name: str
    current_version: str
    latest_version: str


class PluginUpdatesResponse(BaseModel):
    """Available updates"""

    updates: List[PluginUpdateInfo]
    count: int


# ============================================
# Helper Functions
# ============================================


def check_server_ownership(server_id: int, user: User, db: Session):
    """Check if user owns the server"""
    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(404, f"Server not found: {server_id}")

    if server.owner_id != user.id:
        raise HTTPException(403, "You don't own this server")

    return server


# ============================================
# API Endpoints
# ============================================


@router.get("/available", response_model=PluginListResponse)
async def get_available_plugins(
    game_type: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get available plugins for installation.

    **Filters:**
    - game_type: Filter by game (cs16, ag, hldm, etc.)
    - category: Filter by category (admin, fun, stats, etc.)

    Returns list of plugins ready for 1-click installation.
    """
    service = PluginService(db)

    plugins = service.get_available_plugins(game_type=game_type, category=category)

    return PluginListResponse(plugins=plugins, total=len(plugins))


@router.get("/servers/{server_id}/plugins", response_model=List[ServerPluginResponse])
async def get_server_plugins(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get all plugins installed on a server.

    Returns list of installed plugins with status (enabled/disabled).
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = PluginService(db)
    plugins = service.get_server_plugins(server_id)

    return [ServerPluginResponse(**p) for p in plugins]


@router.post("/servers/{server_id}/install", response_model=PluginOperationResponse)
async def install_plugin(
    server_id: int,
    request: PluginInstallRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Install a plugin to a server (1-click install).

    **Process:**
    1. Validates plugin exists and is active
    2. Copies plugin file to server directory
    3. Creates installation record
    4. Returns success status

    **Time:** < 30 seconds
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = PluginService(db)

    success, message = await service.install_plugin(server_id, request.plugin_id, current_user.id)

    if not success:
        raise HTTPException(400, message)

    return PluginOperationResponse(success=True, message=message)


@router.post("/servers/{server_id}/uninstall", response_model=PluginOperationResponse)
async def uninstall_plugin(
    server_id: int,
    request: PluginInstallRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Uninstall a plugin from a server.

    Removes plugin file and database record.
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = PluginService(db)

    success, message = await service.uninstall_plugin(server_id, request.plugin_id)

    if not success:
        raise HTTPException(400, message)

    return PluginOperationResponse(success=True, message=message)


@router.post("/servers/{server_id}/toggle", response_model=PluginOperationResponse)
async def toggle_plugin(
    server_id: int,
    request: PluginToggleRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Enable/disable a plugin without uninstalling.

    Useful for temporary deactivation.
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = PluginService(db)

    success, message = service.toggle_plugin(server_id, request.plugin_id, request.enabled)

    if not success:
        raise HTTPException(400, message)

    return PluginOperationResponse(success=True, message=message)


@router.get("/servers/{server_id}/updates", response_model=PluginUpdatesResponse)
async def check_plugin_updates(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Check for available plugin updates.

    Compares installed plugin versions with latest versions in catalog.
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = PluginService(db)

    updates = await service.check_for_updates(server_id)

    return PluginUpdatesResponse(
        updates=[PluginUpdateInfo(**u) for u in updates], count=len(updates)
    )


@router.post("/servers/{server_id}/update/{plugin_id}", response_model=PluginOperationResponse)
async def update_plugin(
    server_id: int,
    plugin_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Update a plugin to latest version.

    Automatically uninstalls old version and installs new version.
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = PluginService(db)

    success, message = await service.auto_update_plugin(server_id, plugin_id)

    if not success:
        raise HTTPException(400, message)

    return PluginOperationResponse(success=True, message=message)


@router.get("/stats", response_model=PluginStatsResponse)
async def get_plugin_stats(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get overall plugin marketplace statistics.

    Returns total plugins, active count, installation count, and most popular plugins.
    """
    service = PluginService(db)

    stats = service.get_plugin_stats()

    return PluginStatsResponse(**stats)
