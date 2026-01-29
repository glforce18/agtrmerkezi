"""
AGTR Merkezi - Subscription Billing Background Job
Runs daily at 03:00 AM to process automatic subscription renewals
"""

import logging
from datetime import date, datetime
from typing import Dict

from app.models.database import Subscription, SubscriptionStatus, get_session_local
from app.services.notification_service import NotificationService
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


class BillingJobMetrics:
    """Metrics for billing job execution"""

    def __init__(self):
        self.total_subscriptions_checked = 0
        self.billing_attempts = 0
        self.successful_billings = 0
        self.failed_billings = 0
        self.grace_period_entered = 0
        self.suspensions = 0
        self.skipped = 0
        self.errors = []

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            "total_subscriptions_checked": self.total_subscriptions_checked,
            "billing_attempts": self.billing_attempts,
            "successful_billings": self.successful_billings,
            "failed_billings": self.failed_billings,
            "grace_period_entered": self.grace_period_entered,
            "suspensions": self.suspensions,
            "skipped": self.skipped,
            "errors": self.errors,
            "success_rate": (
                f"{(self.successful_billings / self.billing_attempts * 100):.2f}%"
                if self.billing_attempts > 0
                else "N/A"
            ),
        }


def process_subscription_billing():
    """
    Process subscription billing for all due subscriptions

    This job:
    1. Finds subscriptions where next_billing_date <= TODAY and auto_renew_enabled = True
    2. Attempts billing for each subscription
    3. Handles success/failure with grace period logic
    4. Sends notifications
    5. Logs detailed metrics
    """
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("Starting subscription billing job")
    logger.info(f"Execution time: {start_time}")
    logger.info("=" * 80)

    metrics = BillingJobMetrics()
    db = None

    try:
        # Get database session
        SessionLocal = get_session_local()
        db = SessionLocal()

        # Initialize services
        subscription_service = SubscriptionService(db)
        notification_service = NotificationService(db)

        # Find subscriptions due for billing
        today = date.today()
        due_subscriptions = (
            db.query(Subscription)
            .filter(
                Subscription.next_billing_date <= today,
                Subscription.auto_renew_enabled == True,
                Subscription.status.in_(
                    [SubscriptionStatus.ACTIVE, SubscriptionStatus.GRACE_PERIOD]
                ),
            )
            .all()
        )

        metrics.total_subscriptions_checked = len(due_subscriptions)

        logger.info(f"Found {metrics.total_subscriptions_checked} subscriptions due for billing")

        # Process each subscription
        for subscription in due_subscriptions:
            try:
                logger.info(
                    f"Processing subscription {subscription.id} "
                    f"(server: {subscription.game_server_id}, user: {subscription.user_id})"
                )

                metrics.billing_attempts += 1

                # Attempt billing
                result = subscription_service.attempt_billing(
                    subscription_id=subscription.id,
                    ip_address="127.0.0.1",  # System IP
                    user_agent="BillingJob/1.0",
                )

                if result["success"]:
                    # Billing successful
                    metrics.successful_billings += 1

                    logger.info(
                        f"✓ Billing successful for subscription {subscription.id}: "
                        f"amount={result['amount']}, new_expiry={result['new_expiry_date']}"
                    )

                    # Send success notification
                    try:
                        notification_service.send_renewal_success(subscription)
                    except Exception as e:
                        logger.error(f"Error sending success notification: {e}", exc_info=True)
                        metrics.errors.append(
                            {
                                "subscription_id": subscription.id,
                                "error": f"Notification failed: {str(e)}",
                            }
                        )

                else:
                    # Billing failed
                    metrics.failed_billings += 1

                    failure_status = result.get("status", "failed")
                    failure_count = result.get("failure_count", 0)

                    logger.warning(
                        f"✗ Billing failed for subscription {subscription.id}: "
                        f"status={failure_status}, message={result['message']}, "
                        f"failure_count={failure_count}"
                    )

                    # Track specific failure types
                    if failure_status == "grace_period":
                        metrics.grace_period_entered += 1

                        # Send failure notification (first attempt)
                        try:
                            notification_service.send_renewal_failed(
                                subscription, first_attempt=True
                            )
                        except Exception as e:
                            logger.error(f"Error sending failure notification: {e}", exc_info=True)

                    elif failure_status == "suspended":
                        metrics.suspensions += 1

                        # Send suspension notification
                        try:
                            notification_service.send_server_suspended(subscription)
                        except Exception as e:
                            logger.error(
                                f"Error sending suspension notification: {e}", exc_info=True
                            )

                    else:
                        # Regular failure, send notification
                        try:
                            notification_service.send_renewal_failed(
                                subscription, first_attempt=(failure_count == 1)
                            )
                        except Exception as e:
                            logger.error(f"Error sending failure notification: {e}", exc_info=True)

            except Exception as e:
                logger.error(f"Error processing subscription {subscription.id}: {e}", exc_info=True)
                metrics.errors.append({"subscription_id": subscription.id, "error": str(e)})

        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Log summary
        logger.info("=" * 80)
        logger.info("Billing job completed")
        logger.info(f"Execution time: {execution_time:.2f} seconds")
        logger.info("Summary:")
        logger.info(f"  Total checked: {metrics.total_subscriptions_checked}")
        logger.info(f"  Billing attempts: {metrics.billing_attempts}")
        logger.info(f"  ✓ Successful: {metrics.successful_billings}")
        logger.info(f"  ✗ Failed: {metrics.failed_billings}")
        logger.info(f"  ⚠ Grace period: {metrics.grace_period_entered}")
        logger.info(f"  ⛔ Suspended: {metrics.suspensions}")
        logger.info(f"  ⊘ Skipped: {metrics.skipped}")
        logger.info(f"  ⚡ Errors: {len(metrics.errors)}")
        if metrics.billing_attempts > 0:
            success_rate = (metrics.successful_billings / metrics.billing_attempts) * 100
            logger.info(f"  Success rate: {success_rate:.2f}%")
        logger.info("=" * 80)

        # Alert if success rate is too low
        if metrics.billing_attempts > 0:
            success_rate = (metrics.successful_billings / metrics.billing_attempts) * 100
            if success_rate < 90:  # Less than 90% success rate
                logger.error(
                    f"⚠ WARNING: Low billing success rate: {success_rate:.2f}% "
                    f"({metrics.successful_billings}/{metrics.billing_attempts})"
                )
                # TODO: Send admin alert

        return metrics.to_dict()

    except Exception as e:
        logger.error(f"Fatal error in billing job: {e}", exc_info=True)
        raise

    finally:
        if db:
            db.close()


def process_subscription_billing_with_error_handling():
    """
    Wrapper function with error handling for APScheduler

    This ensures the job doesn't crash the scheduler if an error occurs
    """
    try:
        return process_subscription_billing()
    except Exception as e:
        logger.error(f"Billing job failed with error: {e}", exc_info=True)
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


# For manual testing
if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("Running billing job manually...")
    result = process_subscription_billing()

    print("\n" + "=" * 80)
    print("BILLING JOB RESULT")
    print("=" * 80)
    for key, value in result.items():
        print(f"{key}: {value}")
    print("=" * 80)
