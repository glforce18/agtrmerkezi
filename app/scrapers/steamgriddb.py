"""
SteamGridDB Scraper
Oyun banner, logo, icon ve hero gorselleri
https://www.steamgriddb.com/api/v2
"""

import logging
from typing import Optional, Dict, List, Any
from pathlib import Path

from .base import BaseScraper

logger = logging.getLogger(__name__)


# Bilinen oyun ID'leri (SteamGridDB)
# Dogru ID'ler: https://www.steamgriddb.com/game/119 (CS 1.6), https://www.steamgriddb.com/game/21207 (HL)
KNOWN_GAMES = {
    'cs16': {
        'steamgriddb_id': 119,  # Counter-Strike 1.6
        'steam_id': 10,
        'name': 'Counter-Strike 1.6',
        'slug': 'cs16'
    },
    'halflife': {
        'steamgriddb_id': 21207,  # Half-Life
        'steam_id': 70,
        'name': 'Half-Life',
        'slug': 'halflife'
    },
    'halflife2': {
        'steamgriddb_id': 5310,
        'steam_id': 220,
        'name': 'Half-Life 2',
        'slug': 'halflife2'
    },
    'css': {
        'steamgriddb_id': 5318,  # Counter-Strike: Source
        'steam_id': 240,
        'name': 'Counter-Strike: Source',
        'slug': 'css'
    },
    'csgo': {
        'steamgriddb_id': 5262,  # CS:GO
        'steam_id': 730,
        'name': 'Counter-Strike: Global Offensive',
        'slug': 'csgo'
    },
    'tf2': {
        'steamgriddb_id': 5311,  # Team Fortress 2
        'steam_id': 440,
        'name': 'Team Fortress 2',
        'slug': 'tf2'
    },
    'dod': {
        'steamgriddb_id': 5255,  # Day of Defeat
        'steam_id': 30,
        'name': 'Day of Defeat',
        'slug': 'dod'
    },
    'sven': {
        'steamgriddb_id': 20584,  # Sven Co-op
        'steam_id': 225840,
        'name': 'Sven Co-op',
        'slug': 'sven'
    }
}


