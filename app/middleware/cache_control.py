"""
AGTR Merkezi - Cache Control Middleware
Static dosyalar için cache headers ve performans optimizasyonu
"""

from pathlib import Path

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Static dosyalar için cache header'ları ekle"""

    def __init__(self, app):
        super().__init__(app)

        # Cache süreler (saniye)
        self.cache_rules = {
            # Uzun süreli cache (1 yıl) - hash'li dosyalar
            'immutable': {
                'extensions': ['.woff2', '.woff', '.ttf', '.eot'],
                'max_age': 31536000,  # 1 yıl
                'immutable': True
            },
            # Orta süreli cache (1 hafta) - görsellerve CSS/JS
            'long': {
                'extensions': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico',
                             '.css', '.js'],
                'max_age': 604800,  # 1 hafta
                'immutable': False
            },
            # Kısa süreli cache (1 saat) - HTML ve diğerleri
            'short': {
                'extensions': ['.html', '.json', '.xml'],
                'max_age': 3600,  # 1 saat
                'immutable': False
            }
        }

    def get_cache_rule(self, path: str) -> dict:
        """Dosya için cache kuralını belirle"""
        ext = Path(path).suffix.lower()

        for rule_name, rule in self.cache_rules.items():
            if ext in rule['extensions']:
                return rule

        return None

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Sadece static dosyalar için cache headers ekle
        if request.url.path.startswith('/static/'):
            rule = self.get_cache_rule(request.url.path)

            if rule:
                cache_directives = [
                    f"public",
                    f"max-age={rule['max_age']}"
                ]

                if rule.get('immutable'):
                    cache_directives.append('immutable')

                response.headers['Cache-Control'] = ', '.join(cache_directives)

                # ETag için Last-Modified ekle (daha iyi caching)
                # Gerçek dosya modifikasyon zamanı yerine uygulama başlangıcı
                response.headers['Vary'] = 'Accept-Encoding'

        # API responses - no cache
        elif request.url.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

        return response
