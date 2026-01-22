"""
AGTR Merkezi - Leaderboard & ELO API
ELO sistemine katilim icin Steam hesabi gerekli
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.core.security import (
    get_current_user,
    get_current_user_required,
    get_current_user_with_steam,
)
from app.models.connection import get_db
from app.models.database import User, UserStatus

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== CONSTANTS ====================

# ELO Tier thresholds
ELO_TIERS = {
    "Diamond": {"min": 2000, "color": "#B9F2FF", "icon": "diamond"},
    "Platinum": {"min": 1600, "color": "#E5E4E2", "icon": "crown"},
    "Gold": {"min": 1300, "color": "#FFD700", "icon": "trophy"},
    "Silver": {"min": 1000, "color": "#C0C0C0", "icon": "medal"},
    "Bronze": {"min": 0, "color": "#CD7F32", "icon": "shield"},
}

DEFAULT_ELO = 1000


# ==================== SCHEMAS ====================

class EloTierInfo(BaseModel):
    name: str
    color: str
    icon: str
    min_elo: int


class LeaderboardPlayer(BaseModel):
    position: int
    user_id: int
    username: str
    avatar: Optional[str]
    elo: int
    tier: EloTierInfo
    games_played: int
    wins: int
    losses: int
    win_rate: float
    kd_ratio: float
    is_online: bool = False
    steam_id: Optional[str]


class LeaderboardResponse(BaseModel):
    leaderboard: List[LeaderboardPlayer]
    total_players: int
    page: int
    per_page: int
    total_pages: int


class MyRankingResponse(BaseModel):
    position: int
    user_id: int
    username: str
    avatar: Optional[str]
    elo: int
    tier: EloTierInfo
    games_played: int
    wins: int
    losses: int
    win_rate: float
    kd_ratio: float
    is_participating: bool
    steam_connected: bool
    next_tier: Optional[EloTierInfo]
    elo_to_next_tier: Optional[int]


class JoinEloResponse(BaseModel):
    success: bool
    message: str
    elo: int
    tier: EloTierInfo


class LeaderboardStatsResponse(BaseModel):
    total_participants: int
    average_elo: float
    total_games: int
    tier_distribution: dict
    top_player: Optional[LeaderboardPlayer]
    recent_games_24h: int


# ==================== HELPER FUNCTIONS ====================

def get_tier_for_elo(elo: int) -> EloTierInfo:
    """ELO degerine gore tier bilgisini dondur"""
    for tier_name, tier_data in ELO_TIERS.items():
        if elo >= tier_data["min"]:
            return EloTierInfo(
                name=tier_name,
                color=tier_data["color"],
                icon=tier_data["icon"],
                min_elo=tier_data["min"]
            )
    # Default to Bronze
    return EloTierInfo(
        name="Bronze",
        color=ELO_TIERS["Bronze"]["color"],
        icon=ELO_TIERS["Bronze"]["icon"],
        min_elo=ELO_TIERS["Bronze"]["min"]
    )


def get_next_tier(current_elo: int) -> Optional[EloTierInfo]:
    """Bir sonraki tier bilgisini dondur"""
    tiers_sorted = sorted(ELO_TIERS.items(), key=lambda x: x[1]["min"])
    for tier_name, tier_data in tiers_sorted:
        if tier_data["min"] > current_elo:
            return EloTierInfo(
                name=tier_name,
                color=tier_data["color"],
                icon=tier_data["icon"],
                min_elo=tier_data["min"]
            )
    return None


def calculate_win_rate(wins: int, losses: int) -> float:
    """Kazanma oranini hesapla"""
    total = wins + losses
    if total == 0:
        return 0.0
    return round((wins / total) * 100, 2)


def is_participating_in_elo(user: User) -> bool:
    """Kullanici ELO sistemine katilmis mi?"""
    # Steam bagli ve en az 1 oyun oynamis ise katilimci sayilir
    # veya default ELO'dan farkli bir degere sahipse
    return bool(user.steam_id) and (
        user.wins > 0 or user.losses > 0 or user.elo != DEFAULT_ELO
    )


# ==================== ENDPOINTS ====================

@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    page: int = 1,
    per_page: int = 20,
    period: str = "all",  # all, week, month
    tier: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Genel ELO liderlik tablosu (public)
    Steam bagli ve ELO sistemine katilmis oyunculari listeler
    """
    if per_page > 100:
        per_page = 100

    # Base query - only Steam connected users with games
    query = db.query(User).filter(
        User.status == UserStatus.ACTIVE,
        User.steam_id.isnot(None),
        (User.wins > 0) | (User.losses > 0) | (User.elo != DEFAULT_ELO)
    )

    # Tier filter
    if tier and tier in ELO_TIERS:
        tier_data = ELO_TIERS[tier]
        # Find the next tier's min elo
        tier_list = list(ELO_TIERS.items())
        tier_index = [t[0] for t in tier_list].index(tier)
        if tier_index > 0:
            next_tier_min = tier_list[tier_index - 1][1]["min"]
            query = query.filter(
                User.elo >= tier_data["min"],
                User.elo < next_tier_min
            )
        else:
            query = query.filter(User.elo >= tier_data["min"])

    # Get total count
    total_players = query.count()

    # Order by ELO descending
    query = query.order_by(desc(User.elo), desc(User.wins))

    # Pagination
    offset = (page - 1) * per_page
    users = query.offset(offset).limit(per_page).all()

    # Build response
    leaderboard = []
    for i, user in enumerate(users):
        tier_info = get_tier_for_elo(user.elo)
        games_played = user.wins + user.losses

        leaderboard.append(LeaderboardPlayer(
            position=offset + i + 1,
            user_id=user.id,
            username=user.username,
            avatar=user.avatar,
            elo=user.elo,
            tier=tier_info,
            games_played=games_played,
            wins=user.wins,
            losses=user.losses,
            win_rate=calculate_win_rate(user.wins, user.losses),
            kd_ratio=user.kd_ratio or 0.0,
            is_online=user.is_online,
            steam_id=user.steam_id
        ))

    total_pages = (total_players + per_page - 1) // per_page

    return LeaderboardResponse(
        leaderboard=leaderboard,
        total_players=total_players,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/leaderboard/elo")
async def get_elo_rankings(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    ELO siralamasini getir (basit format)
    """
    if limit > 100:
        limit = 100

    users = db.query(User).filter(
        User.status == UserStatus.ACTIVE,
        User.steam_id.isnot(None),
        (User.wins > 0) | (User.losses > 0) | (User.elo != DEFAULT_ELO)
    ).order_by(desc(User.elo), desc(User.wins)).limit(limit).all()

    rankings = []
    for i, user in enumerate(users):
        tier_info = get_tier_for_elo(user.elo)
        rankings.append({
            "rank": i + 1,
            "user_id": user.id,
            "username": user.username,
            "avatar": user.avatar,
            "elo": user.elo,
            "tier": tier_info.name,
            "tier_color": tier_info.color,
            "wins": user.wins,
            "losses": user.losses,
            "total_points": user.elo + (user.wins * 10)  # For backward compatibility
        })

    return {"rankings": rankings, "total": len(rankings)}


@router.post("/leaderboard/join", response_model=JoinEloResponse)
async def join_elo_system(
    current_user: User = Depends(get_current_user_with_steam),
    db: Session = Depends(get_db)
):
    """
    ELO sistemine katil (Steam hesabi gerekli)
    Kullanici ilk kez katiliyorsa default ELO ile baslar
    """
    # Check if already participating
    if is_participating_in_elo(current_user):
        tier_info = get_tier_for_elo(current_user.elo)
        return JoinEloResponse(
            success=True,
            message="Zaten ELO sistemine katilmissiniz!",
            elo=current_user.elo,
            tier=tier_info
        )

    # Initialize ELO for the user (already has default values from model)
    # Just mark them as participating by ensuring default values are set
    if current_user.elo is None:
        current_user.elo = DEFAULT_ELO
    if current_user.wins is None:
        current_user.wins = 0
    if current_user.losses is None:
        current_user.losses = 0
    if current_user.kd_ratio is None:
        current_user.kd_ratio = 0.0

    db.commit()

    tier_info = get_tier_for_elo(current_user.elo)

    logger.info(f"User {current_user.username} joined ELO system with Steam ID: {current_user.steam_id}")

    return JoinEloResponse(
        success=True,
        message=f"ELO sistemine basariyla katildiniz! Baslangic ELO: {DEFAULT_ELO}",
        elo=current_user.elo,
        tier=tier_info
    )


@router.get("/leaderboard/me", response_model=MyRankingResponse)
async def get_my_ranking(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    Kullanicinin kendi siralamasi ve istatistikleri
    """
    is_participant = is_participating_in_elo(current_user)

    # Get position in leaderboard
    position = 0
    if is_participant:
        position = db.query(User).filter(
            User.status == UserStatus.ACTIVE,
            User.steam_id.isnot(None),
            (User.wins > 0) | (User.losses > 0) | (User.elo != DEFAULT_ELO),
            User.elo > current_user.elo
        ).count() + 1

    tier_info = get_tier_for_elo(current_user.elo or DEFAULT_ELO)
    next_tier = get_next_tier(current_user.elo or DEFAULT_ELO)
    elo_to_next = None
    if next_tier:
        elo_to_next = next_tier.min_elo - (current_user.elo or DEFAULT_ELO)

    games_played = (current_user.wins or 0) + (current_user.losses or 0)

    return MyRankingResponse(
        position=position,
        user_id=current_user.id,
        username=current_user.username,
        avatar=current_user.avatar,
        elo=current_user.elo or DEFAULT_ELO,
        tier=tier_info,
        games_played=games_played,
        wins=current_user.wins or 0,
        losses=current_user.losses or 0,
        win_rate=calculate_win_rate(current_user.wins or 0, current_user.losses or 0),
        kd_ratio=current_user.kd_ratio or 0.0,
        is_participating=is_participant,
        steam_connected=bool(current_user.steam_id),
        next_tier=next_tier,
        elo_to_next_tier=elo_to_next
    )


@router.get("/leaderboard/stats", response_model=LeaderboardStatsResponse)
async def get_leaderboard_stats(
    db: Session = Depends(get_db)
):
    """
    Genel liderlik tablosu istatistikleri
    """
    # Base query for participants
    participants = db.query(User).filter(
        User.status == UserStatus.ACTIVE,
        User.steam_id.isnot(None),
        (User.wins > 0) | (User.losses > 0) | (User.elo != DEFAULT_ELO)
    )

    total_participants = participants.count()

    # Average ELO
    avg_elo_result = participants.with_entities(func.avg(User.elo)).scalar()
    average_elo = float(avg_elo_result or DEFAULT_ELO)

    # Total games (wins + losses / 2 since each game has a winner and loser)
    total_wins = participants.with_entities(func.sum(User.wins)).scalar() or 0
    total_games = total_wins  # Each game produces one win

    # Tier distribution
    tier_distribution = {}
    for tier_name, tier_data in ELO_TIERS.items():
        tier_list = list(ELO_TIERS.items())
        tier_index = [t[0] for t in tier_list].index(tier_name)

        if tier_index > 0:
            next_tier_min = tier_list[tier_index - 1][1]["min"]
            count = participants.filter(
                User.elo >= tier_data["min"],
                User.elo < next_tier_min
            ).count()
        else:
            count = participants.filter(User.elo >= tier_data["min"]).count()

        tier_distribution[tier_name] = {
            "count": count,
            "color": tier_data["color"],
            "min_elo": tier_data["min"]
        }

    # Top player
    top_user = participants.order_by(desc(User.elo), desc(User.wins)).first()
    top_player = None
    if top_user:
        tier_info = get_tier_for_elo(top_user.elo)
        top_player = LeaderboardPlayer(
            position=1,
            user_id=top_user.id,
            username=top_user.username,
            avatar=top_user.avatar,
            elo=top_user.elo,
            tier=tier_info,
            games_played=top_user.wins + top_user.losses,
            wins=top_user.wins,
            losses=top_user.losses,
            win_rate=calculate_win_rate(top_user.wins, top_user.losses),
            kd_ratio=top_user.kd_ratio or 0.0,
            is_online=top_user.is_online,
            steam_id=top_user.steam_id
        )

    # Recent games (last 24h) - this would need a game history table
    # For now, estimate based on recent activity
    recent_games_24h = 0

    return LeaderboardStatsResponse(
        total_participants=total_participants,
        average_elo=round(average_elo, 1),
        total_games=total_games,
        tier_distribution=tier_distribution,
        top_player=top_player,
        recent_games_24h=recent_games_24h
    )


@router.get("/leaderboard/tiers")
async def get_tier_info():
    """
    Tum tier bilgilerini getir
    """
    tiers = []
    for tier_name, tier_data in ELO_TIERS.items():
        tiers.append({
            "name": tier_name,
            "color": tier_data["color"],
            "icon": tier_data["icon"],
            "min_elo": tier_data["min"]
        })

    return {"tiers": tiers}


@router.get("/leaderboard/user/{user_id}")
async def get_user_elo_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Belirli bir kullanicinin ELO istatistikleri (public)
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.status == UserStatus.ACTIVE
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanici bulunamadi"
        )

    is_participant = is_participating_in_elo(user)
    tier_info = get_tier_for_elo(user.elo or DEFAULT_ELO)

    # Get position if participating
    position = 0
    if is_participant:
        position = db.query(User).filter(
            User.status == UserStatus.ACTIVE,
            User.steam_id.isnot(None),
            (User.wins > 0) | (User.losses > 0) | (User.elo != DEFAULT_ELO),
            User.elo > user.elo
        ).count() + 1

    return {
        "user_id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "elo": user.elo or DEFAULT_ELO,
        "tier": {
            "name": tier_info.name,
            "color": tier_info.color,
            "icon": tier_info.icon
        },
        "position": position,
        "games_played": (user.wins or 0) + (user.losses or 0),
        "wins": user.wins or 0,
        "losses": user.losses or 0,
        "win_rate": calculate_win_rate(user.wins or 0, user.losses or 0),
        "kd_ratio": user.kd_ratio or 0.0,
        "is_participating": is_participant,
        "steam_connected": bool(user.steam_id)
    }
