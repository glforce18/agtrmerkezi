# 🚀 Shared Game Files Implementation Guide

## 📊 Disk Kullanımı Karşılaştırması

### Mevcut Sistem (Full Copy)
```
Template (her sunucu için):
- Half-Life AG:     2.5 GB
- Counter-Strike:   2.8 GB
- Half-Life DM:     2.2 GB

10 Sunucu Senaryosu:
- 5 AG + 3 CS + 2 HLDM
- Toplam: (5×2.5) + (3×2.8) + (2×2.2) = 25.4 GB
```

### Yeni Sistem (Shared Files)
```
Shared Base (tek kopya):
- hlds_base:      1.8 GB
- ag_base:        0.7 GB
- cstrike_base:   1.0 GB
- valve_base:     0.4 GB
- Toplam Shared:  3.9 GB

Her Sunucu (individual files):
- Config dosyaları:    ~5 MB
- Custom maps:         ~20 MB
- Plugins (AMXModX):   ~10 MB
- Logs:               ~5 MB
- Toplam Per Server:  ~40-50 MB

10 Sunucu Senaryosu:
- Shared: 3.9 GB
- 10 Sunucu: 10 × 0.05 GB = 0.5 GB
- TOPLAM: 4.4 GB

🎯 TASARRUF: 25.4 GB → 4.4 GB = %82.7 tasarruf!
```

## 🏗️ Dosya Yapısı

### Shared Base (Read-Only)
```
/home/gameservers/shared/
├── hlds_base/
│   ├── hlds_linux              # Main binary
│   ├── hlds_run               # Startup script
│   └── libsteam.so            # Steam libraries
├── ag_base/
│   ├── dlls/                  # Mod binaries
│   ├── cl_dlls/               # Client DLLs
│   ├── sprites/               # Sprites
│   ├── models/                # Models
│   ├── sound/                 # Sounds
│   ├── maps/                  # Standard maps
│   ├── server.cfg.template    # Template config
│   └── mapcycle.txt.template
├── cstrike_base/
│   ├── dlls/
│   ├── models/
│   ├── sprites/
│   ├── sound/
│   └── maps/
└── valve_base/
    ├── dlls/
    ├── models/
    └── ...
```

### Per-Server (Individual)
```
/home/gameservers/servers/server_1/
├── hlds_linux -> ../../shared/hlds_base/hlds_linux  (symlink)
├── hlds_run -> ../../shared/hlds_base/hlds_run
└── ag/
    ├── dlls -> ../../shared/ag_base/dlls           (symlink)
    ├── cl_dlls -> ../../shared/ag_base/cl_dlls
    ├── sprites -> ../../shared/ag_base/sprites
    ├── models -> ../../shared/ag_base/models
    ├── sound -> ../../shared/ag_base/sound
    ├── server.cfg              # ✅ Individual config
    ├── mapcycle.txt           # ✅ Individual
    ├── banned.cfg             # ✅ Individual
    ├── listip.cfg             # ✅ Individual
    ├── maps/                  # ✅ Custom maps only
    │   └── ag_crossfire2.bsp
    ├── addons/                # ✅ Custom plugins
    │   ├── amxmodx/
    │   └── metamod/
    ├── logs/                  # ✅ Server logs
    └── demos/                 # ✅ Demo recordings
```

## 🔧 Implementasyon Adımları

### 1. Shared Base Hazırlama (İlk Kurulum - Bir Kere)

```bash
# Shared klasörü oluştur
mkdir -p /home/gameservers/shared

# Template'lerden shared base oluştur
cd /home/gameservers/templates/hlds

# AG
rsync -av ag/ /home/gameservers/shared/ag_base/

# CS 1.6
rsync -av cstrike/ /home/gameservers/shared/cstrike_base/

# HL DM
rsync -av valve/ /home/gameservers/shared/valve_base/

# HLDS binaries (core files)
mkdir -p /home/gameservers/shared/hlds_base
cp hlds_linux hlds_run libsteam.so /home/gameservers/shared/hlds_base/

# Read-only yap (güvenlik)
chmod -R 555 /home/gameservers/shared
```

