"""
Player Management Service
Advanced player search, history, notes, tags
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.orm import Session

from app.models.database import PlayerHistory, PlayerNote, PlayerTag

logger = logging.getLogger(__name__)


class PlayerManagementService:
    """Service for advanced player management"""

    async def search_players(
        self,
        server_id: int,
        query: str = None,
        search_by: List[str] = None,
        date_from: datetime = None,
        date_to: datetime = None,
        limit: int = 50,
        db: Session = None,
    ) -> List[Dict]:
        """
        Advanced player search

        Args:
            server_id: Server ID
            query: Search query
            search_by: ['name', 'steam_id', 'ip']
            date_from: Start date
            date_to: End date
            limit: Result limit

        Returns:
            List of player records with aggregated stats
        """
        try:
            # Base query
            stmt = select(PlayerHistory).filter(PlayerHistory.server_id == server_id)

            # Apply search filters
            if query and search_by:
                filters = []
                if "name" in search_by:
                    filters.append(PlayerHistory.name.ilike(f"%{query}%"))
                if "steam_id" in search_by:
                    filters.append(PlayerHistory.steam_id.ilike(f"%{query}%"))
                if "ip" in search_by:
                    filters.append(PlayerHistory.ip_address.ilike(f"%{query}%"))

                if filters:
                    stmt = stmt.filter(or_(*filters))

            # Date range filter
            if date_from:
                stmt = stmt.filter(PlayerHistory.connected_at >= date_from)
            if date_to:
                stmt = stmt.filter(PlayerHistory.connected_at <= date_to)

            # Order and limit
            stmt = stmt.order_by(desc(PlayerHistory.connected_at)).limit(limit)

            result = db.execute(stmt)
            players = result.scalars().all()

            # Convert to dict with aggregated data
            player_list = []
            for player in players:
                player_list.append(
                    {
                        "id": player.id,
                        "steam_id": player.steam_id,
                        "name": player.name,
                        "ip_address": player.ip_address,
                        "connected_at": (
                            player.connected_at.isoformat() if player.connected_at else None
                        ),
                        "disconnected_at": (
                            player.disconnected_at.isoformat() if player.disconnected_at else None
                        ),
                        "duration_seconds": player.duration_seconds,
                        "map_played": player.map_played,
                        "kills": player.kills,
                        "deaths": player.deaths,
                        "score": player.score,
                        "kd_ratio": (
                            round(player.kills / player.deaths, 2)
                            if player.deaths > 0
                            else player.kills
                        ),
                    }
                )

            return player_list

        except Exception as e:
            logger.error(f"Error searching players: {e}")
            return []

    async def get_player_analytics(self, server_id: int, steam_id: str, db: Session) -> Dict:
        """
        Get detailed player analytics

        Returns:
            Comprehensive player stats and history
        """
        try:
            # Get all sessions
            stmt = (
                select(PlayerHistory)
                .filter(
                    and_(PlayerHistory.server_id == server_id, PlayerHistory.steam_id == steam_id)
                )
                .order_by(desc(PlayerHistory.connected_at))
            )

            result = db.execute(stmt)
            sessions = result.scalars().all()

            if not sessions:
                return {"error": "Player not found"}

            # Calculate aggregated stats
            total_sessions = len(sessions)
            total_playtime = sum(s.duration_seconds or 0 for s in sessions)
            total_kills = sum(s.kills or 0 for s in sessions)
            total_deaths = sum(s.deaths or 0 for s in sessions)
            total_score = sum(s.score or 0 for s in sessions)

            # First and last seen
            first_seen = sessions[-1].connected_at if sessions else None
            last_seen = sessions[0].connected_at if sessions else None

            # Favorite map
            map_counts = {}
            for session in sessions:
                if session.map_played:
                    map_counts[session.map_played] = map_counts.get(session.map_played, 0) + 1
            favorite_map = max(map_counts, key=map_counts.get) if map_counts else None

            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_sessions = [s for s in sessions if s.connected_at >= thirty_days_ago]
            recent_playtime = sum(s.duration_seconds or 0 for s in recent_sessions)

            # Get notes and tags
            notes = await self.get_player_notes(server_id, steam_id, db)
            tags = await self.get_player_tags(server_id, steam_id, db)

            return {
                "steam_id": steam_id,
                "last_name": sessions[0].name if sessions else "Unknown",
                "first_seen": first_seen.isoformat() if first_seen else None,
                "last_seen": last_seen.isoformat() if last_seen else None,
                "total_sessions": total_sessions,
                "total_playtime_hours": round(total_playtime / 3600, 2),
                "total_kills": total_kills,
                "total_deaths": total_deaths,
                "total_score": total_score,
                "kd_ratio": (
                    round(total_kills / total_deaths, 2) if total_deaths > 0 else total_kills
                ),
                "favorite_map": favorite_map,
                "favorite_map_count": map_counts.get(favorite_map, 0) if favorite_map else 0,
                "recent_playtime_hours": round(recent_playtime / 3600, 2),
                "recent_sessions": len(recent_sessions),
                "notes": notes,
                "tags": tags,
                "sessions": [
                    {
                        "connected_at": s.connected_at.isoformat(),
                        "duration_minutes": round((s.duration_seconds or 0) / 60, 1),
                        "map": s.map_played,
                        "kills": s.kills,
                        "deaths": s.deaths,
                        "score": s.score,
                    }
                    for s in sessions[:10]  # Last 10 sessions
                ],
            }

        except Exception as e:
            logger.error(f"Error getting player analytics: {e}")
            return {"error": str(e)}

    async def add_player_note(
        self, server_id: int, steam_id: str, note: str, admin_id: int, db: Session
    ) -> Dict:
        """Add admin note for player"""
        try:
            player_note = PlayerNote(
                server_id=server_id, steam_id=steam_id, admin_id=admin_id, note=note
            )
            db.add(player_note)
            db.commit()

            return {
                "success": True,
                "message": "Note added successfully",
                "note": {
                    "id": player_note.id,
                    "note": player_note.note,
                    "created_at": player_note.created_at.isoformat(),
                },
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error adding player note: {e}")
            return {"success": False, "error": str(e)}

    async def get_player_notes(self, server_id: int, steam_id: str, db: Session) -> List[Dict]:
        """Get all notes for a player"""
        try:
            stmt = (
                select(PlayerNote)
                .filter(and_(PlayerNote.server_id == server_id, PlayerNote.steam_id == steam_id))
                .order_by(desc(PlayerNote.created_at))
            )

            result = db.execute(stmt)
            notes = result.scalars().all()

            return [
                {
                    "id": note.id,
                    "note": note.note,
                    "admin_id": note.admin_id,
                    "created_at": note.created_at.isoformat(),
                    "updated_at": note.updated_at.isoformat() if note.updated_at else None,
                }
                for note in notes
            ]

        except Exception as e:
            logger.error(f"Error getting player notes: {e}")
            return []

    async def add_player_tag(
        self, server_id: int, steam_id: str, tag: str, color: str, admin_id: int, db: Session
    ) -> Dict:
        """Add tag to player"""
        try:
            player_tag = PlayerTag(
                server_id=server_id, steam_id=steam_id, tag=tag, color=color, added_by=admin_id
            )
            db.add(player_tag)
            db.commit()

            return {
                "success": True,
                "message": "Tag added successfully",
                "tag": {"id": player_tag.id, "tag": player_tag.tag, "color": player_tag.color},
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Error adding player tag: {e}")
            return {"success": False, "error": str(e)}

    async def get_player_tags(self, server_id: int, steam_id: str, db: Session) -> List[Dict]:
        """Get all tags for a player"""
        try:
            stmt = select(PlayerTag).filter(
                and_(PlayerTag.server_id == server_id, PlayerTag.steam_id == steam_id)
            )

            result = db.execute(stmt)
            tags = result.scalars().all()

            return [
                {
                    "id": tag.id,
                    "tag": tag.tag,
                    "color": tag.color,
                    "added_by": tag.added_by,
                    "created_at": tag.created_at.isoformat(),
                }
                for tag in tags
            ]

        except Exception as e:
            logger.error(f"Error getting player tags: {e}")
            return []

    async def remove_player_tag(self, server_id: int, tag_id: int, db: Session) -> Dict:
        """Remove tag from player"""
        try:
            stmt = select(PlayerTag).filter(
                and_(PlayerTag.id == tag_id, PlayerTag.server_id == server_id)
            )
            result = db.execute(stmt)
            tag = result.scalar_one_or_none()

            if not tag:
                return {"success": False, "error": "Tag not found"}

            db.delete(tag)
            db.commit()

            return {"success": True, "message": "Tag removed successfully"}

        except Exception as e:
            db.rollback()
            logger.error(f"Error removing player tag: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
player_management_service = PlayerManagementService()
