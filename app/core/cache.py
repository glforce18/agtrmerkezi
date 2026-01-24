# ============================================
# AGTR v6.0 - Caching Layer
# Dosya: app/core/cache.py
# Redis-based caching with decorators and helpers
# ============================================

import functools
import hashlib
import json
import logging
from typing import Any, Callable, Optional, Union

from app.core.redis_manager import redis_manager

logger = logging.getLogger(__name__)


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a unique cache key from function arguments

    Args:
        prefix: Cache key prefix (e.g., "forum:topic")
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Unique cache key
    """
    # Create a string representation of args and kwargs
    key_parts = [prefix]

    # Add positional args
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            # For complex objects, use hash
            key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])

    # Add keyword args (sorted for consistency)
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool, type(None))):
            key_parts.append(f"{k}={v}")
        else:
            key_parts.append(f"{k}={hashlib.md5(str(v).encode()).hexdigest()[:8]}")

    return ":".join(key_parts)


def cache(
    ttl: int = 300,
    key_prefix: Optional[str] = None,
    key_builder: Optional[Callable] = None,
):
    """
    Decorator for caching function results in Redis

    Args:
        ttl: Time to live in seconds (default: 300 = 5 minutes)
        key_prefix: Custom cache key prefix (default: function name)
        key_builder: Custom function to generate cache key

    Example:
        @cache(ttl=60, key_prefix="forum:topic")
        async def get_topic(topic_id: int):
            return db.query(Topic).get(topic_id)
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                prefix = key_prefix or f"{func.__module__}:{func.__name__}"
                cache_key = generate_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            try:
                cached_value = await redis_manager.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning(f"Cache GET error: {e}")
                # Continue without cache on error

            # Cache miss - execute function
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            try:
                await redis_manager.set(cache_key, json.dumps(result), ttl)
            except Exception as e:
                logger.warning(f"Cache SET error: {e}")
                # Continue without caching on error

            return result

        # Add cache invalidation helper
        wrapper.invalidate = lambda *args, **kwargs: invalidate_cache(
            key_prefix or f"{func.__module__}:{func.__name__}", *args, **kwargs
        )

        return wrapper

    return decorator


async def get_cached(key: str, default: Any = None) -> Any:
    """
    Get value from cache

    Args:
        key: Cache key
        default: Default value if key not found

    Returns:
        Cached value or default
    """
    try:
        value = await redis_manager.get(key)
        if value is not None:
            return json.loads(value)
        return default
    except Exception as e:
        logger.warning(f"Cache GET error for key {key}: {e}")
        return default


async def set_cached(key: str, value: Any, ttl: int = 300) -> bool:
    """
    Set value in cache

    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        ttl: Time to live in seconds

    Returns:
        True if successful, False otherwise
    """
    try:
        await redis_manager.set(key, json.dumps(value), ttl)
        return True
    except Exception as e:
        logger.warning(f"Cache SET error for key {key}: {e}")
        return False


async def delete_cached(key: str) -> bool:
    """
    Delete value from cache

    Args:
        key: Cache key

    Returns:
        True if successful, False otherwise
    """
    try:
        await redis_manager.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache DELETE error for key {key}: {e}")
        return False


async def invalidate_cache(pattern: str, *args, **kwargs) -> int:
    """
    Invalidate cache keys matching a pattern

    Args:
        pattern: Cache key pattern (can use wildcards)
        *args, **kwargs: Arguments to generate specific keys

    Returns:
        Number of keys deleted

    Example:
        # Delete all topic caches
        await invalidate_cache("forum:topic:*")

        # Delete specific topic cache
        await invalidate_cache("forum:topic", topic_id=123)
    """
    try:
        if args or kwargs:
            # Generate specific key
            key = generate_cache_key(pattern, *args, **kwargs)
            await redis_manager.delete(key)
            return 1
        else:
            # Pattern-based deletion
            keys = await redis_manager.keys(pattern)
            if keys:
                await redis_manager.delete(*keys)
                return len(keys)
            return 0
    except Exception as e:
        logger.warning(f"Cache INVALIDATE error for pattern {pattern}: {e}")
        return 0


