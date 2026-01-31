"""
AGTR Merkezi - Plugin Manager Service
Kısıtlı plugin yönetimi servisi - kullanıcılar sadece kendi pluginlerini yönetebilir
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.database import GameServer, UserPlugin

logger = logging.getLogger(__name__)


class PluginManagerService:
    """
    Kısıtlı plugin yönetimi servisi

    Kurallar:
    - Kullanıcılar sadece kendi yükledikleri pluginleri yönetebilir
    - Server pluginlerine dokunamazlar
    - Sadece .amxx dosyaları yüklenebilir
    - plugins.ini'de sadece kendi pluginlerini aç/kapa yapabilirler
    """

    SERVERS_BASE = Path("/home/gameservers/servers")
    MAX_PLUGIN_SIZE = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = [".amxx"]

    def __init__(self, db: Session):
        self.db = db

    def get_server_path(self, server_id: int) -> Path:
        """Server dizinini döndür"""
        return self.SERVERS_BASE / f"server_{server_id}"

    def get_plugins_path(self, server_id: int) -> Path:
        """Plugins dizinini döndür"""
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise ValueError(f"Server {server_id} not found")

        # Mod klasörünü belirle
        mod_map = {
            "AG": "ag",
            "HLDM": "valve",
            "CS16": "cstrike",
        }
        mod_folder = mod_map.get(server.game_type.value, "valve")

        return self.get_server_path(server_id) / mod_folder / "addons" / "amxmodx" / "plugins"

    def get_user_plugins_path(self, server_id: int, user_id: int) -> Path:
        """Kullanıcının plugin dizinini döndür"""
        plugins_path = self.get_plugins_path(server_id)
        user_dir = plugins_path / "user_uploads" / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def get_plugins_ini_path(self, server_id: int) -> Path:
        """plugins.ini dosyasının yolunu döndür"""
        plugins_path = self.get_plugins_path(server_id)
        return plugins_path.parent / "configs" / "plugins.ini"

    def list_server_plugins(self, server_id: int) -> List[dict]:
        """
        Server pluginlerini listele (read-only)

        Returns:
            List of server plugins with metadata
        """
        plugins_path = self.get_plugins_path(server_id)
        server_plugins = []

        if not plugins_path.exists():
            return []

        # Sadece root dizindeki .amxx dosyaları (server pluginleri)
        for plugin_file in plugins_path.glob("*.amxx"):
            try:
                stat = plugin_file.stat()
                server_plugins.append(
                    {
                        "name": plugin_file.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": "server",
                        "enabled": self._is_plugin_enabled(server_id, plugin_file.name),
                        "can_delete": False,
                        "can_toggle": False,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to stat server plugin {plugin_file}: {e}")
                continue

        return sorted(server_plugins, key=lambda x: x["name"])

    def list_user_plugins(self, server_id: int, user_id: int) -> List[dict]:
        """
        Kullanıcının pluginlerini listele

        Returns:
            List of user's plugins with metadata
        """
        user_plugins_path = self.get_user_plugins_path(server_id, user_id)
        user_plugins = []

        if not user_plugins_path.exists():
            return []

        for plugin_file in user_plugins_path.glob("*.amxx"):
            try:
                stat = plugin_file.stat()
                relative_path = f"user_uploads/user_{user_id}/{plugin_file.name}"

                user_plugins.append(
                    {
                        "name": plugin_file.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": "user",
                        "enabled": self._is_plugin_enabled(server_id, relative_path),
                        "can_delete": True,
                        "can_toggle": True,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to stat user plugin {plugin_file}: {e}")
                continue

        return sorted(user_plugins, key=lambda x: x["name"])

    def _is_plugin_enabled(self, server_id: int, plugin_path: str) -> bool:
        """Check if plugin is enabled in plugins.ini"""
        try:
            plugins_ini = self.get_plugins_ini_path(server_id)
            if not plugins_ini.exists():
                return False

            content = plugins_ini.read_text()
            lines = content.split("\n")

            for line in lines:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith(";"):
                    continue

                # Check if this line matches the plugin
                if line == plugin_path or line.endswith(plugin_path):
                    return True

            return False
        except Exception as e:
            logger.error(f"Failed to check plugin status: {e}")
            return False

    def upload_plugin(
        self,
        server_id: int,
        user_id: int,
        filename: str,
        content: bytes,
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        Plugin yükle

        Args:
            server_id: Server ID
            user_id: User ID
            filename: Plugin filename
            content: File content

        Returns:
            (success, message, plugin_info)
        """
        try:
            # Validate filename
            if not filename.endswith(".amxx"):
                return False, "Sadece .amxx dosyaları yüklenebilir", None

            # Sanitize filename
            filename = Path(filename).name  # Remove any path components

            # Check file size
            if len(content) > self.MAX_PLUGIN_SIZE:
                return (
                    False,
                    f"Dosya boyutu {self.MAX_PLUGIN_SIZE / 1024 / 1024} MB'dan büyük olamaz",
                    None,
                )

            # Get user plugins directory
            user_plugins_path = self.get_user_plugins_path(server_id, user_id)
            target_file = user_plugins_path / filename

            # Check if file already exists
            if target_file.exists():
                return False, f"'{filename}' zaten mevcut", None

            # Write file
            target_file.write_bytes(content)
            target_file.chmod(0o644)

            # Track in database
            user_plugin = UserPlugin(
                user_id=user_id,
                server_id=server_id,
                filename=filename,
                size=len(content),
                uploaded_at=datetime.utcnow(),
            )
            self.db.add(user_plugin)
            self.db.commit()

            logger.info(f"User {user_id} uploaded plugin {filename} to server {server_id}")

            # Return plugin info
            plugin_info = {
                "name": filename,
                "size": len(content),
                "uploaded": datetime.utcnow().isoformat(),
                "type": "user",
                "enabled": False,
                "can_delete": True,
                "can_toggle": True,
            }

            return True, f"'{filename}' başarıyla yüklendi", plugin_info

        except Exception as e:
            logger.error(f"Failed to upload plugin: {e}", exc_info=True)
            return False, f"Yükleme hatası: {str(e)}", None

    def delete_plugin(
        self,
        server_id: int,
        user_id: int,
        filename: str,
    ) -> Tuple[bool, str]:
        """
        Kullanıcının kendi pluginini sil

        Args:
            server_id: Server ID
            user_id: User ID
            filename: Plugin filename

        Returns:
            (success, message)
        """
        try:
            # Get user plugins directory
            user_plugins_path = self.get_user_plugins_path(server_id, user_id)
            plugin_file = user_plugins_path / filename

            # Check if file exists
            if not plugin_file.exists():
                return False, f"'{filename}' bulunamadı"

            # Remove from plugins.ini if enabled
            relative_path = f"user_uploads/user_{user_id}/{filename}"
            if self._is_plugin_enabled(server_id, relative_path):
                self._toggle_plugin_in_ini(server_id, relative_path, enable=False)

            # Delete file
            plugin_file.unlink()

            # Remove from database
            self.db.query(UserPlugin).filter(
                UserPlugin.user_id == user_id,
                UserPlugin.server_id == server_id,
                UserPlugin.filename == filename,
            ).delete()
            self.db.commit()

            logger.info(f"User {user_id} deleted plugin {filename} from server {server_id}")

            return True, f"'{filename}' silindi"

        except Exception as e:
            logger.error(f"Failed to delete plugin: {e}", exc_info=True)
            return False, f"Silme hatası: {str(e)}"

    def toggle_plugin(
        self,
        server_id: int,
        user_id: int,
        filename: str,
        enable: bool,
    ) -> Tuple[bool, str]:
        """
        Kullanıcının pluginini aç/kapa

        Args:
            server_id: Server ID
            user_id: User ID
            filename: Plugin filename
            enable: True to enable, False to disable

        Returns:
            (success, message)
        """
        try:
            # Verify plugin belongs to user
            user_plugins_path = self.get_user_plugins_path(server_id, user_id)
            plugin_file = user_plugins_path / filename

            if not plugin_file.exists():
                return False, f"'{filename}' bulunamadı"

            # Toggle in plugins.ini
            relative_path = f"user_uploads/user_{user_id}/{filename}"
            success = self._toggle_plugin_in_ini(server_id, relative_path, enable)

            if success:
                action = "aktif edildi" if enable else "devre dışı bırakıldı"
                logger.info(
                    f"User {user_id} toggled plugin {filename} on server {server_id}: {action}"
                )
                return True, f"'{filename}' {action}"
            else:
                return False, "plugins.ini güncellenemedi"

        except Exception as e:
            logger.error(f"Failed to toggle plugin: {e}", exc_info=True)
            return False, f"Güncelleme hatası: {str(e)}"

    def _toggle_plugin_in_ini(self, server_id: int, plugin_path: str, enable: bool) -> bool:
        """Toggle plugin in plugins.ini file"""
        try:
            plugins_ini = self.get_plugins_ini_path(server_id)

            if not plugins_ini.exists():
                # Create if doesn't exist
                plugins_ini.parent.mkdir(parents=True, exist_ok=True)
                plugins_ini.write_text("")

            content = plugins_ini.read_text()
            lines = content.split("\n")
            new_lines = []
            plugin_found = False

            # USER PLUGINS marker
            user_section_marker = "; === USER PLUGINS ==="
            user_section_exists = any(user_section_marker in line for line in lines)

            for line in lines:
                stripped = line.strip()

                # Check if this is our plugin (enabled or disabled)
                if stripped == plugin_path or stripped == f";{plugin_path}":
                    plugin_found = True
                    if enable:
                        new_lines.append(plugin_path)
                    else:
                        new_lines.append(f";{plugin_path}")
                else:
                    new_lines.append(line)

            # If plugin not found, add it
            if not plugin_found and enable:
                # Add user section if it doesn't exist
                if not user_section_exists:
                    new_lines.append("")
                    new_lines.append(user_section_marker)

                new_lines.append(plugin_path)

            # Write back
            plugins_ini.write_text("\n".join(new_lines))
            return True

        except Exception as e:
            logger.error(f"Failed to toggle plugin in ini: {e}", exc_info=True)
            return False

    def get_plugin_stats(self, server_id: int, user_id: int) -> dict:
        """
        Plugin istatistiklerini döndür

        Returns:
            Statistics dict
        """
        server_plugins = self.list_server_plugins(server_id)
        user_plugins = self.list_user_plugins(server_id, user_id)

        user_size = sum(p["size"] for p in user_plugins)
        user_enabled = sum(1 for p in user_plugins if p["enabled"])

        return {
            "server_plugins_count": len(server_plugins),
            "user_plugins_count": len(user_plugins),
            "user_plugins_enabled": user_enabled,
            "user_plugins_size": user_size,
            "user_plugins_size_mb": round(user_size / 1024 / 1024, 2),
            "max_size_mb": self.MAX_PLUGIN_SIZE / 1024 / 1024,
        }
