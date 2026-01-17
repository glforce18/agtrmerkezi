# ============================================
# AGTR v6.0 - User Forum API
# Dosya: app/api/forum.py
# ============================================

import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User
from app.models.forum import ForumCategory, ForumReply, ForumTopic

router = APIRouter(prefix="/forum", tags=["forum"])


# ============ Pydantic Schemas ============

class TopicCreate(BaseModel):
    title: str
    category_id: int
    content: str


class ReplyCreate(BaseModel):
    content: str


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


def ensure_unique_slug(db: Session, slug: str) -> str:
    """Benzersiz slug oluştur"""
    base_slug = slug
    counter = 1
    while db.query(ForumTopic).filter(ForumTopic.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


# ============ Category Endpoints ============

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Aktif kategorileri getir"""
    categories = db.query(ForumCategory).filter(
        ForumCategory.is_active == True
    ).order_by(ForumCategory.order_index).all()
    
    result = []
    for cat in categories:
        topic_count = db.query(func.count(ForumTopic.id)).filter(
            ForumTopic.category_id == cat.id,
            ForumTopic.is_active == True
        ).scalar() or 0
        
        result.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "description": cat.description,
            "icon": cat.icon or "fas fa-folder",
            "topic_count": topic_count
        })
    
    return {"categories": result}


@router.get("/categories/{slug}")
async def get_category(slug: str, db: Session = Depends(get_db)):
    """Kategori detayı"""
    category = db.query(ForumCategory).filter(
        ForumCategory.slug == slug,
        ForumCategory.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")
    
    topic_count = db.query(func.count(ForumTopic.id)).filter(
        ForumTopic.category_id == category.id,
        ForumTopic.is_active == True
    ).scalar() or 0
    
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "icon": category.icon,
        "topic_count": topic_count
    }


@router.get("/categories/{slug}/topics")
async def get_category_topics(
    slug: str,
    page: int = 1,
    limit: int = 20,
    sort: str = "newest",
    db: Session = Depends(get_db)
):
    """Kategorinin konularını getir"""
    category = db.query(ForumCategory).filter(
        ForumCategory.slug == slug,
        ForumCategory.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")
    
    query = db.query(ForumTopic).options(
        joinedload(ForumTopic.author)
    ).filter(
        ForumTopic.category_id == category.id,
        ForumTopic.is_active == True
    )
    
    # Sorting
    if sort == "oldest":
        query = query.order_by(desc(ForumTopic.is_pinned), ForumTopic.created_at)
    elif sort == "popular":
        query = query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.view_count))
    elif sort == "most_replies":
        # Subquery for reply count
        reply_count_subq = db.query(
            ForumReply.topic_id,
            func.count(ForumReply.id).label('reply_count')
        ).group_by(ForumReply.topic_id).subquery()
        
        query = query.outerjoin(
            reply_count_subq, ForumTopic.id == reply_count_subq.c.topic_id
        ).order_by(desc(ForumTopic.is_pinned), desc(func.coalesce(reply_count_subq.c.reply_count, 0)))
    else:  # newest (default)
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
            "author_name": topic.author.username if topic.author else None,
            "author_avatar": None,  # Add if you have avatar field
            "is_pinned": topic.is_pinned,
            "is_locked": topic.is_locked,
            "view_count": topic.view_count or 0,
            "reply_count": reply_count,
            "created_at": topic.created_at.isoformat() if topic.created_at else None
        })
    
    return {
        "topics": result,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }


# ============ Topic Endpoints ============

@router.get("/topics")
async def get_topics(
    limit: int = 10,
    page: int = 1,
    db: Session = Depends(get_db)
):
    """Son konuları getir"""
    query = db.query(ForumTopic).options(
        joinedload(ForumTopic.author)
    ).filter(ForumTopic.is_active == True).order_by(
        desc(ForumTopic.is_pinned),
        desc(ForumTopic.created_at)
    )
    
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
            "author_name": topic.author.username if topic.author else None,
            "is_pinned": topic.is_pinned,
            "is_locked": topic.is_locked,
            "reply_count": reply_count,
            "view_count": topic.view_count or 0,
            "created_at": topic.created_at.isoformat() if topic.created_at else None
        })
    
    return {"topics": result, "total": total}


@router.get("/topics/{slug}")
async def get_topic(slug: str, db: Session = Depends(get_db)):
    """Konu detayı"""
    topic = db.query(ForumTopic).options(
        joinedload(ForumTopic.author),
        joinedload(ForumTopic.category)
    ).filter(
        ForumTopic.slug == slug,
        ForumTopic.is_active == True
    ).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadı")
    
    # Görüntülenme sayısını artır
    topic.view_count = (topic.view_count or 0) + 1
    db.commit()
    
    reply_count = db.query(func.count(ForumReply.id)).filter(
        ForumReply.topic_id == topic.id
    ).scalar() or 0
    
    return {
        "id": topic.id,
        "title": topic.title,
        "slug": topic.slug,
        "content": topic.content,
        "category": {
            "id": topic.category.id,
            "name": topic.category.name,
            "slug": topic.category.slug
        } if topic.category else None,
        "author_id": topic.user_id,
        "author_name": topic.author.username if topic.author else None,
        "author_avatar": None,
        "is_pinned": topic.is_pinned,
        "is_locked": topic.is_locked,
        "view_count": topic.view_count,
        "reply_count": reply_count,
        "created_at": topic.created_at.isoformat() if topic.created_at else None
    }


@router.post("/topics", status_code=status.HTTP_201_CREATED)
async def create_topic(
    data: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Yeni konu oluştur"""
    # Kategori kontrolü
    category = db.query(ForumCategory).filter(
        ForumCategory.id == data.category_id,
        ForumCategory.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(status_code=400, detail="Geçersiz kategori")
    
    # Validation
    if len(data.title.strip()) < 5:
        raise HTTPException(status_code=400, detail="Başlık en az 5 karakter olmalı")
    
    if len(data.content.strip()) < 20:
        raise HTTPException(status_code=400, detail="İçerik en az 20 karakter olmalı")
    
    slug = generate_slug(data.title)
    slug = ensure_unique_slug(db, slug)
    
    topic = ForumTopic(
        title=data.title.strip(),
        slug=slug,
        category_id=data.category_id,
        user_id=current_user.id,
        content=data.content.strip(),
        is_active=True
    )
    
    db.add(topic)
    db.commit()
    db.refresh(topic)
    
    return {"message": "Konu oluşturuldu", "topic_id": topic.id, "slug": topic.slug}


# ============ Reply Endpoints ============

@router.get("/topics/{slug}/replies")
async def get_topic_replies(slug: str, db: Session = Depends(get_db)):
    """Konunun yanıtlarını getir"""
    topic = db.query(ForumTopic).filter(
        ForumTopic.slug == slug,
        ForumTopic.is_active == True
    ).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadı")
    
    replies = db.query(ForumReply).options(
        joinedload(ForumReply.author)
    ).filter(
        ForumReply.topic_id == topic.id,
        ForumReply.is_active == True
    ).order_by(ForumReply.created_at).all()
    
    return {
        "replies": [
            {
                "id": r.id,
                "content": r.content,
                "author_id": r.user_id,
                "author_name": r.author.username if r.author else None,
                "author_avatar": None,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in replies
        ]
    }


@router.post("/topics/{slug}/replies", status_code=status.HTTP_201_CREATED)
async def create_reply(
    slug: str,
    data: ReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Yanıt ekle"""
    topic = db.query(ForumTopic).filter(
        ForumTopic.slug == slug,
        ForumTopic.is_active == True
    ).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadı")
    
    if topic.is_locked:
        raise HTTPException(status_code=403, detail="Bu konu kilitli, yanıt yazılamaz")
    
    if len(data.content.strip()) < 3:
        raise HTTPException(status_code=400, detail="Yanıt en az 3 karakter olmalı")
    
    reply = ForumReply(
        topic_id=topic.id,
        user_id=current_user.id,
        content=data.content.strip(),
        is_active=True
    )
    
    db.add(reply)
    db.commit()
    db.refresh(reply)
    
    return {"message": "Yanıt eklendi", "reply_id": reply.id}


# ============ Stats Endpoint ============

@router.get("/stats")
async def get_forum_stats(db: Session = Depends(get_db)):
    """Forum istatistikleri (public)"""
    category_count = db.query(func.count(ForumCategory.id)).filter(
        ForumCategory.is_active == True
    ).scalar() or 0
    
    topic_count = db.query(func.count(ForumTopic.id)).filter(
        ForumTopic.is_active == True
    ).scalar() or 0
    
    reply_count = db.query(func.count(ForumReply.id)).filter(
        ForumReply.is_active == True
    ).scalar() or 0
    
    return {
        "categories": category_count,
        "topics": topic_count,
        "replies": reply_count
    }
