# AGTR Merkezi - Claude Code Memory

## Proje Hakkinda
- **Versiyon:** 5.1.0
- **Teknoloji:** FastAPI (Python) + Vue.js 3 + MySQL + Redis
- **Domain:** agtrmerkezi.com
- **Amac:** Half-Life & CS 1.6 Gaming Community Platform

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

## Notlar
- Pre-commit hooks python3.11 arıyor, `--no-verify` kullanılabilir
- Frontend build: `cd frontend && npm run build`
- Migration dosyaları: `migrations/` klasoru
