"""
AGTR Merkezi - Admin Subscription Management API
Admin dashboard for subscription management, statistics, and monitoring
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, require_admin
from app.models.database import (
    BillingHistoryStatus,
    Subscription,
    SubscriptionBillingHistory,
    SubscriptionStatus,
    User,
    get_db,
)
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/subscriptions", tags=["Admin - Subscriptions"])


# ==================== PYDANTIC MODELS ====================


class AdminSubscriptionResponse(BaseModel):
    """Admin subscription response with full details"""

    id: int
    game_server_id: int
    server_name: str
    user_id: int
    username: str
    user_email: Optional[str] = None
    billing_period: str
    auto_renew_enabled: bool
    payment_method: str
    next_billing_date: str
    last_billing_date: Optional[str] = None
    status: str
    monthly_amount: float
    failure_count: int
    last_failure_reason: Optional[str] = None
    grace_period_started_at: Optional[str] = None
    suspended_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class SubscriptionStatsResponse(BaseModel):
    """Subscription statistics response"""

    total_subscriptions: int
    active_subscriptions: int
    cancelled_subscriptions: int
    suspended_subscriptions: int
    grace_period_subscriptions: int
    expired_subscriptions: int
    total_monthly_revenue: float
    total_annual_revenue: float
    auto_renew_rate: float
    churn_rate: float
    average_subscription_value: float


class ExtendSubscriptionRequest(BaseModel):
    """Extend subscription request"""

    months: int = Field(..., description="Number of months to extend", ge=1, le=12)
    reason: Optional[str] = Field(None, description="Admin note for extension")


class SuspendSubscriptionRequest(BaseModel):
    """Suspend subscription request"""

    reason: str = Field(..., description="Reason for suspension")


# ==================== API ENDPOINTS ====================


@router.get("/", response_model=List[AdminSubscriptionResponse])
async def list_all_subscriptions(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    auto_renew: Optional[bool] = Query(None, description="Filter by auto-renew"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all subscriptions with filters (Admin only)

    Filters:
    - status: active, cancelled, suspended, expired, grace_period
    - auto_renew: true/false
    - payment_method: real/coin
    - user_id: specific user
    """
    # Check admin permission
    require_admin(current_user)

    try:
        # Build query
        query = db.query(Subscription)

        # Apply filters
        if status_filter:
            try:
                status_enum = SubscriptionStatus(status_filter)
                query = query.filter(Subscription.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Geçersiz durum: {status_filter}",
                )

        if auto_renew is not None:
            query = query.filter(Subscription.auto_renew_enabled == auto_renew)

        if payment_method:
            query = query.filter(Subscription.payment_method == payment_method)

        if user_id:
            query = query.filter(Subscription.user_id == user_id)

        # Get total count
        query.count()

        # Get subscriptions with pagination
        subscriptions = (
            query.order_by(Subscription.created_at.desc()).limit(limit).offset(offset).all()
        )

        # Format response
        result = []
        for sub in subscriptions:
            result.append(
                {
                    "id": sub.id,
                    "game_server_id": sub.game_server_id,
                    "server_name": sub.game_server.name,
                    "user_id": sub.user_id,
                    "username": sub.user.username,
                    "user_email": sub.user.email,
                    "billing_period": sub.billing_period.value,
                    "auto_renew_enabled": sub.auto_renew_enabled,
                    "payment_method": sub.payment_method.value,
                    "next_billing_date": sub.next_billing_date.strftime("%Y-%m-%d"),
                    "last_billing_date": (
                        sub.last_billing_date.strftime("%Y-%m-%d")
                        if sub.last_billing_date
                        else None
                    ),
                    "status": sub.status.value,
                    "monthly_amount": sub.monthly_amount,
                    "failure_count": sub.failure_count,
                    "last_failure_reason": sub.last_failure_reason,
                    "grace_period_started_at": (
                        sub.grace_period_started_at.isoformat()
                        if sub.grace_period_started_at
                        else None
                    ),
                    "suspended_at": sub.suspended_at.isoformat() if sub.suspended_at else None,
                    "cancelled_at": sub.cancelled_at.isoformat() if sub.cancelled_at else None,
                    "created_at": sub.created_at.isoformat(),
                }
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing subscriptions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Abonelikler listelenemedi"
        )


