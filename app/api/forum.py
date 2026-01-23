# ============================================
# AGTR v6.0 - User Forum API
# Dosya: app/api/forum.py
# Versiyon: 6.1 - 25 Backend Improvements
# ============================================

import hashlib
import json
import logging
import random
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy import and_, case, desc, func, or_, text, asc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.redis_manager import redis_manager
from app.core.sanitizer import sanitize_forum_content, sanitize_title
from app.core.security import get_current_user, get_current_user_required, get_current_user_with_steam, get_current_user_optional
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

# ============ Constants ============
# Content length limits
MIN_TITLE_LENGTH = 5
MAX_TITLE_LENGTH = 200
MIN_CONTENT_LENGTH = 20
MAX_CONTENT_LENGTH = 50000  # 50KB max content
MIN_REPLY_LENGTH = 3
MAX_REPLY_LENGTH = 20000  # 20KB max reply
MAX_TAGS_PER_TOPIC = 5
MAX_MENTIONS_PER_CONTENT = 10

# Pagination limits
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 5

# Cache TTL values (seconds)
CACHE_TTL_CATEGORIES = 300  # 5 dakika
CACHE_TTL_TOPICS = 30  # 30 saniye - sik guncellenen veri
CACHE_TTL_TRENDING = 300  # 5 dakika
CACHE_TTL_POPULAR = 60  # 1 dakika
CACHE_TTL_SEARCH = 60  # 1 dakika

# Trending algorithm weights
TRENDING_REPLY_WEIGHT = 2.0  # Replies are more important
TRENDING_VIEW_WEIGHT = 0.1  # Views have less weight
TRENDING_RECENCY_BONUS = 1.5  # Bonus for newer topics


def format_avatar_url(avatar_path: str) -> str:
    """Format avatar path to full URL with proper prefix"""
    if not avatar_path:
        return None
    if avatar_path.startswith(('http://', 'https://', '/')):
        return avatar_path
    # Avatars are stored in /static/images/
    return f"/static/images/{avatar_path}"


def format_datetime_utc(dt: datetime) -> str:
    """Format datetime to ISO format with UTC timezone"""
    if not dt:
        return None
    # Ensure UTC timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def format_datetime_turkish(dt: datetime) -> str:
    """Format datetime to Turkish format (dd.mm.yyyy HH:MM)"""
    if not dt:
        return None
    # Ensure UTC timezone and format
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime("%d.%m.%Y %H:%M")


def validate_pagination(page: int, limit: int) -> Tuple[int, int]:
    """Validate and normalize pagination parameters"""
    page = max(1, page)
    limit = max(MIN_PAGE_SIZE, min(limit, MAX_PAGE_SIZE))
    return page, limit


def create_success_response(
    message: str,
    data: Dict[str, Any] = None,
    status_code: int = 200
) -> Dict[str, Any]:
    """Create standardized success response"""
    response = {
        "success": True,
        "message": message
    }
    if data:
        response.update(data)
    return response


def create_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    limit: int,
    item_key: str = "items"
) -> Dict[str, Any]:
    """Create standardized paginated response"""
    pages = (total + limit - 1) // limit if total > 0 else 0
    return {
        "success": True,
        item_key: items,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }
    }


def calculate_level_from_reputation(reputation: int) -> int:
    """Reputation'dan level hesapla"""
    if reputation is None or reputation < 0:
        return 1
    # Level formula: Her 50 reputation = 1 level, max 99
    level = 1 + (reputation // 50)
    return min(level, 99)


def format_author_info(user: User, include_extended: bool = False) -> Dict[str, Any]:
    """Format author information consistently"""
    if not user:
        return {
            "id": None,
            "username": "Anonim",
            "avatar": None,
            "level": 1,
            "role": None
        }

    reputation = getattr(user, 'reputation', 0) or 0
    level = calculate_level_from_reputation(reputation)

    info = {
        "id": user.id,
        "username": user.display_name or user.username,
        "avatar": format_avatar_url(user.avatar),
        "level": level,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role) if user.role else None
    }

    if include_extended:
        info.update({
            "reputation": getattr(user, 'reputation', 0) or 0,
            "post_count": getattr(user, 'post_count', 0) or 0,
            "joined_at": format_datetime_utc(user.created_at) if hasattr(user, 'created_at') else None
        })

    return info


# ============ Rate Limit Constants ============
# Rate limiting: Saatte izin verilen maksimum islem sayisi
# Bu limitler spam ve abuse'u onlemek icindir
TOPIC_RATE_LIMIT = 5  # Saatte max 5 konu olusturma
REPLY_RATE_LIMIT = 20  # Saatte max 20 yanit yazma
SEARCH_RATE_LIMIT = 30  # Saatte max 30 arama
RATE_LIMIT_WINDOW = 3600  # 1 saat (saniye cinsinden)


# ============ Pydantic Schemas ============

class TopicCreate(BaseModel):
    """Konu olusturma schemasi"""
    title: str = Field(..., min_length=MIN_TITLE_LENGTH, max_length=MAX_TITLE_LENGTH,
                       description="Konu basligi (5-200 karakter)")
    category_id: int = Field(..., gt=0, description="Kategori ID")
    content: str = Field(..., min_length=MIN_CONTENT_LENGTH, max_length=MAX_CONTENT_LENGTH,
                        description="Konu icerigi (20-50000 karakter)")
    tags: Optional[List[str]] = Field(None, max_items=MAX_TAGS_PER_TOPIC,
                                      description="Etiketler (max 5)")

    @validator('title')
    def validate_title(cls, v):
        v = v.strip()
        if len(v) < MIN_TITLE_LENGTH:
            raise ValueError(f'Baslik en az {MIN_TITLE_LENGTH} karakter olmali')
        if len(v) > MAX_TITLE_LENGTH:
            raise ValueError(f'Baslik en fazla {MAX_TITLE_LENGTH} karakter olmali')
        return v

    @validator('content')
    def validate_content(cls, v):
        v = v.strip()
        if len(v) < MIN_CONTENT_LENGTH:
            raise ValueError(f'Icerik en az {MIN_CONTENT_LENGTH} karakter olmali')
        if len(v) > MAX_CONTENT_LENGTH:
            raise ValueError(f'Icerik en fazla {MAX_CONTENT_LENGTH} karakter olmali')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v is None:
            return v
        # Remove empty tags and limit count
        v = [tag.strip().lower() for tag in v if tag and tag.strip()]
        return v[:MAX_TAGS_PER_TOPIC]


class ReplyCreate(BaseModel):
    """Yanit olusturma schemasi"""
    content: str = Field(..., min_length=MIN_REPLY_LENGTH, max_length=MAX_REPLY_LENGTH,
                        description="Yanit icerigi (3-20000 karakter)")
    parent_reply_id: Optional[int] = Field(None, description="Ust yanit ID (threading icin)")

    @validator('content')
    def validate_content(cls, v):
        v = v.strip()
        if len(v) < MIN_REPLY_LENGTH:
            raise ValueError(f'Yanit en az {MIN_REPLY_LENGTH} karakter olmali')
        if len(v) > MAX_REPLY_LENGTH:
            raise ValueError(f'Yanit en fazla {MAX_REPLY_LENGTH} karakter olmali')
        return v


class TopicUpdate(BaseModel):
    """Konu guncelleme schemasi"""
    title: Optional[str] = Field(None, min_length=MIN_TITLE_LENGTH, max_length=MAX_TITLE_LENGTH)
    content: Optional[str] = Field(None, min_length=MIN_CONTENT_LENGTH, max_length=MAX_CONTENT_LENGTH)

    @validator('title')
    def validate_title(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) < MIN_TITLE_LENGTH:
            raise ValueError(f'Baslik en az {MIN_TITLE_LENGTH} karakter olmali')
        if len(v) > MAX_TITLE_LENGTH:
            raise ValueError(f'Baslik en fazla {MAX_TITLE_LENGTH} karakter olmali')
        return v

    @validator('content')
    def validate_content(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) < MIN_CONTENT_LENGTH:
            raise ValueError(f'Icerik en az {MIN_CONTENT_LENGTH} karakter olmali')
        if len(v) > MAX_CONTENT_LENGTH:
            raise ValueError(f'Icerik en fazla {MAX_CONTENT_LENGTH} karakter olmali')
        return v


class ReplyUpdate(BaseModel):
    """Yanit guncelleme schemasi"""
    content: str = Field(..., min_length=MIN_REPLY_LENGTH, max_length=MAX_REPLY_LENGTH)

    @validator('content')
    def validate_content(cls, v):
        v = v.strip()
        if len(v) < MIN_REPLY_LENGTH:
            raise ValueError(f'Yanit en az {MIN_REPLY_LENGTH} karakter olmali')
        if len(v) > MAX_REPLY_LENGTH:
            raise ValueError(f'Yanit en fazla {MAX_REPLY_LENGTH} karakter olmali')
        return v


class ReportCreate(BaseModel):
    """Sikayet olusturma schemasi"""
    content_type: str = Field(..., pattern="^(topic|reply)$",
                              description="Icerik turu: 'topic' veya 'reply'")
    content_id: int = Field(..., gt=0, description="Icerik ID")
    reason: str = Field(..., pattern="^(spam|harassment|inappropriate|other)$",
                       description="Sikayet nedeni")
    details: Optional[str] = Field(None, max_length=1000,
                                   description="Ek detaylar (max 1000 karakter)")

    @validator('details')
    def validate_details(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) > 1000:
                raise ValueError('Detaylar en fazla 1000 karakter olmali')
        return v


# ============ Helper Functions ============

def safe_int_convert(value: str, default: Optional[int] = None) -> Optional[int]:
    """
    Safely convert string to int, handling large numbers and invalid inputs
    BUGFIX: Prevents ValueError from int() conversion
    """
    if not value:
        return default
    if not value.isdigit():
        return default
    try:
        result = int(value)
        # Protect against unreasonably large IDs
        if result > 2147483647:  # Max INT in MySQL
            return default
        return result
    except (ValueError, OverflowError):
        return default

async def invalidate_forum_cache(specific_keys: List[str] = None):
    """
    Forum cache'lerini temizle

    Args:
        specific_keys: Sadece belirli cache key'lerini temizle.
                       None ise tum forum cache'lerini temizler.
    """
    from app.core.redis_manager import redis_manager

    default_keys = [
        "forum:categories",
        "forum:popular_topics",
        "forum:trending",
        "forum:stats"
    ]

    keys_to_delete = specific_keys if specific_keys else default_keys

    try:
        for key in keys_to_delete:
            await redis_manager.delete(key)

        # Pattern-based cache invalidation for paginated topics
        # Delete all forum:topics:* keys
        try:
            keys = await redis_manager.keys("forum:topics:*")
            if keys:
                for key in keys:
                    await redis_manager.delete(key)
        except Exception:
            pass  # Pattern delete not critical

        logger.debug(f"Forum cache temizlendi: {keys_to_delete}")
    except Exception as e:
        logger.warning(f"Cache temizleme hatasi: {e}")


async def invalidate_topic_cache(topic_id: int = None, category_id: int = None):
    """Belirli bir konu veya kategorinin cache'ini temizle"""
    keys_to_delete = [
        "forum:trending",
        "forum:popular_topics"
    ]

    if topic_id:
        keys_to_delete.append(f"forum:topic:{topic_id}")

    if category_id:
        keys_to_delete.append(f"forum:category:{category_id}:topics")

    await invalidate_forum_cache(keys_to_delete)


def generate_slug(title: str) -> str:
    """
    Turkce karakterleri donusturup SEO-friendly slug olustur

    - Turkce karakterler -> Latin karakterler
    - Ozel karakterler kaldirilir
    - Bosluklar tire ile degistirilir
    - Ardisik tireler teke indirilir
    - Max 100 karakter (SEO icin optimal)
    """
    if not title:
        return ""

    tr_map = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u',
        'â': 'a', 'î': 'i', 'û': 'u', 'Â': 'a', 'Î': 'i', 'Û': 'u'
    }

    slug = title.lower().strip()

    # Replace Turkish characters
    for tr_char, en_char in tr_map.items():
        slug = slug.replace(tr_char, en_char)

    # Remove all non-alphanumeric characters except spaces and hyphens
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)

    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)

    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    # Remove leading/trailing hyphens and limit length
    slug = slug.strip('-')[:100]

    # Ensure slug is not empty
    if not slug:
        slug = f"topic-{secrets.token_hex(4)}"

    return slug


def ensure_unique_slug(db: Session, slug: str, exclude_id: int = None) -> str:
    """
    Benzersiz slug olustur

    Args:
        db: Database session
        slug: Base slug
        exclude_id: Bu ID'li konuyu kontrol disinda tut (guncelleme icin)
    """
    base_slug = slug
    counter = 1
    max_attempts = 100  # Sonsuz dongu onleme

    while counter <= max_attempts:
        query = db.query(ForumTopic).filter(ForumTopic.slug == slug)
        if exclude_id:
            query = query.filter(ForumTopic.id != exclude_id)

        if not query.first():
            return slug

        slug = f"{base_slug}-{counter}"
        counter += 1

    # Fallback: Add random suffix
    return f"{base_slug}-{secrets.token_hex(4)}"


async def check_forum_rate_limit(user_id: int, action_type: str) -> Tuple[bool, int]:
    """
    Check if user has exceeded rate limit for forum actions.

    Args:
        user_id: Kullanici ID
        action_type: Islem tipi ("topic", "reply", "search")

    Returns:
        Tuple[bool, int]: (rate_limited, remaining_seconds)
        - rate_limited: True ise limit asilmis, False ise izin var
        - remaining_seconds: Limitin sifirlanmasina kalan sure (saniye)
    """
    rate_limits = {
        "topic": (f"forum:ratelimit:{user_id}:topics", TOPIC_RATE_LIMIT),
        "reply": (f"forum:ratelimit:{user_id}:replies", REPLY_RATE_LIMIT),
        "search": (f"forum:ratelimit:{user_id}:search", SEARCH_RATE_LIMIT)
    }

    if action_type not in rate_limits:
        return False, 0

    key, limit = rate_limits[action_type]

    try:
        # Check if allowed using redis_manager's rate_limit_check
        # Returns True if allowed, False if rate limited
        allowed = await redis_manager.rate_limit_check(key, limit, RATE_LIMIT_WINDOW)

        # Get remaining time until reset
        remaining_seconds = 0
        if not allowed:
            try:
                ttl = await redis_manager.ttl(key)
                remaining_seconds = max(0, ttl) if ttl else RATE_LIMIT_WINDOW
            except Exception:
                remaining_seconds = RATE_LIMIT_WINDOW

        return not allowed, remaining_seconds
    except Exception as e:
        logger.error(f"Rate limit check error for user {user_id}: {e}")
        return False, 0  # Fail open - allow the action


