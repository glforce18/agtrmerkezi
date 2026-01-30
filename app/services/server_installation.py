"""
AGTR Merkezi v6.0 - Server Installation Service
Oyun sunucusu kurulum ve yapilandirma servisi
"""

import asyncio
import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.database import (
    GameServer,
    InstallationStatus,
    OwnershipAction,
    ServerInstallation,
    ServerOwnershipHistory,
)

logger = logging.getLogger(__name__)


class ServerInstallationService:
    """
    Sunucu kurulum servisi

    Template'lerden sunucu kopyalama, yapilandirma ve kurulum takibi
    """

    # Dizin yapisi
    TEMPLATE_BASE = "/home/gameservers/templates/hlds"
    SERVERS_BASE = "/home/gameservers/servers"
    SCRIPTS_BASE = "/home/gameservers/scripts"

    # Template eslestirmeleri (game_type -> dizin adi)
    TEMPLATES = {
        "ag": "ag",
        "ag_openag": "ag_openag",
        "cs16": "cstrike",
        "hldm": "valve",
        "valve_new": "valvenewvalve",
    }

    # Mod klasor adlari
    MOD_FOLDERS = {
        "ag": "ag",
        "ag_openag": "ag",
        "cs16": "cstrike",
        "hldm": "valve",
        "valve_new": "valve",
    }

    # Kilitli cvar'lar (degistirilemez)
    LOCKED_CVARS = {
        "sys_ticrate": "500",
        "fps_max": "600",
        "sv_maxrate": "100000",
        "sv_minrate": "10000",
        "sv_lan": "0",
    }

    # Kurulum adimlari
    INSTALLATION_STEPS = [
        "Dizin hazirlaniyor",
        "Template kopyalaniyor",
        "server.cfg yapilandiriliyor",
        "AMXModX ayarlaniyor",
        "Admin listesi olusturuluyor",
        "Baslangic scripti hazirlaniyor",
        "Kurulum dogrulaniyor",
        "Test baslatiliyor",
    ]

    def __init__(self, db: Session):
        self.db = db

    def generate_unique_code(self) -> str:
        """
        Benzersiz sunucu kodu olustur
        Format: AGTR-2026-00001
        """
        year = datetime.now().year

        # Bu yil icin en yuksek kodu bul
        prefix = f"AGTR-{year}-"

        last_server = (
            self.db.query(GameServer)
            .filter(GameServer.unique_code.like(f"{prefix}%"))
            .order_by(GameServer.unique_code.desc())
            .first()
        )

        if last_server and last_server.unique_code:
            # Mevcut kodun numarasini al ve artir
            try:
                last_num = int(last_server.unique_code.split("-")[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1

        return f"{prefix}{new_num:05d}"

    def get_template_path(self, mod_type: str) -> Optional[Path]:
        """Template dizin yolunu al"""
        template_dir = self.TEMPLATES.get(mod_type)
        if not template_dir:
            return None

        path = Path(self.TEMPLATE_BASE) / template_dir
        if not path.exists():
            logger.error(f"Template bulunamadi: {path}")
            return None

        return path

    def get_server_path(self, server_id: int) -> Path:
        """Sunucu dizin yolunu al"""
        return Path(self.SERVERS_BASE) / f"server_{server_id}"

    def get_mod_folder(self, mod_type: str) -> str:
        """Mod klasor adini al"""
        return self.MOD_FOLDERS.get(mod_type, "valve")

    async def create_installation(
        self, server_id: int, user_id: int, mod_type: str, config: Dict
    ) -> ServerInstallation:
        """
        Yeni kurulum kaydi olustur

        Args:
            server_id: Sunucu ID
            user_id: Kullanici ID
            mod_type: Mod tipi (ag, cs16, hldm, etc.)
            config: Yapilandirma ayarlari

        Returns:
            ServerInstallation instance
        """
        unique_code = self.generate_unique_code()

        installation = ServerInstallation(
            server_id=server_id,
            user_id=user_id,
            unique_code=unique_code,
            status=InstallationStatus.PENDING,
            progress_percent=0,
            current_step=self.INSTALLATION_STEPS[0],
            total_steps=len(self.INSTALLATION_STEPS),
            template_type=mod_type,
            created_at=datetime.utcnow(),
        )

        self.db.add(installation)
        self.db.commit()
        self.db.refresh(installation)

        # Sunucuya unique_code ekle
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if server:
            server.unique_code = unique_code
            server.mod_type = mod_type
            server.installation_id = installation.id
            self.db.commit()

        return installation

    async def update_installation_progress(
        self, installation_id: int, step: int, progress: int, error: Optional[str] = None
    ):
        """Kurulum ilerlemesini guncelle ve WebSocket ile broadcast et"""
        installation = (
            self.db.query(ServerInstallation)
            .filter(ServerInstallation.id == installation_id)
            .first()
        )

        if not installation:
            return

        installation.progress_percent = progress
        current_step_name = (
            self.INSTALLATION_STEPS[step] if step < len(self.INSTALLATION_STEPS) else "Tamamlaniyor"
        )
        installation.current_step = current_step_name

        if error:
            installation.status = InstallationStatus.FAILED
            installation.error_message = error

        self.db.commit()

        # Broadcast progress via WebSocket
        try:
            from app.services.installation_progress import installation_progress_manager

            await installation_progress_manager.broadcast_progress(
                server_id=installation.server_id,
                stage=current_step_name,
                progress=progress,
                message=f"{current_step_name} ({progress}%)",
                error=error,
            )
        except Exception as e:
            logger.debug(f"Failed to broadcast installation progress: {e}")

    async def copy_template(
        self, server_id: int, mod_type: str, installation_id: int
    ) -> Tuple[bool, str]:
        """
        Template'i sunucu dizinine kopyala (2-stage: base HLDS + mod folder)

        Args:
            server_id: Sunucu ID
            mod_type: Mod tipi
            installation_id: Kurulum ID

        Returns:
            (basari, mesaj)
        """
        from app.services.template_cache_service import TemplateCacheService

        server_path = self.get_server_path(server_id)

        # Dizin varsa temizle
        if server_path.exists():
            try:
                shutil.rmtree(server_path)
            except Exception as e:
                logger.error(f"Dizin temizleme hatasi: {e}")
                return False, f"Dizin temizlenemedi: {e}"

        # Parent dizini olustur
        server_path.parent.mkdir(parents=True, exist_ok=True)

        # Try cache first (3x faster)
        cache_service = TemplateCacheService(self.db)

        if cache_service.is_cache_available(mod_type):
            logger.info(f"Using template cache for {mod_type} (fast extraction)")

            success, message = await cache_service.extract_template_archive(mod_type, server_path)

            if success:
                logger.info(f"Template extracted from cache: {server_path}")
                return True, "Template extracted from cache (fast)"
            else:
                logger.warning(f"Cache extraction failed: {message}, falling back to rsync")

        # Fallback to rsync if cache not available or extraction failed
        logger.info(f"Using rsync fallback for {mod_type} (2-stage copy)")

        template_base_path = Path(self.TEMPLATE_BASE)
        if not template_base_path.exists():
            return False, f"Template base bulunamadi: {self.TEMPLATE_BASE}"

        try:
            # STAGE 1: Copy base HLDS files (hlds_run, .so files, etc.)
            logger.info("Stage 1: Copying base HLDS files")

            # Exclude mod folders during base copy
            exclude_mods = ["valve", "cstrike", "ag", "ag_openag", "valvenewvalve", "valve_addon"]
            exclude_args = []
            for mod in exclude_mods:
                exclude_args.extend(["--exclude", mod])

            cmd_base = (
                ["rsync", "-a"] + exclude_args + [f"{template_base_path}/", f"{server_path}/"]
            )

            process = await asyncio.create_subprocess_exec(
                *cmd_base, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Bilinmeyen hata"
                logger.error(f"Stage 1 rsync hatasi: {error_msg}")
                return False, f"Base HLDS kopyalama hatasi: {error_msg}"

            logger.info(f"Stage 1 completed: Base HLDS copied to {server_path}")

            # STAGE 2: Copy specific mod folder
            mod_folder_name = self.TEMPLATES.get(mod_type)
            if not mod_folder_name:
                return False, f"Mod tipi bulunamadi: {mod_type}"

            mod_source_path = template_base_path / mod_folder_name
            if not mod_source_path.exists():
                return False, f"Mod klasoru bulunamadi: {mod_source_path}"

            mod_dest_path = server_path / mod_folder_name

            logger.info(f"Stage 2: Copying mod folder {mod_folder_name}")

            cmd_mod = ["rsync", "-a", f"{mod_source_path}/", f"{mod_dest_path}/"]

            process = await asyncio.create_subprocess_exec(
                *cmd_mod, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Bilinmeyen hata"
                logger.error(f"Stage 2 rsync hatasi: {error_msg}")
                return False, f"Mod kopyalama hatasi: {error_msg}"

            logger.info(f"Stage 2 completed: Mod {mod_folder_name} copied to {mod_dest_path}")
            logger.info(f"Template installation completed: {server_path}")
            return True, "Basarili (2-stage rsync)"

        except Exception as e:
            logger.error(f"Template kopyalama hatasi: {e}")
            return False, str(e)

    def configure_server(
        self,
        server_id: int,
        hostname: str,
        rcon_password: str,
        sv_password: Optional[str] = None,
        maxplayers: int = 32,
        port: int = 27015,
    ) -> Tuple[bool, str]:
        """
        server.cfg dosyasini yapilandir

        Kilitli degerler (sys_ticrate, fps_max, etc.) korunur
        """
        server_path = self.get_server_path(server_id)

        # Sunucu modunu bul
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            return False, "Sunucu bulunamadi"

        mod_folder = self.get_mod_folder(server.mod_type)
        config_path = server_path / mod_folder / "server.cfg"

        if not config_path.exists():
            return False, f"server.cfg bulunamadi: {config_path}"

        try:
            # Mevcut config'i oku
            with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Ayarlanacak degerler
            new_values = {
                "hostname": f'"{hostname}"',
                "rcon_password": f'"{rcon_password}"',
                "maxplayers": str(maxplayers),
                "sv_maxplayers": str(maxplayers),
            }

            if sv_password:
                new_values["sv_password"] = f'"{sv_password}"'

            # Her degeri guncelle veya ekle
            for cvar, value in new_values.items():
                pattern = rf"^(\s*{cvar}\s+).*$"
                replacement = f"{cvar} {value}"

                if re.search(pattern, content, re.MULTILINE):
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                else:
                    content += f"\n{replacement}"

            # Kilitli degerleri zorla
            content = self._enforce_locked_cvars(content)

            # Kaydet
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Sunucu bilgilerini guncelle
            server.server_path = str(server_path)
            server.screen_name = f"agtr_{server_id}"
            self.db.commit()

            logger.info(f"server.cfg yapilandirildi: {config_path}")
            return True, "Basarili"

        except Exception as e:
            logger.error(f"Config yapilandirma hatasi: {e}")
            return False, str(e)

    def _enforce_locked_cvars(self, content: str) -> str:
        """Kilitli cvar'lari zorla"""
        for cvar, value in self.LOCKED_CVARS.items():
            pattern = rf"^(\s*{cvar}\s+).*$"
            replacement = f'{cvar} "{value}"'

            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            else:
                content += f"\n{replacement}"

        return content

    def setup_amxx_config(
        self, server_id: int, admin_steam_ids: List[Dict] = None
    ) -> Tuple[bool, str]:
        """
        AMXModX yapilandirmasi

        Args:
            server_id: Sunucu ID
            admin_steam_ids: Admin listesi [{"steam_id": "...", "flags": "...", "password": "..."}]
        """
        server_path = self.get_server_path(server_id)
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            return False, "Sunucu bulunamadi"

        mod_folder = self.get_mod_folder(server.mod_type)
        amxx_path = server_path / mod_folder / "addons" / "amxmodx"

        if not amxx_path.exists():
            return False, f"AMXModX dizini bulunamadi: {amxx_path}"

        # users.ini olustur
        users_ini_path = amxx_path / "configs" / "users.ini"

        try:
            lines = [
                "; AGTR Merkezi - Auto-generated Admin List",
                f"; Server ID: {server_id}",
                f"; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ";",
                '; Format: "auth" "password" "access" "flags"',
                ";",
            ]

            if admin_steam_ids:
                for admin in admin_steam_ids:
                    steam_id = admin.get("steam_id", "")
                    flags = admin.get("flags", "abcdefghijklmnopqrstu")
                    password = admin.get("password", "")

                    if password:
                        lines.append(f'"{steam_id}" "{password}" "{flags}" "a"')
                    else:
                        lines.append(f'"{steam_id}" "" "{flags}" "ce"')

            # Kaydet
            users_ini_path.parent.mkdir(parents=True, exist_ok=True)
            with open(users_ini_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            logger.info(f"users.ini olusturuldu: {users_ini_path}")
            return True, "Basarili"

        except Exception as e:
            logger.error(f"AMXModX config hatasi: {e}")
            return False, str(e)

    def create_startup_script(
        self, server_id: int, port: int = 27015, maxplayers: int = 32
    ) -> Tuple[bool, str]:
        """
        Sunucu baslangic scripti olustur
        """
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            return False, "Sunucu bulunamadi"

        server_path = self.get_server_path(server_id)
        mod_folder = self.get_mod_folder(server.mod_type)

        # Startup script icerigi
        script_content = f"""#!/bin/bash
# AGTR Merkezi - Server Startup Script
# Server ID: {server_id}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SERVER_DIR="{server_path}"
SCREEN_NAME="agtr_{server_id}"
MOD="{mod_folder}"
PORT={port}
MAXPLAYERS={maxplayers}

cd "$SERVER_DIR"

# Mevcut session varsa durdur
screen -S $SCREEN_NAME -X quit 2>/dev/null

# Sunucuyu baslat
screen -dmS $SCREEN_NAME ./hlds_run -game $MOD +port $PORT +maxplayers $MAXPLAYERS -pingboost 3 +sys_ticrate 500

echo "Server started: $SCREEN_NAME"
"""

        script_path = server_path / "start.sh"

        try:
            with open(script_path, "w") as f:
                f.write(script_content)

            # Calistirma izni ver
            os.chmod(script_path, 0o755)

            # Stop script
            stop_content = f"""#!/bin/bash
# AGTR Merkezi - Server Stop Script
SCREEN_NAME="agtr_{server_id}"

screen -S $SCREEN_NAME -X quit 2>/dev/null
echo "Server stopped: $SCREEN_NAME"
"""

            stop_path = server_path / "stop.sh"
            with open(stop_path, "w") as f:
                f.write(stop_content)
            os.chmod(stop_path, 0o755)

            logger.info(f"Startup scriptleri olusturuldu: {server_path}")
            return True, "Basarili"

        except Exception as e:
            logger.error(f"Script olusturma hatasi: {e}")
            return False, str(e)

    def validate_installation(self, server_id: int) -> Tuple[bool, List[str]]:
        """
        Kurulumu dogrula

        Returns:
            (basari, eksik_dosyalar)
        """
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            return False, ["Sunucu bulunamadi"]

        server_path = self.get_server_path(server_id)
        mod_folder = self.get_mod_folder(server.mod_type)

        # Kontrol edilecek dosyalar
        required_files = [
            "hlds_run",
            "hlds_linux",
            f"{mod_folder}/server.cfg",
            f"{mod_folder}/mapcycle.txt",
            f"{mod_folder}/addons/amxmodx/configs/users.ini",
            "start.sh",
            "stop.sh",
        ]

        missing = []
        for file in required_files:
            file_path = server_path / file
            if not file_path.exists():
                missing.append(file)

        if missing:
            logger.warning(f"Eksik dosyalar: {missing}")
            return False, missing

        return True, []

    async def test_start(self, server_id: int) -> Tuple[bool, str]:
        """
        Sunucuyu test icin baslat ve hemen durdur
        """
        server_path = self.get_server_path(server_id)
        start_script = server_path / "start.sh"

        if not start_script.exists():
            return False, "start.sh bulunamadi"

        try:
            # Baslat
            process = await asyncio.create_subprocess_exec(
                str(start_script),
                cwd=str(server_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            await process.communicate()

            # 3 saniye bekle
            await asyncio.sleep(3)

            # Screen session kontrol
            check_cmd = f"screen -ls | grep agtr_{server_id}"
            check_process = await asyncio.create_subprocess_shell(
                check_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await check_process.communicate()

            if f"agtr_{server_id}" in stdout.decode():
                # Durdur
                stop_script = server_path / "stop.sh"
                if stop_script.exists():
                    stop_process = await asyncio.create_subprocess_exec(
                        str(stop_script), cwd=str(server_path)
                    )
                    await stop_process.communicate()

                return True, "Test basarili"
            else:
                return False, "Sunucu baslatma hatasi"

        except Exception as e:
            logger.error(f"Test baslat hatasi: {e}")
            return False, str(e)

    async def run_installation(self, installation_id: int, config: Dict) -> Tuple[bool, str]:
        """
        Tam kurulum islemini calistir

        Config parametreleri:
        - hostname: Sunucu adi
        - rcon_password: RCON sifresi
        - sv_password: Sunucu sifresi (opsiyonel)
        - port: Port
        - maxplayers: Maksimum oyuncu
        - admins: Admin listesi
        """
        installation = (
            self.db.query(ServerInstallation)
            .filter(ServerInstallation.id == installation_id)
            .first()
        )

        if not installation:
            return False, "Kurulum bulunamadi"

        server_id = installation.server_id
        mod_type = installation.template_type

        try:
            # Basla
            installation.status = InstallationStatus.INSTALLING
            installation.started_at = datetime.utcnow()
            self.db.commit()

            # Adim 1: Dizin hazirlama (10%)
            await self.update_installation_progress(installation_id, 0, 10)
            server_path = self.get_server_path(server_id)
            server_path.parent.mkdir(parents=True, exist_ok=True)

            # Adim 2: Template kopyalama (40%)
            await self.update_installation_progress(installation_id, 1, 20)
            success, msg = await self.copy_template(server_id, mod_type, installation_id)
            if not success:
                await self.update_installation_progress(installation_id, 1, 20, msg)
                return False, msg
            await self.update_installation_progress(installation_id, 1, 40)

            # Adim 3: server.cfg yapilandirma (50%)
            await self.update_installation_progress(installation_id, 2, 45)
            success, msg = self.configure_server(
                server_id,
                hostname=config.get("hostname", f"AGTR Server #{server_id}"),
                rcon_password=config.get("rcon_password", "changeme"),
                sv_password=config.get("sv_password"),
                maxplayers=config.get("maxplayers", 32),
                port=config.get("port", 27015),
            )
            if not success:
                await self.update_installation_progress(installation_id, 2, 45, msg)
                return False, msg
            await self.update_installation_progress(installation_id, 2, 50)

            # Adim 4: AMXModX ayarlari (60%)
            await self.update_installation_progress(installation_id, 3, 55)
            # Ek AMXModX ayarlari yapilabilir
            await self.update_installation_progress(installation_id, 3, 60)

            # Adim 5: Admin listesi (70%)
            await self.update_installation_progress(installation_id, 4, 65)
            admins = config.get("admins", [])
            success, msg = self.setup_amxx_config(server_id, admins)
            if not success:
                await self.update_installation_progress(installation_id, 4, 65, msg)
                return False, msg
            await self.update_installation_progress(installation_id, 4, 70)

            # Auto-admin: Sahip otomatik admin olarak ekle
            try:
                from app.services.amxx_admin import AMXXAdminService

                amxx_service = AMXXAdminService(self.db)
                success, msg = amxx_service.add_owner_as_admin(server_id, installation.user_id)
                if success:
                    logger.info(f"Auto-admin: {msg}")
                else:
                    logger.warning(f"Auto-admin hatasi: {msg}")
            except Exception as e:
                logger.error(f"Auto-admin exception: {e}")

            # Adim 6: Startup script (80%)
            await self.update_installation_progress(installation_id, 5, 75)
            success, msg = self.create_startup_script(
                server_id, port=config.get("port", 27015), maxplayers=config.get("maxplayers", 32)
            )
            if not success:
                await self.update_installation_progress(installation_id, 5, 75, msg)
                return False, msg
            await self.update_installation_progress(installation_id, 5, 80)

            # Adim 7: Dogrulama (90%)
            await self.update_installation_progress(installation_id, 6, 85)
            valid, missing = self.validate_installation(server_id)
            if not valid:
                msg = f"Eksik dosyalar: {', '.join(missing)}"
                await self.update_installation_progress(installation_id, 6, 85, msg)
                return False, msg
            await self.update_installation_progress(installation_id, 6, 90)

            # Adim 8: Test baslat (100%)
            await self.update_installation_progress(installation_id, 7, 95)
            success, msg = await self.test_start(server_id)
            if not success:
                # Test hatasi kritik degil, uyari ver
                logger.warning(f"Test baslat hatasi: {msg}")
            await self.update_installation_progress(installation_id, 7, 100)

            # Tamamlandi
            installation.status = InstallationStatus.COMPLETED
            installation.completed_at = datetime.utcnow()
            self.db.commit()

            # Sahiplik kaydini olustur
            self._record_ownership(server_id, installation.user_id, OwnershipAction.CREATED)

            logger.info(f"Kurulum tamamlandi: Server {server_id}")
            return True, "Kurulum basariyla tamamlandi"

        except Exception as e:
            logger.error(f"Kurulum hatasi: {e}")
            installation.status = InstallationStatus.FAILED
            installation.error_message = str(e)
            self.db.commit()
            return False, str(e)

    def _record_ownership(
        self, server_id: int, user_id: int, action: OwnershipAction, details: Dict = None
    ):
        """Sahiplik kaydini olustur"""
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()

        record = ServerOwnershipHistory(
            server_id=server_id,
            user_id=user_id,
            unique_code=server.unique_code if server else None,
            action=action,
            details=details,
            created_at=datetime.utcnow(),
        )

        self.db.add(record)
        self.db.commit()

    def cancel_installation(self, installation_id: int) -> bool:
        """Kurulumu iptal et"""
        installation = (
            self.db.query(ServerInstallation)
            .filter(ServerInstallation.id == installation_id)
            .first()
        )

        if not installation:
            return False

        if installation.status in [InstallationStatus.COMPLETED, InstallationStatus.CANCELLED]:
            return False

        installation.status = InstallationStatus.CANCELLED
        self.db.commit()

        # Dizini temizle
        server_path = self.get_server_path(installation.server_id)
        if server_path.exists():
            try:
                shutil.rmtree(server_path)
            except Exception as e:
                logger.error(f"Dizin temizleme hatasi: {e}")

        return True

    def get_installation_status(self, installation_id: int) -> Optional[Dict]:
        """Kurulum durumunu al"""
        installation = (
            self.db.query(ServerInstallation)
            .filter(ServerInstallation.id == installation_id)
            .first()
        )

        if not installation:
            return None

        return {
            "id": installation.id,
            "server_id": installation.server_id,
            "unique_code": installation.unique_code,
            "status": installation.status.value if installation.status else None,
            "progress_percent": installation.progress_percent,
            "current_step": installation.current_step,
            "total_steps": installation.total_steps,
            "error_message": installation.error_message,
            "template_type": installation.template_type,
            "started_at": installation.started_at.isoformat() if installation.started_at else None,
            "completed_at": (
                installation.completed_at.isoformat() if installation.completed_at else None
            ),
            "created_at": installation.created_at.isoformat() if installation.created_at else None,
        }

    def delete_server_files(self, server_id: int) -> Tuple[bool, str]:
        """Sunucu dosyalarini sil"""
        server_path = self.get_server_path(server_id)

        if not server_path.exists():
            return True, "Dizin zaten mevcut degil"

        try:
            shutil.rmtree(server_path)
            logger.info(f"Sunucu dizini silindi: {server_path}")
            return True, "Basarili"
        except Exception as e:
            logger.error(f"Dizin silme hatasi: {e}")
            return False, str(e)
