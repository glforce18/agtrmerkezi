"""
🎮 AGTR Activity Feed API
Public activity stream for the platform
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.security import get_current_user, get_current_user_optional
from app.models.connection import get_db
from app.models.database import User

router = APIRouter()


# ============================================================================
# ACTIVITY TYPES
# ============================================================================

class ActivityType:
    # User activities
    USER_JOINED = "user_joined"
    USER_LEVEL_UP = "user_level_up"
    USER_ACHIEVEMENT = "user_achievement"

    # Social activities
    FRIEND_ADDED = "friend_added"
    CLAN_JOINED = "clan_joined"
    CLAN_CREATED = "clan_created"

    # Forum activities
    TOPIC_CREATED = "topic_created"
    POST_CREATED = "post_created"
    POST_LIKED = "post_liked"

    # Gaming activities
    SERVER_ONLINE = "server_online"
    TOURNAMENT_CREATED = "tournament_created"
    TOURNAMENT_WIN = "tournament_win"
    MATCH_PLAYED = "match_played"
    KILLSTREAK = "killstreak"

    # Shop activities
    PURCHASE = "purchase"
    VIP_ACTIVATED = "vip_activated"

    # System
    ANNOUNCEMENT = "announcement"


# ============================================================================
# DATABASE SETUP
# ============================================================================

def ensure_activity_tables(db: Session):
    """Aktivite tablolarını oluştur"""
    try:
        db.execute(text("""CREATE TABLE IF NOT EXISTS public_activities (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            activity_type VARCHAR(50) NOT NULL,
            message TEXT,
            data JSON,
            action_url VARCHAR(500),
            is_public BOOLEAN DEFAULT TRUE,
            is_highlighted BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_activity_type (activity_type),
            INDEX idx_activity_created (created_at),
            INDEX idx_activity_user (user_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        db.commit()
    except Exception:
        db.rollback()


# ============================================================================
# SCHEMAS
# ============================================================================

class ActivityCreate(BaseModel):
    activity_type: str
    message: Optional[str] = None
    data: Optional[dict] = None
    action_url: Optional[str] = None
    is_public: bool = True


class ActivityResponse(BaseModel):
    id: int
    activity_type: str
    message: Optional[str]
    data: Optional[dict]
    action_url: Optional[str]
    created_at: str
    user: Optional[dict]


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("")
async def get_activities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    types: Optional[str] = None,
    user_id: Optional[int] = None,
    friends_only: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """📋 Aktivite akışını getir"""
    ensure_activity_tables(db)

    offset = (page - 1) * limit
    params = {"limit": limit, "offset": offset}

    # Base query
    query = """
        SELECT
            a.id, a.activity_type, a.message, a.data, a.action_url,
            a.is_highlighted, a.created_at,
            u.id as user_id, u.username, u.avatar
        FROM public_activities a
        LEFT JOIN users u ON a.user_id = u.id
        WHERE a.is_public = TRUE
    """

    # Filter by types
    if types:
        type_list = [t.strip() for t in types.split(",")]
        placeholders = ", ".join([f":type_{i}" for i in range(len(type_list))])
        query += f" AND a.activity_type IN ({placeholders})"
        for i, t in enumerate(type_list):
            params[f"type_{i}"] = t

    # Filter by user
    if user_id:
        query += " AND a.user_id = :user_id"
        params["user_id"] = user_id

    # Friends only filter
    if friends_only and current_user:
        query += """
            AND (a.user_id IN (
                SELECT CASE
                    WHEN f.user_id = :current_uid THEN f.friend_id
                    ELSE f.user_id
                END
                FROM friendships f
                WHERE (f.user_id = :current_uid OR f.friend_id = :current_uid)
                AND f.status = 'accepted'
            ) OR a.user_id = :current_uid)
        """
        params["current_uid"] = current_user.id

    query += " ORDER BY a.created_at DESC LIMIT :limit OFFSET :offset"

    rows = db.execute(text(query), params).fetchall()

    activities = []
    for r in rows:
        activity = {
            "id": r[0],
            "type": r[1],
            "message": r[2],
            "data": r[3] if r[3] else {},
            "action_url": r[4],
            "highlighted": bool(r[5]),
            "created_at": r[6].isoformat() if r[6] else None,
            "user": {
                "id": r[7],
                "username": r[8],
                "avatar": r[9]
            } if r[7] else None
        }
        activities.append(activity)

    return {
        "success": True,
        "activities": activities,
        "page": page,
        "limit": limit,
        "has_more": len(activities) >= limit
    }


@router.get("/recent")
async def get_recent_activities(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """⚡ Son aktiviteleri getir (hızlı endpoint)"""
    ensure_activity_tables(db)

    rows = db.execute(text("""
        SELECT
            a.id, a.activity_type, a.message, a.data, a.created_at,
            u.id as user_id, u.username, u.avatar
        FROM public_activities a
        LEFT JOIN users u ON a.user_id = u.id
        WHERE a.is_public = TRUE
        ORDER BY a.created_at DESC
        LIMIT :limit
    """), {"limit": limit}).fetchall()

    activities = [{
        "id": r[0],
        "type": r[1],
        "message": r[2],
        "data": r[3] if r[3] else {},
        "created_at": r[4].isoformat() if r[4] else None,
        "user": {
            "id": r[5],
            "username": r[6],
            "avatar": r[7]
        } if r[5] else None
    } for r in rows]

    return {"success": True, "activities": activities}


@router.post("")
async def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """➕ Yeni aktivite oluştur"""
    ensure_activity_tables(db)

    import json

    result = db.execute(text("""
        INSERT INTO public_activities (user_id, activity_type, message, data, action_url, is_public)
        VALUES (:uid, :type, :msg, :data, :url, :public)
    """), {
        "uid": current_user.id,
        "type": activity.activity_type,
        "msg": activity.message,
        "data": json.dumps(activity.data) if activity.data else None,
        "url": activity.action_url,
        "public": activity.is_public
    })
    db.commit()

    return {"success": True, "id": result.lastrowid, "message": "Aktivite oluşturuldu"}


@router.get("/stats")
async def get_activity_stats(db: Session = Depends(get_db)):
    """📊 Aktivite istatistikleri"""
    ensure_activity_tables(db)

    # Son 24 saat
    stats = db.execute(text("""
        SELECT
            activity_type,
            COUNT(*) as count
        FROM public_activities
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        GROUP BY activity_type
        ORDER BY count DESC
    """)).fetchall()

    # Toplam sayılar
    totals = db.execute(text("""
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT user_id) as unique_users
        FROM public_activities
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """)).fetchone()

    return {
        "success": True,
        "stats": {
            "by_type": {r[0]: r[1] for r in stats},
            "total_activities": totals[0] if totals else 0,
            "unique_users": totals[1] if totals else 0
        }
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def log_activity(
    db: Session,
    activity_type: str,
    user_id: int = None,
    message: str = None,
    data: dict = None,
    action_url: str = None,
    is_public: bool = True
):
    """Aktivite logla (internal kullanım)"""
    ensure_activity_tables(db)

    import json

    try:
        db.execute(text("""
            INSERT INTO public_activities (user_id, activity_type, message, data, action_url, is_public)
            VALUES (:uid, :type, :msg, :data, :url, :public)
        """), {
            "uid": user_id,
            "type": activity_type,
            "msg": message,
            "data": json.dumps(data) if data else None,
            "url": action_url,
            "public": is_public
        })
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
