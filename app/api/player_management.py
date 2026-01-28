"""
Player Management API
Advanced player search, history, notes, tags
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import GameServer, User
from app.services.player_management_service import player_management_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/players", tags=["Player Management"])


# ============================================
# Pydantic Schemas
# ============================================


class PlayerSearchRequest(BaseModel):
    """Player search request"""

    query: Optional[str] = None
    search_by: List[str] = Field(default=["name", "steam_id"], description="Search fields")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=500)


class PlayerNoteRequest(BaseModel):
    """Add player note request"""

    steam_id: str = Field(..., min_length=7, max_length=32)
    note: str = Field(..., min_length=1, max_length=2000)


class PlayerTagRequest(BaseModel):
    """Add player tag request"""

    steam_id: str = Field(..., min_length=7, max_length=32)
    tag: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#3b82f6", pattern="^#[0-9A-Fa-f]{6}$")


# ============================================
# Helper Functions
# ============================================


async def verify_server_ownership(server_id: int, user: User, db: Session) -> GameServer:
    """
    Verify user owns the server

    Admin/Superadmin kullanıcılar tüm sunuculara erişebilir
    """
    from app.models.database import UserRole

    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(404, "Server not found")

    # Admin bypass - admin kullanıcılar tüm sunuculara erişebilir
    if user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        return server

    # Normal kullanıcı - sadece kendi sunucusu
    if server.owner_id != user.id:
        raise HTTPException(403, "Access denied")

    return server


# ============================================
# API Endpoints
# ============================================


@router.post("/{server_id}/search")
async def search_players(
    server_id: int,
    request: PlayerSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Advanced player search"""
    await verify_server_ownership(server_id, current_user, db)

    players = await player_management_service.search_players(
        server_id=server_id,
        query=request.query,
        search_by=request.search_by,
        date_from=request.date_from,
        date_to=request.date_to,
        limit=request.limit,
        db=db,
    )

    return {"players": players, "count": len(players)}


@router.get("/{server_id}/analytics/{steam_id}")
async def get_player_analytics(
    server_id: int,
    steam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get detailed player analytics"""
    await verify_server_ownership(server_id, current_user, db)

    analytics = await player_management_service.get_player_analytics(
        server_id=server_id, steam_id=steam_id, db=db
    )

    if "error" in analytics:
        raise HTTPException(404, analytics["error"])

    return analytics


@router.post("/{server_id}/notes")
async def add_player_note(
    server_id: int,
    request: PlayerNoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Add note to player"""
    await verify_server_ownership(server_id, current_user, db)

    result = await player_management_service.add_player_note(
        server_id=server_id,
        steam_id=request.steam_id,
        note=request.note,
        admin_id=current_user.id,
        db=db,
    )

    if not result.get("success"):
        raise HTTPException(500, result.get("error", "Failed to add note"))

    return result


@router.get("/{server_id}/notes/{steam_id}")
async def get_player_notes(
    server_id: int,
    steam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get player notes"""
    await verify_server_ownership(server_id, current_user, db)

    notes = await player_management_service.get_player_notes(
        server_id=server_id, steam_id=steam_id, db=db
    )

    return {"notes": notes, "count": len(notes)}


@router.post("/{server_id}/tags")
async def add_player_tag(
    server_id: int,
    request: PlayerTagRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Add tag to player"""
    await verify_server_ownership(server_id, current_user, db)

    result = await player_management_service.add_player_tag(
        server_id=server_id,
        steam_id=request.steam_id,
        tag=request.tag,
        color=request.color,
        admin_id=current_user.id,
        db=db,
    )

    if not result.get("success"):
        raise HTTPException(500, result.get("error", "Failed to add tag"))

    return result


@router.get("/{server_id}/tags/{steam_id}")
async def get_player_tags(
    server_id: int,
    steam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Get player tags"""
    await verify_server_ownership(server_id, current_user, db)

    tags = await player_management_service.get_player_tags(
        server_id=server_id, steam_id=steam_id, db=db
    )

    return {"tags": tags, "count": len(tags)}


@router.delete("/{server_id}/tags/{tag_id}")
async def remove_player_tag(
    server_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Remove player tag"""
    await verify_server_ownership(server_id, current_user, db)

    result = await player_management_service.remove_player_tag(
        server_id=server_id, tag_id=tag_id, db=db
    )

    if not result.get("success"):
        raise HTTPException(500, result.get("error", "Failed to remove tag"))

    return result
