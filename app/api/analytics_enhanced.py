"""
AGTR Merkezi v6.2 - Enhanced Analytics API
Time-series data, trends, insights for server monitoring
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import GameServer, User
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# ============================================
# Response Models
# ============================================


class TimeseriesDataPoint(BaseModel):
    """Single timeseries data point"""

    timestamp: str
    cpu_percent: float
    memory_mb: float
    player_count: int
    process_status: str | None


class TimeseriesResponse(BaseModel):
    """Timeseries data response"""

    server_id: int
    period_hours: int
    data_points: int
    data: List[TimeseriesDataPoint]


class ResourceStats(BaseModel):
    """Resource statistics (avg, max, min)"""

    avg: float
    max: float
    min: float


class ServerSummaryResponse(BaseModel):
    """Server summary statistics"""

    server_id: int
    period: str
    data_points: int
    cpu: ResourceStats
    memory: ResourceStats
    players: ResourceStats


class MapPopularityResponse(BaseModel):
    """Map popularity data"""

    map: str
    hours_played: int


class PeakHourResponse(BaseModel):
    """Peak hour data"""

    hour: int
    avg_players: float
    data_points: int


class PlayerSessionResponse(BaseModel):
    """Player session data"""

    player_name: str | None
    steam_id: str | None
    join_time: str | None
    leave_time: str | None
    duration_seconds: int | None
    kills: int
    deaths: int
    score: int


class PlayerRetentionResponse(BaseModel):
    """Player retention statistics"""

    period_days: int
    unique_players: int
    new_players: int
    returning_players: int
    retention_rate: float


class HourlyTrendResponse(BaseModel):
    """Hourly trend data"""

    timestamp: str
    avg_players: float
    max_players: int
    min_players: int
    unique_players: int
    most_played_map: str | None
    uptime_percent: float


# ============================================
# Helper Functions
# ============================================


def check_server_ownership(server_id: int, user: User, db: Session):
    """Check if user owns the server"""
    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(404, f"Server not found: {server_id}")

    if server.owner_id != user.id:
        raise HTTPException(403, "You don't own this server")

    return server


# ============================================
# API Endpoints
# ============================================


@router.get("/servers/{server_id}/timeseries", response_model=TimeseriesResponse)
async def get_server_timeseries(
    server_id: int,
    hours: int = Query(24, ge=1, le=720, description="Time range in hours (max 30 days)"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get time-series metrics for a server.

    **Time Ranges:**
    - 24 hours: Last day (5-minute intervals)
    - 168 hours: Last week
    - 720 hours: Last 30 days

    **Returns:**
    - Timestamp
    - CPU usage %
    - Memory usage MB
    - Player count
    - Process status

    **Use Case:** Chart.js line graphs for dashboard
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = AnalyticsService(db)
    data = service.get_timeseries_data(server_id, hours)

    return TimeseriesResponse(
        server_id=server_id,
        period_hours=hours,
        data_points=len(data),
        data=[TimeseriesDataPoint(**d) for d in data],
    )


@router.get("/servers/{server_id}/summary", response_model=ServerSummaryResponse)
async def get_server_summary(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get aggregated server summary (last 24 hours).

    **Returns:**
    - CPU: avg, max, min
    - Memory: avg, max, min
    - Players: avg, max, min

    **Use Case:** Dashboard KPI cards
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = AnalyticsService(db)
    summary = service.get_server_summary(server_id)

    return ServerSummaryResponse(
        server_id=summary["server_id"],
        period=summary["period"],
        data_points=summary["data_points"],
        cpu=ResourceStats(**summary["cpu"]),
        memory=ResourceStats(**summary["memory"]),
        players=ResourceStats(**summary["players"]),
    )


@router.get("/servers/{server_id}/maps/popular", response_model=List[MapPopularityResponse])
async def get_popular_maps(
    server_id: int,
    days: int = Query(7, ge=1, le=30, description="Time range in days"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get most popular maps by play time.

    **Returns:**
    - Top 10 maps
    - Hours played per map

    **Use Case:** Bar chart for map popularity
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = AnalyticsService(db)
    maps = service.get_popular_maps(server_id, days)

    return [MapPopularityResponse(**m) for m in maps]


@router.get("/servers/{server_id}/peak-hours", response_model=List[PeakHourResponse])
async def get_peak_hours(
    server_id: int,
    days: int = Query(7, ge=1, le=30, description="Time range in days"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get peak player activity hours (0-23).

    **Returns:**
    - Average players per hour
    - Data points per hour

    **Use Case:** Heatmap or bar chart for peak hours
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = AnalyticsService(db)
    peak_hours = service.get_peak_hours(server_id, days)

    return [PeakHourResponse(**h) for h in peak_hours]


@router.get("/servers/{server_id}/players/sessions", response_model=List[PlayerSessionResponse])
async def get_player_sessions(
    server_id: int,
    days: int = Query(7, ge=1, le=30, description="Time range in days"),
    limit: int = Query(100, ge=1, le=500, description="Max sessions to return"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get recent player sessions.

    **Returns:**
    - Player name, Steam ID
    - Join/leave time
    - Duration
    - Kills, deaths, score

    **Use Case:** Player activity table
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = AnalyticsService(db)
    sessions = service.get_player_sessions(server_id, days, limit)

    return [PlayerSessionResponse(**s) for s in sessions]


@router.get("/servers/{server_id}/players/retention", response_model=PlayerRetentionResponse)
async def get_player_retention(
    server_id: int,
    days: int = Query(30, ge=7, le=90, description="Time range in days"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get player retention statistics.

    **Returns:**
    - Unique players
    - New vs returning players
    - Retention rate %

    **Use Case:** Player engagement metrics
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = AnalyticsService(db)
    retention = service.get_player_retention(server_id, days)

    return PlayerRetentionResponse(**retention)


@router.get("/servers/{server_id}/trends/hourly", response_model=List[HourlyTrendResponse])
async def get_hourly_trends(
    server_id: int,
    days: int = Query(7, ge=1, le=30, description="Time range in days"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get hourly statistics trends.

    **Returns:**
    - Hourly aggregated player stats
    - Most played map per hour
    - Uptime percentage

    **Use Case:** Detailed trend analysis
    """
    # Check ownership
    check_server_ownership(server_id, current_user, db)

    service = AnalyticsService(db)
    trends = service.get_hourly_trends(server_id, days)

    return [HourlyTrendResponse(**t) for t in trends]
