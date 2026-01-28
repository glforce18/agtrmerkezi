"""
AGTR Merkezi v5.0 - Server Monitor Service
Sunucu saglik kontrolu ve izleme
"""

import asyncio
import logging
import socket
import struct
from datetime import datetime, timedelta
from typing import List, Optional

logger = logging.getLogger(__name__)


class ServerQuery:
    """Half-Life/Source server query"""

    A2S_INFO = b"\xFF\xFF\xFF\xFFTSource Engine Query\x00"
    A2S_PLAYER = b"\xFF\xFF\xFF\xFF\x55"
    A2S_RULES = b"\xFF\xFF\xFF\xFF\x56"

    def __init__(self, ip: str, port: int, timeout: float = 3.0):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    async def query_info(self) -> Optional[dict]:
        """Sunucu bilgilerini sorgula"""
        try:
            loop = asyncio.get_event_loop()

            def _query():
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.timeout)
                try:
                    sock.sendto(self.A2S_INFO, (self.ip, self.port))
                    data, addr = sock.recvfrom(4096)
                    return self._parse_info(data)
                finally:
                    sock.close()

            return await loop.run_in_executor(None, _query)
        except socket.timeout:
            logger.debug(f"Query timeout: {self.ip}:{self.port}")
            return None
        except Exception as e:
            logger.error(f"Query error {self.ip}:{self.port}: {e}")
            return None

    def _parse_info(self, data: bytes) -> dict:
        """A2S_INFO response parse"""
        try:
            # Skip header
            if data[4] == 0x49:  # Source query response
                offset = 5
            elif data[4] == 0x6D:  # GoldSrc query response
                offset = 5
            else:
                return {}

            # Parse strings
            def read_string(data, offset):
                end = data.index(b"\x00", offset)
                return data[offset:end].decode("utf-8", errors="ignore"), end + 1

            info = {}
            info["name"], offset = read_string(data, offset)
            info["map"], offset = read_string(data, offset)
            info["folder"], offset = read_string(data, offset)
            info["game"], offset = read_string(data, offset)

            # Parse numbers
            if len(data) > offset + 10:
                info["app_id"] = struct.unpack("<H", data[offset : offset + 2])[0]
                info["players"] = data[offset + 2]
                info["max_players"] = data[offset + 3]
                info["bots"] = data[offset + 4]
                info["server_type"] = chr(data[offset + 5])
                info["environment"] = chr(data[offset + 6])
                info["visibility"] = data[offset + 7]
                info["vac"] = data[offset + 8]

            return info
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return {}


