# 🔄 Shared Installation System - Update v2

**Tarih:** 2026-01-31 00:05
**Değişiklikler:** Steam dosyaları + Limit artışı

---

## 📊 YENİ YAPILANDIRMA

### Limit Değişikliği
```
ESKİ LİMİT:  250 MB/server
YENİ LİMİT:  400 MB/server  ✅
```

### Kopyalama Politikası Değişikliği

#### ÖNCEDEN (Symlink):
- .so dosyaları → Symlink
- hlds_linux, hlds_run → Symlink
- linux64/ → Symlink
- steamapps/ → Symlink
- valve_addon/ → Symlink

#### ŞİMDİ (Full Copy):
- .so dosyaları → **KOPYALA** ✅
- hlds_linux, hlds_run → **KOPYALA** ✅
- linux64/ → **KOPYALA** ✅
- steamapps/ → **KOPYALA** ✅
- valve_addon/ → **KOPYALA** ✅
- steam_appid.txt → **KOPYALA** ✅

**Neden?** Steam dosyaları için symlink sorun yaratabilir. Tam kopya daha güvenli.

---

## 📁 YENİ DOSYA YAPISI

### Shared (Symlink - Read Only)
```
Sadece mod içerik dosyaları:
- dlls/          (game binaries)
- cl_dlls/       (client)
- models/        (3D models)
- sound/         (ses dosyaları)
- sprites/       (2D grafikler)
- gfx/           (arayüz)
- events/        (event scripts)
- resource/      (kaynaklar)
```

### Individual (Full Copy - Read/Write)
```
HLDS Core (~50 MB):
- hlds_linux, hlds_run, hltv
- *.so (17 adet library)
- linux64/                   (~20 MB)
- steamapps/                 (~5 MB)
- valve_addon/               (~10 MB)

AMXModX/Metamod (~58 MB):
- addons/                    (metamod + amxmodx)

Maps (~100-200 MB):
- maps/                      (TÜM maplar)

Configs (~2 MB):
- server.cfg
- mapcycle.txt
- plugins.ini
- vb.
```

---

## 💾 SERVER BOYUT ANALİZİ

### Yeni Boyut Dağılımı (400 MB)
```
┌────────────────────────────────────────────┐
│  HLDS Binaries:      ~50 MB  (copied)      │
│  Steam Files:        ~35 MB  (copied)      │
│  AMXModX/Metamod:    ~58 MB  (copied)      │
│  Maps:             ~100-200 MB (copied)    │
│  Mod Content:       ~50 MB  (symlink)      │
│  Configs:            ~2 MB  (copied)       │
│  ──────────────────────────────────────    │
│  TOPLAM:          ~295-395 MB              │
└────────────────────────────────────────────┘
```

### Shared vs Individual Karşılaştırması
```
SHARED (Symlink):
- dlls, models, sound, sprites, etc.
- TOPLAM: ~50 MB shared content
- Tüm serverlar aynı dosyaları kullanır

INDIVIDUAL (Copied):
- HLDS binaries
- Steam files
- AMXModX/Metamod
- Maps
- Configs
- TOPLAM: ~300-350 MB per server
```

---

## 🎯 AVANTAJLAR

### Steam Uyumluluk ✅
- Steam dosyaları symlink değil, gerçek kopya
- Update sorunları yok
- Her server bağımsız Steam dosyalarına sahip

### AMXModX Bağımsızlık ✅
- Her server kendi plugin config'i
- Her server kendi admin listesi
- Her server kendi logları

### Map Esnekliği ✅
- Her server TÜM maplere sahip
- Custom map ekleme kolay
- Map rotasyonu bağımsız

### Sadece İçerik Paylaşılıyor ✅
- Models, sounds, sprites shared
- Değişmez içerik (read-only)
- Disk tasarrufu hala var (~50 MB/server)

---

## 🔧 PANEL STATUS FİX

### Sorun:
Panel'de serverlar offline gözüküyordu.

### Sebep:
Screen name uyuşmazlığı:
- Bizim: `agtr_8`, `agtr_9`
- Beklenen: `server_8`, `server_9`

### Çözüm:
```bash
# SharedInstallationService güncellendi
screen_name = f"server_{server_id}"  # Doğru format

# Mevcut serverlar yeniden başlatıldı
screen -ls:
  server_8  ✅
  server_9  ✅
```

**Artık panel ONLINE gösteriyor!** ✅

---

## 📝 DİKKAT EDİLECEKLER

### 1. Disk Kullanımı
- Eski sistem: ~60 MB/server
- Yeni sistem: ~300-350 MB/server
- Artış: ~240-290 MB/server
- **Ama Steam uyumluluk ve esneklik için gerekli!**

### 2. Yedekleme
- **Shared:** Sadece 1 kere yedekle (~2 GB)
- **Individual:** Her server'ı ayrı yedekle (~350 MB)

### 3. Güncelleme
```bash
# Shared content güncelleme (tüm serverlar için)
rsync -av /templates/hlds/valve/ /home/gameservers/shared/valve_base/

# Server restart gerekli
for i in 8 9; do
  screen -S server_$i -X quit
  cd /home/gameservers/servers/server_$i && ./start.sh
done
```

---

## 🚀 YENİ SERVER OLUŞTURMA

API'den oluşturulan yeni serverlar otomatik olarak:

✅ HLDS binaries kopyalanır (~50 MB)
✅ Steam files kopyalanır (~35 MB)
✅ AMXModX/Metamod kopyalanır (~58 MB)
✅ TÜM maplar kopyalanır (~100-200 MB)
✅ Mod content symlink (~50 MB shared)
✅ Screen name: `server_X` (panel uyumlu)
✅ Start.sh +ip +map parametreleriyle
✅ TOPLAM: ~300-350 MB

---

## 📊 100 SERVER PROJEKSİYONU

### Yeni Sistem:
```
Shared Base:     2 GB (tüm serverlar için)
Individual:    350 MB × 100 = 35 GB
────────────────────────────────────
TOPLAM:         37 GB

Eski Full Copy: 839 MB × 100 = 83.9 GB
TASARRUF:       46.9 GB (%56!)
```

Hala %56 tasarruf var! 🎉

---

## ✅ UYGULANAN DEĞİŞİKLİKLER

1. ✅ SharedInstallationService güncellendi
   - Steam files: symlink → copy
   - HLDS binaries: symlink → copy
   - Screen name: agtr_X → server_X

2. ✅ server_8 & server_9 güncellendi
   - start.sh screen name düzeltildi
   - Serverlar yeniden başlatıldı
   - Panel'de ONLINE ✅

3. ✅ Backend restart edildi
   - Yeni değişiklikler aktif
   - Plugin Manager v2 aktif
   - API güncel

---

**Son Güncelleme:** 2026-01-31 00:05
**Status:** 🟢 PRODUCTION ACTIVE
**Next:** Frontend Plugin Manager UI
