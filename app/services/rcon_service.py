"""
AGTR Merkezi v6.0 - RCON Service
Half-Life/GoldSrc RCON protokolu
"""

import asyncio
import logging
import os
import re
import socket
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.database import (
    BanType,
    CommandType,
    GameServer,
    ServerBan,
    ServerConsoleHistory,
)

logger = logging.getLogger(__name__)


def strip_color_codes(text: str) -> str:
    """Remove Half-Life color codes from text (^0-^9)"""
    return re.sub(r"\^\d", "", text)


class RCONClient:
    """
    Half-Life RCON Client

    GoldSrc (Half-Life 1) RCON protokolu
    """

    # RCON challenge response
    RCON_CHALLENGE = b"\xFF\xFF\xFF\xFFchallenge rcon\n"

    def __init__(self, ip: str, port: int, password: str, timeout: float = 5.0):
        self.ip = ip
        self.port = port
        self.password = password
        self.timeout = timeout
        self.challenge = None

    async def _get_challenge(self) -> Optional[str]:
        """RCON challenge al"""
        try:
            loop = asyncio.get_event_loop()

            def _query():
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.timeout)
                try:
                    sock.sendto(self.RCON_CHALLENGE, (self.ip, self.port))
                    data, _ = sock.recvfrom(4096)
                    # Response: \xFF\xFF\xFF\xFFchallenge rcon 1234567890\n
                    response = data.decode("utf-8", errors="ignore")
                    match = re.search(r"challenge rcon (\d+)", response)
                    if match:
                        return match.group(1)
                    return None
                finally:
                    sock.close()

            return await loop.run_in_executor(None, _query)

        except Exception as e:
            logger.error(f"RCON challenge hatasi: {e}")
            return None

    async def execute(self, command: str) -> Optional[str]:
        """
        RCON komutu calistir

        Args:
            command: Calistirilacak komut

        Returns:
            Komut ciktisi veya None
        """
        try:
            # Challenge al
            challenge = await self._get_challenge()
            if not challenge:
                logger.error("RCON challenge alinamadi")
                return None

            loop = asyncio.get_event_loop()

            def _execute():
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.timeout)
                try:
                    # RCON paketi: \xFF\xFF\xFF\xFFrcon {challenge} "{password}" {command}
                    packet = f'\xFF\xFF\xFF\xFFrcon {challenge} "{self.password}" {command}'
                    sock.sendto(packet.encode("utf-8"), (self.ip, self.port))

                    # Yanit al
                    responses = []
                    while True:
                        try:
                            data, _ = sock.recvfrom(4096)
                            # Response: \xFF\xFF\xFF\xFFl{response}
                            if data.startswith(b"\xFF\xFF\xFF\xFFl"):
                                response = data[5:].decode("utf-8", errors="ignore")
                                responses.append(response)
                            elif data.startswith(b"\xFF\xFF\xFF\xFF"):
                                response = data[4:].decode("utf-8", errors="ignore")
                                responses.append(response)
                        except socket.timeout:
                            break

                    return "\n".join(responses) if responses else ""

                finally:
                    sock.close()

            return await loop.run_in_executor(None, _execute)

        except Exception as e:
            logger.error(f"RCON execute hatasi: {e}")
            return None


