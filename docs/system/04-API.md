# API Dokümantasyonu

## Base URL
```
https://agtrmerkezi.com/api
```

---

## Authentication

### POST /api/auth/login
Kullanıcı girişi yapar.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player@email.com",
    "role": "user",
    "level": 5,
    "xp": 1200
  }
}
```

### POST /api/auth/register
Yeni kullanıcı kaydı.

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

### POST /api/auth/steam
Steam OAuth ile giriş.

### GET /api/auth/me
Mevcut kullanıcı bilgilerini getirir.

**Headers:** `Authorization: Bearer <token>`

---

## Forum API

### GET /api/forum/categories
Tüm forum kategorilerini listeler.

**Response:**
```json
{
  "success": true,
  "categories": [
    {
      "id": 1,
      "name": "Duyurular",
      "slug": "duyurular",
      "description": "Resmi duyurular",
      "icon": "megaphone",
      "color": "#f97316",
      "topic_count": 5,
      "post_count": 23
    }
  ]
}
```

### GET /api/forum/categories/{slug}
Tek kategori detayı.

### GET /api/forum/topics
Konuları listeler.

**Query Parameters:**
| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| category_id | int | Kategori filtresi |
| sort | string | newest, popular, active |
| page | int | Sayfa numarası |
| limit | int | Sayfa başına kayıt |

### GET /api/forum/topics/{id}
Konu detayı ve yanıtları.

### POST /api/forum/topics
Yeni konu oluştur.

**Request:**
```json
{
  "category_id": 1,
  "title": "Konu Başlığı",
  "content": "Konu içeriği..."
}
```

### POST /api/forum/topics/{id}/replies
Konuya yanıt ekle.

### POST /api/forum/topics/{id}/like
Konuyu beğen.

### POST /api/forum/topics/{id}/bookmark
Konuyu kaydet.

---

## Users API

### GET /api/users/{id}
Kullanıcı profili.

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "player1",
    "avatar": "/avatars/1.jpg",
    "level": 10,
    "xp": 5000,
    "role": "vip",
    "steam_id": "STEAM_0:1:12345",
    "created_at": "2024-01-01T00:00:00Z",
    "stats": {
      "topics": 15,
      "replies": 234,
      "reputation": 456
    }
  }
}
```

### PUT /api/users/{id}
Profil güncelle.

### GET /api/users/{id}/activity
Kullanıcı aktiviteleri.

---

## Wallet API

### GET /api/wallet/balance
Cüzdan bakiyesi.

**Response:**
```json
{
  "success": true,
  "balances": {
    "coin": 1500,
    "tl": 250.00,
    "bonus": 50
  }
}
```

### GET /api/wallet/transactions
İşlem geçmişi.

### POST /api/wallet/deposit
Para yatır.

### POST /api/wallet/withdraw
Para çek.

### POST /api/wallet/transfer
Transfer yap.

---

## Games API (Jackpot)

### GET /api/games/jackpot/current
Aktif jackpot turu.

**Response:**
```json
{
  "success": true,
  "round": {
    "id": 123,
    "round_number": 456,
    "status": "active",
    "total_pot": 15000,
    "player_count": 8,
    "server_seed_hash": "abc123...",
    "time_remaining": 45
  },
  "bets": [
    {
      "user_id": 1,
      "username": "player1",
      "amount": 500,
      "win_chance": 3.33
    }
  ]
}
```

### POST /api/games/jackpot/bet
Bahis yap.

**Request:**
```json
{
  "amount": 500
}
```

### GET /api/games/jackpot/history
Geçmiş turlar.

### GET /api/games/jackpot/verify/{round_id}
Provably Fair doğrulama.

---

## Servers API

### GET /api/servers
Sunucu listesi.

**Response:**
```json
{
  "success": true,
  "servers": [
    {
      "id": 1,
      "name": "AGTR #1 Public",
      "ip": "185.x.x.x",
      "port": 27015,
      "game_type": "cs16",
      "map": "de_dust2",
      "players": 24,
      "max_players": 32,
      "status": "online"
    }
  ]
}
```

### GET /api/servers/{id}
Sunucu detayı.

### POST /api/servers/rent
Sunucu kirala.

---

## Admin API

### GET /api/admin/stats
Genel istatistikler.

### GET /api/admin/users
Kullanıcı yönetimi.

### PUT /api/admin/users/{id}
Kullanıcı düzenle.

### DELETE /api/admin/users/{id}
Kullanıcı sil.

### GET /api/admin/health/status
Sistem sağlık durumu.

**Response:**
```json
{
  "success": true,
  "overall_status": "healthy",
  "components": {
    "database": {
      "status": "healthy",
      "message": "PostgreSQL OK",
      "details": { "connection_pool": "5/20" }
    },
    "redis": {
      "status": "healthy",
      "message": "Redis OK",
      "details": { "memory": "921KB" }
    }
  }
}
```

### POST /api/admin/health/fix/{action}
Otomatik düzeltme.

**Actions:**
- `rebuild_frontend` - Frontend yeniden derle
- `flush_redis_cache` - Redis önbelleği temizle
- `create_placeholder_images` - Eksik resimleri oluştur
- `fix_permissions` - Dosya izinlerini düzelt

---

## WebSocket API

### WS /ws/jackpot
Jackpot oyunu canlı güncellemeleri.

**Events:**
```javascript
// Bağlantı
ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'join', room: 'jackpot' }))
}

// Mesajlar
{
  "type": "bet_placed",
  "data": { "user": "player1", "amount": 500 }
}

{
  "type": "round_start",
  "data": { "round_id": 123, "countdown": 60 }
}

{
  "type": "winner",
  "data": { "user": "player1", "amount": 15000, "ticket": 8234 }
}
```

### WS /ws/chat
Genel sohbet.

### WS /ws/notifications
Kullanıcı bildirimleri.

---

## Error Responses

Tüm hatalar standart formatta döner:

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Token geçersiz veya süresi dolmuş"
  }
}
```

### HTTP Status Codes
| Kod | Açıklama |
|-----|----------|
| 200 | Başarılı |
| 201 | Oluşturuldu |
| 400 | Geçersiz istek |
| 401 | Yetkisiz |
| 403 | Yasaklı |
| 404 | Bulunamadı |
| 422 | Validation hatası |
| 429 | Rate limit aşıldı |
| 500 | Sunucu hatası |

---

## Rate Limiting

| Endpoint | Limit |
|----------|-------|
| /api/auth/* | 10/dakika |
| /api/forum/* | 60/dakika |
| /api/games/* | 30/dakika |
| /api/wallet/* | 20/dakika |

---

## API Dosya Yapısı

```
app/api/
├── __init__.py
├── auth.py              # Kimlik doğrulama
├── forum.py             # Forum işlemleri
├── games.py             # Jackpot oyunu
├── servers.py           # Sunucu yönetimi
├── users.py             # Kullanıcı profilleri
├── wallet.py            # Cüzdan işlemleri
├── websocket.py         # WebSocket handler
├── notifications.py     # Bildirimler
├── leaderboard.py       # Sıralama tablosu
├── tournament.py        # Turnuvalar
├── social.py            # Sosyal özellikler
├── analytics.py         # Analitik
└── admin/
    ├── __init__.py
    ├── health.py        # Sistem sağlığı
    ├── stats.py         # İstatistikler
    ├── forum_categories.py
    ├── forum_topics.py
    └── forum_moderation.py
```
