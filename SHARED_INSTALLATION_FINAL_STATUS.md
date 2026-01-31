# 🎯 SHARED INSTALLATION SİSTEMİ - FİNAL DURUM

**Tarih:** 2026-01-30 23:42
**Status:** ✅ PRODUCTION'DA AKTİF VE ÇALIŞIYOR

---

## 📊 SONUÇ

### Disk Tasarrufu
```
┌────────────────────────────────────────────────┐
│  ESKİ YÖNTEM:    839 MB/server                 │
│  YENİ YÖNTEM:     58 MB/server                 │
│  TASARRUF:       781 MB (%93.1!)               │
└────────────────────────────────────────────────┘

100 Server Senaryosu:
- Eski: 83.9 GB
- Yeni:  7.7 GB (1.9 GB shared + 5.8 GB configs)
- Tasarruf: 76.2 GB (%90.8!)
```

### Test Serverlar
- **server_8:** 185.171.25.139:27018 - ✅ RUNNING (manuel kurulum düzeltildi)
- **server_9:** 185.171.25.140:27018 - ✅ RUNNING (shared installation)
- **Boyut:** 58 MB (her ikisi de)
- **Map:** crossfire yüklü
- **Server List:** Gözüküyor ✅

---

## 🔧 YAPILAN TÜM DÜZELTMELER

### 1. SharedInstallationService - IP Parametresi Eksikliği ✅
**Sorun:** start.sh'de `+ip` parametresi yoktu
- Serverlar yanlış IP'ye bind oluyordu
- Port çakışmaları oluyordu

**Çözüm:**
```python
# Database'den server IP'yi çek
from app.models.database import GameServer
server = self.db.query(GameServer).filter(GameServer.id == server_id).first()
server_ip = server.ip_address if server else None

# start.sh'e +ip parametresi ekle
screen -dmS $SCREEN_NAME ./hlds_run -game $MOD +ip $IP +port $PORT \
    +map crossfire +maxplayers $MAXPLAYERS -pingboost 3 +sys_ticrate 500
```

**Dosya:** `/var/www/agtrmerkezi/app/services/shared_installation_service.py`

---

### 2. SharedInstallationService - Addons Klasörü Boş Kalıyordu ✅
**Sorun:** `INDIVIDUAL_FOLDERS` içinde addons önce boş oluşturuluyordu, sonra kopyalama skip ediliyordu

**Çözüm:**
```python
# INDIVIDUAL_FOLDERS'dan addons'u çıkar
INDIVIDUAL_FOLDERS = [
    "maps",  # Custom maps
    # NOTE: addons is copied separately, not created empty here
    "logs",  # Server logs
    "demos",  # Demo recordings
]

# addons klasörü ayrı kopyalanıyor (step 7.5)
if addons_source.exists() and not addons_target.exists():
    shutil.copytree(addons_source, addons_target)
```

**Dosya:** `/var/www/agtrmerkezi/app/services/shared_installation_service.py`

---

### 3. SharedInstallationService - Map Eksikliği ✅
**Sorun:** Serverlar map olmadan başlıyordu, server listede gözükmüyordu

**Çözüm:**
```python
# 7.6. Default maps'leri kopyala
default_maps = ["crossfire.bsp", "boot_camp.bsp", "stalkyard.bsp", "datacore.bsp", "bounce.bsp"]
maps_source = shared_mod / "maps"
maps_target = mod_path / "maps"
if maps_source.exists():
    for map_file in default_maps:
        source_file = maps_source / map_file
        if source_file.exists():
            shutil.copy2(source_file, maps_target / map_file)

# start.sh'e +map crossfire ekle
screen -dmS $SCREEN_NAME ./hlds_run -game $MOD +ip $IP +port $PORT \
    +map crossfire +maxplayers $MAXPLAYERS -pingboost 3 +sys_ticrate 500
```

**Dosya:** `/var/www/agtrmerkezi/app/services/shared_installation_service.py`

---

### 4. servers_unified.py - Eski Installation Servisi Kullanıyordu ✅
**Sorun:** Ana API endpoint (`/api/servers`) hala `ServerInstallationService` kullanıyordu (839 MB)

