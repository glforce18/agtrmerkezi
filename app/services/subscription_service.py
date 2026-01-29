"""
AGTR Merkezi - Subscription Service
Automatic billing and subscription management
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import (
    BillingHistoryStatus,
    BillingPeriod,
    GameServer,
    ServerStatus,
    Subscription,
    SubscriptionBillingHistory,
    SubscriptionStatus,
    TransactionType,
    User,
    WalletType,
)
from app.services.wallet import WalletService

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Subscription and automatic billing service"""

    def __init__(self, db: Session):
        self.db = db
        self.wallet_service = WalletService(db)

    def create_subscription(
        self,
        game_server_id: int,
        user_id: int,
        billing_period: BillingPeriod = BillingPeriod.MONTHLY,
        auto_renew_enabled: bool = True,
        payment_method: WalletType = WalletType.REAL,
        monthly_amount: float = None,
        initial_expiry_date: datetime = None,
    ) -> Subscription:
        """
        Create a new subscription for a game server

        Args:
            game_server_id: Game server ID
            user_id: User ID (owner)
            billing_period: Billing period (monthly, quarterly, etc.)
            auto_renew_enabled: Enable automatic renewal
            payment_method: Payment wallet (REAL or COIN)
            monthly_amount: Monthly price (from server)
            initial_expiry_date: Initial expiry date from first payment

        Returns:
            Created Subscription object
        """
        try:
            # Validate game server exists
            server = (
                self.db.query(GameServer)
                .filter(GameServer.id == game_server_id, GameServer.owner_id == user_id)
                .first()
            )

            if not server:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sunucu bulunamadı veya size ait değil",
                )

            # Check if subscription already exists
            existing = (
                self.db.query(Subscription)
                .filter(Subscription.game_server_id == game_server_id)
                .first()
            )

            if existing:
                logger.warning(f"Subscription already exists for server {game_server_id}")
                return existing

            # Calculate next billing date
            if initial_expiry_date:
                next_billing_date = (
                    initial_expiry_date.date()
                    if isinstance(initial_expiry_date, datetime)
                    else initial_expiry_date
                )
            else:
                next_billing_date = server.expires_at.date() if server.expires_at else date.today()

            # Use server's monthly price if not provided
            if monthly_amount is None:
                monthly_amount = server.monthly_price

            # Create subscription
            subscription = Subscription(
                game_server_id=game_server_id,
                user_id=user_id,
                billing_period=billing_period,
                auto_renew_enabled=auto_renew_enabled,
                payment_method=payment_method,
                next_billing_date=next_billing_date,
                status=SubscriptionStatus.ACTIVE,
                monthly_amount=monthly_amount,
            )

            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)

            logger.info(
                f"Subscription created: id={subscription.id}, server={game_server_id}, "
                f"user={user_id}, next_billing={next_billing_date}"
            )

            return subscription

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating subscription: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Abonelik oluşturulamadı: {str(e)}",
            )

    def attempt_billing(
        self, subscription_id: int, ip_address: str = None, user_agent: str = None
    ) -> Dict[str, Any]:
        """
        Attempt to bill a subscription

        This is the core billing logic with wallet deduction, atomic operations,
        and comprehensive error handling.

        Args:
            subscription_id: Subscription ID
            ip_address: Request IP (for audit)
            user_agent: Request user agent (for audit)

        Returns:
            Dict with status, message, and billing history record
        """
        try:
            # Lock subscription for update (prevents race conditions)
            subscription = (
                self.db.query(Subscription)
                .filter(Subscription.id == subscription_id)
                .with_for_update()
                .first()
            )

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Abonelik bulunamadı"
                )

            # Check if auto-renew is enabled
            if not subscription.auto_renew_enabled:
                logger.info(f"Subscription {subscription_id} has auto-renew disabled, skipping")
                return {
                    "success": False,
                    "message": "Otomatik yenileme kapalı",
                    "billing_history": None,
                }

            # Check if subscription is active or in grace period
            if subscription.status not in [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.GRACE_PERIOD,
            ]:
                logger.info(
                    f"Subscription {subscription_id} status is {subscription.status}, skipping"
                )
                return {
                    "success": False,
                    "message": f"Abonelik durumu uygun değil: {subscription.status.value}",
                    "billing_history": None,
                }

            # Calculate billing amount
            amount = subscription.calculate_billing_amount()
            payment_method = subscription.payment_method

            # Get user balance (with lock)
            user = (
                self.db.query(User)
                .filter(User.id == subscription.user_id)
                .with_for_update()
                .first()
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı"
                )

            # Get current balance
            if payment_method == WalletType.REAL:
                current_balance = float(user.balance) if user.balance is not None else 0.0
            else:
                current_balance = float(user.balance_coin) if user.balance_coin is not None else 0.0

            # Check sufficient balance
            if current_balance < amount:
                return self._handle_insufficient_balance(
                    subscription=subscription,
                    amount=amount,
                    current_balance=current_balance,
                    payment_method=payment_method,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )

            # Deduct from wallet (atomic operation)
            try:
                transaction = self.wallet_service.deduct_balance(
                    user_id=subscription.user_id,
                    amount=amount,
                    wallet_type=payment_method,
                    transaction_type=TransactionType.PAYMENT.value,
                    description=f"Sunucu otomatik yenileme - {subscription.game_server.name}",
                    reference_id=str(subscription.game_server_id),
                    reference_type="subscription_renewal",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    extra_data={
                        "subscription_id": subscription_id,
                        "billing_period": subscription.billing_period.value,
                        "months": subscription.get_billing_months(),
                    },
                )
            except HTTPException as e:
                return self._handle_billing_failure(
                    subscription=subscription,
                    amount=amount,
                    balance_before=current_balance,
                    balance_after=current_balance,
                    failure_reason=str(e.detail),
                    payment_method=payment_method,
                )

            # Extend subscription period
            months = subscription.get_billing_months()
            new_expiry_date = subscription.next_billing_date + relativedelta(months=months)

            # Update subscription
            subscription.next_billing_date = new_expiry_date
            subscription.last_billing_date = date.today()
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.failure_count = 0
            subscription.last_failure_reason = None
            subscription.grace_period_started_at = None

            # Update game server expiry
            server = subscription.game_server
            if server.expires_at:
                server.expires_at = datetime.combine(new_expiry_date, datetime.min.time())
            else:
                server.expires_at = datetime.combine(new_expiry_date, datetime.min.time())

            server.last_payment_date = datetime.now()

            # Reset notification flags for next cycle
            subscription.notification_7days_sent = False
            subscription.notification_3days_sent = False
            subscription.notification_1day_sent = False

            # Create billing history record
            billing_history = SubscriptionBillingHistory(
                subscription_id=subscription.id,
                user_id=subscription.user_id,
                game_server_id=subscription.game_server_id,
                billing_date=date.today(),
                billing_period=subscription.billing_period,
                amount=amount,
                payment_method=payment_method,
                status=BillingHistoryStatus.SUCCESS,
                balance_before=current_balance,
                balance_after=current_balance - amount,
                transaction_id=transaction.id,
                completed_at=datetime.now(),
            )
            self.db.add(billing_history)

            self.db.commit()

            logger.info(
                f"Billing successful: subscription={subscription_id}, "
                f"amount={amount}, new_expiry={new_expiry_date}"
            )

            return {
                "success": True,
                "message": "Ödeme başarılı",
                "billing_history": billing_history,
                "new_expiry_date": new_expiry_date,
                "amount": amount,
            }

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Billing error for subscription {subscription_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Faturalama hatası: {str(e)}",
            )

    def _handle_insufficient_balance(
        self,
        subscription: Subscription,
        amount: float,
        current_balance: float,
        payment_method: WalletType,
        ip_address: str = None,
        user_agent: str = None,
    ) -> Dict[str, Any]:
        """Handle insufficient balance scenario"""

        subscription.failure_count += 1
        failure_reason = f"Yetersiz bakiye. Mevcut: {current_balance:.2f}, Gerekli: {amount:.2f}"
        subscription.last_failure_reason = failure_reason

        # First failure: Enter grace period
        if subscription.failure_count == 1:
            subscription.status = SubscriptionStatus.GRACE_PERIOD
            subscription.grace_period_started_at = datetime.now()
            logger.warning(
                f"Subscription {subscription.id} entered grace period. "
                f"Insufficient balance: {current_balance} < {amount}"
            )
            status_message = "grace_period"

        # Third failure: Suspend server
        elif subscription.failure_count >= 3:
            subscription.status = SubscriptionStatus.SUSPENDED
            subscription.suspended_at = datetime.now()

            # Suspend game server
            server = subscription.game_server
            server.status = ServerStatus.SUSPENDED

            logger.error(
                f"Subscription {subscription.id} suspended after 3 failed attempts. "
                f"Server {server.id} suspended."
            )
            status_message = "suspended"
        else:
            status_message = "failed"

        # Create billing history record
        billing_history = SubscriptionBillingHistory(
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            game_server_id=subscription.game_server_id,
            billing_date=date.today(),
            billing_period=subscription.billing_period,
            amount=amount,
            payment_method=payment_method,
            status=BillingHistoryStatus.FAILED,
            failure_reason=failure_reason,
            retry_count=subscription.failure_count,
            balance_before=current_balance,
            balance_after=current_balance,
            completed_at=datetime.now(),
        )
        self.db.add(billing_history)
        self.db.commit()

        return {
            "success": False,
            "message": failure_reason,
            "status": status_message,
            "billing_history": billing_history,
            "failure_count": subscription.failure_count,
        }

    def _handle_billing_failure(
        self,
        subscription: Subscription,
        amount: float,
        balance_before: float,
        balance_after: float,
        failure_reason: str,
        payment_method: WalletType,
    ) -> Dict[str, Any]:
        """Handle general billing failure"""

        subscription.failure_count += 1
        subscription.last_failure_reason = failure_reason

        # Create billing history record
        billing_history = SubscriptionBillingHistory(
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            game_server_id=subscription.game_server_id,
            billing_date=date.today(),
            billing_period=subscription.billing_period,
            amount=amount,
            payment_method=payment_method,
            status=BillingHistoryStatus.FAILED,
            failure_reason=failure_reason,
            retry_count=subscription.failure_count,
            balance_before=balance_before,
            balance_after=balance_after,
            completed_at=datetime.now(),
        )
        self.db.add(billing_history)
        self.db.commit()

        return {
            "success": False,
            "message": failure_reason,
            "billing_history": billing_history,
            "failure_count": subscription.failure_count,
        }

    def extend_subscription(
        self,
        subscription_id: int,
        months: int,
        payment_id: int = None,
        admin_override: bool = False,
    ) -> Subscription:
        """
        Manually extend subscription (from payment or admin action)

        Args:
            subscription_id: Subscription ID
            months: Number of months to extend
            payment_id: Related payment ID (optional)
            admin_override: Admin manual extension

        Returns:
            Updated Subscription object
        """
        try:
            subscription = (
                self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
            )

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Abonelik bulunamadı"
                )

            # Calculate new expiry date
            new_expiry_date = subscription.next_billing_date + relativedelta(months=months)

            # Update subscription
            subscription.next_billing_date = new_expiry_date
            subscription.last_billing_date = date.today()

            # If was suspended or in grace period, reactivate
            if subscription.status in [
                SubscriptionStatus.SUSPENDED,
                SubscriptionStatus.GRACE_PERIOD,
            ]:
                subscription.status = SubscriptionStatus.ACTIVE
                subscription.suspended_at = None
                subscription.grace_period_started_at = None
                subscription.failure_count = 0

                # Reactivate server
                server = subscription.game_server
                if server.status == ServerStatus.SUSPENDED:
                    server.status = ServerStatus.STOPPED

            # Update game server expiry
            server = subscription.game_server
            server.expires_at = datetime.combine(new_expiry_date, datetime.min.time())
            server.last_payment_date = datetime.now()

            # Reset notification flags
            subscription.notification_7days_sent = False
            subscription.notification_3days_sent = False
            subscription.notification_1day_sent = False

            self.db.commit()
            self.db.refresh(subscription)

            logger.info(
                f"Subscription extended: id={subscription_id}, months={months}, "
                f"new_expiry={new_expiry_date}, admin={admin_override}"
            )

            return subscription

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error extending subscription {subscription_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Abonelik uzatılamadı: {str(e)}",
            )

    def cancel_subscription(
        self, subscription_id: int, user_id: int, reason: str = None
    ) -> Subscription:
        """
        Cancel a subscription (user-initiated)

        Server continues until expiry, but won't auto-renew
        """
        try:
            subscription = (
                self.db.query(Subscription)
                .filter(Subscription.id == subscription_id, Subscription.user_id == user_id)
                .first()
            )

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Abonelik bulunamadı"
                )

            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.now()
            subscription.auto_renew_enabled = False
            subscription.last_failure_reason = reason

            self.db.commit()
            self.db.refresh(subscription)

            logger.info(
                f"Subscription cancelled: id={subscription_id}, user={user_id}, reason={reason}"
            )

            return subscription

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cancelling subscription {subscription_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Abonelik iptal edilemedi: {str(e)}",
            )

    def suspend_subscription(self, subscription_id: int, reason: str = None) -> Subscription:
        """Suspend a subscription (payment failure or admin action)"""
        try:
            subscription = (
                self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
            )

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Abonelik bulunamadı"
                )

            subscription.status = SubscriptionStatus.SUSPENDED
            subscription.suspended_at = datetime.now()
            subscription.last_failure_reason = reason

            # Suspend game server
            server = subscription.game_server
            server.status = ServerStatus.SUSPENDED

            self.db.commit()
            self.db.refresh(subscription)

            logger.info(f"Subscription suspended: id={subscription_id}, reason={reason}")

            return subscription

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error suspending subscription {subscription_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Abonelik askıya alınamadı: {str(e)}",
            )

    def reactivate_subscription(self, subscription_id: int, user_id: int) -> Subscription:
        """Reactivate a suspended subscription"""
        try:
            subscription = (
                self.db.query(Subscription)
                .filter(Subscription.id == subscription_id, Subscription.user_id == user_id)
                .first()
            )

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Abonelik bulunamadı"
                )

            if subscription.status != SubscriptionStatus.SUSPENDED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Abonelik askıda değil"
                )

            # Check sufficient balance for reactivation
            amount = subscription.calculate_billing_amount()
            current_balance = self.wallet_service.get_balance(
                user_id=user_id, wallet_type=subscription.payment_method
            )

            if current_balance < amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Yetersiz bakiye. Gerekli: {amount:.2f}, Mevcut: {current_balance:.2f}",
                )

            subscription.status = SubscriptionStatus.ACTIVE
            subscription.suspended_at = None
            subscription.grace_period_started_at = None
            subscription.failure_count = 0
            subscription.last_failure_reason = None

            # Reactivate server
            server = subscription.game_server
            if server.status == ServerStatus.SUSPENDED:
                server.status = ServerStatus.STOPPED

            self.db.commit()
            self.db.refresh(subscription)

            logger.info(f"Subscription reactivated: id={subscription_id}")

            return subscription

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error reactivating subscription {subscription_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Abonelik yeniden etkinleştirilemedi: {str(e)}",
            )

    def toggle_auto_renew(self, subscription_id: int, user_id: int, enabled: bool) -> Subscription:
        """Toggle auto-renewal on/off"""
        try:
            subscription = (
                self.db.query(Subscription)
                .filter(Subscription.id == subscription_id, Subscription.user_id == user_id)
                .first()
            )

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Abonelik bulunamadı"
                )

            subscription.auto_renew_enabled = enabled
            self.db.commit()
            self.db.refresh(subscription)

            logger.info(f"Auto-renew toggled: subscription={subscription_id}, enabled={enabled}")

            return subscription

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error toggling auto-renew for subscription {subscription_id}: {e}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Otomatik yenileme ayarı değiştirilemedi: {str(e)}",
            )

    def change_payment_method(
        self, subscription_id: int, user_id: int, payment_method: WalletType
    ) -> Subscription:
        """Change payment method (TL or Armor wallet)"""
        try:
            subscription = (
                self.db.query(Subscription)
                .filter(Subscription.id == subscription_id, Subscription.user_id == user_id)
                .first()
            )

            if not subscription:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Abonelik bulunamadı"
                )

            subscription.payment_method = payment_method
            self.db.commit()
            self.db.refresh(subscription)

            logger.info(
                f"Payment method changed: subscription={subscription_id}, "
                f"method={payment_method.value}"
            )

            return subscription

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error changing payment method for subscription {subscription_id}: {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ödeme yöntemi değiştirilemedi: {str(e)}",
            )

    def get_subscription_by_server(self, game_server_id: int) -> Optional[Subscription]:
        """Get subscription by game server ID"""
        return (
            self.db.query(Subscription)
            .filter(Subscription.game_server_id == game_server_id)
            .first()
        )

    def get_user_subscriptions(self, user_id: int) -> list[Subscription]:
        """Get all subscriptions for a user"""
        return (
            self.db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .order_by(Subscription.next_billing_date.asc())
            .all()
        )

    def get_billing_history(
        self, subscription_id: int, user_id: int, limit: int = 50
    ) -> list[SubscriptionBillingHistory]:
        """Get billing history for a subscription"""
        return (
            self.db.query(SubscriptionBillingHistory)
            .filter(
                SubscriptionBillingHistory.subscription_id == subscription_id,
                SubscriptionBillingHistory.user_id == user_id,
            )
            .order_by(SubscriptionBillingHistory.billing_date.desc())
            .limit(limit)
            .all()
        )
