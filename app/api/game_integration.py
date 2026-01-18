"""
AGTR Merkezi - HL/CS 1.6 Oyun Entegrasyonu
AMX Mod X plugin API
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.connection import get_db
from app.models.database import User, WalletType, TransactionType
from app.services.wallet import get_wallet_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/game", tags=["game-integration"])


# ============ Ayarlar ============

# Puan ayarları
POINTS_PER_KILL = 0.5  # Kill başına
POINTS_PER_HEADSHOT = 1.0  # Headshot başına
POINTS_PER_MINUTE = 0.1  # Dakika başına oynama
POINTS_MATCH_WIN = 5.0  # Maç kazanma
POINTS_MVP = 10.0  # MVP ödülü
POINTS_FIRST_BLOOD = 2.0  # First blood

# Günlük limitler
DAILY_POINT_LIMIT = 100.0  # Günde max kazanılabilecek puan
DAILY_PLAYTIME_LIMIT = 480  # Günde max 8 saat (dakika)

# IP Whitelist (sunucu IP'leri)
ALLOWED_SERVER_IPS = [
    "127.0.0.1",
    "85.95.196.155",  # AGTR sunucu IP'leri eklenebilir
]

# API Key (env'den alınabilir)
GAME_API_KEY = getattr(settings, 'GAME_API_KEY', 'agtr-game-secret-key-2024')


# ============ Schemas ============

class PlayerStats(BaseModel):
    """Oyun sonu istatistikleri"""
    steam_id: str = Field(..., description="Steam ID (STEAM_0:X:XXXXX)")
    kills: int = Field(default=0, ge=0)
    deaths: int = Field(default=0, ge=0)
    headshots: int = Field(default=0, ge=0)
    playtime_minutes: int = Field(default=0, ge=0)
    is_winner: bool = Field(default=False)
    is_mvp: bool = Field(default=False)
    first_blood: bool = Field(default=False)
    server_name: str = Field(default="")
    map_name: str = Field(default="")


class PlayerConnect(BaseModel):
    """Oyuncu bağlantı bildirimi"""
    steam_id: str
    player_name: str
    ip_address: str


class PlayerDisconnect(BaseModel):
    """Oyuncu ayrılma bildirimi"""
    steam_id: str
    playtime_minutes: int


class BulkStats(BaseModel):
    """Toplu istatistik gönderimi"""
    players: list[PlayerStats]
    server_name: str
    map_name: str
    match_duration: int = 0


# ============ Security ============

def verify_api_key(x_api_key: str = Header(...)):
    """API key doğrulama"""
    if x_api_key != GAME_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz API key"
        )
    return True


def verify_server_ip(request: Request):
    """Sunucu IP doğrulama"""
    client_ip = request.client.host if request.client else None

    # Development modunda IP kontrolünü atla
    if settings.DEBUG:
        return True

    if client_ip not in ALLOWED_SERVER_IPS:
        logger.warning(f"Yetkisiz sunucu IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Yetkisiz sunucu"
        )
    return True


# ============ Helper Functions ============

def get_user_by_steam_id(db: Session, steam_id: str) -> Optional[User]:
    """Steam ID ile kullanıcı bul"""
    # steam_id formatını normalize et
    steam_id = steam_id.strip().upper()

    # User tablosunda steam_id alanını ara
    user = db.query(User).filter(User.steam_id == steam_id).first()
    return user


def calculate_points(stats: PlayerStats) -> float:
    """İstatistiklerden puan hesapla"""
    points = 0.0

    # Kill puanları
    points += stats.kills * POINTS_PER_KILL

    # Headshot bonusu
    points += stats.headshots * POINTS_PER_HEADSHOT

    # Oynama süresi
    points += min(stats.playtime_minutes, DAILY_PLAYTIME_LIMIT) * POINTS_PER_MINUTE

    # Kazanma bonusu
    if stats.is_winner:
        points += POINTS_MATCH_WIN

    # MVP bonusu
    if stats.is_mvp:
        points += POINTS_MVP

    # First blood bonusu
    if stats.first_blood:
        points += POINTS_FIRST_BLOOD

    return round(points, 2)


def check_daily_limit(db: Session, user_id: int) -> float:
    """Günlük limit kontrolü - kalan limit döndür"""
    from app.models.database import Transaction

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Bugün kazanılan toplam
    today_earned = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.reference_type == "game_stats",
        Transaction.created_at >= today_start
    ).scalar() or 0

    remaining = max(0, DAILY_POINT_LIMIT - today_earned)
    return remaining


# ============ Endpoints ============

@router.post("/report-stats")
async def report_player_stats(
    stats: PlayerStats,
    request: Request,
    db: Session = Depends(get_db),
    _api_key: bool = Depends(verify_api_key),
    _server_ip: bool = Depends(verify_server_ip)
):
    """
    Oyun sonu istatistikleri raporla
    AMX Mod X plugin'den çağrılır
    """
    # Kullanıcıyı bul
    user = get_user_by_steam_id(db, stats.steam_id)

    if not user:
        return {
            "success": False,
            "message": "Kullanıcı bulunamadı (Steam ID bağlı değil)",
            "steam_id": stats.steam_id
        }

    # Puan hesapla
    points = calculate_points(stats)

    if points <= 0:
        return {
            "success": True,
            "message": "Kazanılacak puan yok",
            "points": 0
        }

    # Günlük limit kontrolü
    remaining_limit = check_daily_limit(db, user.id)

    if remaining_limit <= 0:
        return {
            "success": False,
            "message": "Günlük limit aşıldı",
            "daily_limit": DAILY_POINT_LIMIT
        }

    # Limiti aşmayacak şekilde ayarla
    actual_points = min(points, remaining_limit)

    # Puan ekle
    wallet = get_wallet_service(db)
    wallet.add_balance(
        user_id=user.id,
        amount=actual_points,
        wallet_type=WalletType.COIN,
        transaction_type=TransactionType.BONUS.value,
        description=f"Oyun puanı ({stats.server_name} - {stats.map_name})",
        reference_id=f"{stats.steam_id}_{datetime.utcnow().timestamp()}",
        reference_type="game_stats"
    )

    logger.info(
        f"Oyun puanı: user={user.id}, steam={stats.steam_id}, "
        f"points={actual_points}, kills={stats.kills}"
    )

    return {
        "success": True,
        "message": f"+{actual_points} Coin kazandınız!",
        "points": actual_points,
        "remaining_daily_limit": remaining_limit - actual_points,
        "stats_breakdown": {
            "kills": stats.kills * POINTS_PER_KILL,
            "headshots": stats.headshots * POINTS_PER_HEADSHOT,
            "playtime": min(stats.playtime_minutes, DAILY_PLAYTIME_LIMIT) * POINTS_PER_MINUTE,
            "win_bonus": POINTS_MATCH_WIN if stats.is_winner else 0,
            "mvp_bonus": POINTS_MVP if stats.is_mvp else 0,
            "first_blood": POINTS_FIRST_BLOOD if stats.first_blood else 0
        }
    }


@router.post("/report-bulk")
async def report_bulk_stats(
    data: BulkStats,
    request: Request,
    db: Session = Depends(get_db),
    _api_key: bool = Depends(verify_api_key),
    _server_ip: bool = Depends(verify_server_ip)
):
    """
    Toplu istatistik raporla (maç sonu)
    Tüm oyuncuların istatistiklerini tek seferde gönderir
    """
    results = []

    for player_stats in data.players:
        player_stats.server_name = data.server_name
        player_stats.map_name = data.map_name

        # Her oyuncu için ayrı işlem
        user = get_user_by_steam_id(db, player_stats.steam_id)

        if not user:
            results.append({
                "steam_id": player_stats.steam_id,
                "success": False,
                "message": "Kullanıcı bulunamadı"
            })
            continue

        points = calculate_points(player_stats)
        remaining = check_daily_limit(db, user.id)
        actual_points = min(points, remaining)

        if actual_points > 0:
            wallet = get_wallet_service(db)
            wallet.add_balance(
                user_id=user.id,
                amount=actual_points,
                wallet_type=WalletType.COIN,
                transaction_type=TransactionType.BONUS.value,
                description=f"Oyun puanı ({data.server_name} - {data.map_name})",
                reference_id=f"{player_stats.steam_id}_{datetime.utcnow().timestamp()}",
                reference_type="game_stats"
            )

        results.append({
            "steam_id": player_stats.steam_id,
            "success": True,
            "points": actual_points
        })

    return {
        "success": True,
        "processed": len(results),
        "results": results
    }


@router.post("/player-connect")
async def player_connect(
    data: PlayerConnect,
    request: Request,
    db: Session = Depends(get_db),
    _api_key: bool = Depends(verify_api_key)
):
    """Oyuncu sunucuya bağlandığında bildirim"""
    user = get_user_by_steam_id(db, data.steam_id)

    if user:
        # Online durumunu Redis'e kaydet (opsiyonel)
        try:
            from app.core.redis_manager import redis_manager
            import asyncio
            asyncio.create_task(redis_manager.set_online_user(user.id))
        except Exception:
            pass

        return {
            "success": True,
            "user_id": user.id,
            "username": user.username,
            "balance": user.balance_coin or 0,
            "message": f"Hoş geldin {user.display_name or user.username}!"
        }

    return {
        "success": False,
        "message": "Steam hesabı bağlı değil. agtrmerkezi.com'dan hesabını bağla!"
    }


@router.post("/player-disconnect")
async def player_disconnect(
    data: PlayerDisconnect,
    request: Request,
    db: Session = Depends(get_db),
    _api_key: bool = Depends(verify_api_key)
):
    """Oyuncu sunucudan ayrıldığında bildirim"""
    user = get_user_by_steam_id(db, data.steam_id)

    if user and data.playtime_minutes > 0:
        # Oynama süresi puanı
        points = min(data.playtime_minutes, DAILY_PLAYTIME_LIMIT) * POINTS_PER_MINUTE
        remaining = check_daily_limit(db, user.id)
        actual_points = min(points, remaining)

        if actual_points > 0:
            wallet = get_wallet_service(db)
            wallet.add_balance(
                user_id=user.id,
                amount=actual_points,
                wallet_type=WalletType.COIN,
                transaction_type=TransactionType.BONUS.value,
                description=f"Oyun süresi puanı ({data.playtime_minutes} dk)",
                reference_id=f"{data.steam_id}_playtime_{datetime.utcnow().timestamp()}",
                reference_type="game_stats"
            )

            return {
                "success": True,
                "points": actual_points,
                "playtime": data.playtime_minutes
            }

    return {"success": True, "points": 0}


@router.get("/check-user/{steam_id}")
async def check_user(
    steam_id: str,
    db: Session = Depends(get_db),
    _api_key: bool = Depends(verify_api_key)
):
    """Steam ID ile kullanıcı kontrolü"""
    user = get_user_by_steam_id(db, steam_id)

    if user:
        return {
            "found": True,
            "user_id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "balance": user.balance_coin or 0
        }

    return {"found": False}


@router.get("/leaderboard")
async def get_game_leaderboard(
    period: str = "week",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Oyun liderlik tablosu (public)"""
    from app.models.database import Transaction

    if period == "day":
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0)
    elif period == "week":
        start_date = datetime.utcnow() - timedelta(days=7)
    elif period == "month":
        start_date = datetime.utcnow() - timedelta(days=30)
    else:
        start_date = datetime.utcnow() - timedelta(days=7)

    # En çok puan kazananlar
    results = db.query(
        Transaction.user_id,
        func.sum(Transaction.amount).label("total_points")
    ).filter(
        Transaction.reference_type == "game_stats",
        Transaction.created_at >= start_date
    ).group_by(Transaction.user_id).order_by(
        func.sum(Transaction.amount).desc()
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
                "total_points": round(row.total_points, 2)
            })

    return {
        "period": period,
        "leaderboard": leaderboard
    }


@router.get("/point-rates")
async def get_point_rates():
    """Puan oranları (public)"""
    return {
        "rates": {
            "per_kill": POINTS_PER_KILL,
            "per_headshot": POINTS_PER_HEADSHOT,
            "per_minute": POINTS_PER_MINUTE,
            "match_win": POINTS_MATCH_WIN,
            "mvp": POINTS_MVP,
            "first_blood": POINTS_FIRST_BLOOD
        },
        "daily_limits": {
            "points": DAILY_POINT_LIMIT,
            "playtime_minutes": DAILY_PLAYTIME_LIMIT
        }
    }