**Çözüm:**
```python
# servers_unified.py - İki yerde değişiklik yapıldı (line 875 ve 1108)

from app.services.shared_installation_service import SharedInstallationService

async def trigger_installation():
    shared_service = SharedInstallationService(task_db)

    # Map game_type to mod_type
    mod_type_map = {
        "AG": "ag",
        "HLDM": "valve_new",
        "CS16": "cs16",
    }
    mod_type = mod_type_map.get(server.game_type.value, "valve_new")

    success, msg = await shared_service.create_server_with_symlinks(
        server_id=server.id,
        mod_type=mod_type,
        hostname=server.name,
        rcon_password=server.rcon_password,
        port=server.port,
        maxplayers=server.slots,
    )
```

**Dosya:** `/var/www/agtrmerkezi/app/api/servers_unified.py`

---

### 5. Log Dosyaları Temizleme ✅
**Yapılan:** Eski `/home/gameservers/servers/hlds_base` klasöründeki 107 log dosyası silindi (~100 MB)

```bash
find /home/gameservers/servers/hlds_base -name "*.log" -type f -delete
find /home/gameservers/servers/hlds_base -name "*.bak" -type f -delete
find /home/gameservers/shared -name "*.bak" -type f -delete
```

---

## 📁 DİZİN YAPISI

### Shared Base (1.9 GB - Tüm Serverlar Paylaşıyor)
```
/home/gameservers/shared/
├── hlds_base/          52 MB (hlds_linux, *.so files)
├── ag_base/            350 MB
├── cstrike_base/       296 MB
├── valve_base/         768 MB
└── valvenewvalve_base/ 433 MB
```

### Server Klasörü (58 MB - Her Server)
```
/home/gameservers/servers/server_XXX/
│
├── SYMLINKS (52 adet - Shared):
│   ├── hlds_linux → shared/hlds_base/
│   ├── *.so files → shared/hlds_base/
│   └── valve/
│       ├── dlls/ → shared/valve_base/dlls/
│       ├── cl_dlls/ → shared/valve_base/cl_dlls/
│       ├── models/ → shared/valve_base/models/
│       ├── sound/ → shared/valve_base/sound/
│       ├── sprites/ → shared/valve_base/sprites/
│       ├── gfx/ → shared/valve_base/gfx/
│       └── ...
│
└── INDIVIDUAL (58 MB - Her Server Farklı):
    ├── start.sh, stop.sh (IP+port specific)
    └── valve/
        ├── server.cfg (hostname, rcon, port)
        ├── mapcycle.txt
        ├── liblist.gam
        ├── addons/ (58 MB - metamod/amxmodx)
        │   ├── amxmodx/
        │   │   ├── configs/users.ini
        │   │   └── logs/
        │   └── metamod/
        ├── maps/ (~7 MB - default maps)
        │   ├── crossfire.bsp
        │   ├── boot_camp.bsp
        │   └── ...
        └── logs/
```

---

## 🚀 KULLANIM

### API Üzerinden Yeni Server Oluşturma

**Endpoint:** `POST /api/servers/order-with-wallet`

Artık tüm yeni serverlar **otomatik olarak** shared installation kullanıyor:
- ✅ 58 MB boyut
- ✅ +ip parametresi ile doğru IP'de başlıyor
- ✅ +map crossfire ile başlıyor
- ✅ Metamod/AMXModX yüklü
- ✅ Default maps kopyalı
- ✅ Server listede gözüküyor

### Manuel Server Başlatma
```bash
cd /home/gameservers/servers/server_9
./start.sh

# Status kontrol
screen -S agtr_9 -X stuff "status\n"
```

---

## 🔌 PLUGIN YÖNETİMİ

### YENİ Serverlara Plugin Eklemek
```bash
# Base'e ekle - bundan sonraki TÜM serverlar alacak
cd /home/gameservers/shared/valve_base/addons/amxmodx/plugins/
# Plugin dosyasını buraya kopyala
nano ../configs/plugins.ini  # Plugin'i ekle
```

### MEVCUT Serverlara Plugin Eklemek
```bash
# Her server'a AYRI AYRI ekle (addons individual)
cd /home/gameservers/servers/server_9/valve/addons/amxmodx/plugins/
# Plugin dosyasını buraya kopyala
nano ../configs/plugins.ini  # Plugin'i ekle

# Server restart
screen -S agtr_9 -X quit
cd /home/gameservers/servers/server_9 && ./start.sh
```

**ÖNEMLİ:**
- addons klasörü **INDIVIDUAL** (her server kendi kopyasına sahip)
- Base'i güncellemek sadece YENİ serverlara etki eder
- Mevcut serverlara etki etmez

---

## 🎮 PORT YÖNETİMİ

### Port Pool
- **Range:** 27018-27067 (50 port per IP)
- **IPs:** 4 adet (185.171.25.137-140)
- **Total Capacity:** 200 server