def is_admin_or_moderator(user: User) -> bool:
    """Check if user is admin, superadmin, or moderator"""
    if not user:
        return False
    admin_roles = [UserRole.ADMIN, UserRole.SUPERADMIN]
    if hasattr(UserRole, 'MODERATOR'):
        admin_roles.append(UserRole.MODERATOR)
    return user.role in admin_roles


def is_admin_or_author(user: User, author_id: int) -> bool:
    """Check if user is admin, moderator, or the author of the content"""
    if not user:
        return False
    if user.id == author_id:
        return True
    return is_admin_or_moderator(user)


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse date string in YYYY-MM-DD format

    Args:
        date_str: Tarih string'i (YYYY-MM-DD)

    Returns:
        datetime object or None if invalid
    """
    if not date_str:
        return None

    # Validate format with regex first
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return None

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        # Add UTC timezone
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def calculate_hot_score(
    view_count: int,
    reply_count: int,
    created_at: datetime,
    recent_replies: int = 0
) -> float:
    """
    Hot/trending score hesapla (Reddit benzeri algoritma)

    Score = (reply_count * reply_weight + view_count * view_weight) * time_decay * recency_bonus

    Args:
        view_count: Goruntulenme sayisi
        reply_count: Toplam yanit sayisi
        created_at: Olusturulma tarihi
        recent_replies: Son 24 saatteki yanit sayisi
    """
    if not created_at:
        return 0.0

    # Ensure timezone-aware datetime
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    # Hours since creation
    hours_old = (now - created_at).total_seconds() / 3600
    hours_old = max(0.1, hours_old)  # Avoid division by zero

    # Base score
    base_score = (
        (reply_count or 0) * TRENDING_REPLY_WEIGHT +
        (view_count or 0) * TRENDING_VIEW_WEIGHT
    )

    # Time decay (logarithmic)
    import math
    time_decay = 1 / math.log(hours_old + 2, 10)

    # Recency bonus for recent activity
    recency_bonus = 1 + (recent_replies or 0) * TRENDING_RECENCY_BONUS

    return base_score * time_decay * recency_bonus


# ============ Search & Trending Endpoints ============

@router.get("/search")
async def search_forum(
    q: str = Query(..., min_length=2, max_length=100, description="Arama sorgusu (2-100 karakter)"),
    category_id: Optional[int] = Query(None, gt=0, description="Kategori filtresi"),
    author_id: Optional[int] = Query(None, gt=0, description="Yazar filtresi"),
    date_from: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Baslangic tarihi (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Bitis tarihi (YYYY-MM-DD)"),
    sort: str = Query("relevance", pattern="^(relevance|newest|oldest|popular|most_replies)$"),
    include_replies: bool = Query(False, description="Yanitlarda da ara"),
    page: int = Query(1, ge=1, le=100),  # Reduced from 1000 for performance
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db)
):
    """
    Forum arama - Konu basligi ve icerigi arar

    Arama Parametreleri:
    - q: Arama sorgusu (minimum 2, maksimum 100 karakter)
    - category_id: Kategori filtresi (opsiyonel)
    - author_id: Yazar filtresi (opsiyonel)
    - date_from: Baslangic tarihi YYYY-MM-DD formatinda (opsiyonel)
    - date_to: Bitis tarihi YYYY-MM-DD formatinda (opsiyonel)
    - sort: Siralama (relevance, newest, oldest, popular, most_replies)
    - include_replies: Yanitlarda da arama yap (varsayilan: False)
    - page: Sayfa numarasi (1-100)
    - limit: Sayfa basi sonuc sayisi (5-100)
    """
    # Validate pagination
    page, limit = validate_pagination(page, limit)

    # Log search for analytics
    logger.info(f"Forum search: query='{q}', category={category_id}, sort={sort}")

    try:
        # Parse and validate dates
        from_date = parse_date(date_from)
        to_date = parse_date(date_to)

        if from_date and to_date and from_date > to_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Baslangic tarihi bitis tarihinden sonra olamaz"
            )

        if to_date:
            # Include the entire end date
            to_date = to_date + timedelta(days=1)

        # Sanitize and prepare search pattern
        # Escape special SQL LIKE characters
        search_term = q.strip()
        search_term = search_term.replace('%', r'\%').replace('_', r'\_')
        search_pattern = f"%{search_term}%"

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
            # Verify category exists
            category_exists = db.query(ForumCategory).filter(
                ForumCategory.id == category_id,
                ForumCategory.is_visible == True
            ).first()
            if not category_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Kategori bulunamadi"
                )
            query = query.filter(ForumTopic.category_id == category_id)

        if author_id:
            # Verify author exists
            author_exists = db.query(User).filter(User.id == author_id).first()
            if not author_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Kullanici bulunamadi"
                )
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

        # Sorting with improved relevance
        if sort == "relevance":
            # Improved relevance scoring:
            # - Exact title match: 4 points
            # - Title contains: 2 points
            # - Content contains: 1 point
            # - Pinned topics get bonus
            relevance_score = case(
                (ForumTopic.title.ilike(f"%{search_term}%"), 2),
                else_=1
            ) + case(
                (ForumTopic.is_pinned == True, 1),
                else_=0
            )
            query = query.order_by(desc(relevance_score), desc(ForumTopic.created_at))
        elif sort == "newest":
            query = query.order_by(desc(ForumTopic.created_at))
        elif sort == "oldest":
            query = query.order_by(asc(ForumTopic.created_at))
        elif sort == "popular":
            query = query.order_by(
                desc(ForumTopic.view_count),
                desc(func.coalesce(reply_count_subq.c.reply_count, 0))
            )
        elif sort == "most_replies":
            query = query.order_by(
                desc(func.coalesce(reply_count_subq.c.reply_count, 0)),
                desc(ForumTopic.created_at)
            )

        # Get total count (without pagination) - optimized count query
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

        # Build response with enhanced data
        topics = []
        for row in results:
            # SQLAlchemy Row objects need special handling
            if hasattr(row, 'ForumTopic'):
                topic = row.ForumTopic
                reply_count = getattr(row, 'reply_count', 0) or 0
            elif hasattr(row, '__getitem__'):
                topic = row[0]
                reply_count = row[1] if len(row) > 1 else 0
            else:
                topic = row
                reply_count = 0

            # Generate content preview with search highlight context
            content_preview = None
            if topic.content:
                # Find the search term position and extract context
                content_lower = topic.content.lower()
                search_lower = search_term.lower()
                pos = content_lower.find(search_lower)

                if pos >= 0:
                    # Extract context around the match
                    start = max(0, pos - 50)
                    end = min(len(topic.content), pos + len(search_term) + 150)
                    content_preview = ("..." if start > 0 else "") + topic.content[start:end] + ("..." if end < len(topic.content) else "")
                else:
                    # No match in content, use beginning
                    content_preview = topic.content[:200] + ("..." if len(topic.content) > 200 else "")

            topics.append({
                "id": topic.id,
                "title": topic.title,
                "slug": topic.slug,
                "content_preview": content_preview,
                "category": {
                    "id": topic.category.id,
                    "name": topic.category.name,
                    "slug": topic.category.slug,
                    "icon": topic.category.icon,
                    "color": topic.category.color
                } if topic.category else None,
                "author": format_author_info(topic.author),
                "view_count": topic.view_count or 0,
                "reply_count": reply_count,
                "likes": getattr(topic, 'likes', 0) or 0,
                "is_pinned": topic.is_pinned,
                "is_locked": topic.is_locked,
                "is_solved": getattr(topic, 'is_solved', False),
                "is_edited": topic.edited_at is not None if hasattr(topic, 'edited_at') else False,
                "created_at": format_datetime_utc(topic.created_at),
                "updated_at": format_datetime_utc(topic.updated_at) if hasattr(topic, 'updated_at') and topic.updated_at else None
            })

        return create_paginated_response(
            items=topics,
            total=total,
            page=page,
            limit=limit,
            item_key="topics"
        ) | {
            "query": q,
            "filters": {
                "category_id": category_id,
                "author_id": author_id,
                "date_from": date_from,
                "date_to": date_to,
                "sort": sort
            }
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Arama sirasinda bir hata olustu. Lutfen tekrar deneyin."
        )
    except Exception as e:
        logger.error(f"Unexpected error in search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Beklenmeyen bir hata olustu. Lutfen tekrar deneyin."
        )


@router.get("/trending")
async def get_trending_topics(
    hours: int = Query(24, ge=1, le=168, description="Trend hesaplama suresi (saat, 1-168)"),
    limit: int = Query(10, ge=5, le=50, description="Sonuc sayisi"),
    db: Session = Depends(get_db)
):
    """
    Trend konulari getir - Improved hot/trending algorithm

    Algoritma:
    - Son X saatteki yanit sayisi (agirlik: 2.0)
    - Goruntulenme sayisi (agirlik: 0.1)
    - Zaman bazli azalma (logaritmik)
    - Guncellik bonusu

    Parametreler:
    - hours: Trend hesaplama suresi (varsayilan: 24 saat, max: 168 saat / 1 hafta)
    - limit: Dondurulecek konu sayisi (5-50)
    """
    cache_key = f"forum:trending:{hours}:{limit}"

    # Cache kontrol
    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            logger.debug(f"Trending cache hit: {cache_key}")
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Cache read error: {e}")

    try:
        # Zaman siniri
        time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Reply counts subquery for time window
        recent_reply_count = db.query(
            ForumReply.topic_id,
            func.count(ForumReply.id).label('recent_replies')
        ).filter(
            ForumReply.is_active == True,
            ForumReply.created_at >= time_threshold
        ).group_by(ForumReply.topic_id).subquery()

        # Total reply counts
        total_reply_count = db.query(
            ForumReply.topic_id,
            func.count(ForumReply.id).label('total_replies')
        ).filter(ForumReply.is_active == True).group_by(ForumReply.topic_id).subquery()

        # Query for trending topics with hot score calculation
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
                ForumTopic.created_at >= time_threshold,
                recent_reply_count.c.recent_replies > 0
            )
        ).order_by(
            # Improved ordering: prioritize recent activity
            desc(func.coalesce(recent_reply_count.c.recent_replies, 0) * 2 +
                 func.coalesce(ForumTopic.view_count, 0) * 0.01),
            desc(ForumTopic.created_at)
        ).limit(limit * 2)  # Get more for post-processing

        results = query.all()

        # Calculate hot scores and sort
        scored_topics = []
        for topic, recent_replies, total_replies in results:
            hot_score = calculate_hot_score(
                view_count=topic.view_count or 0,
                reply_count=total_replies,
                created_at=topic.created_at,
                recent_replies=recent_replies
            )
            scored_topics.append((topic, recent_replies, total_replies, hot_score))

        # Sort by hot score and take top N
        scored_topics.sort(key=lambda x: x[3], reverse=True)
        scored_topics = scored_topics[:limit]

        topics = []
        for topic, recent_replies, total_replies, hot_score in scored_topics:
            topics.append({
                "id": topic.id,
                "title": topic.title,
                "slug": topic.slug,
                "content_preview": (topic.content[:150] + "...") if topic.content and len(topic.content) > 150 else topic.content,
                "category": {
                    "id": topic.category.id,
                    "name": topic.category.name,
                    "slug": topic.category.slug,
                    "icon": topic.category.icon,
                    "color": topic.category.color
                } if topic.category else None,
                "author": format_author_info(topic.author),
                "view_count": topic.view_count or 0,
                "reply_count": total_replies,
                "recent_replies": recent_replies,
                "hot_score": round(hot_score, 2),
                "likes": getattr(topic, 'likes', 0) or 0,
                "is_pinned": topic.is_pinned,
                "is_locked": topic.is_locked,
                "is_solved": getattr(topic, 'is_solved', False),
                "created_at": format_datetime_utc(topic.created_at)
            })

        response = {
            "success": True,
            "topics": topics,
            "meta": {
                "hours": hours,
                "algorithm": "hot_score_v2",
                "cached_at": format_datetime_utc(datetime.now(timezone.utc))
            }
        }

        # Cache'e kaydet
        try:
            await redis_manager.set(cache_key, json.dumps(response), expire=CACHE_TTL_TRENDING)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

        return response

    except SQLAlchemyError as e:
        logger.error(f"Database error in trending: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trend konulari yuklenirken bir hata olustu"
        )
    except Exception as e:
        logger.error(f"Unexpected error in trending: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Beklenmeyen bir hata olustu"
        )


# ============ Category Endpoints ============

@router.get("/categories")
async def get_categories(
    include_empty: bool = Query(True, description="Bos kategorileri dahil et"),
    db: Session = Depends(get_db)
):
    """
    Aktif kategorileri getir - Redis cache ile

    Sayim Bilgileri:
    - topic_count: Kategorideki aktif konu sayisi
    - reply_count: Kategorideki toplam yanit sayisi
    - post_count: topic_count + reply_count
    - last_activity: Kategorideki son aktivite tarihi
    """
    cache_key = f"forum:categories:{include_empty}"

    # Cache kontrol
    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            logger.debug("Categories cache hit")
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Cache read error: {e}")

    try:
        # Tek sorguda topic ve reply count'lari al (N+1 sorunu cozumu)
        # Sadece aktif konulari say
        topic_counts = db.query(
            ForumTopic.category_id,
            func.count(ForumTopic.id).label('topic_count'),
            func.max(ForumTopic.created_at).label('last_topic')
        ).filter(
            ForumTopic.is_active == True
        ).group_by(ForumTopic.category_id).subquery()

        # Reply count subquery - sadece aktif yanitlar
        reply_counts = db.query(
            ForumTopic.category_id,
            func.count(ForumReply.id).label('reply_count'),
            func.max(ForumReply.created_at).label('last_reply')
        ).join(
            ForumReply, ForumReply.topic_id == ForumTopic.id
        ).filter(
            ForumTopic.is_active == True,
            ForumReply.is_active == True
        ).group_by(ForumTopic.category_id).subquery()

        # Main query
        query = db.query(
            ForumCategory,
            func.coalesce(topic_counts.c.topic_count, 0).label('topic_count'),
            func.coalesce(reply_counts.c.reply_count, 0).label('reply_count'),
            topic_counts.c.last_topic,
            reply_counts.c.last_reply
        ).outerjoin(
            topic_counts, topic_counts.c.category_id == ForumCategory.id
        ).outerjoin(
            reply_counts, reply_counts.c.category_id == ForumCategory.id
        ).filter(
            ForumCategory.is_visible == True
        ).order_by(ForumCategory.display_order, ForumCategory.name)

        # Filter empty categories if requested
        if not include_empty:
            query = query.having(func.coalesce(topic_counts.c.topic_count, 0) > 0)

        categories = query.all()

        result = []
        for cat, topic_count, reply_count, last_topic, last_reply in categories:
            # Post count = topic count + reply count
            post_count = (topic_count or 0) + (reply_count or 0)

            # Determine last activity
            last_activity = None
            if last_topic and last_reply:
                last_activity = max(last_topic, last_reply)
            elif last_topic:
                last_activity = last_topic
            elif last_reply:
                last_activity = last_reply

            result.append({
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "description": cat.description,
                "icon": cat.icon or "📁",
                "color": cat.color or "#ff6b00",
                "game_slug": cat.game_slug,
                "parent_id": cat.parent_id,
                "display_order": cat.display_order or 0,
                "topic_count": topic_count or 0,
                "post_count": post_count,
                "reply_count": reply_count or 0,
                "last_activity": format_datetime_utc(last_activity)
            })

        response = {
            "success": True,
            "categories": result,
            "total": len(result)
        }

        # Cache'e kaydet
        try:
            await redis_manager.set(cache_key, json.dumps(response), expire=CACHE_TTL_CATEGORIES)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

        return response

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kategoriler yuklenirken bir hata olustu"
        )


@router.get("/categories/{slug}")
async def get_category(slug: str, db: Session = Depends(get_db)):
    """
    Kategori detayi getir

    Icerir:
    - Kategori bilgileri
    - Konu ve yanit sayilari
    - Son aktivite
    - En populer konular (top 5)
    """
    try:
        # Get category with counts in single query
        topic_count_subq = db.query(
            func.count(ForumTopic.id)
        ).filter(
            ForumTopic.category_id == ForumCategory.id,
            ForumTopic.is_active == True
        ).correlate(ForumCategory).scalar_subquery()

        reply_count_subq = db.query(
            func.count(ForumReply.id)
        ).join(
            ForumTopic, ForumReply.topic_id == ForumTopic.id
        ).filter(
            ForumTopic.category_id == ForumCategory.id,
            ForumTopic.is_active == True,
            ForumReply.is_active == True
        ).correlate(ForumCategory).scalar_subquery()

        category = db.query(
            ForumCategory,
            topic_count_subq.label('topic_count'),
            reply_count_subq.label('reply_count')
        ).filter(
            ForumCategory.slug == slug,
            ForumCategory.is_visible == True
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kategori bulunamadi"
            )

        cat, topic_count, reply_count = category

        # Get recent topics for this category
        recent_topics = db.query(ForumTopic).options(
            joinedload(ForumTopic.author)
        ).filter(
            ForumTopic.category_id == cat.id,
            ForumTopic.is_active == True
        ).order_by(desc(ForumTopic.created_at)).limit(5).all()

        # Get reply counts for recent topics
        recent_topic_ids = [t.id for t in recent_topics]
        reply_counts_map = {}
        if recent_topic_ids:
            counts = db.query(
                ForumReply.topic_id,
                func.count(ForumReply.id)
            ).filter(
                ForumReply.topic_id.in_(recent_topic_ids),
                ForumReply.is_active == True
            ).group_by(ForumReply.topic_id).all()
            reply_counts_map = {tid: cnt for tid, cnt in counts}

        return {
            "success": True,
            "category": {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "description": cat.description,
                "icon": cat.icon or "📁",
                "color": cat.color or "#ff6b00",
                "game_slug": cat.game_slug,
                "display_order": cat.display_order or 0,
                "topic_count": topic_count or 0,
                "reply_count": reply_count or 0,
                "post_count": (topic_count or 0) + (reply_count or 0)
            },
            "recent_topics": [
                {
                    "id": t.id,
                    "title": t.title,
                    "slug": t.slug,
                    "author": format_author_info(t.author),
                    "reply_count": reply_counts_map.get(t.id, 0),
                    "view_count": t.view_count or 0,
                    "created_at": format_datetime_utc(t.created_at)
                }
                for t in recent_topics
            ]
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kategori bilgileri yuklenirken bir hata olustu"
        )


@router.get("/categories/{slug_or_id}/topics")
async def get_category_topics(
    slug_or_id: str,
    page: int = Query(1, ge=1, le=1000),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE),
    sort: str = Query("newest", pattern="^(newest|oldest|popular|most_replies|last_reply)$"),
    has_replies: Optional[bool] = Query(None, description="Yaniti olan/olmayan konulari filtrele"),
    is_solved: Optional[bool] = Query(None, description="Cozulmus/cozulmemis konulari filtrele"),
    is_pinned: Optional[bool] = Query(None, description="Sabitlenmis konulari filtrele"),
    date_from: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    author_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db)
):
    """
    Kategorinin konularini getir - ID veya slug ile erisim

    Parametreler:
    - slug_or_id: Kategori slug veya ID
    - page: Sayfa numarasi
    - limit: Sayfa basi sonuc sayisi
    - sort: Siralama (newest, oldest, popular, most_replies, last_reply)
    - has_replies: Sadece yaniti olan/olmayan konulari getir
    - is_solved: Cozulmus/cozulmemis konulari filtrele
    - is_pinned: Sabitlenmis konulari filtrele
    - date_from: Baslangic tarihi (YYYY-MM-DD)
    - date_to: Bitis tarihi (YYYY-MM-DD)
    - author_id: Belirli bir yazarin konulari
    """
    # Validate pagination
    page, limit = validate_pagination(page, limit)

    try:
        # Try as ID first if numeric
        category = None
        if slug_or_id.isdigit():
            category = db.query(ForumCategory).filter(
                ForumCategory.id == int(slug_or_id),
                ForumCategory.is_visible == True
            ).first()

        # If not found by ID, try slug
        if not category:
            category = db.query(ForumCategory).filter(
                ForumCategory.slug == slug_or_id,
                ForumCategory.is_visible == True
            ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kategori bulunamadi"
            )

        # Reply counts subquery - needed for has_replies filter and sorting
        reply_count_subq = db.query(
            ForumReply.topic_id,
            func.count(ForumReply.id).label('reply_count'),
            func.max(ForumReply.created_at).label('last_reply_at')
        ).filter(ForumReply.is_active == True).group_by(ForumReply.topic_id).subquery()

        query = db.query(
            ForumTopic,
            func.coalesce(reply_count_subq.c.reply_count, 0).label('reply_count'),
            reply_count_subq.c.last_reply_at
        ).options(
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

        if is_solved is not None:
            if hasattr(ForumTopic, 'is_solved'):
                query = query.filter(ForumTopic.is_solved == is_solved)

        if is_pinned is not None:
            query = query.filter(ForumTopic.is_pinned == is_pinned)

        # Date filters
        from_date = parse_date(date_from)
        to_date = parse_date(date_to)

        if from_date and to_date and from_date > to_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Baslangic tarihi bitis tarihinden sonra olamaz"
            )

        if from_date:
            query = query.filter(ForumTopic.created_at >= from_date)
        if to_date:
            # Include the entire end date
            query = query.filter(ForumTopic.created_at < to_date + timedelta(days=1))

        # Author filter
        if author_id:
            query = query.filter(ForumTopic.author_id == author_id)

        # Sorting - pinned topics always first unless explicitly filtered
        base_order = [] if is_pinned is not None else [desc(ForumTopic.is_pinned)]

        if sort == "oldest":
            query = query.order_by(*base_order, asc(ForumTopic.created_at))
        elif sort == "popular":
            query = query.order_by(*base_order, desc(ForumTopic.view_count), desc(ForumTopic.created_at))
        elif sort == "most_replies":
            query = query.order_by(*base_order, desc(func.coalesce(reply_count_subq.c.reply_count, 0)), desc(ForumTopic.created_at))
        elif sort == "last_reply":
            query = query.order_by(*base_order, desc(func.coalesce(reply_count_subq.c.last_reply_at, ForumTopic.created_at)))
        else:  # newest (default)
            query = query.order_by(*base_order, desc(ForumTopic.created_at))

        # Get total count - optimized
        total = db.query(func.count(ForumTopic.id)).filter(
            ForumTopic.category_id == category.id,
            ForumTopic.is_active == True
        ).scalar() or 0

        # Execute paginated query
        results = query.offset((page - 1) * limit).limit(limit).all()

        # Build response
        topics = []
        for row in results:
            topic = row[0]
            reply_count = row[1]
            last_reply_at = row[2]

            topics.append({
                "id": topic.id,
                "title": topic.title,
                "slug": topic.slug,
                "content_preview": (topic.content[:150] + "...") if topic.content and len(topic.content) > 150 else topic.content,
                "author": format_author_info(topic.author),
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug,
                    "icon": category.icon,
                    "color": category.color
                },
                "is_pinned": topic.is_pinned,
                "is_locked": topic.is_locked,
                "is_solved": getattr(topic, 'is_solved', False),
                "is_edited": topic.edited_at is not None if hasattr(topic, 'edited_at') else False,
                "view_count": topic.view_count or 0,
                "reply_count": reply_count,
                "likes": getattr(topic, 'likes', 0) or 0,
                "created_at": format_datetime_utc(topic.created_at),
                "last_reply_at": format_datetime_utc(last_reply_at) if last_reply_at else None
            })

        # Category info with accurate counts
        category_topic_count = db.query(func.count(ForumTopic.id)).filter(
            ForumTopic.category_id == category.id,
            ForumTopic.is_active == True
        ).scalar() or 0

        category_reply_count = db.query(func.count(ForumReply.id)).join(
            ForumTopic, ForumReply.topic_id == ForumTopic.id
        ).filter(
            ForumTopic.category_id == category.id,
            ForumTopic.is_active == True,
            ForumReply.is_active == True
        ).scalar() or 0

        return create_paginated_response(
            items=topics,
            total=total,
            page=page,
            limit=limit,
            item_key="topics"
        ) | {
            "category": {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "description": category.description,
                "icon": category.icon or "📁",
                "color": category.color or "#ff6b00",
                "game_slug": category.game_slug,
                "topic_count": category_topic_count,
                "reply_count": category_reply_count,
                "post_count": category_topic_count + category_reply_count
            },
            "filters": {
                "sort": sort,
                "has_replies": has_replies,
                "is_solved": is_solved,
                "is_pinned": is_pinned,
                "date_from": date_from,
                "date_to": date_to,
                "author_id": author_id
            }
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_category_topics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Konular yuklenirken bir hata olustu"
        )


# ============ Topic Endpoints ============

@router.get("/topics")
async def get_topics(
    page: int = Query(1, ge=1, le=1000),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE),
    sort: str = Query("newest", pattern="^(newest|oldest|popular|most_replies)$"),
    category_id: Optional[int] = Query(None, gt=0, description="Kategori filtresi"),
    db: Session = Depends(get_db)
):
    """
    Tum konulari getir - N+1 sorunu cozulmus ve Redis cached

    Parametreler:
    - page: Sayfa numarasi (1-1000)
    - limit: Sayfa basi sonuc sayisi (5-100)
    - sort: Siralama (newest, oldest, popular, most_replies)
    - category_id: Kategori filtresi (opsiyonel)
    """
    # Validate pagination
    page, limit = validate_pagination(page, limit)

    cache_key = f"forum:topics:{page}:{limit}:{sort}:{category_id or 'all'}"

    # Cache kontrol
    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            logger.debug(f"Topics cache hit: {cache_key}")
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Cache read error: {e}")

    try:
        # Reply count subquery - N+1 sorunu cozumu
        reply_count_subq = db.query(
            ForumReply.topic_id,
            func.count(ForumReply.id).label('reply_count')
        ).filter(ForumReply.is_active == True).group_by(ForumReply.topic_id).subquery()

        query = db.query(ForumTopic).options(
            joinedload(ForumTopic.author),
            joinedload(ForumTopic.category)
        ).outerjoin(
            reply_count_subq, ForumTopic.id == reply_count_subq.c.topic_id
        ).add_columns(
            func.coalesce(reply_count_subq.c.reply_count, 0).label('reply_count')
        ).filter(
            ForumTopic.is_active == True
        )

        # Category filter
        if category_id:
            query = query.filter(ForumTopic.category_id == category_id)

        # Sorting - pinned always first
        if sort == "oldest":
            query = query.order_by(desc(ForumTopic.is_pinned), asc(ForumTopic.created_at))
        elif sort == "popular":
            query = query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.view_count))
        elif sort == "most_replies":
            query = query.order_by(desc(ForumTopic.is_pinned), desc(func.coalesce(reply_count_subq.c.reply_count, 0)))
        else:  # newest (default)
            query = query.order_by(desc(ForumTopic.is_pinned), desc(ForumTopic.created_at))

        # Optimized count query
        count_query = db.query(func.count(ForumTopic.id)).filter(ForumTopic.is_active == True)
        if category_id:
            count_query = count_query.filter(ForumTopic.category_id == category_id)
        total = count_query.scalar() or 0

        results = query.offset((page - 1) * limit).limit(limit).all()

        topics = []
        for row in results:
            # SQLAlchemy Row objects need special handling
            if hasattr(row, 'ForumTopic'):
                topic = row.ForumTopic
                reply_count = getattr(row, 'reply_count', 0) or 0
            elif hasattr(row, '__getitem__'):
                topic = row[0]
                reply_count = row[1] if len(row) > 1 else 0
            else:
                topic = row
                reply_count = 0

            topics.append({
                "id": topic.id,
                "title": topic.title,
                "slug": topic.slug,
                "content_preview": (topic.content[:150] + "...") if topic.content and len(topic.content) > 150 else topic.content,
                "category": {
                    "id": topic.category.id,
                    "name": topic.category.name,
                    "slug": topic.category.slug,
                    "icon": topic.category.icon,
                    "color": topic.category.color
                } if topic.category else None,
                "author": format_author_info(topic.author),
                "is_pinned": topic.is_pinned,
                "is_locked": topic.is_locked,
                "is_solved": getattr(topic, 'is_solved', False),
                "is_edited": topic.edited_at is not None if hasattr(topic, 'edited_at') else False,
                "reply_count": reply_count,
                "view_count": topic.view_count or 0,
                "likes": getattr(topic, 'likes', 0) or 0,
                "created_at": format_datetime_utc(topic.created_at)
            })

        response = create_paginated_response(
            items=topics,
            total=total,
            page=page,
            limit=limit,
            item_key="topics"
        )

        # Cache'e kaydet
        try:
            await redis_manager.set(cache_key, json.dumps(response), expire=CACHE_TTL_TOPICS)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

        return response

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_topics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Konular yuklenirken bir hata olustu"
        )


@router.get("/topics/popular")
async def get_popular_topics(
    limit: int = Query(10, ge=5, le=50, description="Sonuc sayisi"),
    days: int = Query(30, ge=1, le=365, description="Zaman araligi (gun)"),
    db: Session = Depends(get_db)
):
    """
    Populer konulari getir - Redis cache ile

    Siralama: Goruntulenme sayisi + yanit sayisi agirligi

    Parametreler:
    - limit: Dondurulecek konu sayisi (5-50)
    - days: Zaman araligi (son X gun, 1-365)
    """
    cache_key = f"forum:popular:{limit}:{days}"

    # Cache kontrol
    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            logger.debug(f"Popular cache hit: {cache_key}")
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Cache read error: {e}")

    try:
        # Zaman siniri
        time_threshold = datetime.now(timezone.utc) - timedelta(days=days)

        # Reply count subquery
        reply_count_subq = db.query(
            ForumReply.topic_id,
            func.count(ForumReply.id).label('reply_count')
        ).filter(ForumReply.is_active == True).group_by(ForumReply.topic_id).subquery()

        # Populer konulari getir (view_count + reply_count agirligi ile)
        topics = db.query(
            ForumTopic,
            func.coalesce(reply_count_subq.c.reply_count, 0).label('reply_count')
        ).options(
            joinedload(ForumTopic.author),
            joinedload(ForumTopic.category)
        ).outerjoin(
            reply_count_subq, ForumTopic.id == reply_count_subq.c.topic_id
        ).filter(
            ForumTopic.is_active == True,
            ForumTopic.created_at >= time_threshold
        ).order_by(
            desc(func.coalesce(ForumTopic.view_count, 0) +
                 func.coalesce(reply_count_subq.c.reply_count, 0) * 10)
        ).limit(limit).all()

        result = []
        for topic, reply_count in topics:
            result.append({
                "id": topic.id,
                "title": topic.title,
                "slug": topic.slug,
                "content_preview": (topic.content[:100] + "...") if topic.content and len(topic.content) > 100 else topic.content,
                "category": {
                    "id": topic.category.id,
                    "name": topic.category.name,
                    "slug": topic.category.slug,
                    "icon": topic.category.icon,
                    "color": topic.category.color
                } if topic.category else None,
                "author": format_author_info(topic.author),
                "view_count": topic.view_count or 0,
                "reply_count": reply_count,
                "likes": getattr(topic, 'likes', 0) or 0,
                "is_pinned": topic.is_pinned,
                "is_solved": getattr(topic, 'is_solved', False),
                "created_at": format_datetime_utc(topic.created_at)
            })

        response = {
            "success": True,
            "topics": result,
            "meta": {
                "days": days,
                "limit": limit
            }
        }

        # Cache'e kaydet
        try:
            await redis_manager.set(cache_key, json.dumps(response), expire=CACHE_TTL_POPULAR)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

        return response

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_popular_topics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Populer konular yuklenirken bir hata olustu"
        )


@router.get("/topics/{slug_or_id}")
async def get_topic(
    slug_or_id: str,
    include_replies: bool = Query(True, description="Yanitlari dahil et"),
    reply_page: int = Query(1, ge=1, le=1000, description="Yanit sayfasi"),
    reply_limit: int = Query(DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Konu detayi - ID veya slug ile erisim

    Parametreler:
    - slug_or_id: Konu slug veya ID
    - include_replies: Yanitlari dahil et (varsayilan: True)
    - reply_page: Yanit sayfasi (sayfalama icin)
    - reply_limit: Sayfa basi yanit sayisi
    """
    try:
        # Try as ID first if numeric
        topic = None
        if slug_or_id.isdigit():
            topic = db.query(ForumTopic).options(
                joinedload(ForumTopic.author),
                joinedload(ForumTopic.category)
            ).filter(
                ForumTopic.id == int(slug_or_id),
                ForumTopic.is_active == True
            ).first()

        # If not found by ID, try slug
        if not topic:
            topic = db.query(ForumTopic).options(
                joinedload(ForumTopic.author),
                joinedload(ForumTopic.category)
            ).filter(
                ForumTopic.slug == slug_or_id,
                ForumTopic.is_active == True
            ).first()

        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konu bulunamadi"
            )

        # Goruntülenme sayisini atomik olarak artir (race condition onleme)
        try:
            db.query(ForumTopic).filter(ForumTopic.id == topic.id).update(
                {ForumTopic.view_count: func.coalesce(ForumTopic.view_count, 0) + 1},
                synchronize_session=False
            )
            db.commit()
            topic.view_count = (topic.view_count or 0) + 1
        except Exception as e:
            logger.warning(f"View count update failed: {e}")
            db.rollback()

        # Get accurate reply count
        reply_count = db.query(func.count(ForumReply.id)).filter(
            ForumReply.topic_id == topic.id,
            ForumReply.is_active == True
        ).scalar() or 0

        # Get topic tags
        topic_tags = []
        try:
            topic_tags = get_topic_tags(db, topic.id)
        except Exception as e:
            logger.warning(f"Failed to get topic tags: {e}")

        # Build topic response
        topic_data = {
            "id": topic.id,
            "title": topic.title,
            "slug": topic.slug,
            "content": topic.content,
            "category": {
                "id": topic.category.id,
                "name": topic.category.name,
                "slug": topic.category.slug,
                "icon": topic.category.icon,
                "color": topic.category.color
            } if topic.category else None,
            # Legacy camelCase for frontend compatibility
            "categoryId": topic.category.id if topic.category else None,
            "categoryName": topic.category.name if topic.category else None,
            "categorySlug": topic.category.slug if topic.category else None,
            "author": format_author_info(topic.author, include_extended=True),
            # Legacy fields for frontend compatibility
            "authorId": topic.author_id,
            "authorAvatar": format_avatar_url(topic.author.avatar) if topic.author else None,
            "authorLevel": getattr(topic.author, 'level', 1) if topic.author else 1,
            "authorRole": topic.author.role.value if topic.author and hasattr(topic.author.role, 'value') else str(topic.author.role) if topic.author and topic.author.role else None,
            "isPinned": topic.is_pinned,
            "isLocked": topic.is_locked,
            "isSolved": getattr(topic, 'is_solved', False),
            "isEdited": topic.edited_at is not None if hasattr(topic, 'edited_at') else False,
            "views": topic.view_count,
            "view_count": topic.view_count,
            "likes": getattr(topic, 'likes', 0) or 0,
            "hasLiked": db.execute(text("SELECT 1 FROM forum_likes WHERE user_id = :uid AND content_type = 'topic' AND content_id = :cid"), {"uid": current_user.id, "cid": topic.id}).fetchone() is not None if current_user else False,
            "replyCount": reply_count,
            "reply_count": reply_count,
            "tags": topic_tags,
            "created": format_datetime_turkish(topic.created_at),
            "created_at": format_datetime_utc(topic.created_at),
            "edited_at": format_datetime_utc(topic.edited_at) if hasattr(topic, 'edited_at') and topic.edited_at else None
        }

        # Get replies if requested
        replies_data = []
        best_answer = None
        reply_pagination = None

        if include_replies:
            # Validate pagination
            reply_page, reply_limit = validate_pagination(reply_page, reply_limit)

            # Get paginated replies
            # Build order clauses with proper hasattr checks for optional model columns
            reply_order_clauses = []
            if hasattr(ForumReply, 'is_best_answer'):
                reply_order_clauses.append(desc(ForumReply.is_best_answer))
            reply_order_clauses.append(asc(ForumReply.created_at))

            replies_query = db.query(ForumReply).options(
                joinedload(ForumReply.author)
            ).filter(
                ForumReply.topic_id == topic.id,
                ForumReply.is_active == True
            ).order_by(*reply_order_clauses)

            total_replies = reply_count
            replies = replies_query.offset((reply_page - 1) * reply_limit).limit(reply_limit).all()

            for reply in replies:
                is_best = getattr(reply, 'is_best_answer', False)
                reply_data = {
                    "id": reply.id,
                    "content": reply.content,
                    "author": format_author_info(reply.author, include_extended=True),
                    # Legacy fields
                    "authorId": reply.user_id,
                    "authorAvatar": format_avatar_url(reply.author.avatar) if reply.author else None,
                    "authorLevel": getattr(reply.author, 'level', 1) if reply.author else 1,
                    "authorRole": reply.author.role.value if reply.author and hasattr(reply.author.role, 'value') else str(reply.author.role) if reply.author and reply.author.role else None,
                    "likes": getattr(reply, 'likes', 0) or 0,
                    "hasLiked": db.execute(text("SELECT 1 FROM forum_likes WHERE user_id = :uid AND content_type = 'reply' AND content_id = :cid"), {"uid": current_user.id, "cid": reply.id}).fetchone() is not None if current_user else False,
                    "isBestAnswer": is_best,
                    "is_best_answer": is_best,
                    "isEdited": reply.updated_at is not None and reply.updated_at != reply.created_at if hasattr(reply, 'updated_at') else False,
                    "parent_reply_id": getattr(reply, 'parent_reply_id', None),
                    "created": format_datetime_turkish(reply.created_at),
                    "created_at": format_datetime_utc(reply.created_at),
                    "edited_at": format_datetime_utc(reply.edited_at) if hasattr(reply, 'edited_at') and reply.edited_at else None
                }
                replies_data.append(reply_data)

                # Track best answer
                if is_best:
                    best_answer = reply_data

            reply_pagination = {
                "total": total_replies,
                "page": reply_page,
                "limit": reply_limit,
                "pages": (total_replies + reply_limit - 1) // reply_limit if total_replies > 0 else 0,
                "has_next": reply_page < ((total_replies + reply_limit - 1) // reply_limit if total_replies > 0 else 0),
                "has_prev": reply_page > 1
            }

        return {
            "success": True,
            "topic": topic_data,
            "replies": replies_data,
            "reply_pagination": reply_pagination,
            "bestAnswer": best_answer,
            "best_answer": best_answer
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_topic: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Konu yuklenirken bir hata olustu"
        )


@router.post("/topics", status_code=status.HTTP_201_CREATED)
async def create_topic(
    data: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_steam)
):
    """
    Yeni konu olustur

    Gereksinimler:
    - Steam hesabi bagli olmali
    - Rate limit: Saatte max 5 konu
    - Baslik: 5-200 karakter
    - Icerik: 20-50000 karakter
    - Etiketler: Max 5 adet

    Oduller:
    - +5 Reputation
    - Coin odulu (gunluk limite bagli)
    """
    logger.info(f"Topic creation attempt by user {current_user.id}")

    try:
        # Rate limit check with remaining time
        rate_limited, remaining_seconds = await check_forum_rate_limit(current_user.id, "topic")
        if rate_limited:
            minutes_remaining = (remaining_seconds // 60) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Cok fazla konu olusturdunuz. Saatte en fazla {TOPIC_RATE_LIMIT} konu olusturabilirsiniz. "
                       f"Yaklasik {minutes_remaining} dakika sonra tekrar deneyebilirsiniz."
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
            auto_filter=False  # Reddet modu
        )

        # Kullanici banli mi?
        if moderation_result.get("banned"):
            logger.warning(f"Banned user {current_user.id} attempted to create topic")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=moderation_result.get("message", "Forum erismisiniz askiya alindi")
            )

        # Icerik uygun degil mi?
        if not moderation_result.get("allowed"):
            logger.info(f"Topic content rejected for user {current_user.id}: {moderation_result.get('reason', 'unknown')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=moderation_result.get("message", "Icerik kurallara uygun degil")
            )
        # ===== END CONTENT MODERATION =====

        # Kategori kontrolu
        category = db.query(ForumCategory).filter(
            ForumCategory.id == data.category_id,
            ForumCategory.is_visible == True
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gecersiz veya gorunur olmayan kategori secildi"
            )

        # XSS Protection - Sanitize title and content
        sanitized_title = sanitize_title(data.title.strip())
        sanitized_content = sanitize_forum_content(data.content.strip())

        # Post-sanitization length validation
        if len(sanitized_title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Baslik cok uzun (max 200 karakter)"
            )
        if len(sanitized_content) > 50000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Icerik cok uzun (max 50000 karakter)"
            )

        # Generate unique slug
        slug = generate_slug(sanitized_title)
        slug = ensure_unique_slug(db, slug)

        # Create topic
        topic = ForumTopic(
            title=sanitized_title,
            slug=slug,
            category_id=data.category_id,
            author_id=current_user.id,
            content=sanitized_content,
            is_active=True,
            view_count=0
        )

        db.add(topic)
        db.commit()
        db.refresh(topic)

        logger.info(f"Topic {topic.id} created by user {current_user.id}")

        # Link tags to topic (if provided)
        linked_tags = []
        if data.tags:
            try:
                ensure_forum_tables(db)
                link_tags_to_topic(db, topic.id, data.tags)
                db.commit()
                linked_tags = get_topic_tags(db, topic.id)
            except Exception as e:
                logger.warning(f"Tag linking error for topic {topic.id}: {e}")

        # Process @mentions in content
        mentions_processed = 0
        try:
            mentions_processed = process_mentions(db, data.content, "topic", topic.id, current_user.id, topic.slug)
            if mentions_processed:
                db.commit()
        except Exception as e:
            logger.warning(f"Mention processing error for topic {topic.id}: {e}")

        # Invalidate caches
        await invalidate_forum_cache()
        await invalidate_topic_cache(category_id=category.id)

        # Reputation reward (+5 for topic creation)
        reputation_earned = 0
        try:
            current_user.reputation = (current_user.reputation or 0) + 5
            reputation_earned = 5
            db.commit()
        except Exception as e:
            logger.warning(f"Reputation update error for user {current_user.id}: {e}")

        # Badge check
        badges_earned = []
        try:
            from app.services.forum_gamification import get_forum_gamification_service
            gamification_service = get_forum_gamification_service(db)
            badges_earned = await gamification_service.check_and_award_badges(current_user.id) or []
        except Exception as e:
            logger.warning(f"Badge check error for user {current_user.id}: {e}")

        # Forum coin reward
        reward_amount = None
        try:
            from app.services.forum_rewards import get_forum_reward_service
            reward_service = get_forum_reward_service(db)
            reward_amount = reward_service.reward_topic_create(
                user_id=current_user.id,
                topic_id=topic.id
            )
        except Exception as e:
            logger.warning(f"Forum topic reward error for user {current_user.id}: {e}")

        response = {
            "success": True,
            "message": "Konu basariyla olusturuldu",
            "topic": {
                "id": topic.id,
                "title": topic.title,
                "slug": topic.slug,
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug
                },
                "tags": linked_tags,
                "created_at": format_datetime_utc(topic.created_at)
            },
            "rewards": {
                "reputation": reputation_earned,
                "coins": reward_amount,
                "badges": badges_earned
            }
        }

        if reward_amount:
            response["reward_message"] = f"+{reward_amount} Coin kazandiniz!"

        return response

    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Database integrity error in create_topic: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Konu olusturulurken bir cakisma olustu. Lutfen tekrar deneyin."
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_topic: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Konu olusturulurken bir hata olustu. Lutfen tekrar deneyin."
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_topic: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Beklenmeyen bir hata olustu. Lutfen tekrar deneyin."
        )


