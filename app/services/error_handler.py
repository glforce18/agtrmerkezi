"""
AGTR Merkezi - Transaction Rollback & Error Handler Service
Handles transaction rollbacks and retry logic with exponential backoff
"""

import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import (
    GameServer,
    Payment,
    PaymentStatus,
    ServerStatus,
    TransactionType,
    User,
    WalletType,
)
from app.services.wallet import WalletService

logger = logging.getLogger(__name__)


class TransactionRollbackService:
    """Service for rolling back failed transactions and server creation"""

    def __init__(self, db: Session):
        self.db = db
        self.wallet_service = WalletService(db)

    def rollback_server_creation(
        self,
        server_id: int,
        payment_id: Optional[int] = None,
        reason: str = "Server creation failed",
        send_notification: bool = True,
    ) -> Dict[str, Any]:
        """
        Rollback a failed server creation

        This method:
        1. Marks server as DELETED
        2. Releases port allocation
        3. Refunds payment to wallet (if payment exists)
        4. Creates refund transaction record
        5. Optionally sends user notification

        Args:
            server_id: Game server ID
            payment_id: Related payment ID (optional)
            reason: Reason for rollback
            send_notification: Send email notification to user

        Returns:
            Dict with rollback details
        """
        try:
            # Get server
            server = self.db.query(GameServer).filter(GameServer.id == server_id).first()

            if not server:
                logger.warning(f"Server {server_id} not found for rollback")
                return {
                    "success": False,
                    "message": "Sunucu bulunamadı",
                }

            user_id = server.owner_id
            refund_amount = 0
            refund_wallet_type = WalletType.REAL

            # Step 1: Mark server as DELETED
            old_status = server.status
            server.status = ServerStatus.DELETED
            server.updated_at = datetime.now()

            logger.info(
                f"Rolling back server creation: server_id={server_id}, "
                f"user_id={user_id}, reason={reason}"
            )

            # Step 2: Release port allocation
            # Port pool manager handles this automatically via status change
            # No explicit action needed as PortPoolManager checks server status

            # Step 3: Process payment refund
            refund_transaction = None
            if payment_id:
                payment = self.db.query(Payment).filter(Payment.id == payment_id).first()

                if payment and payment.status == PaymentStatus.COMPLETED:
                    refund_amount = payment.amount

                    # Determine wallet type from payment method
                    if payment.method.value == "balance":
                        # This was a wallet payment, need to determine which wallet
                        # Default to REAL wallet
                        refund_wallet_type = WalletType.REAL
                    else:
                        # External payment, refund to REAL wallet
                        refund_wallet_type = WalletType.REAL

                    # Mark payment as refunded
                    payment.status = PaymentStatus.REFUNDED
                    payment.cancelled_at = datetime.now()

                    # Refund to wallet
                    try:
                        refund_transaction = self.wallet_service.add_balance(
                            user_id=user_id,
                            amount=refund_amount,
                            wallet_type=refund_wallet_type,
                            transaction_type=TransactionType.REFUND.value,
                            description=f"Sunucu kurulum hatası iadesi - {server.name}",
                            reference_id=str(payment_id),
                            reference_type="payment_refund",
                            extra_data={
                                "server_id": server_id,
                                "reason": reason,
                                "original_payment_id": payment_id,
                            },
                        )

                        logger.info(
                            f"Refund processed: payment_id={payment_id}, "
                            f"amount={refund_amount}, wallet={refund_wallet_type.value}"
                        )
                    except Exception as e:
                        logger.error(f"Error processing refund: {e}", exc_info=True)
                        # Continue with rollback even if refund fails
                        # Admin can manually process refund

            # Step 4: Commit changes
            self.db.commit()

            # Step 5: Send notification (if enabled)
            if send_notification and refund_amount > 0:
                try:
                    from app.services.notification_service import NotificationService

                    NotificationService(self.db)

                    user = self.db.query(User).filter(User.id == user_id).first()
                    if user and user.email:
                        # Import here to avoid circular dependency
                        from app.services.email import EmailService

                        email_service = EmailService()

                        email_service.send_email(
                            to_email=user.email,
                            subject="Sunucu Kurulum Hatası - İade İşlemi",
                            template_name="server_creation_rollback",
                            context={
                                "user": user,
                                "server": server,
                                "refund_amount": refund_amount,
                                "wallet_type": (
                                    "TL Bakiye"
                                    if refund_wallet_type == WalletType.REAL
                                    else "Armor"
                                ),
                                "reason": reason,
                            },
                        )
                except Exception as e:
                    logger.error(f"Error sending rollback notification: {e}", exc_info=True)
                    # Don't fail the rollback if notification fails

            return {
                "success": True,
                "message": "Sunucu kurulumu geri alındı",
                "server_id": server_id,
                "old_status": old_status.value,
                "new_status": ServerStatus.DELETED.value,
                "refund_amount": refund_amount,
                "refund_wallet": refund_wallet_type.value if refund_amount > 0 else None,
                "refund_transaction_id": refund_transaction.id if refund_transaction else None,
                "reason": reason,
            }

        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error during server creation rollback: server_id={server_id}, error={e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Geri alma işlemi başarısız: {str(e)}",
            )

    def rollback_payment(
        self, payment_id: int, reason: str = "Payment processing failed"
    ) -> Dict[str, Any]:
        """
        Rollback a failed payment

        Args:
            payment_id: Payment ID
            reason: Reason for rollback

        Returns:
            Dict with rollback details
        """
        try:
            payment = self.db.query(Payment).filter(Payment.id == payment_id).first()

            if not payment:
                logger.warning(f"Payment {payment_id} not found for rollback")
                return {
                    "success": False,
                    "message": "Ödeme bulunamadı",
                }

            # Mark payment as failed
            old_status = payment.status
            payment.status = PaymentStatus.FAILED
            payment.cancelled_at = datetime.now()

            # If balance was deducted, refund it
            refund_transaction = None
            if payment.method.value == "balance" and old_status == PaymentStatus.COMPLETED:
                try:
                    refund_transaction = self.wallet_service.add_balance(
                        user_id=payment.user_id,
                        amount=payment.amount,
                        wallet_type=WalletType.REAL,
                        transaction_type=TransactionType.REFUND.value,
                        description=f"Ödeme iptal iadesi - {payment.description or 'Ödeme'}",
                        reference_id=str(payment_id),
                        reference_type="payment_rollback",
                        extra_data={
                            "reason": reason,
                            "original_payment_id": payment_id,
                        },
                    )
                except Exception as e:
                    logger.error(f"Error refunding payment {payment_id}: {e}", exc_info=True)

            self.db.commit()

            logger.info(f"Payment rolled back: payment_id={payment_id}, reason={reason}")

            return {
                "success": True,
                "message": "Ödeme geri alındı",
                "payment_id": payment_id,
                "old_status": old_status.value,
                "new_status": PaymentStatus.FAILED.value,
                "refunded": refund_transaction is not None,
                "refund_transaction_id": refund_transaction.id if refund_transaction else None,
                "reason": reason,
            }

        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error during payment rollback: payment_id={payment_id}, error={e}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ödeme geri alma başarısız: {str(e)}",
            )

    @staticmethod
    def retry_with_exponential_backoff(
        func: Callable,
        max_retries: int = 3,
        initial_delay: float = 5.0,
        backoff_multiplier: float = 5.0,
        *args,
        **kwargs,
    ) -> Any:
        """
        Retry a function with exponential backoff

        Retry delays:
        - 1st retry: 5 seconds
        - 2nd retry: 25 seconds (5 * 5)
        - 3rd retry: 125 seconds (25 * 5)

        Args:
            func: Function to retry
            max_retries: Maximum number of retry attempts (default: 3)
            initial_delay: Initial delay in seconds (default: 5.0)
            backoff_multiplier: Multiplier for exponential backoff (default: 5.0)
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func if successful

        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting operation (attempt {attempt + 1}/{max_retries})")
                result = func(*args, **kwargs)

                if attempt > 0:
                    logger.info(f"Operation succeeded after {attempt + 1} attempts")

                return result

            except Exception as e:
                last_exception = e
                logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries}): {str(e)}")

                # If this is not the last attempt, wait and retry
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= backoff_multiplier
                else:
                    logger.error(
                        f"Operation failed after {max_retries} attempts. Giving up.", exc_info=True
                    )

        # All retries failed
        if last_exception:
            raise last_exception
        else:
            raise Exception("Operation failed with no exception captured")

    @staticmethod
    def safe_execute(
        func: Callable,
        error_message: str = "Operation failed",
        default_return: Any = None,
        log_errors: bool = True,
        *args,
        **kwargs,
    ) -> Any:
        """
        Safely execute a function and return default value on error

        Args:
            func: Function to execute
            error_message: Error message prefix for logging
            default_return: Value to return on error
            log_errors: Whether to log errors
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func if successful, default_return otherwise
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if log_errors:
                logger.error(f"{error_message}: {str(e)}", exc_info=True)
            return default_return


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for preventing cascade failures

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests immediately fail
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception,
    ):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of func

        Raises:
            Exception if circuit is open or func fails
        """
        if self.state == "OPEN":
            # Check if recovery timeout has passed
            if (
                self.last_failure_time
                and time.time() - self.last_failure_time >= self.recovery_timeout
            ):
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                logger.info("Circuit breaker recovered, entering CLOSED state")

            self.failure_count = 0
            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")

            raise e
