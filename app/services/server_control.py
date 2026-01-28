"""
AGTR Merkezi v6.0 - Server Control Service
Sunucu baslat/durdur/yeniden baslat islemleri
"""

import asyncio
import logging
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import psutil
from sqlalchemy.orm import Session

from app.models.database import GameServer, ServerStatus
from app.services.monitor import ServerQuery

logger = logging.getLogger(__name__)


class ServerControlService:
    """
    Sunucu kontrol servisi

    Screen session yonetimi, process izleme ve A2S query
    """

    SERVERS_BASE = "/home/gameservers/servers"

    # Graceful shutdown timeout (saniye)
    GRACEFUL_TIMEOUT = 10

    # Server start timeout (saniye)
    START_TIMEOUT = 30

    def __init__(self, db: Session):
        self.db = db

    def get_server_path(self, server_id: int) -> Path:
        """Sunucu dizin yolunu al"""
        return Path(self.SERVERS_BASE) / f"server_{server_id}"

    def get_screen_name(self, server_id: int) -> str:
        """Screen session adini al"""
        return f"server_{server_id}"

    async def start_server(self, server_id: int) -> Dict:
        """
        Sunucuyu baslat

        Returns:
            {"success": bool, "message": str, "pid": int|None}
        """
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            return {"success": False, "message": "Sunucu bulunamadi", "pid": None}

        # Zaten calisiyorsa
        if await self.is_running(server_id):
            return {
                "success": False,
                "message": "Sunucu zaten calisiyor",
                "pid": server.process_pid,
            }

        server_path = self.get_server_path(server_id)
        start_script = server_path / "start.sh"

        if not start_script.exists():
            return {"success": False, "message": "Baslangic scripti bulunamadi", "pid": None}

        try:
            # Scripti calistir
            process = await asyncio.create_subprocess_exec(
                str(start_script),
                cwd=str(server_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            await process.communicate()

            # Bekle ve kontrol et
            for _ in range(self.START_TIMEOUT // 2):
                await asyncio.sleep(2)

                if await self.is_running(server_id):
                    # PID'i bul
                    pid = await self._get_server_pid(server_id)

                    # Veritabani guncelle
                    server.status = ServerStatus.RUNNING
                    server.process_pid = pid
                    server.last_started = datetime.utcnow()
                    server.last_heartbeat = datetime.utcnow()
                    self.db.commit()

                    logger.info(f"Sunucu baslatildi: {server_id}, PID: {pid}")
                    return {"success": True, "message": "Sunucu baslatildi", "pid": pid}

            return {"success": False, "message": "Sunucu baslatma timeout", "pid": None}

        except Exception as e:
            logger.error(f"Sunucu baslat hatasi: {e}")
            return {"success": False, "message": str(e), "pid": None}

    async def stop_server(self, server_id: int, graceful: bool = True) -> Dict:
        """
        Sunucuyu durdur

        Args:
            server_id: Sunucu ID
            graceful: True ise SIGTERM ile durdur, False ise SIGKILL

        Returns:
            {"success": bool, "message": str}
        """
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            return {"success": False, "message": "Sunucu bulunamadi"}

        screen_name = self.get_screen_name(server_id)

        # Calismiyorsa
        if not await self.is_running(server_id):
            server.status = ServerStatus.STOPPED
            server.process_pid = None
            self.db.commit()
            return {"success": True, "message": "Sunucu zaten durmus"}

        try:
            if graceful:
                # Screen'e quit komutu gonder
                quit_cmd = f"screen -S {screen_name} -X stuff 'quit\\n'"
                await asyncio.create_subprocess_shell(quit_cmd)

                # Bekle
                for _ in range(self.GRACEFUL_TIMEOUT):
                    await asyncio.sleep(1)
                    if not await self.is_running(server_id):
                        break

            # Hala calisiyorsa zorla durdur
            if await self.is_running(server_id):
                # Screen session'i sonlandir
                kill_cmd = f"screen -S {screen_name} -X quit"
                await asyncio.create_subprocess_shell(kill_cmd)
                await asyncio.sleep(1)

                # PID ile oldur
                if server.process_pid:
                    try:
                        os.kill(server.process_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass

            # Veritabani guncelle
            server.status = ServerStatus.STOPPED
            server.process_pid = None
            self.db.commit()

            logger.info(f"Sunucu durduruldu: {server_id}")
            return {"success": True, "message": "Sunucu durduruldu"}

        except Exception as e:
            logger.error(f"Sunucu durdurma hatasi: {e}")
            return {"success": False, "message": str(e)}

    async def restart_server(self, server_id: int) -> Dict:
        """
        Sunucuyu yeniden baslat

        Returns:
            {"success": bool, "message": str, "pid": int|None}
        """
        # Durdur
        stop_result = await self.stop_server(server_id, graceful=True)

        # Kisa bekle
        await asyncio.sleep(2)

        # Baslat
        start_result = await self.start_server(server_id)

        if start_result["success"]:
            return {
                "success": True,
                "message": "Sunucu yeniden baslatildi",
                "pid": start_result.get("pid"),
            }
        else:
            return {
                "success": False,
                "message": f"Yeniden baslatma hatasi: {start_result['message']}",
                "pid": None,
            }

    async def is_running(self, server_id: int) -> bool:
        """Sunucu calisiyormu kontrol et"""
        screen_name = self.get_screen_name(server_id)

        try:
            cmd = f"screen -ls | grep {screen_name}"
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()

            return screen_name in stdout.decode()

        except Exception:
            return False

    async def _get_server_pid(self, server_id: int) -> Optional[int]:
        """Sunucu process ID'sini bul"""
        screen_name = self.get_screen_name(server_id)

        try:
            # Screen session PID
            cmd = f"screen -ls | grep {screen_name} | cut -d'.' -f1 | awk '{{print $1}}'"
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()

            screen_pid_str = stdout.decode().strip()
            if screen_pid_str:
                screen_pid = int(screen_pid_str)

                # Screen child process'leri bul (hlds_linux)
                try:
                    parent = psutil.Process(screen_pid)
                    for child in parent.children(recursive=True):
                        if "hlds" in child.name().lower():
                            return child.pid
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

                return screen_pid

        except Exception as e:
            logger.error(f"PID bulma hatasi: {e}")

        return None

    async def get_status(self, server_id: int) -> Dict:
        """
        Sunucu durumunu al

        Returns:
            {
                "online": bool,
                "status": str,
                "players": int,
                "max_players": int,
                "map": str,
                "hostname": str,
                "pid": int,
                "cpu_percent": float,
                "memory_mb": float,
                "uptime_seconds": int
            }
        """
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            return {"online": False, "status": "not_found"}

        result = {
            "online": False,
            "status": server.status.value if server.status else "unknown",
            "players": 0,
            "max_players": server.slots,
            "map": server.current_map,
            "hostname": server.name,
            "pid": None,
            "cpu_percent": 0.0,
            "memory_mb": 0.0,
            "uptime_seconds": 0,
        }

        # Screen kontrolu
        is_running = await self.is_running(server_id)

        if is_running:
            result["online"] = True
            result["status"] = "running"

            # PID bilgisi
            pid = await self._get_server_pid(server_id)
            result["pid"] = pid

            # Process bilgileri
            if pid:
                try:
                    proc = psutil.Process(pid)
                    result["cpu_percent"] = proc.cpu_percent(interval=0.1)
                    result["memory_mb"] = proc.memory_info().rss / 1024 / 1024

                    # Uptime
                    create_time = datetime.fromtimestamp(proc.create_time())
                    uptime = datetime.now() - create_time
                    result["uptime_seconds"] = int(uptime.total_seconds())

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # A2S Query
            query = ServerQuery(server.ip_address, server.port)
            info = await query.query_info()

            if info:
                result["players"] = info.get("players", 0)
                result["max_players"] = info.get("max_players", server.slots)
                result["map"] = info.get("map", server.current_map)
                result["hostname"] = info.get("hostname", server.name)

                # Veritabani guncelle
                server.current_players = info.get("players", 0)
                server.current_map = info.get("map")
                server.last_heartbeat = datetime.utcnow()
                self.db.commit()

        else:
            # Calismiyorsa veritabani guncelle
            if server.status == ServerStatus.RUNNING:
                server.status = ServerStatus.STOPPED
                server.process_pid = None
                self.db.commit()

        return result

    async def get_process_info(self, server_id: int) -> Dict:
        """
        Detayli process bilgilerini al

        Returns:
            {
                "pid": int,
                "cpu_percent": float,
                "memory_mb": float,
                "memory_percent": float,
                "threads": int,
                "open_files": int,
                "connections": int,
                "uptime_seconds": int,
                "status": str
            }
        """
        pid = await self._get_server_pid(server_id)

        if not pid:
            return {"error": "Process bulunamadi"}

        try:
            proc = psutil.Process(pid)

            # CPU yuzdesini olc (kisa bekleme ile daha dogruluk)
            cpu_percent = proc.cpu_percent(interval=0.5)

            mem_info = proc.memory_info()

            create_time = datetime.fromtimestamp(proc.create_time())
            uptime = datetime.now() - create_time

            return {
                "pid": pid,
                "cpu_percent": cpu_percent,
                "memory_mb": mem_info.rss / 1024 / 1024,
                "memory_percent": proc.memory_percent(),
                "threads": proc.num_threads(),
                "open_files": len(proc.open_files()),
                "connections": len(proc.connections()),
                "uptime_seconds": int(uptime.total_seconds()),
                "status": proc.status(),
            }

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {"error": str(e)}

    async def send_command(self, server_id: int, command: str) -> Tuple[bool, str]:
        """
        Screen session'a komut gonder

        Args:
            server_id: Sunucu ID
            command: Gonderilecek komut

        Returns:
            (basari, mesaj)
        """
        if not await self.is_running(server_id):
            return False, "Sunucu calismiyorgi"

        screen_name = self.get_screen_name(server_id)

        try:
            # Screen'e komut gonder
            cmd = f"screen -S {screen_name} -X stuff '{command}\\n'"
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()

            if process.returncode != 0:
                return False, stderr.decode() if stderr else "Bilinmeyen hata"

            return True, "Komut gonderildi"

        except Exception as e:
            logger.error(f"Komut gonderme hatasi: {e}")
            return False, str(e)

    async def check_and_restart_crashed(self, server_id: int) -> Dict:
        """
        Coken sunucuyu kontrol et ve gerekirse yeniden baslat

        Returns:
            {"restarted": bool, "reason": str}
        """
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if not server:
            return {"restarted": False, "reason": "Sunucu bulunamadi"}

        # Auto restart aktif degil
        if not server.auto_restart:
            return {"restarted": False, "reason": "Otomatik yeniden baslat kapali"}

        # Running olmasi gerekiyor ama calismiyorsa
        if server.status == ServerStatus.RUNNING and not await self.is_running(server_id):
            logger.warning(f"Sunucu cokmesi tespit edildi: {server_id}")

            # Crash sayisini artir
            server.crash_count = (server.crash_count or 0) + 1
            server.last_crash = datetime.utcnow()
            self.db.commit()

            # Yeniden baslat
            result = await self.start_server(server_id)

            if result["success"]:
                return {"restarted": True, "reason": "Cokme sonrasi yeniden baslatildi"}
            else:
                return {"restarted": False, "reason": f"Yeniden baslat hatasi: {result['message']}"}

        return {"restarted": False, "reason": "Yeniden baslat gerekmiyor"}

    async def get_all_server_statuses(self, user_id: int = None) -> list:
        """
        Tum sunucularin durumunu al

        Args:
            user_id: Belirli kullanicinin sunuculari (None = hepsi)

        Returns:
            List of server status dicts
        """
        query = self.db.query(GameServer)

        if user_id:
            query = query.filter(GameServer.owner_id == user_id)

        servers = query.all()
        results = []

        for server in servers:
            status = await self.get_status(server.id)
            status["server_id"] = server.id
            status["unique_code"] = server.unique_code
            status["name"] = server.name
            status["ip"] = server.ip_address
            status["port"] = server.port
            results.append(status)

        return results

    def update_heartbeat(self, server_id: int):
        """Heartbeat zamanini guncelle"""
        server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
        if server:
            server.last_heartbeat = datetime.utcnow()
            self.db.commit()
