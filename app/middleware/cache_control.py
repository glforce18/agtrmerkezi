"""
AGTR Merkezi - Cache Control Middleware
Static dosyalar icin cache headers, ETag ve performans optimizasyonu
"""

import hashlib
import os
import time
from pathlib import Path
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Static dosyalar icin cache header'lari ve ETag destegi ekle"""

    def __init__(self, app):
        super().__init__(app)

        # Uygulama baslangic zamani (ETag icin fallback)
        self._app_start_time = str(int(time.time()))

        # ETag cache (dosya yolu -> etag)
        self._etag_cache = {}

        # Cache sureler (saniye)
        self.cache_rules = {
            # Uzun sureli cache (1 yil) - hash'li dosyalar
            'immutable': {
                'extensions': ['.woff2', '.woff', '.ttf', '.eot'],
                'max_age': 31536000,  # 1 yil
                'immutable': True
            },
            # Orta sureli cache (1 hafta) - gorseller ve CSS/JS
            'long': {
                'extensions': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico',
                             '.css', '.js'],
                'max_age': 604800,  # 1 hafta
                'immutable': False
            },
            # Kisa sureli cache (1 saat) - HTML ve digerleri
            'short': {
                'extensions': ['.html', '.json', '.xml'],
                'max_age': 3600,  # 1 saat
                'immutable': False
            }
        }

    def _generate_etag(self, file_path: str) -> Optional[str]:
        """Dosya icin ETag olustur (mtime + size hash)"""
        try:
            # Cache'de varsa dondur
            if file_path in self._etag_cache:
                cached_etag, cached_mtime = self._etag_cache[file_path]
                current_mtime = os.path.getmtime(file_path)
                if current_mtime == cached_mtime:
                    return cached_etag

            # Dosya bilgilerini al
            stat = os.stat(file_path)
            mtime = stat.st_mtime
            size = stat.st_size

            # ETag olustur (weak etag format)
            etag_content = f"{mtime}-{size}"
            etag = f'W/"{hashlib.md5(etag_content.encode()).hexdigest()[:16]}"'

            # Cache'e kaydet
            self._etag_cache[file_path] = (etag, mtime)

            return etag
        except (OSError, IOError):
            return None

    def _check_if_none_match(self, request: Request, etag: str) -> bool:
        """If-None-Match header kontrolu"""
        if_none_match = request.headers.get("if-none-match")
        if if_none_match:
            # Birden fazla ETag olabilir
            client_etags = [e.strip() for e in if_none_match.split(",")]
            return etag in client_etags or "*" in client_etags
        return False

    def get_cache_rule(self, path: str) -> dict:
        """Dosya için cache kuralını belirle"""
        ext = Path(path).suffix.lower()

        for rule_name, rule in self.cache_rules.items():
            if ext in rule['extensions']:
                return rule

        return None

    async def dispatch(self, request: Request, call_next):
        # Static dosyalar icin ETag kontrolu
        if request.url.path.startswith('/static/') or request.url.path.startswith('/uploads/'):
            # Dosya yolunu belirle
            if request.url.path.startswith('/static/'):
                file_path = f"static{request.url.path[7:]}"  # /static/ kısmını kaldır
            else:
                file_path = f"uploads{request.url.path[8:]}"  # /uploads/ kısmını kaldır

            # ETag olustur
            etag = self._generate_etag(file_path)

            # If-None-Match kontrolu - 304 Not Modified dondur
            if etag and self._check_if_none_match(request, etag):
                return Response(
                    status_code=304,
                    headers={
                        "ETag": etag,
                        "Cache-Control": "public, max-age=604800",
                        "Vary": "Accept-Encoding"
                    }
                )

        response = await call_next(request)

        # Static dosyalar icin cache headers ve ETag ekle
        if request.url.path.startswith('/static/') or request.url.path.startswith('/uploads/'):
            rule = self.get_cache_rule(request.url.path)

            if rule:
                cache_directives = [
                    "public",
                    f"max-age={rule['max_age']}"
                ]

                if rule.get('immutable'):
                    cache_directives.append('immutable')

                response.headers['Cache-Control'] = ', '.join(cache_directives)

                # ETag ekle
                if request.url.path.startswith('/static/'):
                    file_path = f"static{request.url.path[7:]}"
                else:
                    file_path = f"uploads{request.url.path[8:]}"

                etag = self._generate_etag(file_path)
                if etag:
                    response.headers['ETag'] = etag

                response.headers['Vary'] = 'Accept-Encoding'

        # API responses - no cache
        elif request.url.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

        return response
