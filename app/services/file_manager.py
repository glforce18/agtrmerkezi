"""
AGTR Merkezi v6.0 - File Manager Service
Guvenli dosya yonetimi servisi - KISITLI ERISIM
"""

import logging
import os
import shutil
import stat
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, List

from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

SERVERS_BASE = "/home/gameservers/servers"

# Mod type to directory mapping
MOD_DIRECTORIES = {
    "hldm": "valve",
    "ag": "ag",
    "ag_openag": "ag",
    "cs16": "cstrike",
    "cstrike": "cstrike",
    "tfc": "tfc",
    "dmc": "dmc",
    "ricochet": "ricochet",
    "dod": "dod",
    "valve": "valve",  # Generic Half-Life
}

# KORUNMALI DIZINLER - Erisim yasak
PROTECTED_DIRECTORIES = [
    "addons/amxmodx/plugins",  # Default AMXModX pluginleri
    "addons/metamod/dlls",  # Metamod core files
    "dlls",  # Game DLL files
    "cl_dlls",  # Client DLL files
]

# KORUNMALI DOSYALAR - Silinemez/duzenlenemez
PROTECTED_FILES = [
    "hlds_linux",
    "hlds_run",
    "steamclient.so",
    "steam_appid.txt",
    "libsteam.so",
]

# DUZENLENEBILIR DOSYALAR - SADECE BU DOSYA DUZENLENEBILIR
EDITABLE_FILES = {
    "server.cfg",  # Sadece server.cfg duzenlenebilir
}

# SADECE OKUNABILIR UZANTILAR - Bakılabilir ama duzenlenemez
READABLE_EXTENSIONS = {
    ".log",  # Log files (sadece görüntüleme)
}

# ==================== WEBFTP UPLOAD CONFIGURATION ====================

# Allowed upload file extensions (whitelist)
ALLOWED_UPLOAD_EXTENSIONS = {
    # Config files
    ".cfg",
    ".ini",
    ".rc",
    # Map files
    ".bsp",
    ".nav",
    ".res",
    ".txt",
    # Sound files
    ".wav",
    ".mp3",
    # Model files
    ".mdl",
    ".spr",
    # Image files
    ".tga",
    ".bmp",
    # Plugin files
    ".amxx",
    ".sma",
}

# Max upload size per file type (bytes)
MAX_UPLOAD_SIZES = {
    "text": 1 * 1024 * 1024,  # 1MB for configs
    "audio": 10 * 1024 * 1024,  # 10MB for sounds
    "model": 5 * 1024 * 1024,  # 5MB for models
    "map": 50 * 1024 * 1024,  # 50MB for maps
    "image": 2 * 1024 * 1024,  # 2MB for images
    "plugin": 5 * 1024 * 1024,  # 5MB for plugins
}

# Upload target directories (whitelist) - DYNAMIC BASED ON MOD
# Format: {mod_dir}/{subdir}
ALLOWED_UPLOAD_DIRECTORIES = {
    # Counter-Strike 1.6
    "cstrike/maps",
    "cstrike/sound",
    "cstrike/models",
    "cstrike/sprites",
    "cstrike/gfx",
    "cstrike",
    "cstrike/addons/amxmodx/configs",
    # Half-Life / Valve
    "valve/maps",
    "valve/sound",
    "valve/models",
    "valve/sprites",
    "valve/gfx",
    "valve",
    "valve/addons/amxmodx/configs",
    # Adrenaline Gamer
    "ag/maps",
    "ag/sound",
    "ag/models",
    "ag/sprites",
    "ag/gfx",
    "ag",
    "ag/addons/amxmodx/configs",
    # Team Fortress Classic
    "tfc/maps",
    "tfc/sound",
    "tfc/models",
    "tfc/sprites",
    "tfc/gfx",
    "tfc",
    "tfc/addons/amxmodx/configs",
}

# GIZLI DOSYA UZANTILARI - Bu dosyalar dosya yöneticisinde görünmez
HIDDEN_FILE_EXTENSIONS = {
    ".vdf",  # Valve Data File (Steam/game config)
    ".dat",  # Binary data files
    ".txt",  # Text files (not editable)
    ".dem",  # Demo files
    ".scr",  # Script files
    ".rc",  # Resource files
    ".md",  # Markdown files
    ".db",  # Database files
    ".sqlite",  # SQLite database
}

