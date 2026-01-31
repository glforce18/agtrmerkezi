"""
AGTR Merkezi v6.1 - Shared Game Files Installation Service
Disk tasarrufu için paylaşımlı oyun dosyaları ile sunucu kurulumu

Disk kullanımı: 2.5GB/sunucu -> 50MB/sunucu (%98 tasarruf)
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Tuple

from sqlalchemy.orm import Session

from app.models.database import GameServer

logger = logging.getLogger(__name__)


class SharedInstallationService:
    """
    Paylaşımlı dosya yapısı ile sunucu kurulum servisi

    Yapı:
    /home/gameservers/
    ├── shared/              # Paylaşımlı base dosyalar
    │   ├── hlds_base/      # Core HLDS (~1.8GB) - TÜM SUNUCULAR İÇİN TEK KOPYA
    │   ├── ag_base/        # AG mod (~700MB)
    │   ├── cstrike_base/   # CS 1.6 (~1GB)
    │   └── valve_base/     # HL DM (~400MB)
    └── servers/
        └── server_N/        # Her sunucu sadece ~50MB
            ├── hlds_linux -> ../../shared/hlds_base/hlds_linux (symlink)
            └── [mod]/
                ├── dlls -> ../../shared/[mod]_base/dlls (symlink)
                ├── sprites -> ../../shared/[mod]_base/sprites
                ├── models -> ../../shared/[mod]_base/models
                ├── sound -> ../../shared/[mod]_base/sound
                ├── server.cfg      (individual)
                ├── mapcycle.txt    (individual)
                ├── banned.cfg      (individual)
                ├── maps/           (custom maps only)
                └── addons/         (custom plugins)
    """

    SHARED_BASE = "/home/gameservers/shared"
    SERVERS_BASE = "/home/gameservers/servers"

    # Shared klasörler (symlink yapılacak)
    SHARED_FOLDERS = [
        "dlls",  # Mod binaries (read-only)
        "cl_dlls",  # Client DLLs
        "sprites",  # Sprites
        "models",  # Models
        "sound",  # Sounds
        "gfx",  # Graphics
        "events",  # Events
        "resource",  # Resources
    ]

    # Individual klasörler (her sunucu için ayrı)
    INDIVIDUAL_FOLDERS = [
        # NOTE: maps is copied fully in step 7.6 (all maps, not empty)
        # NOTE: addons is copied fully in step 7.5 (not empty)
        "logs",  # Server logs
        "demos",  # Demo recordings
    ]

    # Individual dosyalar (kopyalanacak ve düzenlenecek)
    INDIVIDUAL_FILES = [
        "server.cfg",
        "mapcycle.txt",
        "motd.txt",
        "banned.cfg",
        "listip.cfg",
        "liblist.gam",  # Metamod için gerekli
        "valve.rc",  # Server startup config
    ]

    # Base HLDS dosyaları (her sunucu için symlink)
    SHARED_HLDS_FILES = [
        # Executables
        "hlds_linux",
        "hlds_run",
        "hltv",
        # Libraries
        "*.so",
        # Other base files
        "steam_appid.txt",
        "steamapps",
        "linux64",
        "valve_addon",
    ]

    # Mod seviyesinde shared dosyalar (symlink)
    SHARED_MOD_FILES = [
        # WAD files
        "*.wad",
        # Config templates
        "*.lst",
        "*_textscheme.txt",
        "default.cfg",
        "config.cfg",
        "autoexec.cfg",
        "dproto.cfg",
        "credits.txt",
    ]

    def __init__(self, db: Session):
        self.db = db

    def get_shared_base_path(self, mod_type: str) -> Path:
        """Shared base klasör yolunu al"""
        mod_map = {
            "ag": "ag_base",
            "ag_openag": "ag_base",
            "cs16": "cstrike_base",
            "hldm": "valve_base",
        }
        return Path(self.SHARED_BASE) / mod_map.get(mod_type, "hlds_base")

    def get_server_path(self, server_id: int) -> Path:
        """Sunucu dizin yolunu al"""
        return Path(self.SERVERS_BASE) / f"server_{server_id}"

    def get_mod_folder(self, mod_type: str) -> str:
        """Mod klasör adını döndür"""
        # Map mod type to folder name
        mod_folders = {
            "ag": "ag",  # Adrenaline Gamer
            "hldm": "valve",  # Half-Life Deathmatch
            "cs16": "cstrike",  # Counter-Strike 1.6
        }
        return mod_folders.get(mod_type, "valve")

    async def initialize_shared_base(self, mod_type: str) -> Tuple[bool, str]:
        """
        Shared base klasörünü hazırla (ilk kurulumda bir kere)

        Template'ten shared klasöre kopyala
        """
        shared_path = self.get_shared_base_path(mod_type)

        if shared_path.exists():
            logger.info(f"Shared base already exists: {shared_path}")
            return True, "Shared base ready"

        logger.info(f"Initializing shared base: {shared_path}")

        # Template yolunu bul
        template_base = Path("/home/gameservers/templates/hlds")
        template_map = {
            "ag": "ag",
            "ag_openag": "ag_openag",
            "cs16": "cstrike",
            "hldm": "valve",
        }
        template_name = template_map.get(mod_type)
        if not template_name:
            return False, f"Unknown mod type: {mod_type}"

        template_path = template_base / template_name

        if not template_path.exists():
            return False, f"Template not found: {template_path}"

        # Shared base oluştur
        shared_path.parent.mkdir(parents=True, exist_ok=True)

        # rsync ile kopyala
        try:
            cmd = [
                "rsync",
                "-av",
                "--progress",
                f"{template_path}/",
                f"{shared_path}/",
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"rsync error: {error_msg}")
                return False, f"Copy failed: {error_msg}"

            logger.info(f"Shared base initialized: {shared_path}")
            return True, "Shared base created successfully"

        except Exception as e:
            logger.error(f"Shared base initialization failed: {e}")
            return False, str(e)

    async def create_server_with_symlinks(
        self,
        server_id: int,
        mod_type: str,
        hostname: str,
        rcon_password: str,
        port: int,
        maxplayers: int = 32,
    ) -> Tuple[bool, str]:
        """
        Symlink'lerle sunucu oluştur (HIZLI - sadece ~50MB)

        1. Shared base'i kontrol et/oluştur
        2. Server dizinini oluştur
        3. Shared klasörlere symlink oluştur
        4. Individual dosyaları kopyala
        5. Config dosyalarını düzenle
        """
        # Get server IP from database
        from app.models.database import GameServer

        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        server_ip = server.ip_address if server else None

        # Validate server_ip
        if not server:
            return False, f"Server {server_id} not found in database"
        if not server_ip:
            return False, f"Server {server_id} has no IP address assigned"

        server_path = self.get_server_path(server_id)
        shared_base = self.get_shared_base_path(mod_type)

        # Mod klasör adı
        mod_folder_map = {
            "ag": "ag",
            "ag_openag": "ag",
            "cs16": "cstrike",
            "hldm": "valve",
        }
        mod_folder = mod_folder_map.get(mod_type, "valve")

        # 1. Shared base'i hazırla
        if not shared_base.exists():
            success, msg = await self.initialize_shared_base(mod_type)
            if not success:
                return False, f"Shared base init failed: {msg}"

        # 2. Server dizini temizle ve oluştur
        if server_path.exists():
            try:
                import shutil

                shutil.rmtree(server_path)
            except Exception as e:
                logger.error(f"Failed to clean server dir: {e}")

        server_path.mkdir(parents=True, exist_ok=True)
        mod_path = server_path / mod_folder
        mod_path.mkdir(parents=True, exist_ok=True)

        shared_hlds = Path(self.SHARED_BASE) / "hlds_base"
        shared_mod = (
            shared_base / mod_folder if (shared_base / mod_folder).exists() else shared_base
        )

        # 3. HLDS seviyesinde dosyaları KOPYALA (Steam uyumluluk için symlink değil)
        import shutil

        # .so dosyaları ve diğer HLDS dosyaları - KOPYAL A (symlink DEĞİL)
        hlds_file_count = 0
        for pattern in ["*.so", "hlds_linux", "hlds_run", "hltv", "ld-linux*.so.*"]:
            for source_file in shared_hlds.glob(pattern):
                target = server_path / source_file.name
                if not target.exists():
                    try:
                        shutil.copy2(source_file, target)
                        target.chmod(0o755)
                        hlds_file_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to copy {source_file.name}: {e}")
        logger.info(f"Copied {hlds_file_count} HLDS binary files")

        # Klasörler (linux64, steamapps, valve_addon) - KOPYALA (400 MB limit)
        steam_folders = ["linux64", "steamapps", "valve_addon"]
        for folder_name in steam_folders:
            source = shared_hlds / folder_name
            target = server_path / folder_name
            if source.exists() and not target.exists():
                try:
                    shutil.copytree(source, target)
                    folder_size = sum(f.stat().st_size for f in target.rglob("*") if f.is_file())
                    logger.info(f"Copied {folder_name}: {folder_size / 1024 / 1024:.1f} MB")
                except Exception as e:
                    logger.warning(f"Failed to copy {folder_name}: {e}")

        # steam_appid.txt - KOPYALA
        if (shared_hlds / "steam_appid.txt").exists():
            try:
                shutil.copy2(shared_hlds / "steam_appid.txt", server_path / "steam_appid.txt")
            except Exception as e:
                logger.warning(f"Failed to copy steam_appid.txt: {e}")

        # 4. Mod klasörü için shared folder symlink'leri
        for folder in self.SHARED_FOLDERS:
            source = shared_mod / folder
            target = mod_path / folder

            if source.exists() and source.is_dir() and not target.exists():
                try:
                    target.symlink_to(source)
                    logger.info(f"Symlink: {mod_folder}/{folder} -> shared")
                except Exception as e:
                    logger.warning(f"Failed to symlink {folder}: {e}")

        # 5. Mod seviyesinde shared dosyalar (.wad, .lst, etc.)
        for pattern in ["*.wad", "*.lst", "*_textscheme.txt"]:
            for source_file in shared_mod.glob(pattern):
                target = mod_path / source_file.name
                if not target.exists():
                    try:
                        target.symlink_to(source_file)
                        logger.debug(f"Symlink: {source_file.name}")
                    except Exception as e:
                        logger.warning(f"Failed to symlink {source_file.name}: {e}")

        # 6. Template config dosyalarını kopyala (symlink değil, kopyala - düzenlenebilir olmalı)
        template_configs = [
            "default.cfg",
            "config.cfg",
            "autoexec.cfg",
            "dproto.cfg",
            "credits.txt",
        ]
        for filename in template_configs:
            source = shared_mod / filename
            target = mod_path / filename
            if source.exists() and not target.exists():
                try:
                    import shutil

                    shutil.copy2(source, target)
                    logger.debug(f"Copied: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to copy {filename}: {e}")

        # 7. Individual klasörleri oluştur
        for folder in self.INDIVIDUAL_FOLDERS:
            (mod_path / folder).mkdir(exist_ok=True, parents=True)

        # 7.5. addons klasörünü kopyala (metamod/amxmodx) - HER SERVER FARKLI CONFIG
        addons_source = shared_mod / "addons"
        addons_target = mod_path / "addons"
        if addons_source.exists() and not addons_target.exists():
            try:
                import shutil

                shutil.copytree(addons_source, addons_target)
                logger.info("Copied addons/ (metamod/amxmodx) - individual per server")

                # logs klasörünü boşalt (her server kendi logunu tutsun)
                logs_dir = addons_target / "amxmodx" / "logs"
                if logs_dir.exists():
                    for log_file in logs_dir.glob("*"):
                        log_file.unlink()
                    logger.debug("Cleared amxmodx logs")
            except Exception as e:
                logger.warning(f"Failed to copy addons: {e}")

        # 7.6. Maps: Base maplar symlink, custom maplar individual
        maps_source = shared_mod / "maps"
        maps_target = mod_path / "maps"
        if maps_source.exists():
            try:
                # Maps klasörünü oluştur
                maps_target.mkdir(exist_ok=True, parents=True)

                # Her base map için symlink oluştur (.bsp, .txt, .nav, .res)
                map_count = 0
                for map_file in maps_source.glob("*"):
                    if map_file.is_file():
                        target_map = maps_target / map_file.name
                        if not target_map.exists():
                            target_map.symlink_to(map_file)
                            map_count += 1

                logger.info(
                    f"Created symlinks for {map_count} base map files "
                    "(custom maps can be uploaded)"
                )
            except Exception as e:
                logger.warning(f"Failed to create map symlinks: {e}")

        # 8. Individual config dosyalarını kopyala
        for filename in self.INDIVIDUAL_FILES:
            source = shared_mod / filename
            target = mod_path / filename

            if source.exists() and source.is_file() and not target.exists():
                try:
                    import shutil

                    shutil.copy2(source, target)
                    logger.info(f"Config copied: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to copy {filename}: {e}")

        # 9. server.cfg'yi düzenle
        server_cfg = mod_path / "server.cfg"
        if server_cfg.exists():
            self._configure_server_cfg(server_cfg, hostname, rcon_password, port, maxplayers)

        # 10. start.sh ve stop.sh oluştur
        self._create_startup_scripts(server_id, mod_folder, server_ip, port, maxplayers)

        logger.info(f"Server created with symlinks: {server_path} (using shared base)")
        return True, "Server created successfully with shared files"

    def _create_startup_scripts(
        self, server_id: int, mod_folder: str, server_ip: str, port: int, maxplayers: int
    ):
        """start.sh ve stop.sh scriptleri oluştur"""
        server_path = self.get_server_path(server_id)
        screen_name = f"server_{server_id}"  # Control service expects this format

        # start.sh
        start_script = server_path / "start.sh"
        start_content = f"""#!/bin/bash
