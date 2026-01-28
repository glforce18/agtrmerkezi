"""
AGTR Merkezi v6.0 - Plugin Manager Service
AMXModX plugin yonetimi servisi
"""

import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

SERVERS_BASE = "/home/gameservers/servers"

# DEFAULT AMXMODX PLUGINLERI - Bunlar kullaniciya gosterilmez ve duzenlenemez
DEFAULT_AMXX_PLUGINS = {
    "admin.amxx",
    "adminchat.amxx",
    "adminhelp.amxx",
    "adminslots.amxx",
    "adminvote.amxx",
    "multilingual.amxx",
    "mapchooser.amxx",
    "nextmap.amxx",
    "timeleft.amxx",
    "pausecfg.amxx",
    "cmdmenu.amxx",
    "plmenu.amxx",
    "telemenu.amxx",
    "menufront.amxx",
    "stats.amxx",
    "statscfg.amxx",
    "restmenu.amxx",
    "scrollmsg.amxx",
    "imessage.amxx",
    "miscstats.amxx",
    "stats_logging.amxx",
    # CS-specific defaults
    "admincmd.amxx",
    "antiflood.amxx",
    "galileo.amxx",
    "mapsmenu.amxx",
    "pluginmenu.amxx",
    # Half-Life AG Mod defaults
    "agmodx.amxx",
    "agmodx_arcade.amxx",
    "agmodx_arena.amxx",
    "agmodx_ctf.amxx",
    "agmodx_instagib.amxx",
    "agmodx_llhl.amxx",
    "agmodx_lms.amxx",
    "agmodx_lts.amxx",
    "agmodx_sgbow.amxx",
}


