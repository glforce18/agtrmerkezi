"""
AGTR Merkezi v6.0 - AMXModX Admin Service
users.ini yonetimi ve admin islemleri
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.database import AdminAuthType, GameServer, ServerAdminEntry

logger = logging.getLogger(__name__)


class AMXXAdminService:
    """
    AMXModX Admin Yonetim Servisi

    users.ini dosyasi okuma/yazma ve admin CRUD islemleri
    """

    SERVERS_BASE = "/home/gameservers/servers"

    # Varsayilan admin flaglari
    DEFAULT_FLAGS = "abcdefghijklmnopqrstu"  # Tam yetki

    # Flag aciklamalari
    FLAG_DESCRIPTIONS = {
        "a": "immunity",
        "b": "reservation",
        "c": "kick",
        "d": "ban",
        "e": "slay",
        "f": "changelevel",
        "g": "cvars",
        "h": "config",
        "i": "chat",
        "j": "vote",
        "k": "password",
        "l": "rcon",
        "m": "level1",
        "n": "level2",
        "o": "level3",
        "p": "level4",
        "q": "level5",
        "r": "level6",
        "s": "level7",
        "t": "level8",
        "u": "menu access",
        "z": "user (non-admin)",
    }

    # Mod klasor adlari
    MOD_FOLDERS = {
        "ag": "ag",
        "ag_openag": "ag",
        "cs16": "cstrike",
        "hldm": "valve",
        "valve_new": "valve",
    }

    def __init__(self, db: Session):
        self.db = db

    def get_server_path(self, server_id: int) -> Path:
        """Sunucu dizin yolunu al"""
        return Path(self.SERVERS_BASE) / f"server_{server_id}"

    def get_mod_folder(self, server: GameServer) -> str:
        """Mod klasor adini al"""
        return self.MOD_FOLDERS.get(server.mod_type, "valve")

    def get_users_ini_path(self, server: GameServer) -> Path:
        """users.ini dosya yolunu al"""
        server_path = self.get_server_path(server.id)
        mod_folder = self.get_mod_folder(server)
        return server_path / mod_folder / "addons" / "amxmodx" / "configs" / "users.ini"

    def read_users_ini(self, server: GameServer) -> List[Dict]:
        """
        users.ini dosyasini oku

        Returns:
            [{"auth": str, "password": str, "flags": str, "access_flags": str}]
        """
        users_ini_path = self.get_users_ini_path(server)

        if not users_ini_path.exists():
            return []

        admins = []

        try:
            with open(users_ini_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()

                    # Yorum veya bos satir atla
                    if not line or line.startswith(";"):
                        continue

                    # Format: "auth" "password" "flags" "access_flags"
                    match = re.match(r'"([^"]+)"\s+"([^"]*)"\s+"([^"]*)"\s+"([^"]*)"', line)

                    if match:
                        admins.append(
                            {
                                "auth": match.group(1),
                                "password": match.group(2),
                                "flags": match.group(3),
                                "access_flags": match.group(4),
                            }
                        )

            return admins

        except Exception as e:
            logger.error(f"users.ini okuma hatasi: {e}")
            return []

    def write_users_ini(self, server: GameServer, admins: List[Dict]) -> Tuple[bool, str]:
        """
        users.ini dosyasini yaz

        Args:
            server: GameServer instance
            admins: Admin listesi [{"auth": str, "password": str, "flags": str, "access_flags": str}]

        Returns:
            (basari, mesaj)
        """
        users_ini_path = self.get_users_ini_path(server)

        try:
            # Dizin yoksa olustur
            users_ini_path.parent.mkdir(parents=True, exist_ok=True)

            lines = [
                "; AGTR Merkezi - Auto-generated Admin List",
                f"; Server ID: {server.id}",
                f"; Server Code: {server.unique_code}",
                f"; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ";",
                '; Format: "auth" "password" "access" "flags"',
                ";",
                "; Access flags:",
                ";   a - immunity",
                ";   b - reservation",
                ";   c - kick",
                ";   d - ban",
                ";   e - slay/slap",
                ";   f - changelevel",
                ";   g - cvars",
                ";   h - config",
                ";   i - chat",
                ";   j - vote",
                ";   k - password",
                ";   l - rcon",
                ";   m-t - custom levels",
                ";   u - menu access",
                ";   z - user (non-admin)",
                ";",
                "; Auth flags:",
                ";   a - name",
                ";   b - ip",
                ";   c - steam",
                ";   d - name from file",
                ";   e - steam from file",
                ";",
                "",
            ]

            for admin in admins:
                auth = admin.get("auth", "")
                password = admin.get("password", "")
                flags = admin.get("flags", self.DEFAULT_FLAGS)
                access_flags = admin.get("access_flags", "ce")  # steam + name from file

                lines.append(f'"{auth}" "{password}" "{flags}" "{access_flags}"')

            with open(users_ini_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            logger.info(f"users.ini yazildi: {users_ini_path}")
            return True, "Basarili"

        except Exception as e:
            logger.error(f"users.ini yazma hatasi: {e}")
            return False, str(e)

    def add_admin(
        self,
        server_id: int,
        steam_id: str,
        name: Optional[str] = None,
        flags: str = None,
        password: Optional[str] = None,
        auth_type: AdminAuthType = AdminAuthType.STEAM,
        added_by: int = None,
        expires_at: datetime = None,
        notes: str = None,
    ) -> Tuple[Optional[ServerAdminEntry], str]:
        """
        Yeni admin ekle

        Args:
            server_id: Sunucu ID
            steam_id: Steam ID
            name: Admin adi
            flags: Yetki flaglari
            password: Sifre (opsiyonel)
            auth_type: Dogrulama tipi
            added_by: Ekleyen kullanici ID
            expires_at: Son kullanma tarihi
            notes: Notlar

        Returns:
            (ServerAdminEntry, mesaj)
        """
        # Steam ID validasyonu
        if not steam_id or not self._validate_steam_id(steam_id):
            return None, "Gecersiz Steam ID"

        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            return None, "Sunucu bulunamadi"

        # Mevcut kontrol
        existing = (
            self.db.query(ServerAdminEntry)
            .filter(ServerAdminEntry.server_id == server_id, ServerAdminEntry.steam_id == steam_id)
            .first()
        )

        if existing:
            return None, "Bu Steam ID zaten admin olarak kayitli"

        # Yeni admin
        admin = ServerAdminEntry(
            server_id=server_id,
            steam_id=steam_id,
            name=name,
            flags=flags or self.DEFAULT_FLAGS,
            password=password,
            access_level=0,
            auth_type=auth_type,
            added_by=added_by,
            expires_at=expires_at,
            is_active=True,
            notes=notes,
            created_at=datetime.utcnow(),
        )

        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)

        # users.ini guncelle
        self._sync_admins_to_file(server)

        logger.info(f"Admin eklendi: {steam_id} -> Server {server_id}")
        return admin, "Admin basariyla eklendi"

    def add_owner_as_admin(self, server_id: int, owner_id: int) -> Tuple[bool, str]:
        """
        Sunucu sahibini otomatik olarak admin olarak ekle

        Args:
            server_id: Sunucu ID
            owner_id: Sahip kullanici ID

        Returns:
            (basari, mesaj)
        """
        from app.models.database import User

        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            return False, "Sunucu bulunamadi"

        user = self.db.query(User).filter(User.id == owner_id).first()
        if not user or not user.steam_id:
            return False, "Kullanici veya Steam ID bulunamadi"

        # Zaten admin mi kontrol et
        existing = (
            self.db.query(ServerAdminEntry)
            .filter(
                ServerAdminEntry.server_id == server_id, ServerAdminEntry.steam_id == user.steam_id
            )
            .first()
        )

        if existing:
            return True, "Sahip zaten admin yetkisine sahip"

        # Tam yetki ile admin ekle
        admin_entry = ServerAdminEntry(
            server_id=server_id,
            steam_id=user.steam_id,
            name=user.username if hasattr(user, "username") else None,
            flags=self.DEFAULT_FLAGS,  # Tam yetki
            auth_type=AdminAuthType.STEAM,
            added_by=owner_id,
            is_active=True,
            notes="Otomatik sahip admin",
            created_at=datetime.utcnow(),
        )
        self.db.add(admin_entry)
        self.db.commit()

        # users.ini guncelle
        self._sync_admins_to_file(server)

        logger.info(f"Sahip admin olarak eklendi: {user.steam_id} -> Server {server_id}")
        return True, "Sahip otomatik olarak admin eklendi"

    def update_admin(
        self,
        admin_id: int,
        flags: str = None,
        password: str = None,
        is_active: bool = None,
        expires_at: datetime = None,
        notes: str = None,
    ) -> Tuple[bool, str]:
        """
        Admin bilgilerini guncelle

        Args:
            admin_id: Admin ID
            flags: Yeni flaglar
            password: Yeni sifre
            is_active: Aktiflik durumu
            expires_at: Son kullanma tarihi
            notes: Notlar

        Returns:
            (basari, mesaj)
        """
        admin = self.db.query(ServerAdminEntry).filter(ServerAdminEntry.id == admin_id).first()

        if not admin:
            return False, "Admin bulunamadi"

        if flags is not None:
            admin.flags = flags
        if password is not None:
            admin.password = password
        if is_active is not None:
            admin.is_active = is_active
        if expires_at is not None:
            admin.expires_at = expires_at
        if notes is not None:
            admin.notes = notes

        admin.updated_at = datetime.utcnow()
        self.db.commit()

        # users.ini guncelle
        server = self.db.query(GameServer).filter(GameServer.id == admin.server_id).first()
        if server:
            self._sync_admins_to_file(server)

        return True, "Admin guncellendi"

    def remove_admin(self, admin_id: int) -> Tuple[bool, str]:
        """
        Admin sil

        Args:
            admin_id: Admin ID

        Returns:
            (basari, mesaj)
        """
        admin = self.db.query(ServerAdminEntry).filter(ServerAdminEntry.id == admin_id).first()

        if not admin:
            return False, "Admin bulunamadi"

        server_id = admin.server_id

        self.db.delete(admin)
        self.db.commit()

        # users.ini guncelle
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if server:
            self._sync_admins_to_file(server)

        logger.info(f"Admin silindi: {admin_id}")
        return True, "Admin silindi"

    def get_admins(self, server_id: int, include_inactive: bool = False) -> List[Dict]:
        """
        Sunucu adminlerini listele

        Args:
            server_id: Sunucu ID
            include_inactive: Pasif adminleri dahil et

        Returns:
            Admin listesi
        """
        query = self.db.query(ServerAdminEntry).filter(ServerAdminEntry.server_id == server_id)

        if not include_inactive:
            query = query.filter(ServerAdminEntry.is_active == True)

        admins = query.order_by(ServerAdminEntry.created_at.desc()).all()

        return [
            {
                "id": a.id,
                "steam_id": a.steam_id,
                "name": a.name,
                "flags": a.flags,
                "has_password": bool(a.password),
                "access_level": a.access_level,
                "auth_type": a.auth_type.value if a.auth_type else None,
                "is_active": a.is_active,
                "expires_at": a.expires_at.isoformat() if a.expires_at else None,
                "notes": a.notes,
                "added_by": a.added_by,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "updated_at": a.updated_at.isoformat() if a.updated_at else None,
            }
            for a in admins
        ]

    def _sync_admins_to_file(self, server: GameServer) -> Tuple[bool, str]:
        """
        Veritabani adminlerini users.ini'ye senkronize et

        Args:
            server: GameServer instance

        Returns:
            (basari, mesaj)
        """
        # Aktif adminleri al
        admins = (
            self.db.query(ServerAdminEntry)
            .filter(ServerAdminEntry.server_id == server.id, ServerAdminEntry.is_active == True)
            .all()
        )

        # Suresi dolanlari filtrele
        now = datetime.utcnow()
        active_admins = []

        for admin in admins:
            if admin.expires_at and admin.expires_at < now:
                # Suresi dolmus, pasif yap
                admin.is_active = False
                continue

            access_flags = "ce"  # steam + name from file
            if admin.auth_type == AdminAuthType.IP:
                access_flags = "b"  # ip
            elif admin.auth_type == AdminAuthType.NAME:
                access_flags = "a"  # name

            active_admins.append(
                {
                    "auth": admin.steam_id,
                    "password": admin.password or "",
                    "flags": admin.flags or self.DEFAULT_FLAGS,
                    "access_flags": access_flags,
                }
            )

        self.db.commit()

        return self.write_users_ini(server, active_admins)

    def sync_to_server(self, server: GameServer, rcon_service=None) -> Tuple[bool, str]:
        """
        Adminleri sunucuya senkronize et (amx_reloadadmins)

        Args:
            server: GameServer instance
            rcon_service: RCONService instance (opsiyonel)

        Returns:
            (basari, mesaj)
        """
        # Once dosyayi guncelle
        success, msg = self._sync_admins_to_file(server)
        if not success:
            return False, msg

        # RCON ile reload komutu gonder
        if rcon_service:
            try:
                import asyncio

                result = asyncio.get_event_loop().run_until_complete(
                    rcon_service.execute(server, "amx_reloadadmins", 0)
                )
                if result["success"]:
                    return True, "Adminler senkronize edildi ve yuklendi"
                else:
                    return True, "Adminler dosyaya yazildi, sunucu yukleme hatasi"
            except Exception as e:
                logger.warning(f"RCON reload hatasi: {e}")
                return True, "Adminler dosyaya yazildi, sunucu reload yapilamadi"

        return True, "Adminler dosyaya yazildi"

    def _validate_steam_id(self, steam_id: str) -> bool:
        """Steam ID validasyonu"""
        # STEAM_0:0:12345 veya STEAM_0:1:12345
        steam_pattern = r"^STEAM_[0-9]:[0-9]:\d+$"

        # Steam64 ID
        steam64_pattern = r"^\d{17}$"

        return bool(re.match(steam_pattern, steam_id) or re.match(steam64_pattern, steam_id))

    def get_flag_descriptions(self) -> Dict[str, str]:
        """Flag aciklamalarini dondur"""
        return self.FLAG_DESCRIPTIONS.copy()

    def check_expired_admins(self) -> int:
        """
        Suresi dolan adminleri kontrol et ve pasif yap

        Returns:
            Pasif yapilan admin sayisi
        """
        now = datetime.utcnow()

        expired = (
            self.db.query(ServerAdminEntry)
            .filter(
                ServerAdminEntry.is_active == True,
                ServerAdminEntry.expires_at != None,
                ServerAdminEntry.expires_at < now,
            )
            .all()
        )

        count = 0
        server_ids = set()

        for admin in expired:
            admin.is_active = False
            server_ids.add(admin.server_id)
            count += 1

        self.db.commit()

        # Etkilenen sunucularin users.ini'sini guncelle
        for server_id in server_ids:
            server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
            if server:
                self._sync_admins_to_file(server)

        if count > 0:
            logger.info(f"Suresi dolan {count} admin pasif yapildi")

        return count
