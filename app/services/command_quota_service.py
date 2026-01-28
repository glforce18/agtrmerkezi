"""
AGTR Merkezi v6.1 - Command Quota Service
Daily quotas for RCON commands
"""

import logging
from datetime import date
from typing import Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# Daily command quotas (commands per day)
COMMAND_DAILY_LIMITS = {
    "ban": 50,
    "kick": 200,
    "restart": 20,
    "changelevel": 50,
    "rcon_command": 500,  # Generic RCON commands
}


class CommandQuotaService:
    """
    Manage daily command quotas for users.

    Prevents abuse by limiting total daily usage of sensitive commands.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_quota(
        self, user_id: int, command_type: str, quota_date: date
    ) -> "CommandQuota":
        """
        Get existing quota record or create new one.

        Args:
            user_id: User ID
            command_type: Command type (ban, kick, restart, etc.)
            quota_date: Date for quota (usually today)

        Returns:
            CommandQuota instance
        """
        from app.models.database import CommandQuota

        quota = (
            self.db.query(CommandQuota)
            .filter(
                CommandQuota.user_id == user_id,
                CommandQuota.command_type == command_type,
                CommandQuota.quota_date == quota_date,
            )
            .first()
        )

        if not quota:
            quota = CommandQuota(
                user_id=user_id,
                command_type=command_type,
                usage_count=0,
                quota_date=quota_date,
            )
            self.db.add(quota)
            self.db.commit()
            self.db.refresh(quota)

        return quota

    def check_and_increment_quota(self, user_id: int, command_type: str) -> None:
        """
        Check if user has quota remaining and increment usage.

        Args:
            user_id: User ID
            command_type: Command type

        Raises:
            HTTPException: 429 if quota exceeded
        """
        if command_type not in COMMAND_DAILY_LIMITS:
            # Not a quota-limited command
            return

        today = date.today()
        limit = COMMAND_DAILY_LIMITS[command_type]

        # Get or create today's quota
        quota = self.get_or_create_quota(user_id, command_type, today)

        # Check limit
        if quota.usage_count >= limit:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Daily quota exceeded for {command_type}. "
                    f"Limit: {limit}/day. "
                    f"Used: {quota.usage_count}. "
                    f"Resets at midnight UTC."
                ),
                headers={"X-Daily-Limit": str(limit), "X-Daily-Used": str(quota.usage_count)},
            )

        # Increment usage
        quota.usage_count += 1
        self.db.commit()

        logger.debug(
            f"Command quota: user={user_id}, command={command_type}, "
            f"usage={quota.usage_count}/{limit}"
        )

    def get_quota_usage(self, user_id: int, command_type: str) -> Dict:
        """
        Get current quota usage for user and command.

        Args:
            user_id: User ID
            command_type: Command type

        Returns:
            Dict with limit, used, remaining, resets_at
        """
        if command_type not in COMMAND_DAILY_LIMITS:
            return {
                "command_type": command_type,
                "limited": False,
            }

        today = date.today()
        limit = COMMAND_DAILY_LIMITS[command_type]

        # Get today's quota
        quota = self.get_or_create_quota(user_id, command_type, today)

        return {
            "command_type": command_type,
            "limited": True,
            "daily_limit": limit,
            "used_today": quota.usage_count,
            "remaining": max(0, limit - quota.usage_count),
            "quota_date": today.isoformat(),
            "resets_at_utc": "00:00:00",
        }

    def get_all_quota_usage(self, user_id: int) -> Dict[str, Dict]:
        """
        Get quota usage for all command types.

        Args:
            user_id: User ID

        Returns:
            Dict mapping command_type to usage stats
        """
        result = {}

        for command_type in COMMAND_DAILY_LIMITS.keys():
            result[command_type] = self.get_quota_usage(user_id, command_type)

        return result

    def cleanup_old_quotas(self, days_to_keep: int = 30) -> int:
        """
        Delete quota records older than specified days.

        Args:
            days_to_keep: Number of days to keep

        Returns:
            Number of records deleted
        """
        from datetime import timedelta

        from app.models.database import CommandQuota

        cutoff_date = date.today() - timedelta(days=days_to_keep)

        deleted = self.db.query(CommandQuota).filter(CommandQuota.quota_date < cutoff_date).delete()

        self.db.commit()

        logger.info(f"Deleted {deleted} old command quota records (older than {cutoff_date})")

        return deleted
