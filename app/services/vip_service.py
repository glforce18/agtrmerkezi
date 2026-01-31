"""
AGTR Merkezi - VIP Management Service
Handles VIP members and users.ini VIP flag integration
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.database import VIPMember
from app.services.admin_service import AdminService

logger = logging.getLogger(__name__)


class VIPService:
    """Service for managing VIP members"""

    def __init__(self, db: Session):
        self.db = db
        self.admin_service = AdminService(db)

    def get_vip_members(self, server_id: int, include_expired: bool = False) -> List[VIPMember]:
        """Get VIP members for a server"""
        query = self.db.query(VIPMember).filter_by(server_id=server_id)

        if not include_expired:
            # Only active VIPs (is_active=True and not expired)
            query = query.filter(
                VIPMember.is_active == True,  # noqa: E712
                (VIPMember.expires_at.is_(None)) | (VIPMember.expires_at > datetime.now()),
            )

        return query.order_by(VIPMember.created_at.desc()).all()

    def add_vip(
        self,
        server_id: int,
        steam_id: str,
        player_name: str,
        vip_flags: str,
        added_by: int,
        expires_at: Optional[datetime] = None,
        password: Optional[str] = None,
    ) -> Optional[VIPMember]:
        """
        Add a VIP member

        Args:
            server_id: Server ID
            steam_id: Player Steam ID
            player_name: Player name
            vip_flags: AMXModX VIP flags (e.g., "abcdefghijklmnopqrstu")
            added_by: User ID who added VIP
            expires_at: Expiration datetime (None = permanent)
            password: Optional password for VIP

        Returns:
            VIPMember object or None if already exists
        """
        # Check if already exists
        existing = (
            self.db.query(VIPMember).filter_by(server_id=server_id, steam_id=steam_id).first()
        )

        if existing:
            logger.warning(f"VIP member {steam_id} already exists for server {server_id}")
            return None

        # Create VIP member
        vip = VIPMember(
            server_id=server_id,
            steam_id=steam_id,
            player_name=player_name,
            vip_flags=vip_flags,
            password=password,
            expires_at=expires_at,
            added_by=added_by,
        )
        self.db.add(vip)
        self.db.commit()

        # Sync to users.ini
        self.sync_vip_to_users_ini(server_id)

        logger.info(f"Added VIP member: {steam_id} with flags {vip_flags}")
        return vip

    def remove_vip(self, server_id: int, steam_id: str) -> bool:
        """Remove a VIP member"""
        vip = self.db.query(VIPMember).filter_by(server_id=server_id, steam_id=steam_id).first()

        if not vip:
            logger.warning(f"VIP member {steam_id} not found")
            return False

        self.db.delete(vip)
        self.db.commit()

        # Sync to users.ini
        self.sync_vip_to_users_ini(server_id)

        logger.info(f"Removed VIP member: {steam_id}")
        return True

    def update_vip(
        self,
        server_id: int,
        steam_id: str,
        vip_flags: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[VIPMember]:
        """Update VIP member details"""
        vip = self.db.query(VIPMember).filter_by(server_id=server_id, steam_id=steam_id).first()

        if not vip:
            return None

        if vip_flags is not None:
            vip.vip_flags = vip_flags
        if expires_at is not None:
            vip.expires_at = expires_at
        if is_active is not None:
            vip.is_active = is_active

        self.db.commit()

        # Sync to users.ini
        self.sync_vip_to_users_ini(server_id)

        logger.info(f"Updated VIP member: {steam_id}")
        return vip

    def check_vip_expiration(self, server_id: int) -> int:
        """
        Check and deactivate expired VIP members

        Returns:
            Number of VIPs expired
        """
        expired_vips = (
            self.db.query(VIPMember)
            .filter(
                VIPMember.server_id == server_id,
                VIPMember.is_active == True,  # noqa: E712
                VIPMember.expires_at.isnot(None),
                VIPMember.expires_at < datetime.now(),
            )
            .all()
        )

        for vip in expired_vips:
            vip.is_active = False

        if expired_vips:
            self.db.commit()
            self.sync_vip_to_users_ini(server_id)
            logger.info(f"Expired {len(expired_vips)} VIP members")

        return len(expired_vips)

    def sync_vip_to_users_ini(self, server_id: int) -> bool:
        """
        Sync VIP members to users.ini file

        This updates the users.ini file with all active VIP members
        """
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")

        # Get active VIP members
        active_vips = self.get_vip_members(server_id, include_expired=False)

        # Get existing admins from users.ini
        existing_admins = self.admin_service.parse_users_ini(server_path)

        # Filter out VIP entries (they'll be re-added from database)
        # VIP entries typically have "t" flag (reservation)
        non_vip_admins = [a for a in existing_admins if "t" not in a.get("flags", "")]

        # Add VIP members
        all_admins = non_vip_admins.copy()
        for vip in active_vips:
            all_admins.append(
                {
                    "steam_id": vip.steam_id,
                    "password": vip.password or "",
                    "flags": vip.vip_flags,
                    "connection_flags": "ce",  # Standard connection flags
                }
            )

        # Update users.ini
        success = self.admin_service.update_users_ini(server_path, all_admins)

        if success:
            logger.info(f"Synced {len(active_vips)} VIP members to users.ini")
        else:
            logger.error("Failed to sync VIP members to users.ini")

        return success

    def get_vip_stats(self, server_id: int) -> dict:
        """Get VIP statistics for a server"""
        all_vips = self.db.query(VIPMember).filter_by(server_id=server_id).all()

        active_count = sum(1 for vip in all_vips if vip.is_active)
        expired_count = sum(
            1 for vip in all_vips if vip.expires_at and vip.expires_at < datetime.now()
        )
        permanent_count = sum(1 for vip in all_vips if vip.expires_at is None and vip.is_active)

        return {
            "total_vips": len(all_vips),
            "active_vips": active_count,
            "expired_vips": expired_count,
            "permanent_vips": permanent_count,
        }
