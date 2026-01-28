"""
AGTR Merkezi - Forum Replies API
Reply management for topics
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
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
from app.models.database import ForumReply, ForumTopic, User

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# Request/Response Models
# ============================================


class ReplyCreateRequest(BaseModel):
    """Reply creation request"""

    content: str = Field(..., min_length=5, max_length=10000)
    topic_id: int


class ReplyUpdateRequest(BaseModel):
    """Reply update request"""

    content: str = Field(..., min_length=5, max_length=10000)


class ReplyResponse(BaseModel):
    """Reply response model"""

    id: int
    content: str
    topic_id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Relationships
    author: Optional[dict] = None

    class Config:
        from_attributes = True


# ============================================
# Endpoints
# ============================================


@router.get("/topic/{topic_id}", response_model=dict)
async def get_topic_replies(
    topic_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Get replies for a topic with pagination"""
    try:
        # Validate topic exists
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Build query
        query = (
            db.query(ForumReply)
            .filter(ForumReply.topic_id == topic_id)
            .order_by(ForumReply.created_at)
        )

        # Get total count
        total = query.count()

        # Pagination
        page, per_page = validate_pagination(page, per_page)
        offset = (page - 1) * per_page

        replies = query.offset(offset).limit(per_page).all()

        # Format response
        reply_data = []
        for reply in replies:
            reply_dict = {
                "id": reply.id,
                "content": reply.content,
                "created_at": reply.created_at.isoformat(),
                "updated_at": reply.updated_at.isoformat() if reply.updated_at else None,
                "author": (
                    {
                        "id": reply.author.id,
                        "username": reply.author.username,
                        "role": reply.author.role,
                        "post_count": getattr(reply.author, "post_count", 0),
                    }
                    if reply.author
                    else None
                ),
            }
            reply_data.append(reply_dict)

        return paginated_response(reply_data, total, page, per_page)

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching replies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ReplyResponse, status_code=201)
async def create_reply(
    request: ReplyCreateRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Create new reply"""
    try:
        log_api_call("create_reply", current_user.id)

        # Validate topic exists
        topic = db.query(ForumTopic).filter(ForumTopic.id == request.topic_id).first()

        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Check if topic is locked
        if topic.is_locked and not current_user.is_admin:
            raise ForbiddenError("Bu konu kilitli, yeni yanıt eklenemez")

        # Create reply
        reply = ForumReply(
            content=request.content, topic_id=request.topic_id, author_id=current_user.id
        )

        db.add(reply)

        # Increment topic reply count
        topic.reply_count += 1

        db.commit()
        db.refresh(reply)

        return reply

    except (BadRequestError, ForbiddenError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Error creating reply: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{reply_id}", response_model=ReplyResponse)
async def update_reply(
    reply_id: int,
    request: ReplyUpdateRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Update reply"""
    try:
        reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()

        if not reply:
            raise NotFoundError("Yanıt bulunamadı")

        # Check permissions
        if reply.author_id != current_user.id and not current_user.is_admin:
            raise ForbiddenError("Bu yanıtı düzenleme yetkiniz yok")

        # Update content
        reply.content = request.content
        reply.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(reply)

        return reply

    except (NotFoundError, ForbiddenError):
        raise
    except Exception as e:
        logger.error(f"Error updating reply: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{reply_id}")
async def delete_reply(
    reply_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Delete reply"""
    try:
        reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()

        if not reply:
            raise NotFoundError("Yanıt bulunamadı")

        # Check permissions
        if reply.author_id != current_user.id and not current_user.is_admin:
            raise ForbiddenError("Bu yanıtı silme yetkiniz yok")

        # Get topic to decrement count
        topic = db.query(ForumTopic).filter(ForumTopic.id == reply.topic_id).first()

        if topic:
            topic.reply_count = max(0, topic.reply_count - 1)

        db.delete(reply)
        db.commit()

        return success_response(message="Yanıt silindi")

    except (NotFoundError, ForbiddenError):
        raise
    except Exception as e:
        logger.error(f"Error deleting reply: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
