"""Test request helper utilities"""
import pytest
from unittest.mock import Mock
from app.utils.request_helpers import (
    get_client_ip,
    get_user_agent,
    is_mobile_request,
    get_request_metadata
)


def test_get_client_ip_direct():
    """Test getting client IP directly"""
    request = Mock()
    request.client.host = "192.168.1.1"
    request.headers = {}

    ip = get_client_ip(request)
    assert ip == "192.168.1.1"


def test_get_client_ip_forwarded():
    """Test getting client IP from X-Forwarded-For"""
    request = Mock()
    request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}

    ip = get_client_ip(request)
    assert ip == "10.0.0.1"


def test_get_user_agent():
    """Test getting user agent"""
    request = Mock()
    request.headers = {"User-Agent": "Mozilla/5.0"}

    ua = get_user_agent(request)
    assert ua == "Mozilla/5.0"


def test_is_mobile_request_desktop():
    """Test desktop detection"""
    request = Mock()
    request.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0)"}

    assert is_mobile_request(request) is False


def test_is_mobile_request_mobile():
    """Test mobile detection"""
    request = Mock()
    request.headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS)"}

    assert is_mobile_request(request) is True


def test_get_request_metadata():
    """Test getting request metadata"""
    request = Mock()
    request.client.host = "192.168.1.1"
    request.headers = {"User-Agent": "Mozilla/5.0"}
    request.method = "GET"
    request.url = Mock()
    request.url.path = "/api/test"
    request.url.__str__ = lambda self: "http://localhost/api/test"

    metadata = get_request_metadata(request)

    assert metadata["ip"] == "192.168.1.1"
    assert metadata["user_agent"] == "Mozilla/5.0"
    assert metadata["method"] == "GET"
    assert "is_mobile" in metadata
