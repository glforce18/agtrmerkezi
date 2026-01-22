# ============================================
# AGTR v6.0 - User Forum API
# Dosya: app/api/forum.py
# ============================================

import hashlib
import json
import logging
import random
import re
import secrets
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, case, desc, func, or_, text
from sqlalchemy.orm import Session, joinedload

from app.core.redis_manager import redis_manager
from app.core.sanitizer import sanitize_forum_content, sanitize_title
from app.core.security import get_current_user, get_current_user_required
from app.models.connection import get_db
from app.models.database import (
    User,
    UserRole,
    Notification,
    ForumTag,
    ForumTopicTag,
    ForumMention,
    ForumSubscription,
)
from app.models.forum import ForumCategory, ForumReply, ForumReport, ForumTopic

router = APIRouter(tags=["forum"])
logger = logging.getLogger(__name__)

# ============ Rate Limit Constants ============
TOPIC_RATE_LIMIT = 5  # topics per hour
REPLY_RATE_LIMIT = 20  # replies per hour
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds


# ============ Pydantic Schemas ============

class TopicCreate(BaseModel):
    title: str
    category_id: int
    content: str
    tags: Optional[List[str]] = None  # Optional list of tag names


class ReplyCreate(BaseModel):
    content: str


class TopicUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class ReplyUpdate(BaseModel):
    content: str


class ReportCreate(BaseModel):
    content_type: str  # "topic" or "reply"
    content_id: int
    reason: str  # spam, harassment, inappropriate, other
    details: Optional[str] = None


# ============ Helper Functions ============

async def invalidate_forum_cache():
    """Forum cache'lerini temizle"""
    from app.core.redis_manager import redis_manager
    try:
        # Kategori cache'ini temizle
        await redis_manager.delete("forum:categories")
        # Populer konular cache'ini temizle
        await redis_manager.delete("forum:popular_topics")
    except Exception:
        pass  # Cache hatasi kritik degil


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


async def check_forum_rate_limit(user_id: int, action_type: str) -> bool:
    """
    Check if user has exceeded rate limit for forum actions.
    Returns True if rate limited (exceeded), False if allowed.
    """
    if action_type == "topic":
        key = f"forum:ratelimit:{user_id}:topics"
        limit = TOPIC_RATE_LIMIT
    elif action_type == "reply":
        key = f"forum:ratelimit:{user_id}:replies"
        limit = REPLY_RATE_LIMIT
    else:
        return False

    try:
        # Check if allowed using redis_manager's rate_limit_check
        # Returns True if allowed, False if rate limited
        allowed = await redis_manager.rate_limit_check(key, limit, RATE_LIMIT_WINDOW)
        return not allowed  # Return True if rate limited (not allowed)
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return False  # Fail open - allow the action


def is_admin_or_author(user: User, author_id: int) -> bool:
    """Check if user is admin or the author of the content"""
    return user.id == author_id or user.role == UserRole.ADMIN


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string in YYYY-MM-DD format"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


# ============ Search & Trending Endpoints ============

