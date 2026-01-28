# AGTR Merkezi v6.0 - Features Documentation

## 🎯 Overview

AGTR Merkezi v6.0, Half-Life ve Counter-Strike 1.6 sunucu yönetimi için kapsamlı bir platform sunar. Bu versiyon, 5 yeni gelişmiş özellik ile sunucu yöneticilerine güçlü araçlar sağlar.

---

## 🔑 Core Features

### 1. Auto Admin System
**Otomatik Sahip Admin Sistemi**

#### Ne Yapar?
Sunucu satın alındığında veya oluşturulduğunda, sunucu sahibi otomatik olarak tam yetkili admin olarak eklenir.

#### Özellikler
- ✅ Otomatik admin ekleme (sunucu kurulumunda)
- ✅ Tam yetki (abcdefghijklmnopqrstu flags)
- ✅ Steam ID tabanlı tanımlama
- ✅ users.ini otomatik güncelleme
- ✅ Manuel senkronizasyon seçeneği

#### Kullanım

**Otomatik (Sunucu Kurulumu):**
```python
# ServerInstallationService içinde otomatik çalışır
amxx_service.add_owner_as_admin(server_id, owner_id)
```

**Manuel Senkronizasyon:**
```bash
POST /api/v2/servers/{server_id}/admins/sync-owner
Authorization: Bearer {token}
```

**Yanıt:**
```json
{
  "success": true,
  "message": "Sahip otomatik olarak admin eklendi"
}
```

#### Güvenlik
- Sadece sunucu sahibi manuel sync yapabilir
- Duplicate kontrolü (zaten adminse tekrar eklenmez)
- Tüm işlemler loglanır

---

### 2. Scheduler - Zamanlanmış Görevler
**Cron-Style Server Task Scheduling**

#### Ne Yapar?
Sunucu görevlerini otomatik olarak zamanlamanıza olanak tanır. Günlük restart, harita değişimi, yedekleme gibi işlemleri otomatikleştirir.

#### Görev Tipleri

1. **RESTART** - Sunucu yeniden başlatma
2. **MAP_CHANGE** - Harita değiştirme
3. **BACKUP** - Yedekleme oluşturma
4. **ANNOUNCEMENT** - Duyuru mesajı gönderme
5. **RCON_COMMAND** - Özel RCON komutu çalıştırma

#### Zamanlama Modları

**1. Cron (Belirli Saatlerde)**
```json
{
  "schedule_type": "cron",
  "cron_minute": "0",
  "cron_hour": "3",
  "cron_day": "*",
  "cron_month": "*",
  "cron_day_of_week": "*"
}
```
Örnek: Her gün saat 03:00'da

**2. Interval (Her X Saatte)**
```json
{
  "schedule_type": "interval",
  "interval_value": 6,
  "interval_unit": "hours"
}
```
Örnek: Her 6 saatte bir

**3. One-Time (Tek Sefer)**
```json
{
  "schedule_type": "one_time",
  "scheduled_time": "2025-01-26T15:30:00"
}
```
Örnek: 26 Ocak 2025, 15:30'da

#### Görev Örnekleri

**Günlük Restart:**
```json
{
  "task_name": "Günlük Sabah Restart",
  "task_type": "restart",
  "schedule_type": "cron",
  "cron_minute": "0",
  "cron_hour": "6",
  "is_enabled": true
}
```

**Harita Rotasyonu:**
```json
{
  "task_name": "Akşam Harita Değişimi",
  "task_type": "map_change",
  "schedule_type": "cron",
  "cron_minute": "0",
  "cron_hour": "20",
  "task_config": {
    "map": "de_dust2"
  },
  "is_enabled": true
}
```

**Otomatik Yedekleme:**
```json
{
  "task_name": "Haftalık Backup",
  "task_type": "backup",
  "schedule_type": "cron",
  "cron_day_of_week": "0",
  "cron_hour": "2",
  "is_enabled": true
}
```

#### UI Özellikleri
- Cron expression builder
- Visual task list
- Enable/disable toggle
- Execution history viewer
- Next run time display
- Status badges (success, failed, skipped)

