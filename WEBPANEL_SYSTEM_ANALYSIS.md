# 📊 AGTR Merkezi WebPanel Sistemi - Kapsamlı Teknik Analiz

**Oluşturulma Tarihi:** 30 Ocak 2026
**Versiyon:** v1.0
**Amaç:** Sistem dokümantasyonu ve geliştirici referansı

---

## 🎯 Sistem Genel Bakış

AGTR Merkezi WebPanel, Half-Life 1 (GoldSrc) oyun sunucularını web üzerinden yönetmek için geliştirilmiş tam özellikli bir yönetim panelidir. Sistem, **dual authentication** (Steam OAuth + Panel Password) desteği ile hem sunucu sahiplerine hem de yetkili kullanıcılara erişim sağlar.

### Ana Özellikler
- 🔐 **Dual Authentication:** Steam OAuth ve Panel Password (cPanel tarzı)
- 🖥️ **RCON Console:** Gerçek zamanlı komut çalıştırma (screen-based)
- 💬 **Live Chat:** Canlı oyuncu sohbeti izleme (monster log parsing)
- 📊 **Dashboard:** Sunucu durumu, oyuncu sayısı, harita bilgisi
- ⚙️ **Server Control:** Başlatma, durdurma, yeniden başlatma
- 🗺️ **Map Management:** Harita değiştirme ve yönetimi

---

## 🏗️ Mimari Yapı

```
┌─────────────────────────────────────────────────────────────────┐
│                   AGTR Merkezi WebPanel Sistemi                  │
│                                                                   │
│  ┌─────────────────┐           ┌──────────────────────────┐     │
│  │   Frontend SPA  │◄─────────►│    Backend API           │     │
│  │    (Vue 3)      │           │    (FastAPI/Python)      │     │
│  │                 │   REST    │                          │     │
│  │  - Router       │   API     │  - RCON Service          │     │
│  │  - Pinia Store  │           │  - Auth Middleware       │     │
│  │  - Axios Client │           │  - Rate Limiter          │     │
│  └─────────────────┘           └──────────────────────────┘     │
│         │                                 │                      │
│         │                                 ▼                      │
│         │                      ┌───────────────────┐             │
│         │                      │   PostgreSQL DB   │             │
│         │                      │                   │             │
│         │                      │  - game_servers   │             │
│         │                      │  - users          │             │
│         │                      │  - console_hist   │             │
│         │                      └───────────────────┘             │
│         │                                 │                      │
│         │                                 ▼                      │
│         │                      ┌───────────────────────────┐     │
│         └─────────────────────►│  HLDS Game Servers       │     │
│                                │  (Screen Sessions)       │     │
│                                │                          │     │
│                                │  /home/gameservers/      │     │
│                                │  servers/server_X/       │     │
│                                └───────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Dual Authentication Sistemi

### 1. Steam OAuth (Ana Site Entegrasyonu)

**Kullanım:** Sunucu sahiplerinin Steam hesabı ile giriş yapması

**Token Yapısı:**
```javascript
{
  "sub": 12345,           // user_id
  "type": "user",         // Token tipi
  "exp": 1738281600       // Expiration timestamp
}
```

**Storage:**
- `localStorage.auth_token` → JWT token
- `localStorage.user` → Kullanıcı bilgileri

**Authentication Flow:**
```
1. User → Steam OAuth Login (/login)
2. Steam → Callback (/api/auth/steam/callback)
3. Backend → User kaydı/güncelleme
4. Backend → JWT token oluştur
5. Frontend → localStorage'e kaydet
6. Redirect → Dashboard
```

---

### 2. Panel Password (Public Erişim - cPanel Tarzı)

**Kullanım:** IP:PORT + şifre ile direkt panel erişimi

**Token Yapısı:**
```javascript
{
  "sub": "panel_7",       // panel_{server_id}
  "server_id": 7,         // Authorized server ID
  "type": "panel",        // Token tipi
  "exp": 1738368000       // 24 saat geçerli
}
```

**Storage:**
- `localStorage.panel_token` → JWT token
- `localStorage.panel_server_id` → Server ID
- `localStorage.panel_mode` → "true"

**Authentication Flow:**
```
1. User → panel.agtrmerkezi.com/panel
2. Dropdown → Server listesi (GET /api/panel/servers)
3. User → Server ID + Panel Password
4. POST /api/panel/auth
5. Backend → Şifre doğrulama (GameServer.panel_password)
6. Backend → Panel JWT token oluştur (24h expiry)
7. Frontend → localStorage'e kaydet
8. Redirect → /servers/{id}/panel
```

**Backend Validation:**
```python
async def get_current_user_or_panel() -> tuple[User | None, int | None]:
    # 1. Panel token var mı?
    panel_server_id = await get_panel_server_id(request, credentials)
    if panel_server_id:
        return (None, panel_server_id)  # Panel auth

    # 2. Steam token var mı?
    user = await get_current_user(request, credentials, db)
    return (user, None)  # Steam auth
