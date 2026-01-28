"""
AGTR Merkezi - RCON Rate Limiter Tests
Unit tests for per-user, per-endpoint rate limiting
"""

import time
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, Request

from app.services.rcon_rate_limiter import (
    ENDPOINT_LIMITS,
    RCONRateLimiter,
    check_rcon_rate_limit,
    get_user_id_from_token,
    rcon_rate_limiter,
)


class TestEndpointClassification:
    """Test endpoint path classification"""

    def test_classify_restart_endpoint(self):
        """Test restart endpoint classification"""
        limiter = RCONRateLimiter()

        assert limiter.classify_endpoint("/api/servers/1/rcon/restart") == "rcon_restart"
        assert limiter.classify_endpoint("/api/servers/123/action") == "rcon_restart"
        assert (
            limiter.classify_endpoint("/api/SERVERS/1/RCON/RESTART") == "rcon_restart"
        )  # Case insensitive

    def test_classify_kick_endpoint(self):
        """Test kick endpoint classification"""
        limiter = RCONRateLimiter()

        assert limiter.classify_endpoint("/api/servers/1/rcon/kick") == "rcon_kick"
        assert limiter.classify_endpoint("/api/servers/1/kick") == "rcon_kick"

    def test_classify_ban_endpoint(self):
        """Test ban endpoint classification"""
        limiter = RCONRateLimiter()

        assert limiter.classify_endpoint("/api/servers/1/rcon/ban") == "rcon_ban"
        assert limiter.classify_endpoint("/api/servers/1/ban") == "rcon_ban"

    def test_classify_status_endpoint(self):
        """Test status endpoint classification"""
        limiter = RCONRateLimiter()

        assert limiter.classify_endpoint("/api/servers/1/rcon/status") == "rcon_status"
        assert limiter.classify_endpoint("/api/servers/1/status") == "rcon_status"

    def test_classify_generic_rcon(self):
        """Test generic RCON command classification"""
        limiter = RCONRateLimiter()

        assert limiter.classify_endpoint("/api/servers/1/rcon/command") == "rcon_command"
        assert limiter.classify_endpoint("/api/servers/1/rcon/exec") == "rcon_command"

    def test_classify_non_rcon_endpoint(self):
        """Test non-RCON endpoint returns None"""
        limiter = RCONRateLimiter()

        assert limiter.classify_endpoint("/api/servers") is None
        assert limiter.classify_endpoint("/api/user/profile") is None
        assert limiter.classify_endpoint("/api/forum/topics") is None


class TestRateLimitingMemory:
    """Test rate limiting with in-memory backend"""

    def test_first_request_allowed(self):
        """Test first request is always allowed"""
        limiter = RCONRateLimiter()
        limiter.redis = None  # Force memory backend

        # First request should succeed
        is_limited, msg = limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")
        assert is_limited is False
        assert msg is None

    def test_within_limit_allowed(self):
        """Test requests within limit are allowed"""
        limiter = RCONRateLimiter()
        limiter.redis = None
        limiter.memory_counters = {}

        # Make 5 requests (limit is 10/hour for restart)
        for i in range(5):
            is_limited, msg = limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")
            assert is_limited is False

    def test_exceed_limit_raises_exception(self):
        """Test exceeding limit raises HTTPException"""
        limiter = RCONRateLimiter()
        limiter.redis = None
        limiter.memory_counters = {}

        # Restart limit is 10/hour
        for i in range(10):
            limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")

        # 11th request should fail
        with pytest.raises(HTTPException) as exc_info:
            limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail

    def test_different_users_independent_limits(self):
        """Test different users have independent limits"""
        limiter = RCONRateLimiter()
        limiter.redis = None
        limiter.memory_counters = {}

        # User 1: exhaust limit
        for i in range(10):
            limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")

        # User 1: should be blocked
        with pytest.raises(HTTPException):
            limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")

        # User 2: should still have full quota
        is_limited, _ = limiter.check_rate_limit(user_id=2, endpoint="rcon_restart")
        assert is_limited is False

    def test_different_endpoints_independent_limits(self):
        """Test different endpoints have independent limits"""
        limiter = RCONRateLimiter()
        limiter.redis = None
        limiter.memory_counters = {}

        # Exhaust restart limit (10/hour)
        for i in range(10):
            limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")

        # Restart should be blocked
        with pytest.raises(HTTPException):
            limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")

        # Kick should still work (different limit: 60/hour)
        is_limited, _ = limiter.check_rate_limit(user_id=1, endpoint="rcon_kick")
        assert is_limited is False

    def test_window_expiry_resets_counter(self):
        """Test counter resets after window expires"""
        limiter = RCONRateLimiter()
        limiter.redis = None
        limiter.memory_counters = {}

        # Make 5 requests
        for i in range(5):
            limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")

        # Manually expire the window
        key = "rcon_limit:1:rcon_restart"
        count, expire_time = limiter.memory_counters[key]
        limiter.memory_counters[key] = (count, time.time() - 1)  # Set to past

        # Next request should reset counter
        is_limited, _ = limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")
        assert is_limited is False

        # Counter should be 1 now
        count, _ = limiter.memory_counters[key]
        assert count == 1


