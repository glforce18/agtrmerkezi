"""Test configuration and settings"""
import pytest
from app.core.config import settings


def test_settings_loaded():
    """Test that settings are loaded correctly"""
    assert settings is not None
    assert settings.APP_NAME == "AGTR Merkezi"
    assert settings.DB_NAME == "agtrmerkezi"


def test_database_url():
    """Test database URL format"""
    db_url = settings.DATABASE_URL
    assert "mysql+pymysql://" in db_url
    assert settings.DB_NAME in db_url


def test_redis_settings():
    """Test Redis settings"""
    assert settings.REDIS_HOST is not None
    assert settings.REDIS_PORT == 6379


def test_security_settings():
    """Test security settings"""
    assert settings.SECRET_KEY is not None
    assert len(settings.SECRET_KEY) >= 32
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
