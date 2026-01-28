"""
AGTR Merkezi - Forum Moderation API
Moderation actions, reports, and admin controls
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.common import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    log_api_call,
    success_response,
)
from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import ForumReply, ForumReport, ForumTopic, User

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# Request/Response Models
# ============================================


class ReportCreateRequest(BaseModel):
    """Report creation request"""

    content_type: str = Field(..., pattern="^(topic|reply)$")
    content_id: int
    reason: str = Field(..., min_length=10, max_length=500)


class ReportResponse(BaseModel):
    """Report response model"""

    id: int
    content_type: str
    content_id: int
    reason: str
    status: str
    reporter_id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None

    class Config:
        from_attributes = True


class ModerationActionRequest(BaseModel):
    """Moderation action request"""

    action: str = Field(..., pattern="^(pin|unpin|lock|unlock)$")
    reason: Optional[str] = Field(None, max_length=200)


# ============================================
# Report Endpoints
# ============================================


@router.post("/reports", response_model=ReportResponse, status_code=201)
async def create_report(
    request: ReportCreateRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Create content report"""
    try:
        log_api_call("create_report", current_user.id)

        # Validate content exists
        if request.content_type == "topic":
            content = db.query(ForumTopic).filter(ForumTopic.id == request.content_id).first()
        else:
            content = db.query(ForumReply).filter(ForumReply.id == request.content_id).first()

        if not content:
            raise NotFoundError("İçerik bulunamadı")

        # Check if user already reported this content
        existing_report = (
            db.query(ForumReport)
            .filter(
                ForumReport.content_type == request.content_type,
                ForumReport.content_id == request.content_id,
                ForumReport.reporter_id == current_user.id,
                ForumReport.status == "pending",
            )
            .first()
        )

        if existing_report:
            raise BadRequestError("Bu içeriği zaten raporladınız")

        # Create report
        report = ForumReport(
            content_type=request.content_type,
            content_id=request.content_id,
            reason=request.reason,
            reporter_id=current_user.id,
            status="pending",
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        return report

    except (BadRequestError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    status: Optional[str] = Query(None, pattern="^(pending|resolved|dismissed)$"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get reports (admin only)"""
    try:
        if not current_user.is_admin:
            raise ForbiddenError("Bu işlem için yetkiniz yok")

        query = db.query(ForumReport)

        if status:
            query = query.filter(ForumReport.status == status)

        reports = query.order_by(desc(ForumReport.created_at)).all()
        return reports

    except ForbiddenError:
        raise
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/{report_id}/resolve")
async def resolve_report(
    report_id: int,
    action: str = Query(..., pattern="^(delete|dismiss)$"),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Resolve report (admin only)"""
    try:
        if not current_user.is_admin:
            raise ForbiddenError("Bu işlem için yetkiniz yok")

        report = db.query(ForumReport).filter(ForumReport.id == report_id).first()

        if not report:
            raise NotFoundError("Rapor bulunamadı")

        if report.status != "pending":
            raise BadRequestError("Bu rapor zaten işlenmiş")

        # Handle action
        if action == "delete":
            # Delete the reported content
            if report.content_type == "topic":
                content = db.query(ForumTopic).filter(ForumTopic.id == report.content_id).first()
            else:
                content = db.query(ForumReply).filter(ForumReply.id == report.content_id).first()

            if content:
                db.delete(content)

            report.status = "resolved"
            message = "Rapor çözüldü ve içerik silindi"
        else:
            report.status = "dismissed"
            message = "Rapor reddedildi"

        report.resolved_at = datetime.utcnow()
        report.resolved_by = current_user.id

        db.commit()

        return success_response(message=message)

    except (ForbiddenError, NotFoundError, BadRequestError):
        raise
    except Exception as e:
        logger.error(f"Error resolving report: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Topic Moderation Endpoints
# ============================================


@router.post("/topics/{topic_id}/moderate")
async def moderate_topic(
    topic_id: int,
    request: ModerationActionRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Moderate topic (admin only)"""
    try:
        if not current_user.is_admin:
            raise ForbiddenError("Bu işlem için yetkiniz yok")

        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()

        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Apply moderation action
        if request.action == "pin":
            topic.is_pinned = True
            message = "Konu sabitlendi"
        elif request.action == "unpin":
            topic.is_pinned = False
            message = "Konu sabitleme kaldırıldı"
        elif request.action == "lock":
            topic.is_locked = True
            message = "Konu kilitlendi"
        elif request.action == "unlock":
            topic.is_locked = False
            message = "Konu kilidi açıldı"

        topic.updated_at = datetime.utcnow()

        db.commit()

        return success_response(message=message)

    except (ForbiddenError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Error moderating topic: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/topics/{topic_id}/force")
async def force_delete_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Force delete topic (admin only)"""
    try:
        if not current_user.is_admin:
            raise ForbiddenError("Bu işlem için yetkiniz yok")

        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()

        if not topic:
            raise NotFoundError("Konu bulunamadı")

        # Delete all replies first
        db.query(ForumReply).filter(ForumReply.topic_id == topic_id).delete()

        # Delete topic
        db.delete(topic)
        db.commit()

        return success_response(message="Konu ve tüm yanıtlar silindi")

    except (ForbiddenError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Error force deleting topic: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Reply Moderation Endpoints
# ============================================


@router.delete("/replies/{reply_id}/force")
async def force_delete_reply(
    reply_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Force delete reply (admin only)"""
    try:
        if not current_user.is_admin:
            raise ForbiddenError("Bu işlem için yetkiniz yok")

        reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()

        if not reply:
            raise NotFoundError("Yanıt bulunamadı")

        # Update topic reply count
        topic = db.query(ForumTopic).filter(ForumTopic.id == reply.topic_id).first()

        if topic:
            topic.reply_count = max(0, (topic.reply_count or 0) - 1)

        db.delete(reply)
        db.commit()

        return success_response(message="Yanıt silindi")

    except (ForbiddenError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Error force deleting reply: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Bulk Moderation Endpoints
# ============================================


@router.post("/bulk/delete")
async def bulk_delete(
    content_type: str = Query(..., pattern="^(topics|replies)$"),
    ids: List[int] = Query(..., min_items=1, max_items=100),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Bulk delete topics or replies (admin only)"""
    try:
        if not current_user.is_admin:
            raise ForbiddenError("Bu işlem için yetkiniz yok")

        deleted_count = 0

        if content_type == "topics":
            # Delete topics and their replies
            for topic_id in ids:
                topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
                if topic:
                    db.query(ForumReply).filter(ForumReply.topic_id == topic_id).delete()
                    db.delete(topic)
                    deleted_count += 1
        else:
            # Delete replies
            for reply_id in ids:
                reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
                if reply:
                    # Update topic reply count
                    topic = db.query(ForumTopic).filter(ForumTopic.id == reply.topic_id).first()
                    if topic:
                        topic.reply_count = max(0, (topic.reply_count or 0) - 1)

                    db.delete(reply)
                    deleted_count += 1

        db.commit()

        return success_response(
            message=f"{deleted_count} içerik silindi", data={"deleted_count": deleted_count}
        )

    except ForbiddenError:
        raise
    except Exception as e:
        logger.error(f"Error bulk deleting: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
