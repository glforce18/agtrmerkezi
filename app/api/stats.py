"""
AGTR Merkezi v6.0 - Stats API
Gelismis istatistik API'leri
"""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import GameServer, User
from app.services.stats_service import StatsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/servers/{server_id}/stats", tags=["Stats"])


# ============================================
# Helper Functions
# ============================================


async def verify_server_ownership(server_id: int, current_user: User, db: Session) -> GameServer:
    """
    Sunucu sahipligini dogrula

    Admin/Superadmin kullanıcılar tüm sunuculara erişebilir
    """
    from app.models.database import UserRole

    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Admin bypass - admin kullanıcılar tüm sunuculara erişebilir
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        return server

    # Normal kullanıcı - sadece kendi sunucusu
    if server.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return server


# ============================================
# API Endpoints
# ============================================


@router.get("/hourly")
async def get_hourly_stats(
    server_id: int,
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Saatlik oyuncu istatistikleri

    Args:
        server_id: Sunucu ID
        hours: Kac saatlik veri (varsayilan 24)

    Returns:
        Saatlik istatistik listesi
    """
    await verify_server_ownership(server_id, current_user, db)

    stats_service = StatsService()
    return stats_service.get_hourly_stats(server_id, hours)


@router.get("/daily")
async def get_daily_stats(
    server_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Gunluk oyuncu istatistikleri

    Args:
        server_id: Sunucu ID
        days: Kac gunluk veri (varsayilan 30)

    Returns:
        Gunluk istatistik listesi
    """
    await verify_server_ownership(server_id, current_user, db)

    stats_service = StatsService()
    return stats_service.get_daily_stats(server_id, days)


@router.get("/heatmap")
async def get_peak_hours_heatmap(
    server_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Yogunluk haritasi (24x7 grid)

    Args:
        server_id: Sunucu ID
        days: Kac gunluk veri (varsayilan 30)

    Returns:
        24 saat x 7 gun yogunluk verisi
    """
    await verify_server_ownership(server_id, current_user, db)

    stats_service = StatsService()
    return stats_service.get_peak_hours_heatmap(server_id, days)


@router.get("/retention")
async def get_retention_rate(
    server_id: int,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Oyuncu sadakat orani

    Args:
        server_id: Sunucu ID
        days: Analiz suresi (varsayilan 7)

    Returns:
        Sadakat istatistikleri
    """
    await verify_server_ownership(server_id, current_user, db)

    stats_service = StatsService()
    return stats_service.calculate_retention_rate(server_id, days)


@router.get("/maps")
async def get_map_distribution(
    server_id: int,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Harita dagilimi

    Args:
        server_id: Sunucu ID
        days: Analiz suresi (varsayilan 7)

    Returns:
        Harita oyun suresi dagilimi
    """
    await verify_server_ownership(server_id, current_user, db)

    stats_service = StatsService()
    return stats_service.get_map_distribution(server_id, days)


@router.get("/export")
async def export_stats_csv(
    server_id: int,
    date_from: date,
    date_to: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """
    Istatistikleri CSV olarak indir

    Args:
        server_id: Sunucu ID
        date_from: Baslangic tarihi
        date_to: Bitis tarihi

    Returns:
        CSV dosyasi
    """
    await verify_server_ownership(server_id, current_user, db)

    stats_service = StatsService()
    csv_data = stats_service.export_stats_csv(server_id, date_from, date_to)

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=stats_{server_id}.csv"},
    )
