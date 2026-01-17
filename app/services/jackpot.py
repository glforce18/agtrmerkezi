"""
AGTR Merkezi - Jackpot Game Service
Provably Fair Jackpot oyun sistemi
"""

import asyncio
import hashlib
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import User, WalletType, TransactionType
from app.models.games import JackpotRound, JackpotBet, GameHistory, GameStatus
from app.services.wallet import get_wallet_service

logger = logging.getLogger(__name__)


class JackpotService:
    """Jackpot oyun servisi"""

    # Oyun ayarları
    MIN_PLAYERS = 2  # Minimum oyuncu sayısı
    MAX_PLAYERS = 50  # Maximum oyuncu sayısı
    ROUND_DURATION = 30  # Tur süresi (saniye)
    SPIN_DURATION = 10  # Çark dönme süresi
    HOUSE_CUT_PERCENT = 5.0  # Site komisyonu (%)
    MIN_BET = 10.0  # Minimum bahis
    MAX_BET = 1000.0  # Maximum bahis

    def __init__(self, db: Session):
        self.db = db
        self.wallet = get_wallet_service(db)

    def _generate_server_seed(self) -> tuple[str, str]:
        """Server seed oluştur ve hash'le"""
        seed = secrets.token_hex(32)
        seed_hash = hashlib.sha256(seed.encode()).hexdigest()
        return seed, seed_hash

    def _calculate_winner(
        self,
        server_seed: str,
        client_seed: str,
        total_tickets: int
    ) -> int:
        """Provably fair kazanan hesapla"""
        combined = f"{server_seed}:{client_seed}"
        hash_result = hashlib.sha256(combined.encode()).hexdigest()
        # Hash'in ilk 8 karakterini sayıya çevir
        number = int(hash_result[:8], 16)
        # Bilet numarasına dönüştür
        winning_ticket = number % total_tickets + 1
        return winning_ticket

    def get_current_round(self) -> Optional[JackpotRound]:
        """Aktif turu getir"""
        return self.db.query(JackpotRound).filter(
            JackpotRound.status.in_([GameStatus.WAITING, GameStatus.ACTIVE])
        ).first()

    def get_or_create_round(self) -> JackpotRound:
        """Aktif tur varsa getir, yoksa yeni oluştur"""
        current_round = self.get_current_round()
        if current_round:
            return current_round

        # Son tur numarasını bul
        last_round = self.db.query(JackpotRound).order_by(
            JackpotRound.round_number.desc()
        ).first()
        next_number = (last_round.round_number + 1) if last_round else 1

        # Server seed oluştur
        server_seed, server_seed_hash = self._generate_server_seed()

        # Yeni tur oluştur
        new_round = JackpotRound(
            round_number=next_number,
            status=GameStatus.WAITING,
            server_seed=server_seed_hash,  # Sadece hash'i kaydet
            server_seed_revealed=server_seed,  # Gerçek seed (oyun bitince açılacak)
            min_bet=self.MIN_BET,
            max_bet=self.MAX_BET,
            house_cut=self.HOUSE_CUT_PERCENT
        )
        self.db.add(new_round)
        self.db.commit()

        logger.info(f"Yeni jackpot turu oluşturuldu: #{next_number}")
        return new_round

    def place_bet(
        self,
        user_id: int,
        amount: float,
        ip_address: str = None,
        user_agent: str = None
    ) -> JackpotBet:
        """Bahis yap"""
        # Tur kontrolü
        round = self.get_or_create_round()

        if round.status not in [GameStatus.WAITING, GameStatus.ACTIVE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu tura bahis yapılamaz"
            )

        # Miktar kontrolü
        if amount < round.min_bet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum bahis: {round.min_bet} Coin"
            )

        if amount > round.max_bet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum bahis: {round.max_bet} Coin"
            )

        # Kullanıcı kontrolü
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

        # Coin bakiye kontrolü ve düşürme
        self.wallet.deduct_balance(
            user_id=user_id,
            amount=amount,
            wallet_type=WalletType.COIN,
            transaction_type=TransactionType.JACKPOT.value,
            description=f"Jackpot #{round.round_number} bahisi",
            reference_id=str(round.id),
            reference_type="jackpot",
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Bilet hesaplama
        # Her 1 Coin = 1 bilet
        ticket_count = int(amount)
        ticket_start = int(round.total_pot) + 1
        ticket_end = ticket_start + ticket_count - 1

        # Bahis oluştur
        bet = JackpotBet(
            round_id=round.id,
            user_id=user_id,
            amount=amount,
            ticket_start=ticket_start,
            ticket_end=ticket_end,
            ticket_count=ticket_count,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(bet)

        # Tur bilgilerini güncelle
        round.total_pot += amount
        round.total_bets += 1

        # İlk bahis ise turu başlat
        if round.status == GameStatus.WAITING and round.total_bets >= 1:
            round.status = GameStatus.ACTIVE
            round.start_time = datetime.utcnow()

        self.db.commit()

        # Kazanma şansını hesapla
        bet.win_chance = (ticket_count / int(round.total_pot)) * 100

        logger.info(
            f"Jackpot bahisi: user={user_id}, round=#{round.round_number}, "
            f"amount={amount}, tickets={ticket_start}-{ticket_end}"
        )

        return bet

    def finish_round(self, round_id: int, client_seed: str = None) -> Dict[str, Any]:
        """Turu bitir ve kazananı belirle"""
        round = self.db.query(JackpotRound).filter(
            JackpotRound.id == round_id
        ).with_for_update().first()

        if not round:
            raise HTTPException(status_code=404, detail="Tur bulunamadı")

        if round.status == GameStatus.FINISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tur zaten bitmiş"
            )

        # Minimum oyuncu kontrolü
        unique_players = self.db.query(JackpotBet.user_id).filter(
            JackpotBet.round_id == round_id
        ).distinct().count()

        if unique_players < self.MIN_PLAYERS:
            # Yetersiz oyuncu - bahisleri iade et
            return self._cancel_round(round)

        # Client seed yoksa rastgele oluştur
        if not client_seed:
            client_seed = secrets.token_hex(16)
        round.client_seed = client_seed

        # Toplam bilet sayısı
        total_tickets = int(round.total_pot)

        # Kazanan bilet
        winning_ticket = self._calculate_winner(
            round.server_seed_revealed,
            client_seed,
            total_tickets
        )
        round.winner_ticket = winning_ticket

        # Kazanan bahisi bul
        winning_bet = self.db.query(JackpotBet).filter(
            JackpotBet.round_id == round_id,
            JackpotBet.ticket_start <= winning_ticket,
            JackpotBet.ticket_end >= winning_ticket
        ).first()

        if not winning_bet:
            logger.error(f"Kazanan bahis bulunamadı! Round: {round_id}, Ticket: {winning_ticket}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Kazanan belirlenemedi"
            )

        # Komisyon hesapla
        house_amount = round.total_pot * (round.house_cut / 100)
        winner_amount = round.total_pot - house_amount

        # Kazananı güncelle
        round.winner_id = winning_bet.user_id
        round.winner_amount = winner_amount
        round.house_amount = house_amount
        round.status = GameStatus.FINISHED
        round.end_time = datetime.utcnow()

        # Kazanan bahisi güncelle
        winning_bet.is_winner = True
        winning_bet.win_amount = winner_amount

        # Kazanana ödeme yap
        self.wallet.add_balance(
            user_id=winning_bet.user_id,
            amount=winner_amount,
            wallet_type=WalletType.COIN,
            transaction_type=TransactionType.GAME_WIN.value,
            description=f"Jackpot #{round.round_number} kazancı",
            reference_id=str(round.id),
            reference_type="jackpot"
        )

        # Oyun geçmişi kaydet (tüm katılımcılar için)
        bets = self.db.query(JackpotBet).filter(JackpotBet.round_id == round_id).all()
        for bet in bets:
            profit = winner_amount - bet.amount if bet.is_winner else -bet.amount
            history = GameHistory(
                user_id=bet.user_id,
                game_type="jackpot",
                game_id=round.id,
                bet_amount=bet.amount,
                win_amount=winner_amount if bet.is_winner else 0,
                profit=profit,
                is_winner=bet.is_winner
            )
            self.db.add(history)

        self.db.commit()

        logger.info(
            f"Jackpot #{round.round_number} bitti! "
            f"Kazanan: {winning_bet.user_id}, Miktar: {winner_amount}"
        )

        return {
            "round_id": round.id,
            "round_number": round.round_number,
            "winner_id": winning_bet.user_id,
            "winner_username": winning_bet.user.username,
            "winning_ticket": winning_ticket,
            "total_pot": round.total_pot,
            "winner_amount": winner_amount,
            "house_amount": house_amount,
            "server_seed": round.server_seed_revealed,
            "client_seed": client_seed
        }

    def _cancel_round(self, round: JackpotRound) -> Dict[str, Any]:
        """Turu iptal et ve bahisleri iade et"""
        bets = self.db.query(JackpotBet).filter(
            JackpotBet.round_id == round.id
        ).all()

        for bet in bets:
            # Bahisi iade et
            self.wallet.add_balance(
                user_id=bet.user_id,
                amount=bet.amount,
                wallet_type=WalletType.COIN,
                transaction_type=TransactionType.REFUND.value,
                description=f"Jackpot #{round.round_number} iadesi (yetersiz oyuncu)",
                reference_id=str(round.id),
                reference_type="jackpot_refund"
            )

        round.status = GameStatus.CANCELLED
        round.end_time = datetime.utcnow()
        self.db.commit()

        logger.info(f"Jackpot #{round.round_number} iptal edildi, {len(bets)} bahis iade edildi")

        return {
            "cancelled": True,
            "round_number": round.round_number,
            "refunded_bets": len(bets),
            "reason": "Yetersiz oyuncu"
        }

    def get_round_info(self, round_id: int = None) -> Dict[str, Any]:
        """Tur bilgilerini getir"""
        if round_id:
            round = self.db.query(JackpotRound).filter(
                JackpotRound.id == round_id
            ).first()
        else:
            round = self.get_current_round()

        if not round:
            return None

        # Bahisleri getir
        bets = self.db.query(JackpotBet).filter(
            JackpotBet.round_id == round.id
        ).order_by(JackpotBet.created_at.desc()).all()

        # Kullanıcı bazlı toplam bahisler
        player_totals = {}
        for bet in bets:
            if bet.user_id not in player_totals:
                player_totals[bet.user_id] = {
                    "user_id": bet.user_id,
                    "username": bet.user.username,
                    "avatar": bet.user.avatar,
                    "total_bet": 0,
                    "ticket_count": 0,
                    "win_chance": 0
                }
            player_totals[bet.user_id]["total_bet"] += bet.amount
            player_totals[bet.user_id]["ticket_count"] += bet.ticket_count

        # Kazanma şanslarını hesapla
        for player_id, data in player_totals.items():
            if round.total_pot > 0:
                data["win_chance"] = (data["ticket_count"] / int(round.total_pot)) * 100

        return {
            "id": round.id,
            "round_number": round.round_number,
            "status": round.status.value,
            "total_pot": round.total_pot,
            "total_bets": round.total_bets,
            "min_bet": round.min_bet,
            "max_bet": round.max_bet,
            "house_cut": round.house_cut,
            "server_seed_hash": round.server_seed,
            "start_time": round.start_time.isoformat() if round.start_time else None,
            "players": list(player_totals.values()),
            "winner": {
                "user_id": round.winner_id,
                "username": round.winner.username if round.winner else None,
                "amount": round.winner_amount,
                "ticket": round.winner_ticket
            } if round.status == GameStatus.FINISHED else None
        }

    def get_recent_rounds(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Son turları getir"""
        rounds = self.db.query(JackpotRound).filter(
            JackpotRound.status == GameStatus.FINISHED
        ).order_by(JackpotRound.created_at.desc()).limit(limit).all()

        return [
            {
                "id": r.id,
                "round_number": r.round_number,
                "total_pot": r.total_pot,
                "winner_username": r.winner.username if r.winner else None,
                "winner_amount": r.winner_amount,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in rounds
        ]


def get_jackpot_service(db: Session) -> JackpotService:
    """Jackpot service instance oluştur"""
    return JackpotService(db)