#### Execution Tracking
Her görev çalıştırması kaydedilir:
- Çalıştırma zamanı
- Durum (success, failed, skipped)
- Sonuç mesajı
- Execution time (ms)

---

### 3. Advanced Statistics Dashboard
**Gelişmiş İstatistik ve Görselleştirme**

#### Ne Yapar?
Sunucu performansını ve oyuncu aktivitesini görselleştirir. Trend analizi, peak hours tespiti ve oyuncu sadakati ölçümü sağlar.

#### Veri Tipleri

**1. Hourly Stats (Saatlik)**
- Ortalama oyuncu sayısı
- Maksimum oyuncu sayısı
- Benzersiz oyuncu sayısı
- En çok oynanan harita

**2. Daily Stats (Günlük)**
- Toplam oyuncu sayısı
- Ortalama oturum süresi
- Peak hour (en yoğun saat)
- Harita playtime dağılımı

**3. Weekly Stats (Haftalık)**
- Retention rate (geri dönüş oranı)
- Yeni vs. dönen oyuncular
- Toplam playtime (saat)

#### Görselleştirmeler

**1. Player Count Trend (Line Chart)**
```javascript
// Son 24 saat veya 30 gün
{
  labels: ['00:00', '01:00', '02:00', ...],
  datasets: [
    {
      label: 'Ortalama Oyuncu',
      data: [5.2, 3.8, 2.1, ...]
    },
    {
      label: 'Max Oyuncu',
      data: [12, 8, 5, ...]
    }
  ]
}
```

**2. Peak Hours Heatmap (24x7 Grid)**
```
        Pzt  Sal  Çar  Per  Cum  Cmt  Paz
00:00 │ 2.5  1.8  2.0  3.2  4.5  6.8  5.2
01:00 │ 1.2  0.8  1.1  1.5  2.3  4.2  3.8
...
23:00 │ 8.5  7.2  8.9  9.5  12.3 15.8 14.2
```
- Renk yoğunluğu = Oyuncu sayısı
- Hover: Detaylı bilgi
- En yoğun saatleri gösterir

**3. Map Distribution (Doughnut Chart)**
```javascript
{
  labels: ['de_dust2', 'de_inferno', 'de_nuke', ...],
  data: [450, 320, 280, ...] // dakika cinsinden playtime
}
```

**4. Retention Rate (Statistic Card)**
```
Geri Dönüş Oranı: 68.5%
Toplam Oyuncu: 245
Geri Dönen: 168
```

#### CSV Export
```csv
Tarih,Toplam Oyuncu,Benzersiz Oyuncu,Ortalama Oyuncu,Max Oyuncu,En Çok Oynanan Harita
2025-01-25,245,189,12.5,28,de_dust2
2025-01-24,223,201,11.8,25,de_inferno
...
```

#### API Endpoints
```bash
# Saatlik veriler (son 24 saat)
GET /api/v2/servers/{id}/stats/hourly?hours=24

# Günlük veriler (son 30 gün)
GET /api/v2/servers/{id}/stats/daily?days=30

# Heatmap (son 30 gün)
GET /api/v2/servers/{id}/stats/heatmap?days=30

# Retention (son 7 gün)
GET /api/v2/servers/{id}/stats/retention?days=7

# Harita dağılımı
GET /api/v2/servers/{id}/stats/maps?days=7

# CSV export
GET /api/v2/servers/{id}/stats/export?date_from=2025-01-01&date_to=2025-01-25
```

---

### 4. Advanced File Manager
**Monaco Editor ile Dosya Yönetimi**

#### Ne Yapar?
Sunucu dosyalarını web üzerinden düzenlemenize olanak tanır. VSCode-like editör deneyimi sunar.

#### Özellikler

**1. File Browser**
- Breadcrumb navigation
- Folder/file icons
- Size display (formatted)
- Last modified date
- Click to navigate folders
- Click to edit files

**2. Monaco Editor**
- Syntax highlighting
- Auto-completion
- Minimap
- Line numbers
- Word wrap
- Dark theme
- Multiple language support