# ============ Reply Endpoints ============

@router.get("/topics/{slug_or_id}/replies")
async def get_topic_replies(
    slug_or_id: str,
    page: int = Query(1, ge=1, le=1000),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE),
    sort: str = Query("oldest", pattern="^(oldest|newest|best)$"),
    db: Session = Depends(get_db)
):
    """
    Konunun yanitlarini getir (sayfalama destekli)

    Parametreler:
    - slug_or_id: Konu slug veya ID
    - page: Sayfa numarasi
    - limit: Sayfa basi yanit sayisi
    - sort: Siralama (oldest, newest, best)
    """
    # Validate pagination
    page, limit = validate_pagination(page, limit)

    try:
        # Find topic by ID or slug
        if slug_or_id.isdigit():
            topic = db.query(ForumTopic).filter(
                ForumTopic.id == int(slug_or_id),
                ForumTopic.is_active == True
            ).first()
        else:
            topic = db.query(ForumTopic).filter(
                ForumTopic.slug == slug_or_id,
                ForumTopic.is_active == True
            ).first()

        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konu bulunamadi"
            )

        # Total count for pagination
        total = db.query(func.count(ForumReply.id)).filter(
            ForumReply.topic_id == topic.id,
            ForumReply.is_active == True
        ).scalar() or 0

        # Build query
        query = db.query(ForumReply).options(
            joinedload(ForumReply.author)
        ).filter(
            ForumReply.topic_id == topic.id,
            ForumReply.is_active == True
        )

        # Sorting
        if sort == "newest":
            query = query.order_by(desc(ForumReply.created_at))
        elif sort == "best":
            # Best answers first, then by likes, then by date
            # Use proper hasattr checks for optional model columns
            order_clauses = []
            if hasattr(ForumReply, 'is_best_answer'):
                order_clauses.append(desc(ForumReply.is_best_answer))
            if hasattr(ForumReply, 'likes'):
                order_clauses.append(desc(ForumReply.likes))
            order_clauses.append(asc(ForumReply.created_at))
            query = query.order_by(*order_clauses)
        else:  # oldest (default - chronological)
            query = query.order_by(asc(ForumReply.created_at))

        # Execute paginated query
        replies = query.offset((page - 1) * limit).limit(limit).all()

        replies_data = []
        for r in replies:
            replies_data.append({
                "id": r.id,
                "content": r.content,
                "author": format_author_info(r.author, include_extended=True),
                # Legacy fields
                "author_id": r.user_id,
                "author_name": r.author.username if r.author else None,
                "author_avatar": format_avatar_url(r.author.avatar) if r.author else None,
                "likes": getattr(r, 'likes', 0) or 0,
                "is_best_answer": getattr(r, 'is_best_answer', False) or False,
                "is_edited": r.updated_at is not None and r.updated_at != r.created_at if hasattr(r, 'updated_at') else False,
                "parent_reply_id": getattr(r, 'parent_reply_id', None),
                "created_at": format_datetime_utc(r.created_at),
                "edited_at": format_datetime_utc(r.edited_at) if hasattr(r, 'edited_at') and r.edited_at else None
            })

        return create_paginated_response(
            items=replies_data,
            total=total,
            page=page,
            limit=limit,
            item_key="replies"
        ) | {
            "topic_id": topic.id,
            "topic_slug": topic.slug,
            "sort": sort
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_topic_replies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yanitlar yuklenirken bir hata olustu"
        )