# SERVER.CFG KRITIK KOMUTLAR - Bu komutlar degistirilemez
PROTECTED_SERVER_CFG_COMMANDS = {
    # Performans kritik
    "sys_ticrate",
    "sys_tickrate",  # Alternatif yazılış
    "fps_max",
    "fps_override",
    # Network kritik
    "sv_maxrate",
    "sv_minrate",
    "sv_maxupdaterate",
    "sv_minupdaterate",
    "sv_maxcmdrate",
    "sv_mincmdrate",
    "rate",
    "sv_fastdownloadurl",
    # Sunucu altyapı
    "ip",
    "port",
    "maxplayers",
    "sv_region",
    # Güvenlik
    "sv_cheats",
    "sv_lan",
    "sv_secure",
    # Sistem
    "exec",
    "alias",
    "bind",
    "unbind",
}

# SERVER.CFG GORSEL AYARLANABILIR KOMUTLAR - Half-Life Sunucusu (Minimal)
VISUAL_EDITABLE_COMMANDS = {
    # Sunucu Bilgileri
    "hostname",
    "sv_contact",
    # Güvenlik
    "rcon_password",
    "sv_password",
    # Sunucu Ayarları
    "sv_allowdownload",
    # AG Mod - Temel Ayarlar
    "sv_ag_gamemode",
    "sv_ag_start_health",
    "sv_ag_start_armour",
    "sv_ag_start_longjump",
    "sv_ag_start_minplayers",
    # AG Mod - Oylama
    "sv_ag_allow_vote",
    "sv_ag_vote_gamemode",
    "sv_ag_vote_map",
}


