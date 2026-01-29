"""
TransactionRollbackService Unit Tests
Rollback mekanizması testleri
"""

import pytest

from app.models.database import GameServer, Payment, PaymentStatus, ServerStatus
from app.services.error_handler import TransactionRollbackService


class TestTransactionRollbackService:
    """TransactionRollbackService test suite"""

    def test_rollback_server_creation(self, db, test_user, test_server, test_payment):
        """Test: Sunucu oluşturma rollback"""
        service = TransactionRollbackService(db)

        # Rollback yap
        result = service.rollback_server_creation(
            server_id=test_server.id,
            payment_id=test_payment.id,
            reason="Test rollback",
            send_notification=False,
        )

        assert result["success"] is True

        # Server DELETED olmalı
        db.refresh(test_server)
        assert test_server.status == ServerStatus.DELETED

        # Payment REFUNDED olmalı
        db.refresh(test_payment)
        assert test_payment.status == PaymentStatus.REFUNDED

        # Bakiye iade edilmeli
        db.refresh(test_user)
        assert test_user.balance == 200.0  # 100 + 100 refund

    def test_retry_with_exponential_backoff(self):
        """Test: Exponential backoff retry"""
        from app.services.error_handler import TransactionRollbackService

        attempt_count = 0

        def failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Test error")
            return "Success"

        # 3. denemede başarılı olmalı
        result = TransactionRollbackService.retry_with_exponential_backoff(
            failing_function,
            max_retries=3,
            initial_delay=0.1,  # Test için kısa delay
            backoff_multiplier=2,
        )

        assert result == "Success"
        assert attempt_count == 3


@pytest.fixture
def test_server(db, test_user):
    from app.models.database import GameType

    server = GameServer(
        owner_id=test_user.id,
        name="Test Server",
        game_type=GameType.CS16,
        ip_address="127.0.0.1",
        port=27015,
        slots=16,
        monthly_price=100.0,
        status=ServerStatus.PENDING,
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    return server


@pytest.fixture
def test_payment(db, test_user, test_server):
    payment = Payment(
        user_id=test_user.id,
        server_id=test_server.id,
        amount=100.0,
        status=PaymentStatus.COMPLETED,
        reference_code="TEST123",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
