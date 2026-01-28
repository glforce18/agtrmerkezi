"""
AGTR Merkezi - Forum Topics API
Topic creation, listing, and management
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.common import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    log_api_call,
    paginated_response,
    success_response,
    validate_pagination,
)
from app.core.security import get_current_user_optional, get_current_user_required
from app.models.connection import get_db
from app.models.database import (
    ForumBookmark,
    ForumCategory,
    ForumTopic,
    ForumTopicLike,
    User,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# Request/Response Models
# ============================================


class TopicCreateRequest(BaseModel):
    """Topic creation request"""

    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10, max_length=50000)
    category_id: int
    is_pinned: bool = False
    is_locked: bool = False


class TopicUpdateRequest(BaseModel):
    """Topic update request"""

    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=50000)
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None


class TopicResponse(BaseModel):
    """Topic response model"""

    id: int
    title: str
    slug: str
    content: str
    category_id: int
    author_id: int
    view_count: int = 0
    reply_count: int = 0
    is_pinned: Optional[bool] = False
    is_locked: Optional[bool] = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Relationships
    author: Optional[dict] = None
    category: Optional[dict] = None

    class Config:
        from_attributes = True


# ============================================
# Endpoints
# ============================================


@router.get("", response_model=dict)
async def get_topics(
    category_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: str = Query("recent", pattern="^(recent|popular|replies|views)$"),
    search: Optional[str] = Query(None, max_length=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Get topics with filtering and pagination"""
    try:
        log_api_call("get_topics", current_user.id if current_user else None)

        # Build query
        query = db.query(ForumTopic)

        # Filter by category
        if category_id:
            query = query.filter(ForumTopic.category_id == category_id)

        # Search
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (ForumTopic.title.ilike(search_term)) | (ForumTopic.content.ilike(search_term))
            )

        # Sorting - Pinned topics first, then by selected sort
        if sort == "popular":
            query = query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.view_count))
        elif sort == "replies":
            query = query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.reply_count))
        elif sort == "views":
            query = query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.view_count))
        else:  # recent
            query = query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.created_at))

        # Get total count
        total = query.count()

        # Pagination
        page, per_page = validate_pagination(page, per_page)
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

        return paginated_response(topic_data, total, page, per_page)

    except Exception as e:
        logger.error(f"Error fetching topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{slug_or_id}", response_model=TopicResponse)
