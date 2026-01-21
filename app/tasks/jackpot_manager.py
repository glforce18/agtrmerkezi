"""
AGTR Merkezi - Jackpot Tur Yöneticisi
Tam animasyonlu, bug-free jackpot sistemi
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.models.connection import db_session
from app.models.database import JackpotGame, JackpotBet, JackpotStatus
from app.services.jackpot import get_jackpot_service

logger = logging.getLogger(__name__)


class JackpotManager:
    """Jackpot tur yöneticisi - Tam animasyonlu"""

    # Ayarlar
    MIN_PLAYERS = 2
    COUNTDOWN_SECONDS = 30  # Geri sayım süresi
    ROLLING_SECONDS = 8  # Spinner animasyonu süresi
    WINNER_DISPLAY_SECONDS = 5  # Kazanan gösterim süresi
    CHECK_INTERVAL = 1  # Kontrol aralığı

    def __init__(self):
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self._countdown_task: Optional[asyncio.Task] = None
        self._is_round_finishing = False  # Tur bitirme kilidi

    async def start(self):
        """Jackpot manager'ı başlat"""
        if self.running:
            logger.warning("Jackpot manager zaten çalışıyor")
            return

        self.running = True

        # Başlangıçta yarım kalmış turları temizle
        await self._cleanup_stale_rounds()

        self._task = asyncio.create_task(self._run_loop())
        logger.info("Jackpot manager başlatıldı")

    async def stop(self):
        """Jackpot manager'ı durdur"""
        self.running = False

        if self._countdown_task and not self._countdown_task.done():
            self._countdown_task.cancel()

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Jackpot manager durduruldu")

    async def _cleanup_stale_rounds(self):
        """Yarım kalmış turları temizle"""
        try:
            with db_session() as db:
                # ACTIVE durumundaki turları WAITING'e çevir
                active_rounds = db.query(JackpotGame).filter(
                    JackpotGame.status == JackpotStatus.ACTIVE
                ).all()

                for round in active_rounds:
                    round.status = JackpotStatus.WAITING
                    round.started_at = None
                    logger.info(f"Yarım kalmış tur sıfırlandı: #{round.round_number}")

                db.commit()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    async def _run_loop(self):
        """Ana döngü"""
        while self.running:
            try:
                await self._check_round()
                await asyncio.sleep(self.CHECK_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Jackpot manager error: {e}")
                await asyncio.sleep(3)

    async def _check_round(self):
        """Aktif turu kontrol et"""
        # Tur bitirme işlemi devam ediyorsa bekle
        if self._is_round_finishing:
            return

        try:
            with db_session() as db:
                # Aktif veya bekleyen turu bul
                round = db.query(JackpotGame).filter(
                    JackpotGame.status.in_([JackpotStatus.WAITING, JackpotStatus.ACTIVE])
                ).first()

                if not round:
                    # Aktif tur yoksa yeni oluştur
                    jackpot = get_jackpot_service(db)
                    jackpot.get_or_create_round()
                    return

                # Benzersiz oyuncu sayısı
                unique_players = db.query(JackpotBet.user_id).filter(
                    JackpotBet.game_id == round.id
                ).distinct().count()

                # WAITING durumunda ve yeterli oyuncu varsa
                if round.status == JackpotStatus.WAITING and unique_players >= self.MIN_PLAYERS:
                    # Geri sayımı başlat
                    round.status = JackpotStatus.ACTIVE
                    round.started_at = datetime.utcnow()
                    db.commit()

                    logger.info(f"Jackpot #{round.round_number} aktif! {self.COUNTDOWN_SECONDS}s geri sayım başlıyor")

                    # Geri sayım task'ı başlat
                    if self._countdown_task and not self._countdown_task.done():
                        self._countdown_task.cancel()

                    self._countdown_task = asyncio.create_task(
                        self._run_countdown(round.id, round.round_number)
                    )

        except Exception as e:
            logger.error(f"Check round error: {e}")

    async def _run_countdown(self, round_id: int, round_number: int):
        """Geri sayım döngüsü"""
        try:
            # Başlangıç broadcast
            await self._broadcast_countdown_start(round_number)

            # Geri sayım
            for remaining in range(self.COUNTDOWN_SECONDS, 0, -1):
                if not self.running:
                    return

                await self._broadcast_countdown(remaining)
                logger.debug(f"Jackpot #{round_number} geri sayım: {remaining}")
                await asyncio.sleep(1)

            # Geri sayım bitti, turu bitir
            await self._broadcast_countdown(0)
            logger.info(f"Jackpot #{round_number} geri sayım bitti!")

            await self._finish_round(round_id)

        except asyncio.CancelledError:
            logger.info(f"Geri sayım iptal edildi: #{round_number}")
        except Exception as e:
            logger.error(f"Countdown error: {e}")
            self._is_round_finishing = False

    async def _finish_round(self, round_id: int):
        """Turu bitir - animasyonlu"""
        self._is_round_finishing = True

        try:
            with db_session() as db:
                # Turu bul
                round = db.query(JackpotGame).filter(JackpotGame.id == round_id).first()
                if not round or round.status != JackpotStatus.ACTIVE:
                    logger.warning(f"Tur bulunamadı veya aktif değil: {round_id}")
                    return

                # Jackpot servisini al ve turu bitir
                jackpot = get_jackpot_service(db)
                result = jackpot.finish_round(round_id)

                logger.info(f"Jackpot #{round.round_number} bitti! Kazanan: {result['winner_username']}")

                # 1. Rolling animasyonu broadcast
                await self._broadcast_rolling(round, result)

                # 2. Rolling animasyonu için bekle
                logger.info(f"Rolling animasyonu: {self.ROLLING_SECONDS} saniye")
                await asyncio.sleep(self.ROLLING_SECONDS)

                # 3. Kazanan broadcast
                await self._broadcast_winner(result)
                logger.info(f"Kazanan gösteriliyor: {result['winner_username']}")

                # 4. Kazanan ekranı için bekle
                await asyncio.sleep(self.WINNER_DISPLAY_SECONDS)

                # 5. Yeni tur oluştur (yeni session ile)

            # Yeni session ile yeni tur
            with db_session() as db:
                jackpot = get_jackpot_service(db)
                new_round = jackpot.get_or_create_round()
                await self._broadcast_new_round(new_round)
                logger.info(f"Yeni tur başladı: #{new_round.round_number}")

        except Exception as e:
            logger.error(f"Finish round error: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            self._is_round_finishing = False

    async def _broadcast_countdown_start(self, round_number: int):
        """Geri sayım başladı broadcast"""
        try:
            from app.api.websocket import broadcast_jackpot_round_update
            await broadcast_jackpot_round_update({
                "type": "countdown_start",
                "round_number": round_number,
                "status": "active",
                "countdown": self.COUNTDOWN_SECONDS
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

    async def _broadcast_rolling(self, round: JackpotGame, result: dict):
        """Rolling animasyonu broadcast"""
        try:
            from app.api.websocket import broadcast_jackpot_rolling
            from app.services.jackpot import get_jackpot_service

            with db_session() as db:
                jackpot = get_jackpot_service(db)
                round_info = jackpot.get_round_info(round.id)

            animation_data = {
                "type": "rolling",
                "round_id": round.id,
                "round_number": round.round_number,
                "total_pot": result["total_pot"],
                "winner_id": result["winner_id"],
                "winner_username": result["winner_username"],
                "winning_ticket": result["winning_ticket"],
                "players": round_info.get("players", []) if round_info else [],
                "duration": self.ROLLING_SECONDS
            }
            await broadcast_jackpot_rolling(animation_data)
        except Exception as e:
            logger.warning(f"Rolling broadcast error: {e}")

    async def _broadcast_winner(self, result: dict):
        """Kazanan broadcast"""
        try:
            from app.api.websocket import broadcast_jackpot_winner
            winner_data = {
                "type": "winner",
                "round_id": result["round_id"],
                "round_number": result["round_number"],
                "winner_id": result["winner_id"],
                "winner_username": result["winner_username"],
                "winning_ticket": result["winning_ticket"],
                "total_pot": result["total_pot"],
                "winner_amount": result["winner_amount"],
                "server_seed": result.get("server_seed", ""),
                "client_seed": result.get("client_seed", "")
            }
            await broadcast_jackpot_winner(winner_data)
        except Exception as e:
            logger.warning(f"Winner broadcast error: {e}")

    async def _broadcast_new_round(self, round: JackpotGame):
        """Yeni tur broadcast"""
        try:
            from app.api.websocket import broadcast_jackpot_round_update
            from app.services.jackpot import get_jackpot_service

            with db_session() as db:
                jackpot = get_jackpot_service(db)
                round_info = jackpot.get_round_info(round.id)

            if round_info:
                round_info["type"] = "new_round"
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
