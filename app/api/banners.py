"""
AGTR Merkezi - Banner/Advertisement Management API
Profesyonel banner ve reklam yönetimi
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.security import get_current_admin, get_current_user_optional
from app.models.connection import get_db
from app.models.database import Banner, BannerPosition, BannerType, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/banners", tags=["Banners"])


# ==================== SCHEMAS ====================

class BannerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    type: str = "image"
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    html_content: Optional[str] = None
    link_url: Optional[str] = None
    link_target: str = "_self"
    link_text: Optional[str] = Field(None, max_length=100)
    position: str
    display_order: int = 0
    width: Optional[int] = None
    height: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True
    target_pages: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    is_advertisement: bool = False
    sponsor_name: Optional[str] = None
    sponsor_contact: Optional[str] = None


class BannerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    type: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    html_content: Optional[str] = None
    link_url: Optional[str] = None
    link_target: Optional[str] = None
    link_text: Optional[str] = None
    position: Optional[str] = None
    display_order: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    target_pages: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    is_advertisement: Optional[bool] = None
    sponsor_name: Optional[str] = None
    sponsor_contact: Optional[str] = None


class BannerResponse(BaseModel):
    id: int
    name: str
    title: Optional[str]
    description: Optional[str]
    type: str
    image_url: Optional[str]
    video_url: Optional[str]
    html_content: Optional[str]
    link_url: Optional[str]
    link_target: str
    link_text: Optional[str]
    position: str
    display_order: int
    width: Optional[int]
    height: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: bool
    target_pages: Optional[List[str]]
    target_roles: Optional[List[str]]
    impressions: int
    clicks: int
    is_advertisement: bool
    sponsor_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== ADMIN ENDPOINTS ====================

@router.post("/", response_model=BannerResponse)
async def create_banner(
    banner: BannerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Yeni banner oluştur (Admin)"""

    # Banner type enum'a çevir
    try:
        banner_type = BannerType[banner.type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Geçersiz banner türü")

    # Position enum'a çevir
    try:
        position = BannerPosition[banner.position.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Geçersiz banner pozisyonu")

    # Banner oluştur
    new_banner = Banner(
        name=banner.name,
        title=banner.title,
        description=banner.description,
        type=banner_type,
        image_url=banner.image_url,
        video_url=banner.video_url,
        html_content=banner.html_content,
        link_url=banner.link_url,
        link_target=banner.link_target,
        link_text=banner.link_text,
        position=position,
        display_order=banner.display_order,
        width=banner.width,
        height=banner.height,
        start_date=banner.start_date,
        end_date=banner.end_date,
        is_active=banner.is_active,
        target_pages=banner.target_pages,
        target_roles=banner.target_roles,
        is_advertisement=banner.is_advertisement,
        sponsor_name=banner.sponsor_name,
        sponsor_contact=banner.sponsor_contact,
        created_by=current_user.id
    )

    db.add(new_banner)
    db.commit()
    db.refresh(new_banner)

    logger.info(f"Banner oluşturuldu: {new_banner.name} (ID: {new_banner.id})")

    return new_banner


@router.get("/admin", response_model=List[BannerResponse])
async def get_all_banners_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
    position: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """Tüm bannerları listele (Admin)"""
    query = db.query(Banner)

    if position:
        try:
            pos = BannerPosition[position.upper()]
            query = query.filter(Banner.position == pos)
        except KeyError:
            pass

    if is_active is not None:
        query = query.filter(Banner.is_active == is_active)

    banners = query.order_by(Banner.position, Banner.display_order).all()
    return banners


@router.get("/admin/{banner_id}", response_model=BannerResponse)
async def get_banner_admin(
    banner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Tek banner detayı (Admin)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner bulunamadı")
    return banner


@router.put("/{banner_id}", response_model=BannerResponse)
async def update_banner(
    banner_id: int,
    banner_update: BannerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Banner güncelle (Admin)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner bulunamadı")

    # Güncelleme
    update_data = banner_update.model_dump(exclude_unset=True)

    # Enum'ları çevir
    if 'type' in update_data:
        try:
            update_data['type'] = BannerType[update_data['type'].upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail="Geçersiz banner türü")

    if 'position' in update_data:
        try:
            update_data['position'] = BannerPosition[update_data['position'].upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail="Geçersiz banner pozisyonu")

    for key, value in update_data.items():
        setattr(banner, key, value)

    db.commit()
    db.refresh(banner)

    logger.info(f"Banner güncellendi: {banner.name} (ID: {banner.id})")

    return banner


@router.delete("/{banner_id}")
async def delete_banner(
    banner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Banner sil (Admin)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner bulunamadı")

    db.delete(banner)
    db.commit()

    logger.info(f"Banner silindi: {banner.name} (ID: {banner_id})")

    return {"success": True, "message": "Banner silindi"}


# ==================== PUBLIC ENDPOINTS ====================

@router.get("/public/{position}", response_model=List[BannerResponse])
async def get_banners_by_position(
    position: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Belirli pozisyondaki aktif bannerları getir (Public)"""

    try:
        pos = BannerPosition[position.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Geçersiz pozisyon")

    now = datetime.utcnow()

    # Aktif, tarih aralığındaki bannerlar
    query = db.query(Banner).filter(
        and_(
            Banner.position == pos,
            Banner.is_active == True,
            or_(Banner.start_date == None, Banner.start_date <= now),
            or_(Banner.end_date == None, Banner.end_date >= now)
        )
    )

    # Kullanıcı rolüne göre filtrele
    # TODO: Role-based filtering eklenebilir

    banners = query.order_by(Banner.display_order).all()

    return banners


@router.post("/track/{banner_id}/impression")
async def track_impression(
    banner_id: int,
    db: Session = Depends(get_db)
):
    """Banner gösterimi kaydet"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if banner:
        banner.impressions += 1
        db.commit()
        return {"success": True}
    return {"success": False}


@router.post("/track/{banner_id}/click")
async def track_click(
    banner_id: int,
    db: Session = Depends(get_db)
):
    """Banner tıklaması kaydet"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if banner:
        banner.clicks += 1
        db.commit()
        return {"success": True, "link_url": banner.link_url}
    return {"success": False}


@router.get("/positions")
async def get_available_positions():
    """Mevcut banner pozisyonlarını listele"""
    return {
        "positions": [
            {"value": pos.value, "label": pos.value.replace("_", " ").title()}
            for pos in BannerPosition
        ]
    }


@router.get("/types")
async def get_available_types():
    """Mevcut banner türlerini listele"""
    return {
        "types": [
            {"value": t.value, "label": t.value.title()}
            for t in BannerType
        ]
    }