@router.post("/topics/{slug_or_id}/replies", status_code=status.HTTP_201_CREATED)
async def create_reply(
    slug_or_id: str,
    data: ReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_steam)
):
    """
    Konuya yanit ekle

    Gereksinimler:
    - Steam hesabi bagli olmali
    - Konu kilitli olmamali
    - Rate limit: Saatte max 20 yanit
    - Icerik: 3-20000 karakter

    Oduller:
    - +2 Reputation
    - Coin odulu (gunluk limite bagli)
    """
    logger.info(f"Reply creation attempt by user {current_user.id} on topic {slug_or_id}")

    try:
        # Rate limit check with remaining time
        rate_limited, remaining_seconds = await check_forum_rate_limit(current_user.id, "reply")
        if rate_limited:
            minutes_remaining = (remaining_seconds // 60) + 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Cok fazla yanit yazdiniz. Saatte en fazla {REPLY_RATE_LIMIT} yanit yazabilirsiniz. "
                       f"Yaklasik {minutes_remaining} dakika sonra tekrar deneyebilirsiniz."
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
            logger.warning(f"Banned user {current_user.id} attempted to reply")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=moderation_result.get("message", "Forum erismisiniz askiya alindi")
            )

        # Icerik uygun degil mi?
        if not moderation_result.get("allowed"):
            logger.info(f"Reply content rejected for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=moderation_result.get("message", "Icerik kurallara uygun degil")
            )
        # ===== END CONTENT MODERATION =====

        # Get topic with author for notification (supports both slug and ID)
        if slug_or_id.isdigit():
            topic = db.query(ForumTopic).options(
                joinedload(ForumTopic.author)
            ).filter(
                ForumTopic.id == int(slug_or_id),
                ForumTopic.is_active == True
            ).first()
        else:
            topic = db.query(ForumTopic).options(
                joinedload(ForumTopic.author)
            ).filter(
                ForumTopic.slug == slug_or_id,
                ForumTopic.is_active == True
            ).first()

        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konu bulunamadi"
            )

        if topic.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu konu kilitli, yanit yazilamaz"
            )

        # Validate parent reply if threading
        parent_reply = None
        if data.parent_reply_id:
            parent_reply = db.query(ForumReply).filter(
                ForumReply.id == data.parent_reply_id,
                ForumReply.topic_id == topic.id,
                ForumReply.is_active == True
            ).first()

            if not parent_reply:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ust yanit bulunamadi veya bu konuya ait degil"
                )

        # XSS Protection - Sanitize reply content
        sanitized_content = sanitize_forum_content(data.content.strip())

        # Create reply
        reply = ForumReply(
            topic_id=topic.id,
            user_id=current_user.id,
            content=sanitized_content,
            is_active=True
        )

        # Add parent_reply_id if threading is supported
        if hasattr(ForumReply, 'parent_reply_id') and data.parent_reply_id:
            reply.parent_reply_id = data.parent_reply_id

        db.add(reply)
        db.commit()
        db.refresh(reply)

        logger.info(f"Reply {reply.id} created by user {current_user.id} on topic {topic.id}")

        # Process @mentions in content
        mentions_processed = 0
        try:
            mentions_processed = process_mentions(db, data.content, "reply", reply.id, current_user.id, topic.slug)
            if mentions_processed:
                db.commit()
        except Exception as e:
            logger.warning(f"Mention processing error for reply {reply.id}: {e}")

        # Notify subscribers about new reply
        try:
            notify_subscribers(db, topic.id, current_user.id, topic.title, topic.slug)
            db.commit()
        except Exception as e:
            logger.warning(f"Subscriber notification error: {e}")

        # Notify topic author if different from replier
        if topic.author_id != current_user.id:
            try:
                notification = Notification(
                    user_id=topic.author_id,
                    type="forum_reply",
                    title="Konunuza yanit geldi",
                    message=f"@{current_user.username} '{topic.title[:50]}...' konunuza yanit verdi.",
                    link=f"/forum/topic/{topic.slug}",
                    is_read=False
                )
                db.add(notification)
                db.commit()
            except Exception as e:
                logger.warning(f"Author notification error: {e}")

        # Invalidate caches
        await invalidate_topic_cache(topic_id=topic.id)

        # Reputation reward (+2 for reply creation)
        reputation_earned = 0
        try:
            current_user.reputation = (current_user.reputation or 0) + 2
            reputation_earned = 2
            db.commit()
        except Exception as e:
            logger.warning(f"Reputation update error: {e}")

        # Badge check
        badges_earned = []
        try:
            from app.services.forum_gamification import get_forum_gamification_service
            gamification_service = get_forum_gamification_service(db)
            badges_earned = await gamification_service.check_and_award_badges(current_user.id) or []
        except Exception as e:
            logger.warning(f"Badge check error: {e}")

        # Forum coin reward
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
            logger.warning(f"Forum reply reward error for user {current_user.id}: {e}")

        # Broadcast new reply via WebSocket
        try:
            from app.api.websocket import broadcast_forum_new_reply
            reply_broadcast_data = {
                "id": reply.id,
                "content": reply.content,
                "author": format_author_info(current_user),
                "parent_reply_id": getattr(reply, 'parent_reply_id', None),
                "created_at": format_datetime_utc(reply.created_at)
            }
            await broadcast_forum_new_reply(topic.id, reply_broadcast_data)
        except Exception as e:
            logger.warning(f"WebSocket broadcast error for topic {topic.id}: {e}")

        response = {
            "success": True,
            "message": "Yanit basariyla eklendi",
            "reply": {
                "id": reply.id,
                "content": reply.content,
                "author": format_author_info(current_user),
                "parent_reply_id": getattr(reply, 'parent_reply_id', None),
                "created_at": format_datetime_utc(reply.created_at)
            },
            "rewards": {
                "reputation": reputation_earned,
                "coins": reward_amount,
                "badges": badges_earned
            }
        }

        if reward_amount:
            response["reward_message"] = f"+{reward_amount} Coin kazandiniz!"

        return response

    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Database integrity error in create_reply: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Yanit olusturulurken bir cakisma olustu. Lutfen tekrar deneyin."
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_reply: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yanit olusturulurken bir hata olustu. Lutfen tekrar deneyin."
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_reply: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Beklenmeyen bir hata olustu. Lutfen tekrar deneyin."
        )


