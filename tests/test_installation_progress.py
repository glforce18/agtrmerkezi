"""
AGTR Merkezi - Installation Progress Tests
Unit tests for real-time installation progress WebSocket
"""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import WebSocket

from app.services.installation_progress import (
    InstallationProgressManager,
)


class TestInstallationProgressManager:
    """Test suite for InstallationProgressManager"""

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test WebSocket connection"""
        manager = InstallationProgressManager()
        mock_ws = AsyncMock(spec=WebSocket)

        await manager.connect(mock_ws, server_id=123)

        # Verify connection tracked
        assert 123 in manager.connections
        assert mock_ws in manager.connections[123]
        assert manager.ws_to_server[mock_ws] == 123

        # Verify accept was called
        mock_ws.accept.assert_called_once()

        # Verify welcome message sent
        mock_ws.send_json.assert_called_once()
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "connected"
        assert call_args["server_id"] == 123

    def test_disconnect(self):
        """Test WebSocket disconnection"""
        manager = InstallationProgressManager()
        mock_ws = Mock(spec=WebSocket)

        # Setup connection
        manager.connections[123] = {mock_ws}
        manager.ws_to_server[mock_ws] = 123

        # Disconnect
        manager.disconnect(mock_ws)

        # Verify cleanup
        assert 123 not in manager.connections
        assert mock_ws not in manager.ws_to_server

    @pytest.mark.asyncio
    async def test_broadcast_progress(self):
        """Test broadcasting progress to connected clients"""
        manager = InstallationProgressManager()
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)

        # Connect 2 clients
        await manager.connect(mock_ws1, server_id=123)
        await manager.connect(mock_ws2, server_id=123)

        # Reset mocks to ignore connection messages
        mock_ws1.reset_mock()
        mock_ws2.reset_mock()

        # Broadcast progress
        await manager.broadcast_progress(
            server_id=123,
            stage="Downloading files",
            progress=50,
            message="Downloading template (50 MB / 100 MB)",
        )

        # Verify both clients received message
        mock_ws1.send_json.assert_called_once()
        mock_ws2.send_json.assert_called_once()

        # Verify message content
        call_args = mock_ws1.send_json.call_args[0][0]
        assert call_args["type"] == "progress"
        assert call_args["server_id"] == 123
        assert call_args["stage"] == "Downloading files"
        assert call_args["progress"] == 50
        assert call_args["message"] == "Downloading template (50 MB / 100 MB)"

    @pytest.mark.asyncio
    async def test_broadcast_progress_with_error(self):
        """Test broadcasting error"""
        manager = InstallationProgressManager()
        mock_ws = AsyncMock(spec=WebSocket)

        await manager.connect(mock_ws, server_id=123)
        mock_ws.reset_mock()

        # Broadcast error
        await manager.broadcast_progress(
            server_id=123,
            stage="Template copy",
            progress=30,
            error="Template not found",
        )

        # Verify error message
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "error"
        assert call_args["error"] == "Template not found"

    @pytest.mark.asyncio
    async def test_broadcast_no_clients(self):
        """Test broadcasting when no clients connected"""
        manager = InstallationProgressManager()

        # Should not raise exception
        await manager.broadcast_progress(server_id=999, stage="Test", progress=50, message="Test")

    @pytest.mark.asyncio
    async def test_broadcast_completion_success(self):
        """Test broadcasting successful completion"""
        manager = InstallationProgressManager()
        mock_ws = AsyncMock(spec=WebSocket)

        await manager.connect(mock_ws, server_id=123)
        mock_ws.reset_mock()

        # Broadcast completion
        await manager.broadcast_completion(
            server_id=123, success=True, message="Server installed successfully"
        )

        # Verify completion message
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "completed"
        assert call_args["success"] is True
        assert call_args["progress"] == 100
        assert call_args["message"] == "Server installed successfully"

    @pytest.mark.asyncio
    async def test_broadcast_completion_failure(self):
        """Test broadcasting failed completion"""
        manager = InstallationProgressManager()
        mock_ws = AsyncMock(spec=WebSocket)

        await manager.connect(mock_ws, server_id=123)
        mock_ws.reset_mock()

        # Broadcast failure
        await manager.broadcast_completion(
            server_id=123, success=False, message="Installation failed: timeout"
        )

        # Verify failure message
        call_args = mock_ws.send_json.call_args[0][0]
        assert call_args["type"] == "failed"
        assert call_args["success"] is False
        assert call_args["progress"] == 0

    def test_get_client_count(self):
        """Test getting client count"""
        manager = InstallationProgressManager()
        mock_ws1 = Mock(spec=WebSocket)
        mock_ws2 = Mock(spec=WebSocket)

        # No clients
        assert manager.get_client_count(123) == 0

        # Add clients
        manager.connections[123] = {mock_ws1, mock_ws2}

        assert manager.get_client_count(123) == 2

    @pytest.mark.asyncio
    async def test_broadcast_handles_dead_connection(self):
        """Test broadcasting handles dead WebSocket connection"""
        manager = InstallationProgressManager()
        mock_ws = AsyncMock(spec=WebSocket)

        # Simulate dead connection
        mock_ws.send_json.side_effect = Exception("Connection closed")

        await manager.connect(mock_ws, server_id=123)

        # Broadcast should not raise exception
        await manager.broadcast_progress(server_id=123, stage="Test", progress=50, message="Test")

        # Connection should be cleaned up
        assert mock_ws not in manager.connections.get(123, set())

    @pytest.mark.asyncio
    async def test_multiple_servers_independent(self):
        """Test multiple servers have independent client lists"""
        manager = InstallationProgressManager()
        mock_ws1 = AsyncMock(spec=WebSocket)
        mock_ws2 = AsyncMock(spec=WebSocket)

        # Connect to different servers
        await manager.connect(mock_ws1, server_id=123)
        await manager.connect(mock_ws2, server_id=456)

        mock_ws1.reset_mock()
        mock_ws2.reset_mock()

        # Broadcast to server 123
        await manager.broadcast_progress(
            server_id=123, stage="Test", progress=50, message="Test 123"
        )

        # Only ws1 should receive
        mock_ws1.send_json.assert_called_once()
        mock_ws2.send_json.assert_not_called()


@pytest.mark.integration
class TestInstallationProgressIntegration:
    """Integration tests with real WebSocket"""

    @pytest.mark.asyncio
    async def test_full_installation_flow(self):
        """Test complete installation progress flow"""
        pytest.skip("Requires WebSocket client and running server")

    @pytest.mark.asyncio
    async def test_websocket_authentication(self):
        """Test WebSocket authentication with JWT"""
        pytest.skip("Requires WebSocket client and auth setup")