@router.get("/stats", response_model=SubscriptionStatsResponse)
async def get_subscription_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get subscription statistics and revenue metrics (Admin only)"""
    # Check admin permission
    require_admin(current_user)

    try:
        # Total subscriptions
        total = db.query(Subscription).count()

        # Status breakdown
        active = (
            db.query(Subscription).filter(Subscription.status == SubscriptionStatus.ACTIVE).count()
        )

        cancelled = (
            db.query(Subscription)
            .filter(Subscription.status == SubscriptionStatus.CANCELLED)
            .count()
        )

        suspended = (
            db.query(Subscription)
            .filter(Subscription.status == SubscriptionStatus.SUSPENDED)
            .count()
        )

        grace_period = (
            db.query(Subscription)
            .filter(Subscription.status == SubscriptionStatus.GRACE_PERIOD)
            .count()
        )

        expired = (
            db.query(Subscription).filter(Subscription.status == SubscriptionStatus.EXPIRED).count()
        )

        # Revenue calculations
        monthly_revenue = (
            db.query(func.sum(Subscription.monthly_amount))
            .filter(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.auto_renew_enabled == True,
            )
            .scalar()
            or 0.0
        )

        # Annual revenue (monthly * 12)
        annual_revenue = monthly_revenue * 12

        # Auto-renew rate
        total_active = active + grace_period
        auto_renew_count = (
            db.query(Subscription)
            .filter(
                Subscription.status.in_(
                    [SubscriptionStatus.ACTIVE, SubscriptionStatus.GRACE_PERIOD]
                ),
                Subscription.auto_renew_enabled == True,
            )
            .count()
        )

        auto_renew_rate = (auto_renew_count / total_active * 100) if total_active > 0 else 0.0

        # Churn rate (cancelled / total)
        churn_rate = (cancelled / total * 100) if total > 0 else 0.0

        # Average subscription value
        avg_value = (
            db.query(func.avg(Subscription.monthly_amount))
            .filter(Subscription.status == SubscriptionStatus.ACTIVE)
            .scalar()
            or 0.0
        )

        return {
            "total_subscriptions": total,
            "active_subscriptions": active,
            "cancelled_subscriptions": cancelled,
            "suspended_subscriptions": suspended,
            "grace_period_subscriptions": grace_period,
            "expired_subscriptions": expired,
            "total_monthly_revenue": monthly_revenue,
            "total_annual_revenue": annual_revenue,
            "auto_renew_rate": round(auto_renew_rate, 2),
            "churn_rate": round(churn_rate, 2),
            "average_subscription_value": round(avg_value, 2),
        }

    except Exception as e:
        logger.error(f"Error getting subscription stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="İstatistikler alınamadı"
        )


@router.post("/{subscription_id}/extend")
async def admin_extend_subscription(
    subscription_id: int,
    request: ExtendSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually extend a subscription (Admin only)"""
    # Check admin permission
    require_admin(current_user)

    try:
        subscription_service = SubscriptionService(db)

        subscription = subscription_service.extend_subscription(
            subscription_id=subscription_id, months=request.months, admin_override=True
        )

        # Log admin action
        logger.info(
            f"Admin {current_user.username} extended subscription {subscription_id} "
            f"by {request.months} months. Reason: {request.reason}"
        )

        return {
            "success": True,
            "message": f"Abonelik {request.months} ay uzatıldı",
            "new_expiry_date": subscription.next_billing_date.strftime("%Y-%m-%d"),
            "extended_by_admin": current_user.username,
            "reason": request.reason,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extending subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Abonelik uzatılamadı"
        )


