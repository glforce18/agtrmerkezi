# AGTR Merkezi - Kapsamli Iyilestirme Plani

## Genel Bakis

Bu plan 3 ana bolumden olusuyor:
1. **Scraper Sistemi** - Oyun gorselleri, banner, icon, animasyon
2. **Performance** - Database, cache, CDN optimizasyonlari
3. **Gorsel Tasarim** - UI/UX iyilestirmeleri, animasyonlar

Tahmini sure: 2-3 hafta (paralel calisma ile)

---

## BOLUM 1: SCRAPER SISTEMI

### 1.1 Hedefler
- CS 1.6 ve Half-Life oyun gorselleri (banner, icon, wallpaper)
- Harita gorselleri (de_dust2, de_inferno, crossfire, etc.)
- Silah ikonlari
- Takım ve turnuva logolari
- Animasyonlu efektler (Lottie/GIF)

### 1.2 Veri Kaynaklari

| Kaynak | API | Icerik |
|--------|-----|--------|
| SteamGridDB | REST API (ucretsiz) | Oyun banner, logo, icon |
| Steam Store | Web scraping | Oyun screenshot, trailer |
| GameBanana | RSS/Web | CS 1.6 mod gorselleri |
| HLTV | Web scraping | Takim logolari |
| Flaticon | API (premium) | UI ikonlari |
| LottieFiles | API | Animasyonlar |

### 1.3 Yeni Dosyalar

```
app/
├── scrapers/
│   ├── __init__.py
│   ├── base.py              # BaseScraper class
│   ├── steam_scraper.py     # Steam gorselleri
│   ├── steamgriddb.py       # SteamGridDB API
│   ├── gamebanana.py        # GameBanana modlari
│   ├── hltv_scraper.py      # HLTV takim logolari
│   └── asset_processor.py   # Gorsel optimizasyon (WebP, resize)
├── tasks/
│   └── scraper_tasks.py     # Background scraper jobs
└── api/
    └── assets.py            # Asset management API
```

### 1.4 Database Modeli

```sql
CREATE TABLE game_assets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    game_slug VARCHAR(50) NOT NULL,        -- 'cs16', 'halflife'
    asset_type ENUM('banner', 'icon', 'logo', 'screenshot', 'map', 'weapon') NOT NULL,
    name VARCHAR(100) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    thumbnail_path VARCHAR(255),
    source_url VARCHAR(500),
    width INT,
    height INT,
    file_size INT,
    is_animated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_game_type (game_slug, asset_type)
);

CREATE TABLE animation_assets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    category ENUM('loading', 'success', 'error', 'game', 'ui') NOT NULL,
    file_type ENUM('lottie', 'gif', 'webp', 'mp4') NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    preview_path VARCHAR(255),
    duration_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.5 API Endpoints

```
GET  /api/assets/games                    # Tum oyun listesi
GET  /api/assets/games/{slug}             # Oyun asset'leri
GET  /api/assets/games/{slug}/maps        # Harita gorselleri
GET  /api/assets/games/{slug}/weapons     # Silah ikonlari
GET  /api/assets/animations               # Animasyon listesi
GET  /api/assets/animations/{category}    # Kategoriye gore
POST /api/admin/assets/scrape             # Manuel scrape tetikle
POST /api/admin/assets/upload             # Manuel upload
```

### 1.6 Frontend Komponetleri

```
frontend/src/
├── components/
│   ├── assets/
│   │   ├── GameBanner.vue        # Oyun banner komponenti
│   │   ├── MapThumbnail.vue      # Harita thumbnail
│   │   ├── WeaponIcon.vue        # Silah ikonu
│   │   ├── LottiePlayer.vue      # Lottie animasyon player
│   │   └── AnimatedBadge.vue     # Animasyonlu rozet
│   └── ui/
│       ├── LoadingAnimation.vue  # Yukleme animasyonu
│       └── SuccessAnimation.vue  # Basari animasyonu
```

---

## BOLUM 2: PERFORMANCE OPTIMIZASYONLARI

### 2.1 Database Optimizasyonlari

**Mevcut Sorunlar:**
- Baglanti havuzu kucuk
- Bazi sorgular yavas
- Index eksiklikleri

**Cozumler:**

```python
# app/core/database.py - Connection Pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # 5'ten 20'ye
    max_overflow=30,        # 10'dan 30'a
    pool_pre_ping=True,     # Baglanti kontrolu
    pool_recycle=3600,      # 1 saat sonra yenile
    echo=False
)
```

**Yeni Indexler:**
```sql
-- Forum performansi
CREATE INDEX idx_topics_category_active ON forum_topics(category_id, is_active, created_at DESC);
CREATE INDEX idx_replies_topic_active ON forum_replies(topic_id, is_active, created_at);

-- Leaderboard performansi
CREATE INDEX idx_users_xp ON users(total_xp DESC);
CREATE INDEX idx_users_level ON users(level DESC, total_xp DESC);

-- Server listesi
CREATE INDEX idx_servers_game_status ON servers(game_type, status, player_count DESC);
```

### 2.2 Redis Cache Stratejisi

**Yeni Cache Katmanlari:**

| Cache Key Pattern | TTL | Aciklama |
|-------------------|-----|----------|
| `page:home` | 60s | Anasayfa HTML fragment |
| `forum:categories` | 300s | Kategori listesi |
| `forum:topic:{id}` | 60s | Tek topic |
| `forum:hot` | 120s | Populer konular |
| `leaderboard:top100` | 300s | Siralama |
| `servers:list` | 30s | Sunucu listesi |
| `user:{id}:profile` | 600s | Kullanici profili |
| `assets:games:{slug}` | 3600s | Oyun asset'leri |

### 2.3 CDN Entegrasyonu (Cloudflare)

**Adimlar:**
1. Cloudflare hesabi olustur (ucretsiz plan yeterli)
2. DNS'i Cloudflare'e yonlendir
3. Page Rules olustur:
   - `/static/*` - Cache Everything, 1 month
   - `/api/*` - Bypass Cache
   - `/uploads/*` - Cache Everything, 1 week

**Nginx Cache Headers:**
```nginx
location /static/ {
    expires 30d;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept-Encoding";
}

location /uploads/ {
    expires 7d;
    add_header Cache-Control "public";
}
```

### 2.4 Backend Monitoring

**Yeni Endpoint: /api/health/detailed**
```json
{
    "status": "healthy",
    "timestamp": "2026-01-22T21:00:00Z",
    "components": {
        "database": {"status": "ok", "latency_ms": 2},
        "redis": {"status": "ok", "latency_ms": 1},
        "disk": {"status": "ok", "free_gb": 45},
        "memory": {"status": "ok", "used_percent": 65}
    },
    "metrics": {
        "requests_per_minute": 150,
        "avg_response_time_ms": 45,
        "error_rate_percent": 0.1
    }
}
```

---

## BOLUM 3: GORSEL TASARIM IYILESTIRMELERI

### 3.1 Yeni Animasyonlar

| Sayfa | Animasyon | Tur |
|-------|-----------|-----|
| Anasayfa | Hero banner parallax | CSS |
| Forum | Skeleton loading | CSS |
| Forum | Yeni mesaj bildirimi | Lottie |
| Leaderboard | Rank degisim animasyonu | Lottie |
| Profil | Level up efekti | Lottie |
| Jackpot | Cark donusu | CSS + JS |
| Sunucular | Canli oyuncu sayisi | CSS pulse |

### 3.2 Oyun Temalı UI Elementleri

**CS 1.6 Temasi:**
- Radar tarzı mini harita (sunucu konumu)
- Silah slot UI (envanter benzeri)
- Headshot/kill feed animasyonu
- Bomb timer stili countdown

**Half-Life Temasi:**
- HUD tarzi saglik/zirh gostergesi (XP bar)
- Lambda sembolü animasyonlari
- Crosshair stili ikonlar

### 3.3 Banner ve Header Gorselleri

**Sayfa Bannerlari:**
```
/static/banners/
├── forum_header.webp         # 1920x300 forum banner
├── servers_header.webp       # 1920x300 sunucular banner
├── leaderboard_header.webp   # 1920x300 siralama banner
├── jackpot_header.webp       # 1920x300 jackpot banner
└── tournaments_header.webp   # 1920x300 turnuva banner
```

**Kategori Gorselleri:**
```
/static/forum/categories/
├── duyurular.webp
├── cs16.webp
├── halflife.webp
├── genel.webp
└── destek.webp
```

### 3.4 Lottie Animasyonlari

**Indirilecek/Olusturulacak:**
1. `loading_crosshair.json` - Nisangah yukleme
2. `success_headshot.json` - Basari (headshot efekti)
3. `error_dead.json` - Hata (olum efekti)
4. `levelup_star.json` - Level atlama
5. `coin_spin.json` - Para/puan kazanma
6. `fire_effect.json` - Populer/hot badge
7. `bomb_countdown.json` - Geri sayim

---

## UYGULAMA SIRASI

### Hafta 1: Altyapi
- [ ] Scraper base class ve Steam scraper
- [ ] Database migration (game_assets, animation_assets)
- [ ] Asset processor (WebP donusum, resize)
- [ ] Redis cache iyilestirmeleri
- [ ] Database index'leri

### Hafta 2: Scraper ve Gorseller
- [ ] SteamGridDB entegrasyonu
- [ ] GameBanana scraper
- [ ] Harita gorselleri toplama
- [ ] Silah ikonlari toplama
- [ ] Lottie animasyonlari indirme/olusturma

### Hafta 3: Frontend Entegrasyonu
- [ ] Asset komponetleri (GameBanner, MapThumbnail, etc.)
- [ ] LottiePlayer komponenti
- [ ] Sayfa banner'lari ekleme
- [ ] Animasyonlari sayfalara entegre etme
- [ ] CDN yapilandirmasi
- [ ] Final testler

---

## ONCELIKLI AKSIYONLAR (Hemen Baslayabiliriz)

1. **SteamGridDB API Key Al** - steamgriddb.com/profile/preferences/api
2. **Lottie Animasyonlari Sec** - lottiefiles.com'dan CS/gaming temalı
3. **Cloudflare Hesabi Olustur** - CDN icin
4. **Database Index'leri Ekle** - Hemen performans artisi

---

## NOTLAR

- Tum gorseller WebP formatinda saklanacak (boyut optimizasyonu)
- Thumbnail'ler otomatik olusturulacak (300x200)
- Scraper'lar rate-limited olacak (ban yememek icin)
- Asset'ler lazy-load edilecek
- Lottie animasyonlari <50KB tutulacak
