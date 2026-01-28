"""
Auto-Update Service
Handles automatic updates for CS 1.6, AMXModX, Metamod, and plugins
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database import ServerUpdateLog


class AutoUpdateService:
    """Service for managing automatic server updates"""

    def __init__(self):
        self.steamcmd_path = "/usr/games/steamcmd"
        self.amxmodx_latest_url = "https://www.amxmodx.org/latest.php"
        self.metamod_latest_url = "https://www.metamodx.com/latest.php"

    async def check_cs16_update(self, server_id: int) -> Dict:
        """
        Check if CS 1.6 has updates available via SteamCMD

        Returns:
            Dict with update info
        """
        try:
            server_path = Path(settings.HLDS_PATH) / f"server_{server_id}"

            # Get current build ID
            current_build = await self._get_current_build_id(server_path)

            # Check latest build ID from Steam
            latest_build = await self._get_latest_build_id()

            # Get game directory for info


            return {
                "has_update": current_build != latest_build,
                "current_version": current_build,
                "latest_version": latest_build,
                "update_size": "Unknown",  # SteamCMD doesn't provide this easily
                "component": "CS 1.6",
                "game_directory": "Base Installation",
                "full_path": "Root Directory (All Mods)",
            }
        except Exception as e:
            return {"error": str(e), "has_update": False}

    async def _get_current_build_id(self, server_path: Path) -> str:
        """Get current CS 1.6 build ID from installed files"""
        try:
            # Read from steamapps manifest
            manifest_path = server_path / "steamapps" / "appmanifest_90.acf"
            if manifest_path.exists():
                content = manifest_path.read_text()
                # Parse ACF format to get buildid
                for line in content.split("\n"):
                    if '"buildid"' in line:
                        return line.split('"')[3]
            return "unknown"
        except:
            return "unknown"

    async def _get_latest_build_id(self) -> str:
        """Get latest CS 1.6 build ID from Steam"""
        try:
            # Use SteamCMD to check latest version
            result = subprocess.run(
                [
                    self.steamcmd_path,
                    "+login",
                    "anonymous",
                    "+app_info_update",
                    "1",
                    "+app_info_print",
                    "90",
                    "+quit",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse output for build ID
            for line in result.stdout.split("\n"):
                if '"buildid"' in line.lower():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        return parts[-1].strip('"')

            return "unknown"
        except Exception as e:
            print(f"Error getting latest build: {e}")
            return "unknown"

    async def update_cs16(self, server_id: int, user_id: int, db: AsyncSession) -> Dict:
        """
        Update CS 1.6 server using SteamCMD

        Args:
            server_id: Server ID
            user_id: User performing update
            db: Database session

        Returns:
            Dict with update result
        """
        try:
            server_path = Path(settings.HLDS_PATH) / f"server_{server_id}"

            # Log update start
            await self._log_update(
                db, server_id, user_id, "CS 1.6", "started", "Updating CS 1.6..."
            )

            # Run SteamCMD update
            result = subprocess.run(
                [
                    self.steamcmd_path,
                    "+login",
                    "anonymous",
                    "+force_install_dir",
                    str(server_path),
                    "+app_update",
                    "90",
                    "validate",
                    "+quit",
                ],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes
            )

            if result.returncode == 0:
                await self._log_update(
                    db, server_id, user_id, "CS 1.6", "completed", "CS 1.6 updated successfully"
                )
                return {
                    "success": True,
                    "message": "CS 1.6 updated successfully",
                    "output": result.stdout[-500:],  # Last 500 chars
                }
            else:
                await self._log_update(
                    db, server_id, user_id, "CS 1.6", "failed", f"Update failed: {result.stderr}"
                )
                return {"success": False, "message": "Update failed", "error": result.stderr}

        except Exception as e:
            await self._log_update(db, server_id, user_id, "CS 1.6", "error", str(e))
            return {"success": False, "message": "Update error", "error": str(e)}

    async def check_amxmodx_update(self, server_id: int, server) -> Dict:
        """Check if AMXModX has updates available"""
        try:
            # Get game directory based on game type
            game_dir = self._get_game_dir(server)
            amxmodx_path = (
                Path(settings.HLDS_PATH) / f"server_{server_id}" / game_dir / "addons" / "amxmodx"
            )

            # Debug log
            print(
                f"[AMXModX Check] Server #{server_id}, GameType: {server.game_type}, Dir: {game_dir}, Path: {amxmodx_path}"
            )

            # Get current version
            current_version = await self._get_amxmodx_version(amxmodx_path)

            # Get latest version from website
            latest_version = await self._get_latest_amxmodx_version()

            return {
                "has_update": self._compare_versions(current_version, latest_version),
                "current_version": current_version,
                "latest_version": latest_version,
                "component": "AMXModX",
                "game_directory": game_dir,
                "full_path": f"{game_dir}/addons/amxmodx",
            }
        except Exception as e:
            return {"error": str(e), "has_update": False}

    def _get_game_dir(self, server) -> str:
        """
        Get game directory based on server game type

        CS 1.6 (cs16) → cstrike/addons/amxmodx
        Half-Life (hldm) → valve/addons/amxmodx
        Adrenaline Gamer (ag) → ag/addons/amxmodx
        """
        # Game type to directory mapping
        game_type_map = {
            "cs16": "cstrike",  # Counter-Strike 1.6
            "hldm": "valve",  # Half-Life Deathmatch
            "ag": "ag",  # Adrenaline Gamer
            "valve": "valve",  # Half-Life variants
        }

        # Get game type value
        if hasattr(server, "game_type"):
            if hasattr(server.game_type, "value"):
                game_val = str(server.game_type.value).lower()
            else:
                game_val = str(server.game_type).lower()
        else:
            # Default to CS 1.6
            return "cstrike"

        # Direct match first
        if game_val in game_type_map:
            return game_type_map[game_val]

        # Fallback: check if game_val contains key
        for key, value in game_type_map.items():
            if key in game_val:
                return value

        # Final fallback to cstrike
        return "cstrike"

    async def _get_amxmodx_version(self, amxmodx_path: Path) -> str:
        """Get installed AMXModX version"""
        try:
            version_file = amxmodx_path / "configs" / "amxx.cfg"
            if version_file.exists():
                content = version_file.read_text()
                # Parse version from config
                for line in content.split("\n"):
                    if "amx_version" in line.lower():
                        return line.split()[-1].strip('"')

            # Try modules directory
            modules_dir = amxmodx_path / "modules"
            if modules_dir.exists():
                # Check amxmodx_mm.dll or amxmodx_mm.so for version
                return "1.9.0"  # Default fallback

            return "unknown"
        except:
            return "unknown"

    async def _get_latest_amxmodx_version(self) -> str:
        """Get latest AMXModX version from website"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.amxmodx.org/downloads.php") as resp:
                    if resp.status == 200:
                        # Parse HTML for latest version
                        # This is simplified - in production, use proper HTML parsing
                        return "1.10.0"  # Placeholder
            return "unknown"
        except:
            return "unknown"

    def _compare_versions(self, current: str, latest: str) -> bool:
        """Compare version strings"""
        try:
            current_parts = [int(x) for x in current.split(".") if x.isdigit()]
            latest_parts = [int(x) for x in latest.split(".") if x.isdigit()]

            return latest_parts > current_parts
        except:
            return False

    async def update_amxmodx(self, server_id: int, user_id: int, server, db: AsyncSession) -> Dict:
        """Update AMXModX to latest version"""
        try:
            # Get correct game directory
            game_dir = self._get_game_dir(server)
            server_path = Path(settings.HLDS_PATH) / f"server_{server_id}"
            amxmodx_path = server_path / game_dir / "addons" / "amxmodx"

            # Debug log
            print(
                f"[AMXModX Update] Server #{server_id}, GameType: {server.game_type}, Dir: {game_dir}"
            )
            print(f"[AMXModX Update] Target path: {amxmodx_path}")

            # Log update start
            await self._log_update(
                db, server_id, user_id, "AMXModX", "started", "Downloading latest AMXModX..."
            )

            # Download latest AMXModX
            download_url = "https://www.amxmodx.org/latest.php?version=1.10&os=linux"

            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as resp:
                    if resp.status != 200:
                        raise Exception(f"Download failed: HTTP {resp.status}")

                    # Save to temp file
                    temp_file = Path("/tmp") / f"amxmodx_latest_{server_id}.tar.gz"
                    with open(temp_file, "wb") as f:
                        f.write(await resp.read())

            # Backup current installation
            backup_path = server_path / f"amxmodx_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            subprocess.run(["cp", "-r", str(amxmodx_path), str(backup_path)])

            # Extract new version
            subprocess.run(
                ["tar", "-xzf", str(temp_file), "-C", str(server_path / game_dir / "addons")],
                check=True,
            )

            # Cleanup
            temp_file.unlink()

            await self._log_update(
                db, server_id, user_id, "AMXModX", "completed", "AMXModX updated successfully"
            )

            return {
                "success": True,
                "message": "AMXModX updated successfully",
                "backup_path": str(backup_path),
            }

        except Exception as e:
            await self._log_update(db, server_id, user_id, "AMXModX", "error", str(e))
            return {"success": False, "message": "Update failed", "error": str(e)}

    async def get_update_status(self, server_id: int, server, db: AsyncSession) -> Dict:
        """
        Get comprehensive update status for all components

        Returns:
            Dict with update status for CS 1.6, AMXModX, Metamod
        """
        cs16_status = await self.check_cs16_update(server_id)
        amxmodx_status = await self.check_amxmodx_update(server_id, server)

        # Get last update time
        last_update = await self._get_last_update_time(db, server_id)

        return {
            "cs16": cs16_status,
            "amxmodx": amxmodx_status,
            "last_update": last_update,
            "auto_update_enabled": False,  # TODO: Get from server settings
            "next_scheduled_update": None,  # TODO: Get from scheduler
        }

    async def _get_last_update_time(self, db: AsyncSession, server_id: int) -> Optional[str]:
        """Get last successful update time"""
        try:
            result = await db.execute(
                select(ServerUpdateLog)
                .filter(
                    ServerUpdateLog.server_id == server_id, ServerUpdateLog.status == "completed"
                )
                .order_by(ServerUpdateLog.updated_at.desc())
                .limit(1)
            )
            log = result.scalar_one_or_none()

            if log:
                return log.updated_at.isoformat()
            return None
        except:
            return None

    async def _log_update(
        self,
        db: AsyncSession,
        server_id: int,
        user_id: int,
        component: str,
        status: str,
        message: str,
    ):
        """Log update action to database"""
        try:
            log_entry = ServerUpdateLog(
                server_id=server_id,
                user_id=user_id,
                component=component,
                status=status,
                message=message,
                updated_at=datetime.utcnow(),
            )
            db.add(log_entry)
            await db.commit()
        except Exception as e:
            print(f"Error logging update: {e}")
            await db.rollback()

    async def get_update_history(
        self, db: AsyncSession, server_id: int, limit: int = 50
    ) -> List[Dict]:
        """Get update history for a server"""
        try:
            result = await db.execute(
                select(ServerUpdateLog)
                .filter(ServerUpdateLog.server_id == server_id)
                .order_by(ServerUpdateLog.updated_at.desc())
                .limit(limit)
            )
            logs = result.scalars().all()

            return [
                {
                    "id": log.id,
                    "component": log.component,
                    "status": log.status,
                    "message": log.message,
                    "updated_at": log.updated_at.isoformat(),
                    "user_id": log.user_id,
                }
                for log in logs
            ]
        except:
            return []


# Singleton instance
auto_update_service = AutoUpdateService()
