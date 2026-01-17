"""
AGTR Merkezi - Games API
Jackpot ve site içi oyunlar
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import User
from app.models.games import GameStatus
from app.services.jackpot import get_jackpot_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== SCHEMAS ====================

class PlaceBetRequest(BaseModel):
    amount: float = Field(gt=0, description="Bahis miktarı (Coin)")


class BetResponse(BaseModel):
    success: bool
    message: str
    bet_id: int
    round_number: int
    amount: float
    tickets: str
    win_chance: float
    new_balance: float


class PlayerInfo(BaseModel):
    user_id: int
    username: str
    avatar: Optional[str]
    total_bet: float
    ticket_count: int
    win_chance: float


class RoundInfoResponse(BaseModel):
    id: int
    round_number: int
    status: str
    total_pot: float
    total_bets: int
    min_bet: float
    max_bet: float
    house_cut: float
    server_seed_hash: str
    start_time: Optional[str]
    players: List[PlayerInfo]
    winner: Optional[dict]


class HistoryItem(BaseModel):
    id: int
    round_number: int
    total_pot: float
    winner_username: Optional[str]
    winner_amount: Optional[float]
    created_at: Optional[str]


# ==================== JACKPOT ENDPOINTS ====================

@router.get("/jackpot/current", response_model=RoundInfoResponse)
async def get_current_round(db: Session = Depends(get_db)):
    """Aktif jackpot turunu getir"""
    jackpot = get_jackpot_service(db)
    round_info = jackpot.get_round_info()

    if not round_info:
        # Yeni tur oluştur
        new_round = jackpot.get_or_create_round()
        round_info = jackpot.get_round_info(new_round.id)

    return round_info


@router.post("/jackpot/bet", response_model=BetResponse)
async def place_jackpot_bet(
    request: Request,
    data: PlaceBetRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Jackpot'a bahis yap"""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")[:500]

    jackpot = get_jackpot_service(db)
    bet = jackpot.place_bet(
        user_id=current_user.id,
        amount=data.amount,
        ip_address=client_ip,
        user_agent=user_agent
    )

    # Güncel bakiye
    from app.services.wallet import get_wallet_service
    from app.models.database import WalletType
    wallet = get_wallet_service(db)
    new_balance = wallet.get_balance(current_user.id, WalletType.COIN)

    return BetResponse(
        success=True,
        message=f"{data.amount} Coin ile bahis yapıldı!",
        bet_id=bet.id,
        round_number=bet.round.round_number,
        amount=bet.amount,
        tickets=f"{bet.ticket_start}-{bet.ticket_end}",
        win_chance=round(bet.win_chance, 2),
        new_balance=new_balance
    )


@router.get("/jackpot/round/{round_id}")
async def get_round_info(round_id: int, db: Session = Depends(get_db)):
    """Belirli bir turun bilgilerini getir"""
    jackpot = get_jackpot_service(db)
    round_info = jackpot.get_round_info(round_id)

    if not round_info:
        raise HTTPException(status_code=404, detail="Tur bulunamadı")

    return round_info


@router.get("/jackpot/history", response_model=List[HistoryItem])
async def get_jackpot_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Son jackpot turlarını getir"""
    jackpot = get_jackpot_service(db)
    return jackpot.get_recent_rounds(min(limit, 50))


@router.post("/jackpot/finish/{round_id}")
async def finish_jackpot_round(
    round_id: int,
    client_seed: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Jackpot turunu bitir (admin veya otomatik)"""
    # Admin kontrolü (normalde bu otomatik çalışır)
    if current_user.role.value not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yetkiniz yok"
        )

    jackpot = get_jackpot_service(db)
    result = jackpot.finish_round(round_id, client_seed)

    return result