# ============ Stats Endpoint ============

@router.get("/stats")
async def get_forum_stats(db: Session = Depends(get_db)):
    """
    Forum istatistikleri (public)

    Dondurur:
    - Kategori sayisi
    - Toplam konu sayisi
    - Toplam yanit sayisi
    - Toplam gonderi sayisi (konu + yanit)
    - Uye sayisi
    - Online kullanici sayisi
    - Bugunun istatistikleri
    """
    cache_key = "forum:stats"

    # Cache kontrol (kisa TTL - 30 saniye)
    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    try:
        # Bugun basi
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        # Sayimlari tek sorguda al (daha verimli)
        category_count = db.query(func.count(ForumCategory.id)).filter(
            ForumCategory.is_visible == True
        ).scalar() or 0

        topic_count = db.query(func.count(ForumTopic.id)).filter(
            ForumTopic.is_active == True
        ).scalar() or 0

        reply_count = db.query(func.count(ForumReply.id)).filter(
            ForumReply.is_active == True
        ).scalar() or 0

        # Bugunun istatistikleri
        today_topics = db.query(func.count(ForumTopic.id)).filter(
            ForumTopic.is_active == True,
            ForumTopic.created_at >= today_start
        ).scalar() or 0

        today_replies = db.query(func.count(ForumReply.id)).filter(
            ForumReply.is_active == True,
            ForumReply.created_at >= today_start
        ).scalar() or 0

        # Total posts = topics + replies
        total_posts = topic_count + reply_count

        # Total members
        member_count = db.query(func.count(User.id)).scalar() or 0

        # Newest member
        newest_member = None
        try:
            newest = db.query(User).order_by(desc(User.created_at)).first()
            if newest:
                newest_member = {
                    "id": newest.id,
                    "username": newest.username,
                    "joined_at": format_datetime_utc(newest.created_at)
                }
        except Exception:
            pass

        # Online users - last 15 minutes
        online_count = 0
        try:
            fifteen_min_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
            if hasattr(User, 'last_activity'):
                online_count = db.query(func.count(User.id)).filter(
                    User.last_activity >= fifteen_min_ago
                ).scalar() or 0
        except Exception:
            pass

        # En aktif kategoriler (top 3)
        top_categories = []
        try:
            cat_stats = db.query(
                ForumCategory.id,
                ForumCategory.name,
                ForumCategory.slug,
                func.count(ForumTopic.id).label('topic_count')
            ).outerjoin(
                ForumTopic, and_(
                    ForumTopic.category_id == ForumCategory.id,
                    ForumTopic.is_active == True
                )
            ).filter(
                ForumCategory.is_visible == True
            ).group_by(ForumCategory.id).order_by(
                desc('topic_count')
            ).limit(3).all()

            top_categories = [
                {"id": c.id, "name": c.name, "slug": c.slug, "topic_count": c.topic_count or 0}
                for c in cat_stats
            ]
        except Exception:
            pass

        response = {
            "success": True,
            "stats": {
                "categories": category_count,
                "topics": topic_count,
                "replies": reply_count,
                "total_posts": total_posts,
                "members": member_count,
                "online_users": online_count
            },
            "today": {
                "topics": today_topics,
                "replies": today_replies,
                "posts": today_topics + today_replies
            },
            "top_categories": top_categories,
            "newest_member": newest_member,
            # Legacy fields for backwards compatibility
            "total_topics": topic_count,
            "topics_count": topic_count,
            "posts_count": total_posts,
            "total_members": member_count,
            "members_count": member_count,
            "online_count": online_count
        }

        # Cache'e kaydet
        try:
            await redis_manager.set(cache_key, json.dumps(response), expire=30)
        except Exception:
            pass

        return response

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_forum_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Istatistikler yuklenirken bir hata olustu"
        )


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

@router.put("/topics/{slug_or_id}")
async def edit_topic(
    slug_or_id: str,
    data: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Konu duzenle - Sadece yazar veya admin duzenleyebilir

    Duzenleme yapar:
    - Baslik ve/veya icerik guncellemesi
    - Duzenleme gecmisi kaydeder
    - Baslik degisirse slug guncellenir
    """
    logger.info(f"Topic edit attempt by user {current_user.id} on topic {slug_or_id}")

    try:
        # Find topic by ID or slug
        if slug_or_id.isdigit():
            topic = db.query(ForumTopic).options(
                joinedload(ForumTopic.category)
            ).filter(
                ForumTopic.id == int(slug_or_id),
                ForumTopic.is_active == True
            ).first()
        else:
            topic = db.query(ForumTopic).options(
                joinedload(ForumTopic.category)
            ).filter(
                ForumTopic.slug == slug_or_id,
                ForumTopic.is_active == True
            ).first()

        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konu bulunamadi"
            )

        # Permission check: only author or admin can edit
        if not is_admin_or_author(current_user, topic.author_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu konuyu duzenleme yetkiniz yok"
            )

        # Check if anything to update
        if data.title is None and data.content is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Guncellenecek alan belirtilmedi"
            )

        changes_made = []
        old_slug = topic.slug

        # Update title if provided
        if data.title is not None:
            # XSS Protection - Sanitize title
            sanitized_title = sanitize_title(data.title.strip())
            topic.title = sanitized_title
            changes_made.append("baslik")

            # Update slug if title changed
            new_slug = generate_slug(sanitized_title)
            if new_slug != topic.slug:
                new_slug = ensure_unique_slug(db, new_slug, exclude_id=topic.id)
                topic.slug = new_slug

        # Update content if provided
        if data.content is not None:
            # XSS Protection - Sanitize content
            sanitized_content = sanitize_forum_content(data.content.strip())
            topic.content = sanitized_content
            changes_made.append("icerik")

        # Track edit history
        topic.edited_at = datetime.now(timezone.utc)
        if hasattr(topic, 'edited_by'):
            topic.edited_by = current_user.id

        db.commit()
        db.refresh(topic)

        logger.info(f"Topic {topic.id} edited by user {current_user.id}: {', '.join(changes_made)}")

        # Invalidate caches
        await invalidate_forum_cache()
        await invalidate_topic_cache(topic_id=topic.id, category_id=topic.category_id)

        return {
            "success": True,
            "message": "Konu basariyla guncellendi",
            "topic": {
                "id": topic.id,
                "title": topic.title,
                "slug": topic.slug,
                "old_slug": old_slug if old_slug != topic.slug else None,
                "edited_at": format_datetime_utc(topic.edited_at)
            },
            "changes": changes_made
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in edit_topic: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Konu guncellenirken bir hata olustu"
        )


@router.delete("/topics/{slug_or_id}")
async def delete_topic(
    slug_or_id: str,
    hard_delete: bool = Query(False, description="Kalici silme (sadece admin)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Konu sil - Sadece yazar veya admin silebilir

    Varsayilan olarak soft delete yapar (is_active = False).
    hard_delete=True ile kalici silme yapilabilir (sadece admin).
    """
    logger.info(f"Topic delete attempt by user {current_user.id} on topic {slug_or_id}")

    try:
        # Find topic by ID or slug
        if slug_or_id.isdigit():
            topic = db.query(ForumTopic).filter(
                ForumTopic.id == int(slug_or_id),
                ForumTopic.is_active == True
            ).first()
        else:
            topic = db.query(ForumTopic).filter(
                ForumTopic.slug == slug_or_id,
                ForumTopic.is_active == True
            ).first()

        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konu bulunamadi"
            )

        # Permission check: only author or admin can delete
        if not is_admin_or_author(current_user, topic.author_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu konuyu silme yetkiniz yok"
            )

        topic_id = topic.id
        category_id = topic.category_id
        reply_count = 0

        if hard_delete:
            # Only admin can hard delete
            if not is_admin_or_moderator(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Kalici silme sadece yoneticiler tarafindan yapilabilir"
                )

            # Count and delete related replies
            reply_count = db.query(func.count(ForumReply.id)).filter(
                ForumReply.topic_id == topic.id
            ).scalar() or 0

            # Delete related data
            db.query(ForumReply).filter(ForumReply.topic_id == topic.id).delete()

            # Delete topic tags
            try:
                db.query(ForumTopicTag).filter(ForumTopicTag.topic_id == topic.id).delete()
            except Exception:
                pass

            # Delete subscriptions
            try:
                db.query(ForumSubscription).filter(ForumSubscription.topic_id == topic.id).delete()
            except Exception:
                pass

            # Delete the topic
            db.delete(topic)
            db.commit()

            logger.warning(f"Topic {topic_id} hard deleted by admin {current_user.id}")
        else:
            # Soft delete - just mark as inactive
            topic.is_active = False
            topic.deleted_at = datetime.now(timezone.utc) if hasattr(topic, 'deleted_at') else None
            if hasattr(topic, 'deleted_by'):
                topic.deleted_by = current_user.id

            # Also soft delete all replies
            reply_count = db.query(ForumReply).filter(
                ForumReply.topic_id == topic.id,
                ForumReply.is_active == True
            ).update({"is_active": False}, synchronize_session=False)

            db.commit()

            logger.info(f"Topic {topic_id} soft deleted by user {current_user.id}")

        # Invalidate caches
        await invalidate_forum_cache()
        await invalidate_topic_cache(topic_id=topic_id, category_id=category_id)

        return {
            "success": True,
            "message": "Konu basariyla silindi",
            "topic_id": topic_id,
            "replies_affected": reply_count,
            "hard_deleted": hard_delete
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_topic: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Konu silinirken bir hata olustu"
        )


@router.put("/replies/{reply_id}")
async def edit_reply(
    reply_id: int,
    data: ReplyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Yanit duzenle - Sadece yazar veya admin duzenleyebilir

    Duzenleme yapar:
    - Icerik guncellemesi
    - Duzenleme zamani kaydeder
    """
    logger.info(f"Reply edit attempt by user {current_user.id} on reply {reply_id}")

    try:
        reply = db.query(ForumReply).options(
            joinedload(ForumReply.author)
        ).filter(
            ForumReply.id == reply_id,
            ForumReply.is_active == True
        ).first()

        if not reply:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Yanit bulunamadi"
            )

        # Permission check: only author or admin can edit
        if not is_admin_or_author(current_user, reply.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu yaniti duzenleme yetkiniz yok"
            )

        # Check if topic is locked
        topic = db.query(ForumTopic).filter(ForumTopic.id == reply.topic_id).first()
        if topic and topic.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu konu kilitli, yanitlar duzenlenemez"
            )

        # XSS Protection - Sanitize reply content
        sanitized_content = sanitize_forum_content(data.content.strip())

        # Update content and track edit time
        reply.content = sanitized_content
        reply.edited_at = datetime.now(timezone.utc)
        reply.updated_at = datetime.now(timezone.utc) if hasattr(reply, 'updated_at') else None

        db.commit()
        db.refresh(reply)

        logger.info(f"Reply {reply_id} edited by user {current_user.id}")

        # Invalidate topic cache
        await invalidate_topic_cache(topic_id=reply.topic_id)

        return {
            "success": True,
            "message": "Yanit basariyla guncellendi",
            "reply": {
                "id": reply.id,
                "content": reply.content,
                "edited_at": format_datetime_utc(reply.edited_at),
                "is_edited": True
            }
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in edit_reply: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yanit guncellenirken bir hata olustu"
        )


@router.delete("/replies/{reply_id}")
async def delete_reply(
    reply_id: int,
    hard_delete: bool = Query(False, description="Kalici silme (sadece admin)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Yanit sil - Sadece yazar veya admin silebilir

    Varsayilan olarak soft delete yapar (is_active = False).
    hard_delete=True ile kalici silme yapilabilir (sadece admin).
    """
    logger.info(f"Reply delete attempt by user {current_user.id} on reply {reply_id}")

    try:
        reply = db.query(ForumReply).filter(
            ForumReply.id == reply_id,
            ForumReply.is_active == True
        ).first()

        if not reply:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Yanit bulunamadi"
            )

        # Permission check: only author or admin can delete
        if not is_admin_or_author(current_user, reply.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu yaniti silme yetkiniz yok"
            )

        topic_id = reply.topic_id
        deleted_reply_id = reply.id

        if hard_delete:
            # Only admin can hard delete
            if not is_admin_or_moderator(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Kalici silme sadece yoneticiler tarafindan yapilabilir"
                )

            # Check for child replies (if threading exists)
            child_count = 0
            if hasattr(ForumReply, 'parent_reply_id'):
                child_count = db.query(func.count(ForumReply.id)).filter(
                    ForumReply.parent_reply_id == reply_id
                ).scalar() or 0

                # Update children to orphan them
                if child_count > 0:
                    db.query(ForumReply).filter(
                        ForumReply.parent_reply_id == reply_id
                    ).update({"parent_reply_id": None}, synchronize_session=False)

            # Delete the reply
            db.delete(reply)
            db.commit()

            logger.warning(f"Reply {deleted_reply_id} hard deleted by admin {current_user.id}")
        else:
            # Soft delete
            reply.is_active = False
            reply.deleted_at = datetime.now(timezone.utc) if hasattr(reply, 'deleted_at') else None
            if hasattr(reply, 'deleted_by'):
                reply.deleted_by = current_user.id
            db.commit()

            logger.info(f"Reply {deleted_reply_id} soft deleted by user {current_user.id}")

        # If this was the best answer, clear it
        if getattr(reply, 'is_best_answer', False):
            # Clear the best answer flag
            try:
                db.query(ForumReply).filter(
                    ForumReply.id == deleted_reply_id
                ).update({"is_best_answer": False}, synchronize_session=False)
                db.commit()
            except Exception:
                pass

        # Invalidate caches
        await invalidate_topic_cache(topic_id=topic_id)

        return {
            "success": True,
            "message": "Yanit basariyla silindi",
            "reply_id": deleted_reply_id,
            "hard_deleted": hard_delete
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_reply: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Yanit silinirken bir hata olustu"
        )


@router.post("/report", status_code=status.HTTP_201_CREATED)
async def report_content(
    data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Forum icerigi sikayet et (konu veya yanit)

    Sikayet Nedenleri:
    - spam: Spam icerik
    - harassment: Taciz veya kotu davranis
    - inappropriate: Uygunsuz icerik
    - other: Diger (detay gerekli)
    """
    logger.info(f"Report submitted by user {current_user.id}: {data.content_type} {data.content_id}")

    try:
        # Check if content exists and get author
        content_author_id = None
        content_title = None

        if data.content_type == "topic":
            content = db.query(ForumTopic).filter(
                ForumTopic.id == data.content_id,
                ForumTopic.is_active == True
            ).first()

            if not content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konu bulunamadi"
                )

            content_author_id = content.author_id
            content_title = content.title

        else:  # reply
            content = db.query(ForumReply).filter(
                ForumReply.id == data.content_id,
                ForumReply.is_active == True
            ).first()

            if not content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Yanit bulunamadi"
                )

            content_author_id = content.user_id

            # Get topic title for context
            topic = db.query(ForumTopic).filter(ForumTopic.id == content.topic_id).first()
            if topic:
                content_title = topic.title

        # Prevent self-reporting
        if content_author_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kendi iceriklerinizi sikayet edemezsiniz"
            )

        # Check for duplicate report
        existing_report = db.query(ForumReport).filter(
            ForumReport.reporter_id == current_user.id,
            ForumReport.content_type == data.content_type,
            ForumReport.content_id == data.content_id
        ).first()

        if existing_report:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
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

        logger.info(f"Report {report.id} created for {data.content_type} {data.content_id}")

        # Count total reports for this content
        report_count = db.query(func.count(ForumReport.id)).filter(
            ForumReport.content_type == data.content_type,
            ForumReport.content_id == data.content_id
        ).scalar() or 0

        # Auto-hide content if too many reports (threshold: 5)
        if report_count >= 5:
            try:
                if data.content_type == "topic":
                    db.query(ForumTopic).filter(
                        ForumTopic.id == data.content_id
                    ).update({"is_active": False}, synchronize_session=False)
                else:
                    db.query(ForumReply).filter(
                        ForumReply.id == data.content_id
                    ).update({"is_active": False}, synchronize_session=False)
                db.commit()
                logger.warning(f"Auto-hidden {data.content_type} {data.content_id} due to {report_count} reports")
            except Exception as e:
                logger.error(f"Auto-hide error: {e}")

        return {
            "success": True,
            "message": "Sikayetiniz alindi. Moderatorler en kisa surede inceleyecektir.",
            "report": {
                "id": report.id,
                "content_type": report.content_type,
                "content_id": report.content_id,
                "reason": report.reason,
                "created_at": format_datetime_utc(report.created_at) if hasattr(report, 'created_at') and report.created_at else None
            }
        }

    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"Duplicate report error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu icerigi zaten sikayet ettiniz"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error in report_content: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sikayet olusturulurken bir hata olustu"
        )


# ============ Table Creation Helper ============

def ensure_forum_tables(db: Session):
    """
    Ensure all new forum tables exist and have proper indexes.

    Tables created:
    - forum_tags: Tag storage
    - forum_topic_tags: Topic-tag relationships
    - forum_mentions: @mention tracking
    - forum_subscriptions: Topic subscription tracking

    Indexes added for performance:
    - Topic indexes for search/filter
    - Reply indexes for threading
    - Composite indexes for common queries
    """
    try:
        # Tags table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS forum_tags (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                slug VARCHAR(50) UNIQUE NOT NULL,
                color VARCHAR(20) DEFAULT '#6b7280',
                usage_count INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_tag_slug (slug),
                INDEX idx_tag_usage (usage_count DESC),
                INDEX idx_tag_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        # Topic-tag relationships
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS forum_topic_tags (
                topic_id INT NOT NULL,
                tag_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (topic_id, tag_id),
                INDEX idx_topic_tags_tag (tag_id),
                FOREIGN KEY (topic_id) REFERENCES forum_topics(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES forum_tags(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        # Mentions table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS forum_mentions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                mentioned_by INT NOT NULL,
                content_type VARCHAR(20) NOT NULL,
                content_id INT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_mention_user (user_id, is_read, created_at DESC),
                INDEX idx_mention_content (content_type, content_id),
                INDEX idx_mention_by (mentioned_by),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (mentioned_by) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        # Subscriptions table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS forum_subscriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                topic_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_forum_subscription (user_id, topic_id),
                INDEX idx_subscription_user (user_id, created_at DESC),
                INDEX idx_subscription_topic (topic_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (topic_id) REFERENCES forum_topics(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        # Add missing columns to forum_replies
        try:
            db.execute(text("ALTER TABLE forum_replies ADD COLUMN is_best_answer BOOLEAN DEFAULT FALSE"))
        except Exception:
            pass

        try:
            db.execute(text("ALTER TABLE forum_replies ADD COLUMN parent_reply_id INT NULL"))
        except Exception:
            pass

        try:
            db.execute(text("ALTER TABLE forum_replies ADD COLUMN edited_at DATETIME NULL"))
        except Exception:
            pass

        try:
            db.execute(text("ALTER TABLE forum_replies ADD COLUMN likes INT DEFAULT 0"))
        except Exception:
            pass

        # Add missing columns to forum_topics
        try:
            db.execute(text("ALTER TABLE forum_topics ADD COLUMN edited_at DATETIME NULL"))
        except Exception:
            pass

        try:
            db.execute(text("ALTER TABLE forum_topics ADD COLUMN edited_by INT NULL"))
        except Exception:
            pass

        try:
            db.execute(text("ALTER TABLE forum_topics ADD COLUMN is_solved BOOLEAN DEFAULT FALSE"))
        except Exception:
            pass

        try:
            db.execute(text("ALTER TABLE forum_topics ADD COLUMN likes INT DEFAULT 0"))
        except Exception:
            pass

        # Add performance indexes to existing tables
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_topics_category_active_created
                ON forum_topics (category_id, is_active, created_at DESC)
            """))
        except Exception:
            pass

        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_topics_author_active
                ON forum_topics (author_id, is_active)
            """))
        except Exception:
            pass

        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_topics_pinned_created
                ON forum_topics (is_pinned DESC, created_at DESC)
            """))
        except Exception:
            pass

        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_replies_topic_active_created
                ON forum_replies (topic_id, is_active, created_at)
            """))
        except Exception:
            pass

        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_replies_user_active
                ON forum_replies (user_id, is_active)
            """))
        except Exception:
            pass

        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_replies_best_answer
                ON forum_replies (topic_id, is_best_answer)
            """))
        except Exception:
            pass

        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_replies_parent
                ON forum_replies (parent_reply_id)
            """))
        except Exception:
            pass

        # Fulltext index for search
        try:
            db.execute(text("""
                CREATE FULLTEXT INDEX IF NOT EXISTS idx_topics_fulltext
                ON forum_topics (title, content)
            """))
        except Exception:
            pass

        db.commit()
        logger.info("Forum tables and indexes ensured")

    except Exception as e:
        db.rollback()
        logger.warning(f"Table creation/index warning: {e}")


# ============ Tag Helper Functions ============

def get_or_create_tag(db: Session, tag_name: str) -> ForumTag:
    """Get existing tag or create a new one"""
    tag_name = tag_name.strip().lower()[:50]
    # BUGFIX: Ensure tag name has minimum length
    if not tag_name or len(tag_name) < 2:
        return None
    tag_slug = generate_slug(tag_name)
    # BUGFIX: Ensure slug generation succeeded
    if not tag_slug or len(tag_slug) < 2:
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
    # BUGFIX: Commit tag associations and usage count updates
    db.commit()


def get_topic_tags(db: Session, topic_id: int) -> List[dict]:
    """Get tags for a topic"""
    tags = db.query(ForumTag).join(ForumTopicTag, ForumTopicTag.tag_id == ForumTag.id).filter(ForumTopicTag.topic_id == topic_id).all()
    return [{"id": t.id, "name": t.name, "slug": t.slug, "color": t.color} for t in tags]


# ============ Mention Helper Functions ============

def extract_mentions(content: str) -> List[str]:
    """
    Extract @username mentions from content

    Returns unique usernames (case-insensitive, limited to MAX_MENTIONS_PER_CONTENT)
    """
    if not content:
        return []

    pattern = r'@([a-zA-Z0-9_-]{3,30})'
    matches = re.findall(pattern, content)

    # Deduplicate case-insensitively
    seen = set()
    unique = []
    for m in matches:
        lower = m.lower()
        if lower not in seen:
            seen.add(lower)
            unique.append(m)

    return unique[:MAX_MENTIONS_PER_CONTENT]


def process_mentions(
    db: Session,
    content: str,
    content_type: str,
    content_id: int,
    mentioned_by_id: int,
    topic_slug: str = None
) -> int:
    """
    Process @mentions in content and create notifications

    Returns: Number of mentions processed
    """
    usernames = extract_mentions(content)
    if not usernames:
        return 0

    mentions_created = 0
    mentioner = db.query(User).filter(User.id == mentioned_by_id).first()
    mentioner_name = mentioner.username if mentioner else "Birisi"

    for username in usernames:
        try:
            # Case-insensitive username search
            mentioned_user = db.query(User).filter(
                func.lower(User.username) == func.lower(username)
            ).first()

            if mentioned_user and mentioned_user.id != mentioned_by_id:
                # Check if mention already exists (prevent duplicates)
                existing = db.query(ForumMention).filter(
                    ForumMention.user_id == mentioned_user.id,
                    ForumMention.content_type == content_type,
                    ForumMention.content_id == content_id,
                    ForumMention.mentioned_by == mentioned_by_id
                ).first()

                if not existing:
                    mention = ForumMention(
                        user_id=mentioned_user.id,
                        mentioned_by=mentioned_by_id,
                        content_type=content_type,
                        content_id=content_id,
                        is_read=False
                    )
                    db.add(mention)

                    notification = Notification(
                        user_id=mentioned_user.id,
                        type="forum_mention",
                        title="Sizi etiketledi",
                        message=f"@{mentioner_name} sizi bir {'konuda' if content_type == 'topic' else 'yanıtta'} etiketledi.",
                        link=f"/forum/topic/{topic_slug}" if topic_slug else None,
                        is_read=False
                    )
                    db.add(notification)
                    mentions_created += 1

        except Exception as e:
            logger.warning(f"Error processing mention for @{username}: {e}")
            continue

    return mentions_created


# ============ Subscription Helper Functions ============

def notify_subscribers(db: Session, topic_id: int, replier_id: int, topic_title: str, topic_slug: str):
    """Notify all subscribers of a topic about a new reply"""
    subscriptions = db.query(ForumSubscription).filter(ForumSubscription.topic_id == topic_id, ForumSubscription.user_id != replier_id).all()
    replier = db.query(User).filter(User.id == replier_id).first()
    replier_name = replier.username if replier else "Birisi"
    for sub in subscriptions:
        notification = Notification(user_id=sub.user_id, type="forum_subscription", title="Takip ettiginiz konuya yanit geldi", message=f"@{replier_name}, '{topic_title[:50]}...' konusuna yanit verdi.", link=f"/forum/topic/{topic_slug}", is_read=False)
        db.add(notification)
    # BUGFIX: Commit notifications to database
    if subscriptions:
        db.commit()


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
        "topics": [{"id": t.id, "title": t.title, "slug": t.slug, "author_name": t.author.username if t.author else None, "author_avatar": format_avatar_url(t.author.avatar) if t.author else None, "view_count": t.view_count or 0, "reply_count": reply_counts.get(t.id, 0), "created_at": t.created_at.isoformat() if t.created_at else None} for t in topics],
        "total": total, "page": page, "pages": (total + limit - 1) // limit
    }


# ============ Subscription Endpoints ============

@router.post("/topics/{slug_or_id}/subscribe")
async def subscribe_to_topic(slug_or_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Subscribe to a topic"""
    ensure_forum_tables(db)

    # BUGFIX: Add input validation
    if not slug_or_id or len(slug_or_id) > 200:
        raise HTTPException(status_code=400, detail="Gecersiz konu ID/slug")

    # Find topic by ID or slug
    if slug_or_id.isdigit():
        topic_id = safe_int_convert(slug_or_id)
        if not topic_id:
            raise HTTPException(status_code=400, detail="Gecersiz konu ID")
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id, ForumTopic.is_active == True).first()
    else:
        topic = db.query(ForumTopic).filter(ForumTopic.slug == slug_or_id, ForumTopic.is_active == True).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")
    existing = db.query(ForumSubscription).filter(ForumSubscription.user_id == current_user.id, ForumSubscription.topic_id == topic.id).first()
    if existing:
        return {"success": True, "message": "Zaten bu konuya abone olmuşsunuz", "subscribed": True}

    # BUGFIX: Add try/except for database operations
    try:
        subscription = ForumSubscription(user_id=current_user.id, topic_id=topic.id)
        db.add(subscription)
        db.commit()
        return {"success": True, "message": "Konuya abone oldunuz", "subscribed": True}
    except Exception as e:
        db.rollback()
        logger.error(f"Subscription error: {e}")
        raise HTTPException(status_code=500, detail="Abonelik islemi basarisiz")


@router.delete("/topics/{slug_or_id}/subscribe")
async def unsubscribe_from_topic(slug_or_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Unsubscribe from a topic"""
    ensure_forum_tables(db)

    # BUGFIX: Add input validation
    if not slug_or_id or len(slug_or_id) > 200:
        raise HTTPException(status_code=400, detail="Gecersiz konu ID/slug")

    # Find topic by ID or slug
    if slug_or_id.isdigit():
        topic_id = safe_int_convert(slug_or_id)
        if not topic_id:
            raise HTTPException(status_code=400, detail="Gecersiz konu ID")
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id, ForumTopic.is_active == True).first()
    else:
        topic = db.query(ForumTopic).filter(ForumTopic.slug == slug_or_id, ForumTopic.is_active == True).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")
    subscription = db.query(ForumSubscription).filter(ForumSubscription.user_id == current_user.id, ForumSubscription.topic_id == topic.id).first()
    if not subscription:
        return {"success": False, "message": "Bu konuya abone degilsiniz", "subscribed": False}

    # BUGFIX: Add try/except for database operations
    try:
        db.delete(subscription)
        db.commit()
        return {"success": True, "message": "Abonelik iptal edildi", "subscribed": False}
    except Exception as e:
        db.rollback()
        logger.error(f"Unsubscribe error: {e}")
        raise HTTPException(status_code=500, detail="Abonelik iptali basarisiz")


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