class PluginManagerService:
    """
    Plugin yonetim servisi

    AMXModX plugin kurulum, aktivasyon ve yonetimi
    """

    def _get_game_dir(self, server) -> str:
        """
        Sunucu game type'ina göre mod klasörünü döndür

        Args:
            server: GameServer instance

        Returns:
            Mod directory name (cstrike, valve, ag)
        """
        game_type_map = {"cs16": "cstrike", "hldm": "valve", "ag": "ag"}

        # Get game_type as string
        if hasattr(server, "game_type"):
            if hasattr(server.game_type, "value"):
                game_val = str(server.game_type.value).lower()
            else:
                game_val = str(server.game_type).lower()
        else:
            game_val = "cs16"  # default

        # Map to directory
        for key, value in game_type_map.items():
            if key in game_val:
                return value

        return "cstrike"  # default fallback

    def get_plugins_path(self, server_id: int, server=None) -> Path:
        """AMXModX plugins dizini"""
        if server:
            game_dir = self._get_game_dir(server)
        else:
            game_dir = "cstrike"  # fallback for backwards compatibility

        return (
            Path(SERVERS_BASE) / f"server_{server_id}" / game_dir / "addons" / "amxmodx" / "plugins"
        )

    def get_plugins_ini_path(self, server_id: int, server=None) -> Path:
        """plugins.ini dosya yolu"""
        if server:
            game_dir = self._get_game_dir(server)
        else:
            game_dir = "cstrike"  # fallback

        return (
            Path(SERVERS_BASE)
            / f"server_{server_id}"
            / game_dir
            / "addons"
            / "amxmodx"
            / "configs"
            / "plugins.ini"
        )

    def list_installed_plugins(self, server_id: int, server=None) -> List[Dict]:
        """
        Yuklenmis pluginleri listele - SADECE KULLANICI PLUGINLERI

        Default AMXModX pluginleri gosterilmez.
        Sadece kullanicinin yuklediği ve admin panelinden eklenen pluginler listelenir.

        Args:
            server_id: Sunucu ID
            server: GameServer instance (for game_dir detection)

        Returns:
            Plugin listesi (sadece kullanici pluginleri)
        """
        plugins_dir = self.get_plugins_path(server_id, server)

        if not plugins_dir.exists():
            return []

        enabled_plugins = self._get_enabled_plugins(server_id, server)

        plugins = []
        for plugin_file in plugins_dir.glob("*.amxx"):
            # GUVENLIK: Default AMXModX pluginlerini atla
            if plugin_file.name in DEFAULT_AMXX_PLUGINS:
                continue

            # Sadece kullanici pluginlerini listele
            info = self._extract_plugin_info(plugin_file)
            is_user_plugin = self._is_user_plugin(plugin_file)

            plugins.append(
                {
                    "filename": plugin_file.name,
                    "name": info.get("name", plugin_file.stem),
                    "version": info.get("version", "Unknown"),
                    "author": info.get("author", "Unknown"),
                    "size": plugin_file.stat().st_size,
                    "modified": datetime.fromtimestamp(plugin_file.stat().st_mtime).isoformat(),
                    "enabled": plugin_file.name in enabled_plugins,
                    "is_user_plugin": is_user_plugin,
                    "can_delete": is_user_plugin,  # Sadece kullanici pluginleri silinebilir
                }
            )

        return sorted(plugins, key=lambda x: x["name"])

    def _get_enabled_plugins(self, server_id: int, server=None) -> set:
        """
        Aktif pluginleri getir

        Args:
            server_id: Sunucu ID

        Returns:
            Aktif plugin dosya adlari seti
        """
        ini_path = self.get_plugins_ini_path(server_id, server)

        if not ini_path.exists():
            return set()

        enabled = set()
        for line in ini_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith(";") and not line.startswith("//"):
                enabled.add(line)

        return enabled

    def _extract_plugin_info(self, plugin_file: Path) -> Dict:
        """
        Plugin metadata cikar

        Args:
            plugin_file: Plugin dosyasi

        Returns:
            Metadata dict
        """
        try:
            # Binary dosyadan ilk 4KB oku
            with plugin_file.open("rb") as f:
                data = f.read(4096)

            # UTF-8 decode (hata toleransli)
            text = data.decode("utf-8", errors="ignore")

            info = {}

            # Basit heuristikler
            for line in text.split("\x00"):
                line_lower = line.lower()
                if "version" in line_lower and len(line) < 50:
                    info["version"] = line.strip()
                elif "author" in line_lower and len(line) < 50:
                    info["author"] = line.strip()

            return info
        except:
            return {}

    def _is_user_plugin(self, plugin_file: Path) -> bool:
        """
        Plugin kullanici tarafindan mi yuklendi kontrol et

        Kontrol mantigi:
        1. DEFAULT_AMXX_PLUGINS listesinde ise -> Sistem plugini (False)
        2. /var/www/scripting dizininde varsa -> Admin yukledi (False)
        3. Degilse -> Kullanici yukledi (True)

        Args:
            plugin_file: Plugin dosyasi

        Returns:
            True ise kullanici plugini (silinebilir), False ise admin/sistem plugini (silinemez)
        """
        # 1. Default plugin listesinde mi?
        if plugin_file.name in DEFAULT_AMXX_PLUGINS:
            return False

        # 2. Admin scripting dizininde var mi?
        admin_plugin = Path("/var/www/scripting") / plugin_file.name
        if admin_plugin.exists():
            return False

        # 3. Kullanici yukledi
        return True

    def is_plugin_enabled(self, server_id: int, filename: str, server=None) -> bool:
        """Plugin aktif mi kontrol et"""
        enabled = self._get_enabled_plugins(server_id)
        return filename in enabled

    def enable_plugin(
        self, server_id: int, filename: str, user_id: int, server=None
    ) -> Tuple[bool, str]:
        """
        Plugin'i aktif et - SADECE KULLANICI PLUGINLERI

        Args:
            server_id: Sunucu ID
            filename: Plugin dosya adi
            user_id: Kullanici ID

        Returns:
            (basari, mesaj)
        """
        # GUVENLIK: Default pluginleri aktif/pasif yapamaz
        if filename in DEFAULT_AMXX_PLUGINS:
            return (False, "Default AMXModX pluginleri değiştirilemez")

        ini_path = self.get_plugins_ini_path(server_id, server)

        # Plugin dosyasi var mi kontrol et
        plugin_file = self.get_plugins_path(server_id, server) / filename
        if not plugin_file.exists():
            return (False, "Plugin file not found")

        # Yedek olustur
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = ini_path.with_suffix(f".backup.{timestamp}")
        shutil.copy2(ini_path, backup_path)

        # Mevcut icerigi oku
        lines = ini_path.read_text().splitlines()

        # Zaten aktif mi kontrol et
        if filename in [l.strip() for l in lines if l.strip() and not l.startswith(";")]:
            return (True, "Plugin already enabled")

        # Plugin ekle
        lines.append(filename)
        ini_path.write_text("\n".join(lines) + "\n")

        logger.info(f"User {user_id} enabled plugin {filename} on server {server_id}")

        return (True, "Plugin enabled")

    def disable_plugin(
        self, server_id: int, filename: str, user_id: int, server=None
    ) -> Tuple[bool, str]:
        """
        Plugin'i devre disi birak - SADECE KULLANICI PLUGINLERI

        Args:
            server_id: Sunucu ID
            filename: Plugin dosya adi
            user_id: Kullanici ID

        Returns:
            (basari, mesaj)
        """
        # GUVENLIK: Default pluginleri aktif/pasif yapamaz
        if filename in DEFAULT_AMXX_PLUGINS:
            return (False, "Default AMXModX pluginleri değiştirilemez")

        ini_path = self.get_plugins_ini_path(server_id, server)

        # Yedek olustur
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = ini_path.with_suffix(f".backup.{timestamp}")
        shutil.copy2(ini_path, backup_path)

        # Satiri yorum yap
        lines = ini_path.read_text().splitlines()
        new_lines = []

        for line in lines:
            if line.strip() == filename:
                new_lines.append(f"; {line}")
            else:
                new_lines.append(line)

        ini_path.write_text("\n".join(new_lines) + "\n")

        logger.info(f"User {user_id} disabled plugin {filename} on server {server_id}")

        return (True, "Plugin disabled")

    def upload_plugin(self, server_id: int, file, user_id: int, server=None) -> Tuple[bool, str]:
        """
        Plugin yukle

        Args:
            server_id: Sunucu ID
            file: Upload dosyasi
            user_id: Kullanici ID

        Returns:
            (basari, mesaj)
        """
        filename = file.filename

        # Uzanti kontrolu
        if not filename.endswith(".amxx"):
            return (False, "Only .amxx files allowed")

        # Boyut limiti (10MB)
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)

        if size > 10 * 1024 * 1024:
            return (False, "File too large (max 10MB)")

        plugins_dir = self.get_plugins_path(server_id, server)
        plugins_dir.mkdir(parents=True, exist_ok=True)

        target_path = plugins_dir / filename

        # Mevcut dosyayi yedekle
        if target_path.exists():
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = target_path.with_suffix(f".amxx.backup.{timestamp}")
            shutil.copy2(target_path, backup_path)

        # Dosyayi yaz
        with target_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        logger.info(f"User {user_id} uploaded plugin {filename} to server {server_id}")

        return (True, "Plugin uploaded successfully")

    def delete_plugin(
        self, server_id: int, filename: str, user_id: int, server=None
    ) -> Tuple[bool, str]:
        """
        Plugin sil - SADECE KULLANICI PLUGINLERI

        Args:
            server_id: Sunucu ID
            filename: Plugin dosya adi
            user_id: Kullanici ID

        Returns:
            (basari, mesaj)
        """
        # GUVENLIK: Default pluginleri silemez
        if filename in DEFAULT_AMXX_PLUGINS:
            return (
                False,
                "Default AMXModX pluginleri silinemez. Sadece kendi yüklediğiniz pluginleri silebilirsiniz.",
            )

        plugin_file = self.get_plugins_path(server_id, server) / filename

        if not plugin_file.exists():
            return (False, "Plugin not found")

        # GUVENLIK: Kullanici plugini mi kontrol et
        if not self._is_user_plugin(plugin_file):
            return (False, "Bu plugin silinemez")

        # Aktif ise once devre disi birak
        if self.is_plugin_enabled(server_id, filename):
            self.disable_plugin(server_id, filename, user_id)

        # Yedek olustur
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(SERVERS_BASE) / f"server_{server_id}" / ".backups" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plugin_file, backup_dir / filename)

        # Sil
        plugin_file.unlink()

        logger.info(f"User {user_id} deleted plugin {filename} from server {server_id}")

        return (True, "Plugin deleted")

    def compile_plugin(
        self, server_id: int, sma_filename: str, user_id: int, server=None
    ) -> Tuple[bool, str]:
        """
        .sma kaynak dosyasini .amxx olarak derle

        Args:
            server_id: Sunucu ID
            sma_filename: Kaynak dosya adi
            user_id: Kullanici ID

        Returns:
            (basari, mesaj)
        """
        scripting_dir = (
            Path(SERVERS_BASE)
            / f"server_{server_id}"
            / "cstrike"
            / "addons"
            / "amxmodx"
            / "scripting"
        )
        sma_file = scripting_dir / sma_filename

        if not sma_file.exists():
            return (False, "Source file not found")

        compiler = scripting_dir / "amxxpc"
        if not compiler.exists():
            return (False, "Compiler not found")

        # Derle
        try:
            result = subprocess.run(
                [str(compiler), str(sma_file)],
                cwd=scripting_dir,
                capture_output=True,
                timeout=30,
            )

            if result.returncode != 0:
                error_msg = result.stderr.decode("utf-8", errors="ignore")
                return (False, f"Compilation failed: {error_msg}")

            # Derlenmis .amxx dosyasini plugins dizinine tasi
            amxx_filename = sma_file.stem + ".amxx"
            compiled_file = scripting_dir / amxx_filename

            if compiled_file.exists():
                plugins_dir = self.get_plugins_path(server_id, server)
                shutil.move(str(compiled_file), str(plugins_dir / amxx_filename))

                logger.info(f"User {user_id} compiled {sma_filename} on server {server_id}")

                return (True, f"Plugin compiled: {amxx_filename}")
            else:
                return (False, "Compilation produced no output")

        except subprocess.TimeoutExpired:
            return (False, "Compilation timeout")
        except Exception as e:
            return (False, f"Compilation error: {str(e)}")

    def get_marketplace_plugins(self) -> List[Dict]:
        """
        Plugin market listesi

        Returns:
            Populer plugin listesi
        """
        return [
            {
                "name": "Admin Commands",
                "filename": "admincmd.amxx",
                "description": "Temel admin komutları",
                "category": "Admin Tools",
                "download_url": "https://example.com/admincmd.amxx",
            },
            {
                "name": "Map Manager",
                "filename": "mapmanager.amxx",
                "description": "Gelişmiş harita yönetimi",
                "category": "Server Management",
                "download_url": "https://example.com/mapmanager.amxx",
            },
            {
                "name": "GunXP Mod",
                "filename": "gunxpmod.amxx",
                "description": "Silah deneyim sistemi",
                "category": "Gameplay",
                "download_url": "https://example.com/gunxpmod.amxx",
            },
        ]

    def get_plugin_status(self, server_id: int, filename: str, server=None) -> Dict:
        """
        Plugin'in gerçek durumunu kontrol et

        Returns:
            {
                "is_enabled_db": bool - Database'deki is_enabled değeri (kullanılmıyor artık)
                "is_enabled_ini": bool - plugins.ini'de aktif mi?
                "file_exists": bool - Plugin dosyası fiziksel olarak var mı?
                "is_running": bool - Sunucu çalışıyorsa RCON ile kontrol edilir (şimdilik False)
                "last_error": str | None - Son hata mesajı
            }
        """
        status = {
            "is_enabled_db": False,  # Artık kullanılmıyor, sadece backward compatibility
            "is_enabled_ini": False,
            "file_exists": False,
            "is_running": False,
            "last_error": None,
        }

        # 1. plugins.ini durumu kontrol et
        ini_path = self.get_plugins_ini_path(server_id, server)
        if ini_path.exists():
            try:
                content = ini_path.read_text(encoding="utf-8", errors="ignore")
                for line in content.splitlines():
                    line = line.strip()
                    # Yorum satırı değilse ve filename eşleşiyorsa aktif
                    if not line.startswith(";") and filename in line:
                        status["is_enabled_ini"] = True
                        break
            except Exception as e:
                logger.error(f"Error reading plugins.ini for server {server_id}: {e}")

        # 2. Plugin dosyası varlığı kontrol et
        plugin_file = self.get_plugins_path(server_id, server) / filename
        status["file_exists"] = plugin_file.exists()

        # 3. Son hata kontrolü
        status["last_error"] = self._get_last_plugin_error(server_id, filename)

        # 4. is_running durumu - RCON ile kontrol edilebilir (sonra implement edilecek)
        # Şimdilik False bırakıyoruz

        return status

    def _get_last_plugin_error(self, server_id: int, filename: str, server=None) -> Optional[str]:
        """
        AMXModX error loglarından plugin'e özel son hatayı bul

        Args:
            server_id: Sunucu ID
            filename: Plugin dosya adı (örn: "myplugin.amxx")

        Returns:
            Son hata mesajı veya None
        """
        game_dir = self._get_game_dir(server) if server else "cstrike"
        logs_path = (
            Path(SERVERS_BASE) / f"server_{server_id}" / game_dir / "addons" / "amxmodx" / "logs"
        )

        if not logs_path.exists():
            return None

        try:
            # En son error log dosyasını bul (error_YYYYMMDD.log formatında)
            error_logs = sorted(
                logs_path.glob("error_*.log"), key=lambda x: x.stat().st_mtime, reverse=True
            )

            if not error_logs:
                return None

            latest_log = error_logs[0]
            content = latest_log.read_text(encoding="utf-8", errors="ignore")

            # Plugin adını stem'den al (uzantısız)
            plugin_stem = Path(filename).stem

            # Plugin adını içeren son hatayı bul (tersten arama)
            for line in reversed(content.splitlines()):
                line_lower = line.lower()
                if plugin_stem.lower() in line_lower and any(
                    keyword in line_lower for keyword in ["error", "fail", "invalid", "not found"]
                ):
                    return line.strip()

            return None

        except Exception as e:
            logger.error(f"Error reading AMXModX logs for server {server_id}: {e}")
            return None

    def get_plugin_logs(
        self, server_id: int, filename: str, limit: int = 50, level: str = "all", server=None
    ) -> List[Dict]:
        """
        Plugin'e özel logları getir

        Args:
            server_id: Sunucu ID
            filename: Plugin dosya adı
            limit: Maksimum log sayısı
            level: Log seviyesi filtresi ('all', 'error', 'warning', 'info')

        Returns:
            Log listesi [{timestamp, level, message, source}]
        """
        logs = []
        plugin_stem = Path(filename).stem

        # AMXModX error loglarını parse et
        error_logs = self.parse_amxmodx_errors(server_id)

        # Plugin'e ait logları filtrele
        for log_entry in error_logs:
            if plugin_stem.lower() in log_entry["message"].lower():
                # Level filtreleme
                if level == "all" or log_entry["level"] == level:
                    logs.append(log_entry)

                if len(logs) >= limit:
                    break

        return logs

    def parse_amxmodx_errors(self, server_id: int, server=None) -> List[Dict]:
        """
        AMXModX error loglarını parse et ve yapılandır

        Args:
            server_id: Sunucu ID

        Returns:
            Log entry listesi (timestamp, level, message, source)
        """
        game_dir = self._get_game_dir(server) if server else "cstrike"
        logs_path = (
            Path(SERVERS_BASE) / f"server_{server_id}" / game_dir / "addons" / "amxmodx" / "logs"
        )
        all_logs = []

        if not logs_path.exists():
            return all_logs

        try:
            # Tüm error log dosyalarını bul (son 7 günlük)
            error_logs = sorted(
                logs_path.glob("error_*.log"), key=lambda x: x.stat().st_mtime, reverse=True
            )[
                :7
            ]  # Son 7 log dosyası

            for log_file in error_logs:
                try:
                    content = log_file.read_text(encoding="utf-8", errors="ignore")
                    file_date = log_file.stem.replace("error_", "")  # YYYYMMDD format

                    for line in content.splitlines():
                        line = line.strip()
                        if not line:
                            continue

                        # Log seviyesini belirle
                        level = "info"
                        if "error" in line.lower() or "fail" in line.lower():
                            level = "error"
                        elif "warn" in line.lower():
                            level = "warning"

                        # Timestamp parse etmeye çalış (L MM/DD/YYYY - HH:MM:SS: format)
                        timestamp_str = None
                        if line.startswith("L "):
                            # "L 01/25/2026 - 14:30:00:" gibi format
                            parts = line.split(":", 1)
                            if len(parts) > 0:
                                timestamp_str = parts[0].replace("L ", "").strip()

                        all_logs.append(
                            {
                                "timestamp": timestamp_str or file_date,
                                "level": level,
                                "message": line,
                                "source": "amxmodx",
                            }
                        )

                except Exception as e:
                    logger.error(f"Error parsing log file {log_file}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error reading AMXModX logs for server {server_id}: {e}")

        # En yeni loglar başta olsun
        all_logs.reverse()
        return all_logs
