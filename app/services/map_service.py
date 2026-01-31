"""
AGTR Merkezi - Map Management Service
Handles custom map uploads, map library, voting, and rotation schedules
"""

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.database import CustomMap, GameServer, MapRotationSchedule, MapVote

logger = logging.getLogger(__name__)


class MapService:
    """Service for managing maps"""

    def __init__(self, db: Session):
        self.db = db

    # =========================
    # Map Library
    # =========================

    def get_all_maps(self, server_id: int) -> List[Dict]:
        """
        Get all maps (base maps + custom maps) for a server

        Returns:
            List of dicts with map metadata
        """
        server = self.db.query(GameServer).filter_by(id=server_id).first()
        if not server:
            return []

        server_path = Path(f"/home/gameservers/servers/server_{server_id}")
        maps_path = server_path / "valve" / "maps"

        all_maps = []

        # Get all .bsp files
        if maps_path.exists():
            for bsp_file in maps_path.glob("*.bsp"):
                map_name = bsp_file.stem

                # Check if it's a custom map in database
                custom_map = (
                    self.db.query(CustomMap)
                    .filter_by(server_id=server_id, map_name=map_name)
                    .first()
                )

                if custom_map:
                    all_maps.append(
                        {
                            "name": map_name,
                            "display_name": custom_map.display_name or map_name,
                            "is_custom": True,
                            "file_size": custom_map.file_size_bytes,
                            "thumbnail_url": custom_map.thumbnail_url,
                            "description": custom_map.description,
                            "author": custom_map.author,
                            "play_count": custom_map.play_count,
                            "last_played": custom_map.last_played,
                        }
                    )
                else:
                    # Base map
                    all_maps.append(
                        {
                            "name": map_name,
                            "display_name": map_name,
                            "is_custom": False,
                            "file_size": bsp_file.stat().st_size,
                            "thumbnail_url": None,
                            "description": None,
                            "author": None,
                            "play_count": 0,
                            "last_played": None,
                        }
                    )

        return sorted(all_maps, key=lambda x: x["name"])

    def upload_custom_map(
        self,
        server_id: int,
        map_file: bytes,
        map_name: str,
        uploaded_by: int,
        **metadata,
    ) -> Optional[CustomMap]:
        """
        Upload a custom map file

        Args:
            server_id: Server ID
            map_file: .bsp file bytes
            map_name: Map name (without .bsp)
            uploaded_by: User ID who uploaded
            metadata: Optional metadata (display_name, description, author, etc.)
        """
        server_path = Path(f"/home/gameservers/servers/server_{server_id}")
        maps_path = server_path / "valve" / "maps"

        try:
            # Ensure maps directory exists
            maps_path.mkdir(parents=True, exist_ok=True)

            # Calculate file hash
            file_hash = hashlib.sha256(map_file).hexdigest()

            # Check if map already exists
            existing = (
                self.db.query(CustomMap).filter_by(server_id=server_id, map_name=map_name).first()
            )
            if existing:
                logger.warning(f"Custom map {map_name} already exists")
                return None

            # Write .bsp file
            bsp_path = maps_path / f"{map_name}.bsp"
            with open(bsp_path, "wb") as f:
                f.write(map_file)

            # Create database record
            custom_map = CustomMap(
                server_id=server_id,
                map_name=map_name,
                file_size_bytes=len(map_file),
                file_hash=file_hash,
                uploaded_by=uploaded_by,
                **metadata,
            )
            self.db.add(custom_map)
            self.db.commit()

            logger.info(f"Uploaded custom map: {map_name} ({len(map_file)} bytes)")
            return custom_map

        except Exception as e:
            logger.error(f"Failed to upload custom map: {e}")
            self.db.rollback()
            return None

    def delete_custom_map(self, server_id: int, map_name: str) -> bool:
        """Delete a custom map"""
        custom_map = (
            self.db.query(CustomMap).filter_by(server_id=server_id, map_name=map_name).first()
        )

        if not custom_map:
            logger.warning(f"Custom map {map_name} not found")
            return False

        try:
            # Delete .bsp file
            server_path = Path(f"/home/gameservers/servers/server_{server_id}")
            bsp_path = server_path / "valve" / "maps" / f"{map_name}.bsp"
            if bsp_path.exists():
                bsp_path.unlink()

            # Delete related files (.nav, .res, .txt)
            for ext in [".nav", ".res", ".txt"]:
                related_file = bsp_path.with_suffix(ext)
                if related_file.exists():
                    related_file.unlink()

            # Delete database record
            self.db.delete(custom_map)
            self.db.commit()

            logger.info(f"Deleted custom map: {map_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete custom map: {e}")
            self.db.rollback()
            return False

    # =========================
    # Map Voting
    # =========================

    def create_vote(
        self,
        server_id: int,
        vote_title: str,
        map_options: List[str],
        created_by: int,
        duration_minutes: int = 60,
    ) -> MapVote:
        """Create a new map vote"""
        from datetime import timedelta

        vote = MapVote(
            server_id=server_id,
            vote_title=vote_title,
            map_options=map_options,
            vote_results={},
            created_by=created_by,
            ends_at=datetime.now() + timedelta(minutes=duration_minutes),
        )
        self.db.add(vote)
        self.db.commit()

        logger.info(f"Created map vote: {vote_title}")
        return vote

    def cast_vote(self, vote_id: int, map_name: str) -> bool:
        """Cast a vote for a map"""
        vote = self.db.query(MapVote).filter_by(id=vote_id, is_active=True).first()
        if not vote:
            logger.warning(f"Vote {vote_id} not found or inactive")
            return False

        # Check if vote has ended
        if vote.ends_at and datetime.now() > vote.ends_at:
            logger.warning(f"Vote {vote_id} has ended")
            return False

        # Check if map is in options
        if map_name not in vote.map_options:
            logger.warning(f"Map {map_name} not in vote options")
            return False

        # Update vote results
        if vote.vote_results is None:
            vote.vote_results = {}

        vote.vote_results[map_name] = vote.vote_results.get(map_name, 0) + 1
        self.db.commit()

        logger.info(f"Vote cast for {map_name} in vote {vote_id}")
        return True

    def complete_vote(self, vote_id: int) -> Optional[str]:
        """Complete a vote and determine winner"""
        vote = self.db.query(MapVote).filter_by(id=vote_id).first()
        if not vote:
            return None

        # Find winning map
        if vote.vote_results:
            winning_map = max(vote.vote_results, key=vote.vote_results.get)
            vote.winning_map = winning_map
        else:
            vote.winning_map = None

        vote.is_active = False
        vote.completed_at = datetime.now()
        self.db.commit()

        logger.info(f"Completed vote {vote_id}, winner: {vote.winning_map}")
        return vote.winning_map

    # =========================
    # Map Rotation Schedules
    # =========================

    def create_rotation_schedule(
        self,
        server_id: int,
        schedule_name: str,
        maps_rotation: List[str],
        rotation_mode: str,
        created_by: int,
        **kwargs,
    ) -> MapRotationSchedule:
        """Create a map rotation schedule"""
        schedule = MapRotationSchedule(
            server_id=server_id,
            schedule_name=schedule_name,
            maps_rotation=maps_rotation,
            rotation_mode=rotation_mode,
            created_by=created_by,
            **kwargs,
        )
        self.db.add(schedule)
        self.db.commit()

        logger.info(f"Created rotation schedule: {schedule_name}")
        return schedule

    def activate_rotation_schedule(self, server_id: int, schedule_id: int) -> bool:
        """Activate a rotation schedule (deactivate others)"""
        # Deactivate all schedules for this server
        self.db.query(MapRotationSchedule).filter_by(server_id=server_id).update(
            {"is_active": False}
        )

        # Activate the selected schedule
        schedule = self.db.query(MapRotationSchedule).filter_by(id=schedule_id).first()
        if not schedule:
            return False

        schedule.is_active = True
        self.db.commit()

        logger.info(f"Activated rotation schedule {schedule_id}")
        return True

    def get_active_rotation(self, server_id: int) -> Optional[MapRotationSchedule]:
        """Get active rotation schedule for a server"""
        return (
            self.db.query(MapRotationSchedule)
            .filter_by(server_id=server_id, is_active=True)
            .first()
        )
