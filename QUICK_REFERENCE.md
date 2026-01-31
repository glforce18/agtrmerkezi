# ⚡ SHARED INSTALLATION - QUICK REFERENCE

## 🎯 Özet
- **Eski Sistem:** 839 MB/server
- **Yeni Sistem:** 58 MB/server
- **Tasarruf:** %93.1
- **Status:** ✅ PRODUCTION AKTİF

---

## 📁 Klasör Yapısı

### Shared (Read-Only)
```
/home/gameservers/shared/
├── hlds_base/     # Binaries (symlink)
├── valve_base/    # Mod files (symlink)
└── ...
```

### Individual (Read-Write)
```
/home/gameservers/servers/server_XXX/
├── start.sh       # IP+port specific
└── valve/
    ├── server.cfg    # Config
    ├── addons/       # 58 MB (FARKLI)
    ├── maps/         # Custom maps
    └── logs/         # Logs
```

---

## 🔌 Plugin Ekleme

### Yeni Serverlara
```bash
# Base'e ekle
cd /home/gameservers/shared/valve_base/addons/amxmodx/plugins/
# Plugin kopyala + plugins.ini düzenle
```

### Mevcut Serverlara
```bash
# Her server'a AYRI ekle
cd /home/gameservers/servers/server_9/valve/addons/amxmodx/plugins/
# Plugin kopyala + plugins.ini düzenle
screen -S agtr_9 -X quit && cd ../../ && ./start.sh
```

---

## 🚀 Server Yönetimi

### Başlat
```bash
cd /home/gameservers/servers/server_9
./start.sh
```

### Durdur
```bash
screen -S agtr_9 -X quit
# veya
cd /home/gameservers/servers/server_9
./stop.sh
```

### Konsol
```bash
screen -r agtr_9
# Çıkmak: Ctrl+A, D
```

### Status
```bash
screen -S agtr_9 -X stuff "status\n"
screen -S agtr_9 -X hardcopy /tmp/status.txt
cat /tmp/status.txt
```

---

## 🔧 Backend

### Restart
```bash
systemctl restart agtrmerkezi.service
```

### Logs
```bash
journalctl -u agtrmerkezi.service -f
```

### Status
```bash
systemctl status agtrmerkezi.service
```

---

## 📝 Önemli Dosyalar

### SharedInstallationService
```
/var/www/agtrmerkezi/app/services/shared_installation_service.py
```

### API Endpoints
```
/var/www/agtrmerkezi/app/api/servers_unified.py
/var/www/agtrmerkezi/app/api/server_v2.py
```

### Dokümantasyon
```
/var/www/agtrmerkezi/SHARED_INSTALLATION_FINAL_STATUS.md
/var/www/agtrmerkezi/SHARED_INSTALLATION_COMPLETE.md
/var/www/agtrmerkezi/SHARED_SYSTEM_ACTIVE.md
```

---

## ⚠️ Hatırlatmalar

1. **addons INDIVIDUAL** - Base değişikliği mevcut serverlara etki etmez
2. **maps INDIVIDUAL** - Her server kendi custom map'lerine sahip
3. **IP parametresi gerekli** - start.sh'de +ip olmalı
4. **Map gerekli** - +map crossfire olmalı (server listede gözükmesi için)
5. **Port range** - 27018-27067 (50 port/IP)

---

## 🎮 Test Serverlar

- **server_8:** 185.171.25.139:27018 ✅
- **server_9:** 185.171.25.140:27018 ✅
- **Boyut:** 58 MB
- **Map:** crossfire

---

**Tarih:** 2026-01-30 23:42
**Status:** ✅ READY
