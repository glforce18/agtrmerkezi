# ============================================
# AGTR v6.0 - Forum API v2
# Dosya: app/api/forum_v2.py
# 20 Yeni Forum Ozelligi - API Endpoints
# ============================================

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import (
    InsufficientPermissionsException,
    PollAlreadyExistsException,
    PollExpiredException,
    PollNotFoundException,
    TopicNotFoundException,
)
from app.core.security import (
    get_current_user_optional,
    get_current_user_required,
)
from app.models.connection import get_db
from app.models.database import User
from app.services.forum_advanced import (
    get_bookmark_service,
    get_draft_service,
    get_poll_service,
    get_reaction_service,
    get_reputation_service,
    get_search_service,
    get_spam_filter_service,
    get_template_service,
)

router = APIRouter(prefix="/forum/v2", tags=["forum-v2"])
logger = logging.getLogger(__name__)


# ============ Pydantic Schemas ============


class ReactionRequest(BaseModel):
    content_type: str = Field(..., pattern="^(topic|reply)$")
    content_id: int = Field(..., gt=0)
    reaction_type: str = Field(..., pattern="^(like|love|laugh|thinking|solution|played)$")


class PollCreateRequest(BaseModel):
    topic_id: int = Field(..., gt=0)
    question: str = Field(..., min_length=5, max_length=500)
    options: List[str] = Field(..., min_items=2, max_items=10)
    allow_multiple: bool = False
    is_anonymous: bool = False
    ends_at: Optional[datetime] = None

    @validator("options")
    def validate_options(cls, v):
        return [opt.strip() for opt in v if opt.strip()]


class PollVoteRequest(BaseModel):
    option_ids: List[int] = Field(..., min_items=1)


class TemplateCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    title_template: str = Field(..., min_length=5, max_length=200)
    content_template: str = Field(..., min_length=10, max_length=10000)
    description: Optional[str] = None
    required_fields: Optional[List[str]] = None
    category_id: Optional[int] = None


class DraftSaveRequest(BaseModel):
    draft_type: str = Field(..., pattern="^(topic|reply)$")
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    topic_id: Optional[int] = None
    poll_data: Optional[Dict] = None
    device_id: Optional[str] = None


class SpamRuleCreateRequest(BaseModel):
    rule_type: str = Field(..., pattern="^(keyword|regex|link_pattern)$")
    pattern: str = Field(..., min_length=2, max_length=500)
    action: str = Field("review", pattern="^(block|review|warn)$")
    severity: int = Field(1, ge=1, le=10)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200)
    category_id: Optional[int] = None
    author_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    is_solved: Optional[bool] = None
    sort: str = Field("relevance", pattern="^(relevance|newest|oldest|most_replies|most_views)$")


class SimilarTopicsRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10, max_length=5000)


# ============ Helper Functions ============


def require_admin(user: User):
    """Admin yetkisi kontrolu"""
    if not user or user.role.value not in ["admin", "superadmin", "moderator"]:
        raise HTTPException(status_code=403, detail="Bu islem icin yetkiniz yok")


# ============ 1. Reactions Endpoints ============


