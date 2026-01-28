"""
AGTR Merkezi - Admin Dashboard API
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import (
    GameServer,
    Payment,
    PaymentStatus,
    ServerStatus,
    User,
    UserStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["Admin Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """Dashboard ana istatistikleri"""
    try:
        total_users = db.query(func.count(User.id)).scalar() or 0
        today = datetime.utcnow().date()
        new_users_today = (
            db.query(func.count(User.id)).filter(func.date(User.created_at) == today).scalar() or 0
        )
        active_users = (
            db.query(func.count(User.id)).filter(User.status == UserStatus.ACTIVE).scalar() or 0
        )
        total_servers = (
            db.query(func.count(GameServer.id))
            .filter(GameServer.status != ServerStatus.DELETED)
            .scalar()
            or 0
        )
        running_servers = (
            db.query(func.count(GameServer.id))
            .filter(GameServer.status == ServerStatus.RUNNING)
            .scalar()
            or 0
        )
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        revenue_this_month = (
            db.query(func.sum(Payment.amount))
            .filter(Payment.status == PaymentStatus.COMPLETED, Payment.completed_at >= month_start)
            .scalar()
            or 0
        )

        return {
            "users": {
                "total": total_users,
                "new_today": new_users_today,
                "online": 0,
                "active": active_users,
            },
            "servers": {
                "total": total_servers,
                "running": running_servers,
                "stopped": total_servers - running_servers,
                "uptime_percentage": (
                    round((running_servers / total_servers * 100), 1) if total_servers > 0 else 0
                ),
            },
            "players": {"online": 0},
            "revenue": {"month": float(revenue_this_month), "today": 0, "payments_month": 0},
            "forum": {"total_topics": 0, "total_posts": 0, "topics_today": 0},
            "system": {"health_score": 95.0, "status": "operational"},
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return {
            "users": {"total": 0, "new_today": 0, "online": 0, "active": 0},
            "servers": {"total": 0, "running": 0, "stopped": 0, "uptime_percentage": 0},
            "players": {"online": 0},
            "revenue": {"month": 0, "today": 0, "payments_month": 0},
            "forum": {"total_topics": 0, "total_posts": 0, "topics_today": 0},
            "system": {"health_score": 0, "status": "error"},
        }


@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Son aktiviteler"""
    return {"activities": []}


@router.get("/top-users")
async def get_top_users(
    limit: int = Query(10, ge=1, le=50),
    metric: str = Query("servers", pattern="^(servers|revenue|reputation|posts)$"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Top users"""
    return {"metric": metric, "users": []}