class TestRateLimitingRedis:
    """Test rate limiting with Redis backend"""

    @pytest.mark.skipif(True, reason="Requires Redis server")
    def test_redis_first_request(self):
        """Test first request with Redis"""
        limiter = RCONRateLimiter()

        # Assumes Redis is available
        if limiter.redis:
            # Clear key first
            limiter.redis.delete("rcon_limit:999:rcon_restart")

            is_limited, _ = limiter.check_rate_limit(user_id=999, endpoint="rcon_restart")
            assert is_limited is False

    @pytest.mark.skipif(True, reason="Requires Redis server")
    def test_redis_exceed_limit(self):
        """Test exceeding limit with Redis"""
        limiter = RCONRateLimiter()

        if limiter.redis:
            # Clear key
            key = "rcon_limit:999:rcon_restart"
            limiter.redis.delete(key)

            # Make 10 requests
            for i in range(10):
                limiter.check_rate_limit(user_id=999, endpoint="rcon_restart")

            # 11th should fail
            with pytest.raises(HTTPException) as exc_info:
                limiter.check_rate_limit(user_id=999, endpoint="rcon_restart")

            assert exc_info.value.status_code == 429


class TestGetCurrentUsage:
    """Test usage statistics retrieval"""

    def test_get_usage_no_requests(self):
        """Test usage stats when no requests made"""
        limiter = RCONRateLimiter()
        limiter.redis = None
        limiter.memory_counters = {}

        usage = limiter.get_current_usage(user_id=1, endpoint="rcon_restart")

        assert usage["endpoint"] == "rcon_restart"
        assert usage["limit"] == 10
        assert usage["current"] == 0
        assert usage["remaining"] == 10
        assert usage["window"] == 3600

    def test_get_usage_after_requests(self):
        """Test usage stats after some requests"""
        limiter = RCONRateLimiter()
        limiter.redis = None
        limiter.memory_counters = {}

        # Make 3 requests
        for i in range(3):
            limiter.check_rate_limit(user_id=1, endpoint="rcon_restart")

        usage = limiter.get_current_usage(user_id=1, endpoint="rcon_restart")

        assert usage["current"] == 3
        assert usage["remaining"] == 7  # 10 - 3

    def test_get_usage_invalid_endpoint(self):
        """Test usage stats for invalid endpoint"""
        limiter = RCONRateLimiter()

        usage = limiter.get_current_usage(user_id=1, endpoint="invalid")
        assert usage == {}


class TestGetUserIdFromToken:
    """Test user ID extraction from JWT"""

    def test_extract_from_request_state(self):
        """Test extracting user_id from request.state.user"""
        request = Mock(spec=Request)
        mock_user = Mock()
        mock_user.id = 123
        request.state.user = mock_user

        user_id = get_user_id_from_token(request)
        assert user_id == 123

    def test_extract_from_authorization_header(self):
        """Test extracting user_id from Authorization header"""
        request = Mock(spec=Request)
        del request.state  # No state.user

        request.headers.get.return_value = "Bearer fake_token"

        with patch("app.services.rcon_rate_limiter.decode_access_token") as mock_decode:
            mock_decode.return_value = {"user_id": 456}

            user_id = get_user_id_from_token(request)
            assert user_id == 456

    def test_no_authentication(self):
        """Test when no authentication present"""
        request = Mock(spec=Request)
        del request.state
        request.headers.get.return_value = None

        user_id = get_user_id_from_token(request)
        assert user_id is None


@pytest.mark.asyncio
class TestCheckRconRateLimitDependency:
    """Test FastAPI dependency function"""

    async def test_dependency_allows_unauthenticated(self):
        """Test dependency allows unauthenticated requests (auth handled elsewhere)"""
        request = Mock(spec=Request)
        request.headers.get.return_value = None
        request.url.path = "/api/servers/1/rcon/restart"

        # Should not raise exception
        await check_rcon_rate_limit(request)

    async def test_dependency_allows_non_rcon(self):
        """Test dependency allows non-RCON endpoints"""
        request = Mock(spec=Request)
        mock_user = Mock()
        mock_user.id = 1
        request.state.user = mock_user
        request.url.path = "/api/servers"

        # Should not raise exception
        await check_rcon_rate_limit(request)

    async def test_dependency_enforces_limit(self):
        """Test dependency enforces rate limit"""
        request = Mock(spec=Request)
        mock_user = Mock()
        mock_user.id = 1
        request.state.user = mock_user
        request.url.path = "/api/servers/1/rcon/restart"

        # Mock limiter to always exceed limit
        with patch.object(rcon_rate_limiter, "check_rate_limit") as mock_check:
            mock_check.side_effect = HTTPException(status_code=429, detail="Rate limited")

            with pytest.raises(HTTPException) as exc_info:
                await check_rcon_rate_limit(request)

            assert exc_info.value.status_code == 429


class TestEndpointLimits:
    """Test endpoint limit configurations"""

    def test_all_limits_defined(self):
        """Test all expected endpoints have limits"""
        expected_endpoints = [
            "rcon_restart",
            "rcon_kick",
            "rcon_ban",
            "rcon_command",
            "rcon_status",
        ]

        for endpoint in expected_endpoints:
            assert endpoint in ENDPOINT_LIMITS
            assert "limit" in ENDPOINT_LIMITS[endpoint]
            assert "window" in ENDPOINT_LIMITS[endpoint]

    def test_restart_limit_strictest(self):
        """Test restart has the strictest limit"""
        restart_limit = ENDPOINT_LIMITS["rcon_restart"]["limit"]

        # Restart should have lower limit than status
        assert restart_limit < ENDPOINT_LIMITS["rcon_status"]["limit"]

    def test_all_windows_consistent(self):
        """Test all windows are 1 hour (3600s)"""
        for config in ENDPOINT_LIMITS.values():
            assert config["window"] == 3600