### 2. Yeni Sunucu Oluşturma

```python
from app.services.shared_installation_service import SharedInstallationService

service = SharedInstallationService(db)

# Yeni sunucu oluştur (symlink'lerle)
success, message = await service.create_server_with_symlinks(
    server_id=123,
    mod_type="ag",
    hostname="AGTR Merkezi Test Server",
    rcon_password="secret123",
    port=27015,
    maxplayers=32
)

# Sonuç: ~50MB sunucu oluşturuldu (2.5GB yerine!)
```

### 3. Mevcut Sunucuları Migrate Etme

```python
from app.services.shared_installation_service import migrate_existing_server_to_shared

# Mevcut sunucuyu shared yapıya çevir
success, message = await migrate_existing_server_to_shared(
    server_id=123,
    db=db
)

# Custom maps/plugins korunur, sadece yapı değişir
```

## 📈 Performans Etkileri

### Kurulum Hızı
- **Mevcut:** 2.5GB kopyalama = ~60 saniye
- **Yeni:** Symlink oluşturma + 50MB = ~3 saniye
- **İyileştirme:** 20x daha hızlı!

### Çalışma Performansı
- **Symlink overhead:** Yok (Linux kernel seviyesinde)
- **I/O performansı:** Aynı (dosya okuma aynı hız)
- **CPU/RAM:** Etkilenmez

### Güncelleme/Patch
- **Mevcut:** Her sunucuyu ayrı patch = N × süre
- **Yeni:** Sadece shared base'i patch = 1 × süre
- **Örnek:** 10 sunucu için 10x daha hızlı güncelleme!

## 🛡️ Güvenlik Özellikleri

### 1. Shared Files Read-Only
```bash
# Shared dosyalar read-only
chmod -R 555 /home/gameservers/shared

# Sunucular sadece okuyabilir, değiştiremez
# Exploit/hack shared files'a zarar veremez
```

### 2. Individual Logs
```
Her sunucu kendi log klasöründe:
- server_1/ag/logs/
- server_2/cstrike/logs/

Birbirini etkilemez
```

### 3. Custom Content İzolasyonu
```
Custom maps/plugins her sunucu için ayrı:
- server_1/ag/maps/custom_map.bsp
- server_2/ag/maps/different_map.bsp

Çakışma olmaz
```

## 🔍 Monitoring & Maintenance

### Disk Kullanımı İzleme

```python
# API endpoint
@router.get("/api/admin/disk-usage")
async def get_disk_usage(db: Session = Depends(get_db)):
    service = SharedInstallationService(db)
    stats = service.get_disk_usage_stats()

    return {
        "shared_total_mb": 3900,
        "per_server_avg_mb": 45,
        "total_servers": 10,
        "total_used_mb": 4350,
        "saved_vs_full_copy_mb": 21050,
        "efficiency_percent": 82.9
    }
```

### Health Check

```python
def check_shared_integrity():
    """Shared base dosyalarının bütünlüğünü kontrol et"""
    shared_base = Path("/home/gameservers/shared")

    critical_files = [
        "hlds_base/hlds_linux",
        "ag_base/dlls/ag.so",
        "cstrike_base/dlls/cs.so"
    ]

    for file_path in critical_files:
        if not (shared_base / file_path).exists():
            return False, f"Missing critical file: {file_path}"

    return True, "All shared files OK"
```

## 📋 Migration Checklist

### Hazırlık
- [ ] Shared base klasörleri oluşturuldu
- [ ] Template'ler shared base'e kopyalandı
- [ ] Permissions ayarlandı (read-only)
- [ ] Test sunucusu ile doğrulandı

