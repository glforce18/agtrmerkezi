"""
AGTR Merkezi v6.1 - Port Pool Management Service
Distributed port allocation with load balancing across multiple IPs
"""

import logging
from typing import Dict, Optional, Tuple

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.database import GameServer, ServerStatus

logger = logging.getLogger(__name__)


class PortPoolManager:
    """
    Port Pool Manager - Atomic IP:PORT allocation with load balancing

    Features:
    - PostgreSQL advisory locks for race condition prevention
    - Round-robin load balancing across multiple IPs
    - Automatic port recycling for deleted/expired servers
    """

    # Advisory lock ID (arbitrary unique number for port allocation)
    ADVISORY_LOCK_ID = 123456789

    # IP and Port configuration from settings
    AVAILABLE_IPS = (
        settings.GAME_SERVER_IPS
    )  # ["185.171.25.138", "185.171.25.139", "185.171.25.140"]
    PORT_RANGE_START = settings.GAME_PORT_START  # 27018
    PORT_RANGE_END = settings.GAME_PORT_END  # 27067
    PORTS_PER_IP = settings.PORTS_PER_IP  # 50

    # Total capacity
    TOTAL_SLOTS = len(AVAILABLE_IPS) * PORTS_PER_IP  # 150

    def __init__(self, db: Session):
        """Initialize PortPoolManager with database session"""
        self.db = db

    def acquire_slot(self) -> Optional[Tuple[str, int]]:
        """
        Atomically acquire an available (IP, port) slot with load balancing.

        Strategy:
        1. Acquire MySQL named lock to prevent race conditions
        2. Find IP with least active servers (load balancing)
        3. Find available port on that IP
        4. Return (ip, port) or None if all slots full
        5. Release named lock

        Returns:
            Tuple[str, int]: (ip_address, port) if available
            None: If all 150 slots are occupied
        """
        try:
            # Acquire advisory lock
            self._acquire_lock()
            logger.debug(f"Acquired advisory lock {self.ADVISORY_LOCK_ID}")

            # Get IP with least servers (load balancing)
            ip_loads = self._get_ip_loads()
            target_ip = min(ip_loads, key=ip_loads.get)

            logger.info(f"Load balancing: {ip_loads}. Target IP: {target_ip}")

            # Find available port on target IP
            port = self._find_available_port(target_ip)

            if port:
                logger.info(f"Allocated slot: {target_ip}:{port}")
                return (target_ip, port)

            # If target IP full, try other IPs
            for ip in self.AVAILABLE_IPS:
                if ip != target_ip:
                    port = self._find_available_port(ip)
                    if port:
                        logger.info(f"Allocated slot (fallback): {ip}:{port}")
                        return (ip, port)

            # All slots full
            logger.warning(f"All {self.TOTAL_SLOTS} slots occupied!")
            return None

        finally:
            # Always release advisory lock
            self._release_lock()
            logger.debug(f"Released advisory lock {self.ADVISORY_LOCK_ID}")

    def _get_ip_loads(self) -> Dict[str, int]:
        """
        Get current server count per IP for load balancing.

        Only counts active servers (not deleted/expired).

        Returns:
            Dict[str, int]: IP address -> server count
        """
        loads = {ip: 0 for ip in self.AVAILABLE_IPS}

        # Query active server counts per IP
        result = (
            self.db.query(GameServer.ip_address, func.count(GameServer.id).label("count"))
            .filter(
                GameServer.ip_address.in_(self.AVAILABLE_IPS),
                GameServer.status.notin_([ServerStatus.DELETED, ServerStatus.EXPIRED]),
            )
            .group_by(GameServer.ip_address)
            .all()
        )

        # Update loads
        for ip, count in result:
            loads[ip] = count

        return loads

    def _find_available_port(self, ip: str) -> Optional[int]:
        """
        Find first available port on given IP.

        Args:
            ip: IP address to search

        Returns:
            int: Available port number
            None: If all ports on this IP are occupied
        """
        # Get all used ports on this IP
        used_ports_query = (
            self.db.query(GameServer.port)
            .filter(
                GameServer.ip_address == ip,
                GameServer.status.notin_([ServerStatus.DELETED, ServerStatus.EXPIRED]),
            )
            .all()
        )

        used_ports = {port[0] for port in used_ports_query}

        # Find first available port in range
        for port in range(self.PORT_RANGE_START, self.PORT_RANGE_END + 1):
            if port not in used_ports:
                return port

        return None

    def _acquire_lock(self):
        """
        Acquire MySQL named lock.

        Blocks until lock is available (timeout: 10 seconds).
        MySQL named locks are connection-scoped and automatically released on disconnect.
        """
        result = self.db.execute(
            text("SELECT GET_LOCK('port_pool_manager', 10)"),
        ).scalar()

        if result != 1:
            raise Exception("Failed to acquire port pool lock")

    def _release_lock(self):
        """
        Release MySQL named lock.

        Should always be called in finally block to ensure cleanup.
        """
        self.db.execute(text("SELECT RELEASE_LOCK('port_pool_manager')"))

    def release_slot(self, ip: str, port: int):
        """
        Mark slot as released (for manual cleanup/recycling).

        Note: Slots are automatically recycled when server status
        changes to DELETED or EXPIRED.

        Args:
            ip: IP address of slot
            port: Port number of slot
        """
        logger.info(f"Slot released: {ip}:{port}")
        # No action needed - allocation check excludes DELETED/EXPIRED

    def get_capacity_info(self) -> Dict:
        """
        Get current capacity information.

        Returns:
            Dict with total, used, available slots and per-IP breakdown
        """
        ip_loads = self._get_ip_loads()
        total_used = sum(ip_loads.values())

        return {
            "total_slots": self.TOTAL_SLOTS,
            "used_slots": total_used,
            "available_slots": self.TOTAL_SLOTS - total_used,
            "utilization_percent": round((total_used / self.TOTAL_SLOTS) * 100, 2),
            "ip_breakdown": [
                {
                    "ip": ip,
                    "used": count,
                    "available": self.PORTS_PER_IP - count,
                    "utilization_percent": round((count / self.PORTS_PER_IP) * 100, 2),
                }
                for ip, count in ip_loads.items()
            ],
        }
