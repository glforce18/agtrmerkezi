"""
AGTR Merkezi v6.1 - Respawn Storm Detection
Detect and prevent server crash loops (respawn storms)
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.database import GameServer, ServerStatus

logger = logging.getLogger(__name__)


class RespawnMonitor:
    """
    Monitor server crashes and prevent respawn storms.

    Respawn storm: Multiple crashes in short time period, usually indicating
    configuration issues or resource problems.
    """

    # Storm detection thresholds
    MAX_CRASHES_IN_WINDOW = 5
    CRASH_WINDOW_MINUTES = 10

    # Exponential backoff config
    INITIAL_BACKOFF_SECONDS = 2
    MAX_BACKOFF_SECONDS = 300  # 5 minutes max

    def __init__(self, db: Session):
        self.db = db

    def is_in_backoff_period(self, server: GameServer) -> bool:
        """
        Check if server is in exponential backoff period.

        Args:
            server: GameServer instance

        Returns:
            True if in backoff, False otherwise
        """
        if not server.restart_backoff_until:
            return False

        now = datetime.utcnow()
        return now < server.restart_backoff_until

    def is_storm_detected(self, server: GameServer) -> bool:
        """
        Check if crash storm is detected.

        Storm = 5+ crashes in 10 minutes

        Args:
            server: GameServer instance

        Returns:
            True if storm detected
        """
        if not server.last_crash:
            return False

        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.CRASH_WINDOW_MINUTES)

        # Check if last crash was within window
        if server.last_crash < window_start:
            # Old crash, reset counter
            server.crash_count = 0
            self.db.commit()
            return False

        # Check crash count
        return server.crash_count >= self.MAX_CRASHES_IN_WINDOW

    def calculate_backoff(self, crash_count: int) -> int:
        """
        Calculate exponential backoff duration in seconds.

        Backoff = min(2^crash_count, MAX_BACKOFF_SECONDS)

        Args:
            crash_count: Number of crashes

        Returns:
            Backoff duration in seconds
        """
        backoff = self.INITIAL_BACKOFF_SECONDS * (2 ** (crash_count - 1))
        return min(backoff, self.MAX_BACKOFF_SECONDS)

    async def handle_server_crash(
        self, server: GameServer, error_message: Optional[str] = None
    ) -> bool:
        """
        Handle server crash and determine if restart should proceed.

        Args:
            server: GameServer instance
            error_message: Optional error message

        Returns:
            True if restart allowed, False if blocked
        """
        now = datetime.utcnow()

        # Update crash tracking
        server.last_crash = now
        server.status = ServerStatus.STOPPED

        # Check if this is within crash window
        window_start = now - timedelta(minutes=self.CRASH_WINDOW_MINUTES)

        if server.last_crash and server.last_crash > window_start:
            # Within window, increment counter
            server.crash_count += 1
        else:
            # Outside window, reset
            server.crash_count = 1

        self.db.commit()

        # Check for storm
        if self.is_storm_detected(server):
            logger.error(
                f"CRASH STORM DETECTED: Server {server.id} ({server.name}) "
                f"crashed {server.crash_count} times in {self.CRASH_WINDOW_MINUTES} minutes"
            )

            # Disable auto-restart
            server.auto_restart = False
            server.restart_backoff_until = None  # Clear backoff, manual restart required
            self.db.commit()

            # TODO: Send notification to owner
            await self._notify_owner_storm_detected(server)

            return False

        # Apply exponential backoff
        backoff_seconds = self.calculate_backoff(server.crash_count)
        server.restart_backoff_until = now + timedelta(seconds=backoff_seconds)
        self.db.commit()

        logger.warning(
            f"Server {server.id} ({server.name}) crashed (count: {server.crash_count}). "
            f"Backoff: {backoff_seconds}s"
        )

        # Check if auto-restart is enabled
        if not server.auto_restart:
            logger.info(f"Auto-restart disabled for server {server.id}")
            return False

        return True

    def reset_crash_tracking(self, server: GameServer):
        """
        Reset crash tracking for server.

        Call this after successful start.

        Args:
            server: GameServer instance
        """
        server.crash_count = 0
        server.restart_backoff_until = None
        self.db.commit()

        logger.info(f"Crash tracking reset for server {server.id}")

    def re_enable_auto_restart(self, server: GameServer) -> bool:
        """
        Manually re-enable auto-restart after storm.

        Args:
            server: GameServer instance

        Returns:
            True if re-enabled, False if storm still active
        """
        # Check if storm has cooled down
        if self.is_storm_detected(server):
            logger.warning(
                f"Cannot re-enable auto-restart for server {server.id}: "
                f"Storm still active ({server.crash_count} crashes)"
            )
            return False

        # Reset and re-enable
        server.auto_restart = True
        server.crash_count = 0
        server.restart_backoff_until = None
        self.db.commit()

        logger.info(f"Auto-restart re-enabled for server {server.id}")
        return True

    async def _notify_owner_storm_detected(self, server: GameServer):
        """
        Notify server owner that crash storm detected.

        Args:
            server: GameServer instance
        """
        try:
            from app.models.database import Notification, User

            owner = self.db.query(User).filter(User.id == server.owner_id).first()

            if not owner:
                return

            notification = Notification(
                user_id=owner.id,
                title="🔥 Crash Storm Detected",
                message=(
                    f"Server '{server.name}' crashed {server.crash_count} times "
                    f"in {self.CRASH_WINDOW_MINUTES} minutes. Auto-restart has been disabled "
                    f"to prevent further issues. Please check server configuration and logs."
                ),
                type="error",
                is_read=False,
                created_at=datetime.utcnow(),
            )

            self.db.add(notification)
            self.db.commit()

            logger.info(f"Crash storm notification sent to user {owner.id}")

        except Exception as e:
            logger.error(f"Failed to send crash storm notification: {e}")

    def get_crash_stats(self, server: GameServer) -> dict:
        """
        Get crash statistics for server.

        Args:
            server: GameServer instance

        Returns:
            Dict with crash stats
        """
        storm_detected = self.is_storm_detected(server)
        in_backoff = self.is_in_backoff_period(server)

        backoff_remaining = None
        if in_backoff and server.restart_backoff_until:
            backoff_remaining = int(
                (server.restart_backoff_until - datetime.utcnow()).total_seconds()
            )

        return {
            "crash_count": server.crash_count,
            "last_crash": server.last_crash.isoformat() if server.last_crash else None,
            "storm_detected": storm_detected,
            "auto_restart_enabled": server.auto_restart,
            "in_backoff": in_backoff,
            "backoff_remaining_seconds": backoff_remaining,
            "restart_allowed": not in_backoff and server.auto_restart and not storm_detected,
        }