```

---

## 📂 Dosya Yapısı

### Backend Structure
```
/var/www/agtrmerkezi/
├── app/
│   ├── api/
│   │   ├── servers_unified.py      # Ana server API
│   │   │   ├── POST /servers/{id}/rcon             # RCON komut çalıştırma
│   │   │   ├── GET /servers/{id}/live-chat         # Canlı chat polling
│   │   │   ├── GET /servers/{id}/webpanel/info     # Server bilgileri
│   │   │   ├── GET /servers/{id}/webpanel/status   # Anlık durum
│   │   │   └── POST /servers/{id}/restart          # Restart
│   │   │
│   │   └── panel_auth.py           # Panel authentication
│   │       ├── POST /api/panel/auth                # Panel login
│   │       └── GET /api/panel/servers              # Server dropdown
│   │
│   ├── core/
│   │   └── security.py             # JWT, authentication, helpers
│   │       ├── create_access_token()
│   │       ├── decode_token()
│   │       ├── get_current_user()
│   │       ├── get_panel_server_id()
│   │       └── get_current_user_or_panel()
│   │
│   ├── services/
│   │   └── rcon_service.py         # RCON execution service
│   │       ├── class RCONService
│   │       │   ├── validate_command()           # Komut güvenlik kontrolü
│   │       │   ├── execute()                    # Screen-based RCON
│   │       │   └── _log_command()               # Database logging
│   │       └── BLOCKED_COMMANDS                 # Yasaklı komutlar listesi
│   │
│   ├── middleware/
│   │   └── rate_limit.py           # Rate limiting middleware
│   │       ├── RateLimitMiddleware (300 req/min, 50 req/sec)
│   │       ├── BruteForceProtection
│   │       └── Exempt paths: /ws, /api/health, /live-chat
│   │
│   └── models/
│       └── database.py             # SQLAlchemy models
│           ├── User
│           ├── GameServer (panel_password field)
│           └── ServerConsoleHistory (user_id nullable)
```

### Frontend Structure
```
/var/www/agtrmerkezi/frontend/src/
├── views/
│   ├── panel/
│   │   └── PanelLogin.vue          # Panel login sayfası
│   │       ├── Server dropdown (IP:PORT)
│   │       ├── Password input
│   │       └── Login handler
│   │
│   └── server/
│       ├── ServerWebPanel.vue      # Ana panel layout
│       │   ├── Sidebar navigation
│       │   ├── Top bar (server info, controls)
│       │   └── Router outlet
│       │
│       └── webpanel/
│           ├── Dashboard.vue        # Sunucu dashboard
│           │   ├── Status cards (Online/Offline, Players, Map)
│           │   ├── Connection info (IP:PORT, RCON, Code)
│           │   ├── Quick actions (Settings, Files, Restart)
│           │   └── Timeline (Created, Expiry, Auto-restart)
│           │
│           └── Console.vue          # RCON + Live Chat (2 tabs)
│               ├── Tab 1: RCON Console
│               │   ├── Command input (↑↓ history)
│               │   ├── Terminal output
│               │   ├── Quick buttons (Status, Stats, Changelevel)
│               │   └── Map change dialog
│               │
│               └── Tab 2: Live Chat
│                   ├── Monster log polling (5 saniyede bir)
│                   ├── Chat messages display
│                   ├── Player-based color coding
│                   └── Auto-scroll
│
├── router/
│   └── index.js                    # Vue Router
│       ├── Panel routes (/servers/:id/panel/*)
│       ├── Router guard (panel mode bypass)
│       └── requiresAuth meta
│
└── api/
    └── client.js                   # Axios client
        ├── Request interceptor (dual auth token injection)
        └── Response interceptor (401 handling)
```

---

## 🎮 Özellik Detayları

### 1. Dashboard (`/servers/:id/panel`)

**Dosya:** `/frontend/src/views/server/webpanel/Dashboard.vue`

**API Endpoints:**
```python
GET /api/servers/{id}/webpanel/info
# Returns:
{
  "id": 7,
  "name": "denemedenemehl",
  "unique_code": "AGTR-2026-00007",
  "ip_address": "185.171.25.138",
  "port": 27019,
  "rcon_password": "VV3A6isnhs1NJUfOruuziQ",
  "created_at": "2026-01-25T00:00:00Z",
  "expires_at": "2026-02-25T00:00:00Z",
  "auto_restart": true
}

GET /api/servers/{id}/webpanel/status
# Returns:
{
  "is_online": true,
  "current_players": 1,
  "max_players": 20,
  "current_map": "crossfire",
  "uptime_seconds": 3600
}
```

**UI Components:**
```vue
<template>
  <!-- Status Cards -->
  <div class="status-grid">
    <StatusCard icon="🟢" label="Durum" :value="status.is_online ? 'Online' : 'Offline'" />
    <StatusCard icon="👥" label="Oyuncular" :value="`${status.current_players}/${status.max_players}`" />
    <StatusCard icon="🗺️" label="Harita" :value="status.current_map" />
  </div>

  <!-- Connection Info -->
  <ConnectionInfo
    :ip-port="`${server.ip_address}:${server.port}`"
    :rcon-password="server.rcon_password"
    :server-code="server.unique_code"
  />

  <!-- Quick Actions -->
  <button @click="goToSettings">⚙️ Ayarlar</button>
  <button @click="goToFiles">📁 Dosyalar</button>
  <button @click="restartServer">🔄 Yeniden Başlat</button>
</template>
```

**Polling:** Dashboard, her 10 saniyede bir status endpoint'ini çağırarak canlı güncellemeler yapar.

---

### 2. RCON Console (`/servers/:id/panel/console` - Tab 1)

**Dosya:** `/frontend/src/views/server/webpanel/Console.vue`

**Backend Service:** `RCONService` (screen-based execution)

#### RCON Komut Çalıştırma Akışı

**Frontend → Backend:**
```javascript
// Console.vue
const executeCommand = async () => {
  const response = await apiClient.post(`/servers/${serverId}/rcon`, {
    command: 'status'
  })

  if (response.data.success) {
    addConsoleLine(response.data.output)
  } else {
    addConsoleLine(`❌ ${response.data.error}`, false, true)
  }
}
```

**Backend → Screen Session:**
```python
# rcon_service.py
async def execute(self, server, command, user_id):
    # 1. Komut validasyonu
    valid, message = self.validate_command(command)
    if not valid:
        return {"success": False, "error": message}

    # 2. Screen'e komut gönder
    screen_name = f"server_{server.id}"
    subprocess.run(["screen", "-S", screen_name, "-X", "stuff", f"{command}\n"])

    # 3. Output'u bekle
    await asyncio.sleep(1.5)

    # 4. Screen hardcopy ile output yakala
    subprocess.run(["screen", "-S", screen_name, "-X", "hardcopy", output_file])

    # 5. Output'u parse et
    with open(output_file, 'r') as f:
        lines = f.readlines()
        # Son komutu bul, sonrasını al
        response = parse_output(lines, command)

    # 6. Database'e log kaydet
    self._log_command(server.id, user_id, command, response, ...)

    return {"success": True, "response": response}
```

#### Güvenlik: Yasaklı Komutlar

```python
BLOCKED_COMMANDS = [
    "quit", "exit", "_restart",        # Server kapatma
    "rcon_password",                   # Şifre değiştirme
    "sv_cheats",                       # Cheat aktifleştirme
    "exec",                            # Dosya çalıştırma
    "plugin_load", "plugin_unload",    # Plugin yönetimi
    "sv_password",                     # Server şifresi
]

RESTRICTED_PATTERNS = {
    "changelevel": r"^changelevel\s+[a-zA-Z0-9_-]+$",
    "kick": r"^kick\s+(#?\d+|\".+\")(\s+.+)?$",
    "ban": r"^ban\s+.+$",
}
```

#### Komut Geçmişi

```javascript
// ↑↓ tuşları ile gezinme
const navigateHistory = (direction) => {
  if (direction === 'up') {
    historyIndex.value++
    currentCommand.value = commandHistory.value[historyIndex.value]
  } else if (direction === 'down') {
    historyIndex.value--
    currentCommand.value = historyIndex.value >= 0
      ? commandHistory.value[historyIndex.value]
      : ''
  }
}
```

#### Quick Action Butonları

```javascript
const quickCommands = [
  { label: '📊 Status', command: 'status' },
  { label: '📈 Stats', command: 'stats' },
  { label: '🗺️ Changelevel', action: () => showMapDialog.value = true },
  { label: '🔄 Restart', command: 'restart', confirm: true }
]
```

---

### 3. Live Chat (`/servers/:id/panel/console` - Tab 2)

**Dosya:** `/frontend/src/views/server/webpanel/Console.vue`

**Backend Endpoint:** `GET /api/servers/{id}/live-chat?since_line=0`

#### Polling Mekanizması

```javascript
// Her 5 saniyede bir polling
const fetchLiveChat = async () => {
  const response = await apiClient.get(`/servers/${serverId}/live-chat`, {
    params: { since_line: lastChatLine.value }
  })

  if (response.data.messages.length > 0) {
    response.data.messages.forEach(msg => {
      chatMessages.value.push(msg)
    })

    lastChatLine.value = response.data.last_line

    // Auto-scroll
    nextTick(() => {
      chatArea.value.scrollTop = chatArea.value.scrollHeight
    })
  }
}

setInterval(fetchLiveChat, 5000)
```

#### Backend Log Parsing

```python
@router.get("/{server_id}/live-chat")
async def get_live_chat(server_id: int, since_line: int = 0):
    # 1. Monster log dosyasını bul
    log_dir = f"/home/gameservers/servers/server_{server_id}/valve/addons/amxmodx/logs"
    monster_logs = glob(f"{log_dir}/monster*.log")
    latest_log = max(monster_logs, key=os.path.getmtime)

    # 2. since_line'dan itibaren oku
    with open(latest_log, 'r') as f:
        lines = f.readlines()
        new_lines = lines[since_line:]
        current_line = since_line

        # 3. Regex ile parse
        for line in new_lines:
            current_line += 1
            # Format: L 01/30/2026 - 18:25:10: [18:25:10] <Player><STEAM_ID>: message
            match = re.match(r'L\s+(\d{2}/\d{2}/\d{4}\s+-\s+\d{2}:\d{2}:\d{2}):\s+\[(\d{2}:\d{2}:\d{2})\]\s+<(.+?)><.+?>:\s+(.+)', line)

            if match:
                _, time_only, player, message = match.groups()

                # Renk kodlarını temizle (^0-^9)
                player_clean = re.sub(r'\^\d', '', player)

                # Oyuncu bazlı renk ata (MD5 hash)
                player_hash = int(hashlib.md5(player_clean.encode()).hexdigest()[:6], 16)
                colors = ['#58a6ff', '#3fb950', '#d29922', '#f85149', '#a371f7']
                color = colors[player_hash % len(colors)]

                messages.append({
                    'time': time_only,
                    'player': player_clean,
                    'message': message.strip(),
                    'color': color
                })

    return {
        "messages": messages,
        "last_line": current_line
    }
```

#### AMX Mod X Chat Logger

**Plugin:** `chatlog.amxx`

**Aktivasyon:**
```bash
# /valve/addons/amxmodx/configs/plugins.ini
chatlog.amxx

# Reload
screen -S server_X -X stuff "amx_plugins reload\n"
```

**Log Format:**
```
L 01/30/2026 - 18:25:10: [18:25:10] <^1|^8AGTR^1|-^8Grandmaster^1-^8><STEAM_0:1:121325554>: Merhaba!
```

**Log Dosyaları:**
```
/valve/addons/amxmodx/logs/
├── monster_2026-01-30.log  # Chat mesajları
├── L0130024.log            # Plugin logları
└── error_*.log             # Plugin hataları
```

---

## 🔒 Security & Validation

### 1. Ownership Validation (Steam Auth)

```python
def validate_server_ownership(server: GameServer, user: User):
    """Sunucunun kullanıcıya ait olduğunu doğrula"""
    if server.user_id != user.id:
        raise HTTPException(403, "Bu sunucu size ait değil")
```

### 2. Panel Token Validation

```python
if panel_server_id:
    if server_id != panel_server_id:
        raise HTTPException(403, "Panel token is for a different server")
```

### 3. CSRF Protection

```python
# middleware/csrf.py
exempt_paths = [
    "/api/auth",
    "/api/panel",     # Panel login exempt
    "/static",
    "/docs"
]
```

### 4. Rate Limiting

**Global Limits:**
- 300 requests/minute
- 50 requests/second

**Exempt Endpoints:**
- `/ws` (WebSocket)
- `/api/health`
- `/api/ws`
- `/live-chat` (Live Chat polling)

**Upload Limits:**
- 10 requests/minute for `/api/media`

**Brute Force Protection:**
- 5 failed login attempts
- 15 minute lockout

---

## 📊 Database Schema

### GameServer Table
```sql
CREATE TABLE game_servers (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    unique_code VARCHAR(20) UNIQUE,
    ip_address VARCHAR(45),
    port INT,
    rcon_password VARCHAR(50),
    panel_password VARCHAR(100),  -- Panel erişim şifresi
    status VARCHAR(20),            -- RUNNING, STOPPED, etc.
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    auto_restart BOOLEAN DEFAULT FALSE
);
```

### ServerConsoleHistory Table
```sql
CREATE TABLE server_console_history (
    id SERIAL PRIMARY KEY,
    server_id INT REFERENCES game_servers(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE CASCADE NULL,  -- Panel için nullable
    command VARCHAR(500) NOT NULL,
    response TEXT,
    command_type VARCHAR(20),  -- RCON, WEB, etc.
    execution_time_ms INT,
    ip_address VARCHAR(45),
    is_success BOOLEAN DEFAULT TRUE,
    error_message VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🚀 Deployment & Configuration

### Nginx Configuration

```nginx
# panel.agtrmerkezi.com
server {
    listen 443 ssl http2;
    server_name panel.agtrmerkezi.com;

    ssl_certificate /etc/letsencrypt/live/agtrmerkezi.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/agtrmerkezi.com/privkey.pem;

    location / {
        root /var/www/agtrmerkezi/static/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Backend Service

```bash
# Uvicorn
cd /var/www/agtrmerkezi
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 > /tmp/uvicorn.log 2>&1 &
```

### Frontend Build

```bash
cd /var/www/agtrmerkezi/frontend
npm run build
# Output: /var/www/agtrmerkezi/static/dist/
```

---

## 🧪 Testing & Debugging

### Debug Mode Aktivasyonu

**Backend:**
```python
# app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
```javascript
// Console.vue
console.log('[CONSOLE] Command:', command)
console.log('[CHAT] New messages:', response.data.messages)
```

### Log Dosyaları

**Backend Logs:**
```bash
tail -f /tmp/uvicorn.log
```

**RCON Service Logs:**
```bash
grep "PANEL_AUTH" /tmp/uvicorn.log
grep "RCON" /tmp/uvicorn.log
```

**Game Server Logs:**
```bash
tail -f /home/gameservers/servers/server_7/valve/logs/L*.log
tail -f /home/gameservers/servers/server_7/valve/addons/amxmodx/logs/monster_*.log
```

---

## 📈 Performance Optimizations

### 1. Rate Limiting Exemptions
Live-chat polling endpoint'i rate limit'ten muaf tutuldu (her 5 saniyede sürekli istek atıyor).

### 2. Polling Intervals
- **Dashboard Status:** 10 saniye
- **Live Chat:** 5 saniye

### 3. Database Indexes
```sql
CREATE INDEX idx_server_user ON game_servers(user_id);
CREATE INDEX idx_console_history_server ON server_console_history(server_id, created_at DESC);
```

### 4. Frontend Optimizations
- Lazy loading for routes
- Component-level code splitting
- Axios request cancellation for unmounted components

---

## 🔮 Future Enhancements (Planlanan)

### 1. Players Page
- Online oyuncu listesi
- Kick/Ban fonksiyonları
- Player stats

### 2. Settings Page
- Server.cfg düzenleme
- Plugin yönetimi
- Scheduled restarts

### 3. File Manager
- Dosya yükleme/indirme
- CFG dosyası düzenleme
- Log dosyası görüntüleme

### 4. Real-time Notifications
- WebSocket entegrasyonu
- Server offline/online bildirimleri
- New player joined notifications

---

## 📞 Troubleshooting

### Problem: 429 Too Many Requests
**Çözüm:** Live-chat endpoint'i rate limit exempt list'e eklendi.

### Problem: Panel login sonrası Steam login'e yönlendiriyor
**Çözüm:** Router guard'da panel mode bypass eklendi.

### Problem: RCON komutu çalışıyor ama database error
**Çözüm:** `ServerConsoleHistory.user_id` nullable yapıldı (panel users için).

### Problem: Live Chat mesajları görünmüyor
**Çözüm:** `chatlog.amxx` plugin'i `plugins.ini`'ye eklendi.

### Problem: Monster log dosyaları bulunamıyor
**Çözüm:** Log path `/valve/logs/` → `/valve/addons/amxmodx/logs/` düzeltildi.

---

## 📚 Referanslar

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Vue 3 Docs:** https://vuejs.org/
- **AMX Mod X:** https://www.amxmodx.org/
- **Half-Life SDK:** https://github.com/ValveSoftware/halflife

---

**Son Güncelleme:** 30 Ocak 2026
**Geliştirici:** Claude Sonnet 4.5 + AGTR Dev Team
**Lisans:** Proprietary - AGTR Merkezi