class FileManagerService:
    """
    Dosya yonetim servisi - KISITLI ERISIM

    Güvenlik kuralları:
    - Default AMXModX pluginlere erisim yok
    - Sadece belirli dosya tipleri duzenlenebilir
    - Silme islemi tamamen devre disi
    - Path traversal koruması
    """

    def get_mod_directory(self, db: Session, server_id: int) -> str:
        """
        Get the mod directory for a server based on its mod_type

        Args:
            db: Database session
            server_id: Server ID

        Returns:
            Mod directory name (e.g., 'valve', 'cstrike', 'ag')
        """
        from app.models.database import GameServer

        server = db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            raise HTTPException(404, "Server not found")

        mod_type = server.mod_type
        if not mod_type:
            # Fallback to cstrike if no mod_type set
            return "cstrike"

        # Map mod_type to directory
        return MOD_DIRECTORIES.get(mod_type.lower(), "cstrike")

    def validate_path(
        self, server_id: int, requested_path: str, allow_protected: bool = False
    ) -> Path:
        """
        Path dogrulama ve traversal koruması

        Args:
            server_id: Sunucu ID
            requested_path: Istenen path
            allow_protected: Korunmali dizinlere erisime izin ver (default: False)

        Returns:
            Guvenli path

        Raises:
            HTTPException: Gecersiz path
        """
        server_root = Path(SERVERS_BASE) / f"server_{server_id}"

        if not server_root.exists():
            raise HTTPException(404, "Server directory not found")

        # Relative path normalize
        if requested_path.startswith("/"):
            requested_path = requested_path[1:]

        full_path = (server_root / requested_path).resolve()

        # Guvenlik: path sunucu dizini icinde mi kontrol et
        if not str(full_path).startswith(str(server_root.resolve())):
            raise HTTPException(403, "Path traversal attempt blocked")

        # Korunmali dizin kontrolu
        if not allow_protected:
            relative_path = str(full_path.relative_to(server_root))

            # cstrike/ prefix'ini kaldir
            if relative_path.startswith("cstrike/"):
                check_path = relative_path[8:]  # "cstrike/" = 8 karakter
            else:
                check_path = relative_path

            for protected_dir in PROTECTED_DIRECTORIES:
                if check_path.startswith(protected_dir):
                    raise HTTPException(
                        403,
                        f"Erisim yasak: {protected_dir} dizini korunmaktadir. "
                        "Default pluginler ve sistem dosyalari degistirilemez.",
                    )

        return full_path

    def _is_protected_file(self, file_path: Path) -> bool:
        """Dosya korunmali mi kontrol et"""
        filename = file_path.name
        return filename in PROTECTED_FILES

    def _can_edit_file(self, file_path: Path) -> bool:
        """Dosya duzenlenebilir mi kontrol et - SADECE server.cfg"""
        filename = file_path.name
        return filename in EDITABLE_FILES

    def _can_read_file(self, file_path: Path) -> bool:
        """Dosya okunabilir mi kontrol et - Sadece server.cfg ve .log dosyalari"""
        filename = file_path.name
        extension = file_path.suffix.lower()

        # server.cfg her zaman okunabilir
        if filename in EDITABLE_FILES:
            return True

        # .log dosyalari okunabilir
        return extension in READABLE_EXTENSIONS

    def _filter_protected_commands(self, content: str) -> str:
        """
        server.cfg icinden korunmali komutlari filtrele (gizle)

        Kullanicinin goremeyecegi komutlar:
        - sys_ticrate, fps_max, sv_maxrate, sv_fastdownloadurl, vb.

        Args:
            content: Orijinal server.cfg icerigi

        Returns:
            Filtrelenmis icerik (korunmali komutlar yorum satirina cevrilir)
        """
        filtered_lines = []
        for line in content.splitlines():
            original_line = line.strip()

            # Bos satir veya yorum
            if not original_line or original_line.startswith("//") or original_line.startswith("#"):
                filtered_lines.append(line)
                continue

            # Command parsing
            parts = original_line.split(None, 1)
            if len(parts) >= 1:
                cmd = parts[0].lower()

                # Korunmali komut mu?
                if cmd in PROTECTED_SERVER_CFG_COMMANDS:
                    # Korunmali komutu yorum satirina cevir (gizle)
                    filtered_lines.append(f"// {line}  // [SISTEM KORUNMALI]")
                else:
                    # Normal komut, oldugu gibi birak
                    filtered_lines.append(line)
            else:
                filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _protect_critical_commands(self, server_id: int, file_path: Path, new_content: str) -> str:
        """
        server.cfg kritik komutlarini koru

        Kullanicinin degistirmeye calistigi kritik komutlari orijinal degerleriyle degistirir.

        Args:
            server_id: Sunucu ID
            file_path: server.cfg path
            new_content: Kullanicinin gonderdigi yeni icerik

        Returns:
            Korunmus icerik
        """
        # Orijinal dosyayi oku
        if not file_path.exists():
            return new_content

        try:
            original_content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return new_content

        # Orijinal icerikteki kritik komutlari parse et
        original_commands = {}
        for line in original_content.splitlines():
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue

            # Command parsing (basit regex)
            parts = line.split(None, 1)
            if len(parts) >= 1:
                cmd = parts[0].lower()
                if cmd in PROTECTED_SERVER_CFG_COMMANDS:
                    original_commands[cmd] = line

        # Yeni icerikteki kritik komutlari orijinal degerlerle degistir
        protected_lines = []
        for line in new_content.splitlines():
            original_line = line.strip()

            # Bos satir veya yorum
            if not original_line or original_line.startswith("//") or original_line.startswith("#"):
                protected_lines.append(line)
                continue

            # Command parsing
            parts = original_line.split(None, 1)
            if len(parts) >= 1:
                cmd = parts[0].lower()

                # Kritik komut mu?
                if cmd in PROTECTED_SERVER_CFG_COMMANDS:
                    # Orijinal degeri kullan
                    if cmd in original_commands:
                        protected_lines.append(
                            original_commands[cmd]
                            + "  // [KORUNMUS] Bu komut guvenlik nedeniyle degistirilemez"
                        )
                    else:
                        # Orijinalde yoksa, yorum satiri yap
                        protected_lines.append(
                            "// " + line + "  // [ENGELLENDI] Kritik komut degistirilemez"
                        )
                else:
                    # Normal komut, kullanici degerini kabul et
                    protected_lines.append(line)
            else:
                protected_lines.append(line)

        return "\n".join(protected_lines)

    def list_directory(self, server_id: int, path: str = "") -> Dict:
        """
        Dizin icerigini listele

        Args:
            server_id: Sunucu ID
            path: Dizin yolu

        Returns:
            Dosya ve dizin listesi
        """
        full_path = self.validate_path(server_id, path)

        if not full_path.is_dir():
            raise HTTPException(400, "Not a directory")

        items = []
        for item in sorted(full_path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
            # GUVENLIK: Gizli dosya uzantılarını atla
            if item.is_file() and item.suffix.lower() in HIDDEN_FILE_EXTENSIONS:
                continue

            # GUVENLIK: addons klasörünü tamamen gizle (plugin yöneticisinden yönetilecek)
            if item.is_dir() and item.name.lower() == "addons":
                continue

            stat = item.stat()
            items.append(
                {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "path": str(item.relative_to(Path(SERVERS_BASE) / f"server_{server_id}")),
                }
            )

        return {"current_path": path, "items": items}

    def read_file(self, server_id: int, file_path: str) -> Dict:
        """
        Dosya icerigini oku

        Args:
            server_id: Sunucu ID
            file_path: Dosya yolu

        Returns:
            Dosya icerigi ve metadata
        """
        full_path = self.validate_path(server_id, file_path)

        if not full_path.is_file():
            raise HTTPException(400, "Not a file")

        # GUVENLIK: Sadece izin verilen dosya tipleri okunabilir
        if not self._can_read_file(full_path):
            raise HTTPException(
                403,
                "Bu dosyaya erisim izniniz yok. Sadece server.cfg ve .log dosyalari goruntülenebilir.",
            )

        # Boyut kontrolu (5MB limit)
        if full_path.stat().st_size > 5 * 1024 * 1024:
            raise HTTPException(400, "File too large (max 5MB)")

        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            raise HTTPException(500, f"Failed to read file: {str(e)}")

        # GUVENLIK: server.cfg ise korunmali komutlari filtrele (gizle)
        if full_path.name == "server.cfg":
            content = self._filter_protected_commands(content)

        # Monaco Editor icin dil tespiti
        extension = full_path.suffix.lower()
        language_map = {
            ".cfg": "ini",
            ".ini": "ini",
            ".txt": "plaintext",
            ".log": "plaintext",
            ".sma": "cpp",
            ".inc": "cpp",
            ".json": "json",
            ".sh": "shell",
            ".bat": "bat",
            ".md": "markdown",
        }
        language = language_map.get(extension, "plaintext")

        # Dosya tipi belirleme
        can_edit = self._can_edit_file(full_path)
        is_readonly = extension in READABLE_EXTENSIONS and not can_edit

        return {
            "content": content,
            "language": language,
            "size": full_path.stat().st_size,
            "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat(),
            "can_edit": can_edit,  # server.cfg icin True, digerleri False
            "is_readonly": is_readonly,  # .log dosyalari icin True
        }

    def write_file(self, server_id: int, file_path: str, content: str, user_id: int) -> Dict:
        """
        Dosyaya yaz (yedekleme ile)

        Args:
            server_id: Sunucu ID
            file_path: Dosya yolu
            content: Icerik
            user_id: Kullanici ID

        Returns:
            Basari mesaji
        """
        full_path = self.validate_path(server_id, file_path)

        # GUVENLIK: Korunmus dosyalar duzenlenemez
        if self._is_protected_file(full_path):
            raise HTTPException(403, f"Bu dosya korunmaktadir ve duzenlenemez: {full_path.name}")

        # GUVENLIK: Sadece server.cfg duzenlenebilir
        if not self._can_edit_file(full_path):
            raise HTTPException(
                403, "Bu dosya duzenlenemez. Sadece server.cfg dosyasi duzenlenebilir."
            )

        # GUVENLIK: server.cfg ise kritik komutlari koru
        if full_path.name == "server.cfg":
            content = self._protect_critical_commands(server_id, full_path, content)

        # Mevcut dosyayi yedekle
        if full_path.exists():
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = full_path.with_suffix(f"{full_path.suffix}.backup.{timestamp}")
            shutil.copy2(full_path, backup_path)

        try:
            full_path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise HTTPException(500, f"Failed to write file: {str(e)}")

        logger.info(f"User {user_id} edited file: {file_path} on server {server_id}")

        return {"success": True, "message": "File saved successfully"}

    def upload_file(self, server_id: int, directory: str, file, user_id: int) -> Dict:
        """
        Dosya yukle - DEVRE DISI (Guvenlik)

        Args:
            server_id: Sunucu ID
            directory: Hedef dizin
            file: Upload dosyasi
            user_id: Kullanici ID

        Returns:
            Upload sonucu
        """
        # GUVENLIK: Dosya yukleme guvenlik nedeniyle devre disi birakildi
        # Kullanicilar sadece mevcut .cfg, .ini, .txt dosyalarini duzenleyebilir
        raise HTTPException(
            403,
            "Dosya yukleme guvenlik nedeniyle devre disi birakildi. "
            "Sadece mevcut config dosyalarini (.cfg, .ini, .txt) duzenleyebilirsiniz.",
        )

    def delete_file(self, server_id: int, file_path: str, user_id: int) -> Dict:
        """
        Dosya/dizin sil - DEVRE DISI (Guvenlik)

        Args:
            server_id: Sunucu ID
            file_path: Dosya yolu
            user_id: Kullanici ID

        Returns:
            Silme sonucu
        """
        # GUVENLIK: Dosya silme guvenlik nedeniyle tamamen devre disi birakildi
        # Yanlislikla onemli dosyalarin silinmesini onlemek icin
        raise HTTPException(
            403,
            "Dosya silme guvenlik nedeniyle devre disi birakildi. "
            "Onemli dosyalarin yanlislikla silinmesini onlemek icin bu ozellik kapatilmistir.",
        )

    def create_directory(
        self, server_id: int, parent_path: str, dir_name: str, user_id: int
    ) -> Dict:
        """
        Yeni dizin olustur - DEVRE DISI (Guvenlik)

        Args:
            server_id: Sunucu ID
            parent_path: Ust dizin
            dir_name: Yeni dizin adi
            user_id: Kullanici ID

        Returns:
            Olusturma sonucu
        """
        # GUVENLIK: Dizin olusturma guvenlik nedeniyle devre disi birakildi
        # Sunucu yapilandirmasinin bozulmasini onlemek icin
        raise HTTPException(
            403,
            "Dizin olusturma guvenlik nedeniyle devre disi birakildi. "
            "Sunucu yapilandirmasinin korunmasi icin bu ozellik kapatilmistir.",
        )

    # ==================== WEBFTP ENHANCED METHODS ====================

    def get_file_permissions(self, file_path: Path) -> Dict:
        """
        Get Unix file permissions in readable format

        Args:
            file_path: Path to file

        Returns:
            {
                'mode': str - rwxr-xr-x format
                'octal': str - 755 format
                'owner': str
                'group': str
                'is_readable': bool
                'is_writable': bool
                'is_executable': bool
            }
        """
        if not file_path.exists():
            return {
                "mode": "---------",
                "octal": "000",
                "owner": "-",
                "group": "-",
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

        try:
            st = file_path.stat()
            mode = st.st_mode

            # Format mode string (rwxrwxrwx)
            mode_str = stat.filemode(mode)

            # Octal format (755)
            octal = oct(stat.S_IMODE(mode))[2:]

            # Owner/group (try to get names, fallback to IDs)
            try:
                import grp
                import pwd

                owner = pwd.getpwuid(st.st_uid).pw_name
                group = grp.getgrgid(st.st_gid).gr_name
            except:
                owner = str(st.st_uid)
                group = str(st.st_gid)

            return {
                "mode": mode_str,
                "octal": octal,
                "owner": owner,
                "group": group,
                "is_readable": os.access(file_path, os.R_OK),
                "is_writable": os.access(file_path, os.W_OK),
                "is_executable": os.access(file_path, os.X_OK),
            }

        except Exception as e:
            logger.error(f"Error getting file permissions for {file_path}: {e}")
            return {
                "mode": "---------",
                "octal": "000",
                "owner": "-",
                "group": "-",
                "is_readable": False,
                "is_writable": False,
                "is_executable": False,
            }

    def get_directory_tree(
        self, db: Session, server_id: int, path: str = "", max_depth: int = 5
    ) -> Dict:
        """
        Get recursive directory tree structure

        Args:
            db: Database session
            server_id: Server ID
            path: Relative path from server root (empty = root)
            max_depth: Maximum recursion depth

        Returns:
            Tree structure with metadata
        """
        mod_dir = self.get_mod_directory(db, server_id)
        server_path = Path(SERVERS_BASE) / f"server_{server_id}" / mod_dir
        target_path = server_path / path if path else server_path

        # Validate path
        try:
            resolved_target = target_path.resolve()
            if not str(resolved_target).startswith(str(server_path.resolve())):
                raise HTTPException(403, "Erisim gecersiz dizine izin verilmiyor")
        except:
            raise HTTPException(400, "Gecersiz dizin yolu")

        if not target_path.exists():
            raise HTTPException(404, "Dizin bulunamadi")

        if not target_path.is_dir():
            raise HTTPException(400, "Belirtilen yol bir dizin degil")

        def build_tree(dir_path: Path, current_depth: int = 0) -> Dict:
            """Recursive tree builder"""
            if current_depth >= max_depth:
                return None

            tree = {
                "label": dir_path.name or mod_dir,
                "key": str(dir_path.relative_to(server_path)),
                "isLeaf": False,
                "children": [],
            }

            try:
                items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

                for item in items:
                    # Skip hidden and protected directories
                    if item.name.startswith("."):
                        continue

                    rel_path = str(item.relative_to(server_path))
                    if any(rel_path.startswith(prot) for prot in PROTECTED_DIRECTORIES):
                        continue

                    if item.is_dir():
                        # Recursive directory
                        child_tree = build_tree(item, current_depth + 1)
                        if child_tree:
                            tree["children"].append(child_tree)
                    else:
                        # File leaf node
                        file_ext = item.suffix.lower()
                        if file_ext not in HIDDEN_FILE_EXTENSIONS:
                            tree["children"].append(
                                {
                                    "label": item.name,
                                    "key": rel_path,
                                    "isLeaf": True,
                                    "size": item.stat().st_size,
                                    "type": self._get_file_type(item),
                                }
                            )

            except PermissionError:
                logger.warning(f"Permission denied accessing {dir_path}")
            except Exception as e:
                logger.error(f"Error building tree for {dir_path}: {e}")

            return tree

        return build_tree(target_path)

    def _get_file_type(self, file_path: Path) -> str:
        """Get file type category"""
        ext = file_path.suffix.lower()
        type_map = {
            ".cfg": "config",
            ".ini": "config",
            ".log": "log",
            ".bsp": "map",
            ".wav": "audio",
            ".mp3": "audio",
            ".mdl": "model",
            ".spr": "sprite",
            ".amxx": "plugin",
            ".sma": "source",
        }
        return type_map.get(ext, "file")

    async def download_file(self, db: Session, server_id: int, file_path: str) -> StreamingResponse:
        """
        Download a single file with streaming - DISABLED for WebPanel users

        Args:
            db: Database session
            server_id: Server ID
            file_path: Relative file path

        Returns:
            StreamingResponse with file content
        """
        raise HTTPException(403, "Dosya indirme WebPanel'den devre dışı bırakıldı")

        mod_dir = self.get_mod_directory(db, server_id)
        server_path = Path(SERVERS_BASE) / f"server_{server_id}" / mod_dir
        target_file = server_path / file_path

        # Validate path
        try:
            resolved_target = target_file.resolve()
            if not str(resolved_target).startswith(str(server_path.resolve())):
                raise HTTPException(403, "Erisim gecersiz dosyaya izin verilmiyor")
        except:
            raise HTTPException(400, "Gecersiz dosya yolu")

        if not target_file.exists():
            raise HTTPException(404, "Dosya bulunamadi")

        if not target_file.is_file():
            raise HTTPException(400, "Belirtilen yol bir dosya degil")

        # Check if file is in protected directory
        rel_path = str(target_file.relative_to(server_path))
        if any(rel_path.startswith(prot) for prot in PROTECTED_DIRECTORIES):
            raise HTTPException(403, "Bu dizinden dosya indirilemez")

        try:
            # Determine content type
            content_type = self._get_content_type(target_file)

            # Stream file
            def file_iterator():
                with open(target_file, "rb") as f:
                    while chunk := f.read(8192):
                        yield chunk

            return StreamingResponse(
                file_iterator(),
                media_type=content_type,
                headers={"Content-Disposition": f'attachment; filename="{target_file.name}"'},
            )

        except Exception as e:
            logger.error(f"Error downloading file {target_file}: {e}")
            raise HTTPException(500, f"Dosya indirme hatasi: {str(e)}")

    def _get_content_type(self, file_path: Path) -> str:
        """Get MIME content type for file"""
        ext = file_path.suffix.lower()
        content_types = {
            ".txt": "text/plain",
            ".cfg": "text/plain",
            ".ini": "text/plain",
            ".log": "text/plain",
            ".bsp": "application/octet-stream",
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".mdl": "application/octet-stream",
            ".amxx": "application/octet-stream",
        }
        return content_types.get(ext, "application/octet-stream")

    async def batch_download(self, db: Session, server_id: int, file_paths: List[str]) -> bytes:
        """
        Create ZIP archive of multiple files - DISABLED for WebPanel users

        Args:
            db: Database session
            server_id: Server ID
            file_paths: List of relative file paths

        Returns:
            ZIP file bytes
        """
        raise HTTPException(403, "Toplu dosya indirme WebPanel'den devre dışı bırakıldı")

        mod_dir = self.get_mod_directory(db, server_id)
        server_path = Path(SERVERS_BASE) / f"server_{server_id}" / mod_dir

        # Create in-memory ZIP
        zip_buffer = BytesIO()

        try:
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in file_paths:
                    target_file = server_path / file_path

                    # Validate each file
                    try:
                        resolved = target_file.resolve()
                        if not str(resolved).startswith(str(server_path.resolve())):
                            continue
                    except:
                        continue

                    if not target_file.exists() or not target_file.is_file():
                        continue

                    # Check protected directories
                    rel_path = str(target_file.relative_to(server_path))
                    if any(rel_path.startswith(prot) for prot in PROTECTED_DIRECTORIES):
                        continue

                    # Add to ZIP
                    zip_file.write(target_file, arcname=target_file.name)

            zip_buffer.seek(0)
            return zip_buffer.getvalue()

        except Exception as e:
            logger.error(f"Error creating ZIP archive: {e}")
            raise HTTPException(500, f"ZIP olusturma hatasi: {str(e)}")

    async def upload_file(
        self,
        db: Session,
        server_id: int,
        target_directory: str,
        file: UploadFile,
        user_id: int,
        overwrite: bool = False,
    ) -> Dict:
        """
        Secure file upload with validation

        Args:
            db: Database session
            server_id: Server ID
            target_directory: Target directory (must be in whitelist)
            file: Uploaded file
            user_id: User ID
            overwrite: Allow overwriting existing files

        Returns:
            Upload result
        """
        # Validate target directory
        if target_directory not in ALLOWED_UPLOAD_DIRECTORIES:
            raise HTTPException(403, f"Bu dizine yukleme izni yok: {target_directory}")

        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_UPLOAD_EXTENSIONS:
            raise HTTPException(400, f"Dosya tipi yuklenemez: {file_ext}")

        # Sanitize filename
        safe_filename = self._sanitize_filename(file.filename)
        if not safe_filename:
            raise HTTPException(400, "Gecersiz dosya adi")

        mod_dir = self.get_mod_directory(db, server_id)
        server_path = Path(SERVERS_BASE) / f"server_{server_id}" / mod_dir
        target_dir = server_path / target_directory
        target_file = target_dir / safe_filename

        # Ensure target directory exists
        target_dir.mkdir(parents=True, exist_ok=True)

        # Check if file exists
        if target_file.exists() and not overwrite:
            raise HTTPException(
                400, "Dosya zaten mevcut. Uzerine yazmak icin overwrite=true kullanin"
            )

        # Backup existing file if overwriting
        if target_file.exists() and overwrite:
            backup_path = target_file.with_suffix(target_file.suffix + ".backup")
            shutil.copy2(target_file, backup_path)

        try:
            # Read file content
            content = await file.read()

            # Validate file size
            file_size = len(content)
            file_type = self._get_upload_file_type(file_ext)
            max_size = MAX_UPLOAD_SIZES.get(file_type, 5 * 1024 * 1024)

            if file_size > max_size:
                raise HTTPException(
                    400, f"Dosya boyutu cok buyuk. Maksimum: {max_size // 1024 // 1024}MB"
                )

            # Write file
            with open(target_file, "wb") as f:
                f.write(content)

            logger.info(f"File uploaded: {target_file} by user {user_id}")

            return {
                "success": True,
                "message": "Dosya yuklendi",
                "filename": safe_filename,
                "path": str(target_file.relative_to(server_path)),
                "size": file_size,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(500, f"Dosya yukleme hatasi: {str(e)}")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        import re

        # Remove path separators and special characters
        safe_name = re.sub(r"[/\\]", "", filename)
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", safe_name)
        # Remove leading dots
        safe_name = safe_name.lstrip(".")
        return safe_name[:255]  # Limit length

    def _get_upload_file_type(self, ext: str) -> str:
        """Get file type category for size limits"""
        type_map = {
            ".cfg": "text",
            ".ini": "text",
            ".txt": "text",
            ".rc": "text",
            ".bsp": "map",
            ".nav": "map",
            ".res": "map",
            ".wav": "audio",
            ".mp3": "audio",
            ".mdl": "model",
            ".spr": "model",
            ".tga": "image",
            ".bmp": "image",
            ".amxx": "plugin",
            ".sma": "plugin",
        }
        return type_map.get(ext, "text")

    async def rename_file(
        self, db: Session, server_id: int, old_path: str, new_name: str, user_id: int
    ) -> Dict:
        """
        Rename file or directory

        Args:
            db: Database session
            server_id: Server ID
            old_path: Current file path
            new_name: New filename (not full path)
            user_id: User ID

        Returns:
            Rename result
        """
        mod_dir = self.get_mod_directory(db, server_id)
        server_path = Path(SERVERS_BASE) / f"server_{server_id}" / mod_dir
        old_file = server_path / old_path

        # Validate old path
        try:
            resolved = old_file.resolve()
            if not str(resolved).startswith(str(server_path.resolve())):
                raise HTTPException(403, "Erisim gecersiz dosyaya izin verilmiyor")
        except:
            raise HTTPException(400, "Gecersiz dosya yolu")

        if not old_file.exists():
            raise HTTPException(404, "Dosya bulunamadi")

        # Check protected
        rel_path = str(old_file.relative_to(server_path))
        if any(rel_path.startswith(prot) for prot in PROTECTED_DIRECTORIES):
            raise HTTPException(403, "Korunmus dosya yeniden adlandirilamaz")

        # Sanitize new name
        safe_new_name = self._sanitize_filename(new_name)
        if not safe_new_name:
            raise HTTPException(400, "Gecersiz dosya adi")

        new_file = old_file.parent / safe_new_name

        # Check if target exists
        if new_file.exists():
            raise HTTPException(400, "Bu isimde bir dosya zaten mevcut")

        try:
            old_file.rename(new_file)
            logger.info(f"File renamed: {old_path} -> {safe_new_name} by user {user_id}")

            return {
                "success": True,
                "message": "Dosya yeniden adlandirildi",
                "old_name": old_file.name,
                "new_name": safe_new_name,
                "new_path": str(new_file.relative_to(server_path)),
            }

        except Exception as e:
            logger.error(f"Error renaming file: {e}")
            raise HTTPException(500, f"Yeniden adlandirma hatasi: {str(e)}")
