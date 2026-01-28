"""
AGTR Merkezi - Redis Manager with Fallback
High-availability Redis client with in-memory fallback
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import redis
from redis.exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


class RedisManager:
    """Redis client with automatic fallback to in-memory cache"""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        self.fallback_cache = {}  # In-memory fallback {key: (value, expiry)}
        self.is_redis_available = False

        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            self.is_redis_available = True
            logger.info("Redis connection successful")
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory fallback: {e}")
            self.is_redis_available = False

    def _cleanup_expired(self):
        """Remove expired keys from in-memory cache"""
        now = datetime.utcnow()
        expired_keys = [k for k, (v, exp) in self.fallback_cache.items() if exp and exp < now]
        for key in expired_keys:
            del self.fallback_cache[key]

    def get(self, key: str) -> Optional[str]:
        """Get value with fallback"""
        if self.is_redis_available:
            try:
                return self.redis_client.get(key)
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Redis get failed, using fallback: {e}")
                self.is_redis_available = False

        # Fallback to in-memory
        self._cleanup_expired()
        if key in self.fallback_cache:
            value, expiry = self.fallback_cache[key]
            if expiry is None or expiry > datetime.utcnow():
                return value
            else:
                del self.fallback_cache[key]
        return None

    def setex(self, key: str, seconds: int, value: str) -> bool:
        """Set with TTL with fallback"""
        if self.is_redis_available:
            try:
                self.redis_client.setex(key, seconds, value)
                return True
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Redis setex failed, using fallback: {e}")
                self.is_redis_available = False

        # Fallback to in-memory
        expiry = datetime.utcnow() + timedelta(seconds=seconds)
        self.fallback_cache[key] = (value, expiry)
        return True

    def incr(self, key: str) -> int:
        """Increment with fallback"""
        if self.is_redis_available:
            try:
                return self.redis_client.incr(key)
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Redis incr failed, using fallback: {e}")
                self.is_redis_available = False

        # Fallback to in-memory
        if key in self.fallback_cache:
            value, expiry = self.fallback_cache[key]
            if expiry and expiry < datetime.utcnow():
                # Expired, reset to 1
                new_value = 1
            else:
                new_value = int(value) + 1
            self.fallback_cache[key] = (str(new_value), expiry)
            return new_value
        else:
            self.fallback_cache[key] = ("1", None)
            return 1

    def ttl(self, key: str) -> int:
        """Get TTL with fallback"""
        if self.is_redis_available:
            try:
                return self.redis_client.ttl(key)
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Redis ttl failed, using fallback: {e}")
                self.is_redis_available = False

        # Fallback to in-memory
        if key in self.fallback_cache:
            value, expiry = self.fallback_cache[key]
            if expiry:
                remaining = (expiry - datetime.utcnow()).total_seconds()
                return int(max(0, remaining))
        return -1

    def ping(self) -> bool:
        """Health check"""
        if self.redis_client:
            try:
                self.redis_client.ping()
                self.is_redis_available = True
                return True
            except Exception:
                self.is_redis_available = False
        return False

    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "redis_available": self.is_redis_available,
            "fallback_keys": len(self.fallback_cache),
            "backend": "redis" if self.is_redis_available else "in-memory",
        }


# Global instance
redis_manager = None


def get_redis_manager() -> RedisManager:
    """Get global Redis manager instance"""
    global redis_manager
    if redis_manager is None:
        from app.core.config import settings

        # Build Redis URL from settings
        if settings.REDIS_PASSWORD:
            redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        else:
            redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

        redis_manager = RedisManager(redis_url)
    return redis_manager
