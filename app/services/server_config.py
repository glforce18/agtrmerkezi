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
            logger.error(f"mapcycle okuma hatasi: {e}")
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
            # Yedek al
            if config_path.exists():
                backup_path = config_path.with_suffix(
                    f'.backup.{datetime.now().strftime("%Y%m%d%H%M%S")}'
                )
                config_path.rename(backup_path)

            # Yaz
            content = "\n".join(maps) + "\n"
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"mapcycle yazildi: {config_path} (user: {user_id})")
            return True, "Basarili"

        except Exception as e:
            logger.error(f"mapcycle yazma hatasi: {e}")
            return False, str(e)

    def get_available_maps(self, server: GameServer) -> List[str]:
        """
        Mevcut harita listesini al

        Returns:
            Harita listesi
        """
        server_path = self.get_server_path(server.id)
        mod_folder = self.get_mod_folder(server)
        maps_path = server_path / mod_folder / "maps"

        if not maps_path.exists():
            return []

        maps = []
        for bsp in maps_path.glob("*.bsp"):
            maps.append(bsp.stem)

        return sorted(maps)

    def validate_config(self, content: str) -> Tuple[bool, str]:
        """
        Config icerigini dogrula

        Returns:
            (gecerli, mesaj)
        """
        # Tehlikeli komutlari kontrol et
        dangerous = ["exec", "alias", "bind", "unbind", "changelevel"]
        lines = content.split("\n")

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue

            for cmd in dangerous:
                if stripped.lower().startswith(cmd.lower()):
                    return False, f"Tehlikeli komut tespit edildi: {cmd}"

        return True, "Gecerli"

    def create_backup(self, server: GameServer, filename: str) -> Tuple[Optional[str], str]:
        """
        Config dosyasinin yedeğini al

        Args:
            server: GameServer instance
            filename: Dosya adi

        Returns:
            (backup_name, mesaj)
        """
        config_path = self.get_config_path(server, filename)

        if not config_path.exists():
            return None, "Dosya bulunamadi"

        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_name = f"{filename}.backup.{timestamp}"
            backup_path = config_path.parent / backup_name

            # Kopyala
            with open(config_path, "rb") as src:
                with open(backup_path, "wb") as dst:
                    dst.write(src.read())

            logger.info(f"Yedek olusturuldu: {backup_path}")
            return backup_name, "Basarili"

        except Exception as e:
            logger.error(f"Yedek olusturma hatasi: {e}")
            return None, str(e)

    def restore_backup(
        self, server: GameServer, filename: str, backup_name: str
    ) -> Tuple[bool, str]:
        """
        Yedegi geri yukle

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

    def parse_visual_config(self, server: GameServer) -> Dict:
        """
        server.cfg'den görsel düzenleyici için güvenli ayarları parse et

        Returns:
            Düzenlenebilir ayarlar dict'i
        """
        config_path = self.get_config_path(server, "server.cfg")

        # Varsayılan değerler (Minimal)
        defaults = {
            # Sunucu Bilgileri
            "hostname": "",
            "sv_contact": "",
            # Güvenlik
            "rcon_password": "********",
            "sv_password": "",
            # Sunucu
            "sv_allowdownload": 1,
            # AG Mod - Temel
            "sv_ag_gamemode": "tdm",
            "sv_ag_start_health": 100,
            "sv_ag_start_armour": 0,
            "sv_ag_start_longjump": 0,
            "sv_ag_start_minplayers": 2,
            # AG Mod - Oylama
            "sv_ag_allow_vote": 1,
            "sv_ag_vote_gamemode": 1,
            "sv_ag_vote_map": 1,
        }

        if not config_path.exists():
            return defaults

        try:
            content = self._read_raw_config(config_path)
            parsed = {}

            for line in content.split("\n"):
                line = line.strip()

                # Yorum veya boş satır
                if not line or line.startswith("//") or line.startswith("#"):
                    continue

                # Cvar parse et
                match = re.match(r'^(\w+)\s+"?([^"\n]*)"?', line)
                if match:
                    cvar = match.group(1).lower()
                    value = match.group(2).strip('"')

                    # Sadece safe cvarlara bak
                    if cvar in defaults:
                        # Sayısal değerler
                        if cvar in [
                            "sv_ag_start_health",
                            "sv_ag_start_armour",
                            "sv_ag_start_minplayers",
                        ]:
                            try:
                                parsed[cvar] = int(value)
                            except:
                                parsed[cvar] = defaults[cvar]
                        # Boolean değerler (0/1)
                        elif cvar in [
                            "sv_allowdownload",
                            "sv_ag_start_longjump",
                            "sv_ag_allow_vote",
                            "sv_ag_vote_gamemode",
                            "sv_ag_vote_map",
                        ]:
                            parsed[cvar] = 1 if value in ["1", "true", "yes"] else 0
                        # String değerler (hostname, sv_contact, sv_password, sv_ag_gamemode)
                        else:
                            parsed[cvar] = value

            # Varsayılanlarla birleştir
            result = defaults.copy()
            result.update(parsed)

            return result

        except Exception as e:
            logger.error(f"Visual config parse hatası: {e}")
            return defaults

    def update_visual_config(
        self, server: GameServer, values: Dict, user_id: int
    ) -> Tuple[bool, str]:
        """
        Görsel düzenleyiciden gelen değerleri server.cfg'ye yaz

        Args:
            server: GameServer instance
            values: Yeni değerler dict'i
            user_id: İşlemi yapan kullanıcı

        Returns:
            (başarı, mesaj)
        """
        config_path = self.get_config_path(server, "server.cfg")

        if not config_path.exists():
            return False, "server.cfg bulunamadı"

        try:
            # Mevcut içeriği oku
            existing_content = self._read_raw_config(config_path)
            lines = existing_content.split("\n")

            # Güncellenmiş satırlar
            result_lines = []
            updated_cvars = set()

            for line in lines:
                stripped = line.strip()

                # Yorum veya boş satır - koru
                if not stripped or stripped.startswith("//") or stripped.startswith("#"):
                    result_lines.append(line)
                    continue

                # Cvar satırı parse et
                match = re.match(r"^(\w+)\s+", stripped)
                if match:
                    cvar = match.group(1).lower()

                    # Güncellenecek cvar mı?
                    if cvar in values:
                        value = values[cvar]

                        # Değer formatla
                        if isinstance(value, bool):
                            value = "1" if value else "0"
                        elif isinstance(value, (int, float)):
                            value = str(value)

                        result_lines.append(f'{cvar} "{value}"')
                        updated_cvars.add(cvar)
                    else:
                        # Değiştirilmeyecek - koru
                        result_lines.append(line)
                else:
                    result_lines.append(line)

            # Eksik cvarlari ekle
            for cvar, value in values.items():
                if cvar not in updated_cvars:
                    if isinstance(value, bool):
                        value = "1" if value else "0"
                    elif isinstance(value, (int, float)):
                        value = str(value)

                    result_lines.append(f'{cvar} "{value}"')

            # Yeni içerik
            new_content = "\n".join(result_lines)

            # Kilitli değerleri koru
            new_content = self._protect_locked_values(new_content)

            # Hassas değerleri koru
            new_content = self._preserve_sensitive_values(existing_content, new_content)

            # Yedek al
            backup_path = config_path.with_suffix(
                f'.backup.{datetime.now().strftime("%Y%m%d%H%M%S")}'
            )
            config_path.rename(backup_path)

            # Yaz
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.info(f"Visual config güncellendi: {config_path} (user: {user_id})")
            return True, "Ayarlar kaydedildi"

        except Exception as e:
            logger.error(f"Visual config güncelleme hatası: {e}")
            return False, str(e)
