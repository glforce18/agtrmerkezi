# ============================================
# AGTR v6.0 - Forum Konu/Yanıt CRUD API
# Dosya: app/api/admin/forum_topics.py
# ============================================

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import User
from app.models.forum import ForumCategory, ForumReply, ForumTopic

router = APIRouter(prefix="/admin/forum", tags=["admin-forum"])


# ============ Pydantic Schemas ============

class TopicCreate(BaseModel):
    title: str
    category_id: int
    content: str
    is_pinned: Optional[bool] = False
    is_locked: Optional[bool] = False
    is_active: Optional[bool] = True


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None
    is_active: Optional[bool] = None


# ============ Helper Functions ============

def generate_slug(title: str) -> str:
    """Türkçe karakterleri dönüştürüp slug oluştur"""
    tr_map = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    slug = title.lower()
    for tr_char, en_char in tr_map.items():
        slug = slug.replace(tr_char, en_char)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')[:250]


def ensure_unique_slug(db: Session, slug: str, exclude_id: Optional[int] = None) -> str:
    """Benzersiz slug oluştur"""
    base_slug = slug
    counter = 1
    while True:
        query = db.query(ForumTopic).filter(ForumTopic.slug == slug)
        if exclude_id:
            query = query.filter(ForumTopic.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


# ============ Topic Endpoints ============

@router.get("/topics")
async def get_topics(
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Tüm konuları getir (filtreli)"""
    query = db.query(ForumTopic).options(joinedload(ForumTopic.author))
    
    if category_id:
        query = query.filter(ForumTopic.category_id == category_id)
    
    if status:
        if status == 'active':
            query = query.filter(ForumTopic.is_active == True)
        elif status == 'inactive':
            query = query.filter(ForumTopic.is_active == False)
        elif status == 'pinned':
            query = query.filter(ForumTopic.is_pinned == True)
        elif status == 'locked':
            query = query.filter(ForumTopic.is_locked == True)
    
    # Pinned önce, sonra tarihe göre
    query = query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.created_at))
    
    total = query.count()
    topics = query.offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for topic in topics:
        reply_count = db.query(func.count(ForumReply.id)).filter(
            ForumReply.topic_id == topic.id
        ).scalar() or 0
        
        result.append({
            "id": topic.id,
            "title": topic.title,
            "slug": topic.slug,
            "category_id": topic.category_id,
            "content": topic.content,
            "author_id": topic.user_id,
            "author_name": topic.author.username if topic.author else None,
            "is_pinned": topic.is_pinned,
            "is_locked": topic.is_locked,
            "is_active": topic.is_active,
            "view_count": topic.view_count or 0,
            "reply_count": reply_count,
            "created_at": topic.created_at.isoformat() if topic.created_at else None,
            "updated_at": topic.updated_at.isoformat() if topic.updated_at else None
        })
    
    return {
        "topics": result,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }


@router.get("/topics/{topic_id}")
async def get_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Tek konu getir"""
    topic = db.query(ForumTopic).options(
        joinedload(ForumTopic.author)
    ).filter(ForumTopic.id == topic_id).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadı")
    
    return {
        "id": topic.id,
        "title": topic.title,
        "slug": topic.slug,
        "category_id": topic.category_id,
        "content": topic.content,
        "author_id": topic.user_id,
        "author_name": topic.author.username if topic.author else None,
        "is_pinned": topic.is_pinned,
        "is_locked": topic.is_locked,
        "is_active": topic.is_active,
        "view_count": topic.view_count,
        "created_at": topic.created_at.isoformat() if topic.created_at else None
    }


@router.post("/topics", status_code=status.HTTP_201_CREATED)
async def create_topic(
    data: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Yeni konu oluştur (admin olarak)"""
    # Kategori kontrolü
    category = db.query(ForumCategory).filter(ForumCategory.id == data.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Geçersiz kategori")
    
    slug = generate_slug(data.title)
    slug = ensure_unique_slug(db, slug)
    
    topic = ForumTopic(
        title=data.title,
        slug=slug,
        category_id=data.category_id,
        user_id=current_user.id,
        content=data.content,
        is_pinned=data.is_pinned or False,
        is_locked=data.is_locked or False,
        is_active=data.is_active if data.is_active is not None else True
    )
    
    db.add(topic)
    db.commit()
    db.refresh(topic)
    
    return {"message": "Konu oluşturuldu", "topic_id": topic.id, "slug": topic.slug}


@router.put("/topics/{topic_id}")
async def update_topic(
    topic_id: int,
    data: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Konu güncelle"""
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadı")
    
    if data.title is not None:
        topic.title = data.title
        topic.slug = ensure_unique_slug(db, generate_slug(data.title), exclude_id=topic_id)
    
    if data.category_id is not None:
        category = db.query(ForumCategory).filter(ForumCategory.id == data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Geçersiz kategori")
        topic.category_id = data.category_id
    
    if data.content is not None:
        topic.content = data.content
    
    if data.is_pinned is not None:
        topic.is_pinned = data.is_pinned
    
    if data.is_locked is not None:
        topic.is_locked = data.is_locked
    
    if data.is_active is not None:
        topic.is_active = data.is_active
    
    db.commit()
    
    return {"message": "Konu güncellendi"}


@router.delete("/topics/{topic_id}")
async def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Konu sil (yanıtlarla birlikte)"""
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadı")
    
    db.delete(topic)
    db.commit()
    
    return {"message": "Konu ve yanıtları silindi"}


# ============ Reply Endpoints ============

@router.get("/topics/{topic_id}/replies")
async def get_topic_replies(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Konunun yanıtlarını getir"""
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadı")
    
    replies = db.query(ForumReply).options(
        joinedload(ForumReply.author)
    ).filter(ForumReply.topic_id == topic_id).order_by(ForumReply.created_at).all()
    
    return {
        "replies": [
            {
                "id": r.id,
                "content": r.content,
                "author_id": r.user_id,
                "author_name": r.author.username if r.author else None,
                "is_active": r.is_active,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in replies
        ]
    }


@router.delete("/replies/{reply_id}")
async def delete_reply(
    reply_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Yanıt sil"""
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Yanıt bulunamadı")
    
    db.delete(reply)
    db.commit()
    
    return {"message": "Yanıt silindi"}


# ============ Stats Endpoint ============

@router.get("/stats")
async def get_forum_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Forum istatistikleri"""
    category_count = db.query(func.count(ForumCategory.id)).scalar() or 0
    topic_count = db.query(func.count(ForumTopic.id)).scalar() or 0
    reply_count = db.query(func.count(ForumReply.id)).scalar() or 0
    
    active_topics = db.query(func.count(ForumTopic.id)).filter(
        ForumTopic.is_active == True
    ).scalar() or 0
    
    return {
        "categories": category_count,
        "topics": topic_count,
        "replies": reply_count,
        "active_topics": active_topics
    }
