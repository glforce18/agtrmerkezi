"""
AGTR Merkezi - Game Models
Jackpot ve site içi oyunlar için veritabanı modelleri
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.connection import Base


class GameStatus(enum.Enum):
    """Oyun durumları"""
    WAITING = "waiting"  # Oyuncular bekleniyor
    ACTIVE = "active"  # Oyun devam ediyor
    SPINNING = "spinning"  # Çark dönüyor
    FINISHED = "finished"  # Oyun bitti
    CANCELLED = "cancelled"  # İptal edildi


class JackpotRound(Base):
    """Jackpot oyun turu"""
    __tablename__ = "jackpot_rounds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    round_number = Column(Integer, nullable=False)  # Tur numarası
    status = Column(Enum(GameStatus), default=GameStatus.WAITING)

    # Havuz bilgileri
    total_pot = Column(Float, default=0.0)  # Toplam havuz
    total_bets = Column(Integer, default=0)  # Toplam bahis sayısı
    min_bet = Column(Float, default=10.0)  # Minimum bahis
    max_bet = Column(Float, default=1000.0)  # Maximum bahis

    # Kazanan bilgileri
    winner_id = Column(Integer, ForeignKey("users.id"))
    winner_ticket = Column(Integer)  # Kazanan bilet numarası
    winner_amount = Column(Float)  # Kazanılan miktar
    house_cut = Column(Float, default=0.0)  # Site komisyonu (%)
    house_amount = Column(Float, default=0.0)  # Site komisyon miktarı

    # Fairness (şeffaflık)
    server_seed = Column(String(64))  # Sunucu seed (hash'lenmiş)
    server_seed_revealed = Column(String(64))  # Açık seed (oyun bitince)
    client_seed = Column(String(64))  # İstemci seed
    round_hash = Column(String(64))  # Tur hash'i

    # Zamanlama
    start_time = Column(DateTime)  # Başlangıç zamanı
    end_time = Column(DateTime)  # Bitiş zamanı
    spin_duration = Column(Integer, default=10)  # Çark dönme süresi (saniye)

    # Tarihler
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    winner = relationship("User", foreign_keys=[winner_id])
    bets = relationship("JackpotBet", back_populates="round", lazy="dynamic")

    # Index
    __table_args__ = (
        Index('idx_jackpot_status', 'status'),
        Index('idx_jackpot_created', 'created_at'),
    )


class JackpotBet(Base):
    """Jackpot bahisi"""
    __tablename__ = "jackpot_bets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    round_id = Column(Integer, ForeignKey("jackpot_rounds.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Bahis bilgileri
    amount = Column(Float, nullable=False)
    ticket_start = Column(Integer, nullable=False)  # Başlangıç bilet numarası
    ticket_end = Column(Integer, nullable=False)  # Bitiş bilet numarası
    ticket_count = Column(Integer, nullable=False)  # Bilet sayısı
    win_chance = Column(Float)  # Kazanma şansı (%)

    # Sonuç
    is_winner = Column(Boolean, default=False)
    win_amount = Column(Float, default=0.0)

    # Meta
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Tarih
    created_at = Column(DateTime, default=func.now())

    # Relationships
    round = relationship("JackpotRound", back_populates="bets")
    user = relationship("User")

    # Index
    __table_args__ = (
        Index('idx_bet_round', 'round_id'),
        Index('idx_bet_user', 'user_id'),
    )


class GameHistory(Base):
    """Genel oyun geçmişi"""
    __tablename__ = "game_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_type = Column(String(50), nullable=False)  # jackpot, coinflip, vb.
    game_id = Column(Integer)  # İlgili oyun ID'si

    # Sonuç
    bet_amount = Column(Float, nullable=False)
    win_amount = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)  # win_amount - bet_amount
    is_winner = Column(Boolean, default=False)

    # Tarih
    created_at = Column(DateTime, default=func.now())

    # Index
    __table_args__ = (
        Index('idx_history_user', 'user_id'),
        Index('idx_history_game', 'game_type'),
        Index('idx_history_created', 'created_at'),
    )
