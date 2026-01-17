"""
AGTR Merkezi - Wallet API
Çift cüzdan sistemi: TL + Coin
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import User, WalletType, TransactionType
from app.services.wallet import get_wallet_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== SCHEMAS ====================

class BalanceResponse(BaseModel):
    balance_real: float = Field(description="TL bakiye")
    balance_coin: float = Field(description="Coin bakiye")


class TransferRequest(BaseModel):
    to_username: str = Field(min_length=1, description="Alıcı kullanıcı adı")
    amount: float = Field(gt=0, description="Transfer miktarı")
    wallet_type: str = Field(default="coin", description="Cüzdan türü: real veya coin")
    message: Optional[str] = Field(None, max_length=200, description="Transfer mesajı")


class ExchangeRequest(BaseModel):
    tl_amount: float = Field(gt=0, description="Dönüştürülecek TL miktarı")


class TransactionResponse(BaseModel):
    id: int
    wallet_type: str
    type: str
    amount: float
    description: Optional[str]
    balance_before: float
    balance_after: float
    created_at: str

    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Kullanıcının tüm bakiyelerini getir"""
    wallet = get_wallet_service(db)
    balances = wallet.get_all_balances(current_user.id)
    return BalanceResponse(**balances)


@router.post("/transfer")
async def transfer_balance(
    request: Request,
    data: TransferRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Başka bir kullanıcıya bakiye transferi"""
    # Alıcıyı bul
    to_user = db.query(User).filter(User.username == data.to_username).first()
    if not to_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alıcı kullanıcı bulunamadı"
        )

    if to_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendinize transfer yapamazsınız"
        )

    # Wallet type
    wallet_type = WalletType.COIN if data.wallet_type == "coin" else WalletType.REAL

    # TL transferi sadece adminler için
    if wallet_type == WalletType.REAL and current_user.role.value not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="TL transferi sadece adminler için kullanılabilir"
        )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]

    wallet = get_wallet_service(db)
    from_tx, to_tx = wallet.transfer(
        from_user_id=current_user.id,
        to_user_id=to_user.id,
        amount=data.amount,
        wallet_type=wallet_type,
        description=data.message,
        ip_address=client_ip,
        user_agent=user_agent
    )

    return {
        "success": True,
        "message": f"{data.amount} {data.wallet_type.upper()} {to_user.username}'e gönderildi",
        "transaction_id": from_tx.id,
        "new_balance": from_tx.balance_after
    }


@router.post("/exchange")
async def exchange_to_coin(
    request: Request,
    data: ExchangeRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """TL bakiyeyi Coin'e dönüştür"""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]

    wallet = get_wallet_service(db)

    # Dönüşüm oranı (1 TL = 10 Coin)
    exchange_rate = 10.0

    tl_tx, coin_tx = wallet.exchange_to_coin(
        user_id=current_user.id,
        tl_amount=data.tl_amount,
        exchange_rate=exchange_rate,
        ip_address=client_ip,
        user_agent=user_agent
    )

    return {
        "success": True,
        "message": f"{data.tl_amount} TL, {data.tl_amount * exchange_rate} Coin'e dönüştürüldü",
        "tl_deducted": data.tl_amount,
        "coin_added": data.tl_amount * exchange_rate,
        "exchange_rate": exchange_rate,
        "new_balance_real": tl_tx.balance_after,
        "new_balance_coin": coin_tx.balance_after
    }


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    wallet_type: Optional[str] = None,
    transaction_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Kullanıcının işlem geçmişini getir"""
    wallet = get_wallet_service(db)

    wt = None
    if wallet_type:
        wt = WalletType.COIN if wallet_type == "coin" else WalletType.REAL

    transactions = wallet.get_transactions(
        user_id=current_user.id,
        wallet_type=wt,
        transaction_type=transaction_type,
        limit=min(limit, 100),  # Max 100
        offset=offset
    )

    return [
        TransactionResponse(
            id=tx.id,
            wallet_type=tx.wallet_type.value,
            type=tx.type,
            amount=tx.amount,
            description=tx.description,
            balance_before=tx.balance_before,
            balance_after=tx.balance_after,
            created_at=tx.created_at.isoformat() if tx.created_at else ""
        )
        for tx in transactions
    ]


@router.get("/exchange-rate")
async def get_exchange_rate():
    """Güncel TL -> Coin dönüşüm oranını getir"""
    return {
        "rate": 10.0,
        "description": "1 TL = 10 Coin"
    }