@router.get("/topics/{slug_or_id}/subscription-status")
async def get_subscription_status(slug_or_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Check if user is subscribed to a topic"""
    ensure_forum_tables(db)
    # Find topic by ID or slug
    if slug_or_id.isdigit():
        topic = db.query(ForumTopic).filter(ForumTopic.id == int(slug_or_id)).first()
    else:
        topic = db.query(ForumTopic).filter(ForumTopic.slug == slug_or_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")
    subscription = db.query(ForumSubscription).filter(ForumSubscription.user_id == current_user.id, ForumSubscription.topic_id == topic.id).first()
    return {"subscribed": subscription is not None}


# ============ Like Endpoints ============

@router.post("/topics/{topic_id}/like")
async def like_topic(topic_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Like a topic - toggles like status"""
    ensure_forum_tables(db)

    # Find topic by id or slug
    if topic_id.isdigit():
        topic = db.query(ForumTopic).filter(ForumTopic.id == int(topic_id), ForumTopic.is_active == True).first()
    else:
        topic = db.query(ForumTopic).filter(ForumTopic.slug == topic_id, ForumTopic.is_active == True).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")

    # BUGFIX: Use try/except to handle race conditions and ensure atomicity
    try:
        # Check if already liked using forum_likes table
        existing_like = db.execute(text(
            "SELECT id FROM forum_likes WHERE user_id = :uid AND content_type = 'topic' AND content_id = :cid"
        ), {"uid": current_user.id, "cid": topic.id}).fetchone()

        if existing_like:
            # Already liked - remove like (toggle off)
            db.execute(text(
                "DELETE FROM forum_likes WHERE user_id = :uid AND content_type = 'topic' AND content_id = :cid"
            ), {"uid": current_user.id, "cid": topic.id})
            # Prevent negative likes
            topic.likes = max(0, (topic.likes or 0) - 1)
            db.commit()
            return {"message": "Begeni kaldirildi", "likes": topic.likes, "has_liked": False}

        # Add new like (prevent duplicates with INSERT IGNORE)
        db.execute(text(
            "INSERT IGNORE INTO forum_likes (user_id, content_type, content_id) VALUES (:uid, 'topic', :cid)"
        ), {"uid": current_user.id, "cid": topic.id})

        if not hasattr(topic, 'likes') or topic.likes is None:
            topic.likes = 0
        topic.likes += 1
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Like topic error: {e}")
        raise HTTPException(status_code=500, detail="Begeni islemi basarisiz")

    # Award armor for receiving likes (only for new likes, not to self)
    if topic.author_id != current_user.id:
        try:
            from app.services.forum_rewards import get_forum_reward_service
            reward_service = get_forum_reward_service(db)
            reward_service.reward_like_received(user_id=topic.author_id, topic_id=topic.id)
        except Exception as e:
            logger.warning(f"Like reward error: {e}")

    return {"message": "Begenildi", "likes": topic.likes, "has_liked": True}


@router.delete("/topics/{topic_id}/like")
async def unlike_topic(topic_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Unlike a topic"""
    ensure_forum_tables(db)

    # Find topic by id or slug
    if topic_id.isdigit():
        topic = db.query(ForumTopic).filter(ForumTopic.id == int(topic_id), ForumTopic.is_active == True).first()
    else:
        topic = db.query(ForumTopic).filter(ForumTopic.slug == topic_id, ForumTopic.is_active == True).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")

    # Remove like from forum_likes table
    result = db.execute(text(
        "DELETE FROM forum_likes WHERE user_id = :uid AND content_type = 'topic' AND content_id = :cid"
    ), {"uid": current_user.id, "cid": topic.id})

    if result.rowcount > 0:
        # Prevent negative likes
        topic.likes = max(0, (topic.likes or 0) - 1)
        db.commit()

    return {"message": "Begeni kaldirildi", "likes": topic.likes or 0, "has_liked": False}


@router.post("/replies/{reply_id}/like")
async def like_reply(reply_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Like a reply - toggles like status"""
    ensure_forum_tables(db)

    reply = db.query(ForumReply).filter(ForumReply.id == reply_id, ForumReply.is_active == True).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Yanit bulunamadi")

    # BUGFIX: Use try/except to handle race conditions and ensure atomicity
    try:
        # Check if already liked
        existing_like = db.execute(text(
            "SELECT id FROM forum_likes WHERE user_id = :uid AND content_type = 'reply' AND content_id = :cid"
        ), {"uid": current_user.id, "cid": reply.id}).fetchone()

        if existing_like:
            # Already liked - remove like (toggle off)
            db.execute(text(
                "DELETE FROM forum_likes WHERE user_id = :uid AND content_type = 'reply' AND content_id = :cid"
            ), {"uid": current_user.id, "cid": reply.id})
            # Prevent negative likes
            reply.likes = max(0, (reply.likes or 0) - 1)
            db.commit()
            return {"message": "Begeni kaldirildi", "likes": reply.likes, "has_liked": False}

        # Add new like (prevent duplicates with INSERT IGNORE)
        db.execute(text(
            "INSERT IGNORE INTO forum_likes (user_id, content_type, content_id) VALUES (:uid, 'reply', :cid)"
        ), {"uid": current_user.id, "cid": reply.id})

        if not hasattr(reply, 'likes') or reply.likes is None:
            reply.likes = 0
        reply.likes += 1
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Like reply error: {e}")
        raise HTTPException(status_code=500, detail="Begeni islemi basarisiz")

    # Award armor for receiving likes (only for new likes, not to self)
    if reply.user_id != current_user.id:
        try:
            from app.services.forum_rewards import get_forum_reward_service
            reward_service = get_forum_reward_service(db)
            reward_service.reward_like_received(user_id=reply.user_id, reply_id=reply.id)
        except Exception as e:
            logger.warning(f"Reply like reward error: {e}")

    return {"message": "Begenildi", "likes": reply.likes, "has_liked": True}


@router.delete("/replies/{reply_id}/like")
async def unlike_reply(reply_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Unlike a reply"""
    ensure_forum_tables(db)

    reply = db.query(ForumReply).filter(ForumReply.id == reply_id, ForumReply.is_active == True).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Yanit bulunamadi")

    # Remove like from forum_likes table
    result = db.execute(text(
        "DELETE FROM forum_likes WHERE user_id = :uid AND content_type = 'reply' AND content_id = :cid"
    ), {"uid": current_user.id, "cid": reply.id})

    if result.rowcount > 0:
        # Prevent negative likes
        reply.likes = max(0, (reply.likes or 0) - 1)
        db.commit()

    return {"message": "Begeni kaldirildi", "likes": reply.likes or 0, "has_liked": False}


# Legacy endpoint for backwards compatibility
@router.delete("/replies/{reply_id}/like_legacy")
async def unlike_reply_legacy(reply_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Unlike a reply (legacy)"""
    ensure_forum_tables(db)

    reply = db.query(ForumReply).filter(ForumReply.id == reply_id, ForumReply.is_active == True).first()
    if not reply:
        raise HTTPException(status_code=404, detail="Yanit bulunamadi")

    if not hasattr(reply, 'likes') or reply.likes is None:
        reply.likes = 0
    if reply.likes > 0:
        reply.likes -= 1
    db.commit()

    return {"message": "Begeni kaldirildi", "likes": reply.likes}


# ============ Bookmark Endpoints ============

@router.post("/topics/{topic_id}/bookmark")
async def bookmark_topic(topic_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Bookmark a topic"""
    ensure_forum_tables(db)

    # BUGFIX: Add input validation
    if not topic_id or len(topic_id) > 200:
        raise HTTPException(status_code=400, detail="Gecersiz konu ID/slug")

    # Find topic by id or slug
    if topic_id.isdigit():
        topic_id_int = safe_int_convert(topic_id)
        if not topic_id_int:
            raise HTTPException(status_code=400, detail="Gecersiz konu ID")
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id_int, ForumTopic.is_active == True).first()
    else:
        topic = db.query(ForumTopic).filter(ForumTopic.slug == topic_id, ForumTopic.is_active == True).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")

    # Check if already bookmarked (use subscription as bookmark for simplicity)
    existing = db.query(ForumSubscription).filter(
        ForumSubscription.user_id == current_user.id,
        ForumSubscription.topic_id == topic.id
    ).first()

    if existing:
        return {"success": True, "message": "Zaten yer iminde", "bookmarked": True}

    # BUGFIX: Add try/except for database operations
    try:
        # Create bookmark (using subscription model)
        bookmark = ForumSubscription(user_id=current_user.id, topic_id=topic.id)
        db.add(bookmark)
        db.commit()
        return {"success": True, "message": "Yer imine eklendi", "bookmarked": True}
    except Exception as e:
        db.rollback()
        logger.error(f"Bookmark error: {e}")
        raise HTTPException(status_code=500, detail="Yer imi ekleme basarisiz")


@router.delete("/topics/{topic_id}/bookmark")
async def unbookmark_topic(topic_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Remove topic from bookmarks"""
    ensure_forum_tables(db)

    # BUGFIX: Add input validation
    if not topic_id or len(topic_id) > 200:
        raise HTTPException(status_code=400, detail="Gecersiz konu ID/slug")

    # Find topic by id or slug
    if topic_id.isdigit():
        topic_id_int = safe_int_convert(topic_id)
        if not topic_id_int:
            raise HTTPException(status_code=400, detail="Gecersiz konu ID")
        topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id_int, ForumTopic.is_active == True).first()
    else:
        topic = db.query(ForumTopic).filter(ForumTopic.slug == topic_id, ForumTopic.is_active == True).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Konu bulunamadi")

    # BUGFIX: Add try/except for database operations
    try:
        # Remove bookmark
        db.query(ForumSubscription).filter(
            ForumSubscription.user_id == current_user.id,
            ForumSubscription.topic_id == topic.id
        ).delete()
        db.commit()
        return {"success": True, "message": "Yer iminden cikarildi", "bookmarked": False}
    except Exception as e:
        db.rollback()
        logger.error(f"Unbookmark error: {e}")
        raise HTTPException(status_code=500, detail="Yer imi cikarma basarisiz")


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

    # Armor ödülü ver (sadece yanıt sahibine, kendi yanıtını seçemez)
    armor_earned = None
    if reply.user_id != current_user.id:
        try:
            from app.services.forum_rewards import get_forum_reward_service
            reward_service = get_forum_reward_service(db)
            armor_earned = reward_service.reward_best_answer(
                user_id=reply.user_id,
                reply_id=reply.id,
                topic_id=topic.id
            )
        except Exception as e:
            logger.warning(f"Best answer reward error: {e}")

        # Bildirim gönder
        notification = Notification(user_id=reply.user_id, type="forum_best_answer", title="Yanitiniz en iyi yanit secildi!", message=f"'{topic.title[:50]}...' konusundaki yanitiniz en iyi yanit olarak secildi. +25 Armor kazandiniz!", link=f"/forum/topic/{topic.slug}", is_read=False)
        db.add(notification)
        db.commit()

    return {"message": "En iyi yanit secildi", "reply_id": reply_id, "armor_earned": armor_earned}


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

    # BUGFIX: Batch load all related data to prevent N+1 queries
    # Get all unique user IDs, topic IDs, and reply IDs
    user_ids = list(set([m.mentioned_by for m in mentions if m.mentioned_by]))
    topic_ids = [m.content_id for m in mentions if m.content_type == "topic"]
    reply_ids = [m.content_id for m in mentions if m.content_type == "reply"]

    # Batch load users
    users_map = {}
    if user_ids:
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        users_map = {u.id: u for u in users}

    # Batch load topics
    topics_map = {}
    if topic_ids:
        topics = db.query(ForumTopic).filter(ForumTopic.id.in_(topic_ids)).all()
        topics_map = {t.id: t for t in topics}

    # Batch load replies with their topics
    replies_map = {}
    reply_topics_map = {}
    if reply_ids:
        replies = db.query(ForumReply).filter(ForumReply.id.in_(reply_ids)).all()
        replies_map = {r.id: r for r in replies}
        reply_topic_ids = [r.topic_id for r in replies if r.topic_id]
        if reply_topic_ids:
            reply_topics = db.query(ForumTopic).filter(ForumTopic.id.in_(reply_topic_ids)).all()
            reply_topics_map = {t.id: t for t in reply_topics}

    # Build result using cached data
    result = []
    for m in mentions:
        mentioner = users_map.get(m.mentioned_by)
        item = {
            "id": m.id,
            "content_type": m.content_type,
            "content_id": m.content_id,
            "mentioned_by": mentioner.username if mentioner else None,
            "mentioned_by_avatar": mentioner.avatar if mentioner else None,
            "is_read": m.is_read,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        if m.content_type == "topic":
            t = topics_map.get(m.content_id)
            if t:
                item["link"] = f"/forum/topic/{t.slug}"
                item["title"] = t.title
        elif m.content_type == "reply":
            r = replies_map.get(m.content_id)
            if r:
                t = reply_topics_map.get(r.topic_id)
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


# ============ Admin Cleanup Endpoints ============

@router.post("/admin/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_deleted_content(
    older_than_days: int = Query(30, ge=1, le=365, description="Bu kadar gunden eski silinen icerikleri temizle"),
    dry_run: bool = Query(True, description="True ise sadece rapor dondurur, silmez"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Silinen icerikleri kalici olarak temizle (sadece admin)

    Bu endpoint soft-delete edilmis icerikleri kalici olarak siler:
    - Silinmis konular ve bagli yanitlar
    - Silinmis yanitlar
    - Orphan (sahipsiz) subscriptions ve mentions

    Parametreler:
    - older_than_days: Bu kadar gunden eski silinen icerikleri temizle (varsayilan: 30)
    - dry_run: True ise sadece rapor dondurur, gercekten silmez (varsayilan: True)
    """
    # Only admin can run cleanup
    if not is_admin_or_moderator(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu islemi sadece yoneticiler yapabilir"
        )

    logger.info(f"Forum cleanup initiated by admin {current_user.id}, dry_run={dry_run}, older_than={older_than_days} days")

    try:
        # Calculate cutoff date
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)

        # Count soft-deleted content
        deleted_topics_count = db.query(func.count(ForumTopic.id)).filter(
            ForumTopic.is_active == False,
            ForumTopic.created_at < cutoff_date
        ).scalar() or 0

        deleted_replies_count = db.query(func.count(ForumReply.id)).filter(
            ForumReply.is_active == False,
            ForumReply.created_at < cutoff_date
        ).scalar() or 0

        # Count orphaned subscriptions (to deleted topics)
        orphan_subscriptions = db.query(func.count(ForumSubscription.id)).filter(
            ~ForumSubscription.topic_id.in_(
                db.query(ForumTopic.id).filter(ForumTopic.is_active == True)
            )
        ).scalar() or 0

        # Count orphaned mentions (to deleted content)
        orphan_mentions = db.query(func.count(ForumMention.id)).filter(
            or_(
                and_(
                    ForumMention.content_type == "topic",
                    ~ForumMention.content_id.in_(
                        db.query(ForumTopic.id).filter(ForumTopic.is_active == True)
                    )
                ),
                and_(
                    ForumMention.content_type == "reply",
                    ~ForumMention.content_id.in_(
                        db.query(ForumReply.id).filter(ForumReply.is_active == True)
                    )
                )
            )
        ).scalar() or 0

        cleanup_report = {
            "success": True,
            "dry_run": dry_run,
            "older_than_days": older_than_days,
            "cutoff_date": format_datetime_utc(cutoff_date),
            "counts": {
                "deleted_topics": deleted_topics_count,
                "deleted_replies": deleted_replies_count,
                "orphan_subscriptions": orphan_subscriptions,
                "orphan_mentions": orphan_mentions,
                "total": deleted_topics_count + deleted_replies_count + orphan_subscriptions + orphan_mentions
            }
        }

        if not dry_run:
            # Perform actual cleanup
            deleted_items = {
                "topics": 0,
                "replies": 0,
                "subscriptions": 0,
                "mentions": 0,
                "topic_tags": 0
            }

            # Get IDs of topics to delete
            topics_to_delete = db.query(ForumTopic.id).filter(
                ForumTopic.is_active == False,
                ForumTopic.created_at < cutoff_date
            ).all()
            topic_ids = [t.id for t in topics_to_delete]

            if topic_ids:
                # Delete related topic tags
                deleted_items["topic_tags"] = db.query(ForumTopicTag).filter(
                    ForumTopicTag.topic_id.in_(topic_ids)
                ).delete(synchronize_session=False)

                # Delete related subscriptions
                deleted_items["subscriptions"] += db.query(ForumSubscription).filter(
                    ForumSubscription.topic_id.in_(topic_ids)
                ).delete(synchronize_session=False)

                # Delete related replies (hard delete)
                deleted_items["replies"] += db.query(ForumReply).filter(
                    ForumReply.topic_id.in_(topic_ids)
                ).delete(synchronize_session=False)

                # Delete related mentions
                deleted_items["mentions"] += db.query(ForumMention).filter(
                    ForumMention.content_type == "topic",
                    ForumMention.content_id.in_(topic_ids)
                ).delete(synchronize_session=False)

                # Delete the topics themselves
                deleted_items["topics"] = db.query(ForumTopic).filter(
                    ForumTopic.id.in_(topic_ids)
                ).delete(synchronize_session=False)

            # Delete standalone orphaned replies
            replies_to_delete = db.query(ForumReply.id).filter(
                ForumReply.is_active == False,
                ForumReply.created_at < cutoff_date,
                ~ForumReply.topic_id.in_(topic_ids) if topic_ids else True
            ).all()
            reply_ids = [r.id for r in replies_to_delete]

            if reply_ids:
                # Delete related mentions
                deleted_items["mentions"] += db.query(ForumMention).filter(
                    ForumMention.content_type == "reply",
                    ForumMention.content_id.in_(reply_ids)
                ).delete(synchronize_session=False)

                # Delete the replies
                deleted_items["replies"] += db.query(ForumReply).filter(
                    ForumReply.id.in_(reply_ids)
                ).delete(synchronize_session=False)

            # Clean up orphaned subscriptions
            deleted_items["subscriptions"] += db.query(ForumSubscription).filter(
                ~ForumSubscription.topic_id.in_(
                    db.query(ForumTopic.id).filter(ForumTopic.is_active == True)
                )
            ).delete(synchronize_session=False)

            # Clean up orphaned mentions
            deleted_items["mentions"] += db.query(ForumMention).filter(
                or_(
                    and_(
                        ForumMention.content_type == "topic",
                        ~ForumMention.content_id.in_(
                            db.query(ForumTopic.id).filter(ForumTopic.is_active == True)
                        )
                    ),
                    and_(
                        ForumMention.content_type == "reply",
                        ~ForumMention.content_id.in_(
                            db.query(ForumReply.id).filter(ForumReply.is_active == True)
                        )
                    )
                )
            ).delete(synchronize_session=False)

            db.commit()

            cleanup_report["deleted"] = deleted_items
            cleanup_report["message"] = "Temizlik islemi tamamlandi"

            logger.info(f"Forum cleanup completed: {deleted_items}")

            # Invalidate all caches after cleanup
            await invalidate_forum_cache()
        else:
            cleanup_report["message"] = "Dry run - hicbir sey silinmedi. Gercek temizlik icin dry_run=false kullanin."

        return cleanup_report

    except SQLAlchemyError as e:
        logger.error(f"Database error in cleanup: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Temizlik sirasinda bir hata olustu"
        )


@router.get("/admin/health")
async def forum_health_check(db: Session = Depends(get_db)):
    """
    Forum saglik kontrolu (public)

    Veritabani baglantisi ve temel sayimlari kontrol eder.
    """
    try:
        # Quick database check
        topic_count = db.query(func.count(ForumTopic.id)).scalar()
        reply_count = db.query(func.count(ForumReply.id)).scalar()
        category_count = db.query(func.count(ForumCategory.id)).scalar()

        # Check Redis
        redis_ok = False
        try:
            await redis_manager.set("forum:health_check", "ok", expire=10)
            redis_ok = True
        except Exception:
            pass

        return {
            "success": True,
            "status": "healthy",
            "database": {
                "connected": True,
                "topics": topic_count,
                "replies": reply_count,
                "categories": category_count
            },
            "cache": {
                "redis": redis_ok
            },
            "version": "6.1.0",
            "timestamp": format_datetime_utc(datetime.now(timezone.utc))
        }

    except SQLAlchemyError as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": "Database connection failed",
            "timestamp": format_datetime_utc(datetime.now(timezone.utc))
        }
