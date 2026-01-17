"""
Advanced Rate Limiting & IP Tracking
Redis-based distributed rate limiting with IP reputation and suspicious activity detection
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session

from app.core.redis_manager import redis_manager
from app.models.database import SecurityEvent

logger = logging.getLogger(__name__)


class EndpointType(str, Enum):
    """Endpoint types for rate limiting"""
    PUBLIC = "public"              # 100 req/min
    AUTH = "auth"                  # 10 req/min (login, register)
    API = "api"                    # 60 req/min
    ADMIN = "admin"                # 120 req/min
    WEBSOCKET = "websocket"        # 200 req/min
    UPLOAD = "upload"              # 5 req/min
    CRITICAL = "critical"          # 3 req/min (password reset, 2FA setup)


class RateLimitConfig:
    """Rate limit configuration per endpoint type"""

    LIMITS = {
        EndpointType.PUBLIC: {"requests": 100, "window": 60},      # 100/min
        EndpointType.AUTH: {"requests": 10, "window": 60},         # 10/min
        EndpointType.API: {"requests": 60, "window": 60},          # 60/min
        EndpointType.ADMIN: {"requests": 120, "window": 60},       # 120/min
        EndpointType.WEBSOCKET: {"requests": 200, "window": 60},   # 200/min
        EndpointType.UPLOAD: {"requests": 5, "window": 60},        # 5/min
        EndpointType.CRITICAL: {"requests": 3, "window": 60},      # 3/min
    }

    # Burst protection - max requests in 1 second
    BURST_LIMITS = {
        EndpointType.PUBLIC: 10,
        EndpointType.AUTH: 2,
        EndpointType.API: 5,
        EndpointType.ADMIN: 10,
        EndpointType.WEBSOCKET: 20,
        EndpointType.UPLOAD: 1,
        EndpointType.CRITICAL: 1,
    }

    # Penalties for violations
    BAN_THRESHOLD = 5           # Number of violations before temp ban
    BAN_DURATION = 3600         # 1 hour ban
    REPUTATION_DECAY = 86400    # 24 hours to reset reputation


class IPReputation:
    """IP reputation tracking"""

    @staticmethod
    def _get_reputation_key(ip: str) -> str:
        """Get Redis key for IP reputation"""
        return f"ip_reputation:{ip}"

    @staticmethod
    def _get_violation_key(ip: str) -> str:
        """Get Redis key for violations"""
        return f"ip_violations:{ip}"

    @staticmethod
    def _get_ban_key(ip: str) -> str:
        """Get Redis key for bans"""
        return f"ip_ban:{ip}"

    @staticmethod
    async def get_reputation(ip: str) -> int:
        """
        Get IP reputation score (0-100)
        100 = excellent, 0 = banned
        """
        key = IPReputation._get_reputation_key(ip)
        reputation = await redis_manager.get(key)

        if reputation is None:
            # New IP starts at 50
            await redis_manager.set(key, "50", ttl=RateLimitConfig.REPUTATION_DECAY)
            return 50

        return int(reputation)

    @staticmethod
    async def decrease_reputation(ip: str, amount: int = 10) -> int:
        """Decrease IP reputation"""
        current = await IPReputation.get_reputation(ip)
        new_reputation = max(0, current - amount)

        key = IPReputation._get_reputation_key(ip)
        await redis_manager.set(key, str(new_reputation), ttl=RateLimitConfig.REPUTATION_DECAY)

        logger.warning(f"IP {ip} reputation decreased to {new_reputation}")
        return new_reputation

    @staticmethod
    async def increase_reputation(ip: str, amount: int = 5) -> int:
        """Increase IP reputation (for good behavior)"""
        current = await IPReputation.get_reputation(ip)
        new_reputation = min(100, current + amount)

        key = IPReputation._get_reputation_key(ip)
        await redis_manager.set(key, str(new_reputation), ttl=RateLimitConfig.REPUTATION_DECAY)

        return new_reputation

    @staticmethod
    async def record_violation(ip: str) -> int:
        """Record rate limit violation"""
        key = IPReputation._get_violation_key(ip)
        violations = await redis_manager.incr(key)
        await redis_manager.expire(key, RateLimitConfig.REPUTATION_DECAY)

        # Decrease reputation
        await IPReputation.decrease_reputation(ip, amount=15)

        # Auto-ban if threshold exceeded
        if violations >= RateLimitConfig.BAN_THRESHOLD:
            await IPReputation.ban_ip(ip, duration=RateLimitConfig.BAN_DURATION)
            logger.critical(f"IP {ip} auto-banned after {violations} violations")

        return violations

    @staticmethod
    async def is_banned(ip: str) -> bool:
        """Check if IP is banned"""
        key = IPReputation._get_ban_key(ip)
        banned = await redis_manager.get(key)
        return banned is not None

    @staticmethod
    async def ban_ip(ip: str, duration: int = 3600, reason: str = "Rate limit violations"):
        """Ban IP address"""
        key = IPReputation._get_ban_key(ip)
        ban_data = {
            "reason": reason,
            "banned_at": datetime.utcnow().isoformat(),
            "duration": duration
        }

        await redis_manager.set(key, str(ban_data), ttl=duration)
        await IPReputation.decrease_reputation(ip, amount=50)

        logger.critical(f"IP {ip} banned for {duration}s: {reason}")

    @staticmethod
    async def unban_ip(ip: str):
        """Unban IP address"""
        key = IPReputation._get_ban_key(ip)
        await redis_manager.delete(key)

        # Reset reputation to neutral
        rep_key = IPReputation._get_reputation_key(ip)
        await redis_manager.set(rep_key, "50", ttl=RateLimitConfig.REPUTATION_DECAY)

        logger.info(f"IP {ip} unbanned")


class AdvancedRateLimiter:
    """Advanced rate limiter with IP tracking"""

    def __init__(self):
        self.whitelist: set = set()  # Whitelisted IPs
        self.blacklist: set = set()  # Permanently blacklisted IPs

    def _get_rate_limit_key(self, ip: str, endpoint_type: EndpointType) -> str:
        """Get Redis key for rate limiting"""
        return f"rate_limit:{endpoint_type.value}:{ip}"

    def _get_burst_key(self, ip: str, endpoint_type: EndpointType) -> str:
        """Get Redis key for burst protection"""
        return f"burst:{endpoint_type.value}:{ip}"

    async def check_rate_limit(
        self,
        ip: str,
        endpoint_type: EndpointType,
        increment: bool = True
    ) -> Dict[str, Any]:
        """
        Check rate limit for IP

        Returns:
            {
                "allowed": bool,
                "current": int,
                "limit": int,
                "remaining": int,
                "reset_at": int,
                "reputation": int
            }
        """
        # Check if whitelisted
        if ip in self.whitelist:
            return {
                "allowed": True,
                "current": 0,
                "limit": 999999,
                "remaining": 999999,
                "reset_at": 0,
                "reputation": 100
            }

        # Check if blacklisted
        if ip in self.blacklist or await IPReputation.is_banned(ip):
            return {
                "allowed": False,
                "current": 0,
                "limit": 0,
                "remaining": 0,
                "reset_at": 0,
                "reputation": 0
            }

        # Get configuration
        config = RateLimitConfig.LIMITS[endpoint_type]
        limit = config["requests"]
        window = config["window"]

        # Check burst protection (1 second window)
        burst_limit = RateLimitConfig.BURST_LIMITS[endpoint_type]
        burst_key = self._get_burst_key(ip, endpoint_type)
        burst_count = await redis_manager.get(burst_key)

        if burst_count and int(burst_count) >= burst_limit:
            logger.warning(f"Burst limit exceeded for {ip} on {endpoint_type.value}")
            await IPReputation.record_violation(ip)

            return {
                "allowed": False,
                "current": int(burst_count),
                "limit": burst_limit,
                "remaining": 0,
                "reset_at": 1,
                "reputation": await IPReputation.get_reputation(ip)
            }

        # Check main rate limit
        key = self._get_rate_limit_key(ip, endpoint_type)

        if increment:
            current = await redis_manager.incr(key)

            # Set expiry on first request
            if current == 1:
                await redis_manager.expire(key, window)

            # Increment burst counter
            await redis_manager.incr(burst_key)
            await redis_manager.expire(burst_key, 1)  # 1 second TTL
        else:
            count = await redis_manager.get(key)
            current = int(count) if count else 0

        # Check if limit exceeded
        allowed = current <= limit

        if not allowed and increment:
            # Record violation
            violations = await IPReputation.record_violation(ip)
            logger.warning(f"Rate limit exceeded for {ip} on {endpoint_type.value} (violation #{violations})")

        # Get TTL for reset time
        ttl = await redis_manager.ttl(key)
        reset_at = ttl if ttl > 0 else window

        # Get reputation
        reputation = await IPReputation.get_reputation(ip)

        return {
            "allowed": allowed,
            "current": current,
            "limit": limit,
            "remaining": max(0, limit - current),
            "reset_at": reset_at,
            "reputation": reputation
        }

    async def reset_rate_limit(self, ip: str, endpoint_type: EndpointType):
        """Reset rate limit for IP (admin use)"""
        key = self._get_rate_limit_key(ip, endpoint_type)
        burst_key = self._get_burst_key(ip, endpoint_type)

        await redis_manager.delete(key)
        await redis_manager.delete(burst_key)

        logger.info(f"Rate limit reset for {ip} on {endpoint_type.value}")

    def add_to_whitelist(self, ip: str):
        """Add IP to whitelist"""
        self.whitelist.add(ip)
        logger.info(f"IP {ip} added to whitelist")

    def remove_from_whitelist(self, ip: str):
        """Remove IP from whitelist"""
        self.whitelist.discard(ip)
        logger.info(f"IP {ip} removed from whitelist")

    def add_to_blacklist(self, ip: str):
        """Add IP to permanent blacklist"""
        self.blacklist.add(ip)
        logger.critical(f"IP {ip} added to permanent blacklist")

    def remove_from_blacklist(self, ip: str):
        """Remove IP from blacklist"""
        self.blacklist.discard(ip)
        logger.info(f"IP {ip} removed from blacklist")

    async def get_ip_stats(self, ip: str) -> Dict[str, Any]:
        """Get comprehensive IP statistics"""
        reputation = await IPReputation.get_reputation(ip)
        is_banned = await IPReputation.is_banned(ip)

        violation_key = IPReputation._get_violation_key(ip)
        violations = await redis_manager.get(violation_key)

        # Get rate limit status for all endpoint types
        limits = {}
        for endpoint_type in EndpointType:
            status = await self.check_rate_limit(ip, endpoint_type, increment=False)
            limits[endpoint_type.value] = status

        return {
            "ip": ip,
            "reputation": reputation,
            "is_banned": is_banned,
            "is_whitelisted": ip in self.whitelist,
            "is_blacklisted": ip in self.blacklist,
            "violations": int(violations) if violations else 0,
            "rate_limits": limits
        }


class SuspiciousActivityDetector:
    """Detect suspicious patterns in user activity"""

    @staticmethod
    async def detect_rapid_requests(ip: str, threshold: int = 50) -> bool:
        """Detect abnormally rapid requests"""
        key = f"request_count:{ip}"
        count = await redis_manager.incr(key)

        if count == 1:
            await redis_manager.expire(key, 10)  # 10 second window

        if count > threshold:
            logger.warning(f"Rapid requests detected from {ip}: {count} in 10s")
            return True

        return False

    @staticmethod
    async def detect_distributed_attack(endpoint: str, threshold: int = 100) -> bool:
        """Detect distributed attack on specific endpoint"""
        key = f"endpoint_requests:{endpoint}"
        count = await redis_manager.incr(key)

        if count == 1:
            await redis_manager.expire(key, 60)  # 1 minute window

        if count > threshold:
            logger.critical(f"Possible DDoS on {endpoint}: {count} requests in 60s")
            return True

        return False

    @staticmethod
    async def detect_credential_stuffing(ip: str, db: Session) -> bool:
        """Detect credential stuffing attacks (multiple failed logins)"""
        # Check recent failed login attempts
        recent_failures = db.query(SecurityEvent).filter(
            SecurityEvent.ip_address == ip,
            SecurityEvent.event_type == "failed_login",
            SecurityEvent.created_at >= datetime.utcnow() - timedelta(minutes=15)
        ).count()

        if recent_failures >= 5:
            logger.critical(f"Credential stuffing detected from {ip}: {recent_failures} failed logins")
            return True

        return False

    @staticmethod
    async def log_security_event(
        db: Session,
        user_id: Optional[int],
        event_type: str,
        severity: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Log security event to database"""
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            event_metadata=metadata,
            is_resolved=False
        )

        db.add(event)
        db.commit()

        logger.info(f"Security event logged: {event_type} from {ip_address}")


# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()


async def rate_limit_middleware(
    request: Request,
    endpoint_type: EndpointType = EndpointType.PUBLIC
) -> Dict[str, Any]:
    """
    Rate limit middleware

    Usage:
        @app.get("/api/endpoint")
        async def endpoint(request: Request):
            await rate_limit_middleware(request, EndpointType.API)
            # ... rest of endpoint logic
    """
    # Get client IP
    ip = request.client.host

    # Get forwarded IP if behind proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()

    # Check rate limit
    result = await rate_limiter.check_rate_limit(ip, endpoint_type)

    if not result["allowed"]:
        # Log violation
        logger.warning(
            f"Rate limit exceeded: {ip} on {endpoint_type.value} "
            f"({result['current']}/{result['limit']})"
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "limit": result["limit"],
                "remaining": result["remaining"],
                "reset_at": result["reset_at"],
                "reputation": result["reputation"]
            }
        )

    # Add rate limit headers to response (will be set by decorator)
    request.state.rate_limit_headers = {
        "X-RateLimit-Limit": str(result["limit"]),
        "X-RateLimit-Remaining": str(result["remaining"]),
        "X-RateLimit-Reset": str(result["reset_at"]),
        "X-IP-Reputation": str(result["reputation"])
    }

    return result
