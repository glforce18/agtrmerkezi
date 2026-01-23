"""
Enhanced WebSocket Manager
Real-time connections with Redis pub/sub integration
"""

import asyncio
import json
import logging
import time
from typing import Callable, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

from app.core.redis_manager import RedisChannels, redis_manager

logger = logging.getLogger(__name__)


class EnhancedConnectionManager:
    """Enhanced WebSocket connection manager with Redis pub/sub"""

    def __init__(self):
        # endpoint -> set of websockets
        self.connections: Dict[str, Set[WebSocket]] = {}

        # websocket -> user_id (authenticated users)
        self.authenticated: Dict[WebSocket, int] = {}

        # websocket -> metadata (connection info)
        self.metadata: Dict[WebSocket, dict] = {}

        # room_id -> set of websockets (for chat rooms)
        self.rooms: Dict[str, Set[WebSocket]] = {}

        # Heartbeat tracking
        self.last_heartbeat: Dict[WebSocket, float] = {}

        # Redis pub/sub subscribed
        self._redis_subscribed = False

    async def connect(self, websocket: WebSocket, endpoint: str, metadata: dict = None):
        """Accept WebSocket connection"""
        await websocket.accept()

        if endpoint not in self.connections:
            self.connections[endpoint] = set()

        self.connections[endpoint].add(websocket)
        self.metadata[websocket] = metadata or {}
        self.metadata[websocket]["endpoint"] = endpoint
        self.metadata[websocket]["connected_at"] = time.time()
        self.last_heartbeat[websocket] = time.time()

        logger.info(f"WebSocket connected: {endpoint} (total: {len(self.connections[endpoint])})")

        # Subscribe to Redis channels if not already
        if not self._redis_subscribed:
            await self._subscribe_redis_channels()

    def disconnect(self, websocket: WebSocket, endpoint: str):
        """Disconnect WebSocket"""
        if endpoint in self.connections:
            self.connections[endpoint].discard(websocket)

        if websocket in self.authenticated:
            user_id = self.authenticated[websocket]
            del self.authenticated[websocket]

            # Remove from online users
            asyncio.create_task(redis_manager.remove_online_user(user_id))

        if websocket in self.metadata:
            del self.metadata[websocket]

        if websocket in self.last_heartbeat:
            del self.last_heartbeat[websocket]

        # Remove from all rooms
        for room in self.rooms.values():
            room.discard(websocket)

        logger.info(f"WebSocket disconnected: {endpoint}")

    async def broadcast(self, endpoint: str, message: dict, exclude: Optional[WebSocket] = None):
        """Broadcast message to all connections on endpoint"""
        if endpoint not in self.connections:
            return

        disconnected = set()
        sent_count = 0

        for ws in self.connections[endpoint]:
            if ws == exclude:
                continue

            try:
                await ws.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                disconnected.add(ws)

        # Clean up disconnected
        for ws in disconnected:
            self.connections[endpoint].discard(ws)

        return sent_count

    async def send_to_user(self, user_id: int, message: dict) -> int:
        """Send message to specific authenticated user"""
        sent_count = 0

        for ws, uid in self.authenticated.items():
            if uid == user_id:
                try:
                    await ws.send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Send to user error: {e}")

        return sent_count

    async def broadcast_to_room(self, room_id: str, message: dict, exclude: Optional[WebSocket] = None):
        """Broadcast to all users in a room"""
        if room_id not in self.rooms:
            return 0

        sent_count = 0
        disconnected = set()

        for ws in self.rooms[room_id]:
            if ws == exclude:
                continue

            try:
                await ws.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Room broadcast error: {e}")
                disconnected.add(ws)

        # Clean up
        for ws in disconnected:
            self.rooms[room_id].discard(ws)

        return sent_count

    def join_room(self, websocket: WebSocket, room_id: str):
        """Join a chat room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()

        self.rooms[room_id].add(websocket)

        if websocket in self.metadata:
            self.metadata[websocket]["room"] = room_id

        logger.info(f"User joined room: {room_id} (total: {len(self.rooms[room_id])})")

    def leave_room(self, websocket: WebSocket, room_id: str):
        """Leave a chat room"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(websocket)

        if websocket in self.metadata and self.metadata[websocket].get("room") == room_id:
            self.metadata[websocket]["room"] = None

    def authenticate(self, websocket: WebSocket, user_id: int):
        """Authenticate WebSocket connection"""
        self.authenticated[websocket] = user_id

        if websocket in self.metadata:
            self.metadata[websocket]["user_id"] = user_id

        # Mark user as online in Redis
        asyncio.create_task(redis_manager.set_online_user(user_id))

    def update_heartbeat(self, websocket: WebSocket):
        """Update last heartbeat timestamp"""
        self.last_heartbeat[websocket] = time.time()

    def get_connection_count(self, endpoint: str = None) -> int:
        """Get connection count"""
        if endpoint:
            return len(self.connections.get(endpoint, set()))

        return sum(len(conns) for conns in self.connections.values())

    def get_authenticated_count(self) -> int:
        """Get authenticated user count"""
        return len(self.authenticated)

    def get_room_count(self, room_id: str) -> int:
        """Get room member count"""
        return len(self.rooms.get(room_id, set()))

    async def cleanup_stale_connections(self, timeout: int = 120):
        """Clean up stale connections (no heartbeat)"""
        now = time.time()
        stale = []

        for ws, last_beat in self.last_heartbeat.items():
            if now - last_beat > timeout:
                stale.append(ws)

        for ws in stale:
            endpoint = self.metadata.get(ws, {}).get("endpoint")
            if endpoint:
                self.disconnect(ws, endpoint)

            try:
                await ws.close()
            except Exception as e:
                logger.debug(f"Error closing stale WebSocket connection: {e}")

        if stale:
            logger.info(f"Cleaned up {len(stale)} stale connections")

    # ==================== REDIS PUB/SUB INTEGRATION ====================

    async def _subscribe_redis_channels(self):
        """Subscribe to Redis channels for cross-server broadcasting"""
        try:
            await redis_manager.subscribe(
                RedisChannels.SERVER_UPDATES,
                self._handle_server_update
            )

            await redis_manager.subscribe(
                RedisChannels.NOTIFICATIONS,
                self._handle_notification
            )

            await redis_manager.subscribe(
                RedisChannels.USER_ACTIVITY,
                self._handle_user_activity
            )

            await redis_manager.subscribe(
                RedisChannels.ADMIN_BROADCAST,
                self._handle_admin_broadcast
            )

            self._redis_subscribed = True
            logger.info("Subscribed to Redis channels for WebSocket broadcasting")

        except Exception as e:
            logger.error(f"Redis subscription error: {e}")

    async def _handle_server_update(self, message: dict):
        """Handle server update from Redis"""
        server_id = message.get("server_id")
        event = message.get("event")
        data = message.get("data", {})

        await self.broadcast("server-stats", {
            "type": "server_update",
            "server_id": server_id,
            "event": event,
            "data": data
        })

        await self.broadcast("dashboard", {
            "type": "server_update",
            "server_id": server_id,
            "event": event
        })

    async def _handle_notification(self, message: dict):
        """Handle notification from Redis"""
        user_id = message.get("user_id")
        notification = message.get("notification")

        if user_id and notification:
            await self.send_to_user(user_id, {
                "type": "notification",
                **notification
            })

    async def _handle_user_activity(self, message: dict):
        """Handle user activity from Redis"""
        await self.broadcast("activity", {
            "type": "user_activity",
            **message
        })

    async def _handle_admin_broadcast(self, message: dict):
        """Handle admin broadcast from Redis"""
        await self.broadcast("dashboard", {
            "type": "admin_broadcast",
            **message
        })

        # Also broadcast to all endpoints
        for endpoint in self.connections.keys():
            await self.broadcast(endpoint, {
                "type": "admin_broadcast",
                **message
            })

    # ==================== STATISTICS ====================

    def get_stats(self) -> dict:
        """Get WebSocket statistics"""
        return {
            "total_connections": self.get_connection_count(),
            "authenticated_users": self.get_authenticated_count(),
            "endpoints": {
                endpoint: len(conns)
                for endpoint, conns in self.connections.items()
            },
            "rooms": {
                room_id: len(members)
                for room_id, members in self.rooms.items()
            }
        }


