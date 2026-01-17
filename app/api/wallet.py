"""
AGTR Merkezi - Wallet API
Çift cüzdan sistemi: TL + Armor
1 TL = 100 Armor
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

# Exchange rate: 1 TL = 100 Armor
ARMOR_RATE = 100

# Armor packages with bonus percentages
ARMOR_PACKAGES = [
    {"id": 1, "armor": 1000, "price": 10, "bonus": 0},
    {"id": 2, "armor": 2500, "price": 25, "bonus": 5},
    {"id": 3, "armor": 5000, "price": 50, "bonus": 10},
    {"id": 4, "armor": 10000, "price": 100, "bonus": 15},
    {"id": 5, "armor": 25000, "price": 250, "bonus": 20},
    {"id": 6, "armor": 50000, "price": 500, "bonus": 25},
]


# ==================== SCHEMAS ====================

class BalanceResponse(BaseModel):
    balance_real: float = Field(description="TL bakiye")
    balance_coin: float = Field(description="Armor bakiye")


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
async def exchange_to_armor(
    request: Request,
    data: ExchangeRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """TL bakiyeyi Armor'a dönüştür (1 TL = 100 Armor)"""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]

    wallet = get_wallet_service(db)

    tl_tx, armor_tx = wallet.exchange_to_coin(
        user_id=current_user.id,
        tl_amount=data.tl_amount,
        exchange_rate=float(ARMOR_RATE),
        ip_address=client_ip,
        user_agent=user_agent
    )

    armor_amount = data.tl_amount * ARMOR_RATE

    return {
        "success": True,
        "message": f"{data.tl_amount} TL, {armor_amount} Armor'a dönüştürüldü",
        "tl_deducted": data.tl_amount,
        "armor_added": armor_amount,
        "exchange_rate": ARMOR_RATE,
        "new_balance_real": tl_tx.balance_after,
        "new_balance_armor": armor_tx.balance_after
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
    """Güncel TL -> Armor dönüşüm oranını getir"""
    return {
        "rate": ARMOR_RATE,
        "description": f"1 TL = {ARMOR_RATE} Armor"
    }


@router.get("/armor-packages")
async def get_armor_packages():
    """Satın alınabilir Armor paketlerini getir"""
    return {
        "packages": ARMOR_PACKAGES,
        "exchange_rate": ARMOR_RATE
    }


class DepositRequest(BaseModel):
    amount: float = Field(gt=0, description="Yüklenecek TL miktarı")
    payment_method: str = Field(default="card", description="Ödeme yöntemi: card, bank, mobile")


class ArmorPackageRequest(BaseModel):
    package_id: int = Field(ge=1, le=6, description="Armor paket ID")


@router.post("/deposit")
async def deposit_tl(
    request: Request,
    data: DepositRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """TL bakiye yükle (ödeme entegrasyonu simülasyonu)"""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]

    wallet = get_wallet_service(db)

    # Gerçek uygulamada burada ödeme gateway entegrasyonu olur
    # Şimdilik simüle ediyoruz
    tx = wallet.add_balance(
        user_id=current_user.id,
        amount=data.amount,
        wallet_type=WalletType.REAL,
        transaction_type=TransactionType.DEPOSIT.value,
        description=f"TL yükleme ({data.payment_method})",
        ip_address=client_ip,
        user_agent=user_agent,
        extra_data={"payment_method": data.payment_method}
    )

    return {
        "success": True,
        "message": f"{data.amount} TL hesabınıza yüklendi",
        "amount": data.amount,
        "new_balance": tx.balance_after,
        "transaction_id": tx.id
    }


@router.post("/buy-armor-package")
async def buy_armor_package(
    request: Request,
    data: ArmorPackageRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """TL ile Armor paketi satın al"""
    # Paketi bul
    package = next((p for p in ARMOR_PACKAGES if p["id"] == data.package_id), None)
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Armor paketi bulunamadı"
        )

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]

    wallet = get_wallet_service(db)

    # TL bakiyesini kontrol et
    balances = wallet.get_all_balances(current_user.id)
    if balances["balance_real"] < package["price"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Yetersiz TL bakiye. Mevcut: {balances['balance_real']} TL, Gerekli: {package['price']} TL"
        )

    # Bonus dahil toplam Armor hesapla
    base_armor = package["armor"]
    bonus_armor = int(base_armor * package["bonus"] / 100)
    total_armor = base_armor + bonus_armor

    # TL düş
    tl_tx = wallet.deduct_balance(
        user_id=current_user.id,
        amount=package["price"],
        wallet_type=WalletType.REAL,
        transaction_type=TransactionType.PAYMENT.value,
        description=f"Armor paketi satın alımı ({total_armor} Armor)",
        ip_address=client_ip,
        user_agent=user_agent,
        extra_data={"package_id": package["id"], "armor_amount": total_armor}
    )

    # Armor ekle
    armor_tx = wallet.add_balance(
        user_id=current_user.id,
        amount=total_armor,
        wallet_type=WalletType.COIN,
        transaction_type=TransactionType.DEPOSIT.value,
        description=f"Armor paketi ({base_armor} + {bonus_armor} bonus)",
        ip_address=client_ip,
        user_agent=user_agent,
        extra_data={"package_id": package["id"], "base_armor": base_armor, "bonus_armor": bonus_armor}
    )

    return {
        "success": True,
        "message": f"{total_armor} Armor hesabınıza eklendi!",
        "package": package,
        "base_armor": base_armor,
        "bonus_armor": bonus_armor,
        "total_armor": total_armor,
        "tl_spent": package["price"],
        "new_balance_real": tl_tx.balance_after,
        "new_balance_armor": armor_tx.balance_after
    }
