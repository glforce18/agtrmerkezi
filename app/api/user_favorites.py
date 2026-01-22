"""
AGTR Merkezi - User Favorites API
Kullanici favori sunuculari
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import User, UserFavoriteServer

router = APIRouter(prefix="/user/favorites", tags=["User Favorites"])


# Pydantic Schemas
class FavoriteServerRequest(BaseModel):
    server_id: int
    server_ip: Optional[str] = None
    server_port: Optional[int] = None


@router.get("/servers")
async def get_favorite_servers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Kullanicinin favori sunucularini getir"""
    favorites = db.query(UserFavoriteServer).filter(
        UserFavoriteServer.user_id == current_user.id
    ).all()

    return {
        "server_ids": [f.server_id for f in favorites],
        "favorites": [
            {
                "id": f.id,
                "server_id": f.server_id,
                "server_ip": f.server_ip,
                "server_port": f.server_port,
                "created_at": f.created_at.isoformat() if f.created_at else None
            }
            for f in favorites
        ]
    }


@router.post("/server")
async def toggle_favorite_server(
    data: FavoriteServerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Favori sunucu ekle/kaldir (toggle)"""
    existing = db.query(UserFavoriteServer).filter(
        UserFavoriteServer.user_id == current_user.id,
        UserFavoriteServer.server_id == data.server_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"action": "removed", "message": "Favorilerden kaldirildi"}
    else:
        favorite = UserFavoriteServer(
            user_id=current_user.id,
            server_id=data.server_id,
            server_ip=data.server_ip,
            server_port=data.server_port
        )
        db.add(favorite)
        db.commit()
        return {"action": "added", "message": "Favorilere eklendi"}


@router.delete("/server/{server_id}")
async def remove_favorite_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Favori sunucu kaldir"""
    favorite = db.query(UserFavoriteServer).filter(
        UserFavoriteServer.user_id == current_user.id,
        UserFavoriteServer.server_id == server_id
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Favori bulunamadi")

    db.delete(favorite)
    db.commit()
    return {"message": "Favorilerden kaldirildi"}
