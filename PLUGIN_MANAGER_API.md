# 🔌 Plugin Manager API v2 - Kısıtlı Sistem

**Tarih:** 2026-01-30
**Status:** ✅ ACTIVE

---

## 🎯 Özellikler

### Kullanıcı Yapabilir:
- ✅ Kendi pluginlerini yükleyebilir (`.amxx`)
- ✅ Kendi yüklediği pluginleri silebilir
- ✅ Kendi pluginlerini aç/kapa yapabilir
- ✅ Server pluginlerini görebilir (read-only)

### Kullanıcı YAPAMAZ:
- ❌ Server pluginlerini silemez/değiştiremez
- ❌ Dosya indiremez
- ❌ Başka yerlere dosya yükleyemez
- ❌ Başka kullanıcıların pluginlerini silemez

---

## 📁 Dosya Yapısı

```
/home/gameservers/servers/server_9/valve/addons/amxmodx/plugins/
├── admin.amxx              [SERVER PLUGIN - READ ONLY]
├── admincmd.amxx           [SERVER PLUGIN - READ ONLY]
├── adminhelp.amxx          [SERVER PLUGIN - READ ONLY]
├── ...
└── user_uploads/
    ├── user_4/             [USER 4'ÜN PLUGİNLERİ]
    │   ├── my_shop.amxx
    │   └── my_gun.amxx
    └── user_7/             [USER 7'NİN PLUGİNLERİ]
        └── custom_mod.amxx
```

**plugins.ini:**
```ini
; Server Plugins (READ ONLY - Kullanıcı dokunamaz)
admin.amxx
admincmd.amxx
adminhelp.amxx

; === USER PLUGINS ===
user_uploads/user_4/my_shop.amxx          ; Aktif
;user_uploads/user_4/my_gun.amxx          ; Devre dışı
user_uploads/user_7/custom_mod.amxx       ; Aktif
```

---

## 🔧 API Endpoints

### Base URL
```
/api/servers/{server_id}/plugins
```

---

### 1. İstatistikler
```http
GET /api/servers/{server_id}/plugins/stats
```

**Response:**
```json
{
  "server_plugins_count": 25,
  "user_plugins_count": 2,
  "user_plugins_enabled": 1,
  "user_plugins_size": 245760,
  "user_plugins_size_mb": 0.23,
  "max_size_mb": 5.0
}
```

---

### 2. Server Pluginlerini Listele (Read-Only)
```http
GET /api/servers/{server_id}/plugins/server
```

**Response:**
```json
{
  "success": true,
  "plugins": [
    {
      "name": "admin.amxx",
      "size": 123456,
      "modified": "2026-01-20T10:30:00",
      "type": "server",
      "enabled": true,
      "can_delete": false,
      "can_toggle": false
    },
    {
      "name": "admincmd.amxx",
      "size": 234567,
      "modified": "2026-01-20T10:30:00",
      "type": "server",
      "enabled": true,
      "can_delete": false,
      "can_toggle": false
    }
  ]
}
```

---

### 3. Kendi Pluginlerimi Listele
```http
GET /api/servers/{server_id}/plugins/my
```

**Response:**
```json
{
  "success": true,
  "plugins": [
    {
      "name": "my_shop.amxx",
      "size": 125440,
      "modified": "2026-01-30T15:20:00",
      "type": "user",
      "enabled": true,
      "can_delete": true,
      "can_toggle": true
    },
    {
      "name": "my_gun.amxx",
      "size": 89600,
      "modified": "2026-01-30T16:45:00",
      "type": "user",
      "enabled": false,
      "can_delete": true,
      "can_toggle": true
    }
  ]
}
```

---

### 4. Tüm Pluginleri Listele (Combined)
```http
GET /api/servers/{server_id}/plugins/all
```

**Response:**
```json
{
  "success": true,
  "server_plugins": [...],
  "user_plugins": [...],
  "stats": {
    "server_plugins_count": 25,
    "user_plugins_count": 2,
    "user_plugins_enabled": 1,
    "user_plugins_size_mb": 0.23
  }
}
```

---

