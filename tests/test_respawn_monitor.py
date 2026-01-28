"""
AGTR Merkezi - Respawn Monitor Tests
Unit tests for crash storm detection
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app.models.database import GameServer, ServerStatus
from app.services.respawn_monitor import RespawnMonitor


class TestRespawnMonitor:
    """Test suite for RespawnMonitor"""

    def test_calculate_backoff(self):
        """Test exponential backoff calculation"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        # Crash 1: 2 seconds
        assert monitor.calculate_backoff(1) == 2

        # Crash 2: 4 seconds
        assert monitor.calculate_backoff(2) == 4

        # Crash 3: 8 seconds
        assert monitor.calculate_backoff(3) == 8

        # Crash 4: 16 seconds
        assert monitor.calculate_backoff(4) == 16

        # Crash 5: 32 seconds
        assert monitor.calculate_backoff(5) == 32

        # Crash 10: capped at 300 seconds
        assert monitor.calculate_backoff(10) == 300

    def test_is_in_backoff_period_no_backoff(self):
        """Test backoff check when no backoff set"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        server.restart_backoff_until = None

        assert monitor.is_in_backoff_period(server) is False

    def test_is_in_backoff_period_expired(self):
        """Test backoff check when backoff expired"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        # Backoff expired 10 minutes ago
        server.restart_backoff_until = datetime.utcnow() - timedelta(minutes=10)

        assert monitor.is_in_backoff_period(server) is False

    def test_is_in_backoff_period_active(self):
        """Test backoff check when backoff active"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        # Backoff for next 5 minutes
        server.restart_backoff_until = datetime.utcnow() + timedelta(minutes=5)

        assert monitor.is_in_backoff_period(server) is True

    def test_is_storm_detected_no_crashes(self):
        """Test storm detection with no crashes"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        server.last_crash = None
        server.crash_count = 0

        assert monitor.is_storm_detected(server) is False

    def test_is_storm_detected_old_crash(self):
        """Test storm detection with old crash (outside window)"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        # Last crash 1 hour ago (outside 10-minute window)
        server.last_crash = datetime.utcnow() - timedelta(hours=1)
        server.crash_count = 3

        # Should reset counter and return False
        assert monitor.is_storm_detected(server) is False
        db.commit.assert_called_once()

    def test_is_storm_detected_within_window_below_threshold(self):
        """Test storm detection with crashes below threshold"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        # Recent crash, but only 3 times
        server.last_crash = datetime.utcnow() - timedelta(minutes=5)
        server.crash_count = 3

        assert monitor.is_storm_detected(server) is False

    def test_is_storm_detected_storm_active(self):
        """Test storm detection when storm active"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        # Recent crash, 5 times (threshold)
        server.last_crash = datetime.utcnow() - timedelta(minutes=5)
        server.crash_count = 5

        assert monitor.is_storm_detected(server) is True

    @pytest.mark.asyncio
    async def test_handle_server_crash_first_crash(self):
        """Test handling first crash"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        server.id = 123
        server.name = "Test Server"
        server.last_crash = None
        server.crash_count = 0
        server.auto_restart = True

        # Handle crash
        result = await monitor.handle_server_crash(server)

        # Should allow restart
        assert result is True

        # Should update crash tracking
        assert server.crash_count == 1
        assert server.last_crash is not None
        assert server.restart_backoff_until is not None
        assert server.status == ServerStatus.STOPPED

        # Backoff should be 2 seconds (first crash)
        backoff_seconds = (server.restart_backoff_until - server.last_crash).total_seconds()
        assert backoff_seconds == 2

        db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_handle_server_crash_multiple_crashes(self):
        """Test handling multiple crashes"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        server.id = 123
        server.name = "Test Server"
        # Already crashed 2 times
        server.last_crash = datetime.utcnow() - timedelta(minutes=2)
        server.crash_count = 2
        server.auto_restart = True

        # Handle 3rd crash
        result = await monitor.handle_server_crash(server)

        # Should allow restart (below 5 threshold)
        assert result is True

        # Crash count incremented
        assert server.crash_count == 3

        # Backoff should be 8 seconds (3rd crash: 2^2 = 4, but 2^(3-1) = 4)
        # Wait, formula is 2^(crash_count-1), so 3rd crash = 2^2 = 4
        # Actually code has: backoff = 2 * (2 ** (crash_count - 1))
        # So crash 3: 2 * 2^2 = 2 * 4 = 8

    @pytest.mark.asyncio
    async def test_handle_server_crash_storm_detected(self):
        """Test handling crash when storm detected"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        server.id = 123
        server.name = "Test Server"
        server.owner_id = 456
        # Already crashed 4 times
        server.last_crash = datetime.utcnow() - timedelta(minutes=2)
        server.crash_count = 4
        server.auto_restart = True

        # Mock notification creation
        with pytest.mock.patch.object(
            monitor, "_notify_owner_storm_detected", new=pytest.mock.AsyncMock()
        ):
            # Handle 5th crash (triggers storm)
            result = await monitor.handle_server_crash(server)

            # Should block restart
            assert result is False

            # Auto-restart disabled
            assert server.auto_restart is False

            # Crash count should be 5
            assert server.crash_count == 5

    def test_reset_crash_tracking(self):
        """Test resetting crash tracking"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        server.id = 123
        server.crash_count = 5
        server.restart_backoff_until = datetime.utcnow() + timedelta(minutes=5)

        # Reset
        monitor.reset_crash_tracking(server)

        assert server.crash_count == 0
        assert server.restart_backoff_until is None
        db.commit.assert_called_once()

    def test_re_enable_auto_restart_storm_active(self):
        """Test re-enabling auto-restart when storm still active"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        server.id = 123
        # Storm still active
        server.last_crash = datetime.utcnow() - timedelta(minutes=2)
        server.crash_count = 5
        server.auto_restart = False

        # Try to re-enable
        result = monitor.re_enable_auto_restart(server)

        # Should fail
        assert result is False
        assert server.auto_restart is False

    def test_re_enable_auto_restart_storm_cooled(self):
        """Test re-enabling auto-restart when storm cooled"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        server.id = 123
        # Storm cooled (old crash)
        server.last_crash = datetime.utcnow() - timedelta(hours=1)
        server.crash_count = 5
        server.auto_restart = False

        # Try to re-enable
        result = monitor.re_enable_auto_restart(server)

        # Should succeed
        assert result is True
        assert server.auto_restart is True
        assert server.crash_count == 0
        assert server.restart_backoff_until is None
        db.commit.assert_called()

    def test_get_crash_stats(self):
        """Test getting crash statistics"""
        db = Mock(spec=Session)
        monitor = RespawnMonitor(db)

        server = Mock(spec=GameServer)
        server.crash_count = 3
        server.last_crash = datetime.utcnow() - timedelta(minutes=5)
        server.auto_restart = True
        server.restart_backoff_until = datetime.utcnow() + timedelta(seconds=30)

        stats = monitor.get_crash_stats(server)

        assert stats["crash_count"] == 3
        assert stats["last_crash"] is not None
        assert stats["storm_detected"] is False  # Below 5 threshold
        assert stats["auto_restart_enabled"] is True
        assert stats["in_backoff"] is True
        assert stats["backoff_remaining_seconds"] is not None
        assert stats["restart_allowed"] is False  # In backoff


@pytest.mark.integration
class TestRespawnMonitorIntegration:
    """Integration tests with real database"""

    @pytest.mark.asyncio
    async def test_full_storm_flow(self):
        """Test complete storm detection flow"""
        pytest.skip("Requires real database and server control")
