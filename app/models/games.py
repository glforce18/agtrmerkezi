"""
AGTR Merkezi - Game Models
Jackpot ve site içi oyunlar için veritabanı modelleri

Not: Bu modeller database.py'de tanımlıdır.
Bu dosya sadece geriye dönük uyumluluk için import'ları sağlar.
"""

import enum


class GameStatus(enum.Enum):
    """Oyun durumları"""
    WAITING = "waiting"  # Oyuncular bekleniyor
    ACTIVE = "active"  # Oyun devam ediyor
    SPINNING = "spinning"  # Çark dönüyor
    FINISHED = "finished"  # Oyun bitti
    CANCELLED = "cancelled"  # İptal edildi


# Import models from database.py for backwards compatibility
from app.models.database import (
    JackpotGame as JackpotRound,  # Alias for compatibility
    JackpotBet,
    JackpotHistory as GameHistory,  # Alias for compatibility
)

__all__ = ['GameStatus', 'JackpotRound', 'JackpotBet', 'GameHistory']