**3. File Operations**
- 📁 **Browse** - Klasör gezinme
- 📄 **Read** - Dosya okuma
- ✏️ **Edit** - Dosya düzenleme
- 📤 **Upload** - Dosya yükleme (drag-drop)
- ➕ **Create Folder** - Yeni klasör
- 🗑️ **Delete** - Dosya/klasör silme

#### Desteklenen Dosya Tipleri

**Config Files:**
- .cfg → ini (syntax)
- .ini → ini
- server.cfg, amxx.cfg, plugins.ini

**Source Files:**
- .sma → cpp (Pawn source)
- .inc → cpp (Include files)

**Data Files:**
- .json → json
- .txt → plaintext
- .log → plaintext

**Scripts:**
- .sh → shell
- .bat → bat

**Documentation:**
- .md → markdown

#### Editor Features

```javascript
// Auto-detect language
const languageMap = {
  '.cfg': 'ini',
  '.sma': 'cpp',
  '.json': 'json',
  '.sh': 'shell',
  '.md': 'markdown'
}

// Editor configuration
{
  theme: 'vs-dark',
  fontSize: 14,
  minimap: { enabled: true },
  wordWrap: 'on',
  automaticLayout: true,
  scrollBeyondLastLine: false
}
```

#### Güvenlik

**Path Traversal Protection:**
```python
# 3-layer validation
def validate_path(server_id, requested_path):
    server_root = Path(f"/home/gameservers/servers/server_{server_id}")
    full_path = (server_root / requested_path).resolve()

    # Check if path is within server directory
    if not str(full_path).startswith(str(server_root.resolve())):
        raise HTTPException(403, "Path traversal blocked")

    return full_path
```

**File Upload Validation:**
- Extension whitelist
- Size limits (5MB edit, 50MB upload)
- Filename sanitization (reject ../, /, \)

**Backup Strategy:**
```python
# Before every modification
timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
backup_path = file_path.with_suffix(f'{suffix}.backup.{timestamp}')
shutil.copy2(file_path, backup_path)
```

#### Usage Example

**Read and Edit server.cfg:**
```javascript
// 1. Browse to file
GET /api/v2/servers/123/files/browse?path=cstrike

// 2. Read file
GET /api/v2/servers/123/files/read?path=cstrike/server.cfg
Response: {
  content: "hostname \"My Server\"\nrcon_password \"...\"",
  language: "ini",
  size: 1024,
  modified: "2025-01-25T10:30:00"
}

// 3. Edit and save
POST /api/v2/servers/123/files/write?path=cstrike/server.cfg
Body: {
  content: "hostname \"My Updated Server\"\n..."
}
```

---

### 5. Plugin Manager
**AMXModX Plugin Yönetim Sistemi**

#### Ne Yapar?
AMXModX pluginlerini yönetir. Upload, enable/disable, compile ve marketplace entegrasyonu sağlar.

#### Özellikler

**1. Installed Plugins Tab**
- Plugin listesi (name, version, author, size)
- Enable/disable switch
- Upload .amxx button
- Delete with confirmation
- Sort by name

**2. Marketplace Tab**
- Curated plugin list
- Category tags
- Description cards
- One-click install (yakında)

**3. Compile Tab**
- .sma source compilation
- amxxpc compiler integration
- Compile status messages

#### Plugin Metadata Extraction

```python
# Binary .amxx parsing
def _extract_plugin_info(plugin_file):
    # Read first 4KB
    data = plugin_file.read(4096)
    text = data.decode('utf-8', errors='ignore')

    # Heuristic parsing
    for line in text.split('\x00'):
        if 'version' in line.lower():
            info['version'] = line.strip()
        if 'author' in line.lower():
            info['author'] = line.strip()

    return info
```

#### Enable/Disable Workflow

**Enable Plugin:**
```python
# plugins.ini önce:
adminvote.amxx
adminchat.amxx
; myplugin.amxx  # disabled

# Enable myplugin.amxx
# plugins.ini sonra:
adminvote.amxx
adminchat.amxx
myplugin.amxx
```

**Disable Plugin:**
```python
# plugins.ini önce:
myplugin.amxx

# Disable myplugin.amxx
# plugins.ini sonra:
; myplugin.amxx
```

