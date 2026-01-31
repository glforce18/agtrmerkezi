# ⚡ Quick Reference Checklist

**Hızlı Kontrol Listesi - Her Zaman Kontrol Et!**

---

## ✅ GAMESERVER OLUŞTURURKEN

```python
# 1. Port allocate
from app.services.port_manager import PortManager
port_mgr = PortManager()
ip, port = port_mgr.allocate_port()

# 2. GameServer create
server = GameServer(
    owner_id=current_user.id,
    name=data.server_name,
    game_type=package.game_type,
    mod_type=package.game_type,      # ⚠️ UNUTMA!
    ip_address=ip,                   # ⚠️ NULL OLMAMALI
    port=port,
    slots=package.slots,
    rcon_password=generate_rcon_password(),
    status=ServerStatus.PENDING,
    ...
)
db.add(server)
db.flush()  # ID almak için

# 3. Exception handling
try:
    db.commit()
except Exception as e:
    db.rollback()  # ⚠️ UNUTMA!
    raise
```

---

## ✅ OWNERSHIP VALIDATION

```python
# 1. Server query
server = db.query(GameServer).filter(GameServer.id == server_id).first()

# 2. NULL check
if not server:
    raise NotFoundError("Sunucu bulunamadı")

# 3. Validate
from app.api.common import validate_server_ownership
validate_server_ownership(server, current_user)  # ⚠️ (server, user)
```

---

## ✅ MOD_TYPE MAPPING

```python
# ⚠️ LOWERCASE KEYS!
mod_type_map = {
    "ag": "ag",              # ✅ lowercase
    "hldm": "valve_new",     # ✅ lowercase
    "cs16": "cs16",          # ✅ lowercase
}
mod_type = mod_type_map.get(server.game_type.value, "valve_new")
```

---

## ✅ SHARED INSTALLATION

```python
# 1. IP validation
server = db.query(GameServer).filter(GameServer.id == server_id).first()
server_ip = server.ip_address if server else None

if not server:
    return False, "Server not found"
if not server_ip:
    return False, "No IP address"  # ⚠️ NULL kontrolü

# 2. Screen name format
screen_name = f"server_{server_id}"  # ⚠️ "server_X" formatı

# 3. Mod folder
mod_folders = {
    "ag": "ag",
    "valve_new": "valve",
    "cs16": "cstrike",
}
mod_folder = mod_folders.get(mod_type, "valve")
```

---

## ✅ COPY vs SYMLINK

```python
import shutil
import os

# ⚠️ HLDS CORE - COPY (not symlink)
shutil.copy2(source, target)  # hlds_linux, hlds_run, *.so
shutil.copytree(source, target)  # linux64/, steamapps/, valve_addon/

# ⚠️ MOD CONTENT - SYMLINK (read-only)
os.symlink(source, target)  # dlls, models, sound, sprites

# ⚠️ MAPS & ADDONS - COPY (full)
shutil.copytree(maps_source, maps_target)  # TÜM maplar
shutil.copytree(addons_source, addons_target)  # AMXModX/Metamod
```

---

## ✅ RCON EXECUTE

```python
from app.services.rcon_service import RCONService

rcon_service = RCONService(db)

# Execute command
result = await rcon_service.execute(
    server,           # GameServer object ⚠️
    command,          # str
    current_user.id,  # int
    # command_type is optional (default: CommandType.RCON)
)

if result["success"]:
    # Command başarılı
    response = result["response"]
```

---

## ✅ ENUM DEĞERLER

```python
# GameType enum values (LOWERCASE!)
GameType.AG.value     # "ag"
GameType.HLDM.value   # "hldm"
GameType.CS16.value   # "cs16"

# ServerStatus enum values
ServerStatus.PENDING      # "pending"
ServerStatus.CREATING     # "creating"
ServerStatus.STOPPED      # "stopped"
ServerStatus.RUNNING      # "running"
```

---

## ✅ BACKEND RESTART

```bash
# Restart service
systemctl restart agtrmerkezi

# Check status
systemctl status agtrmerkezi

# View logs
journalctl -u agtrmerkezi -f
```

---

## ❌ YAPMA!

```python
# ❌ Uppercase enum keys
mod_map = {"AG": "ag"}  # YANLIŞ

# ❌ mod_type unutma
server = GameServer(game_type=x)  # YANLIŞ - mod_type eksik

# ❌ NULL IP
server = GameServer(ip_address=None)  # YANLIŞ

# ❌ Yanlış validation parametreleri
validate_server_ownership(db, id, user_id)  # YANLIŞ

# ❌ rollback unutma
except Exception:
    raise  # YANLIŞ - rollback yok

# ❌ Screen name formatı
screen_name = f"agtr_{id}"  # YANLIŞ - server_X olmalı

# ❌ HLDS files için symlink
os.symlink(hlds_linux, target)  # YANLIŞ - copy olmalı
```

---

## 📋 DATABASE FIELDS CHECKLIST

### GameServer oluştururken MUTLAKA:
- [x] owner_id
- [x] name
- [x] game_type
- [x] **mod_type** ⚠️ (game_type ile aynı)
- [x] **ip_address** ⚠️ (NULL değil)
- [x] port
- [x] slots
- [x] rcon_password
- [x] status
- [x] package_id
- [x] expires_at

---

**Şüphen varsa bu checklist'e bak!** ✅