@router.get("/search")
async def search_forum(
    q: str = Query(..., min_length=2, description="Search query"),
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    date_from: Optional[str] = None,  # YYYY-MM-DD
    date_to: Optional[str] = None,
    sort: str = Query("relevance", pattern="^(relevance|newest|oldest|popular)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=5, le=50),
    db: Session = Depends(get_db)
):
    """
    Forum arama - Konu basligi ve icerigi arar
    - q: Arama sorgusu (minimum 2 karakter)
    - category_id: Kategori filtresi
    - author_id: Yazar filtresi
    - date_from: Baslangic tarihi (YYYY-MM-DD)
    - date_to: Bitis tarihi (YYYY-MM-DD)
    - sort: Siralama (relevance, newest, oldest, popular)
    - page: Sayfa numarasi
    - limit: Sayfa basi sonuc sayisi (5-50)
    """
    # Parse dates
    from_date = parse_date(date_from)
    to_date = parse_date(date_to)
    if to_date:
        # Include the entire end date
        to_date = to_date + timedelta(days=1)

    # Prepare search pattern
    search_pattern = f"%{q}%"

    # Build base query with eager loading to avoid N+1
    query = db.query(ForumTopic).options(
        joinedload(ForumTopic.author),
        joinedload(ForumTopic.category)
    ).filter(
        ForumTopic.is_active == True,
        or_(
            ForumTopic.title.ilike(search_pattern),
            ForumTopic.content.ilike(search_pattern)
        )
    )

    # Apply filters
    if category_id:
        query = query.filter(ForumTopic.category_id == category_id)

    if author_id:
        query = query.filter(ForumTopic.author_id == author_id)

    if from_date:
        query = query.filter(ForumTopic.created_at >= from_date)

    if to_date:
        query = query.filter(ForumTopic.created_at < to_date)

    # Reply counts subquery for all results
    reply_count_subq = db.query(
        ForumReply.topic_id,
        func.count(ForumReply.id).label('reply_count')
    ).filter(ForumReply.is_active == True).group_by(ForumReply.topic_id).subquery()

    # Add reply count to query
    query = query.outerjoin(
        reply_count_subq, ForumTopic.id == reply_count_subq.c.topic_id
    ).add_columns(
        func.coalesce(reply_count_subq.c.reply_count, 0).label('reply_count')
    )

    # Sorting
    if sort == "relevance":
        # Title match is more relevant than content match
        relevance_score = case(
            (ForumTopic.title.ilike(search_pattern), 2),
            else_=1
        )
        query = query.order_by(desc(relevance_score), desc(ForumTopic.created_at))
    elif sort == "newest":
        query = query.order_by(desc(ForumTopic.created_at))
    elif sort == "oldest":
        query = query.order_by(ForumTopic.created_at)
    elif sort == "popular":
        query = query.order_by(
            desc(ForumTopic.view_count),
            desc(func.coalesce(reply_count_subq.c.reply_count, 0))
        )

    # Get total count (without pagination)
    count_query = db.query(func.count(ForumTopic.id)).filter(
        ForumTopic.is_active == True,
        or_(
            ForumTopic.title.ilike(search_pattern),
            ForumTopic.content.ilike(search_pattern)
        )
    )
    if category_id:
        count_query = count_query.filter(ForumTopic.category_id == category_id)
    if author_id:
        count_query = count_query.filter(ForumTopic.author_id == author_id)
    if from_date:
        count_query = count_query.filter(ForumTopic.created_at >= from_date)
    if to_date:
        count_query = count_query.filter(ForumTopic.created_at < to_date)

    total = count_query.scalar() or 0

    # Apply pagination
    offset = (page - 1) * limit
    results = query.offset(offset).limit(limit).all()

    # Build response
    topics = []
    for row in results:
        topic = row[0] if isinstance(row, tuple) else row
        reply_count = row[1] if isinstance(row, tuple) and len(row) > 1 else 0

        topics.append({
            "id": topic.id,
            "title": topic.title,
            "slug": topic.slug,
            "content_preview": (topic.content[:200] + "...") if topic.content and len(topic.content) > 200 else topic.content,
            "category": {
                "id": topic.category.id,
                "name": topic.category.name,
                "slug": topic.category.slug
            } if topic.category else None,
            "author": {
                "id": topic.author.id,
                "username": topic.author.username,
                "avatar": topic.author.avatar
            } if topic.author else None,
            "view_count": topic.view_count or 0,
            "reply_count": reply_count,
            "is_pinned": topic.is_pinned,
            "is_locked": topic.is_locked,
            "created_at": topic.created_at.isoformat() if topic.created_at else None
        })

    return {
        "query": q,
        "topics": topics,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total > 0 else 0
    }


@router.get("/trending")
async def get_trending_topics(db: Session = Depends(get_db)):
    """
    Trend konulari getir - Son 24 saatte en cok goruntulenme/yanit alan konular
    5 dakika Redis cache ile
    """
    cache_key = "forum:trending"
    CACHE_TTL = 300  # 5 dakika

    # Cache kontrol
    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass  # Cache hatasi durumunda DB'den devam

    # Son 24 saat
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    # Reply counts subquery for last 24 hours
    recent_reply_count = db.query(
        ForumReply.topic_id,
        func.count(ForumReply.id).label('recent_replies')
    ).filter(
        ForumReply.is_active == True,
        ForumReply.created_at >= twenty_four_hours_ago
    ).group_by(ForumReply.topic_id).subquery()

    # Total reply counts
    total_reply_count = db.query(
        ForumReply.topic_id,
        func.count(ForumReply.id).label('total_replies')
    ).filter(ForumReply.is_active == True).group_by(ForumReply.topic_id).subquery()

    # Query for trending topics
    query = db.query(
        ForumTopic,
        func.coalesce(recent_reply_count.c.recent_replies, 0).label('recent_replies'),
        func.coalesce(total_reply_count.c.total_replies, 0).label('total_replies')
    ).options(
        joinedload(ForumTopic.author),
        joinedload(ForumTopic.category)
    ).outerjoin(
        recent_reply_count, ForumTopic.id == recent_reply_count.c.topic_id
    ).outerjoin(
        total_reply_count, ForumTopic.id == total_reply_count.c.topic_id
    ).filter(
        ForumTopic.is_active == True,
        or_(
            ForumTopic.created_at >= twenty_four_hours_ago,
            recent_reply_count.c.recent_replies > 0
        )
    ).order_by(
        desc(func.coalesce(recent_reply_count.c.recent_replies, 0)),
        desc(ForumTopic.view_count)
    ).limit(10)

    results = query.all()

    topics = []
    for topic, recent_replies, total_replies in results:
        topics.append({
            "id": topic.id,
            "title": topic.title,
            "slug": topic.slug,
            "category": {
                "id": topic.category.id,
                "name": topic.category.name,
                "slug": topic.category.slug
            } if topic.category else None,
            "author": {
                "id": topic.author.id,
                "username": topic.author.username,
                "avatar": topic.author.avatar
            } if topic.author else None,
            "view_count": topic.view_count or 0,
            "reply_count": total_replies,
            "recent_replies": recent_replies,
            "is_pinned": topic.is_pinned,
            "created_at": topic.created_at.isoformat() if topic.created_at else None
        })

    response = {"topics": topics}

    # Cache'e kaydet
    try:
        await redis_manager.set(cache_key, json.dumps(response), expire=CACHE_TTL)
    except Exception:
        pass  # Cache yazma hatasi kritik degil

    return response


# ============ Category Endpoints ============

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Aktif kategorileri getir - Redis cache ile"""
    import json
    from app.core.redis_manager import redis_manager

    cache_key = "forum:categories"
    CACHE_TTL = 300  # 5 dakika

    # Cache kontrol
    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass  # Cache hatasi durumunda DB'den devam

    # Tek sorguda topic ve reply count'lari al (N+1 sorunu cozumu)
    from sqlalchemy import func as sqlfunc

    # Topic count subquery
    topic_counts = db.query(
        ForumTopic.category_id,
        sqlfunc.count(ForumTopic.id).label('topic_count')
    ).group_by(ForumTopic.category_id).subquery()

    # Reply count subquery (posts = replies)
    reply_counts = db.query(
        ForumTopic.category_id,
        sqlfunc.count(ForumReply.id).label('reply_count')
    ).join(
        ForumReply, ForumReply.topic_id == ForumTopic.id
    ).group_by(ForumTopic.category_id).subquery()

    # Main query
    categories = db.query(
        ForumCategory,
        sqlfunc.coalesce(topic_counts.c.topic_count, 0).label('topic_count'),
        sqlfunc.coalesce(reply_counts.c.reply_count, 0).label('reply_count')
    ).outerjoin(
        topic_counts, topic_counts.c.category_id == ForumCategory.id
    ).outerjoin(
        reply_counts, reply_counts.c.category_id == ForumCategory.id
    ).filter(
        ForumCategory.is_visible == True
    ).order_by(ForumCategory.display_order).all()

    result = []
    for cat, topic_count, reply_count in categories:
        # Post count = topic count + reply count
        post_count = (topic_count or 0) + (reply_count or 0)
        result.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "description": cat.description,
            "icon": cat.icon or "📁",
            "color": cat.color or "#ff6b00",
            "display_order": cat.display_order or 0,
            "topic_count": topic_count or 0,
            "post_count": post_count,
            "reply_count": reply_count or 0
        })

    response = {"categories": result}

    # Cache'e kaydet
    try:
        await redis_manager.set(cache_key, json.dumps(response), expire=CACHE_TTL)
    except Exception:
        pass  # Cache yazma hatasi kritik degil

    return response


@router.get("/categories/{slug}")
async def get_category(slug: str, db: Session = Depends(get_db)):
    """Kategori detayı"""
    category = db.query(ForumCategory).filter(
        ForumCategory.slug == slug,
        ForumCategory.is_visible == True
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")

    topic_count = db.query(func.count(ForumTopic.id)).filter(
        ForumTopic.category_id == category.id
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
    has_replies: Optional[bool] = None,
    date_from: Optional[str] = None,  # YYYY-MM-DD
    date_to: Optional[str] = None,
    author_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Kategorinin konularini getir - Gelismis filtreler ile
    - has_replies: Sadece yaniti olan/olmayan konulari getir
    - date_from: Baslangic tarihi (YYYY-MM-DD)
    - date_to: Bitis tarihi (YYYY-MM-DD)
    - author_id: Belirli bir yazarin konulari
    """
    category = db.query(ForumCategory).filter(
        ForumCategory.slug == slug,
        ForumCategory.is_visible == True
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadi")

    # Reply counts subquery - needed for has_replies filter and sorting
    reply_count_subq = db.query(
        ForumReply.topic_id,
        func.count(ForumReply.id).label('reply_count')
    ).filter(ForumReply.is_active == True).group_by(ForumReply.topic_id).subquery()

    query = db.query(ForumTopic).options(
        joinedload(ForumTopic.author)
    ).outerjoin(
        reply_count_subq, ForumTopic.id == reply_count_subq.c.topic_id
    ).filter(
        ForumTopic.category_id == category.id,
        ForumTopic.is_active == True
    )

    # Apply advanced filters
    if has_replies is not None:
        if has_replies:
            query = query.filter(reply_count_subq.c.reply_count > 0)
        else:
            query = query.filter(or_(
                reply_count_subq.c.reply_count == None,
                reply_count_subq.c.reply_count == 0
            ))

    # Date filters
    from_date = parse_date(date_from)
    to_date = parse_date(date_to)
    if from_date:
        query = query.filter(ForumTopic.created_at >= from_date)
    if to_date:
        # Include the entire end date
        query = query.filter(ForumTopic.created_at < to_date + timedelta(days=1))

    # Author filter
    if author_id:
        query = query.filter(ForumTopic.author_id == author_id)

    # Sorting
    if sort == "oldest":
        query = query.order_by(desc(ForumTopic.is_pinned), ForumTopic.created_at)
    elif sort == "popular":
        query = query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.view_count))
    elif sort == "most_replies":
        query = query.order_by(desc(ForumTopic.is_pinned), desc(func.coalesce(reply_count_subq.c.reply_count, 0)))
    else:  # newest (default)
        query = query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.created_at))

    total = query.count()
    topics = query.offset((page - 1) * limit).limit(limit).all()

    # Get reply counts for all topics in a single query (N+1 fix)
    topic_ids = [t.id for t in topics]
    if topic_ids:
        reply_counts_query = db.query(
            ForumReply.topic_id,
            func.count(ForumReply.id).label('reply_count')
        ).filter(
            ForumReply.topic_id.in_(topic_ids),
            ForumReply.is_active == True
        ).group_by(ForumReply.topic_id).all()
        reply_counts_map = {topic_id: count for topic_id, count in reply_counts_query}
    else:
        reply_counts_map = {}

    result = []
    for topic in topics:
        result.append({
            "id": topic.id,
            "title": topic.title,
            "slug": topic.slug,
            "author_id": topic.author_id,
            "author_name": topic.author.username if topic.author else None,
            "author_avatar": topic.author.avatar if topic.author else None,
            "is_pinned": topic.is_pinned,
            "is_locked": topic.is_locked,
            "view_count": topic.view_count or 0,
            "reply_count": reply_counts_map.get(topic.id, 0),
            "created_at": topic.created_at.isoformat() if topic.created_at else None
        })

    return {
        "topics": result,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "filters": {
            "has_replies": has_replies,
            "date_from": date_from,
            "date_to": date_to,
            "author_id": author_id
        }
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
    ).order_by(
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


@router.get("/topics/popular")
async def get_popular_topics(db: Session = Depends(get_db)):
    """Populer konulari getir - Redis cache ile (60 saniye)"""
    import json
    from app.core.redis_manager import redis_manager

    cache_key = "forum:popular_topics"
    CACHE_TTL = 60  # 60 saniye

    # Cache kontrol
    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass  # Cache hatasi durumunda DB'den devam

    # Top 10 populer konulari getir (view_count'a gore)
    topics = db.query(ForumTopic).options(
        joinedload(ForumTopic.author),
        joinedload(ForumTopic.category)
    ).filter(
        ForumTopic.is_active == True
    ).order_by(
        desc(ForumTopic.view_count)
    ).limit(10).all()

    # Reply count'lari tek sorguda al
    topic_ids = [t.id for t in topics]
    reply_counts_query = db.query(
        ForumReply.topic_id,
        func.count(ForumReply.id).label('reply_count')
    ).filter(
        ForumReply.topic_id.in_(topic_ids)
    ).group_by(ForumReply.topic_id).all()

    reply_counts_map = {topic_id: count for topic_id, count in reply_counts_query}

    result = []
    for topic in topics:
        result.append({
            "id": topic.id,
            "title": topic.title,
            "slug": topic.slug,
            "category_id": topic.category_id,
            "category_name": topic.category.name if topic.category else None,
            "author_name": topic.author.username if topic.author else None,
            "author_avatar": topic.author.avatar if topic.author else None,
            "view_count": topic.view_count or 0,
            "reply_count": reply_counts_map.get(topic.id, 0),
            "created_at": topic.created_at.isoformat() if topic.created_at else None
        })

    response = {"topics": result}

    # Cache'e kaydet
    try:
        await redis_manager.set(cache_key, json.dumps(response), expire=CACHE_TTL)
    except Exception:
        pass  # Cache yazma hatasi kritik degil

    return response


@router.get("/topics/{slug}")
async def get_topic(slug: str, db: Session = Depends(get_db)):
    """Konu detayı"""
    topic = db.query(ForumTopic).options(
        joinedload(ForumTopic.author),
        joinedload(ForumTopic.category)
    ).filter(
        ForumTopic.slug == slug
    ).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadı")

    # Görüntülenme sayısını atomik olarak artır (race condition önleme)
    db.query(ForumTopic).filter(ForumTopic.id == topic.id).update(
        {ForumTopic.view_count: func.coalesce(ForumTopic.view_count, 0) + 1}
    )
    db.commit()

    # Güncel view_count değerini al
    topic.view_count = (topic.view_count or 0) + 1
    
    reply_count = db.query(func.count(ForumReply.id)).filter(
        ForumReply.topic_id == topic.id
    ).scalar() or 0

    # Get topic tags
    topic_tags = []
    try:
        topic_tags = get_topic_tags(db, topic.id)
    except Exception:
        pass

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
        "author_avatar": topic.author.avatar if topic.author else None,
        "is_pinned": topic.is_pinned,
        "is_locked": topic.is_locked,
        "view_count": topic.view_count,
        "reply_count": reply_count,
        "tags": topic_tags,
        "created_at": topic.created_at.isoformat() if topic.created_at else None
    }


