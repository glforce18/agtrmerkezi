# 🚀 SHARED INSTALLATION SİSTEMİ - TAMAMLANDI

**Tarih:** 2026-01-30
**Status:** ✅ TEST EDİLDİ VE ÇALIŞIYOR

---

## 📊 SONUÇLAR

### Disk Kullanımı Karşılaştırması

```
┌─────────────────────────────────────────────────────────┐
│                  FULL COPY vs SHARED                    │
├─────────────────────────────────────────────────────────┤
│  Full Copy (server_7):        839 MB                    │
│  Shared (server_999):          58 MB                    │
│  ─────────────────────────────────────────────────────  │
│  TASARRUF:                    781 MB (%93.1!)           │
└─────────────────────────────────────────────────────────┘

100 SERVER PROJEKSİYONU:
├─ Full Copy:  83.9 GB
├─ Shared:     7.7 GB (1.9 GB shared + 5.8 GB configs)
└─ Tasarruf:   76.2 GB (%90.8!)
```

### Test Server Bilgileri

- **Server ID:** 999
- **Mod:** valve_new (Half-Life Deathmatch)
- **Port:** 27999
- **Status:** ✅ ÇALIŞIYOR
- **Disk:** 58 MB

---

## 🏗️ YAPI

### Shared Base (Tek Kopya - Tüm Serverlar Paylaşıyor)

```
/home/gameservers/shared/
├── hlds_base/          52 MB
│   ├── hlds_linux, hlds_run, hltv
│   ├── *.so files (17 adet)
│   ├── linux64/, steamapps/
│   └── valve_addon/
│
├── ag_base/            350 MB
├── cstrike_base/       296 MB
├── valve_base/         768 MB
└── valvenewvalve_base/ 433 MB

TOPLAM: ~1.9 GB (tüm serverlar için TEK KOPYA)
```

### Server Klasörü (Her Server için ~58 MB)

```
/home/gameservers/servers/server_999/
│
├── SYMLINK'LER (Shared - 52 adet):
│   ├── hlds_linux → shared/hlds_base/
│   ├── *.so files → shared/hlds_base/
│   └── valve/
│       ├── dlls/ → shared/valve_base/dlls/
│       ├── cl_dlls/ → shared/valve_base/cl_dlls/
│       ├── models/ → shared/valve_base/models/
│       ├── sound/ → shared/valve_base/sound/
│       ├── sprites/ → shared/valve_base/sprites/
│       ├── gfx/ → shared/valve_base/gfx/
│       ├── events/ → shared/valve_base/events/
│       ├── resource/ → shared/valve_base/resource/
│       └── *.wad files → shared/valve_base/
│
└── INDIVIDUAL (Her Server Farklı - 58 MB):
    ├── start.sh, stop.sh (server-specific)
    └── valve/
        ├── server.cfg ✏️ (hostname, rcon, port)
        ├── mapcycle.txt ✏️
        ├── liblist.gam ✏️ (metamod config)
        ├── valve.rc ✏️
        ├── addons/ ✏️ (58 MB - metamod/amxmodx)
        │   ├── amxmodx/
        │   │   ├── configs/
        │   │   │   └── users.ini (admin list)
        │   │   └── logs/ (her server kendi logları)
        │   ├── metamod/
        │   └── ... (diğer pluginler)
        ├── maps/ ✏️ (custom maps)
        ├── demos/ ✏️ (demo kayıtları)
        └── logs/ ✏️ (server logs)
```

---

## ✅ ÖNEMLİ: AMXModX/Metamod Ayrımı

```
✅ Her server KENDİ metamod/amxmodx config'ine sahip!
✅ Her server KENDİ admin listesine sahip (users.ini)!
✅ Her server KENDİ plugin ayarlarına sahip!
✅ Loglar karışmaz - her server kendi logs/ klasöründe!

addons/ klasörü SHARED DEĞİL, INDIVIDUAL!
```

---

## 🔧 SharedInstallationService Özellikleri

### Otomatik Symlink Oluşturma

- HLDS core files (hlds_linux, *.so)
- Mod klasörleri (dlls, models, sound, sprites, vb.)
- WAD dosyaları (*.wad)
- Config templates

### Otomatik Kopyalama

- server.cfg (yapılandırılmış)
- mapcycle.txt, motd.txt, banned.cfg
- liblist.gam (metamod için)
- valve.rc
- **addons/** klasörü (metamod/amxmodx) - TAM KOPYA
- start.sh, stop.sh scriptleri

### Otomatik Yapılandırma

- server.cfg'de hostname, rcon_password, port ayarları
- start.sh'de server-specific port ve maxplayers

---

## 📝 Kullanım

### Yeni Server Oluşturma

```python
from app.services.shared_installation_service import SharedInstallationService

service = SharedInstallationService(db)

success, msg = await service.create_server_with_symlinks(
    server_id=123,
    mod_type="valve_new",  # ag, cs16, hldm, valve_new
    hostname="Benim Serverim",
    rcon_password="rcon123",
    port=27015,
    maxplayers=32
)

# Result: ~58 MB server (vs 839 MB full copy)
```

### Desteklenen Modlar

```python
MOD_MAP = {
    "ag": "ag_base",              # Adrenaline Gamer
    "ag_openag": "ag_base",       # OpenAG
    "cs16": "cstrike_base",       # Counter-Strike 1.6
    "hldm": "valve_base",         # Half-Life Deathmatch
    "valve_new": "valve_base",    # Valve DM (new)
}
```

---

## 🎯 Avantajlar

1. **%93 Disk Tasarrufu** (839 MB → 58 MB)
2. **Hızlı Kurulum** (~5 saniye vs ~30 saniye)
3. **Tek Noktadan Güncelleme**
   - Shared base'i güncelleyince TÜM serverlar güncellenir
4. **Her Server Ayrı Config**
   - AMXModX/Metamod configs ayrı
   - Admin lists ayrı
   - Loglar karışmaz
5. **Kolay Yedekleme**
   - Shared base: 1 kere yedefle (~2 GB)
   - Her server: Sadece config + custom files (~58 MB)

---

## ⚠️ Notlar

1. **addons/** klasörü 58 MB
   - Metamod + AMXModX pluginleri
   - Her server için FARKLI olmalı (individual)

2. **Shared dosyalar read-only**
   - User shared dosyaları değiştiremez
   - Değişiklik yapmak isterse kopyala

3. **Template güncelleme:**
   ```bash
   # Shared base'i güncelle
   rsync -av /templates/hlds/valve/ /shared/valve_base/

   # TÜM serverlar otomatik güncellendi! (restart gerekebilir)
   ```

---

## 🚀 Sonraki Adımlar

1. ✅ Shared installation service tamamlandı
2. ✅ Test edildi ve çalışıyor
3. ⏳ Server API'ye entegre et (`server_v2.py`)
4. ⏳ Mevcut serverlari migrate et
5. ⏳ Admin panel'e shared/full copy seçeneği ekle

---

**Son Güncelleme:** 2026-01-30 23:06
**Test Server:** server_999 (port 27999) - ✅ RUNNING
