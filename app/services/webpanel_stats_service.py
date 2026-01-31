"""
AGTR Merkezi - WebPanel Statistics Service
Handles player statistics, match history, and server analytics for WebPanel features
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.database import MatchHistory, PlayerStatistics, ServerAnalytics

logger = logging.getLogger(__name__)


class WebPanelStatsService:
    """Service for managing WebPanel statistics"""

    def __init__(self, db: Session):
        self.db = db

    # =========================
    # Player Statistics
    # =========================

    def get_player_stats(self, server_id: int, steam_id: str) -> Optional[PlayerStatistics]:
        """Get statistics for a specific player"""
        return (
            self.db.query(PlayerStatistics)
            .filter_by(server_id=server_id, steam_id=steam_id)
            .first()
        )

    def update_player_stats(
        self, server_id: int, steam_id: str, player_name: str, stats_update: Dict
    ) -> PlayerStatistics:
        """
        Update player statistics

        Args:
            stats_update: Dict with keys like total_kills, total_deaths, etc.
        """
        stats = self.get_player_stats(server_id, steam_id)

        if not stats:
            # Create new stats record
            stats = PlayerStatistics(
                server_id=server_id, steam_id=steam_id, player_name=player_name
            )
            self.db.add(stats)

        # Update fields
        for key, value in stats_update.items():
            if hasattr(stats, key):
                # Increment numeric fields
                if key.startswith("total_"):
                    current = getattr(stats, key) or 0
                    setattr(stats, key, current + value)
                else:
                    setattr(stats, key, value)

        # Update player name and last_seen
        stats.player_name = player_name
        stats.last_seen = datetime.now()

        self.db.commit()
        return stats

    def calculate_elo_rating(self, winner_elo: int, loser_elo: int, k_factor: int = 32) -> tuple:
        """
        Calculate new ELO ratings after a match

        Returns:
            (new_winner_elo, new_loser_elo)
        """
        expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
        expected_loser = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))

        new_winner_elo = int(winner_elo + k_factor * (1 - expected_winner))
        new_loser_elo = int(loser_elo + k_factor * (0 - expected_loser))

        return new_winner_elo, new_loser_elo

    def get_leaderboard(
        self, server_id: int, limit: int = 100, order_by: str = "elo_rating"
    ) -> List[PlayerStatistics]:
        """Get server leaderboard"""
        query = self.db.query(PlayerStatistics).filter_by(server_id=server_id)

        if order_by == "elo_rating":
            query = query.order_by(PlayerStatistics.elo_rating.desc())
        elif order_by == "total_kills":
            query = query.order_by(PlayerStatistics.total_kills.desc())
        elif order_by == "kd_ratio":
            # Calculate K/D ratio (avoid division by zero)
            query = query.order_by(
                (
                    PlayerStatistics.total_kills / func.greatest(PlayerStatistics.total_deaths, 1)
                ).desc()
            )
        elif order_by == "playtime":
            query = query.order_by(PlayerStatistics.total_playtime_seconds.desc())

        return query.limit(limit).all()

    def update_rankings(self, server_id: int):
        """Update rank numbers for all players on a server"""
        players = (
            self.db.query(PlayerStatistics)
            .filter_by(server_id=server_id)
            .order_by(PlayerStatistics.elo_rating.desc())
            .all()
        )

        for rank, player in enumerate(players, start=1):
            player.rank = rank

        self.db.commit()
        logger.info(f"Updated rankings for {len(players)} players")

    # =========================
    # Match History
    # =========================

    def record_match(self, server_id: int, match_data: Dict) -> MatchHistory:
        """Record a match result"""
        match = MatchHistory(server_id=server_id, **match_data)
        self.db.add(match)
        self.db.commit()

        logger.info(f"Recorded match on {match_data.get('map_name')}")
        return match

    def get_match_history(
        self, server_id: int, limit: int = 100, map_name: Optional[str] = None
    ) -> List[MatchHistory]:
        """Get match history"""
        query = self.db.query(MatchHistory).filter_by(server_id=server_id)

        if map_name:
            query = query.filter_by(map_name=map_name)

        return query.order_by(MatchHistory.match_date.desc()).limit(limit).all()

    def get_match_stats(self, server_id: int, days: int = 30) -> Dict:
        """Get aggregate match statistics"""
        since = datetime.now() - timedelta(days=days)

        matches = (
            self.db.query(MatchHistory)
            .filter(MatchHistory.server_id == server_id, MatchHistory.match_date >= since)
            .all()
        )

        total_matches = len(matches)
        total_kills = sum(m.total_kills or 0 for m in matches)
        total_duration = sum(m.duration_seconds or 0 for m in matches)

        # Most played maps
        map_counts = {}
        for match in matches:
            map_counts[match.map_name] = map_counts.get(match.map_name, 0) + 1

        most_played = (
            sorted(map_counts.items(), key=lambda x: x[1], reverse=True)[:5] if map_counts else []
        )

        return {
            "total_matches": total_matches,
            "total_kills": total_kills,
            "avg_duration_minutes": (total_duration / 60 / total_matches) if total_matches else 0,
            "most_played_maps": [{"map": k, "count": v} for k, v in most_played],
        }

    # =========================
    # Server Analytics
    # =========================

    def record_analytics(self, server_id: int, metrics: Dict) -> ServerAnalytics:
        """Record server performance metrics"""
        analytics = ServerAnalytics(server_id=server_id, **metrics)
        self.db.add(analytics)
        self.db.commit()
        return analytics

    def get_analytics(
        self, server_id: int, hours: int = 24, interval_minutes: int = 5
    ) -> List[ServerAnalytics]:
        """Get server analytics for time range"""
        since = datetime.now() - timedelta(hours=hours)

        return (
            self.db.query(ServerAnalytics)
            .filter(ServerAnalytics.server_id == server_id, ServerAnalytics.recorded_at >= since)
            .order_by(ServerAnalytics.recorded_at)
            .all()
        )

    def get_analytics_summary(self, server_id: int, hours: int = 24) -> Dict:
        """Get summary of analytics data"""
        analytics = self.get_analytics(server_id, hours)

        if not analytics:
            return {
                "avg_cpu": 0,
                "avg_memory": 0,
                "avg_players": 0,
                "max_players": 0,
                "avg_ping": 0,
            }

        return {
            "avg_cpu": sum(a.cpu_usage_percent or 0 for a in analytics) / len(analytics),
            "avg_memory": sum(a.memory_usage_mb or 0 for a in analytics) / len(analytics),
            "avg_players": sum(a.player_count or 0 for a in analytics) / len(analytics),
            "max_players": max((a.player_count or 0) for a in analytics),
            "avg_ping": sum(a.ping_avg or 0 for a in analytics) / len(analytics),
            "data_points": len(analytics),
        }
