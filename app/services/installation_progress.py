"""
AGTR Merkezi v6.1 - Installation Progress Broadcaster
Real-time WebSocket progress updates for server installations
"""

import logging
from typing import Dict, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class InstallationProgressManager:
    """
    Manages WebSocket connections for installation progress updates.

    Broadcasts real-time progress to all clients watching a specific server installation.
    """

    def __init__(self):
        # server_id -> set of websockets
        self.connections: Dict[int, Set[WebSocket]] = {}
        # websocket -> server_id mapping
        self.ws_to_server: Dict[WebSocket, int] = {}

    async def connect(self, websocket: WebSocket, server_id: int):
        """
        Connect a WebSocket client to server installation updates.

        Args:
            websocket: WebSocket connection
            server_id: Server ID to watch
        """
        await websocket.accept()

        if server_id not in self.connections:
            self.connections[server_id] = set()

        self.connections[server_id].add(websocket)
        self.ws_to_server[websocket] = server_id

        logger.info(f"Client connected to installation progress for server {server_id}")

        # Send initial connection confirmation
        await self.send_to_client(
            websocket,
            {
                "type": "connected",
                "server_id": server_id,
                "message": "Connected to installation progress stream",
            },
        )

    def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket client.

        Args:
            websocket: WebSocket connection to disconnect
        """
        server_id = self.ws_to_server.get(websocket)

        if server_id and server_id in self.connections:
            self.connections[server_id].discard(websocket)

            # Cleanup empty sets
            if not self.connections[server_id]:
                del self.connections[server_id]

        if websocket in self.ws_to_server:
            del self.ws_to_server[websocket]

        logger.info(f"Client disconnected from installation progress (server {server_id})")

    async def send_to_client(self, websocket: WebSocket, message: dict):
        """
        Send message to a specific client.

        Args:
            websocket: WebSocket connection
            message: Message dict to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.debug(f"Failed to send to client: {e}")
            # Connection likely dead, will be cleaned up on disconnect

    async def broadcast_progress(
        self,
        server_id: int,
        stage: str,
        progress: int,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ):
        """
        Broadcast installation progress to all watching clients.

        Args:
            server_id: Server ID
            stage: Current installation stage
            progress: Progress percentage (0-100)
            message: Optional progress message
            error: Optional error message
        """
        if server_id not in self.connections:
            # No clients watching, skip
            return

        payload = {
            "type": "progress",
            "server_id": server_id,
            "stage": stage,
            "progress": progress,
        }

        if message:
            payload["message"] = message

        if error:
            payload["error"] = error
            payload["type"] = "error"

        # Broadcast to all clients watching this server
        # Copy set to avoid modification during iteration
        clients = list(self.connections[server_id])

        for websocket in clients:
            try:
                await websocket.send_json(payload)
            except Exception as e:
                logger.debug(f"Failed to broadcast to client: {e}")
                # Mark for cleanup
                self.disconnect(websocket)

        logger.debug(
            f"Broadcasted progress for server {server_id}: {stage} ({progress}%) to {len(clients)} clients"
        )

    async def broadcast_completion(self, server_id: int, success: bool, message: str):
        """
        Broadcast installation completion status.

        Args:
            server_id: Server ID
            success: Whether installation succeeded
            message: Completion message
        """
        if server_id not in self.connections:
            return

        payload = {
            "type": "completed" if success else "failed",
            "server_id": server_id,
            "success": success,
            "message": message,
            "progress": 100 if success else 0,
        }

        clients = list(self.connections[server_id])

        for websocket in clients:
            try:
                await websocket.send_json(payload)
            except Exception as e:
                logger.debug(f"Failed to broadcast completion: {e}")

        logger.info(
            f"Installation {'completed' if success else 'failed'} for server {server_id}: {message}"
        )

    def get_client_count(self, server_id: int) -> int:
        """
        Get number of clients watching a server installation.

        Args:
            server_id: Server ID

        Returns:
            Number of connected clients
        """
        return len(self.connections.get(server_id, set()))


# Global instance
installation_progress_manager = InstallationProgressManager()