@router.post("/reactions")
async def add_reaction(
    request: ReactionRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Tepki ekle/guncelle/kaldir"""
    service = get_reaction_service(db)
    result = service.add_reaction(
        user_id=current_user.id,
        content_type=request.content_type,
        content_id=request.content_id,
        reaction_type=request.reaction_type,
    )
    return {"success": True, **result}


@router.get("/reactions/{content_type}/{content_id}")
async def get_reactions(
    content_type: str,
    content_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Bir icerigin tepkilerini getir"""
    service = get_reaction_service(db)
    reactions = service.get_reactions(content_type, content_id)

    # Kullanicinin tepkisi
    user_reaction = None
    if current_user:
        user_reaction = service.get_user_reaction(current_user.id, content_type, content_id)

    return {"success": True, **reactions, "user_reaction": user_reaction}


@router.get("/reactions/{content_type}/{content_id}/users/{reaction_type}")
async def get_reaction_users(
    content_type: str,
    content_id: int,
    reaction_type: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Belirli tepkiyi veren kullanicilari getir"""
    service = get_reaction_service(db)
    users = service.get_reaction_users(content_type, content_id, reaction_type, limit)
    return {"success": True, "users": users}


# ============ 2. Polls Endpoints ============


@router.post("/polls")
async def create_poll(
    request: PollCreateRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Yeni anket olustur"""
    from app.models.forum import ForumTopic

    # Konu sahibi mi kontrol et
    topic = db.query(ForumTopic).filter(ForumTopic.id == request.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")

    if topic.author_id != current_user.id and current_user.role.value not in [
        "admin",
        "superadmin",
    ]:
        raise HTTPException(status_code=403, detail="Sadece kendi konunuza anket ekleyebilirsiniz")

    service = get_poll_service(db)
    try:
        poll = service.create_poll(
            topic_id=request.topic_id,
            question=request.question,
            options=request.options,
            allow_multiple=request.allow_multiple,
            is_anonymous=request.is_anonymous,
            ends_at=request.ends_at,
        )
        return {"success": True, "poll": poll}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/polls/{poll_id}/vote")
async def vote_poll(
    poll_id: int,
    request: PollVoteRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Ankete oy ver"""
    service = get_poll_service(db)
    try:
        poll = service.vote(poll_id, current_user.id, request.option_ids)
        return {"success": True, "poll": poll}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/polls/{poll_id}")
async def get_poll(
    poll_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Anket detaylarini getir"""
    service = get_poll_service(db)
    user_id = current_user.id if current_user else None
    poll = service.get_poll(poll_id, user_id)

    if not poll:
        raise HTTPException(status_code=404, detail="Anket bulunamadi")

    return {"success": True, "poll": poll}


@router.get("/topics/{topic_id}/poll")
async def get_topic_poll(
    topic_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Konunun anketini getir"""
    service = get_poll_service(db)
    user_id = current_user.id if current_user else None
    poll = service.get_poll_by_topic(topic_id, user_id)

    return {"success": True, "poll": poll}


# ============ 3. Templates Endpoints ============


@router.get("/templates")
async def get_templates(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Konu sablonlarini listele"""
    service = get_template_service(db)
    templates = service.get_templates(category_id)
    return {"success": True, "templates": templates}


@router.post("/templates")
async def create_template(
    request: TemplateCreateRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Yeni sablon olustur (admin only)"""
    require_admin(current_user)

    service = get_template_service(db)
    template = service.create_template(
        name=request.name,
        title_template=request.title_template,
        content_template=request.content_template,
        description=request.description,
        required_fields=request.required_fields,
        category_id=request.category_id,
        created_by=current_user.id,
    )
    return {"success": True, "template": template}


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Sablon sil (admin only)"""
    require_admin(current_user)

    service = get_template_service(db)
    if service.delete_template(template_id):
        return {"success": True, "message": "Sablon silindi"}
    raise HTTPException(status_code=404, detail="Sablon bulunamadi")


# ============ 4. Drafts Endpoints ============


@router.post("/drafts")
async def save_draft(
    request: DraftSaveRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Taslak kaydet"""
    service = get_draft_service(db)
    result = await service.save_draft(
        user_id=current_user.id,
        draft_type=request.draft_type,
        title=request.title,
        content=request.content,
        category_id=request.category_id,
        topic_id=request.topic_id,
        poll_data=request.poll_data,
        device_id=request.device_id,
    )
    return {"success": True, **result}


@router.get("/drafts/{draft_type}")
async def get_draft(
    draft_type: str,
    topic_id: Optional[int] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Taslak getir"""
    service = get_draft_service(db)
    draft = await service.get_draft(current_user.id, draft_type, topic_id)
    return {"success": True, "draft": draft}


@router.delete("/drafts/{draft_type}")
async def delete_draft(
    draft_type: str,
    topic_id: Optional[int] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Taslak sil"""
    service = get_draft_service(db)
    await service.delete_draft(current_user.id, draft_type, topic_id)
    return {"success": True, "message": "Taslak silindi"}


@router.get("/drafts")
async def get_all_drafts(
    current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)
):
    """Tum taslaklari getir"""
    service = get_draft_service(db)
    drafts = service.get_all_drafts(current_user.id)
    return {"success": True, "drafts": drafts}


# ============ 5. Spam Filter Endpoints (Admin) ============


@router.get("/spam/rules")
async def get_spam_rules(
    current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)
):
    """Spam kurallarini listele (admin only)"""
    require_admin(current_user)

    service = get_spam_filter_service(db)
    rules = service.get_rules()
    return {"success": True, "rules": rules}


@router.post("/spam/rules")
async def create_spam_rule(
    request: SpamRuleCreateRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Yeni spam kurali ekle (admin only)"""
    require_admin(current_user)

    service = get_spam_filter_service(db)
    rule = service.add_rule(
        rule_type=request.rule_type,
        pattern=request.pattern,
        action=request.action,
        severity=request.severity,
        created_by=current_user.id,
    )
    return {"success": True, "rule": rule}


@router.delete("/spam/rules/{rule_id}")
async def delete_spam_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Spam kurali sil (admin only)"""
    require_admin(current_user)

    service = get_spam_filter_service(db)
    if service.delete_rule(rule_id):
        return {"success": True, "message": "Kural silindi"}
    raise HTTPException(status_code=404, detail="Kural bulunamadi")


@router.post("/spam/check")
async def check_spam(
    content: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Icerigi spam kontrolunden gecir"""
    service = get_spam_filter_service(db)
    result = service.check_content(content, current_user.id)
    return {"success": True, **result}


# ============ 6. Advanced Search Endpoints ============


@router.post("/search")
async def advanced_search(
    request: SearchRequest,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=5, le=100),
    db: Session = Depends(get_db),
):
    """Gelismis arama"""
    service = get_search_service(db)

    filters = {
        "category_id": request.category_id,
        "author_id": request.author_id,
        "date_from": request.date_from,
        "date_to": request.date_to,
        "tags": request.tags,
        "is_solved": request.is_solved,
        "sort": request.sort,
    }

    result = await service.search(query=request.query, filters=filters, page=page, limit=limit)
    return {"success": True, **result}


@router.get("/search")
async def quick_search(
    q: str = Query(..., min_length=2, max_length=200),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=5, le=100),
    db: Session = Depends(get_db),
):
    """Hizli arama"""
    service = get_search_service(db)
    result = await service.search(query=q, page=page, limit=limit)
    return {"success": True, **result}


@router.post("/search/similar")
async def find_similar_topics(request: SimilarTopicsRequest, db: Session = Depends(get_db)):
    """Benzer konulari bul"""
    service = get_search_service(db)
    topics = service.get_similar_topics(request.title, request.content)
    return {"success": True, "similar_topics": topics}


# ============ 7. Reputation Endpoints ============


@router.get("/reputation/{user_id}")
async def get_user_reputation(user_id: int, db: Session = Depends(get_db)):
    """Kullanici itibar detaylarini getir"""
    service = get_reputation_service(db)
    reputation = service.get_reputation_details(user_id)
    return {"success": True, "reputation": reputation}


@router.get("/reputation/me")
async def get_my_reputation(
    current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)
):
    """Kendi itibar detaylarini getir"""
    service = get_reputation_service(db)
    reputation = service.get_reputation_details(current_user.id)
    return {"success": True, "reputation": reputation}


@router.get("/leaderboard")
async def get_leaderboard(
    timeframe: str = Query("all", pattern="^(all|weekly|monthly)$"),
    limit: int = Query(10, ge=5, le=50),
    db: Session = Depends(get_db),
):
    """Liderlik tablosunu getir"""
    service = get_reputation_service(db)
    leaderboard = service.get_leaderboard(timeframe, limit)
    return {"success": True, "leaderboard": leaderboard}


# ============ 8. Bookmarks Endpoints ============


@router.post("/bookmarks/{topic_id}")
async def toggle_bookmark(
    topic_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Yer imi ekle/kaldir"""
    service = get_bookmark_service(db)
    result = service.toggle_bookmark(current_user.id, topic_id)
    return {"success": True, **result}


@router.get("/bookmarks")
async def get_my_bookmarks(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=5, le=100),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Yer imlerimi getir"""
    service = get_bookmark_service(db)
    result = service.get_bookmarks(current_user.id, page, limit)
    return {"success": True, **result}


@router.get("/bookmarks/{topic_id}/check")
async def check_bookmark(
    topic_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Konu yer iminde mi kontrol et"""
    service = get_bookmark_service(db)
    is_bookmarked = service.is_bookmarked(current_user.id, topic_id)
    return {"success": True, "bookmarked": is_bookmarked}


# ============ 9. Quote Threading Endpoint ============


@router.get("/replies/{reply_id}/thread")
async def get_reply_thread(reply_id: int, db: Session = Depends(get_db)):
    """Yanit zincirini getir (parent'lardan child'lara)"""
    from app.models.database import User
    from app.models.forum import ForumReply

    # Yaniti bul
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Yanit bulunamadi")

    # Parent zinciri - tum parent ID'leri topla
    parent_ids = []
    current = reply
    while current.parent_reply_id:
        parent_ids.append(current.parent_reply_id)
        # Gecici olarak parent'i memory'den oku (dongu sonrasi tek query ile cekilecek)
        parent = db.query(ForumReply).filter(ForumReply.id == current.parent_reply_id).first()
        if not parent:
            break
        current = parent

    # Tum parent'lari ve author'larini tek query ile getir
    parents_data = {}
    if parent_ids:
        parents_with_users = (
            db.query(ForumReply)
            .options(joinedload(ForumReply.user))
            .filter(ForumReply.id.in_(parent_ids))
            .all()
        )
        parents_data = {p.id: p for p in parents_with_users}

    # Parent listesini duzgun sirada olustur
    parents = []
    current = reply
    while current.parent_reply_id and current.parent_reply_id in parents_data:
        parent = parents_data[current.parent_reply_id]
        author = parent.user
        parents.insert(
            0,
            {
                "id": parent.id,
                "content": (
                    parent.content[:200] + "..." if len(parent.content) > 200 else parent.content
                ),
                "author": {
                    "id": author.id if author else None,
                    "username": author.username if author else "Anonim",
                },
                "created_at": parent.created_at.isoformat(),
            },
        )
        current = parent

    # Child yanitlar - eager load user relationship
    children = (
        db.query(ForumReply)
        .options(joinedload(ForumReply.user))
        .filter(ForumReply.parent_reply_id == reply_id, ForumReply.is_active == True)
        .order_by(ForumReply.created_at)
        .limit(10)
        .all()
    )

    child_list = []
    for child in children:
        author = child.user
        child_list.append(
            {
                "id": child.id,
                "content": (
                    child.content[:200] + "..." if len(child.content) > 200 else child.content
                ),
                "author": {
                    "id": author.id if author else None,
                    "username": author.username if author else "Anonim",
                },
                "created_at": child.created_at.isoformat(),
            }
        )

    return {
        "success": True,
        "thread": {
            "parents": parents,
            "current": {"id": reply.id, "content": reply.content},
            "children": child_list,
        },
    }


# ============ 10. Infinite Scroll Support ============


@router.get("/topics/cursor")
async def get_topics_cursor(
    cursor: Optional[str] = None,
    limit: int = Query(20, ge=5, le=50),
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Cursor-based pagination for infinite scroll"""
    import base64

    from app.models.database import User
    from app.models.forum import ForumTopic

    query = db.query(ForumTopic).filter(ForumTopic.is_active == True)

    if category_id:
        query = query.filter(ForumTopic.category_id == category_id)

    # Cursor decode
    if cursor:
        try:
            decoded = base64.b64decode(cursor).decode("utf-8")
            cursor_data = json.loads(decoded)
            cursor_date = datetime.fromisoformat(cursor_data["date"])
            cursor_id = cursor_data["id"]

            # Cursor'dan sonraki konulari getir
            query = query.filter(
                (ForumTopic.created_at < cursor_date)
                | ((ForumTopic.created_at == cursor_date) & (ForumTopic.id < cursor_id))
            )
        except Exception:
            pass

    # Siralama ve limit - eager load author
    topics = (
        query.options(joinedload(ForumTopic.author))
        .order_by(ForumTopic.created_at.desc(), ForumTopic.id.desc())
        .limit(limit + 1)
        .all()
    )

    # Sonraki sayfa var mi?
    has_more = len(topics) > limit
    if has_more:
        topics = topics[:limit]

    # Next cursor
    next_cursor = None
    if has_more and topics:
        last_topic = topics[-1]
        cursor_data = {"date": last_topic.created_at.isoformat(), "id": last_topic.id}
        next_cursor = base64.b64encode(json.dumps(cursor_data).encode("utf-8")).decode("utf-8")

    # Format topics - author already loaded
    result_topics = []
    for topic in topics:
        author = topic.author
        result_topics.append(
            {
                "id": topic.id,
                "title": topic.title,
                "content_preview": (
                    topic.content[:150] + "..." if len(topic.content) > 150 else topic.content
                ),
                "author": {
                    "id": author.id if author else None,
                    "username": author.username if author else "Anonim",
                    "avatar": author.avatar if author else None,
                },
                "category_id": topic.category_id,
                "reply_count": topic.reply_count,
                "view_count": topic.view_count,
                "is_pinned": topic.is_pinned,
                "is_locked": topic.is_locked,
                "is_solved": topic.is_solved,
                "created_at": topic.created_at.isoformat(),
            }
        )

    return {
        "success": True,
        "topics": result_topics,
        "next_cursor": next_cursor,
        "has_more": has_more,
    }


@router.get("/replies/cursor/{topic_id}")
async def get_replies_cursor(
    topic_id: int,
    cursor: Optional[str] = None,
    limit: int = Query(20, ge=5, le=50),
    db: Session = Depends(get_db),
):
    """Cursor-based pagination for replies (infinite scroll)"""
    import base64

    from app.models.database import User
    from app.models.forum import ForumReply

    query = db.query(ForumReply).filter(
        ForumReply.topic_id == topic_id, ForumReply.is_active == True
    )

    # Cursor decode
    if cursor:
        try:
            decoded = base64.b64decode(cursor).decode("utf-8")
            cursor_data = json.loads(decoded)
            cursor_date = datetime.fromisoformat(cursor_data["date"])
            cursor_id = cursor_data["id"]

            query = query.filter(
                (ForumReply.created_at > cursor_date)
                | ((ForumReply.created_at == cursor_date) & (ForumReply.id > cursor_id))
            )
        except Exception:
            pass

    # Siralama ve limit - eager load user
    replies = (
        query.options(joinedload(ForumReply.user))
        .order_by(ForumReply.created_at.asc(), ForumReply.id.asc())
        .limit(limit + 1)
        .all()
    )

    has_more = len(replies) > limit
    if has_more:
        replies = replies[:limit]

    # Next cursor
    next_cursor = None
    if has_more and replies:
        last_reply = replies[-1]
        cursor_data = {"date": last_reply.created_at.isoformat(), "id": last_reply.id}
        next_cursor = base64.b64encode(json.dumps(cursor_data).encode("utf-8")).decode("utf-8")

    # Format replies - user already loaded
    result_replies = []
    for reply in replies:
        author = reply.user
        result_replies.append(
            {
                "id": reply.id,
                "content": reply.content,
                "author": {
                    "id": author.id if author else None,
                    "username": author.username if author else "Anonim",
                    "avatar": author.avatar if author else None,
                },
                "parent_reply_id": reply.parent_reply_id,
                "is_solution": reply.is_solution,
                "created_at": reply.created_at.isoformat(),
                "updated_at": reply.updated_at.isoformat() if reply.updated_at else None,
            }
        )

    return {
        "success": True,
        "replies": result_replies,
        "next_cursor": next_cursor,
        "has_more": has_more,
    }
