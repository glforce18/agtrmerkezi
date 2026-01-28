"""
AGTR Merkezi v6.1 - Crash Statistics API
View crash stats and manage auto-restart after storms
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import GameServer, User
from app.services.respawn_monitor import RespawnMonitor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/servers", tags=["Crash Detection"])


# ============================================
# Response Models
# ============================================


class CrashStatsResponse(BaseModel):
    """Server crash statistics"""

    server_id: int
    crash_count: int
    last_crash: str | None
    storm_detected: bool
    auto_restart_enabled: bool
    in_backoff: bool
    backoff_remaining_seconds: int | None
    restart_allowed: bool


class ReEnableAutoRestartResponse(BaseModel):
    """Re-enable auto-restart response"""

    success: bool
    message: str
    auto_restart_enabled: bool


# ============================================
# Helper Functions
# ============================================


def verify_server_access(server_id: int, user: User, db: Session) -> GameServer:
    """Verify user has access to server"""
    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Check ownership (or admin access)
    if server.owner_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied to this server")

    return server


# ============================================
# API Endpoints
# ============================================


@router.get("/{server_id}/crash-stats", response_model=CrashStatsResponse)
async def get_crash_stats(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get crash statistics for server.

    Shows:
    - Crash count in last 10 minutes
    - Last crash time
    - Storm detection status
    - Auto-restart enabled/disabled
    - Backoff period remaining

    **Storm Detection:**
    - Triggered after 5 crashes in 10 minutes
    - Auto-restart automatically disabled
    - Manual re-enable required
    """
    # Verify access
    server = verify_server_access(server_id, current_user, db)

    # Get crash stats
    monitor = RespawnMonitor(db)
    stats = monitor.get_crash_stats(server)

    return CrashStatsResponse(server_id=server_id, **stats)


@router.post("/{server_id}/re-enable-auto-restart", response_model=ReEnableAutoRestartResponse)
async def re_enable_auto_restart(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Re-enable auto-restart after crash storm.

    **Requirements:**
    - Storm must have cooled down (crash count reset)
    - Only owner or admin can re-enable

    **Use Case:**
    1. Server crashes 5+ times in 10 minutes
    2. Auto-restart disabled automatically
    3. Owner investigates and fixes issue
    4. Owner calls this endpoint to re-enable auto-restart
    """
    # Verify access
    server = verify_server_access(server_id, current_user, db)

    # Check if already enabled
    if server.auto_restart:
        return ReEnableAutoRestartResponse(
            success=True,
            message="Auto-restart is already enabled",
            auto_restart_enabled=True,
        )

    # Try to re-enable
    monitor = RespawnMonitor(db)
    success = monitor.re_enable_auto_restart(server)

    if success:
        return ReEnableAutoRestartResponse(
            success=True,
            message="Auto-restart re-enabled successfully. Crash tracking reset.",
            auto_restart_enabled=True,
        )
    else:
        # Storm still active
        stats = monitor.get_crash_stats(server)
        return ReEnableAutoRestartResponse(
            success=False,
            message=(
                f"Cannot re-enable: Crash storm still active "
                f"({stats['crash_count']} crashes in last 10 minutes). "
                f"Wait for crashes to cool down or contact support."
            ),
            auto_restart_enabled=False,
        )


@router.post("/{server_id}/reset-crash-tracking")
async def reset_crash_tracking(
    server_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Manually reset crash tracking (admin only).

    **Admin Only**

    Use this to force reset crash counter and backoff timer.
    """
    # Verify access
    server = verify_server_access(server_id, current_user, db)

    # Admin only
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Reset
    monitor = RespawnMonitor(db)
    monitor.reset_crash_tracking(server)

    return {
        "success": True,
        "message": "Crash tracking reset successfully",
        "crash_count": 0,
        "restart_backoff_until": None,
    }
