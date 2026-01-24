"""
AGTR Merkezi v6.0 - Server Config Service
server.cfg, mapcycle.txt, motd.txt yonetimi
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.database import GameServer

logger = logging.getLogger(__name__)


class ServerConfigService:
    """
    Sunucu Yapilandirma Servisi

    Config dosyalarini okuma/yazma, kilitli degerleri koruma
    """

    SERVERS_BASE = "/home/gameservers/servers"

    # Kilitli cvar'lar (kullanici degistiremez)
    LOCKED_CVARS = {
        "sys_ticrate": "500",
        "fps_max": "600",
        "fps_override": "1",
        "sv_maxrate": "100000",
        "sv_minrate": "10000",
        "sv_maxupdaterate": "102",
        "sv_minupdaterate": "10",
        "sv_lan": "0",
        "sv_cheats": "0",
        "developer": "0",
    }

    # Hassas cvar'lar (saklanmali)
    SENSITIVE_CVARS = ["rcon_password", "sv_rcon_password", "sv_password"]

    # Mod klasor adlari
    MOD_FOLDERS = {
        "ag": "ag",
        "ag_openag": "ag",
        "cs16": "cstrike",
        "hldm": "valve",
        "valve_new": "valve",
    }

    # Duzenlenebilir config dosyalari
    EDITABLE_CONFIGS = ["server.cfg", "mapcycle.txt", "motd.txt", "listenserver.cfg", "game.cfg"]

    def __init__(self, db: Session):
        self.db = db

    def get_server_path(self, server_id: int) -> Path:
        """Sunucu dizin yolunu al"""
        return Path(self.SERVERS_BASE) / f"server_{server_id}"

    def get_mod_folder(self, server: GameServer) -> str:
        """Mod klasor adini al"""
        return self.MOD_FOLDERS.get(server.mod_type, "valve")

    def get_config_path(self, server: GameServer, filename: str) -> Path:
        """Config dosya yolunu al"""
        server_path = self.get_server_path(server.id)
        mod_folder = self.get_mod_folder(server)
        return server_path / mod_folder / filename

    def read_config(self, server: GameServer, filename: str) -> Tuple[Optional[str], str]:
        """
        Config dosyasini oku

        Args:
            server: GameServer instance
            filename: Dosya adi

        Returns:
            (icerik, mesaj)
        """
        if filename not in self.EDITABLE_CONFIGS:
            return None, f"Bu dosya duzenlenemez: {filename}"

        config_path = self.get_config_path(server, filename)

        if not config_path.exists():
            return None, f"Dosya bulunamadi: {filename}"

        try:
            with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Hassas degerleri gizle
            content = self._mask_sensitive_values(content)

            return content, "OK"

        except Exception as e:
            logger.error(f"Config okuma hatasi: {e}")
            return None, str(e)

    def write_config(
        self, server: GameServer, filename: str, content: str, user_id: int
    ) -> Tuple[bool, str]:
        """
        Config dosyasini yaz

        Args:
            server: GameServer instance
            filename: Dosya adi
            content: Yeni icerik
            user_id: Islemi yapan kullanici

        Returns:
            (basari, mesaj)
        """
        if filename not in self.EDITABLE_CONFIGS:
            return False, f"Bu dosya duzenlenemez: {filename}"

        config_path = self.get_config_path(server, filename)

        try:
            # Kilitli degerleri koru
            if filename == "server.cfg":
                content = self._protect_locked_values(content)

                # Mevcut hassas degerleri koru
                if config_path.exists():
                    existing = self._read_raw_config(config_path)
                    content = self._preserve_sensitive_values(existing, content)

            # Yedek al
            if config_path.exists():
                backup_path = config_path.with_suffix(
                    f'.backup.{datetime.now().strftime("%Y%m%d%H%M%S")}'
                )
                config_path.rename(backup_path)

            # Yaz
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Config yazildi: {config_path} (user: {user_id})")
            return True, "Basarili"

        except Exception as e:
            logger.error(f"Config yazma hatasi: {e}")
            return False, str(e)

    def _read_raw_config(self, path: Path) -> str:
        """Ham config oku (maskeleme olmadan)"""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

    def _protect_locked_values(self, content: str) -> str:
        """Kilitli cvar'lari zorla"""
        lines = content.split("\n")
        result = []
        found_cvars = set()

        for line in lines:
            stripped = line.strip()

            # Yorum veya bos satir
            if not stripped or stripped.startswith("//"):
                result.append(line)
                continue

            # Cvar satiri kontrol
            modified = False
            for cvar, value in self.LOCKED_CVARS.items():
                pattern = rf"^(\s*{cvar}\s+).*$"
                if re.match(pattern, stripped, re.IGNORECASE):
                    result.append(f'{cvar} "{value}"')
                    found_cvars.add(cvar)
                    modified = True
                    break

            if not modified:
                result.append(line)

        # Eksik kilitli cvar'lari ekle
        for cvar, value in self.LOCKED_CVARS.items():
            if cvar not in found_cvars:
                result.append(f'{cvar} "{value}"')

        return "\n".join(result)

    def _mask_sensitive_values(self, content: str) -> str:
        """Hassas degerleri maskele"""
        for cvar in self.SENSITIVE_CVARS:
            pattern = rf'({cvar}\s+)"[^"]*"'
            content = re.sub(pattern, r'\1"********"', content)
            pattern2 = rf"({cvar}\s+)(\S+)"
            content = re.sub(pattern2, r"\1********", content)

        return content

    def _preserve_sensitive_values(self, existing: str, new_content: str) -> str:
        """Hassas degerleri koru"""
        for cvar in self.SENSITIVE_CVARS:
            # Mevcut degeri bul
            match = re.search(rf'{cvar}\s+"([^"]*)"', existing)
            if not match:
                match = re.search(rf"{cvar}\s+(\S+)", existing)

            if match:
                old_value = match.group(1)

                # Yeni icerikte maskelenmis mi kontrol et
                if "********" in new_content:
                    # Maskelenmis degeri eski degerle degistir
                    pattern = rf'({cvar}\s+)"?\*+\"?'
                    new_content = re.sub(pattern, rf'\1"{old_value}"', new_content)

        return new_content

    def read_mapcycle(self, server: GameServer) -> Tuple[Optional[List[str]], str]:
        """
        mapcycle.txt oku

        Returns:
            (harita_listesi, mesaj)
        """
        config_path = self.get_config_path(server, "mapcycle.txt")

        if not config_path.exists():
            return None, "mapcycle.txt bulunamadi"

        try:
            with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            maps = []
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("//"):
                    maps.append(line)

            return maps, "OK"

        except Exception as e:
            logger.error(f"Mapcycle okuma hatasi: {e}")
            return None, str(e)

    def write_mapcycle(self, server: GameServer, maps: List[str], user_id: int) -> Tuple[bool, str]:
        """
        mapcycle.txt yaz

        Args:
            server: GameServer instance
            maps: Harita listesi
            user_id: Islemi yapan kullanici

        Returns:
            (basari, mesaj)
        """
        config_path = self.get_config_path(server, "mapcycle.txt")

        try:
            # Harita adlarini dogrula
            valid_maps = []
            for map_name in maps:
                map_name = map_name.strip()
                if map_name and re.match(r"^[a-zA-Z0-9_-]+$", map_name):
                    valid_maps.append(map_name)

            if not valid_maps:
                return False, "Gecerli harita bulunamadi"

            # Yedek al
            if config_path.exists():
                backup_path = config_path.with_suffix(
                    f'.backup.{datetime.now().strftime("%Y%m%d%H%M%S")}'
                )
                config_path.rename(backup_path)

            # Yaz
            content = "\n".join(valid_maps)
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Mapcycle yazildi: {config_path} (user: {user_id})")
            return True, "Basarili"

        except Exception as e:
            logger.error(f"Mapcycle yazma hatasi: {e}")
            return False, str(e)

    def read_motd(self, server: GameServer) -> Tuple[Optional[str], str]:
        """
        motd.txt oku

        Returns:
            (icerik, mesaj)
        """
        config_path = self.get_config_path(server, "motd.txt")

        if not config_path.exists():
            return None, "motd.txt bulunamadi"

        try:
            with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            return content, "OK"

        except Exception as e:
            logger.error(f"MOTD okuma hatasi: {e}")
            return None, str(e)

    def write_motd(self, server: GameServer, content: str, user_id: int) -> Tuple[bool, str]:
        """
        motd.txt yaz

        Args:
            server: GameServer instance
            content: MOTD icerigi (HTML)
            user_id: Islemi yapan kullanici

        Returns:
            (basari, mesaj)
        """
        config_path = self.get_config_path(server, "motd.txt")

        try:
            # Basit HTML sanitize (script taglarini kaldir)
            content = re.sub(
                r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE
            )
            content = re.sub(
                r"<iframe[^>]*>.*?</iframe>", "", content, flags=re.DOTALL | re.IGNORECASE
            )
            content = re.sub(r"on\w+\s*=", "", content, flags=re.IGNORECASE)

            # Yedek al
            if config_path.exists():
                backup_path = config_path.with_suffix(
                    f'.backup.{datetime.now().strftime("%Y%m%d%H%M%S")}'
                )
                config_path.rename(backup_path)

            # Yaz
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"MOTD yazildi: {config_path} (user: {user_id})")
            return True, "Basarili"

        except Exception as e:
            logger.error(f"MOTD yazma hatasi: {e}")
            return False, str(e)

    def get_available_maps(self, server: GameServer) -> List[str]:
        """
        Mevcut haritalari listele

        Returns:
            Harita listesi
        """
        server_path = self.get_server_path(server.id)
        mod_folder = self.get_mod_folder(server)
        maps_path = server_path / mod_folder / "maps"

        if not maps_path.exists():
            return []

        maps = []
        for file in maps_path.glob("*.bsp"):
            maps.append(file.stem)

        return sorted(maps)

    def get_cvar(self, server: GameServer, cvar_name: str) -> Tuple[Optional[str], str]:
        """
        Belirli bir cvar degerini oku

        Args:
            server: GameServer instance
            cvar_name: Cvar adi

        Returns:
            (deger, mesaj)
        """
        content, msg = self.read_config(server, "server.cfg")
        if content is None:
            return None, msg

        # Cvar'i bul
        match = re.search(rf'{cvar_name}\s+"([^"]*)"', content, re.IGNORECASE)
        if not match:
            match = re.search(rf"{cvar_name}\s+(\S+)", content, re.IGNORECASE)

        if match:
            return match.group(1), "OK"

        return None, "Cvar bulunamadi"

    def set_cvar(
        self, server: GameServer, cvar_name: str, value: str, user_id: int
    ) -> Tuple[bool, str]:
        """
        Belirli bir cvar degerini ayarla

        Args:
            server: GameServer instance
            cvar_name: Cvar adi
            value: Yeni deger
            user_id: Islemi yapan kullanici

        Returns:
            (basari, mesaj)
        """
        # Kilitli cvar kontrolu
        if cvar_name.lower() in [k.lower() for k in self.LOCKED_CVARS.keys()]:
            return False, f"Bu cvar kilitli ve degistirilemez: {cvar_name}"

        config_path = self.get_config_path(server, "server.cfg")
        content = self._read_raw_config(config_path)

        # Cvar guncelle veya ekle
        pattern = rf"^(\s*{cvar_name}\s+).*$"
        replacement = f'{cvar_name} "{value}"'

        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)
        else:
            content += f"\n{replacement}"

        # Yaz
        return self.write_config(server, "server.cfg", content, user_id)

    def get_locked_cvars(self) -> Dict[str, str]:
        """Kilitli cvar'lari dondur"""
        return self.LOCKED_CVARS.copy()

    def get_editable_files(self) -> List[str]:
        """Duzenlenebilir dosya listesini dondur"""
        return self.EDITABLE_CONFIGS.copy()

    def restore_backup(
        self, server: GameServer, filename: str, backup_name: str
    ) -> Tuple[bool, str]:
        """
        Yedekten geri yukle

        Args:
            server: GameServer instance
            filename: Orijinal dosya adi
            backup_name: Yedek dosya adi

        Returns:
            (basari, mesaj)
        """
        config_path = self.get_config_path(server, filename)
        backup_path = config_path.parent / backup_name

        if not backup_path.exists():
            return False, "Yedek dosya bulunamadi"

        try:
            # Mevcut dosyayi sil
            if config_path.exists():
                config_path.unlink()

            # Yedegi geri yukle
            backup_path.rename(config_path)

            logger.info(f"Yedek geri yuklendi: {backup_path} -> {config_path}")
            return True, "Basarili"

        except Exception as e:
            logger.error(f"Yedek geri yukleme hatasi: {e}")
            return False, str(e)

    def list_backups(self, server: GameServer, filename: str) -> List[Dict]:
        """
        Yedek dosyalari listele

        Args:
            server: GameServer instance
            filename: Orijinal dosya adi

        Returns:
            Yedek listesi
        """
        config_path = self.get_config_path(server, filename)
        backups = []

        for backup in config_path.parent.glob(f"{filename}.backup.*"):
            stat = backup.stat()
            backups.append(
                {
                    "name": backup.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

        return sorted(backups, key=lambda x: x["created"], reverse=True)
