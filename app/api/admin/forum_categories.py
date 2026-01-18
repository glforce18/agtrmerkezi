# ============================================
# AGTR v6.0 - Forum Kategori CRUD API
# Dosya: app/api/admin/forum_categories.py
# ============================================

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import User
from app.models.forum import ForumCategory, ForumReply, ForumTopic

router = APIRouter(prefix="/admin/forum", tags=["admin-forum"])


# ============ Pydantic Schemas ============

class CategoryCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = "fas fa-folder"
    display_order: Optional[int] = 0
    is_active: Optional[bool] = True


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str]
    icon: str
    display_order: int
    is_active: bool
    topic_count: int = 0
    reply_count: int = 0


# ============ Helper Functions ============

def generate_slug(name: str) -> str:
    """Türkçe karakterleri dönüştürüp slug oluştur"""
    tr_map = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    slug = name.lower()
    for tr_char, en_char in tr_map.items():
        slug = slug.replace(tr_char, en_char)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def ensure_unique_slug(db: Session, slug: str, exclude_id: Optional[int] = None) -> str:
    """Benzersiz slug oluştur"""
    base_slug = slug
    counter = 1
    while True:
        query = db.query(ForumCategory).filter(ForumCategory.slug == slug)
        if exclude_id:
            query = query.filter(ForumCategory.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


# ============ API Endpoints ============

@router.get("/categories")
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Tüm forum kategorilerini getir"""
    categories = db.query(ForumCategory).order_by(ForumCategory.display_order).all()
    
    result = []
    for cat in categories:
        # Konu ve yanıt sayılarını hesapla
        topic_count = db.query(func.count(ForumTopic.id)).filter(
            ForumTopic.category_id == cat.id
        ).scalar() or 0
        
        reply_count = db.query(func.count(ForumReply.id)).join(
            ForumTopic, ForumReply.topic_id == ForumTopic.id
        ).filter(ForumTopic.category_id == cat.id).scalar() or 0
        
        result.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "description": cat.description,
            "icon": cat.icon or "fas fa-folder",
            "display_order": cat.display_order or 0,
            "is_active": cat.is_visible,
            "topic_count": topic_count,
            "reply_count": reply_count
        })
    
    return {"categories": result}


@router.get("/categories/{category_id}")
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Tek kategori getir"""
    category = db.query(ForumCategory).filter(ForumCategory.id == category_id).first()
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
        "display_order": category.display_order,
        "is_active": category.is_visible,
        "topic_count": topic_count
    }


@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Yeni kategori oluştur"""
    # Slug oluştur
    slug = data.slug if data.slug else generate_slug(data.name)
    slug = ensure_unique_slug(db, slug)
    
    # Aynı isimde kategori var mı kontrol
    existing = db.query(ForumCategory).filter(ForumCategory.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu isimde bir kategori zaten var")
    
    category = ForumCategory(
        name=data.name,
        slug=slug,
        description=data.description,
        icon=data.icon or "fas fa-folder",
        display_order=data.display_order or 0,
        is_visible=data.is_active if data.is_active is not None else True
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return {
        "message": "Kategori oluşturuldu",
        "category": {
            "id": category.id,
            "name": category.name,
            "slug": category.slug
        }
    }


@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Kategori güncelle"""
    category = db.query(ForumCategory).filter(ForumCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")
    
    # Güncelleme yap
    if data.name is not None:
        # Aynı isimde başka kategori var mı?
        existing = db.query(ForumCategory).filter(
            ForumCategory.name == data.name,
            ForumCategory.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Bu isimde bir kategori zaten var")
        category.name = data.name
    
    if data.slug is not None:
        slug = ensure_unique_slug(db, data.slug, exclude_id=category_id)
        category.slug = slug
    elif data.name is not None and not data.slug:
        # İsim değişti ama slug verilmedi, yeni slug oluştur
        slug = generate_slug(data.name)
        category.slug = ensure_unique_slug(db, slug, exclude_id=category_id)
    
    if data.description is not None:
        category.description = data.description
    
    if data.icon is not None:
        category.icon = data.icon
    
    if data.display_order is not None:
        category.display_order = data.display_order
    
    if data.is_active is not None:
        category.is_visible = data.is_active
    
    db.commit()
    db.refresh(category)
    
    return {
        "message": "Kategori güncellendi",
        "category": {
            "id": category.id,
            "name": category.name,
            "slug": category.slug
        }
    }


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Kategori sil"""
    category = db.query(ForumCategory).filter(ForumCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")
    
    # Kategoride konu var mı kontrol
    topic_count = db.query(func.count(ForumTopic.id)).filter(
        ForumTopic.category_id == category_id
    ).scalar() or 0
    
    if topic_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Bu kategoride {topic_count} konu var. Önce konuları silin veya taşıyın."
        )
    
    db.delete(category)
    db.commit()
    
    return {"message": "Kategori silindi"}


@router.post("/categories/reorder")
async def reorder_categories(
    order: list[dict],  # [{"id": 1, "display_order": 0}, ...]
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Kategorileri yeniden sırala"""
    for item in order:
        category = db.query(ForumCategory).filter(ForumCategory.id == item["id"]).first()
        if category:
            category.display_order = item["display_order"]
    
    db.commit()
    return {"message": "Sıralama güncellendi"}