class ServerMonitor:
    """Sunucu izleme servisi"""

    def __init__(self):
        self.servers = {}  # server_id -> ServerStatus
        self.history = {}  # server_id -> [status_entries]
        self._running = False
        self._task = None

    def add_server(self, server_id: int, ip: str, port: int, name: str = None):
        """Izlenecek sunucu ekle"""
        self.servers[server_id] = {
            "ip": ip,
            "port": port,
            "name": name or f"{ip}:{port}",
            "status": "unknown",
            "last_check": None,
            "last_online": None,
            "consecutive_fails": 0,
            "info": {},
        }
        self.history[server_id] = []
        logger.info(f"Server added to monitor: {server_id} ({ip}:{port})")

    def remove_server(self, server_id: int):
        """Sunucuyu izlemeden cikar"""
        if server_id in self.servers:
            del self.servers[server_id]
        if server_id in self.history:
            del self.history[server_id]

    async def check_server(self, server_id: int) -> dict:
        """Tek sunucuyu kontrol et"""
        if server_id not in self.servers:
            return {"error": "Server not found"}

        server = self.servers[server_id]
        query = ServerQuery(server["ip"], server["port"])

        info = await query.query_info()
        now = datetime.utcnow()

        if info:
            server["status"] = "online"
            server["last_online"] = now
            server["consecutive_fails"] = 0
            server["info"] = info
            status = "online"
        else:
            server["consecutive_fails"] += 1
            if server["consecutive_fails"] >= 3:
                server["status"] = "offline"
                status = "offline"
            else:
                status = "checking"

        server["last_check"] = now

        # History'e ekle
        entry = {
            "timestamp": now,
            "status": status,
            "players": info.get("players", 0) if info else 0,
            "map": info.get("map", "") if info else "",
        }
        self.history[server_id].append(entry)

        # Son 24 saat tut
        cutoff = now - timedelta(hours=24)
        self.history[server_id] = [e for e in self.history[server_id] if e["timestamp"] > cutoff]

        return {
            "server_id": server_id,
            "status": status,
            "info": info,
            "checked_at": now.isoformat(),
        }

    async def check_all_servers(self) -> List[dict]:
        """Tum sunuculari kontrol et"""
        results = []
        for server_id in list(self.servers.keys()):
            result = await self.check_server(server_id)
            results.append(result)
            await asyncio.sleep(0.1)  # Rate limiting
        return results

    def get_server_status(self, server_id: int) -> Optional[dict]:
        """Sunucu durumunu getir"""
        if server_id not in self.servers:
            return None

        server = self.servers[server_id]
        history = self.history.get(server_id, [])

        # Uptime hesapla
        online_count = sum(1 for h in history if h["status"] == "online")
        total_count = len(history) or 1
        uptime_percent = (online_count / total_count) * 100

        return {**server, "uptime_24h": round(uptime_percent, 2), "checks_24h": total_count}

    def get_all_status(self) -> List[dict]:
        """Tum sunucu durumlarini getir"""
        return [self.get_server_status(sid) for sid in self.servers.keys()]

    def get_statistics(self) -> dict:
        """Genel istatistikler"""
        total = len(self.servers)
        online = sum(1 for s in self.servers.values() if s["status"] == "online")
        offline = sum(1 for s in self.servers.values() if s["status"] == "offline")

        total_players = sum(s.get("info", {}).get("players", 0) for s in self.servers.values())

        return {
            "total_servers": total,
            "online": online,
            "offline": offline,
            "unknown": total - online - offline,
            "total_players": total_players,
        }

    async def start_monitoring(self, interval: int = 60):
        """Izlemeyi baslat"""
        self._running = True
        logger.info(f"Server monitoring started (interval: {interval}s)")

        while self._running:
            try:
                await self.check_all_servers()
            except Exception as e:
                logger.error(f"Monitoring error: {e}")

            await asyncio.sleep(interval)

    def stop_monitoring(self):
        """Izlemeyi durdur"""
        self._running = False
        logger.info("Server monitoring stopped")

    async def collect_server_metrics(self, server, db):
        """
        Collect detailed resource metrics for a running server.

        Args:
            server: GameServer instance
            db: Database session

        Returns:
            ServerMetrics instance or None if collection failed
        """
        try:
            import psutil

            from app.models.database import ServerMetrics

            # Check if process exists
            if not server.process_pid:
                logger.warning(f"Server {server.id} has no process_pid")
                return None

            if not psutil.pid_exists(server.process_pid):
                logger.warning(f"Server {server.id} process {server.process_pid} not found")
                return None

            # Get process handle
            process = psutil.Process(server.process_pid)

            # Collect CPU usage (1 second interval for accuracy)
            cpu_percent = process.cpu_percent(interval=1.0)

            # Collect memory usage
            mem_info = process.memory_info()
            memory_mb = mem_info.rss / (1024 * 1024)  # Convert bytes to MB

            # Get process status
            process_status = process.status()

            # Query A2S for player count
            player_count = 0
            try:
                query = ServerQuery(server.ip_address, server.port, timeout=2.0)
                info = await query.query_info()
                if info:
                    player_count = info.get("players", 0)
            except Exception as e:
                logger.debug(f"A2S query failed for server {server.id}: {e}")

            # Network I/O (optional, may require elevated permissions)
            network_in_mbps = None
            network_out_mbps = None
            try:
                io_counters = process.io_counters()
                # Store raw bytes for now, can calculate rate in analysis
                network_in_mbps = io_counters.read_bytes / (1024 * 1024)  # MB
                network_out_mbps = io_counters.write_bytes / (1024 * 1024)  # MB
            except (AttributeError, PermissionError):
                # io_counters not available on all platforms or requires permissions
                pass

            # Create metrics record
            metric = ServerMetrics(
                server_id=server.id,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                network_in_mbps=network_in_mbps,
                network_out_mbps=network_out_mbps,
                process_status=process_status,
                player_count=player_count,
                timestamp=datetime.utcnow(),
            )

            db.add(metric)
            db.commit()

            # Alert thresholds
            if cpu_percent > 80:
                await self._alert_high_cpu(server, cpu_percent, db)

            if memory_mb > 2048:  # 2GB threshold
                await self._alert_high_memory(server, memory_mb, db)

            logger.debug(
                f"Metrics collected for server {server.id}: "
                f"CPU={cpu_percent:.1f}%, MEM={memory_mb:.1f}MB, "
                f"Players={player_count}, Status={process_status}"
            )

            return metric

        except psutil.NoSuchProcess:
            logger.error(f"Server {server.id} process died (PID: {server.process_pid})")
            await self._handle_server_crash(server, db)
            return None
        except Exception as e:
            logger.error(f"Failed to collect metrics for server {server.id}: {e}")
            return None

    async def _alert_high_cpu(self, server, cpu_percent, db):
        """Alert on high CPU usage"""
        logger.warning(
            f"HIGH CPU ALERT: Server {server.id} ({server.name}) " f"using {cpu_percent:.1f}% CPU"
        )
        # TODO: Send notification to owner
        # from app.services.notifications import send_alert
        # await send_alert(server.owner_id, f"High CPU usage on {server.name}")

    async def _alert_high_memory(self, server, memory_mb, db):
        """Alert on high memory usage"""
        logger.warning(
            f"HIGH MEMORY ALERT: Server {server.id} ({server.name}) " f"using {memory_mb:.1f}MB RAM"
        )
        # TODO: Send notification to owner

    async def _handle_server_crash(self, server, db):
        """Handle server crash detection"""
        from app.models.database import ServerStatus

        logger.error(f"Server {server.id} ({server.name}) crashed!")

        # Update server status
        server.status = ServerStatus.STOPPED
        server.process_pid = None

        db.commit()

        # TODO: Trigger auto-restart if enabled
        # if server.auto_restart:
        #     await restart_server(server)


