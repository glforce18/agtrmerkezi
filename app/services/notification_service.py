"""
AGTR Merkezi - Notification Service
Handles in-app notifications and email notifications for subscriptions and servers
"""

import logging

from sqlalchemy.orm import Session

from app.models.database import Notification, Subscription, User

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for creating and sending notifications"""

    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        user_id: int,
        type: str,
        title: str,
        message: str,
        link: str = None,
        send_email: bool = False,
    ) -> Notification:
        """
        Create a new in-app notification

        Args:
            user_id: User ID
            type: Notification type
            title: Notification title
            message: Notification message
            link: Optional link
            send_email: Whether to send email notification

        Returns:
            Created Notification object
        """
        try:
            notification = Notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                link=link,
                is_email_sent=send_email,
            )

            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)

            logger.info(f"Notification created: user={user_id}, type={type}, title={title}")

            # Send email if requested
            if send_email:
                try:
                    self._send_email_notification(user_id, title, message, link)
                except Exception as e:
                    logger.error(f"Error sending email notification: {e}", exc_info=True)

            return notification

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification: {e}", exc_info=True)
            raise

    def _send_email_notification(self, user_id: int, title: str, message: str, link: str = None):
        """Send email notification to user"""
        try:
            from app.services.email import EmailService

            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.email:
                logger.warning(f"User {user_id} has no email, skipping email notification")
                return

            email_service = EmailService()
            email_service.send_email(
                to_email=user.email,
                subject=title,
                template_name="generic_notification",
                context={
                    "user": user,
                    "title": title,
                    "message": message,
                    "link": link,
                },
            )

            logger.info(f"Email notification sent to user {user_id}")

        except Exception as e:
            logger.error(f"Error sending email notification: {e}", exc_info=True)

    # ==================== SUBSCRIPTION NOTIFICATIONS ====================

    def send_expiry_warning(self, subscription: Subscription, days: int):
        """
        Send server expiry warning notification

        Args:
            subscription: Subscription object
            days: Number of days until expiry (7, 3, or 1)
        """
        try:
            user = subscription.user
            server = subscription.game_server

            if days == 7:
                title = "Sunucunuz 7 Gün İçinde Sona Eriyor"
                notification_type = "server_expiring_7days"
            elif days == 3:
                title = "Sunucunuz 3 Gün İçinde Sona Eriyor"
                notification_type = "server_expiring_3days"
            elif days == 1:
                title = "Sunucunuz Yarın Sona Eriyor"
                notification_type = "server_expiring_1day"
            else:
                title = f"Sunucunuz {days} Gün İçinde Sona Eriyor"
                notification_type = "server_expiring"

            # Calculate amount needed
            amount = subscription.calculate_billing_amount()

            # Get current balance
            if subscription.payment_method.value == "real":
                current_balance = user.balance if user.balance else 0.0
                wallet_name = "TL Bakiye"
            else:
                current_balance = user.balance_coin if user.balance_coin else 0.0
                wallet_name = "Armor"

            message = (
                f"{server.name} sunucunuzun süresi {subscription.next_billing_date.strftime('%d.%m.%Y')} "
                f"tarihinde dolacak. "
            )

            if subscription.auto_renew_enabled:
                if current_balance >= amount:
                    message += f"Otomatik yenileme aktif. {amount:.2f} TL bakiyenizden çekilecek."
                else:
                    message += (
                        f"Otomatik yenileme aktif ancak bakiyeniz yetersiz! "
                        f"Gerekli: {amount:.2f} {wallet_name}, "
                        f"Mevcut: {current_balance:.2f} {wallet_name}. "
                        f"Lütfen bakiye yükleyin."
                    )
            else:
                message += "Otomatik yenileme kapalı. Sunucunuzu yenilemek için bakiye yükleyin."

            # Create notification
            self.create_notification(
                user_id=user.id,
                type=notification_type,
                title=title,
                message=message,
                link=f"/panel/servers/{server.id}",
                send_email=True,
            )

            # Send email with template
            try:
                from app.services.email import EmailService

                if user.email:
                    email_service = EmailService()
                    email_service.send_email(
                        to_email=user.email,
                        subject=title,
                        template_name="expiry_warning",
                        context={
                            "user": user,
                            "server": server,
                            "subscription": subscription,
                            "days": days,
                            "amount": amount,
                            "current_balance": current_balance,
                            "wallet_name": wallet_name,
                            "expiry_date": subscription.next_billing_date.strftime("%d.%m.%Y"),
                        },
                    )
            except Exception as e:
                logger.error(f"Error sending expiry warning email: {e}", exc_info=True)

            logger.info(f"Expiry warning sent: subscription={subscription.id}, days={days}")

        except Exception as e:
            logger.error(f"Error sending expiry warning: {e}", exc_info=True)
            raise

    def send_renewal_success(self, subscription: Subscription):
        """
        Send successful renewal notification

        Args:
            subscription: Subscription object
        """
        try:
            user = subscription.user
            server = subscription.game_server

            amount = subscription.calculate_billing_amount()

            title = "Sunucunuz Başarıyla Yenilendi"
            message = (
                f"{server.name} sunucunuz otomatik olarak yenilendi. "
                f"{amount:.2f} TL bakiyenizden çekildi. "
                f"Yeni bitiş tarihi: {subscription.next_billing_date.strftime('%d.%m.%Y')}"
            )

            # Create notification
            self.create_notification(
                user_id=user.id,
                type="renewal_success",
                title=title,
                message=message,
                link=f"/panel/servers/{server.id}",
                send_email=True,
            )

            # Send email with template
            try:
                from app.services.email import EmailService

                if user.email:
                    email_service = EmailService()
                    email_service.send_email(
                        to_email=user.email,
                        subject=title,
                        template_name="renewal_success",
                        context={
                            "user": user,
                            "server": server,
                            "subscription": subscription,
                            "amount": amount,
                            "new_expiry_date": subscription.next_billing_date.strftime("%d.%m.%Y"),
                        },
                    )
            except Exception as e:
                logger.error(f"Error sending renewal success email: {e}", exc_info=True)

            logger.info(f"Renewal success notification sent: subscription={subscription.id}")

        except Exception as e:
            logger.error(f"Error sending renewal success notification: {e}", exc_info=True)
            raise

    def send_renewal_failed(self, subscription: Subscription, first_attempt: bool = True):
        """
        Send renewal failed notification

        Args:
            subscription: Subscription object
            first_attempt: Whether this is the first failure
        """
        try:
            user = subscription.user
            server = subscription.game_server

            amount = subscription.calculate_billing_amount()

            if first_attempt:
                title = "Sunucu Yenileme Başarısız - Lütfen Bakiye Yükleyin"
                message = (
                    f"{server.name} sunucunuzun otomatik yenilemesi başarısız oldu. "
                    f"Yetersiz bakiye. Gerekli: {amount:.2f} TL. "
                    f"3 gün yetkisiz kullanım süresi verildi. Bu süre içinde bakiye yüklemezseniz "
                    f"sunucunuz askıya alınacak."
                )
            else:
                title = "Sunucu Yenileme Tekrar Başarısız"
                message = (
                    f"{server.name} sunucunuzun otomatik yenilemesi tekrar başarısız oldu. "
                    f"Gerekli: {amount:.2f} TL. "
                    f"Başarısız deneme: {subscription.failure_count}. "
                    f"3 başarısız denemeden sonra sunucunuz askıya alınacak."
                )

            # Create notification
            self.create_notification(
                user_id=user.id,
                type="renewal_failed",
                title=title,
                message=message,
                link=f"/wallet",
                send_email=True,
            )

            # Send email with template
            try:
                from app.services.email import EmailService

                if user.email:
                    email_service = EmailService()
                    email_service.send_email(
                        to_email=user.email,
                        subject=title,
                        template_name="renewal_failed",
                        context={
                            "user": user,
                            "server": server,
                            "subscription": subscription,
                            "amount": amount,
                            "first_attempt": first_attempt,
                            "failure_count": subscription.failure_count,
                        },
                    )
            except Exception as e:
                logger.error(f"Error sending renewal failed email: {e}", exc_info=True)

            logger.info(
                f"Renewal failed notification sent: subscription={subscription.id}, "
                f"first_attempt={first_attempt}"
            )

        except Exception as e:
            logger.error(f"Error sending renewal failed notification: {e}", exc_info=True)
            raise

    def send_server_suspended(self, subscription: Subscription):
        """
        Send server suspended notification

        Args:
            subscription: Subscription object
        """
        try:
            user = subscription.user
            server = subscription.game_server

            amount = subscription.calculate_billing_amount()

            title = "Sunucunuz Askıya Alındı"
            message = (
                f"{server.name} sunucunuz 3 başarısız ödeme denemesi sonrasında askıya alındı. "
                f"Sunucunuzu yeniden aktifleştirmek için {amount:.2f} TL bakiye yükleyin "
                f"ve aboneliğinizi yeniden etkinleştirin."
            )

            # Create notification
            self.create_notification(
                user_id=user.id,
                type="server_suspended",
                title=title,
                message=message,
                link=f"/wallet",
                send_email=True,
            )

            # Send email with template
            try:
                from app.services.email import EmailService

                if user.email:
                    email_service = EmailService()
                    email_service.send_email(
                        to_email=user.email,
                        subject=title,
                        template_name="server_suspended",
                        context={
                            "user": user,
                            "server": server,
                            "subscription": subscription,
                            "amount": amount,
                        },
                    )
            except Exception as e:
                logger.error(f"Error sending suspension email: {e}", exc_info=True)

            logger.info(f"Suspension notification sent: subscription={subscription.id}")

        except Exception as e:
            logger.error(f"Error sending suspension notification: {e}", exc_info=True)
            raise

    def send_grace_period_reminder(self, subscription: Subscription):
        """
        Send grace period reminder notification

        Args:
            subscription: Subscription object
        """
        try:
            user = subscription.user
            server = subscription.game_server

            amount = subscription.calculate_billing_amount()

            title = "Son Uyarı - Sunucunuz Askıya Alınacak"
            message = (
                f"{server.name} sunucunuz yetkisiz kullanım süresinde. "
                f"Hemen {amount:.2f} TL bakiye yükleyin, aksi takdirde sunucunuz askıya alınacak."
            )

            # Create notification
            self.create_notification(
                user_id=user.id,
                type="grace_period_started",
                title=title,
                message=message,
                link=f"/wallet",
                send_email=True,
            )

            logger.info(f"Grace period reminder sent: subscription={subscription.id}")

        except Exception as e:
            logger.error(f"Error sending grace period reminder: {e}", exc_info=True)
            raise
