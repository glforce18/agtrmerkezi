"""
AGTR Merkezi - Forum Replies API
Reply management for topics
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

        # Build query - best answer first, then chronological
        query = (
            db.query(ForumReply)
            .filter(ForumReply.topic_id == topic_id)
            .order_by(desc(ForumReply.is_best_answer), ForumReply.created_at)
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
            # Check if user liked this reply
            is_liked = False
            if current_user:
                from app.models.database import ForumReplyLike

                is_liked = (
                    db.query(ForumReplyLike)
                    .filter(
                        ForumReplyLike.reply_id == reply.id,
                        ForumReplyLike.user_id == current_user.id,
                    )
                    .first()
                    is not None
                )

            reply_dict = {
                "id": reply.id,
                "content": reply.content,
                "parent_reply_id": reply.parent_reply_id,
                "is_best_answer": reply.is_best_answer or False,
                "likes": reply.likes or 0,
                "is_liked": is_liked,
                "created_at": reply.created_at.isoformat() if reply.created_at else None,
                "updated_at": reply.updated_at.isoformat() if reply.updated_at else None,
                "author": (
                    {
                        "id": reply.author.id,
                        "username": reply.author.username,
                        "role": reply.author.role,
                        "avatar": reply.author.steam_avatar,
                        "steam_id": reply.author.steam_id,
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
            content=request.content, topic_id=request.topic_id, user_id=current_user.id
        )

        db.add(reply)

        # Increment topic reply count (handle NULL)
        topic.reply_count = (topic.reply_count or 0) + 1

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
            topic.reply_count = max(0, (topic.reply_count or 0) - 1)

        db.delete(reply)
        db.commit()

        return success_response(message="Yanıt silindi")

    except (NotFoundError, ForbiddenError):
        raise
    except Exception as e:
        logger.error(f"Error deleting reply: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{reply_id}/like")
async def like_reply(
    reply_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Like a reply"""
    try:
        log_api_call("like_reply", current_user.id)

        # Get reply
        reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
        if not reply:
            raise NotFoundError("Yanıt bulunamadı")

        # Check if already liked
        from app.models.database import ForumReplyLike

        existing_like = (
            db.query(ForumReplyLike)
            .filter(ForumReplyLike.reply_id == reply_id, ForumReplyLike.user_id == current_user.id)
            .first()
        )

        if existing_like:
            return success_response(
                message="Zaten beğenilmiş", data={"likes": reply.likes or 0, "is_liked": True}
            )

        # Add like
        new_like = ForumReplyLike(reply_id=reply_id, user_id=current_user.id)
        db.add(new_like)

        # Update count
        reply.likes = (reply.likes or 0) + 1
        db.commit()

        return success_response(message="Beğenildi", data={"likes": reply.likes, "is_liked": True})

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error liking reply: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{reply_id}/like")
async def unlike_reply(
    reply_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Unlike a reply"""
    try:
        log_api_call("unlike_reply", current_user.id)

        # Get reply
        reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
        if not reply:
            raise NotFoundError("Yanıt bulunamadı")

        # Check if liked
        from app.models.database import ForumReplyLike

        existing_like = (
            db.query(ForumReplyLike)
            .filter(ForumReplyLike.reply_id == reply_id, ForumReplyLike.user_id == current_user.id)
            .first()
        )

        if not existing_like:
            return success_response(
                message="Zaten beğenilmemiş", data={"likes": reply.likes or 0, "is_liked": False}
            )

        # Remove like
        db.delete(existing_like)

        # Update count
        reply.likes = max(0, (reply.likes or 0) - 1)
        db.commit()

        return success_response(
            message="Beğeni kaldırıldı", data={"likes": reply.likes, "is_liked": False}
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error unliking reply: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{reply_id}/best")
async def mark_best_answer(
    reply_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Mark reply as best answer (topic author only)"""
    try:
        log_api_call("mark_best_answer", current_user.id)

        # Get reply
        reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
        if not reply:
            raise NotFoundError("Yanıt bulunamadı")

        # Get topic
        topic = db.query(ForumTopic).filter(ForumTopic.id == reply.topic_id).first()
        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Check permission (only topic author)
        if topic.author_id != current_user.id and not current_user.is_admin:
            raise ForbiddenError("Sadece konu sahibi en iyi cevabı işaretleyebilir")

        # Unmark other best answers in this topic
        db.query(ForumReply).filter(
            ForumReply.topic_id == topic.id, ForumReply.id != reply_id
        ).update({"is_best_answer": False})

        # Mark this as best answer
        reply.is_best_answer = True
        topic.is_solved = True
        db.commit()

        return success_response(message="En iyi cevap işaretlendi")

    except (NotFoundError, ForbiddenError):
        raise
    except Exception as e:
        logger.error(f"Error marking best answer: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{reply_id}/best")
async def unmark_best_answer(
    reply_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Unmark reply as best answer"""
    try:
        log_api_call("unmark_best_answer", current_user.id)

        # Get reply
        reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
        if not reply:
            raise NotFoundError("Yanıt bulunamadı")

        # Get topic
        topic = db.query(ForumTopic).filter(ForumTopic.id == reply.topic_id).first()
        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Check permission
        if topic.author_id != current_user.id and not current_user.is_admin:
            raise ForbiddenError("Sadece konu sahibi en iyi cevap işaretini kaldırabilir")

        # Unmark
        reply.is_best_answer = False

        # Check if there are other best answers
        has_other_best = (
            db.query(ForumReply)
            .filter(ForumReply.topic_id == topic.id, ForumReply.is_best_answer)
            .first()
        )

        if not has_other_best:
            topic.is_solved = False

        db.commit()

        return success_response(message="En iyi cevap işareti kaldırıldı")

    except (NotFoundError, ForbiddenError):
        raise
    except Exception as e:
        logger.error(f"Error unmarking best answer: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
