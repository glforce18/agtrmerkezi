"""
AGTR Merkezi - Admin Content API
Announcements, settings, and site configuration
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.common import NotFoundError, log_api_call, success_response
from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import Announcement, SiteSettings, User

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== REQUEST MODELS ====================


class AnnouncementCreateRequest(BaseModel):
    title: str
    content: str
    type: str = "info"
    show_on_homepage: bool = True


class AnnouncementUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None
    show_on_homepage: Optional[bool] = None


class SiteSettingsUpdateRequest(BaseModel):
    site_name: Optional[str] = None
    site_description: Optional[str] = None
    contact_email: Optional[str] = None
    discord_url: Optional[str] = None
    maintenance_mode: Optional[bool] = None
    registration_enabled: Optional[bool] = None
    price_per_slot: Optional[float] = None
    discount_3_month: Optional[float] = None
    discount_6_month: Optional[float] = None
    discount_12_month: Optional[float] = None
    # Branding
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None
    logo_mobile_url: Optional[str] = None
    logo_width: Optional[str] = None
    logo_height: Optional[str] = None
    logo_text: Optional[str] = None
    logo_subtitle: Optional[str] = None
    show_logo_text: Optional[bool] = None
    footer_logo_url: Optional[str] = None
    footer_logo_width: Optional[str] = None
    footer_logo_height: Optional[str] = None
    favicon_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None


class ThemeRequest(BaseModel):
    theme: str  # light, dark, or custom


# ==================== ANNOUNCEMENTS ====================


@router.get("/announcements", response_model=dict)
async def list_announcements(
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """List all announcements"""
    try:
        log_api_call("admin_list_announcements", admin.id)

        announcements = db.query(Announcement).order_by(desc(Announcement.created_at)).all()

        return success_response(
            data={
                "announcements": [
                    {
                        "id": a.id,
                        "title": a.title,
                        "content": a.content,
                        "type": a.type,
                        "is_active": a.is_active,
                        "show_on_homepage": a.show_on_homepage,
                        "created_at": a.created_at.isoformat() if a.created_at else None,
                    }
                    for a in announcements
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error listing announcements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/announcements")
async def create_announcement(
    data: AnnouncementCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Create new announcement"""
    try:
        announcement = Announcement(
            title=data.title,
            content=data.content,
            type=data.type,
            show_on_homepage=data.show_on_homepage,
        )
        db.add(announcement)
        db.commit()

        return success_response(
            message="Duyuru oluşturuldu", data={"announcement_id": announcement.id}
        )

    except Exception as e:
        logger.error(f"Error creating announcement: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/announcements/{announcement_id}")
async def update_announcement(
    announcement_id: int,
    data: AnnouncementUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update announcement"""
    try:
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not announcement:
            raise NotFoundError("Duyuru bulunamadı")

        if data.title is not None:
            announcement.title = data.title
        if data.content is not None:
            announcement.content = data.content
        if data.type is not None:
            announcement.type = data.type
        if data.is_active is not None:
            announcement.is_active = data.is_active
        if data.show_on_homepage is not None:
            announcement.show_on_homepage = data.show_on_homepage

        db.commit()
        return success_response(message="Duyuru güncellendi")

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error updating announcement: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """Delete announcement"""
    try:
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not announcement:
            raise NotFoundError("Duyuru bulunamadı")

        db.delete(announcement)
        db.commit()

        return success_response(message="Duyuru silindi")

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting announcement: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SETTINGS ====================


@router.get("/settings", response_model=dict)
async def get_settings(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Get site settings"""
    try:
        settings = db.query(SiteSettings).first()
        if not settings:
            raise NotFoundError("Site ayarları bulunamadı")

        return success_response(
            data={
                "settings": {
                    "site_name": settings.site_name,
                    "site_description": settings.site_description,
                    "contact_email": settings.contact_email,
                    "discord_url": settings.discord_url,
                    "maintenance_mode": settings.maintenance_mode,
                    "registration_enabled": settings.registration_enabled,
                    "price_per_slot": settings.price_per_slot,
                    "discount_3_month": settings.discount_3_month,
                    "discount_6_month": settings.discount_6_month,
                    "discount_12_month": settings.discount_12_month,
                    # Branding
                    "logo_url": settings.logo_url,
                    "logo_dark_url": settings.logo_dark_url,
                    "logo_mobile_url": settings.logo_mobile_url,
                    "logo_width": settings.logo_width,
                    "logo_height": settings.logo_height,
                    "logo_text": settings.logo_text,
                    "logo_subtitle": settings.logo_subtitle,
                    "show_logo_text": settings.show_logo_text,
                    "footer_logo_url": settings.footer_logo_url,
                    "footer_logo_width": settings.footer_logo_width,
                    "footer_logo_height": settings.footer_logo_height,
                    "favicon_url": settings.favicon_url,
                    "primary_color": settings.primary_color,
                    "secondary_color": settings.secondary_color,
                }
            }
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings")
async def update_settings(
    data: SiteSettingsUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update site settings"""
    try:
        settings = db.query(SiteSettings).first()
        if not settings:
            # Create default settings
            settings = SiteSettings(
                site_name="AGTR Merkezi", site_description="Half-Life & CS 1.6 Gaming Platform"
            )
            db.add(settings)

        # Update all provided fields
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(settings, field, value)

        db.commit()
        return success_response(message="Site ayarları güncellendi")

    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== THEME ====================


@router.get("/theme", response_model=dict)
async def get_theme(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Get current theme settings"""
    try:
        settings = db.query(SiteSettings).first()

        theme = {
            "primary_color": settings.primary_color if settings else "#f97316",
            "secondary_color": settings.secondary_color if settings else "#3b82f6",
            "mode": "dark",  # Default theme mode
        }

        return success_response(data={"theme": theme})

    except Exception as e:
        logger.error(f"Error getting theme: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/theme")
async def update_theme(
    data: ThemeRequest, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """Update theme settings"""
    try:
        # Theme updates can be stored in site settings or separate table
        # For now, just acknowledge the request
        return success_response(message="Tema güncellendi", data={"theme": data.theme})

    except Exception as e:
        logger.error(f"Error updating theme: {e}")
        raise HTTPException(status_code=500, detail=str(e))
