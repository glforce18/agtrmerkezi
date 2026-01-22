"""
AGTR Merkezi - Test Configuration
pytest fixtures and setup
"""

import pytest
import secrets
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.database import Base
from app.models.connection import get_db


# Test database (SQLite in-memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Test database session"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Test client with database override"""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create test user without Steam"""
    from app.models.database import User, UserRole, UserStatus
    from app.core.security import hash_password

    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        balance=100.0,
        balance_coin=500.0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def steam_user(db):
    """Create test user with Steam linked"""
    from app.models.database import User, UserRole, UserStatus
    from app.core.security import hash_password

    user = User(
        username="steamuser",
        email="steamuser@example.com",
        password_hash=hash_password("testpassword123"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        steam_id="76561198000000000",
        balance=100.0,
        balance_coin=500.0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    """Create admin user"""
    from app.models.database import User, UserRole, UserStatus
    from app.core.security import hash_password

    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password("adminpassword123"),
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        balance=1000.0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def unverified_user(db):
    """Create test user with unverified email"""
    from app.models.database import User, UserRole, UserStatus
    from app.core.security import hash_password

    user = User(
        username="unverified",
        email="unverified@example.com",
        password_hash=hash_password("testpassword123"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        email_verified=False,
        email_verification_token=secrets.token_urlsafe(32)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def verified_user(db):
    """Create test user with verified email"""
    from app.models.database import User, UserRole, UserStatus
    from app.core.security import hash_password

    user = User(
        username="verified",
        email="verified@example.com",
        password_hash=hash_password("testpassword123"),
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        email_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_auth_token_for_user(db, user):
    """Helper to create auth token for a user"""
    from app.core.security import create_access_token, hash_token
    from app.models.database import UserSession

    token = create_access_token({"sub": str(user.id)})

    # Create session
    session = UserSession(
        user_id=user.id,
        token_hash=hash_token(token),
        ip_address="127.0.0.1",
        user_agent="test-client",
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(session)
    db.commit()

    return token


@pytest.fixture
def auth_headers(client, db, test_user):
    """Get authentication headers for test user (no Steam)"""
    token = create_auth_token_for_user(db, test_user)
    return {"Cookie": f"access_token={token}"}


@pytest.fixture
def steam_user_headers(client, db, steam_user):
    """Get authentication headers for test user with Steam linked"""
    token = create_auth_token_for_user(db, steam_user)
    return {"Cookie": f"access_token={token}"}


@pytest.fixture
def admin_headers(client, db, admin_user):
    """Get authentication headers for admin user"""
    token = create_auth_token_for_user(db, admin_user)
    return {"Cookie": f"access_token={token}"}


@pytest.fixture
def forum_category(db):
    """Create a test forum category"""
    from app.models.database import ForumCategory

    category = ForumCategory(
        name="Test Category",
        slug="test-category",
        description="A test category",
        icon="test",
        color="#ff6b00",
        is_visible=True,
        display_order=1
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def forum_topic(db, steam_user, forum_category):
    """Create a test forum topic"""
    from app.models.database import ForumTopic

    topic = ForumTopic(
        title="Test Topic",
        slug="test-topic",
        content="This is a test topic content for testing purposes.",
        category_id=forum_category.id,
        author_id=steam_user.id,
        is_active=True,
        is_pinned=False,
        is_locked=False,
        view_count=0
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@pytest.fixture
def locked_topic(db, steam_user, forum_category):
    """Create a locked forum topic"""
    from app.models.database import ForumTopic

    topic = ForumTopic(
        title="Locked Topic",
        slug="locked-topic",
        content="This topic is locked.",
        category_id=forum_category.id,
        author_id=steam_user.id,
        is_active=True,
        is_pinned=False,
        is_locked=True,
        view_count=0
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic
