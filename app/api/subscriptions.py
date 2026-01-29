"""
AGTR Merkezi - Subscription Management API
Handles subscription management, auto-renewal, and billing history
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.models.database import Subscription, User, WalletType, get_db
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


# ==================== PYDANTIC MODELS ====================


class SubscriptionResponse(BaseModel):
    """Subscription response model"""

    id: int
    game_server_id: int
    server_name: str
    user_id: int
    billing_period: str
    auto_renew_enabled: bool
    payment_method: str
    next_billing_date: str
    last_billing_date: Optional[str] = None
    status: str
    monthly_amount: float
    failure_count: int
    last_failure_reason: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class BillingHistoryResponse(BaseModel):
    """Billing history response model"""

    id: int
    subscription_id: int
    billing_date: str
    billing_period: str
    amount: float
    payment_method: str
    status: str
    failure_reason: Optional[str] = None
    retry_count: int
    balance_before: Optional[float] = None
    balance_after: Optional[float] = None
    created_at: str
    completed_at: Optional[str] = None

    class Config:
        from_attributes = True


class ToggleAutoRenewRequest(BaseModel):
    """Toggle auto-renewal request"""

    enabled: bool = Field(..., description="Enable or disable auto-renewal")


class ChangePaymentMethodRequest(BaseModel):
    """Change payment method request"""

    method: str = Field(..., description="Payment method: 'real' or 'coin'")


class CancelSubscriptionRequest(BaseModel):
    """Cancel subscription request"""

    reason: Optional[str] = Field(None, description="Cancellation reason")


class ManualPaymentRequest(BaseModel):
    """Manual payment request"""

    months: int = Field(..., description="Number of months to extend", ge=1, le=12)
    payment_method: str = Field(..., description="Payment method: 'real' or 'coin'")


# ==================== API ENDPOINTS ====================


@router.get("/my-subscriptions", response_model=List[SubscriptionResponse])
async def get_my_subscriptions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get all subscriptions for the current user

    Returns list of user's subscriptions with details
    """
    try:
        subscription_service = SubscriptionService(db)
        subscriptions = subscription_service.get_user_subscriptions(current_user.id)

        # Format response
        result = []
        for sub in subscriptions:
            result.append(
                {
                    "id": sub.id,
                    "game_server_id": sub.game_server_id,
                    "server_name": sub.game_server.name,
                    "user_id": sub.user_id,
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
                    "created_at": sub.created_at.isoformat(),
                }
            )

        return result

    except Exception as e:
        logger.error(f"Error getting subscriptions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Abonelikler alınamadı"
        )


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get subscription details by ID"""
    try:
        subscription = (
            db.query(Subscription)
            .filter(Subscription.id == subscription_id, Subscription.user_id == current_user.id)
            .first()
        )

        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abonelik bulunamadı")

        return {
            "id": subscription.id,
            "game_server_id": subscription.game_server_id,
            "server_name": subscription.game_server.name,
            "user_id": subscription.user_id,
            "billing_period": subscription.billing_period.value,
            "auto_renew_enabled": subscription.auto_renew_enabled,
            "payment_method": subscription.payment_method.value,
            "next_billing_date": subscription.next_billing_date.strftime("%Y-%m-%d"),
            "last_billing_date": (
                subscription.last_billing_date.strftime("%Y-%m-%d")
                if subscription.last_billing_date
                else None
            ),
            "status": subscription.status.value,
            "monthly_amount": subscription.monthly_amount,
            "failure_count": subscription.failure_count,
            "last_failure_reason": subscription.last_failure_reason,
            "created_at": subscription.created_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription {subscription_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Abonelik alınamadı"
        )


@router.post("/{subscription_id}/toggle-auto-renew")
async def toggle_auto_renew(
    subscription_id: int,
    request: ToggleAutoRenewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle auto-renewal for a subscription"""
    try:
        subscription_service = SubscriptionService(db)

        subscription = subscription_service.toggle_auto_renew(
            subscription_id=subscription_id, user_id=current_user.id, enabled=request.enabled
        )

        return {
            "success": True,
            "message": f"Otomatik yenileme {'açıldı' if request.enabled else 'kapatıldı'}",
            "auto_renew_enabled": subscription.auto_renew_enabled,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling auto-renew: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Otomatik yenileme ayarı değiştirilemedi",
        )