@router.post("/topics", status_code=status.HTTP_201_CREATED)
async def create_topic(
    data: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Yeni konu oluştur"""
    # Rate limit check
    if await check_forum_rate_limit(current_user.id, "topic"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Cok fazla konu olusturdunuz. Saatte en fazla {TOPIC_RATE_LIMIT} konu olusturabilirsiniz."
        )

    # ===== CONTENT MODERATION CHECK =====
    from app.core.content_filter import check_and_process_content

    # Baslik ve icerik kontrolu
    combined_content = f"{data.title} {data.content}"
    moderation_result = check_and_process_content(
        db=db,
        content=combined_content,
        user_id=current_user.id,
        action="topic",
        auto_warn=True,
        auto_filter=False  # Reddet modu (True = filtrele ve izin ver)
    )

    # Kullanici banli mi?
    if moderation_result.get("banned"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=moderation_result.get("message", "Forum erimisiniz askiya alindi")
        )

    # Icerik uygun degil mi?
    if not moderation_result.get("allowed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=moderation_result.get("message", "Icerik kurallara uygun degil")
        )
    # ===== END CONTENT MODERATION =====

    # Kategori kontrolü
    category = db.query(ForumCategory).filter(
        ForumCategory.id == data.category_id,
        ForumCategory.is_visible == True
    ).first()

    if not category:
        raise HTTPException(status_code=400, detail="Geçersiz kategori")

    # Validation
    if len(data.title.strip()) < 5:
        raise HTTPException(status_code=400, detail="Başlık en az 5 karakter olmalı")

    if len(data.content.strip()) < 20:
        raise HTTPException(status_code=400, detail="İçerik en az 20 karakter olmalı")

    # XSS Protection - Sanitize title and content
    sanitized_title = sanitize_title(data.title)
    sanitized_content = sanitize_forum_content(data.content)

    slug = generate_slug(sanitized_title)
    slug = ensure_unique_slug(db, slug)

    topic = ForumTopic(
        title=sanitized_title,
        slug=slug,
        category_id=data.category_id,
        author_id=current_user.id,
        content=sanitized_content,
        is_active=True
    )

    db.add(topic)
    db.commit()
    db.refresh(topic)

    # Link tags to topic (if provided)
    if data.tags:
        try:
            ensure_forum_tables(db)
            link_tags_to_topic(db, topic.id, data.tags)
            db.commit()
        except Exception as e:
            logger.warning(f"Tag linking error: {e}")

    # Process @mentions in content
    try:
        process_mentions(db, data.content, "topic", topic.id, current_user.id, topic.slug)
        db.commit()
    except Exception as e:
        logger.warning(f"Mention processing error: {e}")

    # Yeni konu olusturuldu, cache'leri temizle
    await invalidate_forum_cache()

    # Reputation reward (+5 for topic creation)
    try:
        current_user.reputation = (current_user.reputation or 0) + 5
        db.commit()
    except Exception:
        pass

    # Badge check
    try:
        from app.services.forum_gamification import get_forum_gamification_service
        gamification_service = get_forum_gamification_service(db)
        await gamification_service.check_and_award_badges(current_user.id)
    except Exception:
        pass

    # Forum puan odulu
    reward_amount = None
    try:
        from app.services.forum_rewards import get_forum_reward_service
        reward_service = get_forum_reward_service(db)
        reward_amount = reward_service.reward_topic_create(
            user_id=current_user.id,
            topic_id=topic.id
        )
    except Exception as e:
        # Ödül hatası ana işlemi etkilemesin
        pass

    response = {
        "message": "Konu oluşturuldu",
        "topic_id": topic.id,
        "slug": topic.slug
    }

    if reward_amount:
        response["reward"] = {
            "amount": reward_amount,
            "message": f"+{reward_amount} Coin kazandınız!"
        }

    return response


# ============ Reply Endpoints ============

@router.get("/topics/{slug}/replies")
async def get_topic_replies(
    slug: str,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Konunun yanitlarini getir (sayfalama destekli)"""
    topic = db.query(ForumTopic).filter(
        ForumTopic.slug == slug,
        ForumTopic.is_active == True
    ).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")

    # Total count for pagination
    total = db.query(func.count(ForumReply.id)).filter(
        ForumReply.topic_id == topic.id,
        ForumReply.is_active == True
    ).scalar() or 0

    # Paginated query with ordering by created_at ASC
    replies = db.query(ForumReply).options(
        joinedload(ForumReply.author)
    ).filter(
        ForumReply.topic_id == topic.id,
        ForumReply.is_active == True
    ).order_by(ForumReply.created_at).offset((page - 1) * limit).limit(limit).all()

    has_more = (page * limit) < total

    return {
        "replies": [
            {
                "id": r.id,
                "content": r.content,
                "author_id": r.user_id,
                "author_name": r.author.username if r.author else None,
                "author_avatar": r.author.avatar if r.author else None,
                "is_best_answer": getattr(r, 'is_best_answer', False) or False,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in replies
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "has_more": has_more
    }


@router.post("/topics/{slug}/replies", status_code=status.HTTP_201_CREATED)
async def create_reply(
    slug: str,
    data: ReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Yanıt ekle"""
    # Rate limit check
    if await check_forum_rate_limit(current_user.id, "reply"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Cok fazla yanit yazdınız. Saatte en fazla {REPLY_RATE_LIMIT} yanit yazabilirsiniz."
        )

    # ===== CONTENT MODERATION CHECK =====
    from app.core.content_filter import check_and_process_content

    moderation_result = check_and_process_content(
        db=db,
        content=data.content,
        user_id=current_user.id,
        action="reply",
        auto_warn=True,
        auto_filter=False  # Reddet modu
    )

    # Kullanici banli mi?
    if moderation_result.get("banned"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=moderation_result.get("message", "Forum erimisiniz askiya alindi")
        )

    # Icerik uygun degil mi?
    if not moderation_result.get("allowed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=moderation_result.get("message", "Icerik kurallara uygun degil")
        )
    # ===== END CONTENT MODERATION =====

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

    # XSS Protection - Sanitize reply content
    sanitized_content = sanitize_forum_content(data.content)

    reply = ForumReply(
        topic_id=topic.id,
        user_id=current_user.id,
        content=sanitized_content,
        is_active=True
    )

    db.add(reply)
    db.commit()
    db.refresh(reply)

    # Process @mentions in content
    try:
        process_mentions(db, data.content, "reply", reply.id, current_user.id, topic.slug)
        db.commit()
    except Exception as e:
        logger.warning(f"Mention processing error: {e}")

    # Notify subscribers about new reply
    try:
        notify_subscribers(db, topic.id, current_user.id, topic.title, topic.slug)
        db.commit()
    except Exception as e:
        logger.warning(f"Subscriber notification error: {e}")

    # Reputation reward (+2 for reply creation)
    try:
        current_user.reputation = (current_user.reputation or 0) + 2
        db.commit()
    except Exception:
        pass

    # Badge check
    try:
        from app.services.forum_gamification import get_forum_gamification_service
        gamification_service = get_forum_gamification_service(db)
        await gamification_service.check_and_award_badges(current_user.id)
    except Exception:
        pass

    # Forum puan ödülü
    reward_amount = None
    try:
        from app.services.forum_rewards import get_forum_reward_service
        reward_service = get_forum_reward_service(db)
        reward_amount = reward_service.reward_reply_create(
            user_id=current_user.id,
            reply_id=reply.id,
            topic_id=topic.id
        )
    except Exception as e:
        # Ödül hatası ana işlemi etkilemesin
        pass

    # Broadcast new reply via WebSocket
    try:
        from app.api.websocket import broadcast_forum_new_reply
        reply_data = {
            "id": reply.id,
            "content": reply.content,
            "author": {
                "id": current_user.id,
                "username": current_user.display_name or current_user.username,
                "avatar": current_user.avatar
            },
            "created_at": reply.created_at.isoformat() if reply.created_at else None
        }
        await broadcast_forum_new_reply(topic.id, reply_data)
    except Exception as e:
        # WebSocket hatası ana işlemi etkilemesin
        pass

    response = {
        "message": "Yanıt eklendi",
        "reply_id": reply.id,
        "reply": {
            "id": reply.id,
            "content": reply.content,
            "author_id": current_user.id,
            "author_name": current_user.display_name or current_user.username,
            "author_avatar": current_user.avatar,
            "created_at": reply.created_at.isoformat() if reply.created_at else None
        }
    }

    if reward_amount:
        response["reward"] = {
            "amount": reward_amount,
            "message": f"+{reward_amount} Coin kazandınız!"
        }

    return response


# ============ Stats Endpoint ============

@router.get("/stats")
async def get_forum_stats(db: Session = Depends(get_db)):
    """Forum istatistikleri (public)"""
    category_count = db.query(func.count(ForumCategory.id)).filter(
        ForumCategory.is_visible == True
    ).scalar() or 0

    topic_count = db.query(func.count(ForumTopic.id)).filter(
        ForumTopic.is_active == True
    ).scalar() or 0

    reply_count = db.query(func.count(ForumReply.id)).filter(
        ForumReply.is_active == True
    ).scalar() or 0

    # Total posts = topics + replies
    total_posts = topic_count + reply_count

    # Total members
    member_count = db.query(func.count(User.id)).scalar() or 0

    # Online users - simplified
    online_count = 0
    try:
        from datetime import datetime, timedelta
        fifteen_min_ago = datetime.utcnow() - timedelta(minutes=15)
        if hasattr(User, 'last_activity'):
            online_count = db.query(func.count(User.id)).filter(
                User.last_activity >= fifteen_min_ago
            ).scalar() or 0
    except Exception:
        pass

    return {
        "categories": category_count,
        "topics": topic_count,
        "replies": reply_count,
        "total_topics": topic_count,
        "topics_count": topic_count,
        "total_posts": total_posts,
        "posts_count": total_posts,
        "total_members": member_count,
        "members_count": member_count,
        "online_users": online_count,
        "online_count": online_count
    }


@router.get("/rewards/me")
async def get_my_forum_rewards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanıcının forum puan istatistikleri"""
    from app.services.forum_rewards import get_forum_reward_service
    reward_service = get_forum_reward_service(db)
    return reward_service.get_user_forum_stats(current_user.id)


@router.get("/rewards/info")
async def get_forum_reward_info():
    """Forum puan sistemi bilgileri"""
    from app.services.forum_rewards import (
        REWARD_TOPIC_CREATE,
        REWARD_REPLY_CREATE,
        REWARD_LIKE_RECEIVED,
        REWARD_FIRST_TOPIC,
        REWARD_FIRST_REPLY,
        DAILY_TOPIC_LIMIT,
        DAILY_REPLY_LIMIT,
        DAILY_LIKE_LIMIT
    )

    return {
        "rewards": {
            "topic_create": REWARD_TOPIC_CREATE,
            "reply_create": REWARD_REPLY_CREATE,
            "like_received": REWARD_LIKE_RECEIVED,
            "first_topic_bonus": REWARD_FIRST_TOPIC,
            "first_reply_bonus": REWARD_FIRST_REPLY
        },
        "daily_limits": {
            "topics": DAILY_TOPIC_LIMIT,
            "replies": DAILY_REPLY_LIMIT,
            "likes": DAILY_LIKE_LIMIT
        }
    }


# ============ User Moderation Status ============

@router.get("/moderation/status")
async def get_my_moderation_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Kullanicinin moderasyon durumunu getir.
    - Aktif uyari sayisi
    - Ban durumu
    - Posting izni
    """
    from app.core.content_filter import get_warning_system

    warning_system = get_warning_system(db)

    # Ban durumu kontrolu
    is_banned, ban_info = warning_system.check_ban_status(current_user.id)

    # Aktif uyari sayisi
    active_warnings = warning_system.get_active_warning_count(current_user.id)

    # Uyari detaylari
    warnings = warning_system.get_user_warnings(current_user.id, active_only=True)

    # Maksimum uyari sayisi
    from app.core.content_filter import MAX_WARNINGS_BEFORE_BAN

    return {
        "can_post": not is_banned,
        "is_banned": is_banned,
        "ban_info": ban_info,
        "warnings": {
            "count": active_warnings,
            "max": MAX_WARNINGS_BEFORE_BAN,
            "list": warnings
        }
    }


# ============ Moderation Endpoints ============

@router.put("/topics/{slug}")
async def edit_topic(
    slug: str,
    data: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Edit a topic - only author or admin can edit.
    Updates title and/or content, tracks edit history.
    """
    topic = db.query(ForumTopic).filter(
        ForumTopic.slug == slug,
        ForumTopic.is_active == True
    ).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")

    # Permission check: only author or admin can edit
    if not is_admin_or_author(current_user, topic.author_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu konuyu duzenleme yetkiniz yok"
        )

    # Validate and update title if provided
    if data.title is not None:
        title = data.title.strip()
        if len(title) < 5:
            raise HTTPException(status_code=400, detail="Baslik en az 5 karakter olmali")
        if len(title) > 200:
            raise HTTPException(status_code=400, detail="Baslik en fazla 200 karakter olmali")
        topic.title = title
        # Update slug if title changed
        new_slug = generate_slug(title)
        if new_slug != topic.slug:
            new_slug = ensure_unique_slug(db, new_slug)
            topic.slug = new_slug

    # Validate and update content if provided
    if data.content is not None:
        content = data.content.strip()
        if len(content) < 20:
            raise HTTPException(status_code=400, detail="Icerik en az 20 karakter olmali")
        topic.content = content

    # Track edit history
    topic.edited_at = datetime.utcnow()
    topic.edited_by = current_user.id

    db.commit()
    db.refresh(topic)

    # Invalidate cache
    await invalidate_forum_cache()

    return {
        "message": "Konu guncellendi",
        "topic_id": topic.id,
        "slug": topic.slug,
        "edited_at": topic.edited_at.isoformat() if topic.edited_at else None
    }


@router.delete("/topics/{slug}")
async def delete_topic(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Delete a topic (soft delete) - only author or admin can delete.
    Sets is_active = False instead of actually deleting.
    """
    topic = db.query(ForumTopic).filter(
        ForumTopic.slug == slug,
        ForumTopic.is_active == True
    ).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")

    # Permission check: only author or admin can delete
    if not is_admin_or_author(current_user, topic.author_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu konuyu silme yetkiniz yok"
        )

    # Soft delete
    topic.is_active = False
    db.commit()

    # Invalidate cache
    await invalidate_forum_cache()

    return {
        "message": "Konu silindi",
        "topic_id": topic.id
    }


@router.put("/replies/{reply_id}")
async def edit_reply(
    reply_id: int,
    data: ReplyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Edit a reply - only author or admin can edit.
    Updates content only, tracks edited_at timestamp.
    """
    reply = db.query(ForumReply).filter(
        ForumReply.id == reply_id,
        ForumReply.is_active == True
    ).first()

    if not reply:
        raise HTTPException(status_code=404, detail="Yanit bulunamadi")

    # Permission check: only author or admin can edit
    if not is_admin_or_author(current_user, reply.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu yaniti duzenleme yetkiniz yok"
        )

    # Validate content
    content = data.content.strip()
    if len(content) < 3:
        raise HTTPException(status_code=400, detail="Yanit en az 3 karakter olmali")

    # Update content and track edit time
    reply.content = content
    reply.edited_at = datetime.utcnow()

    db.commit()
    db.refresh(reply)

    return {
        "message": "Yanit guncellendi",
        "reply_id": reply.id,
        "edited_at": reply.edited_at.isoformat() if reply.edited_at else None
    }


@router.delete("/replies/{reply_id}")
async def delete_reply(
    reply_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Delete a reply (soft delete) - only author or admin can delete.
    Sets is_active = False instead of actually deleting.
    """
    reply = db.query(ForumReply).filter(
        ForumReply.id == reply_id,
        ForumReply.is_active == True
    ).first()

    if not reply:
        raise HTTPException(status_code=404, detail="Yanit bulunamadi")

    # Permission check: only author or admin can delete
    if not is_admin_or_author(current_user, reply.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu yaniti silme yetkiniz yok"
        )

    # Soft delete
    reply.is_active = False
    db.commit()

    return {
        "message": "Yanit silindi",
        "reply_id": reply.id
    }


@router.post("/report", status_code=status.HTTP_201_CREATED)
async def report_content(
    data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Report forum content (topic or reply) for moderation.
    Prevents duplicate reports from the same user.
    """
    # Validate content_type
    if data.content_type not in ["topic", "reply"]:
        raise HTTPException(
            status_code=400,
            detail="Gecersiz icerik turu. 'topic' veya 'reply' olmali"
        )

    # Validate reason
    valid_reasons = ["spam", "harassment", "inappropriate", "other"]
    if data.reason not in valid_reasons:
        raise HTTPException(
            status_code=400,
            detail=f"Gecersiz sikayet nedeni. Gecerli nedenler: {', '.join(valid_reasons)}"
        )

    # Check if content exists
    if data.content_type == "topic":
        content = db.query(ForumTopic).filter(
            ForumTopic.id == data.content_id,
            ForumTopic.is_active == True
        ).first()
        if not content:
            raise HTTPException(status_code=404, detail="Konu bulunamadi")
        # Prevent self-reporting
        if content.author_id == current_user.id:
            raise HTTPException(status_code=400, detail="Kendi iceriklerinizi sikayet edemezsiniz")
    else:  # reply
        content = db.query(ForumReply).filter(
            ForumReply.id == data.content_id,
            ForumReply.is_active == True
        ).first()
        if not content:
            raise HTTPException(status_code=404, detail="Yanit bulunamadi")
        # Prevent self-reporting
        if content.user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Kendi iceriklerinizi sikayet edemezsiniz")

    # Check for duplicate report
    existing_report = db.query(ForumReport).filter(
        ForumReport.reporter_id == current_user.id,
        ForumReport.content_type == data.content_type,
        ForumReport.content_id == data.content_id
    ).first()

    if existing_report:
        raise HTTPException(
            status_code=400,
            detail="Bu icerigi zaten sikayet ettiniz"
        )

    # Create report
    report = ForumReport(
        reporter_id=current_user.id,
        content_type=data.content_type,
        content_id=data.content_id,
        reason=data.reason,
        details=data.details.strip() if data.details else None
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "message": "Sikayetiniz alindi. Moderatorler en kisa surede inceleyecektir.",
        "report_id": report.id
    }


# ============ Table Creation Helper ============

def ensure_forum_tables(db: Session):
    """Ensure all new forum tables exist"""
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS forum_tags (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                slug VARCHAR(50) UNIQUE NOT NULL,
                color VARCHAR(20) DEFAULT '#6b7280',
                usage_count INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_tag_slug (slug),
                INDEX idx_tag_usage (usage_count)
            )
        """))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS forum_topic_tags (
                topic_id INT NOT NULL,
                tag_id INT NOT NULL,
                PRIMARY KEY (topic_id, tag_id),
                FOREIGN KEY (topic_id) REFERENCES forum_topics(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES forum_tags(id) ON DELETE CASCADE
            )
        """))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS forum_mentions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                mentioned_by INT NOT NULL,
                content_type VARCHAR(20) NOT NULL,
                content_id INT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_mention_user (user_id, is_read),
                INDEX idx_mention_content (content_type, content_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (mentioned_by) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS forum_subscriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                topic_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_forum_subscription (user_id, topic_id),
                INDEX idx_subscription_user (user_id),
                INDEX idx_subscription_topic (topic_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (topic_id) REFERENCES forum_topics(id) ON DELETE CASCADE
            )
        """))
        try:
            db.execute(text("ALTER TABLE forum_replies ADD COLUMN is_best_answer BOOLEAN DEFAULT FALSE"))
        except Exception:
            pass
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"Table creation warning: {e}")


# ============ Tag Helper Functions ============

def get_or_create_tag(db: Session, tag_name: str) -> ForumTag:
    """Get existing tag or create a new one"""
    tag_name = tag_name.strip().lower()[:50]
    if not tag_name:
        return None
    tag_slug = generate_slug(tag_name)
    if not tag_slug:
        return None
    tag = db.query(ForumTag).filter(or_(ForumTag.name == tag_name, ForumTag.slug == tag_slug)).first()
    if not tag:
        tag = ForumTag(name=tag_name, slug=tag_slug, color="#6b7280", usage_count=0)
        db.add(tag)
        db.flush()
    return tag


def link_tags_to_topic(db: Session, topic_id: int, tag_names: List[str]):
    """Link tags to a topic and update usage counts"""
    if not tag_names:
        return
    for tag_name in tag_names[:5]:
        tag = get_or_create_tag(db, tag_name)
        if tag:
            existing = db.query(ForumTopicTag).filter(ForumTopicTag.topic_id == topic_id, ForumTopicTag.tag_id == tag.id).first()
            if not existing:
                topic_tag = ForumTopicTag(topic_id=topic_id, tag_id=tag.id)
                db.add(topic_tag)
                tag.usage_count = (tag.usage_count or 0) + 1


def get_topic_tags(db: Session, topic_id: int) -> List[dict]:
    """Get tags for a topic"""
    tags = db.query(ForumTag).join(ForumTopicTag, ForumTopicTag.tag_id == ForumTag.id).filter(ForumTopicTag.topic_id == topic_id).all()
    return [{"id": t.id, "name": t.name, "slug": t.slug, "color": t.color} for t in tags]


# ============ Mention Helper Functions ============

def extract_mentions(content: str) -> List[str]:
    """Extract @username mentions from content"""
    pattern = r'@([a-zA-Z0-9_-]+)'
    matches = re.findall(pattern, content)
    return list(set(matches))


def process_mentions(db: Session, content: str, content_type: str, content_id: int, mentioned_by_id: int, topic_slug: str = None):
    """Process @mentions in content and create notifications"""
    usernames = extract_mentions(content)
    if not usernames:
        return
    for username in usernames[:10]:
        mentioned_user = db.query(User).filter(User.username == username).first()
        if mentioned_user and mentioned_user.id != mentioned_by_id:
            mention = ForumMention(user_id=mentioned_user.id, mentioned_by=mentioned_by_id, content_type=content_type, content_id=content_id, is_read=False)
            db.add(mention)
            mentioner = db.query(User).filter(User.id == mentioned_by_id).first()
            mentioner_name = mentioner.username if mentioner else "Birisi"
            notification = Notification(user_id=mentioned_user.id, type="forum_mention", title="Sizi etiketledi", message=f"@{mentioner_name} sizi bir {'konuda' if content_type == 'topic' else 'yanıtta'} etiketledi.", link=f"/forum/topic/{topic_slug}" if topic_slug else None, is_read=False)
            db.add(notification)


# ============ Subscription Helper Functions ============

def notify_subscribers(db: Session, topic_id: int, replier_id: int, topic_title: str, topic_slug: str):
    """Notify all subscribers of a topic about a new reply"""
    subscriptions = db.query(ForumSubscription).filter(ForumSubscription.topic_id == topic_id, ForumSubscription.user_id != replier_id).all()
    replier = db.query(User).filter(User.id == replier_id).first()
    replier_name = replier.username if replier else "Birisi"
    for sub in subscriptions:
        notification = Notification(user_id=sub.user_id, type="forum_subscription", title="Takip ettiginiz konuya yanit geldi", message=f"@{replier_name}, '{topic_title[:50]}...' konusuna yanit verdi.", link=f"/forum/topic/{topic_slug}", is_read=False)
        db.add(notification)


# ============ Tag Endpoints ============

@router.get("/tags")
async def get_tags(limit: int = 50, db: Session = Depends(get_db)):
    """List all tags sorted by usage count"""
    ensure_forum_tables(db)
    tags = db.query(ForumTag).order_by(desc(ForumTag.usage_count)).limit(limit).all()
    return {"tags": [{"id": t.id, "name": t.name, "slug": t.slug, "color": t.color, "usage_count": t.usage_count or 0} for t in tags]}


@router.get("/tags/{slug}/topics")
async def get_topics_by_tag(slug: str, page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    """Get topics with a specific tag"""
    ensure_forum_tables(db)
    tag = db.query(ForumTag).filter(ForumTag.slug == slug).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Etiket bulunamadi")
    query = db.query(ForumTopic).join(ForumTopicTag, ForumTopicTag.topic_id == ForumTopic.id).filter(ForumTopicTag.tag_id == tag.id, ForumTopic.is_active == True).options(joinedload(ForumTopic.author)).order_by(desc(ForumTopic.created_at))
    total = query.count()
    topics = query.offset((page - 1) * limit).limit(limit).all()
    topic_ids = [t.id for t in topics]
    reply_counts = {}
    if topic_ids:
        counts = db.query(ForumReply.topic_id, func.count(ForumReply.id)).filter(ForumReply.topic_id.in_(topic_ids)).group_by(ForumReply.topic_id).all()
        reply_counts = {tid: cnt for tid, cnt in counts}
    return {
        "tag": {"id": tag.id, "name": tag.name, "slug": tag.slug, "color": tag.color, "usage_count": tag.usage_count or 0},
        "topics": [{"id": t.id, "title": t.title, "slug": t.slug, "author_name": t.author.username if t.author else None, "author_avatar": t.author.avatar if t.author else None, "view_count": t.view_count or 0, "reply_count": reply_counts.get(t.id, 0), "created_at": t.created_at.isoformat() if t.created_at else None} for t in topics],
        "total": total, "page": page, "pages": (total + limit - 1) // limit
    }


# ============ Subscription Endpoints ============

@router.post("/topics/{slug}/subscribe")
async def subscribe_to_topic(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Subscribe to a topic"""
    ensure_forum_tables(db)
    topic = db.query(ForumTopic).filter(ForumTopic.slug == slug, ForumTopic.is_active == True).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")
    existing = db.query(ForumSubscription).filter(ForumSubscription.user_id == current_user.id, ForumSubscription.topic_id == topic.id).first()
    if existing:
        return {"message": "Zaten bu konuya abone olmuşsunuz", "subscribed": True}
    subscription = ForumSubscription(user_id=current_user.id, topic_id=topic.id)
    db.add(subscription)
    db.commit()
    return {"message": "Konuya abone oldunuz", "subscribed": True}


@router.delete("/topics/{slug}/subscribe")
async def unsubscribe_from_topic(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Unsubscribe from a topic"""
    ensure_forum_tables(db)
    topic = db.query(ForumTopic).filter(ForumTopic.slug == slug, ForumTopic.is_active == True).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")
    subscription = db.query(ForumSubscription).filter(ForumSubscription.user_id == current_user.id, ForumSubscription.topic_id == topic.id).first()
    if not subscription:
        return {"message": "Bu konuya abone degilsiniz", "subscribed": False}
    db.delete(subscription)
    db.commit()
    return {"message": "Abonelik iptal edildi", "subscribed": False}


@router.get("/subscriptions")
async def get_user_subscriptions(page: int = 1, limit: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Get user's subscribed topics"""
    ensure_forum_tables(db)
    query = db.query(ForumTopic).join(ForumSubscription, ForumSubscription.topic_id == ForumTopic.id).filter(ForumSubscription.user_id == current_user.id, ForumTopic.is_active == True).options(joinedload(ForumTopic.author), joinedload(ForumTopic.category)).order_by(desc(ForumSubscription.created_at))
    total = query.count()
    topics = query.offset((page - 1) * limit).limit(limit).all()
    topic_ids = [t.id for t in topics]
    reply_counts = {}
    if topic_ids:
        counts = db.query(ForumReply.topic_id, func.count(ForumReply.id)).filter(ForumReply.topic_id.in_(topic_ids)).group_by(ForumReply.topic_id).all()
        reply_counts = {tid: cnt for tid, cnt in counts}
    return {
        "topics": [{"id": t.id, "title": t.title, "slug": t.slug, "category_name": t.category.name if t.category else None, "author_name": t.author.username if t.author else None, "view_count": t.view_count or 0, "reply_count": reply_counts.get(t.id, 0), "created_at": t.created_at.isoformat() if t.created_at else None} for t in topics],
        "total": total, "page": page, "pages": (total + limit - 1) // limit
    }


@router.get("/topics/{slug}/subscription-status")
async def get_subscription_status(slug: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Check if user is subscribed to a topic"""
    ensure_forum_tables(db)
    topic = db.query(ForumTopic).filter(ForumTopic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")
    subscription = db.query(ForumSubscription).filter(ForumSubscription.user_id == current_user.id, ForumSubscription.topic_id == topic.id).first()
    return {"subscribed": subscription is not None}


# ============ Best Answer Endpoints ============

@router.post("/replies/{reply_id}/best")
async def mark_best_answer(reply_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Mark a reply as the best answer (only topic author can do this)"""
    ensure_forum_tables(db)
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id, ForumReply.is_active == True).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Yanit bulunamadi")
    topic = db.query(ForumTopic).filter(ForumTopic.id == reply.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")
    if topic.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Sadece konu sahibi en iyi yaniti secebilir")
    db.query(ForumReply).filter(ForumReply.topic_id == topic.id, ForumReply.is_best_answer == True).update({"is_best_answer": False})
    reply.is_best_answer = True
    db.commit()
    if reply.user_id != current_user.id:
        notification = Notification(user_id=reply.user_id, type="forum_best_answer", title="Yanitiniz en iyi yanit secildi!", message=f"'{topic.title[:50]}...' konusundaki yanitiniz en iyi yanit olarak secildi.", link=f"/forum/topic/{topic.slug}", is_read=False)
        db.add(notification)
        db.commit()
    return {"message": "En iyi yanit secildi", "reply_id": reply_id}


@router.delete("/replies/{reply_id}/best")
async def unmark_best_answer(reply_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Remove best answer mark from a reply"""
    ensure_forum_tables(db)
    reply = db.query(ForumReply).filter(ForumReply.id == reply_id, ForumReply.is_active == True).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Yanit bulunamadi")
    topic = db.query(ForumTopic).filter(ForumTopic.id == reply.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")
    if topic.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Sadece konu sahibi en iyi yaniti kaldirabilir")
    reply.is_best_answer = False
    db.commit()
    return {"message": "En iyi yanit kaldirildi", "reply_id": reply_id}


# ============ Mention Endpoints ============

@router.get("/mentions")
async def get_user_mentions(page: int = 1, limit: int = 20, unread_only: bool = False, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Get user's mentions"""
    ensure_forum_tables(db)
    query = db.query(ForumMention).filter(ForumMention.user_id == current_user.id)
    if unread_only:
        query = query.filter(ForumMention.is_read == False)
    query = query.order_by(desc(ForumMention.created_at))
    total = query.count()
    mentions = query.offset((page - 1) * limit).limit(limit).all()
    result = []
    for m in mentions:
        mentioner = db.query(User).filter(User.id == m.mentioned_by).first()
        item = {"id": m.id, "content_type": m.content_type, "content_id": m.content_id, "mentioned_by": mentioner.username if mentioner else None, "mentioned_by_avatar": mentioner.avatar if mentioner else None, "is_read": m.is_read, "created_at": m.created_at.isoformat() if m.created_at else None}
        if m.content_type == "topic":
            t = db.query(ForumTopic).filter(ForumTopic.id == m.content_id).first()
            if t:
                item["link"] = f"/forum/topic/{t.slug}"
                item["title"] = t.title
        elif m.content_type == "reply":
            r = db.query(ForumReply).filter(ForumReply.id == m.content_id).first()
            if r:
                t = db.query(ForumTopic).filter(ForumTopic.id == r.topic_id).first()
                if t:
                    item["link"] = f"/forum/topic/{t.slug}"
                    item["title"] = t.title
        result.append(item)
    return {"mentions": result, "total": total, "page": page, "pages": (total + limit - 1) // limit}


@router.post("/mentions/{mention_id}/read")
async def mark_mention_read(mention_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Mark a mention as read"""
    ensure_forum_tables(db)
    mention = db.query(ForumMention).filter(ForumMention.id == mention_id, ForumMention.user_id == current_user.id).first()
    if not mention:
        raise HTTPException(status_code=404, detail="Mention bulunamadi")
    mention.is_read = True
    db.commit()
    return {"message": "Okundu olarak isaretlendi"}


@router.post("/mentions/read-all")
async def mark_all_mentions_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Mark all mentions as read"""
    ensure_forum_tables(db)
    db.query(ForumMention).filter(ForumMention.user_id == current_user.id, ForumMention.is_read == False).update({"is_read": True})
    db.commit()
    return {"message": "Tum mentionlar okundu olarak isaretlendi"}
