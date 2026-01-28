"""
AGTR Merkezi v6.2 - Plugin Management Service
1-click install, version management, auto-updates
"""

import hashlib
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.database import GameServer, Plugin, ServerPlugin

logger = logging.getLogger(__name__)


class PluginService:
    """
    Plugin installation and management service.

    Features:
    - 1-click plugin installation
    - Version management
    - Auto-update support
    - Dependency resolution
    """

    # Plugin storage
    PLUGIN_STORAGE = "/var/www/agtrmerkezi/static/plugins"

    def __init__(self, db: Session):
        self.db = db
        self._ensure_storage_directory()

    def _ensure_storage_directory(self):
        """Create plugin storage directory if it doesn't exist"""
        Path(self.PLUGIN_STORAGE).mkdir(parents=True, exist_ok=True)
        logger.info(f"Plugin storage directory: {self.PLUGIN_STORAGE}")

    def get_server_plugin_path(self, server_id: int) -> Path:
        """
        Get plugin directory path for a server.

        For CS 1.6: /home/gameservers/servers/AGTR-2026-00001/cstrike/addons/amxmodx/plugins
        """
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()

        if not server:
            raise ValueError(f"Server not found: {server_id}")

        # Base server path
        server_path = Path(f"/home/gameservers/servers/{server.unique_code}")

        # Mod folder mapping
        mod_folders = {
            "ag": "ag",
            "ag_openag": "ag",
            "cs16": "cstrike",
            "hldm": "valve",
            "valve_new": "valve",
        }

        mod_folder = mod_folders.get(server.mod_type, "cstrike")

        # Plugin path
        plugin_path = server_path / mod_folder / "addons" / "amxmodx" / "plugins"

        return plugin_path

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    async def install_plugin(
        self, server_id: int, plugin_id: int, user_id: int
    ) -> Tuple[bool, str]:
        """
        Install a plugin to a server (1-click install).

        Args:
            server_id: Target server
            plugin_id: Plugin to install
            user_id: Installing user

        Returns:
            (success, message)
        """
        # Get plugin
        plugin = self.db.query(Plugin).filter(Plugin.id == plugin_id).first()

        if not plugin:
            return False, f"Plugin not found: {plugin_id}"

        if not plugin.is_active:
            return False, "Plugin is not active"

        # Get server
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()

        if not server:
            return False, f"Server not found: {server_id}"

        # Check if already installed
        existing = (
            self.db.query(ServerPlugin)
            .filter(ServerPlugin.server_id == server_id, ServerPlugin.plugin_id == plugin_id)
            .first()
        )

        if existing:
            return False, "Plugin already installed"

        # Get server plugin directory
        try:
            plugin_dir = self.get_server_plugin_path(server_id)
            plugin_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create plugin directory: {e}")
            return False, f"Failed to create plugin directory: {e}"

        # Source plugin file
        source_file = Path(plugin.file_path)

        if not source_file.exists():
            return False, f"Plugin file not found: {plugin.file_path}"

        # Destination file
        dest_file = plugin_dir / plugin.filename

        try:
            # Copy plugin file
            shutil.copy2(source_file, dest_file)

            logger.info(f"Plugin installed: {plugin.name} -> {server.unique_code} ({dest_file})")

            # Create database record
            server_plugin = ServerPlugin(
                server_id=server_id,
                plugin_id=plugin_id,
                is_enabled=True,
                installed_at=datetime.utcnow(),
                installed_by=user_id,
            )

            self.db.add(server_plugin)
            self.db.commit()

            return True, f"Plugin installed successfully: {plugin.name}"

        except Exception as e:
            logger.error(f"Plugin installation failed: {e}")
            return False, str(e)

    async def uninstall_plugin(self, server_id: int, plugin_id: int) -> Tuple[bool, str]:
        """
        Uninstall a plugin from a server.

        Args:
            server_id: Target server
            plugin_id: Plugin to uninstall

        Returns:
            (success, message)
        """
        # Get installation record
        server_plugin = (
            self.db.query(ServerPlugin)
            .filter(ServerPlugin.server_id == server_id, ServerPlugin.plugin_id == plugin_id)
            .first()
        )

        if not server_plugin:
            return False, "Plugin not installed on this server"

        # Get plugin
        plugin = self.db.query(Plugin).filter(Plugin.id == plugin_id).first()

        if not plugin:
            return False, "Plugin not found"

        # Get plugin file path
        try:
            plugin_dir = self.get_server_plugin_path(server_id)
            plugin_file = plugin_dir / plugin.filename

            # Remove file if exists
            if plugin_file.exists():
                plugin_file.unlink()
                logger.info(f"Plugin file removed: {plugin_file}")

        except Exception as e:
            logger.warning(f"Failed to remove plugin file: {e}")

        # Remove database record
        self.db.delete(server_plugin)
        self.db.commit()

        return True, f"Plugin uninstalled successfully: {plugin.name}"

    def toggle_plugin(self, server_id: int, plugin_id: int, enabled: bool) -> Tuple[bool, str]:
        """
        Enable/disable a plugin without uninstalling.

        Args:
            server_id: Target server
            plugin_id: Plugin to toggle
            enabled: True to enable, False to disable

        Returns:
            (success, message)
        """
        server_plugin = (
            self.db.query(ServerPlugin)
            .filter(ServerPlugin.server_id == server_id, ServerPlugin.plugin_id == plugin_id)
            .first()
        )

        if not server_plugin:
            return False, "Plugin not installed on this server"

        server_plugin.is_enabled = enabled
        self.db.commit()

        status = "enabled" if enabled else "disabled"
        return True, f"Plugin {status} successfully"

    def get_server_plugins(self, server_id: int) -> List[Dict]:
        """
        Get all plugins installed on a server.

        Args:
            server_id: Server ID

        Returns:
            List of plugin info dicts
        """
        server_plugins = (
            self.db.query(ServerPlugin).filter(ServerPlugin.server_id == server_id).all()
        )

        result = []

        for sp in server_plugins:
            plugin = self.db.query(Plugin).filter(Plugin.id == sp.plugin_id).first()

            if plugin:
                result.append(
                    {
                        "server_plugin_id": sp.id,
                        "plugin_id": plugin.id,
                        "name": plugin.name,
                        "slug": plugin.slug,
                        "version": plugin.version,
                        "category": plugin.category,
                        "is_enabled": sp.is_enabled,
                        "installed_at": sp.installed_at.isoformat() if sp.installed_at else None,
                    }
                )

        return result

    def get_available_plugins(
        self, game_type: Optional[str] = None, category: Optional[str] = None
    ) -> List[Dict]:
        """
        Get available plugins for installation.

        Args:
            game_type: Filter by game type (optional)
            category: Filter by category (optional)

        Returns:
            List of available plugins
        """
        query = self.db.query(Plugin).filter(Plugin.is_active == True)

        if game_type:
            query = query.filter(Plugin.game_type == game_type)

        if category:
            query = query.filter(Plugin.category == category)

        plugins = query.all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "description": p.description,
                "version": p.version,
                "author": p.author,
                "category": p.category,
                "game_type": str(p.game_type) if p.game_type else None,
                "file_size": p.file_size,
                "is_default": p.is_default,
                "requires_config": p.requires_config,
            }
            for p in plugins
        ]

    async def check_for_updates(self, server_id: int) -> List[Dict]:
        """
        Check for plugin updates for a server.

        Args:
            server_id: Server ID

        Returns:
            List of available updates
        """
        # Get installed plugins
        installed = self.get_server_plugins(server_id)

        updates = []

        for sp in installed:
            plugin = self.db.query(Plugin).filter(Plugin.id == sp["plugin_id"]).first()

            if plugin and plugin.version != sp["version"]:
                updates.append(
                    {
                        "plugin_id": plugin.id,
                        "name": plugin.name,
                        "current_version": sp["version"],
                        "latest_version": plugin.version,
                    }
                )

        return updates

    async def auto_update_plugin(self, server_id: int, plugin_id: int) -> Tuple[bool, str]:
        """
        Automatically update a plugin to latest version.

        Args:
            server_id: Server ID
            plugin_id: Plugin to update

        Returns:
            (success, message)
        """
        # Uninstall old version
        success, message = await self.uninstall_plugin(server_id, plugin_id)

        if not success:
            return False, f"Failed to uninstall old version: {message}"

        # Get user who originally installed (or system)
        server_plugin = (
            self.db.query(ServerPlugin)
            .filter(ServerPlugin.server_id == server_id, ServerPlugin.plugin_id == plugin_id)
            .first()
        )

        user_id = server_plugin.installed_by if server_plugin else 1  # System user

        # Install new version
        success, message = await self.install_plugin(server_id, plugin_id, user_id)

        if not success:
            return False, f"Failed to install new version: {message}"

        return True, "Plugin updated successfully"

    def get_plugin_stats(self) -> Dict:
        """Get overall plugin statistics"""
        total_plugins = self.db.query(Plugin).count()
        active_plugins = self.db.query(Plugin).filter(Plugin.is_active == True).count()

        total_installations = self.db.query(ServerPlugin).count()

        # Most popular plugins
        from sqlalchemy import func

        popular = (
            self.db.query(Plugin.name, func.count(ServerPlugin.id).label("install_count"))
            .join(ServerPlugin, Plugin.id == ServerPlugin.plugin_id)
            .group_by(Plugin.id, Plugin.name)
            .order_by(func.count(ServerPlugin.id).desc())
            .limit(5)
            .all()
        )

        return {
            "total_plugins": total_plugins,
            "active_plugins": active_plugins,
            "total_installations": total_installations,
            "most_popular": [{"name": p.name, "installs": p.install_count} for p in popular],
        }


# ==================== AUTO-UPDATE TASK ====================


async def auto_update_plugins_task(db: Session) -> Dict:
    """
    Daily task to auto-update plugins (if enabled).

    This would check for updates and optionally auto-update
    plugins that have auto_update flag enabled.
    """
    service = PluginService(db)

    # Get all servers
    from app.models.database import ServerStatus

    servers = (
        db.query(GameServer)
        .filter(GameServer.status.in_([ServerStatus.RUNNING, ServerStatus.STOPPED]))
        .all()
    )

    updates_available = 0
    updates_applied = 0

    for server in servers:
        updates = await service.check_for_updates(server.id)
        updates_available += len(updates)

        # Note: Auto-update disabled by default for safety
        # Enable per-plugin auto_update flag in future

    logger.info(
        f"Plugin update check: {updates_available} updates available for {len(servers)} servers"
    )

    return {
        "servers_checked": len(servers),
        "updates_available": updates_available,
        "updates_applied": updates_applied,
    }