@router.post("/{subscription_id}/change-payment-method")
async def change_payment_method(
    subscription_id: int,
    request: ChangePaymentMethodRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change payment method for a subscription"""
    try:
        # Validate payment method
        if request.method not in ["real", "coin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz ödeme yöntemi. 'real' veya 'coin' olmalı",
            )

        wallet_type = WalletType.REAL if request.method == "real" else WalletType.COIN

        subscription_service = SubscriptionService(db)

        subscription = subscription_service.change_payment_method(
            subscription_id=subscription_id, user_id=current_user.id, payment_method=wallet_type
        )

        return {
            "success": True,
            "message": "Ödeme yöntemi değiştirildi",
            "payment_method": subscription.payment_method.value,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing payment method: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ödeme yöntemi değiştirilemedi",
        )


@router.post("/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: int,
    request: CancelSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a subscription"""
    try:
        subscription_service = SubscriptionService(db)

        subscription = subscription_service.cancel_subscription(
            subscription_id=subscription_id, user_id=current_user.id, reason=request.reason
        )

        return {
            "success": True,
            "message": "Abonelik iptal edildi. Sunucu mevcut süre sonuna kadar aktif kalacak.",
            "status": subscription.status.value,
            "cancelled_at": subscription.cancelled_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Abonelik iptal edilemedi"
        )


@router.post("/{subscription_id}/reactivate")
async def reactivate_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reactivate a suspended subscription"""
    try:
        subscription_service = SubscriptionService(db)

        subscription = subscription_service.reactivate_subscription(
            subscription_id=subscription_id, user_id=current_user.id
        )

        return {
            "success": True,
            "message": "Abonelik yeniden etkinleştirildi",
            "status": subscription.status.value,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reactivating subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Abonelik yeniden etkinleştirilemedi",
        )


@router.get("/{subscription_id}/billing-history", response_model=List[BillingHistoryResponse])
async def get_billing_history(
    subscription_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get billing history for a subscription"""
    try:
        subscription_service = SubscriptionService(db)

        history = subscription_service.get_billing_history(
            subscription_id=subscription_id, user_id=current_user.id, limit=limit
        )

        # Format response
        result = []
        for record in history:
            result.append(
                {
                    "id": record.id,
                    "subscription_id": record.subscription_id,
                    "billing_date": record.billing_date.strftime("%Y-%m-%d"),
                    "billing_period": record.billing_period.value,
                    "amount": record.amount,
                    "payment_method": record.payment_method.value,
                    "status": record.status.value,
                    "failure_reason": record.failure_reason,
                    "retry_count": record.retry_count,
                    "balance_before": record.balance_before,
                    "balance_after": record.balance_after,
                    "created_at": record.created_at.isoformat(),
                    "completed_at": (
                        record.completed_at.isoformat() if record.completed_at else None
                    ),
                }
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting billing history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fatura geçmişi alınamadı"
        )


@router.post("/{subscription_id}/manual-payment")
async def manual_payment(
    subscription_id: int,
    request: ManualPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manual payment to extend subscription"""
    try:
        # Validate payment method
        if request.payment_method not in ["real", "coin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Geçersiz ödeme yöntemi"
            )

        subscription_service = SubscriptionService(db)

        # Get subscription
        subscription = (
            db.query(Subscription)
            .filter(Subscription.id == subscription_id, Subscription.user_id == current_user.id)
            .first()
        )

        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Abonelik bulunamadı")

        # Calculate amount
        amount = subscription.monthly_amount * request.months

        # Deduct from wallet
        from app.services.wallet import WalletService

        wallet_service = WalletService(db)

        wallet_type = WalletType.REAL if request.payment_method == "real" else WalletType.COIN

        transaction = wallet_service.deduct_balance(
            user_id=current_user.id,
            amount=amount,
            wallet_type=wallet_type,
            transaction_type="payment",
            description=f"Manuel sunucu uzatma - {subscription.game_server.name} ({request.months} ay)",
            reference_id=str(subscription_id),
            reference_type="subscription_manual_payment",
        )

        # Extend subscription
        updated_subscription = subscription_service.extend_subscription(
            subscription_id=subscription_id, months=request.months
        )

        return {
            "success": True,
            "message": f"Sunucu {request.months} ay uzatıldı",
            "amount": amount,
            "new_expiry_date": updated_subscription.next_billing_date.strftime("%Y-%m-%d"),
            "transaction_id": transaction.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing manual payment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ödeme işlenemedi"
        )
