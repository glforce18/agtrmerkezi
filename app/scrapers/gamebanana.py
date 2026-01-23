"""
GameBanana Scraper
CS 1.6 ve Half-Life mod gorselleri, harita resimleri, silah skinleri
https://gamebanana.com/apidocs
"""

import logging
import re
from typing import Optional, Dict, List, Any
from pathlib import Path
from bs4 import BeautifulSoup

from .base import BaseScraper

logger = logging.getLogger(__name__)


# GameBanana oyun ID'leri
GAMEBANANA_GAMES = {
    'cs16': {
        'id': 4254,  # Counter-Strike 1.6
        'name': 'Counter-Strike 1.6',
        'slug': 'cs16'
    },
    'halflife': {
        'id': 34,  # Half-Life
        'name': 'Half-Life',
        'slug': 'halflife'
    },
    'css': {
        'id': 4941,  # Counter-Strike: Source
        'name': 'Counter-Strike: Source',
        'slug': 'css'
    },
    'dod': {
        'id': 4942,  # Day of Defeat: Source
        'name': 'Day of Defeat',
        'slug': 'dod'
    }
}

# Populer CS 1.6 haritalari
CS16_POPULAR_MAPS = [
    'de_dust2', 'de_inferno', 'de_nuke', 'de_train', 'de_mirage',
    'de_cache', 'de_cbble', 'de_aztec', 'de_dust', 'de_tuscan',
    'cs_assault', 'cs_office', 'cs_italy', 'cs_militia',
    'fy_iceworld', 'fy_pool_day', 'awp_map', 'aim_map'
]

# Half-Life populer haritalari
HL_POPULAR_MAPS = [
    'crossfire', 'boot_camp', 'subtransit', 'stalkyard', 'undertow',
    'bounce', 'datacore', 'frenzy', 'lambda_bunker', 'snark_pit'
]