class RCONService:
    """
    RCON Servis Katmani

    Komut validasyonu, loglama ve yuksek seviye islemler
    """

    # Yasakli komutlar (guvenlik)
    BLOCKED_COMMANDS = [
        "quit",
        "exit",
        "_restart",
        "kill",
        "rcon_password",
        "sv_rcon_password",
        "sys_ticrate",
        "fps_max",
        "fps_override",
        "sv_maxrate",
        "sv_minrate",
        "sv_maxupdaterate",
        "sv_minupdaterate",
        "sv_lan",
        "sv_cheats",
        "exec",
        "plugin_load",
        "plugin_unload",
        "map_background",
        "connect",
        "disconnect",
        "changelevel2",
        "restart",
        "_restart",
        "developer",
        "sv_password",
        "rcon_address",
    ]

    # Sinirli komutlar (belirli formatta olmali)
    RESTRICTED_PATTERNS = {
        "changelevel": r"^changelevel\s+[a-zA-Z0-9_-]+$",
        "kick": r"^kick\s+(#?\d+|\".+\")(\s+.+)?$",
        "ban": r"^ban\s+.+$",
        "banid": r"^banid\s+\d+\s+.+$",
        "addip": r"^addip\s+\d+\s+[\d\.]+$",
    }

    def __init__(self, db: Session):
        self.db = db

    def validate_command(self, command: str) -> Tuple[bool, str]:
        """
        Komutu dogrula

        Returns:
            (gecerli, mesaj)
        """
        if not command or not command.strip():
            return False, "Bos komut"

        command = command.strip()
        cmd_lower = command.lower()
        cmd_parts = cmd_lower.split()
        cmd_name = cmd_parts[0] if cmd_parts else ""

        # Yasakli komut kontrolu
        for blocked in self.BLOCKED_COMMANDS:
            if cmd_name == blocked.lower():
                return False, f"Yasakli komut: {blocked}"

        # Sinirli komut pattern kontrolu
        for restricted, pattern in self.RESTRICTED_PATTERNS.items():
            if cmd_name == restricted.lower():
                if not re.match(pattern, command, re.IGNORECASE):
                    return False, f"Gecersiz komut formati: {restricted}"

        return True, "OK"

    async def execute(
        self,
        server: GameServer,
        command: str,
        user_id: int,
        command_type: CommandType = CommandType.RCON,
        ip_address: str = None,
    ) -> Dict:
        """
        RCON komutu calistir

        Args:
            server: GameServer instance
            command: Calistirilacak komut
            user_id: Kullanici ID
            command_type: Komut tipi
            ip_address: Kullanici IP

        Returns:
            {
                "success": bool,
                "response": str,
                "error": str,
                "execution_time_ms": int
            }
        """
        start_time = datetime.utcnow()

        # Validasyon
        valid, message = self.validate_command(command)
        if not valid:
            self._log_command(
                server.id, user_id, command, None, command_type, ip_address, False, message
            )
            return {"success": False, "response": None, "error": message, "execution_time_ms": 0}

        # Screen-based command execution (RCON UDP timeout issues)
        try:
            import subprocess

            screen_name = f"server_{server.id}"

            # Send command to screen
            cmd = ["screen", "-S", screen_name, "-X", "stuff", f"{command}\n"]
            subprocess.run(cmd, timeout=5, check=False)

            # Wait a bit for command to execute
            await asyncio.sleep(0.5)

            # Capture output from screen (use temp file securely)
            with tempfile.NamedTemporaryFile(
                mode="w+", prefix=f"server_{server.id}_output_", suffix=".txt", delete=False
            ) as tmp_file:
                output_file = tmp_file.name

            try:
                subprocess.run(
                    ["screen", "-S", screen_name, "-X", "hardcopy", output_file],
                    timeout=5,
                    check=False,
                )

                # Read output
                response = ""
                try:
                    with open(output_file, "r", errors="ignore") as f:
                        lines = f.readlines()
                        # Get last 50 lines
                        response = "".join(lines[-50:])
                except:
                    response = ""
            finally:
                # Clean up temp file
                try:
                    os.unlink(output_file)
                except:
                    pass

            end_time = datetime.utcnow()
            execution_time = int((end_time - start_time).total_seconds() * 1000)

            # Log
            self._log_command(
                server.id,
                user_id,
                command,
                response,
                command_type,
                ip_address,
                True,
                None,
                execution_time,
            )

            return {
                "success": True,
                "response": response,
                "error": None,
                "execution_time_ms": execution_time,
            }

        except Exception as e:
            error = str(e)
            logger.error(f"RCON hatasi: {error}")

            self._log_command(
                server.id, user_id, command, None, command_type, ip_address, False, error
            )

            return {"success": False, "response": None, "error": error, "execution_time_ms": 0}

    def _log_command(
        self,
        server_id: int,
        user_id: int,
        command: str,
        response: Optional[str],
        command_type: CommandType,
        ip_address: Optional[str],
        is_success: bool,
        error_message: Optional[str],
        execution_time_ms: int = 0,
    ):
        """Komut gecmisini kaydet"""
        # Skip logging if user_id is 0 (system commands)
        if user_id == 0:
            return

        log = ServerConsoleHistory(
            server_id=server_id,
            user_id=user_id,
            command=command,
            response=response,
            command_type=command_type,
            execution_time_ms=execution_time_ms,
            ip_address=ip_address,
            is_success=is_success,
            error_message=error_message,
            created_at=datetime.utcnow(),
        )

        self.db.add(log)
        self.db.commit()

    async def get_status(self, server: GameServer) -> Dict:
        """
        Sunucu status komutu

        Returns:
            {
                "hostname": str,
                "map": str,
                "players": str,
                "version": str,
                "raw": str
            }
        """
        result = await self.execute(server, "status", 0, CommandType.SYSTEM)

        if not result["success"]:
            return {"error": result["error"]}

        response = result["response"] or ""

        # Parse status response
        parsed = {"hostname": "", "map": "", "players": "", "version": "", "raw": response}

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("hostname:"):
                parsed["hostname"] = line.split(":", 1)[1].strip()
            elif line.startswith("map"):
                parsed["map"] = line.split(":", 1)[1].strip().split()[0]
            elif line.startswith("players"):
                parsed["players"] = line.split(":", 1)[1].strip()
            elif line.startswith("version"):
                parsed["version"] = line.split(":", 1)[1].strip()

        return parsed

    async def get_players(self, server: GameServer) -> List[Dict]:
        """
        Oyuncu listesini al (Enhanced with frags and loss)

        Returns:
            [{"slot": int, "name": str, "steam_id": str, "frags": int, "time": str, "ping": int, "loss": int, "ip": str}]
        """
        import subprocess

        try:
            screen_name = f"server_{server.id}"

            # Send status command
            subprocess.run(
                ["screen", "-S", screen_name, "-X", "stuff", "status\n"], timeout=5, check=False
            )
            await asyncio.sleep(1)

            # Capture output (use temp file securely)
            with tempfile.NamedTemporaryFile(
                mode="w+", prefix=f"server_{server.id}_status_", suffix=".txt", delete=False
            ) as tmp_file:
                output_file = tmp_file.name

            try:
                subprocess.run(
                    ["screen", "-S", screen_name, "-X", "hardcopy", output_file],
                    timeout=5,
                    check=False,
                )

                # Read and parse
                response = ""
                try:
                    with open(output_file, "r", errors="ignore") as f:
                        response = f.read()
                except:
                    return []
            finally:
                # Clean up temp file
                try:
                    os.unlink(output_file)
                except:
                    pass

            players = []
            seen_steamids = set()  # Track unique players

            # Parse player lines (multiline format - IP can be on next line)
            lines = response.split("\n")

            for i, line in enumerate(lines):
                if line.startswith("# ") and '"' in line:
                    # Pattern: # slot "name" userid steamid frags time ping loss [ip:port or next line]
                    # Group 5 = frags, Group 8 = loss (we were ignoring it with \d+)
                    pattern = r'#\s*(\d+)\s+"([^"]+)"\s+(\d+)\s+(\S+)\s+(-?\d+)\s+(\S+)\s+(\d+)\s+(\d+)(?:\s+([\d\.]+:\d+))?'
                    match = re.search(pattern, line)

                    if match:
                        steam_id = match.group(4)

                        # Skip if already seen (duplicate in console output)
                        if steam_id in seen_steamids:
                            continue
                        seen_steamids.add(steam_id)

                        # Clean player name from color codes
                        player_name = strip_color_codes(match.group(2))

                        ip_port = match.group(9)  # IP might be on same line (shifted by 1)

                        # If not on same line, check next line
                        if not ip_port and i + 1 < len(lines):
                            next_line = lines[i + 1]
                            ip_match = re.search(r"([\d\.]+):(\d+)", next_line)
                            if ip_match:
                                ip_port = ip_match.group(0)

                        players.append(
                            {
                                "slot": int(match.group(1)),
                                "name": player_name,
                                "steam_id": steam_id,
                                "frags": int(match.group(5)),  # NEW: Frags/kills
                                "time": match.group(6),
                                "ping": int(match.group(7)),
                                "loss": int(match.group(8)),  # NEW: Packet loss percentage
                                "ip": ip_port.split(":")[0] if ip_port else "unknown",
                            }
                        )

            return players
        except Exception as e:
            logger.error(f"Get players error: {e}")
            return []

    async def kick_player(
        self,
        server: GameServer,
        player_slot: int,
        reason: str,
        user_id: int,
        ip_address: str = None,
    ) -> Dict:
        """
        Oyuncuyu at

        Args:
            server: GameServer instance
            player_slot: Oyuncu slot numarasi
            reason: Atilma sebebi
            user_id: Islemi yapan kullanici
            ip_address: Kullanici IP

        Returns:
            {"success": bool, "message": str}
        """
        command = f'kick #{player_slot} "{reason}"'

        result = await self.execute(server, command, user_id, CommandType.RCON, ip_address)

        if result["success"]:
            return {"success": True, "message": "Oyuncu atildi"}
        else:
            return {"success": False, "message": result["error"]}

    async def ban_player(
        self,
        server: GameServer,
        steam_id: str,
        ip_address: str,
        player_name: str,
        reason: str,
        duration_minutes: int,
        user_id: int,
        request_ip: str = None,
    ) -> Dict:
        """
        Oyuncuyu banla

        Args:
            server: GameServer instance
            steam_id: Steam ID
            ip_address: Oyuncu IP
            player_name: Oyuncu adi
            reason: Ban sebebi
            duration_minutes: Ban suresi (dakika), 0 = kalici
            user_id: Islemi yapan kullanici
            request_ip: Kullanici IP

        Returns:
            {"success": bool, "message": str, "ban_id": int}
        """
        # Veritabanina kaydet
        ban = ServerBan(
            server_id=server.id,
            steam_id=steam_id,
            ip_address=ip_address,
            name=player_name,
            reason=reason,
            banned_by=user_id,
            duration_minutes=duration_minutes,
            is_active=True,
            ban_type=(
                BanType.BOTH
                if steam_id and ip_address
                else (BanType.STEAM if steam_id else BanType.IP)
            ),
            created_at=datetime.utcnow(),
        )

        if duration_minutes > 0:
            from datetime import timedelta

            ban.expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)

        self.db.add(ban)
        self.db.commit()
        self.db.refresh(ban)

        # RCON ile banla
        if steam_id:
            ban_cmd = f"banid {duration_minutes} {steam_id}"
            await self.execute(server, ban_cmd, user_id, CommandType.RCON, request_ip)

        if ip_address:
            addip_cmd = f"addip {duration_minutes} {ip_address}"
            await self.execute(server, addip_cmd, user_id, CommandType.RCON, request_ip)

        # Kicked
        kick_cmd = f'kick "{player_name}" "{reason}"'
        await self.execute(server, kick_cmd, user_id, CommandType.RCON, request_ip)

        return {"success": True, "message": "Oyuncu banlandi", "ban_id": ban.id}

    async def unban_player(
        self, server: GameServer, ban_id: int, user_id: int, request_ip: str = None
    ) -> Dict:
        """
        Bani kaldir

        Args:
            server: GameServer instance
            ban_id: Ban ID
            user_id: Islemi yapan kullanici
            request_ip: Kullanici IP

        Returns:
            {"success": bool, "message": str}
        """
        ban = (
            self.db.query(ServerBan)
            .filter(ServerBan.id == ban_id, ServerBan.server_id == server.id)
            .first()
        )

        if not ban:
            return {"success": False, "message": "Ban bulunamadi"}

        # RCON ile kaldir
        if ban.steam_id:
            removeid_cmd = f"removeid {ban.steam_id}"
            await self.execute(server, removeid_cmd, user_id, CommandType.RCON, request_ip)

        if ban.ip_address:
            removeip_cmd = f"removeip {ban.ip_address}"
            await self.execute(server, removeip_cmd, user_id, CommandType.RCON, request_ip)

        # Veritabaninda pasif yap
        ban.is_active = False
        self.db.commit()

        return {"success": True, "message": "Ban kaldirildi"}

    async def change_map(
        self, server: GameServer, map_name: str, user_id: int, request_ip: str = None
    ) -> Dict:
        """
        Harita degistir

        Args:
            server: GameServer instance
            map_name: Harita adi
            user_id: Islemi yapan kullanici
            request_ip: Kullanici IP

        Returns:
            {"success": bool, "message": str}
        """
        # Harita adi validasyonu
        if not re.match(r"^[a-zA-Z0-9_-]+$", map_name):
            return {"success": False, "message": "Gecersiz harita adi"}

        command = f"changelevel {map_name}"
        result = await self.execute(server, command, user_id, CommandType.RCON, request_ip)

        if result["success"]:
            return {"success": True, "message": f"Harita degistiriliyor: {map_name}"}
        else:
            return {"success": False, "message": result["error"]}

    async def say(
        self, server: GameServer, message: str, user_id: int, request_ip: str = None
    ) -> Dict:
        """
        Tum oyunculara mesaj gonder

        Args:
            server: GameServer instance
            message: Mesaj
            user_id: Islemi yapan kullanici
            request_ip: Kullanici IP

        Returns:
            {"success": bool, "message": str}
        """
        # Mesaj temizle (RCON injection engelle)
        safe_message = re.sub(r'[;\n\r"\\]', "", message)

        command = f'say "{safe_message}"'
        result = await self.execute(server, command, user_id, CommandType.RCON, request_ip)

        return {
            "success": result["success"],
            "message": "Mesaj gonderildi" if result["success"] else result["error"],
        }

    async def restart_round(self, server: GameServer, user_id: int, request_ip: str = None) -> Dict:
        """
        Round'u yeniden baslat (CS 1.6)
        """
        command = "sv_restart 1"
        result = await self.execute(server, command, user_id, CommandType.RCON, request_ip)

        return {
            "success": result["success"],
            "message": "Round yeniden baslatildi" if result["success"] else result["error"],
        }

    def get_command_history(self, server_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Komut gecmisini al

        Args:
            server_id: Sunucu ID
            limit: Maksimum kayit
            offset: Baslangic

        Returns:
            List of command history
        """
        history = (
            self.db.query(ServerConsoleHistory)
            .filter(ServerConsoleHistory.server_id == server_id)
            .order_by(ServerConsoleHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return [
            {
                "id": h.id,
                "command": h.command,
                "response": h.response,
                "command_type": h.command_type.value if h.command_type else None,
                "is_success": h.is_success,
                "error_message": h.error_message,
                "execution_time_ms": h.execution_time_ms,
                "ip_address": h.ip_address,
                "created_at": h.created_at.isoformat() if h.created_at else None,
            }
            for h in history
        ]

    # ==================== PLAYER MONITORING ENHANCEMENTS ====================

    # In-memory cache for player status
    _player_cache = {}
    _cache_timestamps = {}

    async def get_player_status_cached(
        self, server: GameServer, cache_seconds: int = 5
    ) -> List[Dict]:
        """
        Get player list with caching to prevent RCON spam

        Args:
            server: GameServer instance
            cache_seconds: Cache time in seconds (default 5)

        Returns:
            List of players with cached data
        """
        cache_key = f"players_{server.id}"
        now = datetime.now()

        # Check if cache is valid
        if cache_key in self._player_cache:
            cache_time = self._cache_timestamps.get(cache_key)
            if cache_time and (now - cache_time).total_seconds() < cache_seconds:
                return self._player_cache[cache_key]

        # Cache miss or expired - fetch new data
        players = await self.get_players(server)

        # Update cache
        self._player_cache[cache_key] = players
        self._cache_timestamps[cache_key] = now

        return players

    async def set_server_password(
        self, server: GameServer, password: str, user_id: int, db: Session, ip_address: str = None
    ) -> Dict:
        """
        Set server password via RCON (sv_password cvar)

        Args:
            server: GameServer instance
            password: New password (empty string = remove password)
            user_id: User ID performing the action
            db: Database session for audit log
            ip_address: User IP for audit log

        Returns:
            {"success": bool, "message": str}
        """
        import subprocess

        # Validate password
        if password:
            # Alphanumeric only, max 32 chars
            if not re.match(r"^[a-zA-Z0-9_-]+$", password):
                return {
                    "success": False,
                    "message": "Şifre sadece harf, rakam, tire ve alt çizgi içerebilir",
                }
            if len(password) > 32:
                return {"success": False, "message": "Şifre maksimum 32 karakter olabilir"}

        try:
            screen_name = f"server_{server.id}"

            # Build sv_password command
            if password:
                command = f'sv_password "{password}"'
            else:
                command = 'sv_password ""'  # Remove password

            # Send command via screen
            subprocess.run(
                ["screen", "-S", screen_name, "-X", "stuff", f"{command}\n"], timeout=5, check=False
            )

            await asyncio.sleep(0.5)

            # Log to console history
            try:
                history = ServerConsoleHistory(
                    server_id=server.id,
                    user_id=user_id,
                    command=command,
                    response="Server password updated",
                    command_type=CommandType.SERVER_CONFIG,
                    is_success=True,
                    ip_address=ip_address,
                )
                db.add(history)
                db.commit()
            except Exception as e:
                logger.error(f"Failed to log password change: {e}")

            logger.info(
                f"Server {server.id} password {'set' if password else 'removed'} "
                f"by user {user_id}"
            )

            return {
                "success": True,
                "message": (
                    "Sunucu şifresi güncellendi" if password else "Sunucu şifresi kaldırıldı"
                ),
            }

        except Exception as e:
            logger.error(f"Set password error for server {server.id}: {e}")
            return {"success": False, "message": f"Şifre değiştirme hatası: {str(e)}"}
