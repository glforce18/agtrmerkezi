"""
SubscriptionService Unit Tests
Critical path testleri: billing, rollback, grace period
"""

from datetime import date, datetime, timedelta

import pytest

from app.models.database import (
    BillingPeriod,
    GameServer,
    ServerStatus,
    Subscription,
    SubscriptionStatus,
    WalletType,
)
from app.services.subscription_service import SubscriptionService


class TestSubscriptionService:
    """SubscriptionService test suite"""

    def test_create_subscription(self, db, test_user, test_server):
        """Test: Abonelik oluşturma"""
        service = SubscriptionService(db)

        subscription = service.create_subscription(
            game_server_id=test_server.id,
            user_id=test_user.id,
            billing_period=BillingPeriod.MONTHLY,
            auto_renew_enabled=True,
            payment_method=WalletType.REAL,
            monthly_amount=100.0,
        )

        assert subscription is not None
        assert subscription.game_server_id == test_server.id
        assert subscription.user_id == test_user.id
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.monthly_amount == 100.0
        assert subscription.auto_renew_enabled is True

    def test_attempt_billing_success(self, db, test_subscription, test_user):
        """Test: Başarılı otomatik billing"""
        service = SubscriptionService(db)

        # Kullanıcıya yeterli bakiye ekle
        test_user.balance = 200.0
        db.commit()

        # Billing yap
        result = service.attempt_billing(subscription_id=test_subscription.id)

        assert result["success"] is True
        assert "new_expiry_date" in result
        assert result["amount"] == 100.0

        # Bakiye düştü mü?
        db.refresh(test_user)
        assert test_user.balance == 100.0

    def test_attempt_billing_insufficient_balance(self, db, test_subscription, test_user):
        """Test: Yetersiz bakiye - Grace period"""
        service = SubscriptionService(db)

        # Yetersiz bakiye
        test_user.balance = 50.0
        db.commit()

        # Billing yap
        result = service.attempt_billing(subscription_id=test_subscription.id)

        assert result["success"] is False
        assert result["status"] == "grace_period"

        # Subscription grace period'a geçti mi?
        db.refresh(test_subscription)
        assert test_subscription.status == SubscriptionStatus.GRACE_PERIOD
        assert test_subscription.failure_count == 1

    def test_attempt_billing_suspension_after_3_failures(self, db, test_subscription, test_user):
        """Test: 3 başarısızlıktan sonra suspension"""
        service = SubscriptionService(db)

        # Yetersiz bakiye
        test_user.balance = 0.0
        db.commit()

        # 3 kez başarısız dene
        for i in range(3):
            result = service.attempt_billing(subscription_id=test_subscription.id)
            assert result["success"] is False

        # Subscription suspended olmalı
        db.refresh(test_subscription)
        assert test_subscription.status == SubscriptionStatus.SUSPENDED
        assert test_subscription.failure_count == 3

    def test_toggle_auto_renew(self, db, test_subscription):
        """Test: Auto-renew açma/kapatma"""
        service = SubscriptionService(db)

        # Kapat
        result = service.toggle_auto_renew(
            subscription_id=test_subscription.id, user_id=test_subscription.user_id, enabled=False
        )

        assert result.auto_renew_enabled is False

        # Aç
        result = service.toggle_auto_renew(
            subscription_id=test_subscription.id, user_id=test_subscription.user_id, enabled=True
        )

        assert result.auto_renew_enabled is True

    def test_cancel_subscription(self, db, test_subscription):
        """Test: Abonelik iptali"""
        service = SubscriptionService(db)

        result = service.cancel_subscription(
            subscription_id=test_subscription.id,
            user_id=test_subscription.user_id,
            reason="Test iptali",
        )

        assert result.status == SubscriptionStatus.CANCELLED
        assert result.cancelled_at is not None
        assert result.auto_renew_enabled is False


# Fixtures
@pytest.fixture
def test_server(db, test_user):
    """Test server fixture"""
    from app.models.database import GameType

    server = GameServer(
        owner_id=test_user.id,
        name="Test Server",
        game_type=GameType.CS16,
        ip_address="127.0.0.1",
        port=27015,
        slots=16,
        monthly_price=100.0,
        status=ServerStatus.RUNNING,
        expires_at=datetime.now() + timedelta(days=30),
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    return server


@pytest.fixture
def test_subscription(db, test_user, test_server):
    """Test subscription fixture"""
    subscription = Subscription(
        game_server_id=test_server.id,
        user_id=test_user.id,
        billing_period=BillingPeriod.MONTHLY,
        auto_renew_enabled=True,
        payment_method=WalletType.REAL,
        next_billing_date=date.today() + timedelta(days=30),
        status=SubscriptionStatus.ACTIVE,
        monthly_amount=100.0,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription
