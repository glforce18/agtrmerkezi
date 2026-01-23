# AGTR Merkezi - Claude Code Memory

## Proje Hakkinda
- **Versiyon:** 5.5.0
- **Teknoloji:** FastAPI (Python) + Vue.js 3 + MySQL + Redis
- **Domain:** agtrmerkezi.com
- **Amac:** Half-Life & CS 1.6 Gaming Community Platform
- **Durum:** 🟢 PRODUCTION - Oyuncularla paylasıldı (23 Ocak 2026)

## ⚠️ ONEMLI KURALLAR
1. **Site CANLI** - Degisiklikler gercek kullanicilari etkiler
2. **Build ZORUNLU** - Her frontend degisikligi sonrasi `cd frontend && npm run build`
3. **Test ET** - Degisiklikten once/sonra API'leri test et
4. **Cache Guncelle** - `sw.js` CACHE_VERSION'i artir
5. **Backup AL** - Buyuk degisikliklerden once veritabanı yedekle

## Onemli Dosyalar
- `app/main.py` - FastAPI ana uygulama
- `app/core/config.py` - Tum konfigurasyonlar
- `app/models/database.py` - SQLAlchemy modelleri
- `frontend/src/views/` - Vue.js sayfalari
- `.env` - Environment variables (DB_*, REDIS_*, SECRET_KEY)

## Servisler
- Backend: `systemctl restart agtrmerkezi`
- Redis: `127.0.0.1:6379`
- MySQL: `127.0.0.1:3306` (root/sedatim)

## Son Buyuk Guncellemeler

### Forum Sistemi (22 Ocak 2026) - Commit 4264de6
31 yeni ozellik eklendi:

**Backend:**
- N+1 query fix, atomic view count, Redis cache
- Full-text search, trending, advanced filters
- Tag, mention, subscription, best answer sistemleri
- XSS koruma, auto-moderation, 3-strike warning
- Badge/reputation gamification
- WebSocket real-time (typing, viewers, broadcast)

**Frontend:**
- Draft auto-save, image upload, quote reply
- Lazy load replies, read/unread indicator
- Keyboard shortcuts (R, Q, ?, Ctrl+Enter)

**Yeni API Endpoints:**
- `/api/forum/search` - Arama
- `/api/forum/trending` - Trending
- `/api/forum/tags/*` - Etiketler
- `/api/forum/mentions/*` - Mention'lar
- `/api/forum/**/subscribe` - Abonelikler
- `/api/forum/replies/*/best` - En iyi cevap
- `/api/forum/badges/*` - Rozetler
- `/api/forum/reputation/*` - Reputation
- `/api/forum/captcha/*` - CAPTCHA
- `/api/admin/moderation/*` - Admin moderation
- `/ws/forum/topic/{id}` - WebSocket

**Yeni Dosyalar:**
- `app/core/sanitizer.py`
- `app/core/content_filter.py`
- `app/services/forum_gamification.py`
- `app/api/forum_gamification.py`
- `app/api/admin/forum_moderation.py`

### Steam-Exclusive Ozellikler (22 Ocak 2026) - Commit d6d25cd
Steam hesabi baglantisi gerektiren ozellikler eklendi:

**Backend Dependency:**
- `get_current_user_with_steam` - Steam zorunlu
- `get_current_user_with_steam_optional` - Steam opsiyonel

**Korunan Ozellikler:**
| Ozellik | Endpoint | Dosya |
|---------|----------|-------|
| Forum konu olusturma | POST /api/forum/topics | forum.py |
| Forum yanit yazma | POST /api/forum/topics/*/replies | forum.py |
| Jackpot bahis | POST /api/jackpot/bet | games.py |
| Turnuva kayit | POST /api/tournaments/*/register | tournament.py |
| Klan olusturma | POST /api/clans | social.py |
| Klana katilma | POST /api/clans/*/apply | social.py |
| Sunucu ekleme | POST /api/admin/servers/add | scraper.py |

**Frontend Komponetleri:**
- `composables/useRequireSteam.js` - Steam kontrol composable
- `components/SteamRequiredModal.vue` - Steam baglama modal

**Guncellenen Sayfalar:**
- Jackpot.vue, Tournaments.vue, TournamentDetail.vue
- Forum.vue, ForumTopic.vue
- Clans.vue, ClanDetail.vue, Shop.vue

## Kod Stilleri
- Commit mesajlari: `feat:`, `fix:`, `docs:` prefix
- Python: FastAPI + Pydantic + SQLAlchemy
- Frontend: Vue 3 Composition API + Pinia
- Turkce yorumlar ve hata mesajlari

### Forum Bugfix ve Iyilestirmeler (22 Ocak 2026)
100+ bugfix ve iyilestirme yapildi:

**Avatar URL Sistemi:**
- `format_avatar_url()` helper fonksiyonu eklendi (forum.py, auth.py, user.py, leaderboard.py)
- Avatar path: `/static/images/avatars/...` formatinda
- Tum API response'larda avatar URL'leri duzgun donuyor

**Topic API Duzeltmeleri:**
- `GET /api/forum/topics/{id}` response formati: `{topic: {...}, replies: [...], bestAnswer: null}`
- Frontend beklentilerine uygun hale getirildi

**Veritabani Duzeltmeleri:**
- `forum_replies.is_best_answer` sutunu eklendi
- Database indexes optimize edildi

**Forum Dosyalari:**
| Dosya | Aciklama |
|-------|----------|
| `frontend/src/views/Forum.vue` | Ana forum sayfasi |
| `frontend/src/views/ForumCategory.vue` | Kategori sayfasi |
| `frontend/src/views/ForumTopic.vue` | Konu detay sayfasi |
| `frontend/src/components/forum/` | Forum componentleri |
| `frontend/src/assets/styles/forum.css` | Forum stilleri |
| `app/api/forum.py` | Forum API endpoints |

### Forum 100+ Iyilestirme (22 Ocak 2026)
4 paralel agent ile 100+ forum iyilestirmesi yapildi:

**CSS/UI Iyilestirmeleri (25 adet):**
- Skeleton loading animasyonlari
- Hover efektleri ve mikro animasyonlar
- Topic card tasarimi ve badges
- Author info ve gamification UI
- Responsive tasarim iyilestirmeleri
- Focus states ve accessibility
- Dark theme optimizasyonlari

**Backend API Iyilestirmeleri (25 adet):**
- Query optimizasyonlari
- Pagination ve caching
- Rate limiting ve security
- Error handling standartlari
- Response format tutarliligi
- Validation katmanlari
- Avatar URL sistemi

**Vue Component Iyilestirmeleri (25 adet):**
- Loading states tum componentlerde
- Error handling ve retry mekanizmalari
- ARIA labels ve accessibility
- Reactive state management
- Watch ve computed optimizasyonlari
- Memory leak onlemleri
- Event cleanup

**Fonksiyonellik Iyilestirmeleri (25 adet):**
- Like/unlike toggle
- Bookmark sistemi
- Share functionality
- Edit/delete islemleri
- Keyboard shortcuts (R, Q, ?, Ctrl+Enter)
- Real-time updates
- Draft auto-save

### Forum Navigation Bugfix (22 Ocak 2026)
Forum sayfalarinda navigation sorunlari cozuldu:

**Sorunlar:**
- Topic linklerine tiklandiginda sayfa yuklenmiyordu
- Geri/ileri navigasyonda bos sayfa geliyordu
- Service Worker eski JS dosyalarini cache'liyordu

**Cozumler:**
1. **App.vue Transition Kaldirildi:**
   - `<transition name="page-slide">` sayfa gecislerinde takılmaya neden oluyordu
   - Simdi sadece `:key="route.fullPath"` ile component remount yapiliyor

2. **ForumTopic.vue Watch Kaldirildi:**
   - `:key` zaten remount yapiyor, watch gereksizdi ve cakisma olusturuyordu

3. **Service Worker Guncellendi (v4):**
   - Forum topic'leri NEVER_CACHE_PATTERNS'e eklendi
   - `/api/forum/categories/*/topics` ve `/api/forum/topics/*` asla cache'lenmiyor

4. **SQLAlchemy Row Handling:**
   - `forum.py`'da Row objeleri duzgun handle ediliyor
   - `hasattr(row, 'ForumTopic')` kontrolu eklendi

5. **Cift Navigation Duzeltildi:**
   - ForumTopicCard zaten `router.push` yapiyor
   - ForumCategory'deki gereksiz `@click` kaldirildi

6. **Emoji Encoding Duzeltildi:**
   - Veritabani `utf8mb4` charset ile guncellendi
   - Kategori ikonlari ve topic basliklari duzgun gosteriliyor

**Author Object Handling:**
- API'den gelen `author` objesi duzgun parse ediliyor
- `formatPostForCard()` ve `formatReplyForCard()` fonksiyonlari guncellendi

### Game Assets Scraper System (22 Ocak 2026)
Oyun gorselleri, banner, logo, harita resimleri ve animasyonlar icin scraper sistemi:

**Backend Dosyalari:**
- `app/scrapers/__init__.py` - Module exports
- `app/scrapers/base.py` - BaseScraper (rate limit, retry, download)
- `app/scrapers/steamgriddb.py` - SteamGridDB API (banner, logo, icon, hero)
- `app/scrapers/gamebanana.py` - GameBanana (harita, skin gorselleri)
- `app/scrapers/asset_processor.py` - Gorsel isleme (WebP, thumbnail)
- `app/api/game_assets.py` - REST API endpoints

**Database Tablolari:**
- `game_assets` - Oyun gorselleri
- `animation_assets` - Lottie/GIF animasyonlar
- `map_assets` - Harita gorselleri

**API Endpoints:**
| Endpoint | Aciklama |
|----------|----------|
| GET `/api/game-assets/games` | Desteklenen oyun listesi |
| GET `/api/game-assets/games/{slug}` | Oyuna ait asset'ler |
| GET `/api/game-assets/games/{slug}/banner` | Oyun banner'i |
| GET `/api/game-assets/games/{slug}/maps` | Harita gorselleri |
| GET `/api/game-assets/animations` | Animasyon listesi |
| GET `/api/game-assets/animations/{slug}` | Tek animasyon |
| POST `/api/game-assets/admin/scrape/steamgriddb` | SteamGridDB scraper (Admin) |
| POST `/api/game-assets/admin/scrape/gamebanana` | GameBanana scraper (Admin) |
| GET `/api/game-assets/admin/stats` | Asset istatistikleri (Admin) |

**Frontend Dosyalari:**
- `composables/useGameAssets.js` - API composable
- `components/games/GameBanner.vue` - Oyun banner komponenti
- `components/games/GameCard.vue` - Oyun karti komponenti
- `components/games/MapGrid.vue` - Harita grid komponenti

**Desteklenen Oyunlar:**
| Slug | Oyun | Steam ID |
|------|------|----------|
| cs16 | Counter-Strike 1.6 | 10 |
| halflife | Half-Life | 70 |
| css | Counter-Strike: Source | 240 |
| csgo | CS:GO | 730 |
| tf2 | Team Fortress 2 | 440 |
| sven | Sven Co-op | 225840 |

**Konfigurasyon:**
`.env` dosyasina `STEAMGRIDDB_API_KEY` eklenmeli (https://www.steamgriddb.com/profile/preferences/api)

**Asset Dizini:**
`/var/www/agtrmerkezi/static/assets/games/{oyun}/{asset_type}/`

### Production Release (23 Ocak 2026)
Site oyuncularla paylasildi. Asagidaki sistemler aktif:

**Armor (Coin) Odul Sistemi:**
| Aktivite | Armor | Reputation |
|----------|-------|------------|
| Konu Acma | 10 | +5 |
| Ilk Konu Bonusu | +50 | - |
| Yanit Yazma | 5 | +2 |
| Ilk Yanit Bonusu | +25 | - |
| En Iyi Cevap | 25 | - |
| Begeni Alma | 1 | +1 |

**Gunluk Limitler:** 10 konu, 50 yanit, 20 begeni odulu

**Level Sistemi:**
- Formula: `Level = 1 + (Reputation / 50)`
- Max Level: 99
- `calculate_level_from_reputation()` fonksiyonu: `forum.py:145`

**Forum UX Ozellikleri:**
- Yukari Cik butonu (sag alt, scroll sonrasi gorunur)
- Sticky arama/aksiyon bar
- Klavye kisayollari: `T` = yukari, `/` = arama
- Back-to-top: Forum.vue, ForumCategory.vue

**Aktif Servisler:**
- Forum: ✅ Kategoriler, konular, yanitlar
- Jackpot: ✅ Armor ile bahis
- Turnuvalar: ✅ Kayit sistemi
- Klanlar: ✅ Olusturma/katilma
- Badges: ✅ 9 rozet tanimli
- Leaderboard: ✅ Reputation/ELO siralaması

**Onemli Dosyalar (Gamification):**
- `app/services/forum_rewards.py` - Armor odul sistemi
- `app/services/forum_gamification.py` - Badge/reputation servisi
- `app/api/forum.py:145` - Level hesaplama

### Comprehensive Security & Bug Fixes (23 Ocak 2026)
72 bug taramasi yapildi, 29 bug duzeltildi (7 CRITICAL, 14 HIGH, 8 MEDIUM):

**CRITICAL Security Fixes (7 adet):**
| Bug | Dosya | Cozum |
|-----|-------|-------|
| XSS v-html | Footer.vue:50 | DOMPurify.sanitize() eklendi |
| XSS v-html | ForumBestAnswer.vue:39,137 | DOMPurify + sanitized computed |
| XSS v-html | ForumPostCard.vue:133 | sanitizedHtmlContent computed |
| XSS v-html | TournamentDetail.vue:231,333 | sanitizedDescription/Rules |
| Race Condition | payments.py:236,497,536,717 | with_for_update() coupon lock |
| Race Condition | payments.py:354 | BankTransfer row-level lock |
| Race Condition | jackpot.py:270-276 | JackpotHistory lock |

**HIGH Priority Fixes (14 adet):**
| Bug | Dosya | Cozum |
|-----|-------|-------|
| Payment locks (5 endpoint) | payments.py:189,400,442,453,524 | with_for_update() |
| Wallet atomic | jackpot.py:104-172 | begin_nested() savepoint |
| Memory leak | Jackpot.vue:898-935 | cancelAnimationFrame cleanup |
| Unhandled promises | Jackpot.vue:709,779,1016,1019 | .catch() handlers |
| WebSocket race | Jackpot.vue:722-765 | isMounted/isUnmounting checks |
| AudioContext leak | Jackpot.vue:1075-1079 | state check before close |
| ELO update lock | leaderboard.py:309-318 | with_for_update() |
| Tier index error | leaderboard.py:199-201 | Bounds check + comments |
| Webhook session pool | webhooks.py:50-105 | Shared aiohttp session |
| Webhook error tracking | webhooks.py:107-135 | error_count + last_error |

**MEDIUM Priority Fixes (8 adet):**
| Bug | Dosya | Cozum |
|-----|-------|-------|
| Forum page limit | forum.py:601 | le=1000 -> le=100 |
| Content length | forum.py:1945-1955 | Post-sanitization validation |
| Hasattr checks | forum.py:1794,2144 | Safe attribute access |
| Coupon errors | payments.py:213-220 | Proper HTTPException messages |
| Admin query errors | admin/_main.py:427 | try-catch wrapper |
| Invoice error | payments.py:338 | invoice_error field tracking |
| URL validation | social.py:46-62 | validate_url() helper |
| Upload errors | api.js:182-189 | .catch() handler |

**Yeni Guvenlik Fonksiyonlari:**
- `validate_url()` - URL validation helper (social.py:33-38)
- `get_session()` - Shared aiohttp session pool (webhooks.py:15-35)
- `close_session()` - Session cleanup on shutdown (webhooks.py:28-35)

**DOMPurify Kullanimi:**
```javascript
// Frontend XSS koruma
import DOMPurify from 'dompurify'
const sanitizedContent = computed(() => DOMPurify.sanitize(content.value))
```

**SQLAlchemy Lock Pattern:**
```python
# Race condition koruma
entity = db.query(Entity).filter(Entity.id == id).with_for_update().first()
entity.field = new_value
db.commit()
```

**Database Model Sync (23 Ocak 2026):**
Database kolonlari ile model senkronize edildi (`app/models/database.py`):
- ForumTopic: `likes`, `is_sticky`, `is_solved`, `last_reply_id`, `last_reply_at`
- ForumReply: `likes`, `parent_reply_id` (nested replies)

**CSRF Exempt APIs (23 Ocak 2026):**
JWT ile korunan API'ler CSRF'den exempt edildi (`app/middleware/csrf.py`):
- `/api/forum` - Forum islemleri (like, reply, vb.)
- `/api/jackpot` - Jackpot bahis
- `/api/tournaments` - Turnuva kayit
- `/api/clans` - Klan islemleri
- `/api/leaderboard` - Leaderboard guncellemeleri
- `/api/errors` - Hata raporlama

### Forum Kategori Organizasyonu (23 Ocak 2026)
Kategoriler oyunlara gore gruplandirildi:

**Database:**
- `forum_categories.game_slug` kolonu eklendi
- CS 1.6 kategorileri: `game_slug='cs16'`
- Half-Life kategorileri: `game_slug='halflife'`

**API Guncellemesi:**
- `/api/forum/categories` artik `game_slug` ve `parent_id` donuyor
- Frontend bu degerleri kullanarak kategorileri grupluyor

## Notlar
- Pre-commit hooks python3.11 ariyor, `--no-verify` kullanilabilir
- Frontend build: `cd frontend && npm run build`
- Migration dosyalari: `migrations/` klasoru
- Avatar dosyalari: `/var/www/agtrmerkezi/static/images/avatars/`
- nginx uploads: `/var/www/agtrmerkezi/static/uploads` (alias /uploads)
- Service Worker versiyonu: v19 (`frontend/public/sw.js`)
- Game assets dizini: `/var/www/agtrmerkezi/static/assets/games/`

## Hizli Komutlar
```bash
# Build & Restart
cd /var/www/agtrmerkezi/frontend && npm run build && sudo systemctl restart agtrmerkezi

# Cache Temizle (versiyon artir)
sed -i "s/const CACHE_VERSION = [0-9]*/const CACHE_VERSION = 20/" frontend/public/sw.js

# Servis Durumu
sudo systemctl status agtrmerkezi

# Log Izle
journalctl -u agtrmerkezi -f

# Veritabani Yedekle
mysqldump -u root -psedatim agtrmerkezi > backup_$(date +%Y%m%d).sql
```
