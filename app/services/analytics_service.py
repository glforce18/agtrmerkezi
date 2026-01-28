"""
AGTR Merkezi v6.2 - Analytics Service
Advanced server analytics and insights
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.database import PlayerSession, ServerMetrics, ServerStatsHourly

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Server analytics and insights service.

    Provides time-series data, aggregated statistics, and insights
    for server performance monitoring and dashboard visualization.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_timeseries_data(self, server_id: int, hours: int = 24) -> List[Dict]:
        """
        Get time-series metrics for a server.

        Args:
            server_id: Server ID
            hours: Time range in hours (24, 168=7d, 720=30d)

        Returns:
            List of data points with timestamp, cpu, memory, players
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        metrics = (
            self.db.query(ServerMetrics)
            .filter(
                ServerMetrics.server_id == server_id,
                ServerMetrics.timestamp >= cutoff,
            )
            .order_by(ServerMetrics.timestamp.asc())
            .all()
        )

        return [
            {
                "timestamp": m.timestamp.isoformat(),
                "cpu_percent": m.cpu_percent or 0,
                "memory_mb": m.memory_mb or 0,
                "player_count": m.player_count or 0,
                "process_status": m.process_status,
            }
            for m in metrics
        ]

    def get_server_summary(self, server_id: int) -> Dict:
        """
        Get aggregated server statistics summary.

        Returns:
            Summary with avg/max/min for CPU, memory, players
        """
        # Last 24 hours
        cutoff = datetime.utcnow() - timedelta(hours=24)

        metrics = (
            self.db.query(ServerMetrics)
            .filter(
                ServerMetrics.server_id == server_id,
                ServerMetrics.timestamp >= cutoff,
            )
            .all()
        )

        if not metrics:
            return {
                "server_id": server_id,
                "period": "24h",
                "data_points": 0,
                "cpu": {"avg": 0, "max": 0, "min": 0},
                "memory": {"avg": 0, "max": 0, "min": 0},
                "players": {"avg": 0, "max": 0, "min": 0},
            }

        cpu_values = [m.cpu_percent for m in metrics if m.cpu_percent is not None]
        memory_values = [m.memory_mb for m in metrics if m.memory_mb is not None]
        player_values = [m.player_count for m in metrics if m.player_count is not None]

        return {
            "server_id": server_id,
            "period": "24h",
            "data_points": len(metrics),
            "cpu": {
                "avg": round(sum(cpu_values) / len(cpu_values), 2) if cpu_values else 0,
                "max": round(max(cpu_values), 2) if cpu_values else 0,
                "min": round(min(cpu_values), 2) if cpu_values else 0,
            },
            "memory": {
                "avg": round(sum(memory_values) / len(memory_values), 2) if memory_values else 0,
                "max": round(max(memory_values), 2) if memory_values else 0,
                "min": round(min(memory_values), 2) if memory_values else 0,
            },
            "players": {
                "avg": round(sum(player_values) / len(player_values), 2) if player_values else 0,
                "max": max(player_values) if player_values else 0,
                "min": min(player_values) if player_values else 0,
            },
        }

    def get_popular_maps(self, server_id: int, days: int = 7) -> List[Dict]:
        """
        Get most played maps on a server.

        Args:
            server_id: Server ID
            days: Time range in days

        Returns:
            List of maps with play time/count
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get hourly stats
        stats = (
            self.db.query(ServerStatsHourly)
            .filter(
                ServerStatsHourly.server_id == server_id,
                ServerStatsHourly.hour_timestamp >= cutoff,
            )
            .all()
        )

        # Aggregate by map
        map_counts = {}
        for stat in stats:
            if stat.most_played_map:
                map_name = stat.most_played_map
                map_counts[map_name] = map_counts.get(map_name, 0) + 1

        # Sort by count
        popular = sorted(map_counts.items(), key=lambda x: x[1], reverse=True)

        return [{"map": map_name, "hours_played": count} for map_name, count in popular[:10]]

    def get_peak_hours(self, server_id: int, days: int = 7) -> List[Dict]:
        """
        Get peak player activity hours.

        Args:
            server_id: Server ID
            days: Time range in days

        Returns:
            Hourly average player count (0-23 hours)
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get hourly stats
        stats = (
            self.db.query(ServerStatsHourly)
            .filter(
                ServerStatsHourly.server_id == server_id,
                ServerStatsHourly.hour_timestamp >= cutoff,
            )
            .all()
        )

        # Group by hour of day
        hourly_data = {hour: [] for hour in range(24)}

        for stat in stats:
            hour = stat.hour_timestamp.hour
            if stat.avg_players is not None:
                hourly_data[hour].append(stat.avg_players)

        # Calculate averages
        result = []
        for hour in range(24):
            values = hourly_data[hour]
            avg = round(sum(values) / len(values), 2) if values else 0

            result.append({"hour": hour, "avg_players": avg, "data_points": len(values)})

        return result

    def get_player_sessions(self, server_id: int, days: int = 7, limit: int = 100) -> List[Dict]:
        """
        Get recent player sessions.

        Args:
            server_id: Server ID
            days: Time range in days
            limit: Max sessions to return

        Returns:
            List of player sessions with duration, kills, deaths
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        sessions = (
            self.db.query(PlayerSession)
            .filter(
                PlayerSession.server_id == server_id,
                PlayerSession.join_time >= cutoff,
            )
            .order_by(PlayerSession.join_time.desc())
            .limit(limit)
            .all()
        )

        result = []

        for session in sessions:
            duration_seconds = None
            if session.leave_time and session.join_time:
                duration_seconds = int((session.leave_time - session.join_time).total_seconds())

            result.append(
                {
                    "player_name": session.player_name,
                    "steam_id": session.steam_id,
                    "join_time": session.join_time.isoformat() if session.join_time else None,
                    "leave_time": session.leave_time.isoformat() if session.leave_time else None,
                    "duration_seconds": duration_seconds,
                    "kills": session.kills or 0,
                    "deaths": session.deaths or 0,
                    "score": session.score or 0,
                }
            )

        return result

    def get_player_retention(self, server_id: int, days: int = 30) -> Dict:
        """
        Get player retention statistics.

        Args:
            server_id: Server ID
            days: Time range in days

        Returns:
            Retention stats (unique players, returning players, new players)
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get all sessions in period
        sessions = (
            self.db.query(PlayerSession)
            .filter(
                PlayerSession.server_id == server_id,
                PlayerSession.join_time >= cutoff,
            )
            .all()
        )

        unique_players = set()
        player_visit_count = {}

        for session in sessions:
            if session.steam_id:
                unique_players.add(session.steam_id)
                player_visit_count[session.steam_id] = (
                    player_visit_count.get(session.steam_id, 0) + 1
                )

        # Calculate returning vs new
        returning_players = sum(1 for count in player_visit_count.values() if count > 1)
        new_players = len(unique_players) - returning_players

        return {
            "period_days": days,
            "unique_players": len(unique_players),
            "new_players": new_players,
            "returning_players": returning_players,
            "retention_rate": (
                round((returning_players / len(unique_players)) * 100, 2) if unique_players else 0
            ),
        }

    def get_hourly_trends(self, server_id: int, days: int = 7) -> List[Dict]:
        """
        Get hourly statistics trends.

        Args:
            server_id: Server ID
            days: Time range in days

        Returns:
            Hourly aggregated stats
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        stats = (
            self.db.query(ServerStatsHourly)
            .filter(
                ServerStatsHourly.server_id == server_id,
                ServerStatsHourly.hour_timestamp >= cutoff,
            )
            .order_by(ServerStatsHourly.hour_timestamp.asc())
            .all()
        )

        return [
            {
                "timestamp": s.hour_timestamp.isoformat(),
                "avg_players": s.avg_players or 0,
                "max_players": s.max_players or 0,
                "min_players": s.min_players or 0,
                "unique_players": s.unique_players or 0,
                "most_played_map": s.most_played_map,
                "uptime_percent": s.uptime_percent or 0,
            }
            for s in stats
        ]
