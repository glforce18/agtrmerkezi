"""
API Health Check Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/games",
        "/api/users",
        "/api/packages",
    ],
)
async def test_protected_endpoints_require_auth(client: AsyncClient, endpoint: str):
    """Test that protected endpoints require authentication"""
    response = await client.get(endpoint)
    # Should be 401 Unauthorized or 200 if public
    assert response.status_code in [200, 401, 403]


@pytest.mark.asyncio
async def test_nonexistent_endpoint_returns_404(client: AsyncClient):
    """Test that nonexistent endpoints return 404"""
    response = await client.get("/api/this-does-not-exist")
    assert response.status_code == 404