async def get_topic(
    slug_or_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Get topic by slug or ID and increment view count"""
    try:
        # Try to parse as ID first
        if slug_or_id.isdigit():
            topic = db.query(ForumTopic).filter(ForumTopic.id == int(slug_or_id)).first()
        else:
            topic = db.query(ForumTopic).filter(ForumTopic.slug == slug_or_id).first()

        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Increment view count (handle None case)
        if topic.view_count is None:
            topic.view_count = 1
        else:
            topic.view_count += 1
        db.commit()

        # Check if user liked this topic
        is_liked = False
        is_bookmarked = False
        if current_user:
            is_liked = (
                db.query(ForumTopicLike)
                .filter(
                    ForumTopicLike.topic_id == topic.id, ForumTopicLike.user_id == current_user.id
                )
                .first()
                is not None
            )
            is_bookmarked = (
                db.query(ForumBookmark)
                .filter(
                    ForumBookmark.topic_id == topic.id, ForumBookmark.user_id == current_user.id
                )
                .first()
                is not None
            )

        # Format response with relationships serialized before Pydantic validation
        topic_dict = {
            "id": topic.id,
            "title": topic.title,
            "slug": topic.slug,
            "content": topic.content,
            "category_id": topic.category_id,
            "author_id": topic.author_id,
            "view_count": topic.view_count or 0,
            "reply_count": topic.reply_count or 0,
            "likes": topic.likes or 0,
            "is_liked": is_liked,
            "is_bookmarked": is_bookmarked,
            "is_pinned": topic.is_pinned or False,
            "is_locked": topic.is_locked or False,
            "is_solved": topic.is_solved or False,
            "created_at": topic.created_at,
            "updated_at": topic.updated_at,
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
                {"id": topic.category.id, "name": topic.category.name, "slug": topic.category.slug}
                if topic.category
                else None
            ),
        }

        return TopicResponse(**topic_dict)

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=TopicResponse, status_code=201)
async def create_topic(
    request: TopicCreateRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Create new topic"""
    try:
        log_api_call("create_topic", current_user.id)

        # Validate category exists
        category = db.query(ForumCategory).filter(ForumCategory.id == request.category_id).first()

        if not category:
            raise BadRequestError("Geçersiz kategori")

        # Generate slug
        from slugify import slugify

        base_slug = slugify(request.title)
        slug = base_slug
        counter = 1

        # Ensure unique slug
        while db.query(ForumTopic).filter(ForumTopic.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Create topic
        topic = ForumTopic(
            title=request.title,
            slug=slug,
            content=request.content,
            category_id=request.category_id,
            author_id=current_user.id,
            is_pinned=request.is_pinned if current_user.is_admin else False,
            is_locked=request.is_locked if current_user.is_admin else False,
        )

        db.add(topic)
        db.commit()
        db.refresh(topic)

        return topic

    except (BadRequestError, ForbiddenError):
        raise
    except Exception as e:
        logger.error(f"Error creating topic: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    request: TopicUpdateRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Update topic"""
    try:
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()

        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Check permissions
        if topic.author_id != current_user.id and not current_user.is_admin:
            raise ForbiddenError("Bu konuyu düzenleme yetkiniz yok")

        # Update fields
        if request.title:
            topic.title = request.title
        if request.content:
            topic.content = request.content

        # Only admins can pin/lock
        if current_user.is_admin:
            if request.is_pinned is not None:
                topic.is_pinned = request.is_pinned
            if request.is_locked is not None:
                topic.is_locked = request.is_locked

        topic.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(topic)

        return topic

    except (NotFoundError, ForbiddenError):
        raise
    except Exception as e:
        logger.error(f"Error updating topic: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{topic_id}")
async def delete_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Delete topic"""
    try:
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()

        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Check permissions
        if topic.author_id != current_user.id and not current_user.is_admin:
            raise ForbiddenError("Bu konuyu silme yetkiniz yok")

        db.delete(topic)
        db.commit()

        return success_response(message="Konu silindi")

    except (NotFoundError, ForbiddenError):
        raise
    except Exception as e:
        logger.error(f"Error deleting topic: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}/like")
async def like_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Like a topic"""
    try:
        log_api_call("like_topic", current_user.id)

        # Get topic
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Check if already liked
        existing_like = (
            db.query(ForumTopicLike)
            .filter(ForumTopicLike.topic_id == topic_id, ForumTopicLike.user_id == current_user.id)
            .first()
        )

        if existing_like:
            return success_response(
                message="Zaten beğenilmiş", data={"likes": topic.likes or 0, "is_liked": True}
            )

        # Add like
        new_like = ForumTopicLike(topic_id=topic_id, user_id=current_user.id)
        db.add(new_like)

        # Update count
        topic.likes = (topic.likes or 0) + 1
        db.commit()

        return success_response(message="Beğenildi", data={"likes": topic.likes, "is_liked": True})

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error liking topic: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{topic_id}/like")
async def unlike_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Unlike a topic"""
    try:
        log_api_call("unlike_topic", current_user.id)

        # Get topic
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Check if liked
        existing_like = (
            db.query(ForumTopicLike)
            .filter(ForumTopicLike.topic_id == topic_id, ForumTopicLike.user_id == current_user.id)
            .first()
        )

        if not existing_like:
            return success_response(
                message="Zaten beğenilmemiş", data={"likes": topic.likes or 0, "is_liked": False}
            )

        # Remove like
        db.delete(existing_like)

        # Update count
        topic.likes = max(0, (topic.likes or 0) - 1)
        db.commit()

        return success_response(
            message="Beğeni kaldırıldı", data={"likes": topic.likes, "is_liked": False}
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error unliking topic: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}/bookmark")
async def bookmark_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Bookmark a topic"""
    try:
        log_api_call("bookmark_topic", current_user.id)

        # Get topic
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Check if already bookmarked
        existing_bookmark = (
            db.query(ForumBookmark)
            .filter(ForumBookmark.topic_id == topic_id, ForumBookmark.user_id == current_user.id)
            .first()
        )

        if existing_bookmark:
            return success_response(message="Zaten kaydedilmiş", data={"is_bookmarked": True})

        # Add bookmark
        new_bookmark = ForumBookmark(topic_id=topic_id, user_id=current_user.id)
        db.add(new_bookmark)
        db.commit()

        return success_response(message="Kaydedildi", data={"is_bookmarked": True})

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error bookmarking topic: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{topic_id}/bookmark")
async def unbookmark_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Remove bookmark from a topic"""
    try:
        log_api_call("unbookmark_topic", current_user.id)

        # Get topic
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Check if bookmarked
        existing_bookmark = (
            db.query(ForumBookmark)
            .filter(ForumBookmark.topic_id == topic_id, ForumBookmark.user_id == current_user.id)
            .first()
        )

        if not existing_bookmark:
            return success_response(message="Zaten kaydedilmemiş", data={"is_bookmarked": False})

        # Remove bookmark
        db.delete(existing_bookmark)
        db.commit()

        return success_response(message="Kayıt kaldırıldı", data={"is_bookmarked": False})

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error unbookmarking topic: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