### 5. Plugin Yükle
```http
POST /api/servers/{server_id}/plugins/upload
Content-Type: multipart/form-data
```

**Request:**
```
file: [binary .amxx file]
```

**Kısıtlamalar:**
- Sadece `.amxx` dosyaları
- Maksimum 5 MB
- `user_uploads/user_{id}/` klasörüne yüklenir

**Response (Success):**
```json
{
  "success": true,
  "message": "'my_shop.amxx' başarıyla yüklendi",
  "plugin": {
    "name": "my_shop.amxx",
    "size": 125440,
    "uploaded": "2026-01-30T15:20:00",
    "type": "user",
    "enabled": false,
    "can_delete": true,
    "can_toggle": true
  }
}
```

**Response (Error):**
```json
{
  "detail": "Sadece .amxx dosyaları yüklenebilir"
}
```

---

### 6. Plugin Sil
```http
DELETE /api/servers/{server_id}/plugins/{filename}
```

**Example:**
```http
DELETE /api/servers/9/plugins/my_shop.amxx
```

**Response:**
```json
{
  "success": true,
  "message": "'my_shop.amxx' silindi"
}
```

**Not:** Sadece kendi yüklediğiniz pluginleri silebilirsiniz!

---

### 7. Plugin Aç/Kapa
```http
POST /api/servers/{server_id}/plugins/{filename}/toggle
Content-Type: application/json
```

**Request Body:**
```json
{
  "enabled": true
}
```

**Example:**
```http
POST /api/servers/9/plugins/my_shop.amxx/toggle
{
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "'my_shop.amxx' aktif edildi",
  "enabled": true
}
```

**Not:**
- `plugins.ini` dosyasını günceller
- `enabled: true` → Plugin aktif (uncommented)
- `enabled: false` → Plugin devre dışı (commented with `;`)

---

## 🎨 Frontend Tasarım Önerileri

### 1. Plugin Listesi (Ana Görünüm)

```
┌─────────────────────────────────────────────────────────────┐
│  📊 İstatistikler                                           │
├─────────────────────────────────────────────────────────────┤
│  Server Pluginleri: 25    Kendi Pluginlerim: 2             │
│  Aktif: 1/2              Kullanılan Alan: 0.23 MB / 5 MB   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  📦 Server Pluginleri (Read-Only)              [Gizle]     │
├─────────────────────────────────────────────────────────────┤
│  ✅ admin.amxx                        120 KB    [Aktif]    │
│  ✅ admincmd.amxx                     229 KB    [Aktif]    │
│  ✅ adminhelp.amxx                     45 KB    [Aktif]    │
│  ...                                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  🔌 Kendi Pluginlerim                    [📤 Yükle]        │
├─────────────────────────────────────────────────────────────┤
│  ✅ my_shop.amxx                      122 KB               │
│     [🗑️ Sil]  [✓ Aktif]                                   │
│                                                              │
│  ❌ my_gun.amxx                        87 KB               │
│     [🗑️ Sil]  [☐ Kapalı]                                  │
└─────────────────────────────────────────────────────────────┘
```

### 2. Upload Modal

```
┌─────────────────────────────────────────────────────────────┐
│  📤 Plugin Yükle                                      [✕]   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [📁 Dosya Seç] veya sürükle-bırak                         │
│                                                              │
│  ⚠️ Kısıtlamalar:                                          │
│  • Sadece .amxx dosyaları                                   │
│  • Maksimum 5 MB                                           │
│  • Aynı isimde dosya varsa yükleme başarısız olur          │
│                                                              │
│  [İptal]                        [Yükle]                     │
└─────────────────────────────────────────────────────────────┘
```

### 3. Toggle Switch (Aç/Kapa)

```css
/* Aktif */
[✓ Aktif]      /* Yeşil, kaydırıcı sağda */

/* Kapalı */
[☐ Kapalı]     /* Gri, kaydırıcı solda */
```

### 4. Renk Paleti

