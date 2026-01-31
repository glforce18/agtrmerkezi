"""
AGTR Merkezi - Admin Management Service
Handles users.ini parsing, admin flags, ban management
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.database import PlayerActionLog

logger = logging.getLogger(__name__)


class AdminService:
    """Service for managing server admins and bans"""

    def __init__(self, db: Session):
        self.db = db

    # =========================
    # users.ini Management (Admins)
    # =========================

    def parse_users_ini(self, server_path: Path) -> List[Dict[str, str]]:
        """
        Parse users.ini file to get admin list

        Returns list of dicts with keys: steam_id, password, flags, connection_flags
        """
        users_path = server_path / "valve" / "addons" / "amxmodx" / "configs" / "users.ini"
        admins = []

        try:
            if not users_path.exists():
                logger.warning(f"users.ini not found: {users_path}")
                return admins

            with open(users_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith(";") or line.startswith("//"):
                        continue

                    # Format: "STEAM_ID" "password" "flags" "connection_flags"
                    # Example: "STEAM_ID_LAN" "" "abcdefghijklmnopqrstu" "ce"
                    match = re.match(r'"([^"]+)"\s+"([^"]*)"\s+"([^"]+)"(?:\s+"([^"]*)")?', line)
                    if match:
                        steam_id, password, flags, conn_flags = match.groups()
                        admins.append(
                            {
                                "steam_id": steam_id,
                                "password": password or "",
                                "flags": flags,
                                "connection_flags": conn_flags or "",
                            }
                        )

            logger.info(f"Parsed {len(admins)} admins from users.ini")
            return admins

        except Exception as e:
            logger.error(f"Failed to parse users.ini: {e}")
            return []

    def update_users_ini(self, server_path: Path, admins: List[Dict[str, str]]) -> bool:
        """
        Update users.ini with new admin list

        Args:
            server_path: Path to server directory
            admins: List of dicts with steam_id, password, flags, connection_flags
        """
        users_path = server_path / "valve" / "addons" / "amxmodx" / "configs" / "users.ini"

        try:
            # Create backup
            if users_path.exists():
                backup_path = users_path.with_suffix(".ini.bak")
                import shutil

                shutil.copy2(users_path, backup_path)

            # Write new users.ini
            with open(users_path, "w", encoding="utf-8") as f:
                # Write header
                f.write("; AMX Mod X - Users Configuration\n")
                f.write('; Format: "steam_id" "password" "access_flags" "connection_flags"\n')
                f.write("; Access flags: a-z (a=immunity, b=reservation, c=kick, d=ban, etc.)\n")
                f.write(";\n\n")

                # Write admins
                for admin in admins:
                    steam_id = admin.get("steam_id", "")
                    password = admin.get("password", "")
                    flags = admin.get("flags", "")
                    conn_flags = admin.get("connection_flags", "ce")

                    f.write(f'"{steam_id}" "{password}" "{flags}" "{conn_flags}"\n')

            logger.info(f"Updated users.ini with {len(admins)} admins")
            return True

        except Exception as e:
            logger.error(f"Failed to update users.ini: {e}")
            return False

    def add_admin(
        self,
        server_path: Path,
        steam_id: str,
        flags: str = "abcdefghijklmnopqrstu",
        password: str = "",
        connection_flags: str = "ce",
    ) -> bool:
        """Add a new admin to users.ini"""
        admins = self.parse_users_ini(server_path)

        # Check if admin already exists
        for admin in admins:
            if admin["steam_id"] == steam_id:
                logger.warning(f"Admin {steam_id} already exists")
                return False

        # Add new admin
        admins.append(
            {
                "steam_id": steam_id,
                "password": password,
                "flags": flags,
                "connection_flags": connection_flags,
            }
        )

        return self.update_users_ini(server_path, admins)

    def remove_admin(self, server_path: Path, steam_id: str) -> bool:
        """Remove an admin from users.ini"""
        admins = self.parse_users_ini(server_path)
        original_count = len(admins)

        # Remove admin
        admins = [a for a in admins if a["steam_id"] != steam_id]

        if len(admins) == original_count:
            logger.warning(f"Admin {steam_id} not found")
            return False

        return self.update_users_ini(server_path, admins)

    # =========================
    # banned.cfg Management
    # =========================

    def parse_banned_cfg(self, server_path: Path) -> List[Dict[str, str]]:
        """Parse banned.cfg to get ban list"""
        banned_path = server_path / "valve" / "banned.cfg"
        bans = []

        try:
            if not banned_path.exists():
                return bans

            with open(banned_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("//"):
                        continue

                    # Format: addip 0 "IP_ADDRESS"
                    # Format: banid 0 "STEAM_ID"
                    if line.startswith("addip"):
                        match = re.match(r'addip\s+(\d+)\s+"?([^"]+)"?', line)
                        if match:
                            duration, ip = match.groups()
                            bans.append({"type": "ip", "value": ip, "duration": duration})
                    elif line.startswith("banid"):
                        match = re.match(r'banid\s+(\d+)\s+"?([^"]+)"?', line)
                        if match:
                            duration, steam_id = match.groups()
                            bans.append(
                                {"type": "steam_id", "value": steam_id, "duration": duration}
                            )

            logger.info(f"Parsed {len(bans)} bans from banned.cfg")
            return bans

        except Exception as e:
            logger.error(f"Failed to parse banned.cfg: {e}")
            return []

    def add_ban(self, server_path: Path, ban_type: str, value: str, duration: int = 0) -> bool:
        """
        Add a ban to banned.cfg

        Args:
            ban_type: "ip" or "steam_id"
            value: IP address or Steam ID
            duration: Ban duration in minutes (0 = permanent)
        """
        banned_path = server_path / "valve" / "banned.cfg"

        try:
            # Read existing bans
            bans = self.parse_banned_cfg(server_path)

            # Check if already banned
            for ban in bans:
                if ban["type"] == ban_type and ban["value"] == value:
                    logger.warning(f"{ban_type} {value} already banned")
                    return False

            # Append new ban
            with open(banned_path, "a", encoding="utf-8") as f:
                if ban_type == "ip":
                    f.write(f'addip {duration} "{value}"\n')
                else:  # steam_id
                    f.write(f'banid {duration} "{value}"\n')

            logger.info(f"Added {ban_type} ban: {value}")
            return True

        except Exception as e:
            logger.error(f"Failed to add ban: {e}")
            return False

    def remove_ban(self, server_path: Path, ban_type: str, value: str) -> bool:
        """Remove a ban from banned.cfg"""
        banned_path = server_path / "valve" / "banned.cfg"

        try:
            if not banned_path.exists():
                return False

            # Read and filter bans
            with open(banned_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            updated_lines = []
            removed = False

            for line in lines:
                stripped = line.strip()

                # Check if this is the ban to remove
                if ban_type == "ip" and stripped.startswith("addip"):
                    if value not in stripped:
                        updated_lines.append(line)
                    else:
                        removed = True
                elif ban_type == "steam_id" and stripped.startswith("banid"):
                    if value not in stripped:
                        updated_lines.append(line)
                    else:
                        removed = True
                else:
                    updated_lines.append(line)

            if removed:
                with open(banned_path, "w", encoding="utf-8") as f:
                    f.writelines(updated_lines)
                logger.info(f"Removed {ban_type} ban: {value}")
                return True
            else:
                logger.warning(f"Ban not found: {ban_type} {value}")
                return False

        except Exception as e:
            logger.error(f"Failed to remove ban: {e}")
            return False

    # =========================
    # Player Action Logging
    # =========================

    def log_action(
        self,
        server_id: int,
        admin_id: Optional[int],
        action_type: str,
        target_steam_id: Optional[str] = None,
        target_name: Optional[str] = None,
        reason: Optional[str] = None,
        duration_minutes: Optional[int] = None,
    ) -> PlayerActionLog:
        """Log a player action (kick, ban, slay, etc.)"""
        log = PlayerActionLog(
            server_id=server_id,
            admin_id=admin_id,
            target_steam_id=target_steam_id,
            target_name=target_name,
            action_type=action_type,
            reason=reason,
            duration_minutes=duration_minutes,
        )
        self.db.add(log)
        self.db.commit()
        return log

    def get_action_logs(
        self, server_id: int, limit: int = 100, action_type: Optional[str] = None
    ) -> List[PlayerActionLog]:
        """Get player action logs"""
        query = self.db.query(PlayerActionLog).filter_by(server_id=server_id)

        if action_type:
            query = query.filter_by(action_type=action_type)

        return query.order_by(PlayerActionLog.created_at.desc()).limit(limit).all()
