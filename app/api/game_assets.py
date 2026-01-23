"""
Game Assets API
Oyun gorselleri, haritalar ve scraper yonetimi
"""

import logging
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.connection import get_db
from app.core.security import get_current_user
from app.models.assets import (
    GameAsset, AnimationAsset, MapAsset,
    GameAssetType, AnimationCategory, AnimationFormat
)
from app.models.database import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/game-assets", tags=["Game Assets"])

# Asset dizini
ASSETS_DIR = Path('/var/www/agtrmerkezi/static/assets')


# ============================================
# PUBLIC ENDPOINTS
# ============================================

@router.get("/games")
async def get_game_list():
    """Desteklenen oyun listesi"""
    return {
        "success": True,
        "games": [
            {"slug": "cs16", "name": "Counter-Strike 1.6", "steam_id": 10, "icon": "🔫"},
            {"slug": "halflife", "name": "Half-Life", "steam_id": 70, "icon": "🎮"},
            {"slug": "css", "name": "Counter-Strike: Source", "steam_id": 240, "icon": "🎯"},
            {"slug": "csgo", "name": "CS:GO", "steam_id": 730, "icon": "💣"},
            {"slug": "tf2", "name": "Team Fortress 2", "steam_id": 440, "icon": "🏰"},
            {"slug": "sven", "name": "Sven Co-op", "steam_id": 225840, "icon": "👥"}
        ]
    }