# ============ Specialized Cache Functions ============


async def cache_leaderboard(timeframe: str, limit: int, data: list, ttl: int = 300):
    """Cache leaderboard data"""
    key = f"forum:leaderboard:{timeframe}:{limit}"
    await set_cached(key, data, ttl)


async def get_cached_leaderboard(timeframe: str, limit: int) -> Optional[list]:
    """Get cached leaderboard"""
    key = f"forum:leaderboard:{timeframe}:{limit}"
    return await get_cached(key)


async def cache_popular_topics(category_id: Optional[int], limit: int, data: list, ttl: int = 60):
    """Cache popular topics"""
    key = f"forum:popular:{category_id or 'all'}:{limit}"
    await set_cached(key, data, ttl)


async def get_cached_popular_topics(category_id: Optional[int], limit: int) -> Optional[list]:
    """Get cached popular topics"""
    key = f"forum:popular:{category_id or 'all'}:{limit}"
    return await get_cached(key)


async def cache_trending_topics(hours: int, limit: int, data: list, ttl: int = 300):
    """Cache trending topics"""
    key = f"forum:trending:{hours}:{limit}"
    await set_cached(key, data, ttl)


async def get_cached_trending_topics(hours: int, limit: int) -> Optional[list]:
    """Get cached trending topics"""
    key = f"forum:trending:{hours}:{limit}"
    return await get_cached(key)


async def cache_category_stats(category_id: int, data: dict, ttl: int = 300):
    """Cache category statistics"""
    key = f"forum:category:stats:{category_id}"
    await set_cached(key, data, ttl)


async def get_cached_category_stats(category_id: int) -> Optional[dict]:
    """Get cached category stats"""
    key = f"forum:category:stats:{category_id}"
    return await get_cached(key)


async def invalidate_forum_cache(category_id: Optional[int] = None):
    """
    Invalidate all forum-related caches

    Args:
        category_id: If provided, only invalidate caches for this category
    """
    if category_id:
        patterns = [
            f"forum:category:{category_id}:*",
            f"forum:category:stats:{category_id}",
            f"forum:popular:{category_id}:*",
        ]
    else:
        patterns = [
            "forum:leaderboard:*",
            "forum:popular:*",
            "forum:trending:*",
            "forum:category:*",
        ]

    total_deleted = 0
    for pattern in patterns:
        deleted = await invalidate_cache(pattern)
        total_deleted += deleted

    logger.info(f"Invalidated {total_deleted} forum cache keys")
    return total_deleted


# ============ Cache Statistics ============


async def get_cache_stats() -> dict:
    """
    Get cache statistics

    Returns:
        Dict with cache stats (keys count, memory usage, hit rate, etc.)
    """
    try:
        # Get Redis info
        info = await redis_manager.info()

        # Count keys by pattern
        forum_keys = len(await redis_manager.keys("forum:*"))
        user_keys = len(await redis_manager.keys("user:*"))
        server_keys = len(await redis_manager.keys("server:*"))

        return {
            "total_keys": info.get("db0", {}).get("keys", 0) if "db0" in info else 0,
            "memory_used": info.get("used_memory_human", "unknown"),
            "hit_rate": info.get("keyspace_hit_rate", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "keys_by_namespace": {
                "forum": forum_keys,
                "user": user_keys,
                "server": server_keys,
            },
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": str(e)}


# ============ Bulk Operations ============


async def cache_multiple(items: dict, ttl: int = 300) -> int:
    """
    Cache multiple key-value pairs at once

    Args:
        items: Dict of {key: value} pairs
        ttl: Time to live in seconds

    Returns:
        Number of items successfully cached
    """
    count = 0
    for key, value in items.items():
        if await set_cached(key, value, ttl):
            count += 1
    return count


async def get_multiple(keys: list) -> dict:
    """
    Get multiple values from cache

    Args:
        keys: List of cache keys

    Returns:
        Dict of {key: value} for found keys
    """
    result = {}
    for key in keys:
        value = await get_cached(key)
        if value is not None:
            result[key] = value
    return result