class SteamGridDBScraper(BaseScraper):
    """
    SteamGridDB API Scraper

    API Dokumanati: https://www.steamgriddb.com/api/v2

    Asset Turleri:
    - grids: Dikey posterler (600x900)
    - heroes: Yatay banner'lar (1920x620)
    - logos: Seffaf logolar
    - icons: Kare ikonlar

    Kullanim:
        async with SteamGridDBScraper(api_key='...') as scraper:
            assets = await scraper.scrape_game('cs16')
    """

    BASE_URL = 'https://www.steamgriddb.com/api/v2'

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.headers['Authorization'] = f'Bearer {api_key}'

    def get_source_name(self) -> str:
        return 'steamgriddb'

    async def search_game(self, query: str) -> Optional[List[Dict]]:
        """
        Oyun ara

        Args:
            query: Arama terimi

        Returns:
            Bulunan oyunlarin listesi
        """
        url = f'{self.BASE_URL}/search/autocomplete/{query}'
        result = await self.fetch(url)

        if result and result.get('success'):
            return result.get('data', [])
        return None

    async def get_game_by_steam_id(self, steam_id: int) -> Optional[Dict]:
        """Steam App ID ile oyun bul"""
        url = f'{self.BASE_URL}/games/steam/{steam_id}'
        result = await self.fetch(url)

        if result and result.get('success'):
            return result.get('data')
        return None

    async def get_grids(
        self,
        game_id: int,
        styles: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Grid (poster) gorselleri getir

        Args:
            game_id: SteamGridDB oyun ID
            styles: ['alternate', 'blurred', 'white_logo', 'material', 'no_logo']
            dimensions: ['460x215', '920x430', '600x900', '342x482']
            limit: Maksimum sonuc

        Returns:
            Grid listesi
        """
        url = f'{self.BASE_URL}/grids/game/{game_id}'
        params = {'limit': limit}

        if styles:
            params['styles'] = ','.join(styles)
        if dimensions:
            params['dimensions'] = ','.join(dimensions)

        result = await self.fetch(url, params=params)

        if result and result.get('success'):
            return result.get('data', [])
        return []

    async def get_heroes(
        self,
        game_id: int,
        styles: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Hero (banner) gorselleri getir - 1920x620 yatay bannerlar

        Args:
            game_id: SteamGridDB oyun ID
            styles: ['alternate', 'blurred', 'material']
            limit: Maksimum sonuc
        """
        url = f'{self.BASE_URL}/heroes/game/{game_id}'
        params = {'limit': limit}

        if styles:
            params['styles'] = ','.join(styles)

        result = await self.fetch(url, params=params)

        if result and result.get('success'):
            return result.get('data', [])
        return []

    async def get_logos(
        self,
        game_id: int,
        styles: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Logo gorselleri getir - seffaf PNG logolar

        Args:
            game_id: SteamGridDB oyun ID
            styles: ['official', 'white', 'black', 'custom']
            limit: Maksimum sonuc
        """
        url = f'{self.BASE_URL}/logos/game/{game_id}'
        params = {'limit': limit}

        if styles:
            params['styles'] = ','.join(styles)

        result = await self.fetch(url, params=params)

        if result and result.get('success'):
            return result.get('data', [])
        return []

    async def get_icons(
        self,
        game_id: int,
        styles: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Icon gorselleri getir - kare ikonlar

        Args:
            game_id: SteamGridDB oyun ID
            styles: ['official', 'custom']
            limit: Maksimum sonuc
        """
        url = f'{self.BASE_URL}/icons/game/{game_id}'
        params = {'limit': limit}

        if styles:
            params['styles'] = ','.join(styles)

        result = await self.fetch(url, params=params)

        if result and result.get('success'):
            return result.get('data', [])
        return []

    async def scrape_game(
        self,
        game_slug: str,
        save_path: Optional[Path] = None,
        download: bool = True
    ) -> Dict[str, Any]:
        """
        Tek bir oyunun tum asset'lerini topla

        Args:
            game_slug: Oyun slug (cs16, halflife, etc.)
            save_path: Kayit dizini
            download: Gorselleri indir

        Returns:
            Toplanan asset bilgileri
        """
        if game_slug not in KNOWN_GAMES:
            logger.error(f"Unknown game: {game_slug}")
            return {'error': f'Unknown game: {game_slug}'}

        game_info = KNOWN_GAMES[game_slug]
        game_id = game_info['steamgriddb_id']

        logger.info(f"Scraping assets for {game_info['name']} (ID: {game_id})")

        result = {
            'game': game_info,
            'assets': {
                'heroes': [],
                'grids': [],
                'logos': [],
                'icons': []
            },
            'downloaded': []
        }

        # Heroes (bannerlar) - en onemli
        heroes = await self.get_heroes(game_id, limit=5)
        result['assets']['heroes'] = heroes
        logger.info(f"Found {len(heroes)} heroes for {game_slug}")

        # Grids (posterler)
        grids = await self.get_grids(game_id, limit=5)
        result['assets']['grids'] = grids
        logger.info(f"Found {len(grids)} grids for {game_slug}")

        # Logos
        logos = await self.get_logos(game_id, limit=3)
        result['assets']['logos'] = logos
        logger.info(f"Found {len(logos)} logos for {game_slug}")

        # Icons
        icons = await self.get_icons(game_id, limit=3)
        result['assets']['icons'] = icons
        logger.info(f"Found {len(icons)} icons for {game_slug}")

        # Gorselleri indir
        if download and save_path:
            game_path = save_path / game_slug
            downloaded = []

            # En iyi hero'yu indir (banner)
            if heroes:
                best_hero = heroes[0]
                hero_path = await self.download_image(
                    best_hero['url'],
                    game_path / 'heroes',
                    f"{game_slug}_hero.png"
                )
                if hero_path:
                    downloaded.append({
                        'type': 'hero',
                        'path': str(hero_path),
                        'source_url': best_hero['url']
                    })

            # En iyi grid'i indir (poster)
            if grids:
                best_grid = grids[0]
                grid_path = await self.download_image(
                    best_grid['url'],
                    game_path / 'grids',
                    f"{game_slug}_grid.png"
                )
                if grid_path:
                    downloaded.append({
                        'type': 'grid',
                        'path': str(grid_path),
                        'source_url': best_grid['url']
                    })

            # En iyi logo'yu indir
            if logos:
                best_logo = logos[0]
                logo_path = await self.download_image(
                    best_logo['url'],
                    game_path / 'logos',
                    f"{game_slug}_logo.png"
                )
                if logo_path:
                    downloaded.append({
                        'type': 'logo',
                        'path': str(logo_path),
                        'source_url': best_logo['url']
                    })

            # En iyi icon'u indir
            if icons:
                best_icon = icons[0]
                icon_path = await self.download_image(
                    best_icon['url'],
                    game_path / 'icons',
                    f"{game_slug}_icon.png"
                )
                if icon_path:
                    downloaded.append({
                        'type': 'icon',
                        'path': str(icon_path),
                        'source_url': best_icon['url']
                    })

            result['downloaded'] = downloaded
            logger.info(f"Downloaded {len(downloaded)} assets for {game_slug}")

        return result

    async def scrape(
        self,
        games: Optional[List[str]] = None,
        save_path: Optional[Path] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Birden fazla oyun icin asset topla

        Args:
            games: Oyun slug listesi (None ise tum bilinen oyunlar)
            save_path: Kayit dizini

        Returns:
            Tum oyunlarin asset bilgileri
        """
        if games is None:
            games = list(KNOWN_GAMES.keys())

        results = []
        for game_slug in games:
            try:
                result = await self.scrape_game(
                    game_slug,
                    save_path=save_path,
                    download=save_path is not None
                )
                results.append(result)
            except Exception as e:
                logger.exception(f"Error scraping {game_slug}: {e}")
                results.append({
                    'game': {'slug': game_slug},
                    'error': str(e)
                })

        return results


# Convenience function
async def fetch_game_assets(
    api_key: str,
    game_slug: str,
    save_path: Path
) -> Dict[str, Any]:
    """
    Tek bir oyun icin asset'leri topla ve kaydet

    Kullanim:
        result = await fetch_game_assets(
            api_key='your_key',
            game_slug='cs16',
            save_path=Path('/var/www/agtrmerkezi/static/assets/games')
        )
    """
    async with SteamGridDBScraper(api_key) as scraper:
        return await scraper.scrape_game(game_slug, save_path, download=True)
