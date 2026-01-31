"""
AGTR Merkezi - Player Statistics Service
Player leaderboard, individual stats, and ELO tracking
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import Float, desc, func

from app.models.connection import SessionLocal
from app.models.database import MatchHistory, PlayerStatistics

logger = logging.getLogger(__name__)


class PlayerStatsService:
    """
    Player statistics service

    Handles player leaderboard, individual stats, ELO rankings
    """

    def get_leaderboard(
        self,
        server_id: int,
        sort_by: str = "elo_rating",
        limit: int = 100,
        min_playtime: int = 3600,  # 1 hour minimum
    ) -> List[Dict]:
        """
        Get player leaderboard

        Args:
            server_id: Server ID
            sort_by: Sort column (elo_rating, total_kills, total_score, kd_ratio)
            limit: Max results
            min_playtime: Minimum playtime in seconds

        Returns:
            List of player stats
        """
        db = SessionLocal()
        try:
            query = db.query(PlayerStatistics).filter(
                PlayerStatistics.server_id == server_id,
                PlayerStatistics.total_playtime_seconds >= min_playtime,
            )

            # Sort by requested column
            if sort_by == "elo_rating":
                query = query.order_by(desc(PlayerStatistics.elo_rating))
            elif sort_by == "total_kills":
                query = query.order_by(desc(PlayerStatistics.total_kills))
            elif sort_by == "total_score":
                query = query.order_by(desc(PlayerStatistics.total_score))
            elif sort_by == "kd_ratio":
                # K/D ratio calculated on-the-fly
                query = query.order_by(
                    desc(
                        func.cast(PlayerStatistics.total_kills, Float)
                        / func.nullif(PlayerStatistics.total_deaths, 0)
                    )
                )
            else:
                query = query.order_by(desc(PlayerStatistics.elo_rating))

            players = query.limit(limit).all()

            return [
                {
                    "steam_id": p.steam_id,
                    "player_name": p.player_name,
                    "elo_rating": p.elo_rating,
                    "rank": idx + 1,
                    "total_kills": p.total_kills,
                    "total_deaths": p.total_deaths,
                    "kd_ratio": (
                        round(p.total_kills / p.total_deaths, 2)
                        if p.total_deaths > 0
                        else p.total_kills
                    ),
                    "total_headshots": p.total_headshots,
                    "headshot_percentage": round(
                        (p.total_headshots / p.total_kills * 100) if p.total_kills > 0 else 0,
                        1,
                    ),
                    "total_score": p.total_score,
                    "wins": p.wins,
                    "losses": p.losses,
                    "win_rate": round(
                        (p.wins / (p.wins + p.losses) * 100) if (p.wins + p.losses) > 0 else 0, 1
                    ),
                    "total_playtime": p.total_playtime_seconds,
                    "playtime_hours": round(p.total_playtime_seconds / 3600, 1),
                    "favorite_weapon": p.favorite_weapon,
                    "favorite_map": p.favorite_map,
                    "last_seen": p.last_seen.isoformat() if p.last_seen else None,
                }
                for idx, p in enumerate(players)
            ]

        finally:
            db.close()

    def get_player_stats(self, server_id: int, steam_id: str) -> Optional[Dict]:
        """
        Get individual player statistics

        Args:
            server_id: Server ID
            steam_id: Player Steam ID

        Returns:
            Player stats dict or None
        """
        db = SessionLocal()
        try:
            player = (
                db.query(PlayerStatistics)
                .filter(
                    PlayerStatistics.server_id == server_id,
                    PlayerStatistics.steam_id == steam_id,
                )
                .first()
            )

            if not player:
                return None

            # Get rank
            rank = (
                db.query(func.count(PlayerStatistics.id))
                .filter(
                    PlayerStatistics.server_id == server_id,
                    PlayerStatistics.elo_rating > player.elo_rating,
                )
                .scalar()
                + 1
            )

            return {
                "steam_id": player.steam_id,
                "player_name": player.player_name,
                "elo_rating": player.elo_rating,
                "rank": rank,
                "total_kills": player.total_kills,
                "total_deaths": player.total_deaths,
                "kd_ratio": (
                    round(player.total_kills / player.total_deaths, 2)
                    if player.total_deaths > 0
                    else player.total_kills
                ),
                "total_headshots": player.total_headshots,
                "headshot_percentage": round(
                    (
                        (player.total_headshots / player.total_kills * 100)
                        if player.total_kills > 0
                        else 0
                    ),
                    1,
                ),
                "total_score": player.total_score,
                "total_rounds": player.total_rounds,
                "wins": player.wins,
                "losses": player.losses,
                "win_rate": round(
                    (
                        (player.wins / (player.wins + player.losses) * 100)
                        if (player.wins + player.losses) > 0
                        else 0
                    ),
                    1,
                ),
                "total_playtime": player.total_playtime_seconds,
                "playtime_hours": round(player.total_playtime_seconds / 3600, 1),
                "favorite_weapon": player.favorite_weapon,
                "favorite_map": player.favorite_map,
                "first_seen": player.first_seen.isoformat() if player.first_seen else None,
                "last_seen": player.last_seen.isoformat() if player.last_seen else None,
            }

        finally:
            db.close()

    def get_top_players_by_category(self, server_id: int, limit: int = 5) -> Dict:
        """
        Get top players in different categories

        Args:
            server_id: Server ID
            limit: Number of top players per category

        Returns:
            Dict with top players for each category
        """
        db = SessionLocal()
        try:
            # Top by ELO
            top_elo = (
                db.query(PlayerStatistics)
                .filter(
                    PlayerStatistics.server_id == server_id,
                    PlayerStatistics.total_playtime_seconds >= 3600,
                )
                .order_by(desc(PlayerStatistics.elo_rating))
                .limit(limit)
                .all()
            )

            # Top by K/D
            top_kd = (
                db.query(PlayerStatistics)
                .filter(
                    PlayerStatistics.server_id == server_id,
                    PlayerStatistics.total_playtime_seconds >= 3600,
                    PlayerStatistics.total_deaths > 0,
                )
                .order_by(
                    desc(
                        func.cast(PlayerStatistics.total_kills, Float)
                        / func.nullif(PlayerStatistics.total_deaths, 0)
                    )
                )
                .limit(limit)
                .all()
            )

            # Top by kills
            top_kills = (
                db.query(PlayerStatistics)
                .filter(
                    PlayerStatistics.server_id == server_id,
                    PlayerStatistics.total_playtime_seconds >= 3600,
                )
                .order_by(desc(PlayerStatistics.total_kills))
                .limit(limit)
                .all()
            )

            # Top by headshots
            top_headshots = (
                db.query(PlayerStatistics)
                .filter(
                    PlayerStatistics.server_id == server_id,
                    PlayerStatistics.total_playtime_seconds >= 3600,
                    PlayerStatistics.total_kills > 0,
                )
                .order_by(
                    desc(
                        func.cast(PlayerStatistics.total_headshots, Float)
                        / func.nullif(PlayerStatistics.total_kills, 0)
                    )
                )
                .limit(limit)
                .all()
            )

            def format_player(p, include_kd=False):
                data = {
                    "steam_id": p.steam_id,
                    "player_name": p.player_name,
                    "elo_rating": p.elo_rating,
                    "total_kills": p.total_kills,
                    "total_headshots": p.total_headshots,
                }
                if include_kd:
                    data["kd_ratio"] = (
                        round(p.total_kills / p.total_deaths, 2)
                        if p.total_deaths > 0
                        else p.total_kills
                    )
                    data["headshot_percentage"] = round(
                        (p.total_headshots / p.total_kills * 100) if p.total_kills > 0 else 0, 1
                    )
                return data

            return {
                "top_elo": [format_player(p) for p in top_elo],
                "top_kd": [format_player(p, include_kd=True) for p in top_kd],
                "top_kills": [format_player(p) for p in top_kills],
                "top_headshots": [format_player(p, include_kd=True) for p in top_headshots],
            }

        finally:
            db.close()

    def update_player_stats(
        self,
        server_id: int,
        steam_id: str,
        player_name: str,
        stats_delta: Dict,
    ) -> bool:
        """
        Update player statistics (incremental)

        Args:
            server_id: Server ID
            steam_id: Player Steam ID
            player_name: Player name
            stats_delta: Stats to increment (kills, deaths, headshots, etc.)

        Returns:
            Success status
        """
        db = SessionLocal()
        try:
            # Find or create player stats
            player = (
                db.query(PlayerStatistics)
                .filter(
                    PlayerStatistics.server_id == server_id,
                    PlayerStatistics.steam_id == steam_id,
                )
                .first()
            )

            if not player:
                player = PlayerStatistics(
                    server_id=server_id,
                    steam_id=steam_id,
                    player_name=player_name,
                )
                db.add(player)
            else:
                # Update name if changed
                player.player_name = player_name

            # Increment stats
            if "kills" in stats_delta:
                player.total_kills += stats_delta["kills"]
            if "deaths" in stats_delta:
                player.total_deaths += stats_delta["deaths"]
            if "headshots" in stats_delta:
                player.total_headshots += stats_delta["headshots"]
            if "score" in stats_delta:
                player.total_score += stats_delta["score"]
            if "playtime" in stats_delta:
                player.total_playtime_seconds += stats_delta["playtime"]
            if "rounds" in stats_delta:
                player.total_rounds += stats_delta["rounds"]
            if "wins" in stats_delta:
                player.wins += stats_delta["wins"]
            if "losses" in stats_delta:
                player.losses += stats_delta["losses"]

            # Update weapon/map favorites if provided
            if "weapon" in stats_delta:
                player.favorite_weapon = stats_delta["weapon"]
            if "map" in stats_delta:
                player.favorite_map = stats_delta["map"]

            # Update last seen
            player.last_seen = datetime.utcnow()

            db.commit()
            logger.info(f"Updated stats for player {steam_id} on server {server_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update player stats: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def calculate_elo_change(self, winner_elo: int, loser_elo: int, k_factor: int = 32) -> tuple:
        """
        Calculate ELO rating changes

        Args:
            winner_elo: Winner's current ELO
            loser_elo: Loser's current ELO
            k_factor: K-factor (sensitivity)

        Returns:
            (winner_new_elo, loser_new_elo)
        """
        # Expected scores
        expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
        expected_loser = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))

        # New ratings
        winner_new = winner_elo + k_factor * (1 - expected_winner)
        loser_new = loser_elo + k_factor * (0 - expected_loser)

        return int(winner_new), int(loser_new)

    def get_recent_matches(self, server_id: int, limit: int = 20) -> List[Dict]:
        """
        Get recent match history

        Args:
            server_id: Server ID
            limit: Max results

        Returns:
            List of recent matches
        """
        db = SessionLocal()
        try:
            matches = (
                db.query(MatchHistory)
                .filter(MatchHistory.server_id == server_id)
                .order_by(desc(MatchHistory.match_date))
                .limit(limit)
                .all()
            )

            return [
                {
                    "id": m.id,
                    "match_date": m.match_date.isoformat() if m.match_date else None,
                    "map_name": m.map_name,
                    "match_type": m.match_type,
                    "duration_seconds": m.duration_seconds,
                    "team1_score": m.team1_score,
                    "team2_score": m.team2_score,
                    "winner_team": m.winner_team,
                    "total_kills": m.total_kills,
                }
                for m in matches
            ]

        finally:
            db.close()

    def get_player_activity_chart(self, server_id: int, days: int = 30) -> Dict:
        """
        Get player activity over time

        Args:
            server_id: Server ID
            days: Number of days

        Returns:
            Chart data with daily player counts
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            # Group by date
            results = (
                db.query(
                    func.date(PlayerStatistics.last_seen).label("date"),
                    func.count(PlayerStatistics.id).label("count"),
                )
                .filter(
                    PlayerStatistics.server_id == server_id,
                    PlayerStatistics.last_seen >= cutoff,
                )
                .group_by(func.date(PlayerStatistics.last_seen))
                .order_by("date")
                .all()
            )

            return {
                "labels": [
                    r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date)
                    for r in results
                ],
                "data": [r.count for r in results],
            }

        finally:
            db.close()
