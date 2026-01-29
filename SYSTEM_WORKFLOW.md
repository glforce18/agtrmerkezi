# 🎮 AGTR Merkezi - Sistem Akış Dökümanı

## 📋 İçindekiler
1. [Kullanıcı Sunucu Kiralama Akışı](#1-kullanıcı-sunucu-kiralama-akışı)
2. [Backend İşlem Süreci](#2-backend-işlem-süreci)
3. [Sunucu Kurulum Süreci](#3-sunucu-kurulum-süreci)
4. [Sunucu Kontrol Sistemi](#4-sunucu-kontrol-sistemi)
5. [RCON Yönetimi](#5-rcon-yönetimi)
6. [Web Panel Kullanımı](#6-web-panel-kullanımı)
7. [Monitoring & Health Check](#7-monitoring--health-check)

---

## 1. Kullanıcı Sunucu Kiralama Akışı

### Frontend → Backend → Database → Installation

```
┌──────────────────────────────────────────────────────────────────┐
│                    KULLANICI AKIŞI                                │
└──────────────────────────────────────────────────────────────────┘

1️⃣ Kullanıcı /servers/rent sayfasına gider
   ↓
   📄 ServerRent.vue yüklenir
   ↓
   🔍 API: GET /api/servers/packages
   ├─→ Backend: servers_unified.py @router.get("/packages")
   ├─→ Database: SELECT * FROM server_packages WHERE is_active = 1
   └─→ Response: [
         {id: 10, name: "Half-Life DM", game_type: "HLDM", price: 450, slots: 32},
         {id: 11, name: "Half-Life AG", game_type: "AG", price: 450, slots: 32},
         {id: 12, name: "CS 1.6 Pro", game_type: "CS16", price: 450, slots: 32}
       ]

2️⃣ Kullanıcı paket seçer (örn: Half-Life AG)
   ↓
   Form doldurur:
   - Sunucu adı: "AGTR Test Server"
   - Süre: 1 ay
   - Auto-renew: Evet

3️⃣ "Kirala" butonuna tıklar
   ↓
   🔄 API: POST /api/servers/order
   Body: {
     package_id: 11,
     server_name: "AGTR Test Server",
     duration: 1,
     auto_renew: true
   }

4️⃣ Backend İşleme Başlar
   ↓
   [Devamı aşağıda...]
```

---

## 2. Backend İşlem Süreci

### Order Server Endpoint Detayı

```python
# File: app/api/servers_unified.py
@router.post("/order")
async def order_server(data, current_user, db):
```

### Adım Adım İşlem:

```
┌──────────────────────────────────────────────────────────────────┐
│              BACKEND ORDER PROCESSING                             │
└──────────────────────────────────────────────────────────────────┘

STEP 1: Paket Doğrulama
─────────────────────────
SELECT * FROM server_packages
WHERE id = 11 AND is_active = 1
→ Half-Life AG paketi bulundu ✓

STEP 2: Port Slot Bulma
─────────────────────────
PortPoolManager.acquire_slot()
├─→ Available IP: 5.188.99.102
├─→ Available Port: 27015
└─→ Slot reserved ✓

STEP 3: Fiyat Hesaplama
─────────────────────────
Base Price: 450₺
Duration: 1 month
Discount: 0% (1 ay için indirim yok)
─────────────────
Total: 450₺

İndirim Tablosu:
- 3-5 ay: %10
- 6-11 ay: %15
- 12+ ay: %20

STEP 4: Server Kaydı Oluştur
─────────────────────────
INSERT INTO game_servers (
  owner_id = 1,
  name = "AGTR Test Server",
  game_type = "AG",
  ip_address = "5.188.99.102",
  port = 27015,
  slots = 32,
  rcon_password = "rcon_abc123xyz",  -- auto-generated
  package_id = 11,
  status = "PENDING",
  monthly_price = 450,
  unique_code = "SRV-2026-00042",   -- auto-generated
  expires_at = "2026-02-28 12:00:00"
)
→ Server ID: 123 created ✓

STEP 5: Payment Kaydı Oluştur
─────────────────────────
INSERT INTO payments (
  user_id = 1,
  amount = 450,
  status = "PENDING",
  reference_code = "PAY-2026-00123",
  description = "Half-Life AG - 1 Aylık Sunucu",
  server_id = 123,
  months = 1
)
→ Payment ID: 456 created ✓

STEP 6: Response Döndür
─────────────────────────
{
  "success": true,
  "server_id": 123,
  "payment_id": 456,
  "reference_code": "PAY-2026-00123",
  "amount": 450,
  "server_info": {
    "name": "AGTR Test Server",
    "ip": "5.188.99.102:27015",
    "slots": 32,
    "unique_code": "SRV-2026-00042"
  }
}
```

### Database Durumu (After Order)

```sql
-- game_servers tablosu
id  | owner_id | name              | game_type | ip            | port  | status  | rcon_password
123 | 1        | AGTR Test Server  | AG        | 5.188.99.102  | 27015 | PENDING | rcon_abc123xyz

-- payments tablosu
id  | user_id | amount | status  | reference_code  | server_id
456 | 1       | 450    | PENDING | PAY-2026-00123  | 123
```

---

## 3. Sunucu Kurulum Süreci

### Ödeme Onayından Sonra Kurulum

```
┌──────────────────────────────────────────────────────────────────┐
│            SERVER INSTALLATION WORKFLOW                           │
└──────────────────────────────────────────────────────────────────┘

TRIGGER: Payment status → COMPLETED
        (Admin panelden veya otomatik ödeme onayı)

UPDATE payments SET status = 'COMPLETED' WHERE id = 456;
  ↓
  🎬 Background Task Başlatılır
  ↓
  ServerInstallationService.install_server(server_id=123)
```

### Installation Steps

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Installation Record Oluştur                            │
└─────────────────────────────────────────────────────────────────┘
INSERT INTO server_installations (
  server_id = 123,
  status = 'IN_PROGRESS',
  progress_percent = 0,
  current_step = 'Dizin hazırlanıyor'
)

┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Server Dizini Hazırla                                  │
└─────────────────────────────────────────────────────────────────┘
mkdir -p /home/gameservers/servers/server_123
chmod 755 /home/gameservers/servers/server_123

Progress: 10%

┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Template Kopyala (METVİCUT SİSTEM)                     │
└─────────────────────────────────────────────────────────────────┘
Source: /home/gameservers/templates/hlds/ag/
Dest:   /home/gameservers/servers/server_123/

Method 1: Template Cache (FAST - 10 saniye)
─────────────────────────────────────────────
TemplateCacheService.extract_template_archive()
├─→ Cached ag.tar.gz extracted
└─→ 2.5 GB extracted in ~10 seconds ⚡

Method 2: Rsync Fallback (SLOW - 60 saniye)
─────────────────────────────────────────────
rsync -av /templates/hlds/ag/ /servers/server_123/
└─→ 2.5 GB copied in ~60 seconds

Progress: 40%

┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: server.cfg Yapılandır                                  │
└─────────────────────────────────────────────────────────────────┘
File: /home/gameservers/servers/server_123/ag/server.cfg

Değişiklikler:
├─→ hostname "AGTR Test Server"
├─→ rcon_password "rcon_abc123xyz"
├─→ port 27015
├─→ maxplayers 32
├─→ sv_contact "admin@agtrmerkezi.com"
├─→ sys_ticrate 500      (LOCKED - performans)
├─→ fps_max 600          (LOCKED - performans)
└─→ sv_maxrate 100000    (LOCKED - network)

Progress: 55%

┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: AMXModX Admin Ayarla                                   │
└─────────────────────────────────────────────────────────────────┘
File: /home/gameservers/servers/server_123/ag/addons/amxmodx/configs/users.ini

Sunucu sahibini admin yap:
"STEAM_0:1:123456" "" "abcdefghijklmnopqrstu" "ce"

Progress: 70%

┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Başlangıç Scripti Oluştur                              │
└─────────────────────────────────────────────────────────────────┘
File: /home/gameservers/servers/server_123/start.sh

#!/bin/bash
SCREEN_NAME="server_123"
HLDS_PATH="/home/gameservers/servers/server_123"

cd $HLDS_PATH

screen -dmS $SCREEN_NAME ./hlds_run \
  -game ag \
  +ip 5.188.99.102 \
  +port 27015 \
  +maxplayers 32 \
  +map ag_crossfire \
  +sys_ticrate 500 \
  +fps_max 600

chmod +x /home/gameservers/servers/server_123/start.sh

Progress: 85%

┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: Kurulum Doğrula                                        │
└─────────────────────────────────────────────────────────────────┘
Checks:
✓ hlds_linux exists
✓ ag/dlls/ag.so exists
✓ start.sh executable
✓ server.cfg valid

Progress: 95%

┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: Sunucuyu Başlat (Test)                                 │
└─────────────────────────────────────────────────────────────────┘
Execute: /home/gameservers/servers/server_123/start.sh

Screen session started: server_123
Process PID: 12345

Wait 10 seconds...

A2S Query Test:
├─→ IP: 5.188.99.102:27015
├─→ Status: ONLINE ✓
├─→ Players: 0/32
└─→ Map: ag_crossfire

Progress: 100%

┌─────────────────────────────────────────────────────────────────┐
│  STEP 9: Database Güncelle                                      │
└─────────────────────────────────────────────────────────────────┘
UPDATE game_servers SET
  status = 'RUNNING',
  server_path = '/home/gameservers/servers/server_123',
  screen_name = 'server_123',
  process_pid = 12345,
  mod_type = 'ag',
  last_started = NOW(),
  last_heartbeat = NOW()
WHERE id = 123;

UPDATE server_installations SET
  status = 'COMPLETED',
  progress_percent = 100,
  completed_at = NOW()
WHERE server_id = 123;

🎉 KURULUM TAMAMLANDI!
```

### Installation Timeline

```
00:00 - Start installation
00:05 - Directory created
00:15 - Template extracted (cache)
00:20 - server.cfg configured
00:25 - AMXModX setup
00:30 - Start script created
00:35 - Validation complete
00:45 - Server started
00:55 - Query test OK
01:00 - Installation complete ✓

TOTAL TIME: ~60 seconds (with cache)
           ~120 seconds (without cache)
```

---

## 4. Sunucu Kontrol Sistemi

### Start/Stop/Restart Operations

```
┌──────────────────────────────────────────────────────────────────┐
│                SERVER CONTROL WORKFLOW                            │
└──────────────────────────────────────────────────────────────────┘

SERVICE: ServerControlService (app/services/server_control.py)
```

### 🟢 START SERVER

```
Frontend: serverPanel.vue
  ↓
  Button Click: "Start Server"
  ↓
  API: POST /api/servers/123/start
  ↓
Backend: servers_unified.py
  ↓
  ServerControlService.start_server(123)

┌─────────────────────────────────────────────────────────────────┐
│  START PROCESS                                                   │
└─────────────────────────────────────────────────────────────────┘

1. Check if already running
   ├─→ A2S Query: 5.188.99.102:27015
   └─→ Not running ✓

2. Find start script
   ├─→ /home/gameservers/servers/server_123/start.sh
   └─→ Exists ✓

3. Execute script
   ├─→ subprocess.exec('./start.sh')
   └─→ Screen session created

4. Wait & Poll (30 seconds max)
   Loop every 2 seconds:
   ├─→ Check A2S Query
   ├─→ Check process (ps aux | grep hlds)
   └─→ Server responded! ✓

5. Get PID
   ├─→ ps aux | grep "server_123"
   └─→ PID: 12345

6. Update Database
   UPDATE game_servers SET
     status = 'RUNNING',
     process_pid = 12345,
     last_started = NOW(),
     last_heartbeat = NOW()
   WHERE id = 123;

7. Return success
   {
     "success": true,
     "message": "Sunucu başlatıldı",
     "pid": 12345
   }

TOTAL TIME: 5-15 seconds
```

### 🔴 STOP SERVER

```
API: POST /api/servers/123/stop
  ↓
ServerControlService.stop_server(123, graceful=True)

┌─────────────────────────────────────────────────────────────────┐
│  STOP PROCESS (Graceful)                                         │
└─────────────────────────────────────────────────────────────────┘

1. Check if running
   └─→ Running ✓

2. Send graceful shutdown
   ├─→ screen -S server_123 -X stuff 'quit\n'
   └─→ Sent to screen session

3. Wait for graceful stop (10 seconds)
   Loop every 1 second:
   ├─→ Check if process exists
   └─→ Process terminated ✓

4. Force kill (if still running)
   ├─→ screen -S server_123 -X quit
   ├─→ kill -9 12345
   └─→ Process killed

5. Update Database
   UPDATE game_servers SET
     status = 'STOPPED',
     process_pid = NULL
   WHERE id = 123;

6. Return success
   {
     "success": true,
     "message": "Sunucu durduruldu"
   }

TOTAL TIME: 1-11 seconds
```

### 🔄 RESTART SERVER

```
API: POST /api/servers/123/restart
  ↓
ServerControlService.restart_server(123)

┌─────────────────────────────────────────────────────────────────┐
│  RESTART PROCESS                                                 │
└─────────────────────────────────────────────────────────────────┘

1. Stop Server
   └─→ (Stop process above)

2. Wait 2 seconds
   └─→ Cooldown period

3. Start Server
   └─→ (Start process above)

4. Return success
   {
     "success": true,
     "message": "Sunucu yeniden başlatıldı"
   }

TOTAL TIME: 10-30 seconds
```

---

## 5. RCON Yönetimi

### RCON Command Execution

```
┌──────────────────────────────────────────────────────────────────┐
│                    RCON WORKFLOW                                  │
└──────────────────────────────────────────────────────────────────┘

SERVICE: RCONService (app/services/rcon_service.py)
PROTOCOL: Half-Life/GoldSrc RCON (UDP)
```

### Command Flow

```
Frontend: ServerPanel.vue Terminal
  ↓
  User types: "status"
  ↓
  Press ENTER
  ↓
  API: POST /api/servers/123/rcon
  Body: {command: "status"}
  ↓
Backend: servers_unified.py
  ↓
  RCONService.execute_command()

┌─────────────────────────────────────────────────────────────────┐
│  RCON PROTOCOL (GoldSrc)                                         │
└─────────────────────────────────────────────────────────────────┘

STEP 1: Get Challenge
─────────────────────────
UDP Socket → 5.188.99.102:27015
Send: \xFF\xFF\xFF\xFFchallenge rcon\n
  ↓
Receive: \xFF\xFF\xFF\xFFchallenge rcon 1234567890\n
  ↓
Challenge: 1234567890 ✓

STEP 2: Send Command
─────────────────────────
Packet Format:
\xFF\xFF\xFF\xFFrcon {challenge} "{password}" {command}

Example:
\xFF\xFF\xFF\xFFrcon 1234567890 "rcon_abc123xyz" status

UDP Socket → 5.188.99.102:27015
  ↓
Send packet
  ↓
Receive response (max 4096 bytes)

STEP 3: Parse Response
─────────────────────────
Raw: \xFF\xFF\xFF\xFFl
hostname:  AGTR Test Server
version :  48/1.1.2.7/2.0.0.0 7559 secure
udp/ip  :  5.188.99.102:27015
map     :  ag_crossfire at: 0 x, 0 y, 0 z
players :  0 active (32 max)

STEP 4: Clean Output
─────────────────────────
Remove:
- Color codes (^0-^9)
- RCON prefix (\xFF\xFF\xFF\xFFl)
- Extra whitespace

Return cleaned text ✓

STEP 5: Save to History
─────────────────────────
INSERT INTO server_console_history (
  server_id = 123,
  user_id = 1,
  command = 'status',
  output = '...',
  executed_at = NOW()
)

STEP 6: Return to Frontend
─────────────────────────
{
  "success": true,
  "output": "hostname: AGTR Test Server\n..."
}

Frontend displays in terminal ✓
```

### RCON Commands Supported

```
BASIC COMMANDS:
├─→ status       - Server status
├─→ users        - Connected players
├─→ maps *       - Available maps
├─→ stats        - Server stats
├─→ version      - Server version
└─→ say <text>   - Broadcast message

PLAYER MANAGEMENT:
├─→ kick #<slot>            - Kick player
├─→ ban <minutes> #<slot>   - Ban player
└─→ banid <minutes> <steamid>

MAP CONTROL:
├─→ changelevel <map>  - Change map
└─→ restart            - Restart round (CS)

ADMIN COMMANDS (AMXModX):
├─→ amx_ban <name> <time> <reason>
├─→ amx_kick <name> <reason>
├─→ amx_map <mapname>
└─→ amx_cfg <config>
```

---

## 6. Web Panel Kullanımı

### ServerPanel.vue Full Features

```
┌──────────────────────────────────────────────────────────────────┐
│                  WEB PANEL INTERFACE                              │
└──────────────────────────────────────────────────────────────────┘

URL: /servers/panel/123

SECTIONS:
```

### 📊 Server Stats

```
┌───────────────────────────────────────┐
│  Server Statistics                    │
├───────────────────────────────────────┤
│  Players:    5/32                     │
│  Map:        ag_crossfire             │
│  Game Type:  Half-Life AG             │
│  Uptime:     24h 32m                  │
└───────────────────────────────────────┘

Data Source:
- Real-time A2S Query (every 30s)
- Database cache
```

### 🎮 Server Control

```
┌───────────────────────────────────────┐
│  Control Panel                        │
├───────────────────────────────────────┤
│  [▶ Start]  [⏹ Stop]  [🔄 Restart]   │
│  [👥 Players]  [🔧 Config]           │
└───────────────────────────────────────┘

Buttons:
├─→ Start: POST /api/servers/123/start
├─→ Stop: POST /api/servers/123/stop
└─→ Restart: POST /api/servers/123/restart
```

### 💻 RCON Terminal

```
┌──────────────────────────────────────────────────────────────────┐
│  λ RCON TERMINAL                              SERVER #123         │
├──────────────────────────────────────────────────────────────────┤
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║  AGTR Merkezi - Remote Console Access System v3.0        ║  │
│  ║  Connected to: AGTR TEST SERVER                          ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
│                                                                   │
│  root@server-123:~$ status                                       │
│  hostname:  AGTR Test Server                                     │
│  version :  48/1.1.2.7/2.0.0.0 7559 secure                      │
│  players :  5 active (32 max)                                    │
│                                                                   │
│  root@server-123:~$ users                                        │
│  #  1 "PlayerOne"   STEAM_0:1:123456    01:23:45               │
│  #  2 "PlayerTwo"   STEAM_0:0:789012    00:45:12               │
│                                                                   │
│  root@server-123:~$ _                                            │
├──────────────────────────────────────────────────────────────────┤
│  Quick Commands:                                                  │
│  [status] [users] [maps] [de_dust2] [announce] [stats]          │
└──────────────────────────────────────────────────────────────────┘

Features:
✓ Command history (↑/↓ arrow keys)
✓ Auto-complete
✓ Color-coded output
✓ Quick command buttons
✓ Terminal scrollback
```

### 👥 Active Players

```
┌──────────────────────────────────────────────────────────────────┐
│  Active Players (5)                               [🔄 Refresh]   │
├──────────────────────────────────────────────────────────────────┤
│  Slot | Name         | Steam ID        | Time    | Actions      │
│  ─────┼──────────────┼─────────────────┼─────────┼──────────    │
│  #1   | PlayerOne    | STEAM_0:1:12345 | 01:23   | [Kick]       │
│  #2   | PlayerTwo    | STEAM_0:0:78901 | 00:45   | [Kick]       │
│  #3   | PlayerThree  | STEAM_0:1:55555 | 00:12   | [Kick]       │
└──────────────────────────────────────────────────────────────────┘

Data: GET /api/servers/123/players (RCON users command)
Kick: POST /api/servers/123/players/{slot}/kick
```

---

## 7. Monitoring & Health Check

### Background Services

```
┌──────────────────────────────────────────────────────────────────┐
│               BACKGROUND MONITORING                               │
└──────────────────────────────────────────────────────────────────┘

SERVICE: ServerSchedulerService
INTERVAL: Every 60 seconds
```

### Health Check Process

```
FOR EACH server IN game_servers WHERE status = 'RUNNING':

1. A2S Query Check
   ├─→ Query: 5.188.99.102:27015
   ├─→ Timeout: 5 seconds
   └─→ Response:
       ├─→ SUCCESS: Update last_heartbeat
       └─→ FAILED: Mark as potential crash

2. Process Check
   ├─→ Check PID: ps aux | grep 12345
   └─→ Process exists: ✓

3. Update Database
   UPDATE game_servers SET
     last_heartbeat = NOW(),
     current_players = 5,
     current_map = 'ag_crossfire'
   WHERE id = 123;

4. Crash Detection
   IF last_heartbeat > 5 minutes ago:
     ├─→ Increment crash_count
     ├─→ Send alert to admin
     ├─→ Auto-restart? (if enabled)
     └─→ UPDATE status = 'CRASHED'
```

### Auto-Restart Logic

```
IF server.auto_restart = TRUE AND status = 'CRASHED':

1. Check crash count
   IF crash_count < 3:
     ├─→ Restart immediately
     └─→ Log restart attempt
   ELSE:
     ├─→ Exponential backoff
     ├─→ Wait: 2^crash_count minutes
     └─→ Notify admin

2. Restart
   ServerControlService.restart_server(123)

3. Monitor
   Wait 60 seconds
   Check if stable
   Reset crash_count if OK
```

---

## 📊 Sistem Performans Metrikleri

### Tipik İşlem Süreleri

| İşlem | Süre | Notlar |
|-------|------|--------|
| Paket Listeleme | 50-100ms | Database query |
| Sunucu Sipariş | 200-500ms | DB insert + validation |
| Kurulum (Cache) | 30-60s | Template extract + config |
| Kurulum (No Cache) | 60-120s | Full rsync copy |
| Start Server | 5-15s | Screen start + A2S check |
| Stop Server | 1-11s | Graceful + force kill |
| RCON Command | 100-500ms | UDP round-trip |
| A2S Query | 50-200ms | Server info fetch |
| Health Check | 5s | Full monitoring cycle |

### Resource Usage (Per Server)

```
Disk Space:
├─→ Full Copy: 2.5 GB
└─→ Shared Files: 50 MB

RAM:
├─→ HLDS Process: 50-150 MB
├─→ 32 Slot AG: ~100 MB
└─→ With players: +2MB per player

CPU:
├─→ Idle: 1-2%
├─→ 10 players: 5-10%
└─→ 32 players: 15-25%

Network:
├─→ Idle: 1-5 KB/s
├─→ Per player: ~5-10 KB/s
└─→ 32 players: ~300 KB/s
```

---

## 🔐 Güvenlik Katmanları

### 1. Authentication
```
JWT Token → Header: Authorization: Bearer xxx
├─→ Token validation
├─→ User session check
└─→ Permission verification
```

### 2. Server Ownership
```
EVERY API call checks:
validate_server_ownership(server, current_user)
├─→ server.owner_id == current_user.id
└─→ or current_user.role == ADMIN
```

### 3. RCON Rate Limiting
```
Max 10 commands per minute per user
├─→ Redis counter
├─→ Sliding window
└─→ 429 Too Many Requests
```

### 4. Input Validation
```
├─→ Server name: max 100 chars, no special chars
├─→ RCON commands: max 255 chars
├─→ Package ID: exists in database
└─→ Port range: 27015-27050 only
```

---

## 🎯 Sonuç

### Sistem Akış Özeti

```
USER → Frontend (Vue.js)
  ↓
  API Call (axios)
  ↓
Backend (FastAPI) → servers_unified.py
  ↓
Services:
├─→ ServerInstallationService (kurulum)
├─→ ServerControlService (start/stop)
├─→ RCONService (komutlar)
└─→ ServerSchedulerService (monitoring)
  ↓
Database (MySQL)
├─→ game_servers
├─→ server_packages
├─→ payments
└─→ server_console_history
  ↓
Linux System:
├─→ /home/gameservers/servers/
├─→ Screen sessions
├─→ HLDS processes
└─→ A2S queries (UDP)
  ↓
Result → Frontend → User
```

### 36 Servis Listesi

```
app/services/
├── alert_service.py              (6.9K)   - Alert/notification
├── amxx_admin.py                 (17K)    - AMXModX admin management
├── analytics_service.py          (10K)    - Analytics & metrics
├── auto_update_service.py        (15K)    - Auto-update system
├── command_quota_service.py      (5.1K)   - Command quotas
├── ddos_protection_service.py    (13K)    - DDoS protection
├── email.py                      (15K)    - Email service
├── file_manager.py               (36K)    - File manager
├── forum_advanced.py             (44K)    - Forum advanced features
├── forum_gamification.py         (15K)    - Forum gamification
├── forum_rewards.py              (9.6K)   - Forum rewards
├── installation_progress.py      (5.5K)   - Installation tracking
├── monitor.py                    (16K)    - Server monitoring (A2S)
├── player_management_service.py  (12K)    - Player management
├── plugin_manager.py             (24K)    - Plugin management
├── port_pool_manager.py          (6.7K)   - Port allocation
├── rcon_rate_limiter.py          (8.9K)   - RCON rate limiting
├── rcon_service.py               (26K)    - RCON protocol ⭐
├── redis_manager.py              (5.2K)   - Redis cache
├── respawn_monitor.py            (7.9K)   - Crash detection
├── server_config.py              (19K)    - Server config ⭐
├── server_control.py             (16K)    - Start/stop/restart ⭐
├── server_installation.py        (27K)    - Installation ⭐
├── server_scheduler.py           (12K)    - Background tasks ⭐
├── server_scraper.py             (21K)    - Server scraping
├── shared_installation_service.py (16K)   - Shared files (YENİ)
├── stats_service.py              (14K)    - Statistics
├── template_cache_service.py     (14K)    - Template cache
└── wallet.py                     (15K)    - Wallet system

⭐ = Core server management services
```

---

**Döküman Sonu** - AGTR Merkezi v6.0 System Workflow
