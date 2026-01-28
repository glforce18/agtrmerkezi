"""
AGTR Merkezi v6.1 - Command Quotas API
View daily command usage quotas
"""

import logging
from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import User
from app.services.command_quota_service import COMMAND_DAILY_LIMITS, CommandQuotaService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/command-quotas", tags=["Command Quotas"])


# ============================================
# Response Models
# ============================================


class QuotaUsageResponse(BaseModel):
    """Single command quota usage"""

    command_type: str
    limited: bool
    daily_limit: int | None = None
    used_today: int | None = None
    remaining: int | None = None
    quota_date: str | None = None
    resets_at_utc: str | None = None


class AllQuotasResponse(BaseModel):
    """All command quotas for user"""

    user_id: int
    quotas: Dict[str, QuotaUsageResponse]


class QuotaLimitsResponse(BaseModel):
    """Quota limits configuration"""

    limits: Dict[str, int]


# ============================================
# API Endpoints
# ============================================


@router.get("/usage", response_model=AllQuotasResponse)
async def get_all_quota_usage(
    current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)
):
    """
    Get current daily quota usage for all command types.

    Returns usage stats for:
    - ban (50/day)
    - kick (200/day)
    - restart (20/day)
    - changelevel (50/day)
    - rcon_command (500/day)

    **Resets:** Daily at midnight UTC
    """
    service = CommandQuotaService(db)
    usage = service.get_all_quota_usage(current_user.id)

    # Convert to response format
    quotas = {}
    for cmd_type, stats in usage.items():
        quotas[cmd_type] = QuotaUsageResponse(**stats)

    return AllQuotasResponse(user_id=current_user.id, quotas=quotas)


@router.get("/usage/{command_type}", response_model=QuotaUsageResponse)
async def get_specific_quota_usage(
    command_type: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get quota usage for specific command type.

    **Args:**
    - command_type: One of ban, kick, restart, changelevel, rcon_command

    **Returns:**
    - Current usage stats for that command
    """
    service = CommandQuotaService(db)
    usage = service.get_quota_usage(current_user.id, command_type)

    return QuotaUsageResponse(**usage)


@router.get("/limits", response_model=QuotaLimitsResponse)
async def get_quota_limits():
    """
    Get daily quota limits for all command types (no auth required).

    Useful for displaying limits in UI.
    """
    return QuotaLimitsResponse(limits=COMMAND_DAILY_LIMITS)
