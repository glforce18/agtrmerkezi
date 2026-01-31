# ✅ SHARED INSTALLATION SİSTEMİ - AKTİF

**Tarih:** 2026-01-30 23:18
**Status:** 🟢 PRODUCTION'DA AKTİF

---

## 🎯 TAMAMLANAN İŞLEMLER

### 1. SharedInstallationService Güncellemeleri ✅
- Tüm gerekli dosyalar eklendi (.so, .wad, liblist.gam, valve.rc)
- addons/ klasörü INDIVIDUAL olarak kopyalanıyor (metamod/amxmodx ayrımı)
- Startup scriptleri otomatik oluşturuluyor (start.sh, stop.sh)
- Test server_999 başarıyla çalıştırıldı

### 2. API Entegrasyonu ✅
- `/var/www/agtrmerkezi/app/api/server_v2.py` güncellendi
- `create_server` endpoint artık SharedInstallationService kullanıyor
- Eski ServerInstallationService yerine shared installation aktif
- Background task'lar güncellendi

### 3. Backend Restart ✅
- Service: `agtrmerkezi.service`
- Process ID: 2327837
- Port: 8000
- Status: ✅ RUNNING (23:17'de başlatıldı)
- Memory: 171 MB
- Startup: HATASIZ

---

## 📊 SİSTEM BİLGİLERİ

### Disk Tasarrufu
```
┌────────────────────────────────────────┐
│  ESKİ YÖNTEM:    839 MB/server         │
│  YENİ YÖNTEM:     58 MB/server         │
│  TASARRUF:       781 MB (%93.1)        │
└────────────────────────────────────────┘

100 Server Senaryosu:
- Eski: 83.9 GB
- Yeni:  7.7 GB (1.9 GB shared + 5.8 GB configs)
- Tasarruf: 76.2 GB
```

### Shared Base
- **Konum:** `/home/gameservers/shared/`
- **Boyut:** ~1.9 GB (TÜM serverlar paylaşıyor)
- **Modlar:** hlds_base, ag_base, cstrike_base, valve_base, valvenewvalve_base

### Per-Server
- **Konum:** `/home/gameservers/servers/server_XXX/`
- **Boyut:** ~58 MB
- **İçerik:**
  - 52 symlink (shared files)
  - 58 MB addons/ (metamod/amxmodx - INDIVIDUAL)
  - Config files (server.cfg, mapcycle.txt, vb.)
  - Startup scripts (start.sh, stop.sh)

---

## 🚀 KULLANIM

### API Üzerinden Yeni Server Oluşturma

Artık API'ye gönderilen tüm server oluşturma istekleri otomatik olarak shared installation kullanacak:

```bash
POST /api/servers/create
{
  "mod_type": "valve_new",
  "name": "Yeni Serverim",
  "maxplayers": 32,
  "port": 27015  # opsiyonel
}

# Response:
{
  "success": true,
  "server_id": 123,
  "message": "Sunucu olusturuldu, SHARED installation baslatildi (disk optimized - 58MB)"
}
```

### Desteklenen Modlar
- `ag` - Adrenaline Gamer
- `ag_openag` - OpenAG
- `cs16` - Counter-Strike 1.6
- `hldm` - Half-Life Deathmatch
- `valve_new` - Valve DM

### Background Installation Process
1. Server veritabanına kaydedilir (status: INSTALLING)
2. Background task shared installation başlatır
3. Symlink'ler oluşturulur (~5 saniye)
4. Config dosyaları hazırlanır
5. addons/ klasörü kopyalanır (metamod/amxmodx)
6. Startup scriptleri oluşturulur
7. Status STOPPED olarak güncellenir (hazır)

---

## ✅ BAŞARILI TEST

### Test Server: server_999
- **Mod:** valve_new (Half-Life DM)
- **Port:** 27999
- **Boyut:** 58 MB
- **Symlink:** 52 adet
- **Status:** ✅ RUNNING
- **Process:** screen session `agtr_999`

### Test Sonuçları
```bash
✅ Server başarıyla başlatıldı
✅ Metamod yüklendi (4 plugin)
✅ AMXModX çalışıyor
✅ JK_Botti yüklendi
✅ Loglar yazılıyor
✅ Port binding doğru (27999)
```

---

## 🔐 ÖNEMLİ NOTLAR

### Metamod/AMXModX Ayrımı
```
✅ Her server KENDİ addons/ klasörüne sahip (INDIVIDUAL)
✅ Her server KENDİ admin listesine sahip (users.ini)
✅ Her server KENDİ plugin ayarlarına sahip
✅ Loglar birbirine karışmaz (ayrı logs/ klasörleri)
✅ Her server bağımsız yapılandırılabilir
```

### Shared Dosyalar (Read-Only)
- HLDS binary'leri (.so files, hlds_linux)
- Mod dosyaları (models/, sound/, sprites/, dlls/)
- WAD dosyaları
- Linux libraries

User bu dosyaları değiştiremez (symlink). Değişiklik için server-specific kopya oluşturulmalı.

---

## 📈 PERSİSTENCE VE GÜNCELLEME

### Shared Base Güncelleme
```bash
# Template'leri shared base'e kopyala
rsync -av /templates/hlds/valve/ /home/gameservers/shared/valve_base/

# TÜM serverlar otomatik güncellenir (restart gerekebilir)
```

### Yedekleme Stratejisi
```bash
# 1. Shared base (tek seferlik)
tar -czf shared_base_backup.tar.gz /home/gameservers/shared/

# 2. Her server (sadece config + custom)
tar -czf server_123_backup.tar.gz /home/gameservers/servers/server_123/
```

---

## 🎮 BACKEND STATUS

### Service Bilgileri
- **Service:** agtrmerkezi.service
- **PID:** 2327837
- **Start Time:** 2026-01-30 23:17:58
- **Uptime:** Active
- **Memory:** 171 MB
- **Workers:** 1 (uvicorn)

### Restart Komutu
```bash
systemctl restart agtrmerkezi.service
systemctl status agtrmerkezi.service
```

### Log İzleme
```bash
journalctl -u agtrmerkezi.service -f
```

---

## 📋 SONRAKİ ADIMLAR

### Tamamlandı ✅
1. ✅ SharedInstallationService implementation
2. ✅ Test server_999 başarıyla çalıştırıldı
3. ✅ API entegrasyonu (server_v2.py)
4. ✅ Backend restart
5. ✅ Production'da aktif

### Opsiyonel (İhtiyaç Halinde)
- [ ] Mevcut serverlari shared installation'a migrate et
- [ ] Admin panel'e shared/full copy seçeneği ekle
- [ ] Monitoring: Shared installation disk kullanımı tracking
- [ ] Dokümantasyon: User guide for shared system

---

## 🎉 SONUÇ

**Shared Installation Sistemi Production'da Aktif ve Çalışıyor!**

Yeni oluşturulan tüm serverlar otomatik olarak:
- ✅ %93 daha az disk kullanacak (58 MB vs 839 MB)
- ✅ ~5 saniyede kurulacak
- ✅ Merkezi güncellemelerden faydalanacak
- ✅ Her server bağımsız config'e sahip olacak (metamod/amxmodx)

**API Endpoint:** `POST /api/servers/create`
**Backend Status:** 🟢 RUNNING
**Test Server:** server_999 (port 27999) 🟢 RUNNING

---

**Son Güncelleme:** 2026-01-30 23:18
**Sistem:** PRODUCTION READY ✅
