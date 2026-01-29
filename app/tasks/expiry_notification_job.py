"""
AGTR Merkezi - Expiry Notification Background Job
Runs daily at 09:00 AM to send server expiry warning notifications
Sends notifications at 7, 3, and 1 day(s) before expiry
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict

from app.models.database import Subscription, SubscriptionStatus, get_session_local
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class ExpiryNotificationMetrics:
    """Metrics for expiry notification job execution"""

    def __init__(self):
        self.total_subscriptions_checked = 0
        self.notifications_7days = 0
        self.notifications_3days = 0
        self.notifications_1day = 0
        self.total_notifications_sent = 0
        self.errors = []

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            "total_subscriptions_checked": self.total_subscriptions_checked,
            "notifications_7days": self.notifications_7days,
            "notifications_3days": self.notifications_3days,
            "notifications_1day": self.notifications_1day,
            "total_notifications_sent": self.total_notifications_sent,
            "errors": self.errors,
        }


def send_expiry_notifications():
    """
    Send expiry warning notifications for subscriptions

    This job:
    1. Finds subscriptions expiring in 7, 3, or 1 day(s)
    2. Checks if notification has already been sent
    3. Sends email warning
    4. Marks notification flag
    """
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("Starting expiry notification job")
    logger.info(f"Execution time: {start_time}")
    logger.info("=" * 80)

    metrics = ExpiryNotificationMetrics()
    db = None

    try:
        # Get database session
        SessionLocal = get_session_local()
        db = SessionLocal()

        # Initialize notification service
        notification_service = NotificationService(db)

        today = date.today()

        # Calculate target dates
        date_7days = today + timedelta(days=7)
        date_3days = today + timedelta(days=3)
        date_1day = today + timedelta(days=1)

        # Process 7-day warnings
        logger.info(f"Checking for subscriptions expiring on {date_7days} (7 days)")
        subscriptions_7days = (
            db.query(Subscription)
            .filter(
                Subscription.next_billing_date == date_7days,
                Subscription.notification_7days_sent == False,
                Subscription.status.in_(
                    [SubscriptionStatus.ACTIVE, SubscriptionStatus.GRACE_PERIOD]
                ),
            )
            .all()
        )

        logger.info(f"Found {len(subscriptions_7days)} subscriptions for 7-day notification")

        for subscription in subscriptions_7days:
            try:
                logger.info(
                    f"Sending 7-day expiry warning: subscription={subscription.id}, "
                    f"server={subscription.game_server_id}, user={subscription.user_id}"
                )

                notification_service.send_expiry_warning(subscription, days=7)

                # Mark notification as sent
                subscription.notification_7days_sent = True
                db.commit()

                metrics.notifications_7days += 1
                metrics.total_notifications_sent += 1

                logger.info(f"✓ 7-day notification sent for subscription {subscription.id}")

            except Exception as e:
                logger.error(
                    f"Error sending 7-day notification for subscription {subscription.id}: {e}",
                    exc_info=True,
                )
                metrics.errors.append(
                    {
                        "subscription_id": subscription.id,
                        "notification_type": "7days",
                        "error": str(e),
                    }
                )
                db.rollback()

        # Process 3-day warnings
        logger.info(f"Checking for subscriptions expiring on {date_3days} (3 days)")
        subscriptions_3days = (
            db.query(Subscription)
            .filter(
                Subscription.next_billing_date == date_3days,
                Subscription.notification_3days_sent == False,
                Subscription.status.in_(
                    [SubscriptionStatus.ACTIVE, SubscriptionStatus.GRACE_PERIOD]
                ),
            )
            .all()
        )

        logger.info(f"Found {len(subscriptions_3days)} subscriptions for 3-day notification")

        for subscription in subscriptions_3days:
            try:
                logger.info(
                    f"Sending 3-day expiry warning: subscription={subscription.id}, "
                    f"server={subscription.game_server_id}, user={subscription.user_id}"
                )

                notification_service.send_expiry_warning(subscription, days=3)

                # Mark notification as sent
                subscription.notification_3days_sent = True
                db.commit()

                metrics.notifications_3days += 1
                metrics.total_notifications_sent += 1

                logger.info(f"✓ 3-day notification sent for subscription {subscription.id}")

            except Exception as e:
                logger.error(
                    f"Error sending 3-day notification for subscription {subscription.id}: {e}",
                    exc_info=True,
                )
                metrics.errors.append(
                    {
                        "subscription_id": subscription.id,
                        "notification_type": "3days",
                        "error": str(e),
                    }
                )
                db.rollback()

        # Process 1-day warnings
        logger.info(f"Checking for subscriptions expiring on {date_1day} (1 day)")
        subscriptions_1day = (
            db.query(Subscription)
            .filter(
                Subscription.next_billing_date == date_1day,
                Subscription.notification_1day_sent == False,
                Subscription.status.in_(
                    [SubscriptionStatus.ACTIVE, SubscriptionStatus.GRACE_PERIOD]
                ),
            )
            .all()
        )

        logger.info(f"Found {len(subscriptions_1day)} subscriptions for 1-day notification")

        for subscription in subscriptions_1day:
            try:
                logger.info(
                    f"Sending 1-day expiry warning: subscription={subscription.id}, "
                    f"server={subscription.game_server_id}, user={subscription.user_id}"
                )

                notification_service.send_expiry_warning(subscription, days=1)

                # Mark notification as sent
                subscription.notification_1day_sent = True
                db.commit()

                metrics.notifications_1day += 1
                metrics.total_notifications_sent += 1

                logger.info(f"✓ 1-day notification sent for subscription {subscription.id}")

            except Exception as e:
                logger.error(
                    f"Error sending 1-day notification for subscription {subscription.id}: {e}",
                    exc_info=True,
                )
                metrics.errors.append(
                    {
                        "subscription_id": subscription.id,
                        "notification_type": "1day",
                        "error": str(e),
                    }
                )
                db.rollback()

        # Calculate total checked
        metrics.total_subscriptions_checked = (
            len(subscriptions_7days) + len(subscriptions_3days) + len(subscriptions_1day)
        )

        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Log summary
        logger.info("=" * 80)
        logger.info("Expiry notification job completed")
        logger.info(f"Execution time: {execution_time:.2f} seconds")
        logger.info("Summary:")
        logger.info(f"  Total checked: {metrics.total_subscriptions_checked}")
        logger.info(f"  7-day notifications: {metrics.notifications_7days}")
        logger.info(f"  3-day notifications: {metrics.notifications_3days}")
        logger.info(f"  1-day notifications: {metrics.notifications_1day}")
        logger.info(f"  Total sent: {metrics.total_notifications_sent}")
        logger.info(f"  Errors: {len(metrics.errors)}")
        logger.info("=" * 80)

        return metrics.to_dict()

    except Exception as e:
        logger.error(f"Fatal error in expiry notification job: {e}", exc_info=True)
        raise

    finally:
        if db:
            db.close()


def send_expiry_notifications_with_error_handling():
    """
    Wrapper function with error handling for APScheduler

    This ensures the job doesn't crash the scheduler if an error occurs
    """
    try:
        return send_expiry_notifications()
    except Exception as e:
        logger.error(f"Expiry notification job failed with error: {e}", exc_info=True)
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


# For manual testing
if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("Running expiry notification job manually...")
    result = send_expiry_notifications()

    print("\n" + "=" * 80)
    print("EXPIRY NOTIFICATION JOB RESULT")
    print("=" * 80)
    for key, value in result.items():
        print(f"{key}: {value}")
    print("=" * 80)