@router.post("/{subscription_id}/suspend")
async def admin_suspend_subscription(
    subscription_id: int,
    request: SuspendSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually suspend a subscription (Admin only)"""
    # Check admin permission
    require_admin(current_user)

    try:
        subscription_service = SubscriptionService(db)

        subscription = subscription_service.suspend_subscription(
            subscription_id=subscription_id, reason=f"Admin: {request.reason}"
        )

        # Log admin action
        logger.info(
            f"Admin {current_user.username} suspended subscription {subscription_id}. "
            f"Reason: {request.reason}"
        )

        return {
            "success": True,
            "message": "Abonelik askıya alındı",
            "status": subscription.status.value,
            "suspended_by_admin": current_user.username,
            "reason": request.reason,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suspending subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Abonelik askıya alınamadı"
        )


@router.get("/failed-billings")
async def get_failed_billings(
    days: int = Query(7, description="Number of days to look back", ge=1, le=90),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recent failed billing attempts (Admin only)"""
    # Check admin permission
    require_admin(current_user)

    try:
        cutoff_date = datetime.now() - timedelta(days=days)

        failed_billings = (
            db.query(SubscriptionBillingHistory)
            .filter(
                SubscriptionBillingHistory.status == BillingHistoryStatus.FAILED,
                SubscriptionBillingHistory.created_at >= cutoff_date,
            )
            .order_by(SubscriptionBillingHistory.created_at.desc())
            .limit(limit)
            .all()
        )

        # Format response
        result = []
        for billing in failed_billings:
            result.append(
                {
                    "id": billing.id,
                    "subscription_id": billing.subscription_id,
                    "user_id": billing.user_id,
                    "username": billing.user.username,
                    "server_name": billing.game_server.name,
                    "billing_date": billing.billing_date.strftime("%Y-%m-%d"),
                    "amount": billing.amount,
                    "payment_method": billing.payment_method.value,
                    "failure_reason": billing.failure_reason,
                    "retry_count": billing.retry_count,
                    "created_at": billing.created_at.isoformat(),
                }
            )

        return {
            "failed_billings": result,
            "count": len(result),
            "period_days": days,
        }

    except Exception as e:
        logger.error(f"Error getting failed billings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Başarısız faturalar alınamadı",
        )


@router.get("/expiring-soon")
async def get_expiring_soon(
    days: int = Query(7, description="Number of days ahead to check", ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get subscriptions expiring soon (Admin only)"""
    # Check admin permission
    require_admin(current_user)

    try:
        future_date = date.today() + timedelta(days=days)

        expiring = (
            db.query(Subscription)
            .filter(
                Subscription.next_billing_date <= future_date,
                Subscription.next_billing_date >= date.today(),
                Subscription.status.in_(
                    [SubscriptionStatus.ACTIVE, SubscriptionStatus.GRACE_PERIOD]
                ),
            )
            .order_by(Subscription.next_billing_date.asc())
            .all()
        )

        # Format response
        result = []
        for sub in expiring:
            days_until_expiry = (sub.next_billing_date - date.today()).days

            result.append(
                {
                    "id": sub.id,
                    "user_id": sub.user_id,
                    "username": sub.user.username,
                    "server_name": sub.game_server.name,
                    "expiry_date": sub.next_billing_date.strftime("%Y-%m-%d"),
                    "days_until_expiry": days_until_expiry,
                    "auto_renew_enabled": sub.auto_renew_enabled,
                    "monthly_amount": sub.monthly_amount,
                    "status": sub.status.value,
                }
            )

        return {
            "expiring_subscriptions": result,
            "count": len(result),
            "check_period_days": days,
        }

    except Exception as e:
        logger.error(f"Error getting expiring subscriptions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Süre dolan abonelikler alınamadı",
        )