#### Plugin Compilation

```bash
# Upload .sma file to scripting/ folder
POST /api/v2/servers/123/plugins/compile/myplugin.sma

# Server runs:
cd /home/gameservers/servers/server_123/cstrike/addons/amxmodx/scripting
./amxxpc myplugin.sma

# Output: myplugin.amxx
# Moved to: ../plugins/myplugin.amxx
```

#### Marketplace Plugins

```javascript
{
  "name": "Admin Commands",
  "filename": "admincmd.amxx",
  "description": "Essential admin commands",
  "category": "Admin Tools",
  "download_url": "https://example.com/admincmd.amxx"
}
```

Categories:
- 🛡️ Admin Tools
- ⚙️ Server Management
- 🎮 Gameplay
- 🎉 Fun

#### API Endpoints

```bash
# List plugins
GET /api/v2/servers/{id}/plugins/list

# Enable
POST /api/v2/servers/{id}/plugins/{filename}/enable

# Disable
POST /api/v2/servers/{id}/plugins/{filename}/disable

# Upload
POST /api/v2/servers/{id}/plugins/upload
Content-Type: multipart/form-data

# Delete
DELETE /api/v2/servers/{id}/plugins/{filename}

# Compile
POST /api/v2/servers/{id}/plugins/compile/{sma_filename}

# Marketplace
GET /api/v2/servers/{id}/plugins/marketplace
```

---

## 🎨 User Interface

### ServerPanel Integration

#### Tab Structure
```
ServerPanel.vue
├── 🖥️ Konsol (Console)
├── 👥 Oyuncular (Players)
├── 📊 İstatistik (Basic Stats)
├── 🛡️ Adminler (Admins)
├── ⏰ Zamanlanmış Görevler (Scheduler) ← NEW
├── 📈 Gelişmiş İstatistikler (Advanced Stats) ← NEW
├── 📁 Dosya Yöneticisi (File Manager) ← NEW
├── 🔌 Plugin Yöneticisi (Plugin Manager) ← NEW
└── ⚙️ Ayarlar (Config)
```

#### Component Hierarchy
```
ServerPanel.vue
├── SchedulerManager.vue
│   ├── Task Creation Modal
│   ├── Task List Table
│   └── Execution History Modal
│
├── ServerStats.vue
│   ├── StatsChart.vue (Line)
│   ├── Heatmap Table
│   ├── StatsChart.vue (Doughnut)
│   └── Retention Card
│
├── FileManager.vue
│   ├── FileBrowser.vue
│   │   ├── Breadcrumb
│   │   ├── Upload Modal
│   │   └── Mkdir Modal
│   └── MonacoEditor.vue
│
└── PluginManager.vue
    ├── Installed Tab
    ├── Marketplace Tab
    └── Compile Tab
```

---

## 🔐 Security Features

### 1. Authentication & Authorization
- JWT token authentication
- Server ownership verification on all endpoints
- Role-based access control (RBAC)

### 2. Input Validation
- File path validation (no traversal)
- Extension whitelist
- Size limits
- Filename sanitization

### 3. Backup Strategy
- Timestamped backups before all modifications
- Separate backup directory per server
- Retention policy (auto-cleanup old backups)

### 4. Logging & Audit
- All operations logged with user ID
- Execution history for scheduled tasks
- File modification tracking

### 5. Rate Limiting
- API rate limits (1000 req/min)
- Upload size limits
- Compilation timeouts

---

## 📊 Performance

### Optimization Strategies

**1. Database Indexing**
```sql
-- Scheduler
INDEX idx_server_enabled (server_id, is_enabled)
UNIQUE INDEX apscheduler_job_id

-- Stats
UNIQUE INDEX idx_server_date (server_id, date)
INDEX idx_session_time (server_id, join_time)
INDEX idx_steam_id (steam_id)
```

**2. Caching**
- Redis cache for stats (1-minute TTL)
- Browser cache for static assets
- Chart.js data decimation

**3. Background Processing**
- APScheduler for async task execution
- Daily stats aggregation at midnight
- WebSocket for real-time updates

