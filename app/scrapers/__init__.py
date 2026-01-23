# AGTR Merkezi - Scraper System
# Oyun gorselleri, banner, icon ve animasyon toplama

from .base import BaseScraper
from .steamgriddb import SteamGridDBScraper
from .gamebanana import GameBananaScraper
from .asset_processor import AssetProcessor

__all__ = [
    'BaseScraper',
    'SteamGridDBScraper',
    'GameBananaScraper',
    'AssetProcessor'
]
