"""
AGTR Merkezi - Server Performance Monitoring Service
Collects and aggregates server performance metrics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import desc, func

from app.models.connection import SessionLocal
from app.models.database import ServerAnalytics

logger = logging.getLogger(__name__)


class PerformanceService:
    """
    Server performance monitoring service

    Handles CPU, RAM, network metrics collection and retrieval
    """

    def collect_metrics(
        self,
        server_id: int,
        cpu_usage: Optional[float] = None,
        memory_usage_mb: Optional[float] = None,
        network_in_mbps: Optional[float] = None,
        network_out_mbps: Optional[float] = None,
        disk_usage_mb: Optional[float] = None,
        player_count: Optional[int] = None,
        tick_rate: Optional[float] = None,
        fps: Optional[float] = None,
        ping_avg: Optional[float] = None,
        ping_max: Optional[float] = None,
        current_map: Optional[str] = None,
    ) -> bool:
        """
        Collect and store performance metrics

        Args:
            server_id: Server ID
            cpu_usage: CPU usage percentage
            memory_usage_mb: Memory usage in MB
            network_in_mbps: Network incoming Mbps
            network_out_mbps: Network outgoing Mbps
            disk_usage_mb: Disk usage in MB
            player_count: Current player count
            tick_rate: Server tickrate
            fps: Server FPS
            ping_avg: Average ping
            ping_max: Max ping
            current_map: Current map name

        Returns:
            Success status
        """
        db = SessionLocal()
        try:
            analytics = ServerAnalytics(
                server_id=server_id,
                cpu_usage_percent=cpu_usage,
                memory_usage_mb=memory_usage_mb,
                network_in_mbps=network_in_mbps,
                network_out_mbps=network_out_mbps,
                disk_usage_mb=disk_usage_mb,
                player_count=player_count,
                tick_rate=tick_rate,
                fps=fps,
                ping_avg=ping_avg,
                ping_max=ping_max,
                current_map=current_map,
            )
            db.add(analytics)
            db.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to collect metrics for server {server_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def get_metrics_history(
        self,
        server_id: int,
        hours: int = 24,
        interval_minutes: int = 5,
    ) -> List[Dict]:
        """
        Get historical performance metrics

        Args:
            server_id: Server ID
            hours: Number of hours to fetch
            interval_minutes: Sample interval (to reduce data points)

        Returns:
            List of performance metrics
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)

            # Fetch all metrics within time range
            metrics = (
                db.query(ServerAnalytics)
                .filter(
                    ServerAnalytics.server_id == server_id,
                    ServerAnalytics.recorded_at >= cutoff,
                )
                .order_by(ServerAnalytics.recorded_at.asc())
                .all()
            )

            # Sample data points based on interval
            sampled = []
            last_timestamp = None

            for metric in metrics:
                if (
                    last_timestamp is None
                    or (metric.recorded_at - last_timestamp).total_seconds()
                    >= interval_minutes * 60
                ):
                    sampled.append(
                        {
                            "timestamp": metric.recorded_at.isoformat(),
                            "cpu_usage": (
                                round(metric.cpu_usage_percent, 2)
                                if metric.cpu_usage_percent
                                else None
                            ),
                            "memory_usage": (
                                round(metric.memory_usage_mb, 2) if metric.memory_usage_mb else None
                            ),
                            "network_in": (
                                round(metric.network_in_mbps, 2) if metric.network_in_mbps else None
                            ),
                            "network_out": (
                                round(metric.network_out_mbps, 2)
                                if metric.network_out_mbps
                                else None
                            ),
                            "disk_usage": (
                                round(metric.disk_usage_mb, 2) if metric.disk_usage_mb else None
                            ),
                            "player_count": metric.player_count,
                            "tick_rate": round(metric.tick_rate, 1) if metric.tick_rate else None,
                            "fps": round(metric.fps, 1) if metric.fps else None,
                            "ping_avg": round(metric.ping_avg, 1) if metric.ping_avg else None,
                            "ping_max": round(metric.ping_max, 1) if metric.ping_max else None,
                            "current_map": metric.current_map,
                        }
                    )
                    last_timestamp = metric.recorded_at

            return sampled

        finally:
            db.close()

    def get_current_metrics(self, server_id: int) -> Optional[Dict]:
        """
        Get most recent performance metrics

        Args:
            server_id: Server ID

        Returns:
            Latest metrics or None
        """
        db = SessionLocal()
        try:
            latest = (
                db.query(ServerAnalytics)
                .filter(ServerAnalytics.server_id == server_id)
                .order_by(desc(ServerAnalytics.recorded_at))
                .first()
            )

            if not latest:
                return None

            return {
                "timestamp": latest.recorded_at.isoformat(),
                "cpu_usage": round(latest.cpu_usage_percent, 2) if latest.cpu_usage_percent else 0,
                "memory_usage": round(latest.memory_usage_mb, 2) if latest.memory_usage_mb else 0,
                "network_in": round(latest.network_in_mbps, 2) if latest.network_in_mbps else 0,
                "network_out": round(latest.network_out_mbps, 2) if latest.network_out_mbps else 0,
                "disk_usage": round(latest.disk_usage_mb, 2) if latest.disk_usage_mb else 0,
                "player_count": latest.player_count or 0,
                "tick_rate": round(latest.tick_rate, 1) if latest.tick_rate else 0,
                "fps": round(latest.fps, 1) if latest.fps else 0,
                "ping_avg": round(latest.ping_avg, 1) if latest.ping_avg else 0,
                "ping_max": round(latest.ping_max, 1) if latest.ping_max else 0,
                "current_map": latest.current_map or "N/A",
            }

        finally:
            db.close()

    def get_metrics_summary(self, server_id: int, hours: int = 24) -> Dict:
        """
        Get performance metrics summary (avg, max, min)

        Args:
            server_id: Server ID
            hours: Time range in hours

        Returns:
            Summary statistics
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)

            # Aggregate statistics
            stats = (
                db.query(
                    func.avg(ServerAnalytics.cpu_usage_percent).label("cpu_avg"),
                    func.max(ServerAnalytics.cpu_usage_percent).label("cpu_max"),
                    func.avg(ServerAnalytics.memory_usage_mb).label("mem_avg"),
                    func.max(ServerAnalytics.memory_usage_mb).label("mem_max"),
                    func.avg(ServerAnalytics.network_in_mbps).label("net_in_avg"),
                    func.max(ServerAnalytics.network_in_mbps).label("net_in_max"),
                    func.avg(ServerAnalytics.network_out_mbps).label("net_out_avg"),
                    func.max(ServerAnalytics.network_out_mbps).label("net_out_max"),
                    func.avg(ServerAnalytics.player_count).label("players_avg"),
                    func.max(ServerAnalytics.player_count).label("players_max"),
                    func.avg(ServerAnalytics.fps).label("fps_avg"),
                    func.min(ServerAnalytics.fps).label("fps_min"),
                    func.avg(ServerAnalytics.ping_avg).label("ping_avg"),
                    func.max(ServerAnalytics.ping_max).label("ping_max_overall"),
                )
                .filter(
                    ServerAnalytics.server_id == server_id,
                    ServerAnalytics.recorded_at >= cutoff,
                )
                .first()
            )

            return {
                "cpu": {
                    "avg": round(stats.cpu_avg, 2) if stats.cpu_avg else 0,
                    "max": round(stats.cpu_max, 2) if stats.cpu_max else 0,
                },
                "memory": {
                    "avg": round(stats.mem_avg, 2) if stats.mem_avg else 0,
                    "max": round(stats.mem_max, 2) if stats.mem_max else 0,
                },
                "network": {
                    "in_avg": round(stats.net_in_avg, 2) if stats.net_in_avg else 0,
                    "in_max": round(stats.net_in_max, 2) if stats.net_in_max else 0,
                    "out_avg": round(stats.net_out_avg, 2) if stats.net_out_avg else 0,
                    "out_max": round(stats.net_out_max, 2) if stats.net_out_max else 0,
                },
                "players": {
                    "avg": round(stats.players_avg, 2) if stats.players_avg else 0,
                    "max": stats.players_max if stats.players_max else 0,
                },
                "performance": {
                    "fps_avg": round(stats.fps_avg, 1) if stats.fps_avg else 0,
                    "fps_min": round(stats.fps_min, 1) if stats.fps_min else 0,
                    "ping_avg": round(stats.ping_avg, 1) if stats.ping_avg else 0,
                    "ping_max": round(stats.ping_max_overall, 1) if stats.ping_max_overall else 0,
                },
            }

        finally:
            db.close()

    def cleanup_old_metrics(self, server_id: int, days_to_keep: int = 30) -> int:
        """
        Delete old performance metrics

        Args:
            server_id: Server ID
            days_to_keep: Number of days to retain

        Returns:
            Number of deleted records
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_to_keep)

            deleted = (
                db.query(ServerAnalytics)
                .filter(
                    ServerAnalytics.server_id == server_id,
                    ServerAnalytics.recorded_at < cutoff,
                )
                .delete()
            )

            db.commit()
            logger.info(f"Deleted {deleted} old metrics for server {server_id}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to cleanup metrics for server {server_id}: {e}")
            db.rollback()
            return 0
        finally:
            db.close()