**4. Frontend Optimization**
- Code splitting (lazy load components)
- Monaco Editor CDN
- Chart.js tree-shaking

---

## 🧪 Testing Guide

### Manual Testing

**Auto Admin:**
```bash
1. Create new server
2. Check /home/gameservers/servers/server_X/cstrike/addons/amxmodx/configs/users.ini
3. Verify owner's Steam ID is present with full flags
```

**Scheduler:**
```bash
1. Create cron task (every minute)
2. Wait 1-2 minutes
3. Check execution history
4. Verify task ran successfully
```

**Stats:**
```bash
1. Navigate to Advanced Stats tab
2. Check if charts load
3. Export CSV
4. Verify data format
```

**File Manager:**
```bash
1. Browse to cstrike/server.cfg
2. Edit hostname
3. Save
4. Check backup file created
5. Verify changes applied
```

**Plugins:**
```bash
1. Upload test.amxx
2. Enable plugin
3. Check plugins.ini updated
4. Disable plugin
5. Verify commented in plugins.ini
```

---

## 📚 API Reference

See `API_REFERENCE.md` for complete endpoint documentation.

### Quick Reference

| Feature | Base Endpoint | Methods |
|---------|--------------|---------|
| Auto Admin | `/api/v2/servers/{id}/admins` | POST |
| Scheduler | `/api/v2/servers/{id}/scheduler` | GET, POST, PUT, DELETE |
| Stats | `/api/v2/servers/{id}/stats` | GET |
| Files | `/api/v2/servers/{id}/files` | GET, POST, DELETE |
| Plugins | `/api/v2/servers/{id}/plugins` | GET, POST, DELETE |

---

## 🐛 Troubleshooting

### Common Issues

**Scheduler tasks not running:**
- Check APScheduler logs
- Verify `scheduler_service.start()` called
- Check database connection

**Stats not showing:**
- Ensure hourly stats exist
- Run daily aggregation manually
- Check server monitoring is active

**File upload fails:**
- Check file size (< 50MB)
- Verify extension is whitelisted
- Check disk space

**Plugin compilation fails:**
- Verify amxxpc exists in scripting/
- Check .sma file is valid
- Review compiler output

**Monaco Editor not loading:**
- Clear browser cache
- Check console for errors
- Verify monaco-editor installed

---

## 🚀 Future Enhancements

### Planned Features

1. **Marketplace Download**
   - Direct plugin download from marketplace
   - Automatic installation
   - Version update checker

2. **Real-time Stats**
   - WebSocket updates every 5 seconds
   - Live player count graph
   - Real-time console output integration

3. **Scheduler Templates**
   - Pre-configured task templates
   - Community-shared schedules
   - Import/export functionality

4. **File Diff Viewer**
   - Compare config versions
   - Restore from backup UI
   - Change highlighting

5. **Plugin Dependencies**
   - Auto-detect required plugins
   - Dependency resolution
   - Installation order management

6. **Advanced Analytics**
   - Player behavior analysis
   - Peak time predictions
   - Churn rate tracking
   - Revenue forecasting

---

## 📖 User Guide

### Getting Started

1. **Navigate to Server Panel**
   - Go to "Sunucularım"
   - Click on your server

2. **Access New Features**
   - Use left sidebar tabs
   - Click feature icons

3. **Create First Scheduled Task**
   - Go to "Zamanlanmış Görevler"
   - Click "Yeni Görev Ekle"
   - Select task type and schedule
   - Save

4. **View Statistics**
   - Go to "Gelişmiş İstatistikler"
   - Select time range
   - Export data if needed

5. **Edit Configuration**
   - Go to "Dosya Yöneticisi"
   - Navigate to file
   - Click "Düzenle"
   - Make changes and save

6. **Manage Plugins**
   - Go to "Plugin Yöneticisi"
   - Upload .amxx or browse marketplace
   - Toggle plugins on/off
   - Compile .sma sources

---

## 🤝 Support

For issues or questions:
- Check logs: `/var/www/agtrmerkezi/logs/`
- API docs: `{BASE_URL}/api/docs`
- GitHub issues: (if applicable)
- Discord support: (if applicable)
