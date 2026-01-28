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
from app.models.database import ForumCategory, ForumTopic, User

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

        # Sorting
        if sort == "popular":
            query = query.order_by(desc(ForumTopic.view_count))
        elif sort == "replies":
            query = query.order_by(desc(ForumTopic.reply_count))
        elif sort == "views":
            query = query.order_by(desc(ForumTopic.view_count))
        else:  # recent
            query = query.order_by(desc(ForumTopic.created_at))

        # Pinned topics first
        query = query.order_by(desc(ForumTopic.is_pinned))

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
                "view_count": topic.view_count,
                "reply_count": topic.reply_count,
                "is_pinned": topic.is_pinned,
                "is_locked": topic.is_locked,
                "created_at": topic.created_at.isoformat(),
                "author": (
                    {"id": topic.author.id, "username": topic.author.username}
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

        # Increment view count
        topic.view_count += 1
        db.commit()

        # Format response with relationships serialized before Pydantic validation
        topic_dict = {
            "id": topic.id,
            "title": topic.title,
            "slug": topic.slug,
            "content": topic.content,
            "category_id": topic.category_id,
            "author_id": topic.author_id,
            "view_count": topic.view_count,
            "reply_count": topic.reply_count,
            "is_pinned": topic.is_pinned,
            "is_locked": topic.is_locked,
            "created_at": topic.created_at,
            "updated_at": topic.updated_at,
            "author": (
                {
                    "id": topic.author.id,
                    "username": topic.author.username,
                    "role": topic.author.role,
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
