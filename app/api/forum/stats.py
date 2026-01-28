"""
AGTR Merkezi - Forum Stats & General Endpoints
Forum statistics, trending topics, bookmarks
"""

import json
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.cache import redis_manager
from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import ForumReply, ForumSubscription, ForumTopic, User

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# Forum Stats
# ============================================


@router.get("/stats")
async def get_forum_stats(db: Session = Depends(get_db)):
    """
    Forum genel istatistikleri - Ana sayfa için

    Cache: 60 saniye
    """
    cache_key = "forum:stats"

    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    try:
        # Online kullanıcı sayısı (son 5 dakika)
        since_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        online_count = (
            db.query(func.count(User.id)).filter(User.last_seen >= since_time).scalar() or 0
        )

        # Toplam konu sayısı
        total_topics = (
            db.query(func.count(ForumTopic.id)).filter(ForumTopic.is_active).scalar() or 0
        )

        # Bugün oluşturulan konu sayısı
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        topics_today = (
            db.query(func.count(ForumTopic.id))
            .filter(ForumTopic.is_active, ForumTopic.created_at >= today_start)
            .scalar()
            or 0
        )

        # Toplam yanıt sayısı
        total_replies = (
            db.query(func.count(ForumReply.id)).filter(ForumReply.is_active).scalar() or 0
        )

        result = {
            "success": True,
            "data": {
                "online_users": online_count,
                "total_topics": total_topics,
                "topics_today": topics_today,
                "total_replies": total_replies,
                "total_users": db.query(func.count(User.id)).scalar() or 0,
            },
        }

        # 60 saniye cache
        try:
            await redis_manager.set(cache_key, json.dumps(result), expire=60)
        except Exception:
            pass

        return result

    except Exception as e:
        logger.error(f"Forum stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Forum istatistikleri alınamadı",
        )


# ============================================
# Trending Topics
# ============================================


@router.get("/trending")
async def get_trending_topics(
    days: int = Query(default=7, le=30),
    limit: int = Query(default=5, le=20),
    db: Session = Depends(get_db),
):
    """
    Belirli gün sayısı içinde en popüler konular

    Cache: 60 saniye
    Metrikler: view_count, reply_count, likes
    """
    cache_key = f"forum:trending:{days}:{limit}"

    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    try:
        # Son X gün içindeki konular
        since_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Popularity score hesapla: views*1 + replies*3 + likes*5
        topics = (
            db.query(ForumTopic)
            .options(joinedload(ForumTopic.author), joinedload(ForumTopic.category))
            .filter(ForumTopic.is_active, ForumTopic.created_at >= since_date)
            .order_by(
                (
                    func.coalesce(ForumTopic.view_count, 0) * 1
                    + func.coalesce(ForumTopic.reply_count, 0) * 3
                    + func.coalesce(ForumTopic.likes, 0) * 5
                ).desc()
            )
            .limit(limit)
            .all()
        )

        topic_data = []
        for topic in topics:
            topic_dict = {
                "id": topic.id,
                "title": topic.title,
                "slug": topic.slug,
                "view_count": topic.view_count or 0,
                "reply_count": topic.reply_count or 0,
                "likes": topic.likes or 0,
                "created_at": topic.created_at.isoformat() if topic.created_at else None,
                "author": (
                    {
                        "id": topic.author.id,
                        "username": topic.author.username,
                        "role": topic.author.role,
                        "avatar": topic.author.steam_avatar,
                        "steam_id": topic.author.steam_id,
                    }
                    if topic.author
                    else None
                ),
                "category": (
                    {
                        "id": topic.category.id,
                        "name": topic.category.name,
                        "slug": topic.category.slug,
                    }
                    if topic.category
                    else None
                ),
            }
            topic_data.append(topic_dict)

        result = {
            "success": True,
            "data": topic_data,
            "days": days,
        }

        # 60 saniye cache
        try:
            await redis_manager.set(cache_key, json.dumps(result), expire=60)
        except Exception:
            pass

        return result

    except Exception as e:
        logger.error(f"Trending topics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Trend konular alınamadı"
        )


# ============================================
# Bookmarks
# ============================================


@router.get("/bookmarks")
async def get_bookmarks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Kullanıcının kaydettiği konuları listele
    """
    try:
        # Get bookmarked topic IDs (using subscriptions as bookmarks)
        query = (
            db.query(ForumTopic)
            .join(ForumSubscription, ForumSubscription.topic_id == ForumTopic.id)
            .filter(ForumSubscription.user_id == current_user.id)
            .filter(ForumTopic.is_active)
            .options(joinedload(ForumTopic.author), joinedload(ForumTopic.category))
            .order_by(ForumSubscription.created_at.desc())
        )

        # Get total count
        total = query.count()

        # Pagination
        offset = (page - 1) * per_page
        topics = query.offset(offset).limit(per_page).all()

        # Format response
        topic_data = []
        for topic in topics:
            topic_dict = {
                "id": topic.id,
                "title": topic.title,
                "slug": topic.slug,
                "content": topic.content,
                "view_count": topic.view_count or 0,
                "reply_count": topic.reply_count or 0,
                "likes": topic.likes or 0,
                "is_pinned": topic.is_pinned or False,
                "is_locked": topic.is_locked or False,
                "is_solved": topic.is_solved or False,
                "created_at": topic.created_at.isoformat() if topic.created_at else None,
                "updated_at": topic.updated_at.isoformat() if topic.updated_at else None,
                "author": (
                    {
                        "id": topic.author.id,
                        "username": topic.author.username,
                        "role": topic.author.role,
                        "avatar": topic.author.steam_avatar,
                        "steam_id": topic.author.steam_id,
                    }
                    if topic.author
                    else None
                ),
                "category": (
                    {
                        "id": topic.category.id,
                        "name": topic.category.name,
                        "slug": topic.category.slug,
                    }
                    if topic.category
                    else None
                ),
            }
            topic_data.append(topic_dict)

        return {
            "success": True,
            "data": topic_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
            },
        }

    except Exception as e:
        logger.error(f"Error fetching bookmarks: {e}")
        raise HTTPException(status_code=500, detail=str(e))
