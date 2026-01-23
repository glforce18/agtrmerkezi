"""
Base Scraper Class
Tum scraper'lar icin temel sinif
"""

import asyncio
import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Tum scraper'lar icin base class"""

    # Rate limiting
    DEFAULT_RATE_LIMIT = 1.0  # saniye arasi bekleme
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        rate_limit: float = DEFAULT_RATE_LIMIT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT
    ):
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self._last_request_time = 0

        # Default headers
        self.headers = {
            'User-Agent': 'AGTR-Merkezi-Scraper/1.0 (Gaming Community Platform)',
            'Accept': 'application/json, image/*',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8'
        }

    async def __aenter__(self):
        """Context manager girisi"""
        await self.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager cikisi"""
        await self.close_session()

    async def init_session(self):
        """HTTP session olustur"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=timeout
            )

    async def close_session(self):
        """HTTP session kapat"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _rate_limit_wait(self):
        """Rate limiting icin bekle"""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch(
        self,
        url: str,
        method: str = 'GET',
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Dict | bytes]:
        """
        HTTP request yap (retry ve rate limiting ile)

        Returns:
            JSON response veya binary data
        """
        await self.init_session()
        await self._rate_limit_wait()

        request_headers = {**self.headers, **(headers or {})}

        for attempt in range(self.max_retries):
            try:
                async with self.session.request(
                    method,
                    url,
                    params=params,
                    json=json_data,
                    headers=request_headers
                ) as response:

                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')

                        if 'application/json' in content_type:
                            return await response.json()
                        elif 'image/' in content_type or 'application/octet-stream' in content_type:
                            return await response.read()
                        else:
                            return await response.text()

                    elif response.status == 429:  # Rate limited
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limited, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue

                    elif response.status >= 500:  # Server error
                        logger.warning(f"Server error {response.status}, retry {attempt + 1}")
                        await asyncio.sleep(2 ** attempt)
                        continue

                    else:
                        logger.error(f"HTTP {response.status} for {url}")
                        return None

            except asyncio.TimeoutError:
                logger.warning(f"Timeout for {url}, retry {attempt + 1}")
                await asyncio.sleep(2 ** attempt)
            except aiohttp.ClientError as e:
                logger.error(f"Client error for {url}: {e}")
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.exception(f"Unexpected error for {url}: {e}")
                return None

        logger.error(f"Max retries exceeded for {url}")
        return None

    async def download_image(
        self,
        url: str,
        save_path: Path,
        filename: Optional[str] = None
    ) -> Optional[Path]:
        """
        Gorsel indir ve kaydet

        Args:
            url: Gorsel URL'i
            save_path: Kayit dizini
            filename: Dosya adi (opsiyonel, yoksa URL'den turetilir)

        Returns:
            Kaydedilen dosya yolu veya None
        """
        try:
            await self._rate_limit_wait()

            # CDN download icin temiz session kullan (Authorization olmadan)
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as download_session:
                async with download_session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"HTTP {response.status} for image download: {url}")
                        return None
                    data = await response.read()

            if not data:
                return None

            # Dosya adini belirle
            if not filename:
                # URL'den dosya adini al veya hash olustur
                url_path = url.split('?')[0]  # Query parametrelerini kaldir
                ext = Path(url_path).suffix or '.jpg'
                filename = hashlib.md5(url.encode()).hexdigest()[:12] + ext

            # Dizini olustur
            save_path.mkdir(parents=True, exist_ok=True)

            # Dosyayi kaydet
            file_path = save_path / filename
            file_path.write_bytes(data)

            logger.info(f"Downloaded: {url} -> {file_path}")
            return file_path

        except Exception as e:
            logger.exception(f"Failed to download {url}: {e}")
            return None

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Dosya adi icin guvenli karakter donusumu"""
        # Turkce karakterleri donustur
        tr_chars = {'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
                    'İ': 'I', 'Ğ': 'G', 'Ü': 'U', 'Ş': 'S', 'Ö': 'O', 'Ç': 'C'}
        for tr, en in tr_chars.items():
            name = name.replace(tr, en)

        # Ozel karakterleri kaldir
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.')
        name = ''.join(c if c in safe_chars else '_' for c in name)

        # Ardisik alt cizgileri temizle
        while '__' in name:
            name = name.replace('__', '_')

        return name.strip('_').lower()

    @abstractmethod
    async def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Ana scrape metodu - alt siniflar implement etmeli

        Returns:
            Toplanan asset'lerin listesi
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Scraper kaynak adi"""
        pass
