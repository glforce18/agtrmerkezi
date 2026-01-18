"""
AGTR Merkezi v5.2 - Rate Limiting Middleware
IP bazli istek limiti, DDoS korumasi
Redis backend desteği (fallback: in-memory)
"""

import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# Redis bağlantısı (opsiyonel)
try:
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info("Rate limiter using Redis backend")
except Exception as e:
    redis_client = None
    REDIS_AVAILABLE = False
    logger.info(f"Rate limiter using in-memory backend (Redis unavailable: {e})")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IP bazli rate limiting middleware - Redis veya Memory"""

    # Memory cleanup limits (max items to prevent unbounded growth)
    MAX_TRACKED_IPS = 10000
    CLEANUP_THRESHOLD = 8000  # Cleanup when reaching this many IPs

    def __init__(self, app, requests_per_minute: int = 300, requests_per_second: int = 50):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_second
        # In-memory fallback with size limits
        self.minute_requests = defaultdict(list)  # IP -> [timestamps]
        self.second_requests = defaultdict(list)
        self.blocked_ips = {}  # IP -> unblock_time
        self.whitelist = {"127.0.0.1", "localhost"}
        self._lock = asyncio.Lock()
        self._last_cleanup = time.time()
        
    def get_client_ip(self, request: Request) -> str:
        """Gercek IP adresini al (proxy arkasinda bile)"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"
    
    async def cleanup_old_requests(self, ip: str):
        """Eski request kayitlarini temizle (sadece memory backend)"""
        if REDIS_AVAILABLE:
            return  # Redis TTL ile otomatik temizler

        now = time.time()

        # 1 dakikadan eski kayitlari sil
        self.minute_requests[ip] = [
            ts for ts in self.minute_requests[ip]
            if now - ts < 60
        ]

        # 1 saniyeden eski kayitlari sil
        self.second_requests[ip] = [
            ts for ts in self.second_requests[ip]
            if now - ts < 1
        ]

        # Tamamen boş IP'leri sil
        if not self.minute_requests[ip]:
            self.minute_requests.pop(ip, None)
        if not self.second_requests[ip]:
            self.second_requests.pop(ip, None)

    async def aggressive_cleanup(self):
        """Aggressive cleanup to prevent memory leak"""
        if REDIS_AVAILABLE:
            return

        now = time.time()

        # Her 60 saniyede bir agresif temizlik yap
        if now - self._last_cleanup < 60:
            return

        self._last_cleanup = now

        # Eski blocked IP'leri temizle
        self.blocked_ips = {
            ip: unblock_time
            for ip, unblock_time in self.blocked_ips.items()
            if unblock_time > now
        }

        # Eğer IP sayısı limite yaklaştıysa, en eski IP'leri temizle
        total_ips = len(self.minute_requests)
        if total_ips > self.CLEANUP_THRESHOLD:
            # En eski IP'leri bul ve temizle
            ips_to_remove = []
            for ip, timestamps in list(self.minute_requests.items()):
                if not timestamps or (now - max(timestamps)) > 120:  # 2 dakikadan eski
                    ips_to_remove.append(ip)

            for ip in ips_to_remove:
                self.minute_requests.pop(ip, None)
                self.second_requests.pop(ip, None)

            logger.info(f"Aggressive cleanup: removed {len(ips_to_remove)} inactive IPs, remaining: {len(self.minute_requests)}")

        # Eğer hala çok fazla IP varsa, en eski %20'sini temizle
        if len(self.minute_requests) > self.MAX_TRACKED_IPS:
            ips_with_last_access = [
                (ip, max(timestamps) if timestamps else 0)
                for ip, timestamps in self.minute_requests.items()
            ]
            ips_with_last_access.sort(key=lambda x: x[1])  # En eski önce

            remove_count = len(ips_with_last_access) // 5  # %20'sini temizle
            for ip, _ in ips_with_last_access[:remove_count]:
                self.minute_requests.pop(ip, None)
                self.second_requests.pop(ip, None)

            logger.warning(f"Emergency cleanup: removed {remove_count} oldest IPs to prevent memory overflow")
    
    async def is_rate_limited_redis(self, ip: str) -> tuple:
        """Redis ile rate limit kontrolu"""
        now = time.time()
        pipe = redis_client.pipeline()
        
        # Keys
        second_key = f"ratelimit:sec:{ip}"
        minute_key = f"ratelimit:min:{ip}"
        block_key = f"ratelimit:block:{ip}"
        
        # Blocked kontrolu
        block_ttl = redis_client.ttl(block_key)
        if block_ttl > 0:
            return True, f"IP blocked for {block_ttl} seconds"
        
        # Mevcut sayilari al
        second_count = redis_client.llen(second_key)
        minute_count = redis_client.llen(minute_key)
        
        # Saniye kontrolu
        if second_count >= self.requests_per_second:
            return True, "Too many requests per second"
        
        # Dakika kontrolu
        if minute_count >= self.requests_per_minute:
            redis_client.setex(block_key, 60, "blocked")
            logger.warning(f"IP blocked for rate limiting (Redis): {ip}")
            return True, "Rate limit exceeded, blocked for 1 minute"
        
        # Request kaydet
        pipe.lpush(second_key, now)
        pipe.expire(second_key, 2)  # 2 saniye TTL
        pipe.lpush(minute_key, now)
        pipe.expire(minute_key, 61)  # 61 saniye TTL
        pipe.execute()
        
        return False, None
    
    async def is_rate_limited(self, ip: str) -> tuple:
        """Rate limit kontrolu - (limited, reason)"""
        # Redis varsa Redis kullan
        if REDIS_AVAILABLE:
            return await self.is_rate_limited_redis(ip)
        
        # Memory backend
        now = time.time()
        
        # Blocked IP kontrolu
        if ip in self.blocked_ips:
            if now < self.blocked_ips[ip]:
                remaining = int(self.blocked_ips[ip] - now)
                return True, f"IP blocked for {remaining} seconds"
            else:
                del self.blocked_ips[ip]
        
        await self.cleanup_old_requests(ip)
        
        # Saniye bazli kontrol
        if len(self.second_requests[ip]) >= self.requests_per_second:
            return True, "Too many requests per second"
        
        # Dakika bazli kontrol
        if len(self.minute_requests[ip]) >= self.requests_per_minute:
            # Cok fazla istek - IP'yi gecici engelle
            self.blocked_ips[ip] = now + 60  # 1 dakika block
            logger.warning(f"IP blocked for rate limiting: {ip}")
            return True, "Rate limit exceeded, blocked for 1 minute"
        
        return False, None
    
    async def dispatch(self, request: Request, call_next):
        ip = self.get_client_ip(request)

        # Whitelist kontrolu
        if ip in self.whitelist:
            return await call_next(request)

        # Static dosyalar icin limit yok
        if request.url.path.startswith(("/static/", "/favicon")):
            return await call_next(request)

        # WebSocket, health check ve bazi API'ler icin limit yok
        if request.url.path.startswith(("/ws", "/api/health", "/api/ws")):
            return await call_next(request)

        # Admin paneli ve media upload icin limit yok (zaten auth middleware koruyor)
        if request.url.path.startswith(("/api/admin", "/api/media", "/api/smart-media", "/admin")):
            return await call_next(request)

        # Periodic aggressive cleanup (memory leak prevention)
        await self.aggressive_cleanup()

        async with self._lock:
            limited, reason = await self.is_rate_limited(ip)
            
            if limited:
                logger.warning(f"Rate limited: {ip} - {reason}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests",
                        "reason": reason,
                        "retry_after": 60
                    },
                    headers={"Retry-After": "60"}
                )
            
            # Request kaydet
            now = time.time()
            self.minute_requests[ip].append(now)
            self.second_requests[ip].append(now)
        
        # Request'i isle
        response = await call_next(request)
        
        # Rate limit header'lari ekle
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.minute_requests[ip])
        )
        
        return response


