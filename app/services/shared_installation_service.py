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
        "maps",  # Custom maps
        "addons",  # AMXModX plugins
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
        "users.ini",
        "amxx.cfg",
        "plugins.ini",
    ]

    # Base oyun dosyaları (her sunucu için symlink)
    SHARED_BINARIES = [
        "hlds_linux",
        "hlds_run",
        "libsteam.so",
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
            "valve_new": "valve_base",
        }
        return Path(self.SHARED_BASE) / mod_map.get(mod_type, "hlds_base")

    def get_server_path(self, server_id: int) -> Path:
        """Sunucu dizin yolunu al"""
        return Path(self.SERVERS_BASE) / f"server_{server_id}"

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
            "valve_new": "valvenewvalve",
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
        server_path = self.get_server_path(server_id)
        shared_base = self.get_shared_base_path(mod_type)

        # Mod klasör adı
        mod_folder_map = {
            "ag": "ag",
            "ag_openag": "ag",
            "cs16": "cstrike",
            "hldm": "valve",
            "valve_new": "valve",
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

        # 3. Shared binaries için symlink (hlds_linux, etc.)
        for binary in self.SHARED_BINARIES:
            source = (
                shared_hlds / binary
                if (shared_hlds / binary).exists()
                else shared_mod.parent / binary
            )
            target = server_path / binary

            if source.exists():
                try:
                    target.symlink_to(source)
                    logger.info(f"Symlink created: {binary}")
                except FileExistsError:
                    pass

        # 4. Mod klasörü için symlink'ler oluştur
        for folder in self.SHARED_FOLDERS:
            source = shared_mod / folder
            target = mod_path / folder

            if source.exists() and source.is_dir():
                try:
                    target.symlink_to(source)
                    logger.info(f"Symlink created: {mod_folder}/{folder} -> shared")
                except FileExistsError:
                    pass

        # 5. Individual klasörleri oluştur
        for folder in self.INDIVIDUAL_FOLDERS:
            (mod_path / folder).mkdir(exist_ok=True)

        # 6. Individual config dosyalarını kopyala
        for filename in self.INDIVIDUAL_FILES:
            source = shared_mod / filename
            target = mod_path / filename

            if source.exists() and source.is_file():
                try:
                    import shutil

                    shutil.copy2(source, target)
                    logger.info(f"Config copied: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to copy {filename}: {e}")

        # 7. server.cfg'yi düzenle
        server_cfg = mod_path / "server.cfg"
        if server_cfg.exists():
            self._configure_server_cfg(server_cfg, hostname, rcon_password, port, maxplayers)

        logger.info(f"Server created with symlinks: {server_path} (using shared base)")
        return True, "Server created successfully with shared files"

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
    backup_path = Path(f"/tmp/server_{server_id}_backup")

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
