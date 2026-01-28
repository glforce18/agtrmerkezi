"""
AGTR Merkezi - Metrics Archival Service
Automatic aggregation and cleanup of old server metrics
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.database import ServerMetrics

logger = logging.getLogger(__name__)


class MetricsArchiver:
    """
    Metrics retention and aggregation service.

    Retention Policy:
    - Raw data: 7 days (5-minute intervals)
    - Hourly aggregates: 30 days
    - Daily aggregates: 1 year
    - Monthly aggregates: Forever
    """

    def __init__(self, db: Session):
        self.db = db

    def cleanup_old_raw_metrics(self, days_to_keep: int = 7) -> int:
        """
        Delete raw metrics older than N days.

        Args:
            days_to_keep: Number of days to keep raw data

        Returns:
            Number of rows deleted
        """
        cutoff = datetime.utcnow() - timedelta(days=days_to_keep)

        deleted = self.db.query(ServerMetrics).filter(ServerMetrics.timestamp < cutoff).delete()

        self.db.commit()

        logger.info(f"Deleted {deleted} raw metrics older than {days_to_keep} days")
        return deleted

    def aggregate_to_hourly(self, target_date: datetime) -> int:
        """
        Aggregate 5-minute metrics to hourly averages for a specific date.

        Creates hourly ServerStatsHourly records with aggregated data.

        Args:
            target_date: Date to aggregate (will process all hours for that day)

        Returns:
            Number of hourly records created
        """
        from app.models.database import GameServer, ServerStatsHourly

        # Get all servers
        servers = self.db.query(GameServer).all()

        records_created = 0

        for server in servers:
            # For each hour of target_date
            for hour in range(24):
                hour_start = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                hour_end = hour_start + timedelta(hours=1)

                # Query metrics for this hour
                metrics = (
                    self.db.query(ServerMetrics)
                    .filter(
                        ServerMetrics.server_id == server.id,
                        ServerMetrics.timestamp >= hour_start,
                        ServerMetrics.timestamp < hour_end,
                    )
                    .all()
                )

                if not metrics:
                    continue

                # Calculate aggregates
                sum(m.cpu_percent or 0 for m in metrics) / len(metrics)
                sum(m.memory_mb or 0 for m in metrics) / len(metrics)
                max_players = max((m.player_count or 0 for m in metrics), default=0)
                avg_players = sum(m.player_count or 0 for m in metrics) / len(metrics)

                # Check if hourly record already exists
                existing = (
                    self.db.query(ServerStatsHourly)
                    .filter(
                        ServerStatsHourly.server_id == server.id,
                        ServerStatsHourly.hour_timestamp == hour_start,
                    )
                    .first()
                )

                if not existing:
                    # Create hourly aggregate
                    hourly_stats = ServerStatsHourly(
                        server_id=server.id,
                        hour_timestamp=hour_start,
                        avg_players=avg_players,
                        max_players=max_players,
                        min_players=min((m.player_count or 0 for m in metrics), default=0),
                        unique_players=max_players,  # Approximate
                        uptime_percent=100.0 if metrics else 0.0,
                        created_at=datetime.utcnow(),
                    )
                    self.db.add(hourly_stats)
                    records_created += 1

        self.db.commit()

        logger.info(f"Created {records_created} hourly aggregate records for {target_date.date()}")
        return records_created

    def get_metrics_table_size(self) -> dict:
        """
        Get current size of metrics table.

        Returns:
            Dict with row count and oldest/newest timestamps
        """
        total_count = self.db.query(func.count(ServerMetrics.id)).scalar()

        oldest = self.db.query(func.min(ServerMetrics.timestamp)).scalar()
        newest = self.db.query(func.max(ServerMetrics.timestamp)).scalar()

        return {
            "total_rows": total_count,
            "oldest_timestamp": oldest.isoformat() if oldest else None,
            "newest_timestamp": newest.isoformat() if newest else None,
            "estimated_size_mb": total_count * 0.001,  # Rough estimate: 1KB/row
        }


async def run_daily_archival(db: Session):
    """
    Daily scheduled task for metrics archival.

    Runs at 3 AM:
    1. Aggregate yesterday's data to hourly
    2. Delete raw data older than 7 days
    """
    archiver = MetricsArchiver(db)

    # Aggregate yesterday
    yesterday = datetime.utcnow() - timedelta(days=1)
    archiver.aggregate_to_hourly(yesterday)

    # Cleanup old data
    deleted = archiver.cleanup_old_raw_metrics(days_to_keep=7)

    # Log stats
    stats = archiver.get_metrics_table_size()
    logger.info(
        f"Metrics archival complete: {stats['total_rows']} rows, "
        f"{stats['estimated_size_mb']:.1f} MB"
    )

    return {
        "aggregated_date": yesterday.date().isoformat(),
        "deleted_rows": deleted,
        "table_stats": stats,
    }
