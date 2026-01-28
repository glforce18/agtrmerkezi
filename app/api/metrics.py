"""
AGTR Merkezi v6.1 - Server Metrics API
Real-time and historical server resource metrics
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import GameServer, ServerMetrics, User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/servers", tags=["Server Metrics"])


# ============================================
# Response Models
# ============================================


class MetricResponse(BaseModel):
    """Single metric data point"""

    id: int
    server_id: int
    cpu_percent: Optional[float]
    memory_mb: Optional[float]
    network_in_mbps: Optional[float]
    network_out_mbps: Optional[float]
    process_status: Optional[str]
    player_count: int
    timestamp: datetime

    class Config:
        from_attributes = True


class MetricsHistoryResponse(BaseModel):
    """Historical metrics response"""

    server_id: int
    period_hours: int
    data_points: int
    metrics: List[MetricResponse]


class MetricsSummaryResponse(BaseModel):
    """Aggregated metrics summary"""

    server_id: int
    period_hours: int
    avg_cpu: Optional[float]
    max_cpu: Optional[float]
    avg_memory_mb: Optional[float]
    max_memory_mb: Optional[float]
    avg_players: Optional[float]
    max_players: Optional[int]
    uptime_percent: Optional[float]


# ============================================
# Helper Functions
# ============================================


def verify_server_access(server_id: int, user: User, db: Session) -> GameServer:
    """Verify user has access to server"""
    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")

    # Check ownership (or admin access)
    if server.owner_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Bu sunucuya erisim yetkiniz yok")

    return server


# ============================================
# API Endpoints
# ============================================


@router.get("/{server_id}/metrics/current", response_model=MetricResponse)
async def get_current_metrics(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get latest metrics for a server.

    Returns the most recent metric data point.
    """
    # Verify access
    verify_server_access(server_id, current_user, db)

    # Get latest metric
    latest = (
        db.query(ServerMetrics)
        .filter(ServerMetrics.server_id == server_id)
        .order_by(ServerMetrics.timestamp.desc())
        .first()
    )

    if not latest:
        raise HTTPException(status_code=404, detail="Bu sunucu icin henuz metrik verisi yok")

    return latest


@router.get("/{server_id}/metrics/history", response_model=MetricsHistoryResponse)
async def get_metrics_history(
    server_id: int,
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history (1-168)"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max data points"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get historical metrics for graphing.

    Returns time-series data for the specified period.
    Default: Last 24 hours, max 100 data points.
    """
    # Verify access
    verify_server_access(server_id, current_user, db)

    # Calculate time range
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    # Query metrics
    metrics = (
        db.query(ServerMetrics)
        .filter(ServerMetrics.server_id == server_id, ServerMetrics.timestamp >= cutoff)
        .order_by(ServerMetrics.timestamp.asc())
        .limit(limit)
        .all()
    )

    return {
        "server_id": server_id,
        "period_hours": hours,
        "data_points": len(metrics),
        "metrics": metrics,
    }


@router.get("/{server_id}/metrics/summary", response_model=MetricsSummaryResponse)
async def get_metrics_summary(
    server_id: int,
    hours: int = Query(default=24, ge=1, le=168, description="Hours to summarize"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get aggregated metrics summary.

    Returns averages, maximums, and uptime percentage for the period.
    """
    # Verify access
    verify_server_access(server_id, current_user, db)

    # Calculate time range
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    # Aggregate query
    result = (
        db.query(
            func.avg(ServerMetrics.cpu_percent).label("avg_cpu"),
            func.max(ServerMetrics.cpu_percent).label("max_cpu"),
            func.avg(ServerMetrics.memory_mb).label("avg_memory"),
            func.max(ServerMetrics.memory_mb).label("max_memory"),
            func.avg(ServerMetrics.player_count).label("avg_players"),
            func.max(ServerMetrics.player_count).label("max_players"),
            func.count(ServerMetrics.id).label("total_checks"),
        )
        .filter(ServerMetrics.server_id == server_id, ServerMetrics.timestamp >= cutoff)
        .first()
    )

    if not result or result.total_checks == 0:
        raise HTTPException(status_code=404, detail="Bu donem icin metrik verisi yok")

    # Calculate uptime (ratio of 'running' status)
    running_count = (
        db.query(func.count(ServerMetrics.id))
        .filter(
            ServerMetrics.server_id == server_id,
            ServerMetrics.timestamp >= cutoff,
            ServerMetrics.process_status == "running",
        )
        .scalar()
    )

    uptime_percent = (running_count / result.total_checks * 100) if result.total_checks > 0 else 0

    return {
        "server_id": server_id,
        "period_hours": hours,
        "avg_cpu": round(result.avg_cpu, 2) if result.avg_cpu else None,
        "max_cpu": round(result.max_cpu, 2) if result.max_cpu else None,
        "avg_memory_mb": round(result.avg_memory, 2) if result.avg_memory else None,
        "max_memory_mb": round(result.max_memory, 2) if result.max_memory else None,
        "avg_players": round(result.avg_players, 2) if result.avg_players else None,
        "max_players": int(result.max_players) if result.max_players else 0,
        "uptime_percent": round(uptime_percent, 2),
    }


@router.delete("/{server_id}/metrics/cleanup")
async def cleanup_old_metrics(
    server_id: int,
    days: int = Query(default=30, ge=7, le=365, description="Delete metrics older than N days"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Cleanup old metrics (admin or owner only).

    Deletes metrics older than specified days to save storage.
    """
    # Verify access
    verify_server_access(server_id, current_user, db)

    # Calculate cutoff
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Delete old metrics
    deleted = (
        db.query(ServerMetrics)
        .filter(ServerMetrics.server_id == server_id, ServerMetrics.timestamp < cutoff)
        .delete()
    )

    db.commit()

    logger.info(f"Cleaned up {deleted} old metrics for server {server_id} (older than {days} days)")

    return {"success": True, "deleted_count": deleted, "cutoff_date": cutoff.isoformat()}
