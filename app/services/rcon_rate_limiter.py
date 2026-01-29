"""
AGTR Merkezi - RCON Rate Limiter
Simple in-memory rate limiter for RCON commands
Per-endpoint rate limiting
"""

import logging
import time
from collections import defaultdict, deque
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================
# Rate Limit Configuration
# ============================================

# Endpoint-specific rate limits
# Format: {endpoint_name: {"limit": commands_per_window, "window": seconds}}
ENDPOINT_LIMITS = {
    "rcon_restart": {"limit": 10, "window": 3600},  # 10 per hour
    "rcon_kick": {"limit": 60, "window": 3600},  # 60 per hour
    "rcon_ban": {"limit": 30, "window": 3600},  # 30 per hour
    "rcon_command": {"limit": 100, "window": 3600},  # 100 per hour
    "rcon_status": {"limit": 300, "window": 3600},  # 300 per hour
}


class RconRateLimiter:
    """
    In-memory rate limiter for RCON commands

    Uses a sliding window algorithm with deque
    Supports per-endpoint rate limiting
    """

    def __init__(self):
        # {(user_id, endpoint): deque of timestamps}
        self.request_history = defaultdict(deque)

    def check_limit(
        self,
        user_id: int,
        endpoint: str,
        max_commands: Optional[int] = None,
        window_seconds: Optional[int] = None,
    ) -> Tuple[bool, int]:
        """
        Check if request is within rate limit

        Args:
            user_id: User ID
            endpoint: Endpoint name (e.g., "rcon_restart")
            max_commands: Maximum commands allowed in window (defaults from ENDPOINT_LIMITS)
            window_seconds: Time window in seconds (defaults from ENDPOINT_LIMITS)

        Returns:
            (is_allowed, wait_seconds)
            - is_allowed: True if request is allowed
            - wait_seconds: Seconds to wait before next request (0 if allowed)
        """
        # Get limits from config if not provided
        if endpoint in ENDPOINT_LIMITS:
            max_commands = max_commands or ENDPOINT_LIMITS[endpoint]["limit"]
            window_seconds = window_seconds or ENDPOINT_LIMITS[endpoint]["window"]
        else:
            # Default: 10 commands per minute
            max_commands = max_commands or 10
            window_seconds = window_seconds or 60

        key = (user_id, endpoint)
        now = time.time()
        cutoff = now - window_seconds

        # Get request history for this key
        history = self.request_history[key]

        # Remove old timestamps outside the window
        while history and history[0] < cutoff:
            history.popleft()

        # Check if limit exceeded
        if len(history) >= max_commands:
            # Calculate wait time
            oldest_request = history[0]
            wait_seconds = int(window_seconds - (now - oldest_request)) + 1

            logger.warning(
                f"Rate limit exceeded: user={user_id}, endpoint={endpoint}, "
                f"commands={len(history)}/{max_commands}, wait={wait_seconds}s"
            )

            return False, wait_seconds

        # Add current timestamp
        history.append(now)

        return True, 0

    def get_current_usage(self, user_id: int, endpoint: str) -> Dict:
        """
        Get current rate limit usage for an endpoint

        Args:
            user_id: User ID
            endpoint: Endpoint name

        Returns:
            Dictionary with usage statistics
        """
        if endpoint not in ENDPOINT_LIMITS:
            return {
                "endpoint": endpoint,
                "limit": 0,
                "current": 0,
                "remaining": 0,
                "window": 0,
                "reset_in": 0,
            }

        config = ENDPOINT_LIMITS[endpoint]
        max_commands = config["limit"]
        window_seconds = config["window"]

        key = (user_id, endpoint)
        now = time.time()
        cutoff = now - window_seconds

        # Get request history
        history = self.request_history[key]

        # Remove old timestamps
        while history and history[0] < cutoff:
            history.popleft()

        current_count = len(history)
        remaining = max(0, max_commands - current_count)

        # Calculate reset time
        reset_in = 0
        if history:
            oldest_request = history[0]
            reset_in = int(window_seconds - (now - oldest_request)) + 1

        return {
            "endpoint": endpoint,
            "limit": max_commands,
            "current": current_count,
            "remaining": remaining,
            "window": window_seconds,
            "reset_in": reset_in,
        }


# Global rate limiter instance
rcon_rate_limiter = RconRateLimiter()


def check_rcon_rate_limit(
    user_id: int,
    endpoint: str,
    max_commands: Optional[int] = None,
    window_seconds: Optional[int] = None,
) -> Tuple[bool, int]:
    """
    Check RCON rate limit

    Args:
        user_id: User ID
        endpoint: Endpoint name
        max_commands: Optional override for max commands
        window_seconds: Optional override for window

    Returns:
        (is_allowed, wait_seconds)
    """
    return rcon_rate_limiter.check_limit(user_id, endpoint, max_commands, window_seconds)
