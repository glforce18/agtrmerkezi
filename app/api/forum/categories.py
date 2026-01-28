"""
AGTR Merkezi - Forum Categories API
Category management and listing
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.common import NotFoundError, log_api_call
from app.models.connection import get_db
from app.models.database import ForumCategory

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================
# Response Models
# ============================================


class CategoryResponse(BaseModel):
    """Category response model"""

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    topic_count: int = 0
    post_count: int = 0
    display_order: Optional[int] = 0
    is_visible: Optional[bool] = True
    is_locked: Optional[bool] = False

    class Config:
        from_attributes = True


# ============================================
# Endpoints
# ============================================


@router.get("", response_model=List[CategoryResponse])
async def get_categories(
    include_stats: bool = Query(True, description="Include topic/reply counts"),
    db: Session = Depends(get_db),
):
    """Get all forum categories"""
    try:
        log_api_call("get_categories", None)

        categories = (
            db.query(ForumCategory)
            .filter(ForumCategory.is_active == True)
            .filter(ForumCategory.is_visible == True)
            .order_by(ForumCategory.display_order)
            .all()
        )

        return categories

    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise


@router.get("/{slug_or_id}", response_model=CategoryResponse)
async def get_category(slug_or_id: str, db: Session = Depends(get_db)):
    """Get category by slug or ID"""
    try:
        # Try to parse as ID first
        if slug_or_id.isdigit():
            category = db.query(ForumCategory).filter(ForumCategory.id == int(slug_or_id)).first()
        else:
            category = db.query(ForumCategory).filter(ForumCategory.slug == slug_or_id).first()

        if not category:
            raise NotFoundError("Kategori bulunamadı")

        return category

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching category: {e}")
        raise
