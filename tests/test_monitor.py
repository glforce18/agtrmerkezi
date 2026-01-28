"""
AGTR Merkezi - Server Monitor Tests
Unit tests for enhanced resource monitoring
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.orm import Session

from app.models.database import GameServer
from app.services.monitor import ServerMonitor


class TestServerMonitorMetrics:
    """Test suite for ServerMonitor metrics collection"""

    @pytest.mark.asyncio
    async def test_collect_metrics_success(self, db_session: Session):
        """Test successful metrics collection"""
        monitor = ServerMonitor()

        # Create test server
        server = Mock(spec=GameServer)
        server.id = 1
        server.name = "Test Server"
        server.process_pid = 12345
        server.ip_address = "185.171.25.138"
        server.port = 27018

        # Mock psutil.Process
        mock_process = Mock()
        mock_process.cpu_percent.return_value = 25.5
        mock_process.memory_info.return_value.rss = 512 * 1024 * 1024  # 512 MB
        mock_process.status.return_value = "running"

        # Mock A2S query
        mock_query_info = AsyncMock(
            return_value={"players": 10, "max_players": 32, "map": "de_dust2"}
        )

        with patch("psutil.pid_exists", return_value=True), patch(
            "psutil.Process", return_value=mock_process
        ), patch.object(monitor, "_query_a2s", mock_query_info):

            metric = await monitor.collect_server_metrics(server, db_session)

            # Verify metric was created
            assert metric is not None
            assert metric.server_id == 1
            assert metric.cpu_percent == 25.5
            assert metric.memory_mb == 512.0
            assert metric.player_count == 10
            assert metric.process_status == "running"

            # Verify database add was called
            db_session.add.assert_called_once()
            db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_collect_metrics_no_process(self, db_session: Session):
        """Test metrics collection when process doesn't exist"""
        monitor = ServerMonitor()

        server = Mock(spec=GameServer)
        server.id = 2
        server.process_pid = None

        metric = await monitor.collect_server_metrics(server, db_session)

        # Should return None
        assert metric is None
        db_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_collect_metrics_process_died(self, db_session: Session):
        """Test metrics collection when process died"""
        monitor = ServerMonitor()

        server = Mock(spec=GameServer)
        server.id = 3
        server.process_pid = 99999

        with patch("psutil.pid_exists", return_value=False):
            metric = await monitor.collect_server_metrics(server, db_session)

            # Should return None
            assert metric is None
            db_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_collect_metrics_high_cpu_alert(self, db_session: Session):
        """Test high CPU alert triggering"""
        monitor = ServerMonitor()

        server = Mock(spec=GameServer)
        server.id = 4
        server.name = "High CPU Server"
        server.process_pid = 12345
        server.ip_address = "185.171.25.138"
        server.port = 27018

        # Mock high CPU usage (85%)
        mock_process = Mock()
        mock_process.cpu_percent.return_value = 85.0
        mock_process.memory_info.return_value.rss = 512 * 1024 * 1024
        mock_process.status.return_value = "running"

        mock_query_info = AsyncMock(return_value={"players": 5})
        mock_alert = AsyncMock()

        with patch("psutil.pid_exists", return_value=True), patch(
            "psutil.Process", return_value=mock_process
        ), patch.object(monitor, "_query_a2s", mock_query_info), patch.object(
            monitor, "_alert_high_cpu", mock_alert
        ):

            await monitor.collect_server_metrics(server, db_session)

            # Verify alert was called
            mock_alert.assert_called_once()
            call_args = mock_alert.call_args
            assert call_args[0][0] == server
            assert call_args[0][1] == 85.0

    @pytest.mark.asyncio
    async def test_collect_metrics_high_memory_alert(self, db_session: Session):
        """Test high memory alert triggering"""
        monitor = ServerMonitor()

        server = Mock(spec=GameServer)
        server.id = 5
        server.name = "High Memory Server"
        server.process_pid = 12345
        server.ip_address = "185.171.25.138"
        server.port = 27018

        # Mock high memory usage (2.5 GB)
        mock_process = Mock()
        mock_process.cpu_percent.return_value = 50.0
        mock_process.memory_info.return_value.rss = int(2.5 * 1024 * 1024 * 1024)
        mock_process.status.return_value = "running"

        mock_query_info = AsyncMock(return_value={"players": 20})
        mock_alert = AsyncMock()

        with patch("psutil.pid_exists", return_value=True), patch(
            "psutil.Process", return_value=mock_process
        ), patch.object(monitor, "_query_a2s", mock_query_info), patch.object(
            monitor, "_alert_high_memory", mock_alert
        ):

            await monitor.collect_server_metrics(server, db_session)

            # Verify alert was called
            mock_alert.assert_called_once()
            call_args = mock_alert.call_args
            assert call_args[0][0] == server
            assert call_args[0][1] > 2048  # > 2GB

    @pytest.mark.asyncio
    async def test_collect_metrics_a2s_query_fails(self, db_session: Session):
        """Test metrics collection when A2S query fails"""
        monitor = ServerMonitor()

        server = Mock(spec=GameServer)
        server.id = 6
        server.process_pid = 12345
        server.ip_address = "185.171.25.138"
        server.port = 27018

        mock_process = Mock()
        mock_process.cpu_percent.return_value = 30.0
        mock_process.memory_info.return_value.rss = 256 * 1024 * 1024
        mock_process.status.return_value = "running"

        # A2S query fails (returns None)
        mock_query_info = AsyncMock(return_value=None)

        with patch("psutil.pid_exists", return_value=True), patch(
            "psutil.Process", return_value=mock_process
        ), patch.object(monitor, "_query_a2s", mock_query_info):

            metric = await monitor.collect_server_metrics(server, db_session)

            # Metric should still be created with player_count=0
            assert metric is not None
            assert metric.player_count == 0
            assert metric.cpu_percent == 30.0

    @pytest.mark.asyncio
    async def test_collect_metrics_psutil_no_such_process(self, db_session: Session):
        """Test handling of psutil.NoSuchProcess exception"""
        monitor = ServerMonitor()

        server = Mock(spec=GameServer)
        server.id = 7
        server.process_pid = 99999
        server.name = "Crashed Server"

        mock_handle_crash = AsyncMock()

        with patch("psutil.pid_exists", return_value=True), patch(
            "psutil.Process", side_effect=__import__("psutil").NoSuchProcess(99999)
        ), patch.object(monitor, "_handle_server_crash", mock_handle_crash):

            metric = await monitor.collect_server_metrics(server, db_session)

            # Should handle crash
            assert metric is None
            mock_handle_crash.assert_called_once_with(server, db_session)

    @pytest.mark.asyncio
    async def test_collect_metrics_network_io(self, db_session: Session):
        """Test network I/O metrics collection"""
        monitor = ServerMonitor()

        server = Mock(spec=GameServer)
        server.id = 8
        server.process_pid = 12345
        server.ip_address = "185.171.25.138"
        server.port = 27018

        # Mock with network I/O counters
        mock_io_counters = Mock()
        mock_io_counters.read_bytes = 100 * 1024 * 1024  # 100 MB
        mock_io_counters.write_bytes = 50 * 1024 * 1024  # 50 MB

        mock_process = Mock()
        mock_process.cpu_percent.return_value = 20.0
        mock_process.memory_info.return_value.rss = 300 * 1024 * 1024
        mock_process.status.return_value = "running"
        mock_process.io_counters.return_value = mock_io_counters

        mock_query_info = AsyncMock(return_value={"players": 15})

        with patch("psutil.pid_exists", return_value=True), patch(
            "psutil.Process", return_value=mock_process
        ), patch.object(monitor, "_query_a2s", mock_query_info):

            metric = await monitor.collect_server_metrics(server, db_session)

            # Verify network metrics
            assert metric is not None
            assert metric.network_in_mbps == 100.0  # MB
            assert metric.network_out_mbps == 50.0  # MB


@pytest.fixture
def db_session():
    """Mock database session for testing"""
    session = Mock(spec=Session)
    session.add = Mock()
    session.commit = Mock()
    session.query = Mock()
    return session


# Integration test markers (requires real database)
@pytest.mark.integration
class TestServerMonitorIntegration:
    """Integration tests with real database"""

    @pytest.mark.asyncio
    async def test_full_metrics_collection_flow(self, real_db_session):
        """Test complete metrics collection flow with real database"""
        pytest.skip("Requires real database and running server")

    @pytest.mark.asyncio
    async def test_metrics_api_endpoints(self, real_db_session):
        """Test metrics API endpoints return correct data"""
        pytest.skip("Requires real database and API client")
