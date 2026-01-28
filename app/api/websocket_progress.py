"""
AGTR Merkezi v6.1 - Installation Progress WebSocket
Real-time server installation progress endpoint
"""

import logging
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.models.connection import get_db
from app.models.database import GameServer, User
from app.services.installation_progress import installation_progress_manager

logger = logging.getLogger(__name__)
router = APIRouter()


def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """
    Validate JWT token and get user.

    Args:
        token: JWT token string
        db: Database session

    Returns:
        User instance or None
    """
    try:
        payload = decode_token(token)
        if not payload:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        return user

    except Exception as e:
        logger.debug(f"Token validation failed: {e}")
        return None


def verify_server_access(server_id: int, user: User, db: Session) -> GameServer:
    """
    Verify user has access to server.

    Args:
        server_id: Server ID
        user: User instance
        db: Database session

    Returns:
        GameServer instance

    Raises:
        HTTPException: If server not found or access denied
    """
    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Check ownership (or admin access)
    if server.owner_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied to this server")

    return server


@router.websocket("/ws/servers/{server_id}/progress")
async def installation_progress_websocket(
    websocket: WebSocket,
    server_id: int,
    token: Optional[str] = Query(None, description="JWT authentication token"),
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time installation progress.

    **Authentication:** Required via query param `token`

    **URL:** `ws://localhost:8000/ws/servers/{server_id}/progress?token=YOUR_JWT`

    **Message Types:**
    - `connected`: Initial connection confirmation
    - `progress`: Progress update (stage, progress %, message)
    - `completed`: Installation completed successfully
    - `failed`: Installation failed
    - `error`: Error occurred

    **Example Message:**
    ```json
    {
        "type": "progress",
        "server_id": 123,
        "stage": "Downloading server files",
        "progress": 45,
        "message": "Downloading cs16 template (45 MB / 100 MB)"
    }
    ```

    **Usage (JavaScript):**
    ```javascript
    const ws = new WebSocket(`ws://localhost:8000/ws/servers/${serverId}/progress?token=${jwt}`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'progress') {
            updateProgressBar(data.progress);
            updateStatusText(data.stage);
        } else if (data.type === 'completed') {
            showSuccess(data.message);
        } else if (data.type === 'error') {
            showError(data.error);
        }
    };
    ```
    """
    # Validate token
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return

    user = get_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # Verify server access
    try:
        verify_server_access(server_id, user, db)
    except HTTPException as e:
        await websocket.close(code=1008, reason=e.detail)
        return

    # Connect to progress manager
    await installation_progress_manager.connect(websocket, server_id)

    try:
        # Keep connection alive and listen for client messages
        while True:
            try:
                # Receive messages from client (optional)
                data = await websocket.receive_text()
                logger.debug(f"Received from client for server {server_id}: {data}")

                # Client can send ping to keep connection alive
                if data == "ping":
                    await websocket.send_json({"type": "pong"})

            except WebSocketDisconnect:
                logger.info(f"Client disconnected from installation progress (server {server_id})")
                break

    except Exception as e:
        logger.error(f"WebSocket error for server {server_id}: {e}")

    finally:
        # Cleanup connection
        installation_progress_manager.disconnect(websocket)


@router.get("/api/servers/{server_id}/installation/progress")
async def get_installation_progress(
    server_id: int,
    db: Session = Depends(get_db),
):
    """
    Get current installation progress (HTTP fallback for polling).

    Use this as a fallback if WebSocket is not available.
    """
    from app.models.database import ServerInstallation

    installation = (
        db.query(ServerInstallation)
        .filter(ServerInstallation.server_id == server_id)
        .order_by(ServerInstallation.created_at.desc())
        .first()
    )

    if not installation:
        raise HTTPException(status_code=404, detail="No installation found for this server")

    return {
        "server_id": server_id,
        "status": installation.status.value,
        "progress": installation.progress_percent,
        "current_step": installation.current_step,
        "total_steps": installation.total_steps,
        "error_message": installation.error_message,
        "created_at": installation.created_at.isoformat() if installation.created_at else None,
        "started_at": installation.started_at.isoformat() if installation.started_at else None,
        "completed_at": (
            installation.completed_at.isoformat() if installation.completed_at else None
        ),
    }
