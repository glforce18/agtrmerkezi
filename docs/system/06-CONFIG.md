# Konfigürasyon Rehberi

## Ortam Değişkenleri

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agtrmerkezi
# veya MySQL
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/agtrmerkezi

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Steam OAuth
STEAM_API_KEY=your-steam-api-key
STEAM_CALLBACK_URL=https://agtrmerkezi.com/api/auth/steam/callback

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Environment
ENV=production
DEBUG=false
```

### Frontend (.env)
```bash
VITE_API_URL=/api
VITE_WS_URL=wss://agtrmerkezi.com/ws
```

---

## Nginx Konfigürasyonu

```nginx
# /etc/nginx/sites-available/agtrmerkezi

server {
    listen 80;
    server_name agtrmerkezi.com www.agtrmerkezi.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name agtrmerkezi.com www.agtrmerkezi.com;

    # SSL
    ssl_certificate /etc/letsencrypt/live/agtrmerkezi.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agtrmerkezi.com/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # Static Files
    location /static/ {
        alias /var/www/agtrmerkezi/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Frontend (SPA)
    location / {
        root /var/www/agtrmerkezi/static/dist;
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

---

## Systemd Service

```ini
# /etc/systemd/system/agtrmerkezi.service

[Unit]
Description=AGTR Merkezi FastAPI Application
After=network.target postgresql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/agtrmerkezi
Environment="PATH=/var/www/agtrmerkezi/venv/bin"
EnvironmentFile=/var/www/agtrmerkezi/.env
ExecStart=/var/www/agtrmerkezi/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Service Komutları
```bash
# Başlat
sudo systemctl start agtrmerkezi

# Durdur
sudo systemctl stop agtrmerkezi

# Yeniden başlat
sudo systemctl restart agtrmerkezi

# Durum
sudo systemctl status agtrmerkezi

# Logları izle
sudo journalctl -u agtrmerkezi -f
```

---

## PostgreSQL Konfigürasyonu

```sql
-- Veritabanı oluştur
CREATE DATABASE agtrmerkezi;

-- Kullanıcı oluştur
CREATE USER agtrmerkezi_user WITH PASSWORD 'secure_password';

-- Yetkiler
GRANT ALL PRIVILEGES ON DATABASE agtrmerkezi TO agtrmerkezi_user;

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Bağlantı Havuzu (SQLAlchemy)
```python
# app/models/connection.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

---

## Redis Konfigürasyonu

```conf
# /etc/redis/redis.conf

# Network
bind 127.0.0.1
port 6379

# Memory
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Security
requirepass your_redis_password
```

### Redis Kullanımı
```python
# Cache
await redis.setex(f"user:{user_id}", 3600, json.dumps(user_data))

# Pub/Sub
await redis.publish("jackpot:updates", json.dumps({"type": "bet"}))

# Sessions
await redis.hset(f"session:{token}", mapping=session_data)
```

---

## Uygulama Konfigürasyonu

### app/core/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AGTR Merkezi"
    APP_VERSION: str = "6.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # Steam
    STEAM_API_KEY: str = ""

    # Jackpot
    JACKPOT_HOUSE_EDGE: float = 0.05  # 5%
    JACKPOT_MIN_BET: int = 100
    JACKPOT_MAX_BET: int = 100000
    JACKPOT_ROUND_DURATION: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Dosya Yolları

```python
# Paths
BASE_DIR = Path("/var/www/agtrmerkezi")
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
AVATAR_DIR = STATIC_DIR / "avatars"
MAP_DIR = STATIC_DIR / "maps"

# URLs
STATIC_URL = "/static"
UPLOAD_URL = f"{STATIC_URL}/uploads"
```

---

## Logging Konfigürasyonu

```python
# app/core/logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/agtrmerkezi/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("agtrmerkezi")
```

---

## CORS Ayarları

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://agtrmerkezi.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Rate Limiting

```python
# app/core/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Kullanım
@app.get("/api/auth/login")
@limiter.limit("10/minute")
async def login():
    pass
```

---

## Güvenlik Kontrol Listesi

- [x] HTTPS zorunlu
- [x] JWT token süresi sınırlı
- [x] Password hashing (bcrypt)
- [x] SQL injection koruması (ORM)
- [x] XSS koruması (template escaping)
- [x] CSRF koruması (SameSite cookies)
- [x] Rate limiting aktif
- [x] Security headers (nginx)
- [x] Environment variables (.env)
- [x] Redis password korumalı

---

## Bakım Komutları

```bash
# Frontend build
cd /var/www/agtrmerkezi/frontend
npm run build

# Backend restart
sudo systemctl restart agtrmerkezi

# Log temizleme
sudo truncate -s 0 /var/log/agtrmerkezi/app.log

# Redis cache temizleme
redis-cli FLUSHDB

# Database backup
pg_dump agtrmerkezi > backup_$(date +%Y%m%d).sql

# SSL sertifika yenileme
sudo certbot renew
```
