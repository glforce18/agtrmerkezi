"""
AGTR Merkezi - Wallet Service
Çift cüzdan sistemi: TL (real) + Armor (sanal para)
1 TL = 100 Armor
Transaction ledger ile tam izlenebilirlik
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import (
    User,
    Transaction,
    WalletType,
    TransactionType,
)

logger = logging.getLogger(__name__)


class WalletService:
    """Cüzdan işlemleri servisi"""

    def __init__(self, db: Session):
        self.db = db

    def get_balance(self, user_id: int, wallet_type: WalletType = WalletType.REAL) -> float:
        """Kullanıcı bakiyesini getir"""
        if user_id is None:
            raise HTTPException(status_code=400, detail="Geçersiz kullanıcı ID")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

        if wallet_type == WalletType.REAL:
            balance = user.balance
            return float(balance) if balance is not None else 0.0
        else:
            balance = user.balance_coin
            return float(balance) if balance is not None else 0.0

    def get_all_balances(self, user_id: int) -> Dict[str, float]:
        """Tüm cüzdan bakiyelerini getir"""
        if user_id is None:
            raise HTTPException(status_code=400, detail="Geçersiz kullanıcı ID")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

        return {
            "balance_real": float(user.balance) if user.balance is not None else 0.0,
            "balance_coin": float(user.balance_coin) if user.balance_coin is not None else 0.0
        }

    def _update_balance(
        self,
        user: User,
        wallet_type: WalletType,
        amount: float
    ) -> tuple[float, float]:
        """Bakiyeyi güncelle ve önceki/sonraki değerleri döndür"""
        if user is None:
            raise HTTPException(status_code=400, detail="Geçersiz kullanıcı")

        if amount is None:
            raise HTTPException(status_code=400, detail="Geçersiz miktar")

        if wallet_type == WalletType.REAL:
            balance_before = float(user.balance) if user.balance is not None else 0.0
            user.balance = balance_before + amount
            balance_after = float(user.balance) if user.balance is not None else 0.0
        else:
            balance_before = float(user.balance_coin) if user.balance_coin is not None else 0.0
            user.balance_coin = balance_before + amount
            balance_after = float(user.balance_coin) if user.balance_coin is not None else 0.0

        return balance_before, balance_after

    def add_balance(
        self,
        user_id: int,
        amount: float,
        wallet_type: WalletType = WalletType.REAL,
        transaction_type: str = TransactionType.DEPOSIT.value,
        description: str = None,
        reference_id: str = None,
        reference_type: str = None,
        ip_address: str = None,
        user_agent: str = None,
        extra_data: Dict[str, Any] = None
    ) -> Transaction:
        """Bakiye ekle ve transaction kaydı oluştur"""
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz kullanıcı ID"
            )

        if amount is None or amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Miktar 0'dan büyük olmalı"
            )

        user = self.db.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

        # Bakiye güncelle
        balance_before, balance_after = self._update_balance(user, wallet_type, amount)

        # Transaction kaydı oluştur
        transaction = Transaction(
            user_id=user_id,
            wallet_type=wallet_type,
            type=transaction_type,
            amount=amount,
            description=description or f"{amount} eklendi",
            reference_id=reference_id,
            reference_type=reference_type,
            balance_before=balance_before,
            balance_after=balance_after,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data
        )
        self.db.add(transaction)
        self.db.commit()

        logger.info(
            f"Bakiye eklendi: user={user_id}, wallet={wallet_type.value}, "
            f"amount={amount}, before={balance_before}, after={balance_after}"
        )

        return transaction

    def deduct_balance(
        self,
        user_id: int,
        amount: float,
        wallet_type: WalletType = WalletType.REAL,
        transaction_type: str = TransactionType.PAYMENT.value,
        description: str = None,
        reference_id: str = None,
        reference_type: str = None,
        ip_address: str = None,
        user_agent: str = None,
        extra_data: Dict[str, Any] = None,
        allow_negative: bool = False
    ) -> Transaction:
        """Bakiye düş ve transaction kaydı oluştur"""
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz kullanıcı ID"
            )

        if amount is None or amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Miktar 0'dan büyük olmalı"
            )

        user = self.db.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

        # Bakiye kontrolü - LOCKED user objesinden oku, yeni query yapma
        if wallet_type == WalletType.REAL:
            current_balance = float(user.balance) if user.balance is not None else 0.0
        else:
            current_balance = float(user.balance_coin) if user.balance_coin is not None else 0.0

        if not allow_negative and current_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Yetersiz bakiye. Mevcut: {current_balance}, Gerekli: {amount}"
            )

        # Bakiye güncelle (negatif miktar)
        balance_before, balance_after = self._update_balance(user, wallet_type, -amount)

        # Transaction kaydı oluştur
        transaction = Transaction(
            user_id=user_id,
            wallet_type=wallet_type,
            type=transaction_type,
            amount=-amount,  # Negatif (düşürme)
            description=description or f"{amount} düşüldü",
            reference_id=reference_id,
            reference_type=reference_type,
            balance_before=balance_before,
            balance_after=balance_after,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data
        )
        self.db.add(transaction)
        self.db.commit()

        logger.info(
            f"Bakiye düşüldü: user={user_id}, wallet={wallet_type.value}, "
            f"amount={amount}, before={balance_before}, after={balance_after}"
        )

        return transaction

    def transfer(
        self,
        from_user_id: int,
        to_user_id: int,
        amount: float,
        wallet_type: WalletType = WalletType.COIN,
        description: str = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> tuple[Transaction, Transaction]:
        """Kullanıcılar arası transfer"""
        if from_user_id is None or to_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz kullanıcı ID"
            )

        if from_user_id == to_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kendinize transfer yapamazsınız"
            )

        if amount is None or amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Miktar 0'dan büyük olmalı"
            )

        # Gönderen kullanıcı
        from_user = self.db.query(User).filter(User.id == from_user_id).with_for_update().first()
        if not from_user:
            raise HTTPException(status_code=404, detail="Gönderen kullanıcı bulunamadı")

        # Alıcı kullanıcı
        to_user = self.db.query(User).filter(User.id == to_user_id).with_for_update().first()
        if not to_user:
            raise HTTPException(status_code=404, detail="Alıcı kullanıcı bulunamadı")

        # Bakiye kontrolü - LOCKED from_user objesinden oku, yeni query yapma
        if wallet_type == WalletType.REAL:
            current_balance = float(from_user.balance) if from_user.balance is not None else 0.0
        else:
            current_balance = float(from_user.balance_coin) if from_user.balance_coin is not None else 0.0

        if current_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Yetersiz bakiye. Mevcut: {current_balance}"
            )

        # Gönderenden düş
        from_before, from_after = self._update_balance(from_user, wallet_type, -amount)

        # Alıcıya ekle
        to_before, to_after = self._update_balance(to_user, wallet_type, amount)

        # Transaction kayıtları
        from_tx = Transaction(
            user_id=from_user_id,
            wallet_type=wallet_type,
            type=TransactionType.TRANSFER.value,
            amount=-amount,
            description=description or f"{to_user.username}'e transfer",
            target_user_id=to_user_id,
            balance_before=from_before,
            balance_after=from_after,
            ip_address=ip_address,
            user_agent=user_agent
        )

        to_tx = Transaction(
            user_id=to_user_id,
            wallet_type=wallet_type,
            type=TransactionType.TRANSFER.value,
            amount=amount,
            description=description or f"{from_user.username}'den transfer",
            target_user_id=from_user_id,
            balance_before=to_before,
            balance_after=to_after
        )

        self.db.add(from_tx)
        self.db.add(to_tx)
        self.db.commit()

        logger.info(
            f"Transfer: {from_user_id} -> {to_user_id}, "
            f"wallet={wallet_type.value}, amount={amount}"
        )

        return from_tx, to_tx

    def exchange_to_coin(
        self,
        user_id: int,
        tl_amount: float,
        exchange_rate: float = 100.0,  # 1 TL = 100 Armor
        ip_address: str = None,
        user_agent: str = None
    ) -> tuple[Transaction, Transaction]:
        """TL bakiyeyi Armor'a dönüştür"""
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz kullanıcı ID"
            )

        if tl_amount is None or tl_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Miktar 0'dan büyük olmalı"
            )

        if exchange_rate is None or exchange_rate <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Geçersiz dönüşüm oranı"
            )

        user = self.db.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

        # TL bakiye kontrolü with null safety
        current_balance = float(user.balance) if user.balance is not None else 0.0
        if current_balance < tl_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Yetersiz TL bakiye. Mevcut: {current_balance}"
            )

        armor_amount = tl_amount * exchange_rate

        # TL düş
        tl_before, tl_after = self._update_balance(user, WalletType.REAL, -tl_amount)

        # Armor ekle
        armor_before, armor_after = self._update_balance(user, WalletType.COIN, armor_amount)

        # Transaction kayıtları
        tl_tx = Transaction(
            user_id=user_id,
            wallet_type=WalletType.REAL,
            type=TransactionType.EXCHANGE.value,
            amount=-tl_amount,
            description=f"{tl_amount} TL -> {int(armor_amount)} Armor dönüştürüldü",
            balance_before=tl_before,
            balance_after=tl_after,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data={"exchange_rate": exchange_rate, "armor_amount": armor_amount}
        )

        armor_tx = Transaction(
            user_id=user_id,
            wallet_type=WalletType.COIN,
            type=TransactionType.EXCHANGE.value,
            amount=armor_amount,
            description=f"{tl_amount} TL'den dönüştürüldü",
            balance_before=armor_before,
            balance_after=armor_after,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data={"exchange_rate": exchange_rate, "tl_amount": tl_amount}
        )

        self.db.add(tl_tx)
        self.db.add(armor_tx)
        self.db.commit()

        logger.info(
            f"Exchange: user={user_id}, {tl_amount} TL -> {armor_amount} Armor"
        )

        return tl_tx, armor_tx

    def get_transactions(
        self,
        user_id: int,
        wallet_type: WalletType = None,
        transaction_type: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Transaction]:
        """Kullanıcının işlem geçmişini getir"""
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)

        if wallet_type:
            query = query.filter(Transaction.wallet_type == wallet_type)

        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)

        return query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()


# Singleton-like factory
def get_wallet_service(db: Session) -> WalletService:
    """Wallet service instance oluştur"""
    return WalletService(db)