```css
/* Server Plugins (Read-Only) */
--plugin-server-bg: #1a1a2e;
--plugin-server-border: #4a4a6a;
--plugin-server-icon: #6b7280;

/* User Plugins (Editable) */
--plugin-user-bg: #2d3748;
--plugin-user-border: #4299e1;
--plugin-user-icon: #4299e1;

/* Enabled */
--plugin-enabled: #10b981;

/* Disabled */
--plugin-disabled: #6b7280;

/* Delete button */
--plugin-delete: #ef4444;
```

---

## 🔒 Güvenlik

### Dosya Validasyonu
1. **Extension Check:** Sadece `.amxx` kabul edilir
2. **Size Limit:** Maksimum 5 MB
3. **Filename Sanitization:** Path traversal engellenmiştir
4. **Owner Check:** Kullanıcı sadece kendi pluginlerini yönetebilir

### Path Isolation
```
user_uploads/user_4/   → Sadece user 4 erişebilir
user_uploads/user_7/   → Sadece user 7 erişebilir
```

### Database Tracking
Her yüklenen plugin `user_plugins` tablosunda kayıt altına alınır:
- user_id
- server_id
- filename
- size
- uploaded_at

---

## 📝 Örnek Frontend Kodu (React)

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function PluginManager({ serverId }) {
  const [plugins, setPlugins] = useState({ server: [], user: [] });
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadPlugins();
  }, [serverId]);

  const loadPlugins = async () => {
    const res = await axios.get(`/api/servers/${serverId}/plugins/all`);
    setPlugins({
      server: res.data.server_plugins,
      user: res.data.user_plugins
    });
    setStats(res.data.stats);
  };

  const uploadPlugin = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    await axios.post(
      `/api/servers/${serverId}/plugins/upload`,
      formData
    );

    loadPlugins(); // Reload
  };

  const deletePlugin = async (filename) => {
    await axios.delete(
      `/api/servers/${serverId}/plugins/${filename}`
    );
    loadPlugins();
  };

  const togglePlugin = async (filename, enabled) => {
    await axios.post(
      `/api/servers/${serverId}/plugins/${filename}/toggle`,
      { enabled }
    );
    loadPlugins();
  };

  return (
    <div className="plugin-manager">
      {/* Stats */}
      <div className="stats">
        <div>Server Pluginleri: {stats?.server_plugins_count}</div>
        <div>Kendi Pluginlerim: {stats?.user_plugins_count}</div>
        <div>Aktif: {stats?.user_plugins_enabled}/{stats?.user_plugins_count}</div>
        <div>Alan: {stats?.user_plugins_size_mb} MB / {stats?.max_size_mb} MB</div>
      </div>

      {/* Server Plugins (Read-Only) */}
      <div className="server-plugins">
        <h3>📦 Server Pluginleri</h3>
        {plugins.server.map(p => (
          <div key={p.name} className="plugin-item">
            <span>{p.enabled ? '✅' : '❌'} {p.name}</span>
            <span>{(p.size / 1024).toFixed(0)} KB</span>
          </div>
        ))}
      </div>

      {/* User Plugins (Editable) */}
      <div className="user-plugins">
        <h3>🔌 Kendi Pluginlerim</h3>

        <input
          type="file"
          accept=".amxx"
          onChange={(e) => uploadPlugin(e.target.files[0])}
        />

        {plugins.user.map(p => (
          <div key={p.name} className="plugin-item user">
            <span>{p.name}</span>
            <span>{(p.size / 1024).toFixed(0)} KB</span>
            <button onClick={() => deletePlugin(p.name)}>🗑️ Sil</button>
            <label>
              <input
                type="checkbox"
                checked={p.enabled}
                onChange={(e) => togglePlugin(p.name, e.target.checked)}
              />
              {p.enabled ? 'Aktif' : 'Kapalı'}
            </label>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## ✅ Backend Status

- **Service:** `PluginManagerService` - ✅ Created
- **API:** `plugin_manager.py` - ✅ Created
- **Database:** `UserPlugin` model - ✅ Added
- **Router:** Registered in `main.py` - ✅ Done
- **Endpoint:** `/api/servers/{server_id}/plugins` - ✅ Active

---

**Son Güncelleme:** 2026-01-30 23:45
**Status:** 🟢 READY FOR FRONTEND INTEGRATION
