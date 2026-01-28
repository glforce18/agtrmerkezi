"""
AGTR Merkezi - Alert & Notification Service
Proactive alerts for critical system events
"""

import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert delivery channels"""

    LOG = "log"
    EMAIL = "email"
    DISCORD = "discord"
    DATABASE = "database"


class AlertService:
    """
    Centralized alerting service for system events.

    Supports multiple channels: logs, email, Discord webhooks, database storage.
    """

    def __init__(self, db: Session):
        self.db = db

    async def send_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        server_id: Optional[int] = None,
        user_id: Optional[int] = None,
        channels: List[AlertChannel] = None,
    ):
        """
        Send alert to specified channels.

        Args:
            level: Alert severity
            title: Short alert title
            message: Detailed message
            server_id: Related server (optional)
            user_id: Related user (optional)
            channels: Delivery channels (defaults to LOG + DATABASE)
        """
        if channels is None:
            channels = [AlertChannel.LOG, AlertChannel.DATABASE]

        alert_data = {
            "level": level.value,
            "title": title,
            "message": message,
            "server_id": server_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Send to each channel
        for channel in channels:
            try:
                if channel == AlertChannel.LOG:
                    await self._send_to_log(level, title, message)
                elif channel == AlertChannel.EMAIL:
                    await self._send_to_email(alert_data)
                elif channel == AlertChannel.DISCORD:
                    await self._send_to_discord(alert_data)
                elif channel == AlertChannel.DATABASE:
                    await self._send_to_database(alert_data)
            except Exception as e:
                logger.error(f"Failed to send alert to {channel.value}: {e}")

    async def _send_to_log(self, level: AlertLevel, title: str, message: str):
        """Log alert"""
        log_message = f"[ALERT] {title}: {message}"

        if level == AlertLevel.CRITICAL or level == AlertLevel.ERROR:
            logger.error(log_message)
        elif level == AlertLevel.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)

    async def _send_to_email(self, alert_data: dict):
        """Send email alert (placeholder)"""
        # TODO: Implement email sending
        # from app.core.email import send_email
        # await send_email(...)

    async def _send_to_discord(self, alert_data: dict):
        """Send Discord webhook alert (placeholder)"""
        # TODO: Implement Discord webhook
        # import aiohttp
        # async with aiohttp.ClientSession() as session:
        #     await session.post(DISCORD_WEBHOOK_URL, json=payload)

    async def _send_to_database(self, alert_data: dict):
        """Store alert in database"""
        from app.models.database import SystemAlert

        try:
            alert = SystemAlert(
                level=alert_data["level"],
                title=alert_data["title"],
                message=alert_data["message"],
                server_id=alert_data.get("server_id"),
                user_id=alert_data.get("user_id"),
                created_at=datetime.utcnow(),
            )
            self.db.add(alert)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to store alert in database: {e}")

    # ==================== PREDEFINED ALERTS ====================

    async def alert_high_cpu(self, server_id: int, cpu_percent: float):
        """Alert for high CPU usage"""
        await self.send_alert(
            level=AlertLevel.WARNING,
            title=f"High CPU Usage - Server {server_id}",
            message=f"Server {server_id} CPU usage: {cpu_percent:.1f}%",
            server_id=server_id,
            channels=[AlertChannel.LOG, AlertChannel.DATABASE],
        )

    async def alert_high_memory(self, server_id: int, memory_mb: float):
        """Alert for high memory usage"""
        await self.send_alert(
            level=AlertLevel.WARNING,
            title=f"High Memory Usage - Server {server_id}",
            message=f"Server {server_id} memory usage: {memory_mb:.0f} MB",
            server_id=server_id,
            channels=[AlertChannel.LOG, AlertChannel.DATABASE],
        )

    async def alert_crash_storm(self, server_id: int, crash_count: int):
        """Alert for crash storm detection"""
        await self.send_alert(
            level=AlertLevel.ERROR,
            title=f"Crash Storm Detected - Server {server_id}",
            message=f"Server {server_id} crashed {crash_count} times in 10 minutes. Auto-restart disabled.",
            server_id=server_id,
            channels=[AlertChannel.LOG, AlertChannel.DATABASE, AlertChannel.EMAIL],
        )

    async def alert_port_pool_exhausted(self):
        """Alert when all ports are in use"""
        await self.send_alert(
            level=AlertLevel.CRITICAL,
            title="Port Pool Exhausted",
            message="All 150 server slots are in use. Cannot create new servers.",
            channels=[AlertChannel.LOG, AlertChannel.DATABASE, AlertChannel.EMAIL],
        )

    async def alert_installation_timeout(self, server_id: int):
        """Alert for installation timeout"""
        await self.send_alert(
            level=AlertLevel.ERROR,
            title=f"Installation Timeout - Server {server_id}",
            message=f"Server {server_id} installation exceeded 30-minute timeout.",
            server_id=server_id,
            channels=[AlertChannel.LOG, AlertChannel.DATABASE],
        )

    async def alert_redis_down(self):
        """Alert when Redis is unavailable"""
        await self.send_alert(
            level=AlertLevel.ERROR,
            title="Redis Connection Lost",
            message="Redis server is unavailable. Rate limiting using in-memory fallback.",
            channels=[AlertChannel.LOG, AlertChannel.DATABASE],
        )

    async def alert_database_slow_query(self, query: str, duration_ms: float):
        """Alert for slow database queries"""
        if duration_ms > 1000:  # > 1 second
            await self.send_alert(
                level=AlertLevel.WARNING,
                title="Slow Database Query",
                message=f"Query took {duration_ms:.0f}ms: {query[:100]}...",
                channels=[AlertChannel.LOG],
            )