### Existing Sunucuları Migrate Et
- [ ] Yedekleme yapıldı
- [ ] Custom maps/plugins listelendi
- [ ] Migration script test edildi
- [ ] Sırayla her sunucu migrate edildi
- [ ] Fonksiyonellik test edildi

### Monitoring
- [ ] Disk kullanım monitoring eklendi
- [ ] Alert sistemi kuruldu
- [ ] Backup stratejisi güncellendi

## 🎯 Best Practices

### 1. Shared Base Güncellemeleri
```bash
# Güncelleme öncesi yedek
cp -a /home/gameservers/shared/ag_base /backup/ag_base_$(date +%Y%m%d)

# Güncelleme
rsync -av /path/to/new/ag/ /home/gameservers/shared/ag_base/

# Test sunucusunda kontrol
systemctl restart test-server

# Sorun yoksa tüm sunucuları restart
for server in server_*; do
    systemctl restart $server
done
```

### 2. Disaster Recovery
```bash
# Shared base corrupt olursa:
# 1. Yedekten geri yükle
rsync -av /backup/ag_base_20260129/ /home/gameservers/shared/ag_base/

# 2. Permissions düzelt
chmod -R 555 /home/gameservers/shared/ag_base/

# 3. Sunucuları restart et
systemctl restart server-*
```

### 3. New Game Version
```bash
# Yeni AG versiyonu için:
# 1. Yeni shared base oluştur
mkdir /home/gameservers/shared/ag_base_v7

# 2. Kopyala
rsync -av /path/to/ag_v7/ /home/gameservers/shared/ag_base_v7/

# 3. Test sunucusunu yeni versiyona geçir
rm /home/gameservers/servers/test_server/ag/dlls
ln -s ../../shared/ag_base_v7/dlls /home/gameservers/servers/test_server/ag/dlls

# 4. Test OK ise diğerlerini de geçir
```

## 💡 Pro Tips

### 1. Cache Warming
```bash
# Shared files'ı RAM'e cache'le (daha hızlı)
cat /home/gameservers/shared/ag_base/dlls/ag.so > /dev/null
```

### 2. Monitoring Script
```bash
#!/bin/bash
# check_shared.sh

SHARED_BASE="/home/gameservers/shared"
ALERT_EMAIL="admin@agtrmerkezi.com"

# Check if shared files are accessible
if [ ! -r "$SHARED_BASE/ag_base/dlls/ag.so" ]; then
    echo "CRITICAL: Shared files not accessible" | mail -s "AGTR Alert" $ALERT_EMAIL
fi

# Check disk usage
USAGE=$(df -h $SHARED_BASE | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $USAGE -gt 90 ]; then
    echo "WARNING: Disk usage at ${USAGE}%" | mail -s "AGTR Disk Alert" $ALERT_EMAIL
fi
```

### 3. Automated Backup
```bash
#!/bin/bash
# backup_shared.sh - Daily cron job

BACKUP_DIR="/backup/shared"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Incremental backup (sadece değişiklikleri)
rsync -av --link-dest=$BACKUP_DIR/latest \
    /home/gameservers/shared/ \
    $BACKUP_DIR/$DATE/

ln -sfn $BACKUP_DIR/$DATE $BACKUP_DIR/latest

# 7 günden eski yedekleri sil
find $BACKUP_DIR -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;
```

## 🚀 Özet

### Avantajlar
✅ %82+ disk tasarrufu
✅ 20x daha hızlı sunucu kurulumu
✅ Tek seferde güncelleme (tüm sunucular için)
✅ Daha kolay yönetim
✅ Backup boyutları küçülür

### Dezavantajlar
⚠️ İlk kurulum biraz karmaşık
⚠️ Shared files bozulursa tüm sunucular etkilenir (backup önemli)
⚠️ Symlink desteği gerekli (Linux/Unix)

### Sonuç
**Kesinlikle tavsiye edilir!** Production sistemlerde yaygın kullanılır.

## 📞 Support

Sorularınız için: support@agtrmerkezi.com
