"""
AGTR Merkezi - Jackpot Tur Yöneticisi
Otomatik tur başlatma, geri sayım ve bitirme
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.models.connection import db_session
from app.models.database import JackpotGame, JackpotBet, JackpotStatus
from app.services.jackpot import get_jackpot_service

# Alias
JackpotRound = JackpotGame

logger = logging.getLogger(__name__)


class JackpotManager:
    """Jackpot tur yöneticisi"""

    # Ayarlar
    MIN_PLAYERS = 2  # Minimum oyuncu
    ROUND_DURATION = 30  # Tur süresi (saniye)
    COUNTDOWN_START = 30  # Geri sayım başlangıcı
    CHECK_INTERVAL = 1  # Kontrol aralığı (saniye)
    COOLDOWN_AFTER_ROUND = 5  # Tur sonrası bekleme

    def __init__(self):
        self.running = False
        self.current_countdown = 0
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Jackpot manager'ı başlat"""
        if self.running:
            logger.warning("Jackpot manager zaten çalışıyor")
            return

        self.running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Jackpot manager başlatıldı")

    async def stop(self):
        """Jackpot manager'ı durdur"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Jackpot manager durduruldu")

    async def _run_loop(self):
        """Ana döngü"""
        while self.running:
            try:
                await self._check_round()
                await asyncio.sleep(self.CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Jackpot manager error: {e}")
                await asyncio.sleep(5)  # Hata durumunda bekle

    async def _check_round(self):
        """Aktif turu kontrol et"""
        try:
            with db_session() as db:
                # Aktif turu bul
                round = db.query(JackpotRound).filter(
                    JackpotRound.status.in_([JackpotStatus.WAITING, JackpotStatus.ACTIVE])
                ).first()

                if not round:
                    # Aktif tur yoksa yeni oluştur
                    jackpot = get_jackpot_service(db)
                    round = jackpot.get_or_create_round()
                    return

                # Benzersiz oyuncu sayısını hesapla
                unique_players = db.query(JackpotBet.user_id).filter(
                    JackpotBet.game_id == round.id
                ).distinct().count()

                # Minimum oyuncuya ulaşıldı mı?
                if unique_players >= self.MIN_PLAYERS:
                    if round.status == JackpotStatus.WAITING:
                        # Turu aktif yap ve geri sayımı başlat
                        round.status = JackpotStatus.ACTIVE
                        round.started_at = datetime.utcnow()
                        db.commit()
                        logger.info(f"Jackpot #{round.round_number} aktif, geri sayım başladı")

                        # Geri sayım broadcast
                        await self._broadcast_countdown_start(round)

                    elif round.status == JackpotStatus.ACTIVE:
                        # Geri sayım kontrolü
                        if round.started_at:
                            elapsed = (datetime.utcnow() - round.started_at).total_seconds()
                            remaining = max(0, self.COUNTDOWN_START - int(elapsed))

                            if remaining > 0:
                                # Geri sayım devam ediyor
                                if remaining != self.current_countdown:
                                    self.current_countdown = remaining
                                    await self._broadcast_countdown(remaining)
                            else:
                                # Süre doldu, turu bitir
                                await self._finish_round(db, round)

        except Exception as e:
            logger.error(f"Check round error: {e}")

    async def _finish_round(self, db, round: JackpotRound):
        """Turu bitir"""
        try:
            jackpot = get_jackpot_service(db)
            result = jackpot.finish_round(round.id)

            logger.info(f"Jackpot #{round.round_number} bitti, kazanan: {result.get('winner_username')}")

            # Rolling animasyonu broadcast
            await self._broadcast_rolling(round, result)

            # Cooldown
            await asyncio.sleep(self.COOLDOWN_AFTER_ROUND)

            # Kazanan broadcast
            await self._broadcast_winner(result)

            # Yeni tur oluştur
            new_round = jackpot.get_or_create_round()
            await self._broadcast_new_round(new_round)

        except Exception as e:
            logger.error(f"Finish round error: {e}")

    async def _broadcast_countdown_start(self, round: JackpotRound):
        """Geri sayım başladı broadcast"""
        try:
            from app.api.websocket import broadcast_jackpot_round_update
            await broadcast_jackpot_round_update({
                "id": round.id,
                "round_number": round.round_number,
                "status": "active",
                "countdown_started": True,
                "countdown": self.COUNTDOWN_START
            })
        except Exception as e:
            logger.warning(f"Countdown start broadcast error: {e}")

    async def _broadcast_countdown(self, seconds: int):
        """Geri sayım broadcast"""
        try:
            from app.api.websocket import broadcast_jackpot_countdown
            await broadcast_jackpot_countdown(seconds)
        except Exception as e:
            logger.warning(f"Countdown broadcast error: {e}")

    async def _broadcast_rolling(self, round: JackpotRound, result: dict):
        """Rolling animasyonu broadcast"""
        try:
            from app.api.websocket import broadcast_jackpot_rolling
            from app.services.jackpot import get_jackpot_service
            from app.models.connection import db_session

            with db_session() as db:
                jackpot = get_jackpot_service(db)
                round_info = jackpot.get_round_info(round.id)

            animation_data = {
                "round_id": round.id,
                "round_number": round.round_number,
                "total_pot": result["total_pot"],
                "winner_id": result["winner_id"],
                "winner_username": result["winner_username"],
                "winning_ticket": result["winning_ticket"],
                "players": round_info.get("players", []) if round_info else [],
                "duration": 10
            }
            await broadcast_jackpot_rolling(animation_data)
        except Exception as e:
            logger.warning(f"Rolling broadcast error: {e}")

    async def _broadcast_winner(self, result: dict):
        """Kazanan broadcast"""
        try:
            from app.api.websocket import broadcast_jackpot_winner
            winner_data = {
                "round_id": result["round_id"],
                "round_number": result["round_number"],
                "winner_id": result["winner_id"],
                "winner_username": result["winner_username"],
                "winning_ticket": result["winning_ticket"],
                "total_pot": result["total_pot"],
                "winner_amount": result["winner_amount"],
                "server_seed": result["server_seed"],
                "client_seed": result["client_seed"]
            }
            await broadcast_jackpot_winner(winner_data)
        except Exception as e:
            logger.warning(f"Winner broadcast error: {e}")

    async def _broadcast_new_round(self, round: JackpotRound):
        """Yeni tur broadcast"""
        try:
            from app.api.websocket import broadcast_jackpot_round_update
            from app.services.jackpot import get_jackpot_service
            from app.models.connection import db_session

            with db_session() as db:
                jackpot = get_jackpot_service(db)
                round_info = jackpot.get_round_info(round.id)

            if round_info:
                round_info["new_round"] = True
                await broadcast_jackpot_round_update(round_info)
        except Exception as e:
            logger.warning(f"New round broadcast error: {e}")


# Global instance
jackpot_manager = JackpotManager()


async def start_jackpot_manager():
    """Jackpot manager'ı başlat"""
    await jackpot_manager.start()


async def stop_jackpot_manager():
    """Jackpot manager'ı durdur"""
    await jackpot_manager.stop()