SERVER_DIR="{server_path}"
SCREEN_NAME="{screen_name}"
MOD="{mod_folder}"
IP="{server_ip}"
PORT={port}
MAXPLAYERS={maxplayers}

cd "$SERVER_DIR"

# Stop existing session
screen -S $SCREEN_NAME -X quit 2>/dev/null

# Start server in screen
screen -dmS $SCREEN_NAME ./hlds_run -game $MOD +ip $IP +port $PORT \\
    +map crossfire +maxplayers $MAXPLAYERS -pingboost 3 +sys_ticrate 500

echo "Server started in screen session: $SCREEN_NAME"
"""
        try:
            with open(start_script, "w") as f:
                f.write(start_content)
            start_script.chmod(0o755)
            logger.info(f"Created start.sh for server {server_id}")
        except Exception as e:
            logger.error(f"Failed to create start.sh: {e}")

        # stop.sh
        stop_script = server_path / "stop.sh"
        stop_content = f"""#!/bin/bash
SCREEN_NAME="{screen_name}"

# Send quit command
screen -S $SCREEN_NAME -X stuff 'quit\\n'

# Wait 10 seconds
sleep 10

# Force kill if still running
screen -S $SCREEN_NAME -X quit 2>/dev/null

echo "Server stopped: $SCREEN_NAME"
"""
        try:
            with open(stop_script, "w") as f:
                f.write(stop_content)
            stop_script.chmod(0o755)
            logger.info(f"Created stop.sh for server {server_id}")
        except Exception as e:
            logger.error(f"Failed to create stop.sh: {e}")

    def _configure_server_cfg(
        self, config_path: Path, hostname: str, rcon_password: str, port: int, maxplayers: int
    ):
        """server.cfg dosyasını düzenle"""
        try:
            with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Hostname
            content = self._update_cvar(content, "hostname", hostname)
            content = self._update_cvar(content, "sv_contact", "admin@agtrmerkezi.com")

            # RCON
            content = self._update_cvar(content, "rcon_password", rcon_password)

            # Network
            content = self._update_cvar(content, "port", str(port))
            content = self._update_cvar(content, "hostport", str(port))  # Also set hostport
            content = self._update_cvar(content, "maxplayers", str(maxplayers))
            content = self._update_cvar(content, "sv_maxrate", "100000")
            content = self._update_cvar(content, "sv_minrate", "10000")

            # Performance (kilitli değerler)
            content = self._update_cvar(content, "sys_ticrate", "500")
            content = self._update_cvar(content, "fps_max", "600")

            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"server.cfg configured: {config_path}")

        except Exception as e:
            logger.error(f"Failed to configure server.cfg: {e}")

    def _update_cvar(self, content: str, cvar: str, value: str) -> str:
        """Config dosyasında cvar güncelle"""
        import re

        pattern = rf'^\s*{re.escape(cvar)}\s+"[^"]*"'
        replacement = f'{cvar} "{value}"'

        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            # Yoksa ekle
            content += f'\n{cvar} "{value}"\n'

        return content

    def get_disk_usage_stats(self) -> Dict[str, any]:
        """
        Disk kullanım istatistiklerini hesapla

        Returns:
            {
                "shared_total_mb": 3800,
                "per_server_mb": 50,
                "total_servers": 10,
                "total_used_mb": 4300,
                "saved_vs_full_copy_mb": 21700,
                "efficiency_percent": 83.4
            }
        """
        import subprocess

        stats = {
            "shared_total_mb": 0,
            "per_server_avg_mb": 0,
            "total_servers": 0,
            "total_used_mb": 0,
            "saved_vs_full_copy_mb": 0,
            "efficiency_percent": 0,
        }

        try:
            # Shared base boyutu
            if Path(self.SHARED_BASE).exists():
                result = subprocess.run(
                    ["du", "-sm", self.SHARED_BASE],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    stats["shared_total_mb"] = int(result.stdout.split()[0])

            # Server dizinleri
            if Path(self.SERVERS_BASE).exists():
                servers = list(Path(self.SERVERS_BASE).glob("server_*"))
                stats["total_servers"] = len(servers)

                if servers:
                    total_server_mb = 0
                    for server_dir in servers:
                        result = subprocess.run(
                            ["du", "-sm", str(server_dir)],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0:
                            total_server_mb += int(result.stdout.split()[0])

                    stats["per_server_avg_mb"] = total_server_mb // len(servers) if servers else 0
                    stats["total_used_mb"] = stats["shared_total_mb"] + total_server_mb

            # Tasarruf hesaplama (2.5GB/sunucu varsayımı)
            avg_full_copy_mb = 2500
            full_copy_total = avg_full_copy_mb * stats["total_servers"]
            stats["saved_vs_full_copy_mb"] = full_copy_total - stats["total_used_mb"]

            if full_copy_total > 0:
                stats["efficiency_percent"] = round(
                    (stats["saved_vs_full_copy_mb"] / full_copy_total) * 100, 1
                )

        except Exception as e:
            logger.error(f"Failed to calculate disk stats: {e}")

        return stats


# API Endpoint için yardımcı fonksiyon
async def migrate_existing_server_to_shared(server_id: int, db: Session) -> Tuple[bool, str]:
    """
    Mevcut sunucuyu shared files yapısına migrate et

    1. Mevcut sunucuyu yedekle
    2. Custom dosyaları tespit et (maps, plugins)
    3. Sunucuyu sil
    4. Shared yapı ile yeniden oluştur
    5. Custom dosyaları geri kopyala
    """
    service = SharedInstallationService(db)

    server = db.query(GameServer).filter(GameServer.id == server_id).first()
    if not server:
        return False, "Server not found"

    old_path = service.get_server_path(server_id)
    backup_path = Path(f"/tmp/server_{server_id}_backup")  # nosec B108 - temporary backup

    try:
        # 1. Custom dosyaları yedekle
        import shutil

        if old_path.exists():
            backup_path.mkdir(parents=True, exist_ok=True)

            mod_folder = service.get_mod_folder(server.mod_type)
            custom_folders = ["maps", "addons", "logs"]

            for folder in custom_folders:
                source = old_path / mod_folder / folder
                if source.exists():
                    shutil.copytree(source, backup_path / folder)

        # 2. Yeni shared yapı ile oluştur
        success, msg = await service.create_server_with_symlinks(
            server_id, server.mod_type, server.name, server.rcon_password, server.port, server.slots
        )

        if not success:
            return False, f"Failed to create shared structure: {msg}"

        # 3. Custom dosyaları geri kopyala
        new_path = service.get_server_path(server_id)
        for folder in custom_folders:
            source = backup_path / folder
            target = new_path / mod_folder / folder
            if source.exists():
                shutil.copytree(source, target, dirs_exist_ok=True)

        # 4. Yedekleri temizle
        shutil.rmtree(backup_path)

        return True, "Server migrated to shared structure successfully"

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False, str(e)