class BruteForceProtection:
    """Login brute force korumasi"""
    
    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 15):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        self.attempts = defaultdict(list)  # IP -> [timestamps]
        self.locked = {}  # IP -> unlock_time
    
    def record_attempt(self, ip: str, success: bool):
        """Login denemesi kaydet"""
        now = datetime.utcnow()
        
        if success:
            # Basarili giris - kayitlari temizle
            self.attempts[ip] = []
            if ip in self.locked:
                del self.locked[ip]
            return
        
        # Basarisiz deneme kaydet
        self.attempts[ip].append(now)
        
        # Eski denemeleri temizle (15 dk oncesi)
        cutoff = now - timedelta(minutes=self.lockout_minutes)
        self.attempts[ip] = [t for t in self.attempts[ip] if t > cutoff]
        
        # Limit asildiysa kilitle
        if len(self.attempts[ip]) >= self.max_attempts:
            self.locked[ip] = now + timedelta(minutes=self.lockout_minutes)
            logger.warning(f"IP locked for brute force: {ip}")
    
    def is_locked(self, ip: str) -> tuple:
        """IP kilitli mi - (locked, remaining_seconds)"""
        if ip not in self.locked:
            return False, 0
        
        now = datetime.utcnow()
        if now >= self.locked[ip]:
            del self.locked[ip]
            self.attempts[ip] = []
            return False, 0
        
        remaining = (self.locked[ip] - now).seconds
        return True, remaining


# Global instance
brute_force_protection = BruteForceProtection()
