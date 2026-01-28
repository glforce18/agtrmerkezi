"""
AGTR Merkezi v6.1 - RCON Rate Limiting Service
Per-user, per-endpoint rate limiting for RCON operations
Prevents abuse of restart, kick, ban commands
"""

import logging
from typing import Optional, Tuple

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

# Redis client (initialized on import)
try:
    import redis

    redis_client = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info("RCON Rate Limiter using Redis backend")
except Exception as e:
    redis_client = None
    REDIS_AVAILABLE = False
    logger.warning(f"RCON Rate Limiter: Redis unavailable ({e}), using memory fallback")


# Endpoint-specific limits (requests/hour)
ENDPOINT_LIMITS = {
    "rcon_restart": {"limit": 10, "window": 3600},  # 10 restarts/hour
    "rcon_kick": {"limit": 60, "window": 3600},  # 60 kicks/hour
    "rcon_ban": {"limit": 30, "window": 3600},  # 30 bans/hour
    "rcon_command": {"limit": 100, "window": 3600},  # 100 generic commands/hour
    "rcon_status": {"limit": 300, "window": 3600},  # 300 status checks/hour
}


class RCONRateLimiter:
    """User-based rate limiting for RCON endpoints"""

    def __init__(self):
        self.redis = redis_client
        # Memory fallback
        self.memory_counters = {}  # {user_id:endpoint: (count, expire_time)}

    def classify_endpoint(self, path: str) -> Optional[str]:
        """
        Map URL path to rate limit category.

        Args:
            path: Request URL path

        Returns:
            Endpoint category or None if not rate limited
        """
        path_lower = path.lower()

        # Restart/action endpoints (most critical)
        if "rcon/restart" in path_lower or "/action" in path_lower:
            return "rcon_restart"

        # Kick player
        elif "rcon/kick" in path_lower or "/kick" in path_lower:
            return "rcon_kick"

        # Ban player
        elif "rcon/ban" in path_lower or "/ban" in path_lower:
            return "rcon_ban"

        # Status/query endpoints (less critical)
        elif "rcon/status" in path_lower or "/status" in path_lower:
            return "rcon_status"

        # Generic RCON command
        elif "rcon" in path_lower:
            return "rcon_command"

        # Not an RCON endpoint
        return None

    def check_rate_limit(self, user_id: int, endpoint: str) -> Tuple[bool, Optional[str]]:
        """
        Check if user has exceeded rate limit for endpoint.

        Args:
            user_id: User ID from JWT token
            endpoint: Endpoint category (from classify_endpoint)

        Returns:
            (is_limited, error_message)

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        if endpoint not in ENDPOINT_LIMITS:
            # Not a rate-limited endpoint
            return False, None

        config = ENDPOINT_LIMITS[endpoint]
        key = f"rcon_limit:{user_id}:{endpoint}"

        if REDIS_AVAILABLE:
            return self._check_redis(key, config, endpoint)
        else:
            return self._check_memory(key, config, endpoint)

    def _check_redis(self, key: str, config: dict, endpoint: str) -> Tuple[bool, Optional[str]]:
        """Check rate limit using Redis"""
        try:
            # Get current count
            current = self.redis.get(key)

            if current is None:
                # First request in window
                self.redis.setex(key, config["window"], 1)
                return False, None

            count = int(current)

            if count >= config["limit"]:
                # Rate limit exceeded
                ttl = self.redis.ttl(key)
                error_msg = (
                    f"Rate limit exceeded for {endpoint}. "
                    f"Limit: {config['limit']}/{config['window']}s. "
                    f"Try again in {ttl}s."
                )
                logger.warning(f"Rate limit exceeded: {key} ({count}/{config['limit']})")
                raise HTTPException(
                    status_code=429,
                    detail=error_msg,
                    headers={"Retry-After": str(ttl)},
                )

            # Increment counter
            self.redis.incr(key)
            return False, None

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Fallback to allowing request
            return False, None

    def _check_memory(self, key: str, config: dict, endpoint: str) -> Tuple[bool, Optional[str]]:
        """Check rate limit using in-memory fallback"""
        import time

        now = time.time()

        if key in self.memory_counters:
            count, expire_time = self.memory_counters[key]

            # Check if window expired
            if now >= expire_time:
                # Reset counter
                self.memory_counters[key] = (1, now + config["window"])
                return False, None

            # Check limit
            if count >= config["limit"]:
                remaining = int(expire_time - now)
                error_msg = (
                    f"Rate limit exceeded for {endpoint}. "
                    f"Limit: {config['limit']}/{config['window']}s. "
                    f"Try again in {remaining}s."
                )
                logger.warning(f"Rate limit exceeded (memory): {key} ({count}/{config['limit']})")
                raise HTTPException(
                    status_code=429,
                    detail=error_msg,
                    headers={"Retry-After": str(remaining)},
                )

            # Increment counter
            self.memory_counters[key] = (count + 1, expire_time)
        else:
            # First request
            self.memory_counters[key] = (1, now + config["window"])

        return False, None

    def get_current_usage(self, user_id: int, endpoint: str) -> dict:
        """
        Get current usage stats for user+endpoint.

        Args:
            user_id: User ID
            endpoint: Endpoint category

        Returns:
            Dict with limit, current, remaining, reset_in
        """
        if endpoint not in ENDPOINT_LIMITS:
            return {}

        config = ENDPOINT_LIMITS[endpoint]
        key = f"rcon_limit:{user_id}:{endpoint}"

        if REDIS_AVAILABLE:
            current = self.redis.get(key)
            current = int(current) if current else 0
            ttl = self.redis.ttl(key) if current > 0 else config["window"]
        else:
            import time

            now = time.time()
            if key in self.memory_counters:
                count, expire_time = self.memory_counters[key]
                if now >= expire_time:
                    current = 0
                    ttl = config["window"]
                else:
                    current = count
                    ttl = int(expire_time - now)
            else:
                current = 0
                ttl = config["window"]

        return {
            "endpoint": endpoint,
            "limit": config["limit"],
            "current": current,
            "remaining": max(0, config["limit"] - current),
            "window": config["window"],
            "reset_in": ttl,
        }


# Global instance
rcon_rate_limiter = RCONRateLimiter()


def get_user_id_from_token(request: Request) -> Optional[int]:
    """
    Extract user ID from JWT token.

    Args:
        request: FastAPI request

    Returns:
        User ID or None if not authenticated
    """
    try:
        # Check if user is attached to request (from dependency)
        if hasattr(request.state, "user"):
            return request.state.user.id

        # Fallback: extract from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.replace("Bearer ", "")

        # Decode JWT
        from app.core.security import decode_access_token

        payload = decode_access_token(token)
        if payload:
            return payload.get("user_id")

    except Exception as e:
        logger.debug(f"Failed to extract user_id from token: {e}")

    return None


async def check_rcon_rate_limit(request: Request) -> None:
    """
    Dependency for RCON endpoints to enforce rate limiting.

    Usage:
        @router.post("/servers/{id}/rcon/restart", dependencies=[Depends(check_rcon_rate_limit)])

    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    # Get user ID from JWT
    user_id = get_user_id_from_token(request)

    if not user_id:
        # Not authenticated, let auth middleware handle it
        return

    # Classify endpoint
    endpoint = rcon_rate_limiter.classify_endpoint(request.url.path)

    if not endpoint:
        # Not an RCON endpoint
        return

    # Check rate limit
    rcon_rate_limiter.check_rate_limit(user_id, endpoint)
