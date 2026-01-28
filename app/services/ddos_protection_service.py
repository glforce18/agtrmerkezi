"""
DDoS Protection Service
Monitors traffic, detects attacks, and provides mitigation
"""

import asyncio
import subprocess
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import DDoSAttackLog, IPBlockList


class DDoSProtectionService:
    """Service for DDoS detection and mitigation"""

    def __init__(self):
        self.traffic_buffer = defaultdict(lambda: deque(maxlen=60))  # Last 60 seconds
        self.blocked_ips = set()
        self.attack_threshold = 1000  # Packets per second
        self.connection_threshold = 100  # Connections per IP

    async def get_traffic_stats(self, server_id: int, server) -> Dict:
        """
        Get real-time traffic statistics for a server

        Returns:
            Dict with traffic metrics
        """
        try:
            ip = server.ip_address
            port = server.port

            # Get network statistics using iptables
            stats = await self._get_iptables_stats(ip, port)

            # Get connection count
            connections = await self._get_connection_count(port)

            # Detect if under attack
            is_attack = await self._detect_attack(stats, connections)

            return {
                "packets_per_second": stats.get("pps", 0),
                "bytes_per_second": stats.get("bps", 0),
                "connection_count": connections,
                "is_under_attack": is_attack,
                "blocked_ips_count": len(self.blocked_ips),
                "traffic_level": self._get_traffic_level(stats.get("pps", 0)),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {"error": str(e), "is_under_attack": False}

    async def _get_iptables_stats(self, ip: str, port: int) -> Dict:
        """Get traffic stats from iptables"""
        try:
            # Use iptables to get packet/byte counters (without shell=True)
            iptables_proc = subprocess.Popen(
                ["sudo", "iptables", "-L", "INPUT", "-v", "-n", "-x"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            grep_proc = subprocess.Popen(
                ["grep", f"dpt:{port}"],
                stdin=iptables_proc.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            iptables_proc.stdout.close()
            output, _ = grep_proc.communicate(timeout=5)

            # Parse output
            # Format: pkts bytes target prot opt in out source destination
            if output:
                parts = output.strip().split()
                if len(parts) >= 2:
                    return {
                        "packets": int(parts[0]),
                        "bytes": int(parts[1]),
                        "pps": int(parts[0]) // 60,  # Rough estimate
                        "bps": int(parts[1]) // 60,
                    }

            return {"pps": 0, "bps": 0}
        except Exception as e:
            print(f"Error getting iptables stats: {e}")
            return {"pps": 0, "bps": 0}

    async def _get_connection_count(self, port: int) -> int:
        """Get active connection count for a port"""
        try:
            # Chain commands without shell=True using Popen
            netstat_proc = subprocess.Popen(
                ["netstat", "-an"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            grep_proc = subprocess.Popen(
                ["grep", f":{port}"],
                stdin=netstat_proc.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            netstat_proc.stdout.close()
            grep_output, _ = grep_proc.communicate(timeout=5)

            # Count lines
            line_count = len(grep_output.strip().split('\n')) if grep_output.strip() else 0
            return line_count
        except:
            return 0

    async def _detect_attack(self, stats: Dict, connections: int) -> bool:
        """Detect if server is under DDoS attack"""
        pps = stats.get("pps", 0)

        # Simple heuristics
        if pps > self.attack_threshold:
            return True

        if connections > self.connection_threshold:
            return True

        return False

    def _get_traffic_level(self, pps: int) -> str:
        """Get traffic level classification"""
        if pps < 100:
            return "low"
        elif pps < 500:
            return "normal"
        elif pps < 1000:
            return "high"
        else:
            return "critical"

    async def block_ip(
        self,
        ip: str,
        reason: str,
        duration: int,  # seconds, 0 = permanent
        user_id: int,
        db: AsyncSession,
    ) -> Dict:
        """
        Block an IP address using iptables

        Args:
            ip: IP address to block
            reason: Reason for blocking
            duration: Block duration in seconds (0 = permanent)
            user_id: User who initiated block
            db: Database session

        Returns:
            Dict with result
        """
        try:
            # Add to iptables
            result = subprocess.run(
                ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                # Add to blocked set
                self.blocked_ips.add(ip)

                # Log to database
                block_entry = IPBlockList(
                    ip_address=ip,
                    reason=reason,
                    blocked_by=user_id,
                    blocked_at=datetime.utcnow(),
                    expires_at=(
                        datetime.utcnow() + timedelta(seconds=duration) if duration > 0 else None
                    ),
                    is_active=True,
                )
                db.add(block_entry)
                await db.commit()

                # Schedule unblock if temporary
                if duration > 0:
                    asyncio.create_task(self._schedule_unblock(ip, duration, db))

                return {
                    "success": True,
                    "message": f"IP {ip} blocked successfully",
                    "duration": "permanent" if duration == 0 else f"{duration}s",
                }
            else:
                return {"success": False, "message": "Failed to block IP", "error": result.stderr}

        except Exception as e:
            return {"success": False, "message": "Error blocking IP", "error": str(e)}

    async def unblock_ip(self, ip: str, db: AsyncSession) -> Dict:
        """Unblock an IP address"""
        try:
            # Remove from iptables
            result = subprocess.run(
                ["sudo", "iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                # Remove from blocked set
                self.blocked_ips.discard(ip)

                # Update database
                result = await db.execute(
                    select(IPBlockList).filter(
                        and_(IPBlockList.ip_address == ip, IPBlockList.is_active == True)
                    )
                )
                block = result.scalar_one_or_none()

                if block:
                    block.is_active = False
                    block.unblocked_at = datetime.utcnow()
                    await db.commit()

                return {"success": True, "message": f"IP {ip} unblocked successfully"}
            else:
                return {"success": False, "message": "Failed to unblock IP", "error": result.stderr}

        except Exception as e:
            return {"success": False, "message": "Error unblocking IP", "error": str(e)}

    async def _schedule_unblock(self, ip: str, duration: int, db: AsyncSession):
        """Schedule automatic unblock after duration"""
        await asyncio.sleep(duration)
        await self.unblock_ip(ip, db)

    async def get_blocked_ips(self, db: AsyncSession, active_only: bool = True) -> List[Dict]:
        """Get list of blocked IPs"""
        try:
            query = select(IPBlockList).order_by(IPBlockList.blocked_at.desc())

            if active_only:
                query = query.filter(IPBlockList.is_active == True)

            result = await db.execute(query.limit(100))
            blocks = result.scalars().all()

            return [
                {
                    "id": block.id,
                    "ip_address": block.ip_address,
                    "reason": block.reason,
                    "blocked_at": block.blocked_at.isoformat(),
                    "expires_at": block.expires_at.isoformat() if block.expires_at else None,
                    "is_active": block.is_active,
                    "blocked_by": block.blocked_by,
                }
                for block in blocks
            ]
        except:
            return []

    async def log_attack(
        self,
        server_id: int,
        attack_type: str,
        peak_pps: int,
        peak_gbps: float,
        duration: int,
        blocked_ips_count: int,
        db: AsyncSession,
    ):
        """Log DDoS attack to database"""
        try:
            attack_log = DDoSAttackLog(
                server_id=server_id,
                attack_type=attack_type,
                peak_packets_per_second=peak_pps,
                peak_gbps=peak_gbps,
                duration_seconds=duration,
                blocked_ips_count=blocked_ips_count,
                detected_at=datetime.utcnow(),
                mitigated=True,
            )
            db.add(attack_log)
            await db.commit()
        except Exception as e:
            print(f"Error logging attack: {e}")
            await db.rollback()

    async def get_attack_history(
        self, db: AsyncSession, server_id: Optional[int] = None, limit: int = 50
    ) -> List[Dict]:
        """Get DDoS attack history"""
        try:
            query = select(DDoSAttackLog).order_by(DDoSAttackLog.detected_at.desc())

            if server_id:
                query = query.filter(DDoSAttackLog.server_id == server_id)

            result = await db.execute(query.limit(limit))
            attacks = result.scalars().all()

            return [
                {
                    "id": attack.id,
                    "server_id": attack.server_id,
                    "attack_type": attack.attack_type,
                    "peak_pps": attack.peak_packets_per_second,
                    "peak_gbps": attack.peak_gbps,
                    "duration": attack.duration_seconds,
                    "blocked_ips": attack.blocked_ips_count,
                    "detected_at": attack.detected_at.isoformat(),
                    "mitigated": attack.mitigated,
                }
                for attack in attacks
            ]
        except:
            return []

    async def get_protection_status(self, server_id: int, server, db: AsyncSession) -> Dict:
        """
        Get comprehensive DDoS protection status

        Returns:
            Dict with protection status and statistics
        """
        try:
            # Get current traffic
            traffic = await self.get_traffic_stats(server_id, server)

            # Get blocked IPs
            blocked_ips = await self.get_blocked_ips(db, active_only=True)

            # Get recent attacks
            recent_attacks = await self.get_attack_history(db, server_id, limit=10)

            # Calculate stats
            total_attacks = len(recent_attacks)
            last_attack = recent_attacks[0] if recent_attacks else None

            return {
                "enabled": True,
                "current_traffic": traffic,
                "blocked_ips_count": len(blocked_ips),
                "total_attacks_24h": total_attacks,
                "last_attack": last_attack,
                "protection_level": "high",  # TODO: Make configurable
                "auto_mitigation": True,
            }
        except Exception as e:
            return {"error": str(e), "enabled": False}


# Singleton instance
ddos_protection_service = DDoSProtectionService()
