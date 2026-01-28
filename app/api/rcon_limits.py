"""
AGTR Merkezi v6.1 - RCON Rate Limit API
Endpoints for checking RCON rate limit usage
"""

import logging
from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user_required
from app.models.database import User
from app.services.rcon_rate_limiter import ENDPOINT_LIMITS, rcon_rate_limiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rcon", tags=["RCON Rate Limits"])


# ============================================
# Response Models
# ============================================


class RateLimitUsageResponse(BaseModel):
    """Single endpoint rate limit usage"""

    endpoint: str
    limit: int
    current: int
    remaining: int
    window: int
    reset_in: int


class AllRateLimitsResponse(BaseModel):
    """All RCON rate limits for user"""

    user_id: int
    limits: List[RateLimitUsageResponse]


# ============================================
# API Endpoints
# ============================================


@router.get("/limits", response_model=AllRateLimitsResponse)
async def get_rcon_rate_limits(current_user: User = Depends(get_current_user_required)):
    """
    Get current RCON rate limit usage for all endpoints.

    Returns usage statistics for:
    - rcon_restart (10/hour)
    - rcon_kick (60/hour)
    - rcon_ban (30/hour)
    - rcon_command (100/hour)
    - rcon_status (300/hour)
    """
    limits = []

    for endpoint in ENDPOINT_LIMITS.keys():
        usage = rcon_rate_limiter.get_current_usage(current_user.id, endpoint)
        if usage:
            limits.append(RateLimitUsageResponse(**usage))

    return AllRateLimitsResponse(user_id=current_user.id, limits=limits)


@router.get("/limits/{endpoint}", response_model=RateLimitUsageResponse)
async def get_specific_rcon_limit(
    endpoint: str, current_user: User = Depends(get_current_user_required)
):
    """
    Get rate limit usage for specific RCON endpoint.

    Args:
        endpoint: One of rcon_restart, rcon_kick, rcon_ban, rcon_command, rcon_status

    Returns:
        Current usage stats for that endpoint
    """
    if endpoint not in ENDPOINT_LIMITS:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail=f"Unknown endpoint. Valid: {list(ENDPOINT_LIMITS.keys())}",
        )

    usage = rcon_rate_limiter.get_current_usage(current_user.id, endpoint)

    return RateLimitUsageResponse(**usage)


@router.get("/limits/info/all", response_model=Dict[str, dict])
async def get_rcon_limit_info():
    """
    Get RCON rate limit configuration (no auth required).

    Returns limit and window for all RCON endpoints.
    Useful for displaying limits in UI.
    """
    return ENDPOINT_LIMITS