# Global instance
connection_manager = EnhancedConnectionManager()


# ==================== HEARTBEAT TASK ====================

async def heartbeat_cleanup_task():
    """Background task to clean up stale connections"""
    while True:
        try:
            await asyncio.sleep(60)  # Every 60 seconds
            await connection_manager.cleanup_stale_connections()
        except Exception as e:
            logger.error(f"Heartbeat cleanup error: {e}")


# ==================== HELPER FUNCTIONS ====================

async def broadcast_server_event(server_id: int, event: str, data: dict = None):
    """Broadcast server event to all connected clients"""
    await connection_manager.broadcast("server-stats", {
        "type": "server_event",
        "server_id": server_id,
        "event": event,
        "data": data or {},
        "timestamp": time.time()
    })


async def broadcast_notification_to_user(user_id: int, notification: dict):
    """Send notification to specific user"""
    await connection_manager.send_to_user(user_id, {
        "type": "notification",
        **notification,
        "timestamp": time.time()
    })


async def broadcast_global_message(message: str, level: str = "info"):
    """Broadcast global message to all users"""
    for endpoint in connection_manager.connections.keys():
        await connection_manager.broadcast(endpoint, {
            "type": "global_message",
            "message": message,
            "level": level,
            "timestamp": time.time()
        })