class HealthChecker:
    """Sistem saglik kontrolu"""

    @staticmethod
    async def check_database() -> dict:
        """Database baglanti kontrolu"""
        try:
            from app.models.database import check_database_connection

            result = check_database_connection()
            return {
                "component": "database",
                "status": result.get("status", "unknown"),
                "message": result.get("message", ""),
            }
        except Exception as e:
            return {"component": "database", "status": "unhealthy", "message": str(e)}

    @staticmethod
    async def check_redis() -> dict:
        """Redis baglanti kontrolu"""
        try:
            import redis

            r = redis.Redis(host="localhost", port=6379, socket_timeout=2)
            r.ping()
            return {"component": "redis", "status": "healthy"}
        except Exception as e:
            return {"component": "redis", "status": "unhealthy", "message": str(e)}

    @staticmethod
    async def check_disk() -> dict:
        """Disk kullanimi kontrolu"""
        try:
            import shutil

            total, used, free = shutil.disk_usage("/")
            percent = (used / total) * 100

            status = "healthy" if percent < 80 else "warning" if percent < 90 else "critical"

            return {
                "component": "disk",
                "status": status,
                "total_gb": round(total / (2**30), 2),
                "used_gb": round(used / (2**30), 2),
                "free_gb": round(free / (2**30), 2),
                "percent": round(percent, 2),
            }
        except Exception as e:
            return {"component": "disk", "status": "unknown", "message": str(e)}

    @staticmethod
    async def check_memory() -> dict:
        """Memory kullanimi kontrolu"""
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()

            mem = {}
            for line in lines:
                parts = line.split()
                if parts[0] in ["MemTotal:", "MemFree:", "MemAvailable:", "Buffers:", "Cached:"]:
                    mem[parts[0].rstrip(":")] = int(parts[1])

            total = mem.get("MemTotal", 0)
            available = mem.get("MemAvailable", mem.get("MemFree", 0))
            used = total - available
            percent = (used / total) * 100 if total > 0 else 0

            status = "healthy" if percent < 80 else "warning" if percent < 90 else "critical"

            return {
                "component": "memory",
                "status": status,
                "total_mb": round(total / 1024, 2),
                "used_mb": round(used / 1024, 2),
                "available_mb": round(available / 1024, 2),
                "percent": round(percent, 2),
            }
        except Exception as e:
            return {"component": "memory", "status": "unknown", "message": str(e)}

    @staticmethod
    async def full_health_check() -> dict:
        """Tam saglik kontrolu"""
        checks = await asyncio.gather(
            HealthChecker.check_database(),
            HealthChecker.check_redis(),
            HealthChecker.check_disk(),
            HealthChecker.check_memory(),
        )

        overall = "healthy"
        for check in checks:
            if check["status"] == "critical":
                overall = "critical"
                break
            elif check["status"] == "unhealthy":
                overall = "unhealthy"
            elif check["status"] == "warning" and overall == "healthy":
                overall = "warning"

        return {
            "overall": overall,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {c["component"]: c for c in checks},
        }


# Global instances
server_monitor = ServerMonitor()
health_checker = HealthChecker()