@router.get("/games/{game_slug}")
async def get_game_assets(
    game_slug: str,
    asset_type: Optional[str] = Query(None, description="Asset tipi filtresi"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Oyuna ait asset'leri getir"""
    query = db.query(GameAsset).filter(
        GameAsset.game_slug == game_slug,
        GameAsset.is_active == True
    )

    if asset_type:
        try:
            asset_type_enum = GameAssetType(asset_type)
            query = query.filter(GameAsset.asset_type == asset_type_enum)
        except ValueError:
            pass

    query = query.order_by(GameAsset.is_featured.desc(), GameAsset.created_at.desc())
    assets = query.limit(limit).all()

    return {
        "success": True,
        "game_slug": game_slug,
        "count": len(assets),
        "assets": [asset.to_dict() for asset in assets]
    }


@router.get("/games/{game_slug}/banner")
async def get_game_banner(game_slug: str, db: Session = Depends(get_db)):
    """Oyunun ana banner'ini getir"""
    asset = db.query(GameAsset).filter(
        GameAsset.game_slug == game_slug,
        GameAsset.asset_type.in_([GameAssetType.BANNER, GameAssetType.HERO]),
        GameAsset.is_active == True
    ).order_by(GameAsset.is_featured.desc()).first()

    if not asset:
        return {
            "success": True,
            "asset": {
                "file_path": f"/static/assets/games/{game_slug}/default_banner.webp",
                "game_slug": game_slug
            }
        }

    return {"success": True, "asset": asset.to_dict()}


@router.get("/games/{game_slug}/maps")
async def get_game_maps(
    game_slug: str,
    map_type: Optional[str] = Query(None, description="Harita tipi (de_, cs_, fy_)"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Oyuna ait harita gorsellerini getir"""
    query = db.query(MapAsset).filter(
        MapAsset.game_slug == game_slug,
        MapAsset.is_active == True
    )

    if map_type:
        query = query.filter(MapAsset.map_type == map_type)

    query = query.order_by(MapAsset.popularity_score.desc(), MapAsset.map_name)
    maps = query.limit(limit).all()

    return {
        "success": True,
        "game_slug": game_slug,
        "count": len(maps),
        "maps": [m.to_dict() for m in maps]
    }


@router.get("/animations")
async def get_animations(
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Animasyon listesi"""
    query = db.query(AnimationAsset).filter(AnimationAsset.is_active == True)

    if category:
        try:
            cat_enum = AnimationCategory(category)
            query = query.filter(AnimationAsset.category == cat_enum)
        except ValueError:
            pass

    query = query.order_by(AnimationAsset.is_featured.desc(), AnimationAsset.use_count.desc())
    animations = query.limit(limit).all()

    return {
        "success": True,
        "count": len(animations),
        "animations": [a.to_dict() for a in animations]
    }


@router.get("/animations/{slug}")
async def get_animation(slug: str, db: Session = Depends(get_db)):
    """Tek animasyon detayi"""
    animation = db.query(AnimationAsset).filter(
        AnimationAsset.slug == slug,
        AnimationAsset.is_active == True
    ).first()

    if not animation:
        raise HTTPException(status_code=404, detail="Animasyon bulunamadi")

    animation.use_count += 1
    db.commit()

    return {"success": True, "animation": animation.to_dict()}


# ============================================
# ADMIN ENDPOINTS - SCRAPER
# ============================================

@router.post("/admin/scrape/steamgriddb")
async def trigger_steamgriddb_scrape(
    games: List[str] = Query(default=['cs16', 'halflife']),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """SteamGridDB scraper'i calistir"""
    # Admin kontrolu
    if not current_user.is_admin and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")

    from app.core.config import settings

    api_key = getattr(settings, 'STEAMGRIDDB_API_KEY', None)
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="STEAMGRIDDB_API_KEY ayarlanmamis. .env dosyasina ekleyin."
        )

    async def run_scraper():
        try:
            from app.scrapers import SteamGridDBScraper, AssetProcessor
            save_path = ASSETS_DIR / 'games'

            async with SteamGridDBScraper(api_key) as scraper:
                results = await scraper.scrape(games=games, save_path=save_path)

                processor = AssetProcessor()

                for game_result in results:
                    if 'error' in game_result:
                        continue

                    game_info = game_result.get('game', {})
                    game_slug = game_info.get('slug')

                    for downloaded in game_result.get('downloaded', []):
                        local_path = Path(downloaded['path'])
                        if local_path.exists():
                            webp_path = processor.convert_to_webp(local_path)
                            thumb_path = processor.create_thumbnail(local_path)

                            existing = db.query(GameAsset).filter(
                                GameAsset.game_slug == game_slug,
                                GameAsset.asset_type == GameAssetType(downloaded['type'])
                            ).first()

                            if existing:
                                existing.file_path = str(webp_path) if webp_path else str(local_path)
                                existing.thumbnail_path = str(thumb_path) if thumb_path else None
                                existing.source_url = downloaded.get('source_url')
                            else:
                                asset = GameAsset(
                                    game_slug=game_slug,
                                    game_name=game_info.get('name'),
                                    asset_type=GameAssetType(downloaded['type']),
                                    name=f"{game_slug}_{downloaded['type']}",
                                    slug=f"{game_slug}_{downloaded['type']}",
                                    file_path=str(webp_path) if webp_path else str(local_path),
                                    thumbnail_path=str(thumb_path) if thumb_path else None,
                                    source='steamgriddb',
                                    source_url=downloaded.get('source_url'),
                                    is_featured=True
                                )
                                db.add(asset)

                db.commit()
                logger.info(f"SteamGridDB scrape completed for {len(results)} games")

        except Exception as e:
            logger.exception(f"Scraper error: {e}")

    if background_tasks:
        background_tasks.add_task(run_scraper)
        return {"success": True, "message": "Scraper arka planda baslatildi", "games": games}
    else:
        await run_scraper()
        return {"success": True, "message": "Scraper tamamlandi", "games": games}


@router.post("/admin/scrape/gamebanana")
async def trigger_gamebanana_scrape(
    games: List[str] = Query(default=['cs16', 'halflife']),
    include_maps: bool = Query(True),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """GameBanana scraper'i calistir - harita gorselleri"""
    if not current_user.is_admin and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")

    async def run_scraper():
        try:
            from app.scrapers import GameBananaScraper, AssetProcessor
            save_path = ASSETS_DIR / 'games'

            async with GameBananaScraper() as scraper:
                results = await scraper.scrape(
                    games=games,
                    save_path=save_path,
                    include_maps=include_maps,
                    include_skins=False
                )

                processor = AssetProcessor()

                for game_result in results:
                    game_slug = game_result.get('game')

                    for map_data in game_result.get('maps', []):
                        existing = db.query(MapAsset).filter(
                            MapAsset.game_slug == game_slug,
                            MapAsset.map_name == map_data.get('name')
                        ).first()

                        local_path = map_data.get('local_path')
                        webp_path = None
                        if local_path and Path(local_path).exists():
                            webp_path = processor.convert_to_webp(Path(local_path))

                        if existing:
                            if webp_path:
                                existing.thumbnail_path = str(webp_path)
                            existing.popularity_score = map_data.get('downloads', 0)
                        else:
                            map_asset = MapAsset(
                                game_slug=game_slug,
                                map_name=map_data.get('name'),
                                map_slug=map_data.get('slug'),
                                thumbnail_path=str(webp_path) if webp_path else local_path,
                                source='gamebanana',
                                source_url=map_data.get('source_url'),
                                popularity_score=map_data.get('downloads', 0)
                            )

                            name_lower = map_data.get('name', '').lower()
                            for prefix in ['de_', 'cs_', 'fy_', 'aim_', 'awp_', 'as_']:
                                if name_lower.startswith(prefix):
                                    map_asset.map_type = prefix
                                    break

                            db.add(map_asset)

                db.commit()
                logger.info(f"GameBanana scrape completed")

        except Exception as e:
            logger.exception(f"GameBanana scraper error: {e}")

    if background_tasks:
        background_tasks.add_task(run_scraper)
        return {"success": True, "message": "GameBanana scraper baslatildi", "games": games}
    else:
        await run_scraper()
        return {"success": True, "message": "Scraper tamamlandi", "games": games}


@router.get("/admin/stats")
async def get_asset_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Asset istatistikleri"""
    if not current_user.is_admin and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")

    game_assets_count = db.query(GameAsset).count()
    animations_count = db.query(AnimationAsset).count()
    maps_count = db.query(MapAsset).count()

    game_distribution = db.query(
        GameAsset.game_slug,
        func.count(GameAsset.id)
    ).group_by(GameAsset.game_slug).all()

    return {
        "success": True,
        "stats": {
            "total_game_assets": game_assets_count,
            "total_animations": animations_count,
            "total_maps": maps_count,
            "by_game": {g: c for g, c in game_distribution}
        }
    }
