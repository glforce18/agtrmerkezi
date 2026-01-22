"""
Redis Connection Manager & Pub/Sub
Real-time messaging, caching, session management
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisManager:
    """Redis connection and pub/sub manager"""

    def __init__(self):
        self.redis: Optional[Redis] = None
        self.pubsub: Optional[aioredis.client.PubSub] = None
        self.subscribers: Dict[str, Callable] = {}
        self._listener_task: Optional[asyncio.Task] = None

    async def connect(self):
        """Connect to Redis"""
        try:
            # Build connection URL with optional password
            if settings.REDIS_PASSWORD:
                redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}"
            else:
                redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

            self.redis = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            await self.redis.ping()
            logger.info("Redis connected successfully")

            # Initialize pub/sub
            self.pubsub = self.redis.pubsub()

        except RedisError as e:
            logger.error(f"Redis connection error: {e}")
            self.redis = None

    async def disconnect(self):
        """Disconnect from Redis"""
        if self._listener_task:
            self._listener_task.cancel()

        if self.pubsub:
            await self.pubsub.close()

        if self.redis:
            await self.redis.close()
            logger.info("Redis disconnected")

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if not self.redis:
            return None
        try:
            return await self.redis.get(key)
        except RedisError as e:
            logger.error(f"Redis GET error: {e}")
            return None

    async def set(self, key: str, value: str, expire: Optional[int] = None, ttl: Optional[int] = None):
        """Set value in Redis. Accepts both 'expire' and 'ttl' parameters for compatibility."""
        if not self.redis:
            return
        try:
            # Use ttl if expire is not provided (for backward compatibility)
            expiration = expire if expire is not None else ttl
            await self.redis.set(key, value, ex=expiration)
        except RedisError as e:
            logger.error(f"Redis SET error: {e}")

    async def delete(self, key: str):
        """Delete key from Redis"""
        if not self.redis:
            return
        try:
            await self.redis.delete(key)
        except RedisError as e:
            logger.error(f"Redis DELETE error: {e}")

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis:
            return False
        try:
            return bool(await self.redis.exists(key))
        except RedisError as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False

    async def incr(self, key: str) -> int:
        """Increment counter"""
        if not self.redis:
            return 0
        try:
            return await self.redis.incr(key)
        except RedisError as e:
            logger.error(f"Redis INCR error: {e}")
            return 0

    async def expire(self, key: str, seconds: int):
        """Set key expiration"""
        if not self.redis:
            return
        try:
            await self.redis.expire(key, seconds)
        except RedisError as e:
            logger.error(f"Redis EXPIRE error: {e}")

    # ==================== PUB/SUB ====================

    async def publish(self, channel: str, message: dict):
        """Publish message to channel"""
        if not self.redis:
            return
        try:
            await self.redis.publish(channel, json.dumps(message))
        except RedisError as e:
            logger.error(f"Redis PUBLISH error: {e}")

    async def subscribe(self, channel: str, callback: Callable):
        """Subscribe to channel with callback"""
        if not self.pubsub:
            logger.error("PubSub not initialized")
            return

        try:
            await self.pubsub.subscribe(channel)
            self.subscribers[channel] = callback

            # Start listener if not running
            if not self._listener_task:
                self._listener_task = asyncio.create_task(self._listen())

            logger.info(f"Subscribed to Redis channel: {channel}")

        except RedisError as e:
            logger.error(f"Redis SUBSCRIBE error: {e}")

    async def unsubscribe(self, channel: str):
        """Unsubscribe from channel"""
        if not self.pubsub:
            return

        try:
            await self.pubsub.unsubscribe(channel)
            if channel in self.subscribers:
                del self.subscribers[channel]
            logger.info(f"Unsubscribed from Redis channel: {channel}")
        except RedisError as e:
            logger.error(f"Redis UNSUBSCRIBE error: {e}")

    async def _listen(self):
        """Listen for pub/sub messages"""
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    data = message["data"]

                    # Parse JSON
                    try:
                        payload = json.loads(data)
                    except json.JSONDecodeError:
                        payload = {"raw": data}

                    # Call subscriber callback
                    if channel in self.subscribers:
                        callback = self.subscribers[channel]
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(payload)
                            else:
                                callback(payload)
                        except Exception as e:
                            logger.error(f"Subscriber callback error: {e}")

        except asyncio.CancelledError:
            logger.info("Redis listener cancelled")
        except Exception as e:
            logger.error(f"Redis listener error: {e}")

    # ==================== CACHE HELPERS ====================

    async def cache_get(self, key: str) -> Optional[Any]:
        """Get and deserialize cached object"""
        data = await self.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None

    async def cache_set(self, key: str, value: Any, expire: int = 300):
        """Serialize and cache object (default 5 min TTL)"""
        try:
            data = json.dumps(value)
            await self.set(key, data, expire)
        except (TypeError, ValueError) as e:
            logger.error(f"Cache serialization error: {e}")

    # ==================== SESSION MANAGEMENT ====================

    async def set_online_user(self, user_id: int, metadata: dict = None):
        """Mark user as online"""
        key = f"online:user:{user_id}"
        data = metadata or {}
        data["user_id"] = user_id
        data["timestamp"] = asyncio.get_event_loop().time()
        await self.cache_set(key, data, expire=60)  # 60s TTL, needs refresh

    async def remove_online_user(self, user_id: int):
        """Mark user as offline"""
        await self.delete(f"online:user:{user_id}")

    async def get_online_users(self) -> list:
        """Get all online users"""
        if not self.redis:
            return []

        try:
            keys = await self.redis.keys("online:user:*")
            users = []
            for key in keys:
                data = await self.cache_get(key)
                if data:
                    users.append(data)
            return users
        except RedisError as e:
            logger.error(f"Get online users error: {e}")
            return []

    async def get_online_count(self) -> int:
        """Get count of online users"""
        if not self.redis:
            return 0
        try:
            keys = await self.redis.keys("online:user:*")
            return len(keys)
        except RedisError as e:
            logger.error(f"Get online count error: {e}")
            return 0

    # ==================== RATE LIMITING ====================

    async def rate_limit_check(self, key: str, limit: int, window: int) -> bool:
        """
        Check rate limit (sliding window)
        Returns True if allowed, False if rate limited
        """
        if not self.redis:
            return True

        try:
            count = await self.incr(key)

            if count == 1:
                await self.expire(key, window)

            return count <= limit
        except RedisError as e:
            logger.error(f"Rate limit error: {e}")
            return True  # Fail open

    # ==================== LEADERBOARD ====================

    async def zadd(self, key: str, mapping: dict):
        """Add to sorted set (leaderboard)"""
        if not self.redis:
            return
        try:
            await self.redis.zadd(key, mapping)
        except RedisError as e:
            logger.error(f"Redis ZADD error: {e}")

    async def zrange(self, key: str, start: int, end: int, desc: bool = True) -> list:
        """Get range from sorted set"""
        if not self.redis:
            return []
        try:
            return await self.redis.zrange(
                key, start, end,
                desc=desc,
                withscores=True
            )
        except RedisError as e:
            logger.error(f"Redis ZRANGE error: {e}")
            return []

    async def zincrby(self, key: str, amount: float, member: str):
        """Increment score in sorted set"""
        if not self.redis:
            return
        try:
            await self.redis.zincrby(key, amount, member)
        except RedisError as e:
            logger.error(f"Redis ZINCRBY error: {e}")


# Global instance
redis_manager = RedisManager()


# ==================== REDIS CHANNELS ====================

# Channel names for pub/sub
class RedisChannels:
    SERVER_UPDATES = "server:updates"
    USER_ACTIVITY = "user:activity"
    CHAT_GLOBAL = "chat:global"
    NOTIFICATIONS = "notifications"
    LEADERBOARD_UPDATE = "leaderboard:update"
    ADMIN_BROADCAST = "admin:broadcast"


# ==================== CONVENIENCE FUNCTIONS ====================

async def publish_server_update(server_id: int, event: str, data: dict = None):
    """Publish server update event"""
    message = {
        "server_id": server_id,
        "event": event,
        "data": data or {},
        "timestamp": asyncio.get_event_loop().time()
    }
    await redis_manager.publish(RedisChannels.SERVER_UPDATES, message)


async def publish_user_activity(user_id: int, activity: str, metadata: dict = None):
    """Publish user activity"""
    message = {
        "user_id": user_id,
        "activity": activity,
        "metadata": metadata or {},
        "timestamp": asyncio.get_event_loop().time()
    }
    await redis_manager.publish(RedisChannels.USER_ACTIVITY, message)


async def publish_notification(user_id: int, notification: dict):
    """Publish notification to user"""
    message = {
        "user_id": user_id,
        "notification": notification,
        "timestamp": asyncio.get_event_loop().time()
    }
    await redis_manager.publish(RedisChannels.NOTIFICATIONS, message)
