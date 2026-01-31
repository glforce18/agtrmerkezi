# 🎯 AGTR Merkezi - Complete System Reference

**Tarih:** 2026-01-31 00:32
**Versiyon:** v6.1 (Shared Installation + Bug Fixes)
**Durum:** 🟢 PRODUCTION

---

## 📋 İÇİNDEKİLER

1. [Sistem Mimarisi](#sistem-mimarisi)
2. [Database Schema](#database-schema)
3. [API Endpoints](#api-endpoints)
4. [Shared Installation System](#shared-installation-system)
5. [Düzeltilen Kritik Buglar](#düzeltilen-kritik-buglar)
6. [Common Pitfalls (SAKININ!)](#common-pitfalls)
7. [Port Management](#port-management)
8. [File Structure](#file-structure)

---

## 1️⃣ SISTEM MIMARİSİ

### Tech Stack
```
Backend:  FastAPI (Python 3.13)
Database: PostgreSQL
Frontend: React
ORM:      SQLAlchemy
Server:   Uvicorn
```

### Ana Servisler
```python
# API Layer
/var/www/agtrmerkezi/app/api/
├── servers_unified.py     # Server CRUD, order, management
├── plugin_manager.py      # Plugin management v2
├── common.py             # Validation helpers

# Service Layer
/var/www/agtrmerkezi/app/services/
├── shared_installation_service.py   # Server installation (SHARED)
├── server_control.py               # Start/stop/status
├── rcon_service.py                 # RCON commands
├── plugin_manager_service.py       # Plugin operations
├── port_manager.py                 # Port allocation

# Models
/var/www/agtrmerkezi/app/models/
├── database.py           # All database models
└── connection.py         # DB session management
```

---

## 2️⃣ DATABASE SCHEMA

### GameServer Model
**Tablo:** `game_servers`
**Önemli Fieldlar:**

```python
class GameServer(Base):
    id: int                          # Primary key
    owner_id: int                    # FK -> users.id
    name: str                        # Server hostname
    game_type: GameType             # Enum: "ag", "hldm", "cs16"
    mod_type: GameType              # ⚠️ AYNI DEĞER (game_type ile)
    ip_address: str                 # ⚠️ NULL OLMAMALI
    port: int                       # 27015-27050 arası
    slots: int                      # Max players
    rcon_password: str              # RCON şifresi
    status: ServerStatus            # "pending", "stopped", "running"
    package_id: int                 # FK -> server_packages.id
    expires_at: datetime            # Bitiş tarihi

    # Relations
    owner: User
    package: ServerPackage
```

### ⚠️ KRİTİK FIELD NOTLARI

#### mod_type
```python
# ✅ DOĞRU - GameServer oluştururken MUTLAKA set et
server = GameServer(
    game_type=package.game_type,
    mod_type=package.game_type,  # ⚠️ UNUTMA!
    ...
)

# ❌ YANLIŞ - mod_type NULL kalır
server = GameServer(
    game_type=package.game_type,
    # mod_type yok ❌
    ...
)
```

#### ip_address
```python
# ✅ DOĞRU - Port ayırırken IP mutlaka set edilmeli
from app.services.port_manager import PortManager
port_mgr = PortManager()
ip, port = port_mgr.allocate_port()

server = GameServer(
    ip_address=ip,  # ⚠️ NULL OLMAMALI
    port=port,
    ...
)

# ❌ YANLIŞ - NULL IP bash script'i bozar
server = GameServer(
    ip_address=None,  # ❌ IP="None" olur bash'te
    ...
)
```

### GameType Enum
```python
class GameType(enum.Enum):
    HLDM = "hldm"   # ⚠️ LOWERCASE
    AG = "ag"       # ⚠️ LOWERCASE
    CS16 = "cs16"   # ⚠️ LOWERCASE

# Kullanım:
server.game_type.value  # Returns: "ag" (lowercase)
```

### ServerStatus Enum
```python
class ServerStatus(enum.Enum):
    PENDING = "pending"        # Yeni oluşturuldu, kurulum bekliyor
    CREATING = "creating"      # Kurulum yapılıyor
    INSTALLING = "installing"  # Dosyalar kopyalanıyor
    STOPPED = "stopped"        # Kurulum tamamlandı, kapalı
    RUNNING = "running"        # Aktif çalışıyor
    FAILED = "failed"         # Kurulum başarısız
```

### UserPlugin Model
**Tablo:** `user_plugins`

```python
class UserPlugin(Base):
    id: int
    user_id: int              # FK -> users.id
    server_id: int            # FK -> game_servers.id
    filename: str             # plugin.amxx
    size: int                 # Bytes
    uploaded_at: datetime

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("user_id", "server_id", "filename"),
    )
```

---

## 3️⃣ API ENDPOINTS

### Server Management

#### POST `/api/servers/order/package`
**Kredi kartı ile server siparişi**

Request:
```json
{
  "package_id": 1,
  "server_name": "My Server",
  "duration": 1,
  "auto_renew": true
}
```

Önemli Kod Blokları:
```python
# 1. Port allocation
ip, port = port_manager.allocate_port()

# 2. GameServer creation
server = GameServer(
    owner_id=current_user.id,
    name=data.server_name,
    game_type=package.game_type,
    mod_type=package.game_type,      # ⚠️ UNUTMA
    ip_address=ip,                   # ⚠️ NULL OLMAMALI
    port=port,
    ...
)

# 3. Background installation
background_tasks.add_task(trigger_installation)

# 4. Installation içinde mod_type mapping
mod_type_map = {
    "ag": "ag",              # ⚠️ LOWERCASE keys
    "hldm": "valve_new",
    "cs16": "cs16",
}
mod_type = mod_type_map.get(server.game_type.value, "valve_new")
```

#### POST `/api/servers/order/package-wallet`
**Bakiye ile server siparişi**

Aynı mantık, sadece ödeme bakiyeden düşülür:
```python
# Bakiye kontrolü
if current_user.balance_coin < total_price:
    raise BadRequestError("Yetersiz bakiye")

# Bakiyeden düş
current_user.balance_coin -= total_price
```

#### POST `/api/servers/{server_id}/start`
**Server başlat**

```python
# 1. Ownership validation
server = db.query(GameServer).filter(GameServer.id == server_id).first()
if not server:
    raise NotFoundError("Sunucu bulunamadı")
validate_server_ownership(server, current_user)

# 2. Start server
control_service = ServerControlService(db)
success = await control_service.start_server(server_id)

# 3. Update database status
if success:
    server.status = ServerStatus.RUNNING
    db.commit()
```

#### POST `/api/servers/{server_id}/stop`
**Server durdur**

```python
# Stop işlemi
await control_service.stop_server(server_id)
server.status = ServerStatus.STOPPED
db.commit()
```

#### PUT `/api/servers/{server_id}/settings`
**Server ayarlarını güncelle**

```python
# ⚠️ DOĞRU ownership validation
server = db.query(GameServer).filter(GameServer.id == server_id).first()
if not server:
    raise NotFoundError("Sunucu bulunamadı")
validate_server_ownership(server, current_user)  # ⚠️ (server, user) parametreleri

# RCON ile ayar değiştir
rcon_service = RCONService(db)
result = await rcon_service.execute(
    server,                    # GameServer object
    f'hostname "{new_name}"',  # Command
    current_user.id,          # User ID
    # command_type optional (default: CommandType.RCON)
)
```

### ⚠️ VALIDATION FUNCTIONS

```python
# common.py içinde

def validate_server_ownership(server: GameServer, user: User) -> bool:
    """
    ⚠️ DİKKAT: Parametre sırası!

    Args:
        server: GameServer object (NOT server_id!)
        user: User object (NOT user_id!)

    Returns:
        True veya ForbiddenError raise eder
    """
    if server.owner_id != user.id and not user.is_admin:
        raise ForbiddenError("Bu sunucuya erişim yetkiniz yok")
    return True

# ✅ DOĞRU KULLANIM:
server = db.query(GameServer).filter(GameServer.id == server_id).first()
if not server:
    raise NotFoundError("Sunucu bulunamadı")
validate_server_ownership(server, current_user)

# ❌ YANLIŞ KULLANIM:
validate_server_ownership(db, server_id, current_user.id)  # ❌ TypeError!
```

---

## 4️⃣ SHARED INSTALLATION SYSTEM

### Dizin Yapısı

```
/home/gameservers/
├── shared/                      # Shared templates (1.9 GB total)
│   ├── hlds_base/              # Core HLDS binaries (52 MB)
│   │   ├── hlds_linux
│   │   ├── hlds_run
│   │   ├── *.so (17 files)
│   │   ├── linux64/
│   │   └── steamapps/
│   ├── ag_base/                # AG mod content (350 MB)
│   ├── valve_base/             # HLDM content (767 MB)
│   ├── cstrike_base/           # CS 1.6 content (296 MB)
│   └── valvenewvalve_base/     # New valve (433 MB)
│
└── servers/                     # Individual servers
    ├── server_1/               # ~300-350 MB per server
    │   ├── hlds_linux          # COPIED from shared (not symlink)
    │   ├── hlds_run            # COPIED
    │   ├── *.so                # COPIED (17 files)
    │   ├── linux64/            # COPIED
    │   ├── steamapps/          # COPIED
    │   ├── valve_addon/        # COPIED
    │   ├── start.sh
    │   ├── stop.sh
    │   └── valve/              # or ag/ or cstrike/
    │       ├── dlls -> /home/gameservers/shared/valve_base/dlls  # SYMLINK
    │       ├── models -> .../valve_base/models                    # SYMLINK
    │       ├── sound -> .../valve_base/sound                      # SYMLINK
    │       ├── sprites -> .../valve_base/sprites                  # SYMLINK
    │       ├── addons/         # COPIED - Individual plugins
    │       ├── maps/           # COPIED - All maps
    │       ├── server.cfg      # COPIED - Individual config
    │       └── mapcycle.txt    # COPIED
    │
    └── server_2/
        └── ...
```

### SharedInstallationService

**File:** `/var/www/agtrmerkezi/app/services/shared_installation_service.py`

#### Önemli Constants

```python
class SharedInstallationService:
    SHARED_BASE = "/home/gameservers/shared"
    SERVERS_BASE = "/home/gameservers/servers"

    # Symlink yapılacak klasörler (read-only shared content)
    SHARED_FOLDERS = [
        "dlls",      # Mod binaries
        "cl_dlls",   # Client DLLs
        "sprites",   # Sprites
        "models",    # Models
        "sound",     # Sounds
        "gfx",       # Graphics
        "events",    # Events
        "resource",  # Resources
    ]

    # Individual klasörler (her server kendi kopyası)
    INDIVIDUAL_FOLDERS = [
        "logs",   # Server logs
        "demos",  # Demo recordings
        # NOT: maps ve addons artık burada değil!
        # maps -> step 7.6'da FULL COPY
        # addons -> step 7.5'te FULL COPY
    ]

    # Individual dosyalar
    INDIVIDUAL_FILES = [
        "server.cfg",
        "mapcycle.txt",
        "motd.txt",
        "banned.cfg",
        "listip.cfg",
        "liblist.gam",
        "valve.rc",
    ]
```

#### Önemli Metodlar

```python
def get_mod_folder(self, mod_type: str) -> str:
    """
    Mod klasör adını döndür

    ⚠️ Bu method eklendi bug fix sırasında!
    """
    mod_folders = {
        "ag": "ag",
        "valve_new": "valve",
        "cs16": "cstrike",
    }
    return mod_folders.get(mod_type, "valve")

async def create_server_with_symlinks(
    self,
    server_id: int,
    mod_type: str,
    hostname: str,
    rcon_password: str,
    port: int,
    maxplayers: int = 32,
) -> Tuple[bool, str]:
    """
    Server oluştur (shared files + symlinks)

    ⚠️ ÖNEMLI NOKTALAR:
    """
    # 1. IP validation (bug fix)
    server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
    server_ip = server.ip_address if server else None

    if not server:
        return False, f"Server {server_id} not found in database"
    if not server_ip:
        return False, f"Server {server_id} has no IP address assigned"

    # 2. Mod folder mapping
    mod_folder = self.get_mod_folder(mod_type)

    # 3. Copy HLDS binaries (NOT symlink!)
    # .so files, hlds_linux, hlds_run -> COPY
    # linux64/, steamapps/, valve_addon/ -> COPY

    # 4. Copy ALL maps (NOT just 5!)
    # TÜM .bsp dosyaları kopyalanır

    # 5. Copy addons FULL (NOT empty!)
    # AMXModX/Metamod tam kopya

    # 6. Create symlinks for shared content
    # dlls, models, sound, sprites -> SYMLINK

    # 7. Create startup scripts
    self._create_startup_scripts(server_id, mod_folder, server_ip, port, maxplayers)
```

#### Startup Script Template

```bash
#!/bin/bash
SERVER_DIR="/home/gameservers/servers/server_{id}"
SCREEN_NAME="server_{id}"          # ⚠️ FORMAT: server_X (panel uyumlu)
MOD="{mod_folder}"                 # ag, valve, cstrike
IP="{server_ip}"                   # ⚠️ NULL OLMAMALI
PORT={port}
MAXPLAYERS={maxplayers}

cd "$SERVER_DIR"

# Stop existing
screen -S $SCREEN_NAME -X quit 2>/dev/null

# Start server
screen -dmS $SCREEN_NAME ./hlds_run -game $MOD +ip $IP +port $PORT \
    +map crossfire +maxplayers $MAXPLAYERS -pingboost 3 +sys_ticrate 500

echo "Server started in screen session: $SCREEN_NAME"
```

### Disk Kullanımı

```
PER SERVER:
├── HLDS binaries:    ~50 MB  (copied)
├── Steam files:      ~35 MB  (copied)
├── AMXModX/Metamod:  ~58 MB  (copied)
├── Maps:          ~100-200 MB (copied)
├── Mod content:     ~50 MB  (symlink - shared)
├── Configs:          ~2 MB  (copied)
└── TOTAL:        ~300-350 MB

100 SERVER:
├── Shared base:       2 GB   (one copy for all)
├── Individual:       35 GB   (350 MB × 100)
└── TOTAL:            37 GB
```

---

## 5️⃣ DÜZELTİLEN KRİTİK BUGLAR

### Bug #1: mod_type Mapping Keys
**Lokasyon:** `servers_unified.py` lines 886-891, 1120-1125

```python
# ❌ YANLIŞ
mod_type_map = {
    "AG": "ag",         # ❌ Uppercase
    "HLDM": "valve_new",
    "CS16": "cs16",
}

# ✅ DOĞRU
mod_type_map = {
    "ag": "ag",         # ✅ Lowercase (enum değerleri ile match)
    "hldm": "valve_new",
    "cs16": "cs16",
}
mod_type = mod_type_map.get(server.game_type.value, "valve_new")
```

**Sebep:** `GameType.AG.value` returns `"ag"` (lowercase)

---

### Bug #2: Eksik mod_type Field
**Lokasyon:** `servers_unified.py` lines 802-819, 1028-1045

```python
# ❌ YANLIŞ
server = GameServer(
    game_type=package.game_type,
    # mod_type eksik!
    ...
)

# ✅ DOĞRU
server = GameServer(
    game_type=package.game_type,
    mod_type=package.game_type,  # ⚠️ Eklendi
    ...
)
```

---

### Bug #3: validate_server_ownership Yanlış Çağrı
**Lokasyon:** `servers_unified.py` line 1409

```python
# ❌ YANLIŞ
server = validate_server_ownership(db, server_id, current_user.id)

# ✅ DOĞRU
server = db.query(GameServer).filter(GameServer.id == server_id).first()
if not server:
    raise NotFoundError("Sunucu bulunamadı")
validate_server_ownership(server, current_user)
```

**Function signature:**
```python
def validate_server_ownership(server: GameServer, user: User) -> bool:
    # Takes objects, not IDs!
```

---

### Bug #4: Eksik db.rollback()
**Lokasyon:** `servers_unified.py` line 960

```python
# ❌ YANLIŞ
except Exception as e:
    log_api_error("order_server", e, current_user.id)
    raise HTTPException(status_code=500, detail=str(e))

# ✅ DOĞRU
except Exception as e:
    db.rollback()  # ⚠️ Eklendi
    log_api_error("order_server", e, current_user.id)
    raise HTTPException(status_code=500, detail=str(e))
```

---

### Bug #5: Eksik get_mod_folder() Method
**Lokasyon:** `shared_installation_service.py` line 605

```python
# ❌ HATA: Method yoktu
mod_folder = service.get_mod_folder(server.mod_type)  # AttributeError!

# ✅ FIX: Method eklendi
def get_mod_folder(self, mod_type: str) -> str:
    """Mod klasör adını döndür"""
    mod_folders = {
        "ag": "ag",
        "valve_new": "valve",
        "cs16": "cstrike",
    }
    return mod_folders.get(mod_type, "valve")
```

---

### Bug #6: NULL server_ip Risk
**Lokasyon:** `shared_installation_service.py` line 224

```python
# ❌ YANLIŞ
server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
server_ip = server.ip_address if server else None
# Sonra bash: IP="None" ❌

# ✅ DOĞRU - Validation eklendi
server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
server_ip = server.ip_address if server else None

if not server:
    return False, f"Server {server_id} not found in database"
if not server_ip:
    return False, f"Server {server_id} has no IP address assigned"
```

---

## 6️⃣ COMMON PITFALLS (SAKININ!)

### ❌ Pitfall 1: Enum Keys Uppercase
```python
# ❌ YANLIŞ
mapping = {"AG": "ag", "HLDM": "valve"}
value = mapping[server.game_type.value]  # KeyError!

# ✅ DOĞRU
mapping = {"ag": "ag", "hldm": "valve"}
value = mapping[server.game_type.value]  # ✅ Works
```

### ❌ Pitfall 2: mod_type Unutmak
```python
# ❌ YANLIŞ - Installation fail olur
server = GameServer(
    game_type=GameType.AG,
    # mod_type yok!
)

# ✅ DOĞRU
server = GameServer(
    game_type=GameType.AG,
    mod_type=GameType.AG,  # ⚠️ ALWAYS SET!
)
```

### ❌ Pitfall 3: NULL IP
```python
# ❌ YANLIŞ - Bash script: IP="None"
server = GameServer(
    ip_address=None,  # ❌ Bash bozulur
)

# ✅ DOĞRU - Port manager kullan
ip, port = PortManager().allocate_port()
server = GameServer(
    ip_address=ip,  # ✅ Valid IP
    port=port,
)
```

### ❌ Pitfall 4: Validation Function Yanlış Parametreler
```python
# ❌ YANLIŞ
server = validate_server_ownership(db, server_id, user_id)

# ✅ DOĞRU
server = db.query(GameServer).filter_by(id=server_id).first()
if not server:
    raise NotFoundError("Sunucu bulunamadı")
validate_server_ownership(server, current_user)
```

### ❌ Pitfall 5: Exception'da rollback Unutmak
```python
# ❌ YANLIŞ
try:
    db.add(server)
    db.commit()
except Exception as e:
    raise  # ❌ Transaction açık kalır!

# ✅ DOĞRU
try:
    db.add(server)
    db.commit()
except Exception as e:
    db.rollback()  # ✅ Transaction temizlendi
    raise
```

### ❌ Pitfall 6: Screen Name Format
```python
# ❌ YANLIŞ - Panel bulamaz
screen_name = f"agtr_{server_id}"

# ✅ DOĞRU - Panel uyumlu
screen_name = f"server_{server_id}"
```

### ❌ Pitfall 7: Symlink vs Copy Karışması
```python
# ⚠️ STEAM FILES - COPY (not symlink)
# hlds_linux, hlds_run, *.so, linux64/, steamapps/
shutil.copy2(source, target)  # ✅ COPY

# ⚠️ MOD CONTENT - SYMLINK (read-only)
# dlls, models, sound, sprites
os.symlink(source, target)  # ✅ SYMLINK
```

---

## 7️⃣ PORT MANAGEMENT

### Port Range
```python
# IP Pool
IPS = [
    "185.171.25.140",
    "185.171.25.150",
    "185.171.25.160",
]

# Port Range
PORT_MIN = 27015
PORT_MAX = 27050  # 36 ports per IP
```

### PortManager Usage
```python
from app.services.port_manager import PortManager

# Allocate port
port_mgr = PortManager()
ip, port = port_mgr.allocate_port()

# Creates server with:
# - IP from available IPs
# - Port from 27015-27050
# - Load balanced across IPs
```

---

## 8️⃣ FILE STRUCTURE

### Önemli Dosyalar

```
/var/www/agtrmerkezi/
├── app/
│   ├── main.py                    # FastAPI app entry
│   ├── api/
│   │   ├── servers_unified.py     # ⚠️ Server endpoints
│   │   ├── plugin_manager.py      # Plugin management v2
│   │   └── common.py              # ⚠️ Validation helpers
│   ├── services/
│   │   ├── shared_installation_service.py  # ⚠️ Installation
│   │   ├── server_control.py               # Start/stop
│   │   ├── rcon_service.py                 # RCON
│   │   ├── port_manager.py                 # Ports
│   │   └── plugin_manager_service.py       # Plugins
│   └── models/
│       ├── database.py            # ⚠️ All models
│       └── connection.py          # DB session
│
├── SYSTEM_REFERENCE_COMPLETE.md  # ⚠️ THIS FILE
├── SERVER_CREATION_BUGFIXES.md   # Bug fixes detail
├── SHARED_SYSTEM_UPDATE_V2.md    # V2 update notes
└── PLUGIN_MANAGER_API.md         # Plugin API docs
```

### Systemd Service
```bash
# Service file
/etc/systemd/system/agtrmerkezi.service

# Commands
systemctl restart agtrmerkezi
systemctl status agtrmerkezi
systemctl logs -f agtrmerkezi
```

---

## 🎯 QUICK CHECKLIST

### Yeni Server Oluşturma
- [ ] Port allocate et (`PortManager`)
- [ ] GameServer create et
  - [ ] `game_type` set et
  - [ ] `mod_type` set et (AYNI DEĞER)
  - [ ] `ip_address` set et (NULL OLMAMALI)
  - [ ] `port` set et
- [ ] mod_type mapping doğru (lowercase keys)
- [ ] Background task ile install et
- [ ] Exception'da `db.rollback()`

### Server Validation
- [ ] Server query yap
- [ ] NULL check yap
- [ ] `validate_server_ownership(server, user)` çağır (DOĞRU PARAMETRELER)

### Installation
- [ ] IP validation yap (NULL değil mi?)
- [ ] mod_folder mapping doğru mu?
- [ ] HLDS files COPY (not symlink)
- [ ] Mod content SYMLINK (not copy)
- [ ] Screen name format: `server_X`

---

**Son Güncelleme:** 2026-01-31 00:32
**Status:** 🟢 PRODUCTION READY
**Next Step:** Admin Panel Development