class GameBananaScraper(BaseScraper):
    """
    GameBanana Scraper

    Mod, harita ve skin gorselleri toplar

    Kullanim:
        async with GameBananaScraper() as scraper:
            maps = await scraper.scrape_maps('cs16', limit=20)
    """

    BASE_URL = 'https://gamebanana.com/apiv11'
    SITE_URL = 'https://gamebanana.com'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # GameBanana daha yavas, rate limit artir
        self.rate_limit = 2.0

    def get_source_name(self) -> str:
        return 'gamebanana'

    async def get_maps(
        self,
        game_id: int,
        page: int = 1,
        per_page: int = 20,
        sort: str = 'downloads'
    ) -> Optional[Dict]:
        """
        Harita listesi getir

        Args:
            game_id: GameBanana oyun ID
            page: Sayfa numarasi
            per_page: Sayfa basi sonuc
            sort: Siralama (downloads, date, rating)

        Returns:
            Harita listesi
        """
        url = f'{self.BASE_URL}/Mod/Index'
        params = {
            '_aGameRowIds[]': game_id,
            '_sModelName': 'Map',
            '_nPage': page,
            '_nPerpage': per_page,
            '_sSort': sort
        }

        return await self.fetch(url, params=params)

    async def get_map_details(self, map_id: int) -> Optional[Dict]:
        """Tek harita detaylari"""
        url = f'{self.BASE_URL}/Map/{map_id}'
        return await self.fetch(url)

    async def get_map_images(self, map_id: int) -> List[Dict]:
        """Harita gorsellerini getir"""
        url = f'{self.BASE_URL}/Map/{map_id}/Images'
        result = await self.fetch(url)

        if result and isinstance(result, list):
            return result
        return []

    async def get_skins(
        self,
        game_id: int,
        category: str = 'Skin',
        page: int = 1,
        per_page: int = 20
    ) -> Optional[Dict]:
        """
        Skin listesi getir

        Args:
            game_id: GameBanana oyun ID
            category: Kategori (Skin, Sound, Spray, etc.)
            page: Sayfa
            per_page: Sonuc sayisi
        """
        url = f'{self.BASE_URL}/Mod/Index'
        params = {
            '_aGameRowIds[]': game_id,
            '_sModelName': category,
            '_nPage': page,
            '_nPerpage': per_page,
            '_sSort': 'downloads'
        }

        return await self.fetch(url, params=params)

    async def search(
        self,
        query: str,
        game_id: Optional[int] = None,
        model: str = 'Map'
    ) -> Optional[Dict]:
        """
        Arama yap

        Args:
            query: Arama terimi
            game_id: Oyun filtresi
            model: Mod tipi (Map, Skin, Sound, etc.)
        """
        url = f'{self.BASE_URL}/Util/Search'
        params = {
            '_sSearchString': query,
            '_sModelName': model
        }

        if game_id:
            params['_aGameRowIds[]'] = game_id

        return await self.fetch(url, params=params)

    async def scrape_maps(
        self,
        game_slug: str,
        limit: int = 20,
        save_path: Optional[Path] = None,
        popular_only: bool = True
    ) -> List[Dict]:
        """
        Harita gorsellerini topla

        Args:
            game_slug: Oyun slug (cs16, halflife)
            limit: Maksimum harita sayisi
            save_path: Kayit dizini
            popular_only: Sadece populer haritalar

        Returns:
            Harita bilgileri listesi
        """
        if game_slug not in GAMEBANANA_GAMES:
            logger.error(f"Unknown game: {game_slug}")
            return []

        game_info = GAMEBANANA_GAMES[game_slug]
        game_id = game_info['id']

        results = []

        # Populer harita listesi
        popular_maps = CS16_POPULAR_MAPS if game_slug == 'cs16' else HL_POPULAR_MAPS

        if popular_only:
            # Populer haritalari ara
            for map_name in popular_maps[:limit]:
                logger.info(f"Searching for map: {map_name}")
                search_result = await self.search(map_name, game_id, 'Map')

                if search_result and search_result.get('_aRecords'):
                    records = search_result['_aRecords']
                    if records:
                        # Ilk sonucu al
                        map_data = records[0]
                        map_info = await self._process_map(map_data, save_path, game_slug)
                        if map_info:
                            results.append(map_info)
        else:
            # Tum haritalari getir
            maps_response = await self.get_maps(game_id, per_page=limit)
            if maps_response and maps_response.get('_aRecords'):
                for map_data in maps_response['_aRecords']:
                    map_info = await self._process_map(map_data, save_path, game_slug)
                    if map_info:
                        results.append(map_info)

        logger.info(f"Scraped {len(results)} maps for {game_slug}")
        return results

    async def _process_map(
        self,
        map_data: Dict,
        save_path: Optional[Path],
        game_slug: str
    ) -> Optional[Dict]:
        """Tek harita isle"""
        try:
            map_id = map_data.get('_idRow')
            map_name = map_data.get('_sName', 'unknown')

            # Screenshot URL'i bul
            preview_url = None

            # _aPreviewMedia icerisinde screenshot ara
            preview_media = map_data.get('_aPreviewMedia', {})
            if preview_media:
                images = preview_media.get('_aImages', [])
                if images:
                    # 220 boyutlu (orta) resmi tercih et
                    preview_url = images[0].get('_sFile220') or images[0].get('_sBaseUrl')

            if not preview_url and map_data.get('_sImageUrl'):
                preview_url = map_data['_sImageUrl']

            result = {
                'id': map_id,
                'name': map_name,
                'slug': self.sanitize_filename(map_name),
                'game': game_slug,
                'preview_url': preview_url,
                'downloads': map_data.get('_nDownloadCount', 0),
                'likes': map_data.get('_nLikeCount', 0),
                'source': 'gamebanana',
                'source_url': f"{self.SITE_URL}/maps/{map_id}"
            }

            # Gorseli indir
            if save_path and preview_url:
                filename = f"{result['slug']}.jpg"
                downloaded = await self.download_image(
                    preview_url,
                    save_path / game_slug / 'maps',
                    filename
                )
                if downloaded:
                    result['local_path'] = str(downloaded)

            return result

        except Exception as e:
            logger.exception(f"Error processing map: {e}")
            return None

    async def scrape_weapon_skins(
        self,
        game_slug: str = 'cs16',
        limit: int = 20,
        save_path: Optional[Path] = None
    ) -> List[Dict]:
        """
        Silah skin gorsellerini topla

        Args:
            game_slug: Oyun (cs16)
            limit: Maksimum skin sayisi
            save_path: Kayit dizini

        Returns:
            Skin bilgileri
        """
        if game_slug not in GAMEBANANA_GAMES:
            return []

        game_info = GAMEBANANA_GAMES[game_slug]
        game_id = game_info['id']

        results = []

        # Skin kategorilerini ara
        skins_response = await self.get_skins(game_id, 'Skin', per_page=limit)

        if skins_response and skins_response.get('_aRecords'):
            for skin_data in skins_response['_aRecords']:
                try:
                    skin_id = skin_data.get('_idRow')
                    skin_name = skin_data.get('_sName', 'unknown')

                    preview_url = None
                    preview_media = skin_data.get('_aPreviewMedia', {})
                    if preview_media:
                        images = preview_media.get('_aImages', [])
                        if images:
                            preview_url = images[0].get('_sFile220') or images[0].get('_sBaseUrl')

                    result = {
                        'id': skin_id,
                        'name': skin_name,
                        'slug': self.sanitize_filename(skin_name),
                        'game': game_slug,
                        'type': 'weapon_skin',
                        'preview_url': preview_url,
                        'downloads': skin_data.get('_nDownloadCount', 0),
                        'source': 'gamebanana'
                    }

                    if save_path and preview_url:
                        filename = f"{result['slug']}.jpg"
                        downloaded = await self.download_image(
                            preview_url,
                            save_path / game_slug / 'skins',
                            filename
                        )
                        if downloaded:
                            result['local_path'] = str(downloaded)

                    results.append(result)

                except Exception as e:
                    logger.error(f"Error processing skin: {e}")

        logger.info(f"Scraped {len(results)} weapon skins")
        return results

    async def scrape(
        self,
        games: Optional[List[str]] = None,
        save_path: Optional[Path] = None,
        include_maps: bool = True,
        include_skins: bool = True,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Ana scrape metodu

        Args:
            games: Oyun listesi
            save_path: Kayit dizini
            include_maps: Haritalari dahil et
            include_skins: Skinleri dahil et
        """
        if games is None:
            games = ['cs16', 'halflife']

        results = []

        for game_slug in games:
            game_result = {
                'game': game_slug,
                'maps': [],
                'skins': []
            }

            if include_maps:
                maps = await self.scrape_maps(game_slug, limit=15, save_path=save_path)
                game_result['maps'] = maps

            if include_skins and game_slug == 'cs16':
                skins = await self.scrape_weapon_skins(game_slug, limit=10, save_path=save_path)
                game_result['skins'] = skins

            results.append(game_result)

        return results