@router.get("/jackpot/verify/{round_id}")
async def verify_round_fairness(round_id: int, db: Session = Depends(get_db)):
    """Tur adilliğini doğrula (Provably Fair)"""
    from app.models.games import JackpotRound
    import hashlib

    round = db.query(JackpotRound).filter(JackpotRound.id == round_id).first()

    if not round:
        raise HTTPException(status_code=404, detail="Tur bulunamadı")

    if round.status != GameStatus.FINISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece bitmiş turlar doğrulanabilir"
        )

    # Server seed'in hash'ini doğrula
    calculated_hash = hashlib.sha256(
        round.server_seed_revealed.encode()
    ).hexdigest()

    hash_matches = calculated_hash == round.server_seed

    # Kazanan bileti yeniden hesapla
    combined = f"{round.server_seed_revealed}:{round.client_seed}"
    result_hash = hashlib.sha256(combined.encode()).hexdigest()
    number = int(result_hash[:8], 16)
    total_tickets = int(round.total_pot)
    calculated_ticket = number % total_tickets + 1

    ticket_matches = calculated_ticket == round.winner_ticket

    return {
        "round_id": round.id,
        "round_number": round.round_number,
        "server_seed": round.server_seed_revealed,
        "server_seed_hash": round.server_seed,
        "client_seed": round.client_seed,
        "calculated_hash": calculated_hash,
        "hash_verified": hash_matches,
        "winning_ticket": round.winner_ticket,
        "calculated_ticket": calculated_ticket,
        "ticket_verified": ticket_matches,
        "fully_verified": hash_matches and ticket_matches
    }


# ==================== OYUNCU İSTATİSTİKLERİ ====================

@router.get("/stats/me")
async def get_my_game_stats(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Kendi oyun istatistiklerimi getir"""
    from app.models.games import GameHistory
    from sqlalchemy import func

    # Toplam istatistikler
    stats = db.query(
        func.count(GameHistory.id).label("total_games"),
        func.sum(GameHistory.bet_amount).label("total_bet"),
        func.sum(GameHistory.win_amount).label("total_won"),
        func.sum(GameHistory.profit).label("total_profit"),
        func.sum(func.cast(GameHistory.is_winner, Integer)).label("wins")
    ).filter(GameHistory.user_id == current_user.id).first()

    total_games = stats.total_games or 0
    wins = stats.wins or 0

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "total_games": total_games,
        "total_bet": stats.total_bet or 0,
        "total_won": stats.total_won or 0,
        "total_profit": stats.total_profit or 0,
        "wins": wins,
        "losses": total_games - wins,
        "win_rate": round((wins / total_games * 100) if total_games > 0 else 0, 2)
    }


@router.get("/leaderboard")
async def get_game_leaderboard(
    period: str = "all",  # all, week, month
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Oyun liderlik tablosu"""
    from app.models.games import GameHistory
    from sqlalchemy import func
    from datetime import datetime, timedelta

    query = db.query(
        GameHistory.user_id,
        func.sum(GameHistory.profit).label("total_profit"),
        func.count(GameHistory.id).label("games_played"),
        func.sum(func.cast(GameHistory.is_winner, Integer)).label("wins")
    )

    # Dönem filtresi
    if period == "week":
        start_date = datetime.utcnow() - timedelta(days=7)
        query = query.filter(GameHistory.created_at >= start_date)
    elif period == "month":
        start_date = datetime.utcnow() - timedelta(days=30)
        query = query.filter(GameHistory.created_at >= start_date)

    results = query.group_by(GameHistory.user_id).order_by(
        func.sum(GameHistory.profit).desc()
    ).limit(limit).all()

    leaderboard = []
    for i, row in enumerate(results):
        user = db.query(User).filter(User.id == row.user_id).first()
        if user:
            leaderboard.append({
                "rank": i + 1,
                "user_id": row.user_id,
                "username": user.username,
                "avatar": user.avatar,
                "total_profit": row.total_profit or 0,
                "games_played": row.games_played or 0,
                "wins": row.wins or 0
            })

    return leaderboard


# Integer import için
from sqlalchemy import Integer
