# ============================================
# AGTR v6.0 - Pages Content Admin API
# Dosya: app/api/admin/pages.py
# ============================================

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import PageContent, User

router = APIRouter(prefix="/api/admin/pages", tags=["admin-pages"])


# ============ Pydantic Schemas ============

class PageCreate(BaseModel):
    page_slug: str
    section_slug: str
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    background_image_url: Optional[str] = None
    cta_text: Optional[str] = None
    cta_link: Optional[str] = None
    settings: Optional[dict] = None
    display_order: Optional[int] = 0
    is_active: Optional[bool] = True


class PageUpdate(BaseModel):
    page_slug: Optional[str] = None
    section_slug: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    background_image_url: Optional[str] = None
    cta_text: Optional[str] = None
    cta_link: Optional[str] = None
    settings: Optional[dict] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


# ============ API Endpoints ============

@router.get("")
async def get_pages(
    page_slug: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Tüm sayfa içeriklerini getir"""
    query = db.query(PageContent)

    if page_slug:
        query = query.filter(PageContent.page_slug == page_slug)

    pages = query.order_by(PageContent.page_slug, PageContent.display_order).all()

    return {
        "pages": [
            {
                "id": p.id,
                "page_slug": p.page_slug,
                "section_slug": p.section_slug,
                "title": p.title,
                "subtitle": p.subtitle,
                "content": p.content,
                "image_url": p.image_url,
                "background_image_url": p.background_image_url,
                "cta_text": p.cta_text,
                "cta_link": p.cta_link,
                "settings": p.settings,
                "display_order": p.display_order,
                "is_active": p.is_active,
                "icon": "file-text",
                "icon_class": "default",
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None
            }
            for p in pages
        ]
    }


@router.get("/{page_id}")
async def get_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Tek sayfa içeriği getir"""
    page = db.query(PageContent).filter(PageContent.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Sayfa bulunamadı")

    return {
        "id": page.id,
        "page_slug": page.page_slug,
        "section_slug": page.section_slug,
        "title": page.title,
        "subtitle": page.subtitle,
        "content": page.content,
        "image_url": page.image_url,
        "background_image_url": page.background_image_url,
        "cta_text": page.cta_text,
        "cta_link": page.cta_link,
        "settings": page.settings,
        "display_order": page.display_order,
        "is_active": page.is_active
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_page(
    data: PageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Yeni sayfa içeriği oluştur"""
    # Aynı slug kombinasyonu var mı kontrol
    existing = db.query(PageContent).filter(
        PageContent.page_slug == data.page_slug,
        PageContent.section_slug == data.section_slug
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Bu sayfa ve bölüm kombinasyonu zaten mevcut"
        )

    page = PageContent(
        page_slug=data.page_slug,
        section_slug=data.section_slug,
        title=data.title,
        subtitle=data.subtitle,
        content=data.content,
        image_url=data.image_url,
        background_image_url=data.background_image_url,
        cta_text=data.cta_text,
        cta_link=data.cta_link,
        settings=data.settings or {},
        display_order=data.display_order or 0,
        is_active=data.is_active if data.is_active is not None else True,
        updated_by=current_user.id
    )

    db.add(page)
    db.commit()
    db.refresh(page)

    return {"message": "Sayfa içeriği oluşturuldu", "id": page.id}


@router.put("/{page_id}")
async def update_page(
    page_id: int,
    data: PageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Sayfa içeriği güncelle"""
    page = db.query(PageContent).filter(PageContent.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Sayfa bulunamadı")

    # Slug değişiyorsa çakışma kontrolü
    if data.page_slug or data.section_slug:
        new_page_slug = data.page_slug or page.page_slug
        new_section_slug = data.section_slug or page.section_slug

        existing = db.query(PageContent).filter(
            PageContent.page_slug == new_page_slug,
            PageContent.section_slug == new_section_slug,
            PageContent.id != page_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Bu sayfa ve bölüm kombinasyonu zaten mevcut"
            )

    # Güncelleme
    if data.page_slug is not None:
        page.page_slug = data.page_slug
    if data.section_slug is not None:
        page.section_slug = data.section_slug
    if data.title is not None:
        page.title = data.title
    if data.subtitle is not None:
        page.subtitle = data.subtitle
    if data.content is not None:
        page.content = data.content
    if data.image_url is not None:
        page.image_url = data.image_url
    if data.background_image_url is not None:
        page.background_image_url = data.background_image_url
    if data.cta_text is not None:
        page.cta_text = data.cta_text
    if data.cta_link is not None:
        page.cta_link = data.cta_link
    if data.settings is not None:
        page.settings = data.settings
    if data.display_order is not None:
        page.display_order = data.display_order
    if data.is_active is not None:
        page.is_active = data.is_active

    page.updated_by = current_user.id

    db.commit()

    return {"message": "Sayfa içeriği güncellendi"}


@router.delete("/{page_id}")
async def delete_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Sayfa içeriği sil"""
    page = db.query(PageContent).filter(PageContent.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Sayfa bulunamadı")

    db.delete(page)
    db.commit()

    return {"message": "Sayfa içeriği silindi"}
