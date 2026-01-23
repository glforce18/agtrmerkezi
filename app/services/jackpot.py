"""
AGTR Merkezi - Jackpot Game Service
Mevcut JackpotGame modeline uyumlu
"""

import hashlib
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import (
    User, WalletType, TransactionType,
    JackpotStatus, JackpotGame, JackpotBet, JackpotHistory
)
from app.services.wallet import get_wallet_service

logger = logging.getLogger(__name__)


class JackpotService:
    """Jackpot oyun servisi - Mevcut modele uyumlu"""

    # Oyun ayarları
    MIN_PLAYERS = 2
    MAX_PLAYERS = 50
    ROUND_DURATION = 30
    SPIN_DURATION = 10
    HOUSE_CUT_PERCENT = 5.0
    MIN_BET = 10.0
    MAX_BET = 1000.0

    def __init__(self, db: Session):
        self.db = db
        self.wallet = get_wallet_service(db)

    def _generate_seed(self) -> str:
        """Random seed oluştur"""
        return secrets.token_hex(32)

    def get_current_round(self) -> Optional[JackpotGame]:
        """Aktif turu getir"""
        return self.db.query(JackpotGame).filter(
            JackpotGame.status.in_([JackpotStatus.WAITING, JackpotStatus.ACTIVE])
        ).first()

    def get_or_create_round(self) -> JackpotGame:
        """Aktif tur varsa getir, yoksa yeni oluştur"""
        current_round = self.get_current_round()
        if current_round:
            return current_round

        # Son tur numarasını bul
        last_round = self.db.query(JackpotGame).order_by(
            JackpotGame.round_number.desc()
        ).first()
        next_number = (last_round.round_number + 1) if last_round else 1

        # Yeni tur oluştur
        new_round = JackpotGame(
            round_number=next_number,
            status=JackpotStatus.WAITING,
            total_pot=0,
            participant_count=0,
            house_cut_percent=self.HOUSE_CUT_PERCENT,
            roll_animation_seed=self._generate_seed()
        )
        self.db.add(new_round)
        self.db.commit()
        self.db.refresh(new_round)

        logger.info(f"Yeni jackpot turu oluşturuldu: #{next_number}")
        return new_round

    def place_bet(
        self,
        user_id: int,
        amount: float,
        ip_address: str = None,
        user_agent: str = None
    ) -> JackpotBet:
        """Bahis yap - Database-level locking ile race condition onleme"""
        # Miktar kontrolü (lock öncesi)
        if amount < self.MIN_BET:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum bahis: {self.MIN_BET} Armor"
            )

        if amount > self.MAX_BET:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum bahis: {self.MAX_BET} Armor"
            )

        # Kullanıcı kontrolü
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

        try:
            # Database-level locking ile tur al - race condition önleme
            round = self.db.query(JackpotGame).filter(
                JackpotGame.status.in_([JackpotStatus.WAITING, JackpotStatus.ACTIVE])
            ).with_for_update(nowait=False).first()

            if not round:
                # Yeni tur oluştur (lock ile)
                round = self.get_or_create_round()
                # Yeni oluşturulan turu da kilitle
                round = self.db.query(JackpotGame).filter(
                    JackpotGame.id == round.id
                ).with_for_update(nowait=False).first()

            if round.status not in [JackpotStatus.WAITING, JackpotStatus.ACTIVE]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu tura bahis yapılamaz"
                )

            # Savepoint oluştur - wallet deduction ve bet creation atomik olsun
            # Eğer bet oluşturma başarısız olursa, wallet deduction da geri alınır
            self.db.begin_nested()

            try:
                # Coin bakiye kontrolü ve düşürme (wallet service kendi lock'unu kullanır)
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

                # Bilet hesaplama (1 Armor = 1 bilet) - atomik okuma/yazma
                current_pot = round.total_pot or 0
                ticket_count = int(amount)
                ticket_start = int(current_pot) + 1
                ticket_end = ticket_start + ticket_count - 1

                # Bahis oluştur
                bet = JackpotBet(
                    game_id=round.id,
                    user_id=user_id,
                    amount=amount,
                    ticket_start=ticket_start,
                    ticket_end=ticket_end
                )
                self.db.add(bet)

                # Tur bilgilerini güncelle - atomik
                round.total_pot = current_pot + amount
                round.participant_count = (round.participant_count or 0) + 1

                # NOT: Status değişikliği jackpot_manager tarafından yapılacak
                # 2+ benzersiz oyuncu olduğunda manager ACTIVE'e geçirecek

                # Savepoint commit - nested transaction başarılı
                self.db.commit()
            except Exception as nested_error:
                # Savepoint rollback - wallet deduction da geri alınır
                self.db.rollback()
                raise nested_error

            self.db.commit()
            self.db.refresh(bet)

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Jackpot bahis hatasi: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bahis işlemi sırasında bir hata oluştu"
            )

        # Kazanma şansını hesapla
        win_chance = (ticket_count / int(round.total_pot)) * 100

        logger.info(
            f"Jackpot bahisi: user={user_id}, round=#{round.round_number}, "
            f"amount={amount}, tickets={ticket_start}-{ticket_end}"
        )

        # bet nesnesine ek bilgi ekle (response için)
        bet.win_chance = win_chance
        bet.round = round

        return bet

    def finish_round(self, round_id: int, client_seed: str = None) -> Dict[str, Any]:
        """Turu bitir ve kazananı belirle"""
        round = self.db.query(JackpotGame).filter(
            JackpotGame.id == round_id
        ).with_for_update().first()

        if not round:
            raise HTTPException(status_code=404, detail="Tur bulunamadı")

        if round.status == JackpotStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tur zaten bitmiş"
            )

        # Minimum oyuncu kontrolü
        unique_players = self.db.query(JackpotBet.user_id).filter(
            JackpotBet.game_id == round_id
        ).distinct().count()

        if unique_players < self.MIN_PLAYERS:
            return self._cancel_round(round)

        # Client seed yoksa rastgele oluştur
        if not client_seed:
            client_seed = secrets.token_hex(16)

        # Toplam bilet sayısı
        total_tickets = int(round.total_pot)

        # Kazanan hesapla
        combined = f"{round.roll_animation_seed}:{client_seed}"
        hash_result = hashlib.sha256(combined.encode()).hexdigest()
        number = int(hash_result[:8], 16)
        winning_ticket = number % total_tickets + 1

        round.winner_ticket = winning_ticket
        round.roll_value = number

        # Kazanan bahisi bul
        winning_bet = self.db.query(JackpotBet).filter(
            JackpotBet.game_id == round_id,
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
        house_amount = round.total_pot * (round.house_cut_percent / 100)
        winner_amount = round.total_pot - house_amount

        # Kazananı güncelle
        round.winner_id = winning_bet.user_id
        round.win_chance = (winning_bet.ticket_end - winning_bet.ticket_start + 1) / total_tickets * 100
        round.house_cut_amount = house_amount
        round.status = JackpotStatus.COMPLETED
        round.rolled_at = datetime.utcnow()
        round.completed_at = datetime.utcnow()

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

        # Kullanıcı istatistiklerini güncelle
        bets = self.db.query(JackpotBet).filter(JackpotBet.game_id == round_id).all()
        for bet in bets:
            is_winner = bet.user_id == winning_bet.user_id

            # Kullanıcının history kaydını bul veya oluştur - with_for_update ile race condition önleme
            history = self.db.query(JackpotHistory).filter(
                JackpotHistory.user_id == bet.user_id
            ).with_for_update().first()

            if not history:
                history = JackpotHistory(user_id=bet.user_id)
                self.db.add(history)
                self.db.flush()  # ID ataması için flush, sonra lock al
                history = self.db.query(JackpotHistory).filter(
                    JackpotHistory.user_id == bet.user_id
                ).with_for_update().first()

            # İstatistikleri güncelle
            history.total_games_played = (history.total_games_played or 0) + 1
            history.total_wagered = (history.total_wagered or 0) + bet.amount

            if is_winner:
                history.win_count = (history.win_count or 0) + 1
                history.total_won = (history.total_won or 0) + winner_amount
                if winner_amount > (history.biggest_win or 0):
                    history.biggest_win = winner_amount
            else:
                history.total_lost = (history.total_lost or 0) + bet.amount

        self.db.commit()

        winner_user = self.db.query(User).filter(User.id == winning_bet.user_id).first()

        logger.info(
            f"Jackpot #{round.round_number} bitti! "
            f"Kazanan: {winning_bet.user_id}, Miktar: {winner_amount}"
        )

        return {
            "round_id": round.id,
            "round_number": round.round_number,
            "winner_id": winning_bet.user_id,
            "winner_username": winner_user.username if winner_user else "Unknown",
            "winning_ticket": winning_ticket,
            "total_pot": round.total_pot,
            "winner_amount": winner_amount,
            "house_amount": house_amount,
            "server_seed": round.roll_animation_seed,
            "client_seed": client_seed
        }

    def _cancel_round(self, round: JackpotGame) -> Dict[str, Any]:
        """Turu iptal et ve bahisleri iade et"""
        bets = self.db.query(JackpotBet).filter(
            JackpotBet.game_id == round.id
        ).all()

        for bet in bets:
            self.wallet.add_balance(
                user_id=bet.user_id,
                amount=bet.amount,
                wallet_type=WalletType.COIN,
                transaction_type=TransactionType.REFUND.value,
                description=f"Jackpot #{round.round_number} iadesi (yetersiz oyuncu)",
                reference_id=str(round.id),
                reference_type="jackpot_refund"
            )

        round.status = JackpotStatus.CANCELLED
        round.completed_at = datetime.utcnow()
        self.db.commit()

        logger.info(f"Jackpot #{round.round_number} iptal edildi, {len(bets)} bahis iade edildi")

        return {
            "cancelled": True,
            "round_number": round.round_number,
            "refunded_bets": len(bets),
            "reason": "Yetersiz oyuncu"
        }

    def get_round_info(self, round_id: int = None) -> Optional[Dict[str, Any]]:
        """Tur bilgilerini getir"""
        if round_id:
            round = self.db.query(JackpotGame).filter(
                JackpotGame.id == round_id
            ).first()
        else:
            round = self.get_current_round()

        if not round:
            return None

        # Bahisleri getir
        bets = self.db.query(JackpotBet).filter(
            JackpotBet.game_id == round.id
        ).all()

        # Kullanıcı bazlı toplam bahisler - N+1 sorgu optimizasyonu
        user_ids = list(set(bet.user_id for bet in bets))
        users = self.db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
        user_map = {u.id: u for u in users}

        player_totals = {}
        for bet in bets:
            if bet.user_id not in player_totals:
                user = user_map.get(bet.user_id)
                player_totals[bet.user_id] = {
                    "user_id": bet.user_id,
                    "username": user.username if user else "Unknown",
                    "avatar": user.avatar if user else None,
                    "total_bet": 0,
                    "ticket_count": 0,
                    "win_chance": 0
                }
            player_totals[bet.user_id]["total_bet"] += bet.amount
            player_totals[bet.user_id]["ticket_count"] += int(bet.ticket_end - bet.ticket_start + 1)

        # Kazanma şanslarını hesapla
        total_tickets = int(round.total_pot) if round.total_pot else 0
        for player_id, data in player_totals.items():
            if total_tickets > 0:
                data["win_chance"] = (data["ticket_count"] / total_tickets) * 100

        winner_info = None
        if round.status == JackpotStatus.COMPLETED and round.winner_id:
            winner_user = self.db.query(User).filter(User.id == round.winner_id).first()
            winner_info = {
                "user_id": round.winner_id,
                "username": winner_user.username if winner_user else None,
                "amount": round.total_pot * (1 - round.house_cut_percent / 100) if round.total_pot else 0,
                "ticket": round.winner_ticket
            }

        return {
            "id": round.id,
            "round_number": round.round_number,
            "status": round.status.value,
            "total_pot": round.total_pot or 0,
            "total_bets": round.participant_count or 0,
            "min_bet": self.MIN_BET,
            "max_bet": self.MAX_BET,
            "house_cut": round.house_cut_percent,
            "server_seed_hash": hashlib.sha256(round.roll_animation_seed.encode()).hexdigest() if round.roll_animation_seed else None,
            "start_time": round.started_at.isoformat() if round.started_at else None,
            "players": list(player_totals.values()),
            "winner": winner_info
        }

    def get_recent_rounds(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Son turları getir"""
        rounds = self.db.query(JackpotGame).filter(
            JackpotGame.status == JackpotStatus.COMPLETED
        ).order_by(JackpotGame.created_at.desc()).limit(limit).all()

        # N+1 sorgu optimizasyonu - tüm kazananları tek seferde çek
        winner_ids = [r.winner_id for r in rounds if r.winner_id]
        winners = self.db.query(User).filter(User.id.in_(winner_ids)).all() if winner_ids else []
        winner_map = {u.id: u for u in winners}

        results = []
        for r in rounds:
            winner_user = winner_map.get(r.winner_id) if r.winner_id else None
            winner_amount = r.total_pot * (1 - r.house_cut_percent / 100) if r.total_pot else 0

            results.append({
                "id": r.id,
                "round_number": r.round_number,
                "total_pot": r.total_pot or 0,
                "winner_username": winner_user.username if winner_user else None,
                "winner_amount": winner_amount,
                "created_at": r.created_at.isoformat() if r.created_at else None
            })

        return results


def get_jackpot_service(db: Session) -> JackpotService:
    """Jackpot service instance oluştur"""
    return JackpotService(db)
