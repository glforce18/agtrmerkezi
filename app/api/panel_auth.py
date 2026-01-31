"""
AGTR Merkezi - Panel Authentication API
Public panel access with IP:PORT + panel password
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.connection import get_db
from app.models.database import GameServer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/panel", tags=["Panel Authentication"])


class PanelLoginRequest(BaseModel):
    """Panel login request"""

    server_id: int = Field(..., description="Server ID")
    panel_password: str = Field(..., min_length=1, description="Panel password")


class PanelLoginResponse(BaseModel):
    """Panel login response"""

    success: bool
    message: str
    token: str | None = None
    server_id: int | None = None
    server_name: str | None = None


@router.post("/auth", response_model=PanelLoginResponse)
async def panel_authenticate(data: PanelLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with panel password for public access

    Returns:
        - token: JWT token for panel access
        - server_id: Authenticated server ID
        - server_name: Server name
    """
    try:
        # Find server by ID
        server = db.query(GameServer).filter(GameServer.id == data.server_id).first()

        if not server:
            raise HTTPException(
                status_code=404,
                detail=f"Sunucu bulunamadı (ID: {data.server_id})",
            )

        # Check panel password
        if not server.panel_password:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Bu sunucu için panel erişimi aktif değil. "
                    "Sunucu sahibi ile iletişime geçin."
                ),
            )

        if server.panel_password != data.panel_password:
            logger.warning(f"Failed panel login attempt for server {server.id} ({server.name})")
            raise HTTPException(status_code=401, detail="Panel şifresi hatalı")

        # Create panel access token (limited scope - only for this server)
        token_data = {
            "sub": f"panel_{server.id}",  # Special panel user
            "server_id": server.id,
            "type": "panel",  # Mark as panel token
        }

        access_token = create_access_token(data=token_data, expires_delta=timedelta(hours=12))

        logger.info(f"Panel login successful for server {server.id} ({server.name})")

        return PanelLoginResponse(
            success=True,
            message="Panel girişi başarılı",
            token=access_token,
            server_id=server.id,
            server_name=server.name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Panel auth error: {e}")
        raise HTTPException(status_code=500, detail="Panel girişi başarısız")


@router.get("/servers")
async def get_panel_servers(db: Session = Depends(get_db)):
    """
    Get list of all servers with panel access enabled (public endpoint)

    Returns:
        List of servers with basic info for dropdown selection
    """
    try:
        # Only show servers with panel_password set
        servers = (
            db.query(GameServer)
            .filter(GameServer.panel_password.isnot(None))
            .order_by(GameServer.name)
            .all()
        )

        return {
            "servers": [
                {
                    "id": s.id,
                    "name": s.name,
                    "ip_address": s.ip_address,
                    "port": s.port,
                    "game_type": s.game_type.value if s.game_type else "unknown",
                    "display": f"{s.ip_address}:{s.port}",
                }
                for s in servers
            ]
        }

    except Exception as e:
        logger.error(f"Server list error: {e}")
        raise HTTPException(status_code=500, detail="Sunucu listesi alınamadı")