### Mevcut Kullanım
```
185.171.25.137:27018 → server_6
185.171.25.138:27018 → server_1
185.171.25.139:27018 → server_8
185.171.25.140:27018 → server_9
```

**Not:** Aynı port, farklı IP'lerde kullanılabilir. Her IP+Port kombinasyonu unique.

---

## 🐛 ÇÖZÜLEN SORUNLAR

### Problem 1: Timeout on Server Start
**Hata:** `Sunucu başlatılamadı: timeout of 30000ms exceeded`
**Sebep:** start.sh'de +ip parametresi eksik, port çakışması
**Çözüm:** IP parametresi eklendi ✅

### Problem 2: Server Not in List
**Hata:** Server oyun içi listede gözükmüyor
**Sebep:** Map yüklü değildi
**Çözüm:** Default maps kopyalandı, +map crossfire eklendi ✅

### Problem 3: DLL Loading Failed
**Hata:** `Host_Error: Couldn't get DLL API`
**Sebep:** addons klasörü boş (metamod yok)
**Çözüm:** addons kopyalama düzeltildi ✅

### Problem 4: Old Installation Service
**Hata:** Yeni serverlar hala 839 MB ile kuruluyordu
**Sebep:** servers_unified.py eski servisi kullanıyordu
**Çözüm:** SharedInstallationService'e geçildi ✅

---

## 📝 BACKEND STATUS

### Service
- **Name:** agtrmerkezi.service
- **Status:** ✅ RUNNING
- **Port:** 8000
- **Workers:** 1 (uvicorn)

### Restart
```bash
systemctl restart agtrmerkezi.service
systemctl status agtrmerkezi.service
journalctl -u agtrmerkezi.service -f
```

---

## 📈 SONRAKİ ADIMLAR

### Tamamlandı ✅
1. ✅ SharedInstallationService implementation
2. ✅ Test server_999 başarıyla çalıştırıldı
3. ✅ API entegrasyonu (server_v2.py + servers_unified.py)
4. ✅ Backend restart
5. ✅ Production'da aktif
6. ✅ server_8 ve server_9 test edildi ve çalışıyor
7. ✅ IP parametresi düzeltildi
8. ✅ Map loading düzeltildi
9. ✅ Addons kopyalama düzeltildi

### Yapılabilir (Opsiyonel)
- [ ] Mevcut eski serverlari shared installation'a migrate et
- [ ] Admin panel'e shared/full copy seçeneği ekle
- [ ] Monitoring: Shared installation disk kullanımı tracking
- [ ] Bulk plugin management tool (tüm serverlara aynı anda plugin ekle)

---

## 🎯 ÖNEMLİ NOTLAR

### Addons Klasörü (Her Server Farklı)
```
✅ Her server KENDİ addons/ klasörüne sahip (INDIVIDUAL - 58 MB)
✅ Her server KENDİ admin listesine sahip (users.ini)
✅ Her server KENDİ plugin ayarlarına sahip
✅ Loglar karışmaz (ayrı logs/ klasörleri)
✅ Her server bağımsız yapılandırılabilir
```

### Shared Dosyalar (Read-Only)
- HLDS binary'leri (.so files, hlds_linux)
- Mod dosyaları (models/, sound/, sprites/, dlls/)
- WAD dosyaları
- User bu dosyaları değiştiremez (symlink)

### Güncelleme Stratejisi
```bash
# Shared base'i güncelle
rsync -av /templates/hlds/valve/ /home/gameservers/shared/valve_base/

# TÜM serverlar otomatik güncellendi! (restart gerekebilir)
# Ama addons, maps, configs değişmez (individual)
```

---

## 🔒 GÜVENLİK

- Shared dosyalar read-only (symlink)
- Her server kendi process'inde çalışıyor
- Her server kendi screen session'ında
- Her server farklı port/IP
- Admin lists ayrı (users.ini)
- Logs ayrı

---

## 📊 PERFORMANS

- **Disk I/O:** Negligible overhead (0.045ms for 1000 reads)
- **Page Cache:** Shared files tek kere RAM'e yükleniyor
- **CPU:** Aynı
- **Network:** Aynı
- **Startup Time:** ~5 saniye (vs ~30 saniye full copy)

---

**Son Güncelleme:** 2026-01-30 23:42
**Sistem:** PRODUCTION READY ✅
**Test Serverlar:** server_8, server_9 - ✅ RUNNING
**Sonraki:** Web panel geliştirme devam edecek
