# AGTR Merkezi - Server Oluşturma ve Kurulum Süreci

**Dokümantasyon Tarihi:** 2026-01-30
**Sistem Versiyonu:** AGTR Merkezi v6.1

---

## İÇİNDEKİLER

1. [Genel Bakış](#genel-bakış)
2. [Server Durumları (Status Flow)](#server-durumları)
3. [Adım Adım Süreç](#adım-adım-süreç)
4. [Dosya Sistemi Yapısı](#dosya-sistemi-yapısı)
5. [Screen Session Yönetimi](#screen-session-yönetimi)
6. [Panel Erişimi](#panel-erişimi)
7. [Database Tabloları](#database-tabloları)
8. [Önemli Konfigürasyon Dosyaları](#önemli-konfigürasyon-dosyaları)

---

## GENEL BAKIŞ

Server oluşturma süreci 4 ana aşamadan oluşur:

```
OLUŞTURMA → KURULUM → YAPILANDIRMA → ÇALIŞTIRMA
```

**Süre:** ~30-60 saniye (mod tipine göre)
**Disk Kullanımı:** ~50MB (shared installation) veya ~2.5GB (full copy)

---

## SERVER DURUMLARI

### Status Flow Chart

```
PENDING (onay bekliyor)
    ↓
CREATING (oluşturuluyor)
    ↓
INSTALLING (kurulum yapılıyor)
    ↓
STOPPED (kurulum tamam, başlatılmaya hazır)
    ↓
RUNNING (çalışıyor)
    ↓
STOPPED / EXPIRED / DELETED / SUSPENDED
```

### Durumlar ve Anlamları

| Durum | Açıklama | Kullanıcı Yapabilir |
|-------|----------|---------------------|
| `PENDING` | Sunucu oluşturuldu, admin onayı bekleniyor | Bekle |
| `CREATING` | Sunucu kaydı oluşturuluyor | Kurulum takibi |
| `INSTALLING` | Dosyalar kopyalanıyor, yapılandırılıyor | Kurulum takibi |
| `STOPPED` | Sunucu hazır ama çalışmıyor | Başlat düğmesi |
| `RUNNING` | Sunucu aktif | Durdur, RCON, Panel |
| `SUSPENDED` | Çok fazla crash / admin tarafından askıya alındı | Ticket aç |
| `EXPIRED` | Süre doldu | Yenile |
| `REJECTED` | Admin tarafından reddedildi | - |
| `DELETED` | Silindi | - |

---

## ADIM ADIM SÜREÇ

### 1. KULLANICI SERVER OLUŞTURUR

**Endpoint:** `POST /api/v2/servers/create`

**Request Body:**
```json
{
    "name": "Benim Serverim",
    "mod_type": "ag",  // ag, ag_openag, cs16, hldm, valve_new
    "port": 27015,
    "maxplayers": 32,
    "rcon_password": "myRconPass",  // opsiyonel
    "sv_password": "joinPass",  // opsiyonel
    "panel_password": "panelSifre",  // GEREKLİ (panel için)
    "admins": [  // opsiyonel
        {"steam_id": "STEAM_0:1:12345", "flags": "abcdefghijklmnopqrstu"}
    ]
}
```

**İşlem Adımları:**

1. **Mod Tipi Kontrolü**
   - Geçerli modlar: `ag`, `ag_openag`, `cs16`, `hldm`, `valve_new`

2. **Unique Code Oluşturma**
   - Format: `AGTR-2026-00001`
   - Her server için benzersiz

3. **Boş Slot Bulma (PortPoolManager)**
   ```python
   slot = pool_manager.acquire_slot()
   allocated_ip, allocated_port = slot
   # Örnek: ("176.53.66.10", 27015)
   ```

4. **Database Kaydı Oluşturma**
   ```sql
   INSERT INTO game_servers (
       owner_id, owner_steam_id, name, game_type,
       ip_address, port, slots, rcon_password,
       sv_password, unique_code, mod_type,
       status, created_at
   ) VALUES (
       user_id, steam_id, "Benim Serverim", "AG",
       "176.53.66.10", 27015, 32, "rconpass",
       "joinpass", "AGTR-2026-00001", "ag",
       "CREATING", NOW()
   )
   ```

5. **Installation Record Oluşturma**
   ```sql
   INSERT INTO server_installations (
       server_id, user_id, unique_code, status,
       template_type, total_steps, created_at
   ) VALUES (
       123, user_id, "AGTR-2026-00001", "PENDING",
       "ag", 8, NOW()
   )
   ```

6. **Background Task Başlatma**
   - Installation service arka planda çalışmaya başlar
   - Kullanıcı progress takibi yapabilir

**Response:**
```json
{
    "success": true,
    "server_id": 123,
    "unique_code": "AGTR-2026-00001",
    "installation_id": 456,
    "message": "Sunucu olusturuldu, kurulum baslatildi"
}
```

---

### 2. KURULUM SÜRECİ (ServerInstallationService)

**Toplam 8 Adım, ~30-60 saniye**

#### **Adım 0-1: Dizin Hazırlama ve Template Kopyalama (0-40%)**

**Kaynak Template:**
```
/home/gameservers/templates/hlds/
├── ag/               # AG Mod template
├── ag_openag/        # OpenAG template
├── cstrike/          # CS 1.6 template
├── valve/            # HL Deathmatch
└── valvenewvalve/    # Valve DM (new)
```

**Hedef Dizin:**
```
/home/gameservers/servers/server_123/
```

**İşlemler:**
```bash
# Stage 1: HLDS base dosyalarını kopyala
rsync -a --exclude=[mod_folders] /templates/hlds/ /servers/server_123/

# Stage 2: Mod-specific dosyaları kopyala
rsync -a /templates/hlds/ag/ /servers/server_123/ag/
```

**Kopyalanan Dosyalar:**
- `hlds_run` - Ana HLDS executable
- `hlds_linux` - Linux HLDS binary
- `libsteam.so` - Steam kütüphanesi
- Mod klasörü (ag, cstrike, valve)
- Tüm oyun dosyaları (maps, models, sprites, sound, vb.)

---

#### **Adım 2: server.cfg Yapılandırma (45-50%)**

**Dosya:** `/servers/server_123/ag/server.cfg`

**Yapılandırılan Ayarlar:**
```cfg
hostname "Benim Serverim"
rcon_password "myRconPass"
sv_password "joinPass"  // opsiyonel
maxplayers 32
sv_maxplayers 32

// Sabit ayarlar (değişmez)
sys_ticrate 500
fps_max 600
sv_maxrate 100000
sv_minrate 10000
sv_lan 0
```

**İşlem:**
```python
# server.cfg dosyasını oku
config = read_file(server_cfg_path)

# Ayarları güncelle/ekle
config = update_cvar(config, "hostname", server_name)
config = update_cvar(config, "rcon_password", rcon_pass)
config = update_cvar(config, "sv_password", sv_pass)
config = update_cvar(config, "maxplayers", maxplayers)

# Dosyaya geri yaz
write_file(server_cfg_path, config)
```

---

#### **Adım 3: AMXModX Framework (55-60%)**

AMXModX zaten template'te mevcut olduğu için bu adımda özel bir işlem yapılmaz.

**Klasör Yapısı:**
```
/servers/server_123/ag/addons/amxmodx/
├── amxx.exe
├── plugins/
│   ├── admin.amxx
│   ├── admincmd.amxx
│   ├── mapchooser.amxx
│   └── ... (diğer pluginler)
├── configs/
│   ├── amxx.cfg
│   ├── plugins.ini
│   └── users.ini  (Adım 4'te oluşturulacak)
├── logs/
└── modules/
```

---

#### **Adım 4: Admin Listesi Oluşturma (65-70%)**

**Dosya:** `/servers/server_123/ag/addons/amxmodx/configs/users.ini`

**Format:**
```ini
; AGTR Merkezi - Auto-generated Admin List
; Server ID: 123
; Generated: 2026-01-30 12:00:00

"STEAM_0:1:12345678" "admin_pass" "abcdefghijklmnopqrstu" "a"
"STEAM_0:0:87654321" "" "abcdefg" "ce"
```

**Flaglar:**
- `a` - immunity (kick/ban edilemez)
- `b` - reservation (reserved slot)
- `c` - amx_kick command
- `d` - amx_ban command
- `e` - amx_slay command
- ... (toplam 20+ flag)
- `abcdefghijklmnopqrstu` = FULL ADMIN

**Otomatik Eklenenler:**
1. Server sahibi (owner_steam_id) - FULL ADMIN
2. Request'teki admins listesi

---

#### **Adım 5: Başlatma Scriptleri Oluşturma (75-80%)**

**Dosya 1:** `/servers/server_123/start.sh`

```bash
#!/bin/bash
SERVER_DIR="/home/gameservers/servers/server_123"
SCREEN_NAME="agtr_123"
MOD="ag"
PORT=27015
MAXPLAYERS=32

cd "$SERVER_DIR"

# Eski session varsa kapat
screen -S $SCREEN_NAME -X quit 2>/dev/null

# Server'ı screen içinde başlat
screen -dmS $SCREEN_NAME ./hlds_run \
    -game $MOD \
    +port $PORT \
    +maxplayers $MAXPLAYERS \
    -pingboost 3 \
    +sys_ticrate 500
```

**Dosya 2:** `/servers/server_123/stop.sh`

```bash
#!/bin/bash
SCREEN_NAME="agtr_123"

# Graceful shutdown (quit komutu gönder)
screen -S $SCREEN_NAME -X stuff 'quit\n'

# 10 saniye bekle
sleep 10

# Hala çalışıyorsa force kill
screen -S $SCREEN_NAME -X quit 2>/dev/null
```

**Permissions:**
```bash
chmod +x start.sh stop.sh
```

---

#### **Adım 6: Kurulum Doğrulama (85-90%)**

**Gerekli Dosyalar Kontrolü:**
```
✓ hlds_run
✓ hlds_linux
✓ ag/server.cfg
✓ ag/mapcycle.txt
✓ ag/addons/amxmodx/configs/users.ini
✓ start.sh
✓ stop.sh
```

Herhangi bir dosya eksikse → `INSTALLATION FAILED`

---

#### **Adım 7: Test Başlatma (95-100%)**

**İşlem:**
```bash
# Server'ı başlat
./start.sh

# 3 saniye bekle
sleep 3

# Screen session kontrol et
screen -ls | grep agtr_123

# Eğer bulunduysa:
# - Kurulum BAŞARILI
# - Server'ı durdur (test amaçlıydı)
./stop.sh
```

**Sonuç:**
- Başarılı → `status = STOPPED` (kullanıcı başlatabilir)
- Başarısız → `status = SUSPENDED`

---

#### **Adım 8: Kurulum Tamamlandı**

**Database Updates:**
```sql
-- Installation record
UPDATE server_installations SET
    status = 'COMPLETED',
    progress_percent = 100,
    current_step = 'Kurulum tamamlandi',
    completed_at = NOW()
WHERE id = 456;

-- Server status
UPDATE game_servers SET
    status = 'STOPPED'
WHERE id = 123;
```

**WebSocket Broadcast:**
```javascript
{
    "event": "installation_progress",
    "server_id": 123,
    "progress": 100,
    "stage": "Kurulum tamamlandi",
    "message": "Server hazir, başlatabilirsiniz"
}
```

---

### 3. SERVER BAŞLATMA (User Action)

**Endpoint:** `POST /api/v2/servers/123/start`

**İşlem Akışı:**
```python
1. start.sh dosyasını çalıştır
   └─ screen -dmS agtr_123 ./hlds_run -game ag +port 27015 ...

2. 30 saniye boyunca kontrol et:
   └─ Her 2 saniyede bir screen session'ı kontrol et
   └─ Eğer session bulunursa:
       ├─ PID'yi al (psutil ile HLDS process bulunur)
       ├─ Database'i güncelle:
       │   ├─ status = RUNNING
       │   ├─ process_pid = PID
       │   └─ last_started = NOW()
       └─ Return success

3. 30 saniye içinde başlamazsa:
   └─ Return error (timeout)
```

**Database Update:**
```sql
UPDATE game_servers SET
    status = 'RUNNING',
    process_pid = 12345,
    last_started = NOW()
WHERE id = 123;
```

---

### 4. PANEL ERİŞİMİ KURULUMU

**Panel Şifresi Ayarlama:**

Server oluşturulurken `panel_password` alanı doluysa, public panel erişimi aktif olur.

**Login Endpoint:** `POST /api/panel/auth`

**Request:**
```json
{
    "server_id": 123,
    "panel_password": "panelSifre"
}
```

**Response (Başarılı):**
```json
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "server_id": 123,
    "server_name": "Benim Serverim"
}
```

**JWT Token İçeriği:**
```json
{
    "sub": "panel_123",
    "server_id": 123,
    "type": "panel",
    "exp": 1738356296  // 12 saat geçerli
}
```

**Token ile Erişilebilen Endpoint'ler:**
- `GET /servers/123/webpanel/info` - Server bilgileri
- `GET /servers/123/webpanel/status` - Anlık durum
- `POST /servers/123/rcon` - RCON komutları
- `GET /servers/123/players` - Oyuncu listesi
- `GET /servers/123/logs` - Log dosyaları
- `POST /servers/123/start` - Server başlat
- `POST /servers/123/stop` - Server durdur

---

## DOSYA SİSTEMİ YAPISI

### Kurulum Sonrası Tam Klasör Yapısı

```
/home/gameservers/servers/server_123/
│
├── hlds_run                          # Ana HLDS executable
├── hlds_linux                        # HLDS Linux binary
├── start.sh                          # Başlatma scripti (oluşturuldu)
├── stop.sh                           # Durdurma scripti (oluşturuldu)
├── libsteam.so                       # Steam kütüphanesi
├── valve/                            # Base Half-Life mod (her zaman var)
│
└── ag/                               # AG Mod klasörü (mod_type'a göre: ag, cstrike, valve)
    │
    ├── server.cfg                    # ✓ YAPILANDIRILDI
    ├── mapcycle.txt                  # Map rotasyonu
    ├── motd.txt                      # Sunucu mesajı
    ├── banned.cfg                    # Banned entities
    │
    ├── addons/
    │   └── amxmodx/
    │       ├── amxx.dll              # AMXModX core
    │       ├── plugins.ini           # Aktif plugin listesi
    │       │
    │       ├── plugins/              # Plugin dosyaları (.amxx)
    │       │   ├── admin.amxx
    │       │   ├── admincmd.amxx
    │       │   ├── mapchooser.amxx
    │       │   ├── nextmap.amxx
    │       │   ├── chatlog.amxx      # Chat logger (monster logs)
    │       │   └── ... (50+ plugin)
    │       │
    │       ├── configs/              # Konfigürasyon dosyaları
    │       │   ├── amxx.cfg          # AMXModX ayarları
    │       │   ├── plugins.ini       # Plugin listesi
    │       │   ├── users.ini         # ✓ ADMIN LİSTESİ OLUŞTURULDU
    │       │   ├── maps.ini          # Map ayarları
    │       │   └── ... (diğer configler)
    │       │
    │       ├── logs/                 # Plugin logları
    │       │   ├── L0130001.log      # Plugin events (L + tarih)
    │       │   ├── error_20260130.log # Hata logları
    │       │   └── monster20260130.log # Chat logları
    │       │
    │       └── modules/              # AMX modülleri (.so)
    │
    ├── maps/                         # Oynanabilir haritalar
    │   ├── crossfire.bsp
    │   ├── bounce.bsp
    │   ├── bootbox.bsp
    │   └── ... (100+ map)
    │
    ├── sprites/                      # Sprite dosyaları
    ├── models/                       # Model dosyaları (.mdl)
    ├── sound/                        # Ses dosyaları (.wav)
    ├── events/                       # Event scriptleri
    ├── gfx/                          # Grafik dosyaları
    ├── resource/                     # Kaynak dosyaları
    │
    └── dlls/                         # Mod DLL'leri
        ├── ag.dll                    # AG Mod DLL
        └── ... (diğer DLL'ler)
```

---

## SCREEN SESSION YÖNETİMİ

### Session İsimlendirme

```
Format: agtr_[SERVER_ID]
Örnek: agtr_123
```

### Session Kontrolü

**Çalışan session'ları listeleme:**
```bash
screen -ls
# Çıktı:
# There are screens on:
#     12345.agtr_123  (Detached)
#     67890.agtr_124  (Detached)
```

**Belirli bir session'a attach olma:**
```bash
screen -r agtr_123
```

**Session'dan detach olma:**
```
Ctrl+A, D
```

### HLDS Process Yönetimi

**Process ID bulma:**
```bash
# Screen PID'yi al
screen_pid=$(pgrep -f "SCREEN.*agtr_123")

# HLDS child process'i bul (psutil ile)
hlds_pid=$(pgrep -P $screen_pid hlds_linux)
```

**Resource monitoring:**
```python
import psutil

process = psutil.Process(hlds_pid)
cpu_percent = process.cpu_percent()
memory_mb = process.memory_info().rss / 1024 / 1024
```

---

## PANEL ERİŞİMİ

### Public Panel URL

```
https://panel.agtrmerkezi.com
```

**Login Akışı:**

1. **Server Seçimi**
   - `GET /api/panel/servers`
   - Tüm panel_password'ü olan serverlar listelenir

2. **Panel Login**
   - Kullanıcı server seçer
   - Panel şifresini girer
   - `POST /api/panel/auth`

3. **Token Saklama**
   ```javascript
   localStorage.setItem('panel_token', token)
   localStorage.setItem('panel_server_id', server_id)
   localStorage.setItem('panel_mode', 'true')
   ```

4. **Panel Kullanımı**
   - Her API isteğinde `Authorization: Bearer [token]` header'ı gönderilir
   - Token 12 saat geçerli
   - Süre dolunca tekrar login gerekir

---

## DATABASE TABLOLARI

### game_servers

```sql
CREATE TABLE game_servers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    owner_id INT NOT NULL,
    owner_steam_id VARCHAR(50),
    name VARCHAR(100) NOT NULL,
    game_type ENUM('HLDM', 'AG', 'CS16'),
    ip_address VARCHAR(45) NOT NULL,
    port INT NOT NULL,
    slots INT NOT NULL,

    rcon_password VARCHAR(50),
    sv_password VARCHAR(50),
    panel_password VARCHAR(128),  -- Panel erişim şifresi

    unique_code VARCHAR(20) UNIQUE,  -- AGTR-2026-00001
    mod_type VARCHAR(20),  -- ag, ag_openag, cs16, hldm, valve_new

    status ENUM('PENDING', 'CREATING', 'INSTALLING', 'STOPPED',
                'RUNNING', 'SUSPENDED', 'EXPIRED', 'REJECTED',
                'DELETED') DEFAULT 'PENDING',

    current_map VARCHAR(64),
    current_players INT DEFAULT 0,
    max_players INT,

    process_pid INT,  -- HLDS process ID
    screen_name VARCHAR(50),  -- agtr_123

    auto_restart BOOLEAN DEFAULT TRUE,
    crash_count INT DEFAULT 0,
    last_crash DATETIME,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    last_started DATETIME,
    expires_at DATETIME,

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### server_installations

```sql
CREATE TABLE server_installations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    server_id INT NOT NULL,
    user_id INT NOT NULL,
    unique_code VARCHAR(20),

    status ENUM('PENDING', 'INSTALLING', 'COMPLETED',
                'FAILED', 'CANCELLED') DEFAULT 'PENDING',

    progress_percent INT DEFAULT 0,  -- 0-100
    current_step VARCHAR(200),
    total_steps INT DEFAULT 8,

    template_type VARCHAR(20),  -- ag, cs16, hldm, vb.
    error_message TEXT,

    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
```

### server_console_history

```sql
CREATE TABLE server_console_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    server_id INT NOT NULL,
    user_id INT,  -- NULL for panel users
    command TEXT NOT NULL,
    response TEXT,
    command_type ENUM('RCON', 'START', 'STOP', 'RESTART'),
    ip_address VARCHAR(45),
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (server_id) REFERENCES game_servers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
```

---

## ÖNEMLİ KONFİGÜRASYON DOSYALARI

### 1. server.cfg

**Lokasyon:** `/servers/server_123/ag/server.cfg`

**Önemli Ayarlar:**

```cfg
// ============================================
// TEMEL AYARLAR
// ============================================
hostname "Benim Serverim"
rcon_password "myRconPass"
sv_password "joinPass"  // Opsiyonel (boş = herkese açık)

// ============================================
// OYUNCU AYARLARI
// ============================================
maxplayers 32
sv_maxplayers 32
sv_visiblemaxplayers 32

// ============================================
// NETWORK AYARLARI (SABİT)
// ============================================
sys_ticrate 500  // Server tickrate
fps_max 600      // Max FPS
sv_maxrate 100000
sv_minrate 10000
sv_maxupdaterate 101
sv_minupdaterate 20

// ============================================
// AG MOD AYARLARI (AG serverlar için)
// ============================================
sv_ag_gamemode "2"  // 0=Normal, 1=CTF, 2=Arena
sv_ag_start_health "100"
sv_ag_start_armour "0"
sv_ag_start_longjump "1"
sv_ag_allow_vote "1"
sv_ag_vote_gamemode "1"
sv_ag_vote_map "1"

// ============================================
// DİĞER AYARLAR
// ============================================
sv_allowdownload "1"
sv_allowupload "1"
sv_lan "0"  // Internet server
```

### 2. users.ini (Admin List)

**Lokasyon:** `/servers/server_123/ag/addons/amxmodx/configs/users.ini`

**Format:**

```ini
; ============================================
; AGTR Merkezi - Auto-generated Admin List
; Server ID: 123
; Server Name: Benim Serverim
; Generated: 2026-01-30 12:00:00
; ============================================

; Format: "STEAM_ID" "password" "flags" "auth_type"
; Auth types: a = Steam ID, c = IP, d = Name

; ============================================
; SERVER OWNER (Auto-added)
; ============================================
"STEAM_0:1:12345678" "" "abcdefghijklmnopqrstu" "a"

; ============================================
; CUSTOM ADMINS
; ============================================
"STEAM_0:0:87654321" "admin_pass" "abcdefg" "ce"
"STEAM_0:1:11111111" "" "abc" "a"
```

**Flag Açıklamaları:**

| Flag | Yetki | Açıklama |
|------|-------|----------|
| `a` | immunity | Kick/ban edilemez |
| `b` | reservation | Reserved slot kullanabilir |
| `c` | amx_kick | Oyuncu atabilir |
| `d` | amx_ban | Ban atabilir |
| `e` | amx_slay | Oyuncu öldürebilir |
| `f` | amx_map | Map değiştirebilir |
| `g` | amx_cvar | Cvar değiştirebilir |
| `h` | amx_cfg | Config çalıştırabilir |
| `i` | amx_chat | Admin chat kullanabilir |
| `j` | amx_vote | Vote başlatabilir |
| `k` | amx_password | Server şifresi değiştirebilir |
| `l` | amx_rcon | RCON komutları |
| `m` | custom1 | Custom yetki 1 |
| ... | ... | ... |
| `t` | menu access | Admin menüsü |
| `u` | custom | Diğer yetkiler |

**Full Admin:** `abcdefghijklmnopqrstu` (tüm yetkiler)

### 3. plugins.ini

**Lokasyon:** `/servers/server_123/ag/addons/amxmodx/configs/plugins.ini`

**Örnek İçerik:**

```ini
; ============================================
; AMX Mod X Plugins
; ============================================

; Admin Base
admin.amxx
admincmd.amxx
adminhelp.amxx
adminslots.amxx
adminvote.amxx

; Maps
mapchooser.amxx
mapsmenu.amxx
nextmap.amxx

; Temel Özellikler
pausecfg.amxx
cmdmenu.amxx
plmenu.amxx
stats_logging.amxx

; Chat Logging (AGTR Panel için gerekli)
chatlog.amxx  ; monster*.log dosyası oluşturur

; Multilingual
multilingual.amxx

; Menu Front-End
menufront.amxx

; Commands Menu
cmdmenu.amxx

; Players Menu
plmenu.amxx

; Teleport Menu
teleportmenu.amxx

; Maps Menu
mapsmenu.amxx

; Config Menu
configmenu.amxx

; Spec Menu
specmenu.amxx

; Stats Configuration
stats.amxx
statscfg.amxx
```

### 4. mapcycle.txt

**Lokasyon:** `/servers/server_123/ag/mapcycle.txt`

**Örnek (AG Mod):**

```
crossfire
bounce
bootbox
gasworks
lostvillage
rapidcore
lambda_bunker
subtransit
datacore
```

**Örnek (CS 1.6):**

```
de_dust2
de_inferno
de_mirage
de_nuke
de_train
cs_office
cs_italy
```

---

## MONİTORİNG VE AUTO-RESTART

### Heartbeat System

**Servis:** Background task (Celery veya async scheduler)

**Kontrol Periyodu:** 30 saniye

**İşlem Akışı:**

```python
async def heartbeat_check():
    while True:
        # Tüm RUNNING serverları al
        running_servers = db.query(GameServer).filter(
            GameServer.status == ServerStatus.RUNNING
        ).all()

        for server in running_servers:
            # Screen session kontrol et
            is_alive = check_screen_session(f"agtr_{server.id}")

            if not is_alive:
                # Crash tespit edildi
                server.crash_count += 1
                server.last_crash = datetime.utcnow()

                # Auto-restart aktifse
                if server.auto_restart:
                    logger.warning(f"Server {server.id} crashed, restarting...")
                    await restart_server(server.id)
                else:
                    # Sadece durumu güncelle
                    server.status = ServerStatus.STOPPED

                db.commit()

        await asyncio.sleep(30)  # 30 saniye bekle
```

### Exponential Backoff (Crash Loop Prevention)

**Amaç:** Server sürekli crash oluyorsa, tekrar başlatma aralığını artır.

```python
if server.crash_count > 3:
    # Son 5 dakikada 3'ten fazla crash
    backoff_minutes = 2 ** min(server.crash_count - 3, 5)  # Max 32 dakika
    server.restart_backoff_until = datetime.utcnow() + timedelta(minutes=backoff_minutes)
    logger.error(f"Server {server.id} crash loop detected, backoff {backoff_minutes}m")
```

---

## ÖZET: SÜREÇ AKIŞ DİYAGRAMI

```
┌─────────────────────────────────────────────────────────────────┐
│ KULLANICI: "Yeni Server Oluştur" düğmesine tıklar              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ POST /api/v2/servers │
          │       /create        │
          └──────────┬───────────┘
                     │
        ┌────────────┴────────────┐
        │ Validasyon              │
        │ - Mod type kontrol      │
        │ - Slot bulma            │
        │ - Unique code oluştur   │
        └────────────┬────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Database Kayıt         │
        │ - GameServer (CREATING)│
        │ - ServerInstallation   │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Background Task Başlat │
        └────────────┬───────────┘
                     │
     ┌───────────────┴───────────────┐
     │ KURULUM SÜRECİ (8 Adım)      │
     └───────────────┬───────────────┘
                     │
        ┌────────────┴────────────┐
        │ Adım 1-2: Template Copy │
        │ Progress: 0% → 40%      │
        │ rsync ile dosya kopyala │
        └────────────┬────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Adım 3: server.cfg     │
        │ Progress: 45% → 50%    │
        │ Ayarları yapılandır    │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Adım 4: AMXModX        │
        │ Progress: 55% → 60%    │
        │ Framework hazır        │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Adım 5: users.ini      │
        │ Progress: 65% → 70%    │
        │ Admin listesi oluştur  │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Adım 6: start.sh       │
        │ Progress: 75% → 80%    │
        │ Scriptler oluştur      │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Adım 7: Doğrulama      │
        │ Progress: 85% → 90%    │
        │ Dosya kontrolü         │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Adım 8: Test Start     │
        │ Progress: 95% → 100%   │
        │ Başlat → Durdur        │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Status: STOPPED        │
        │ Kurulum tamamlandı!    │
        └────────────┬───────────┘
                     │
     ┌───────────────┴───────────────┐
     │ KULLANICI: "Başlat" düğmesi  │
     └───────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ POST /api/v2/servers/  │
        │    {id}/start          │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ ./start.sh çalıştır    │
        │ Screen session oluştur │
        │ agtr_123               │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ 30 saniye kontrol      │
        │ Screen session var mı? │
        └────────────┬───────────┘
                     │
            ┌────────┴────────┐
            │                 │
         EVET                HAYIR
            │                 │
            ▼                 ▼
    ┌───────────────┐  ┌──────────────┐
    │ PID al        │  │ Error return │
    │ Status=RUNNING│  │ Timeout      │
    └───────┬───────┘  └──────────────┘
            │
            ▼
    ┌───────────────────┐
    │ Server RUNNING!   │
    │ IP:PORT aktif     │
    │ Panel erişilebilir│
    └───────────────────┘
```

---

## SON NOTLAR

1. **Disk Optimizasyonu:**
   - Shared installation kullanılırsa server başına ~50MB
   - Full copy kullanılırsa server başına ~2.5GB

2. **Kurulum Süresi:**
   - Shared: ~20 saniye
   - Full copy: ~45 saniye
   - Mod tipine göre değişir (CS 1.6 daha büyük)

3. **Panel Token Süresi:**
   - 12 saat geçerli
   - Süre dolunca tekrar login gerekir

4. **Auto-Restart:**
   - Crash tespit edildiğinde otomatik başlar
   - Crash loop prevention (exponential backoff)

5. **Monitoring:**
   - 30 saniyede bir heartbeat
   - Resource tracking (CPU, RAM, Network)

---

**Dokümantasyon Sonu**
