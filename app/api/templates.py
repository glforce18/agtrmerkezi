"""
AGTR Merkezi v6.2 - Template Cache API
Admin endpoints for managing template caches
"""

import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import User, UserRole
from app.services.template_cache_service import TemplateCacheService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/templates", tags=["Template Cache"])


# ============================================
# Response Models
# ============================================


class TemplateCacheResponse(BaseModel):
    """Single template cache info"""

    mod_type: str
    template_name: str
    version: str | None
    file_size_mb: float | None
    checksum: str | None
    is_active: bool
    last_updated: str | None
    last_validated: str | None


class TemplateCacheListResponse(BaseModel):
    """List of all cached templates"""

    templates: List[Dict]
    stats: Dict


class CacheStatsResponse(BaseModel):
    """Cache statistics"""

    total_templates: int
    active_templates: int
    total_size_mb: float
    cache_directory: str


class CacheOperationResponse(BaseModel):
    """Cache operation result"""

    success: bool
    message: str
    mod_type: str | None = None


# ============================================
# Helper Functions
# ============================================


def require_admin(current_user: User = Depends(get_current_user_required)):
    """Require admin role"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(403, "Admin access required")
    return current_user


# ============================================
# API Endpoints
# ============================================


@router.get("/cache", response_model=TemplateCacheListResponse)
async def get_all_cached_templates(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    """
    Get all cached templates (Admin only).

    Returns list of all template caches with metadata and overall stats.
    """
    service = TemplateCacheService(db)

    templates = service.get_all_cached_templates()
    stats = service.get_cache_stats()

    return TemplateCacheListResponse(templates=templates, stats=stats)


@router.get("/cache/{mod_type}", response_model=TemplateCacheResponse)
async def get_template_cache_info(
    mod_type: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get cache info for specific mod type (Admin only).

    Args:
        mod_type: Mod type (ag, cs16, hldm, etc.)

    Returns:
        Template cache metadata
    """
    service = TemplateCacheService(db)

    cache_info = service.get_cache_info(mod_type)

    if not cache_info:
        raise HTTPException(404, f"No cache found for mod type: {mod_type}")

    return TemplateCacheResponse(**cache_info)


@router.post("/cache/{mod_type}/update", response_model=CacheOperationResponse)
async def update_template_cache(
    mod_type: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Manually update/cache a specific template (Admin only).

    Creates or updates the cache archive for the specified mod type.

    Args:
        mod_type: Mod type to cache

    Returns:
        Operation result
    """
    service = TemplateCacheService(db)

    success, message = await service.cache_template(mod_type)

    if not success:
        raise HTTPException(500, message)

    return CacheOperationResponse(success=True, message=message, mod_type=mod_type)


@router.post("/cache/update-all", response_model=Dict)
async def update_all_template_caches(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    """
    Update all template caches (Admin only).

    Recreates cache archives for all defined templates.

    **Warning:** This operation can take several minutes.

    Returns:
        Operation results for each template
    """
    from app.services.template_cache_service import update_template_caches

    result = await update_template_caches(db)

    return result


@router.post("/cache/{mod_type}/validate", response_model=CacheOperationResponse)
async def validate_template_cache(
    mod_type: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Validate template cache (Admin only).

    Checks if cache file exists and checksum matches.

    Args:
        mod_type: Mod type to validate

    Returns:
        Validation result
    """
    service = TemplateCacheService(db)

    is_valid, message = service.validate_cache(mod_type)

    return CacheOperationResponse(success=is_valid, message=message, mod_type=mod_type)


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    """
    Get overall cache statistics (Admin only).

    Returns:
        Total templates, active count, total size, cache directory
    """
    service = TemplateCacheService(db)

    stats = service.get_cache_stats()

    return CacheStatsResponse(**stats)
