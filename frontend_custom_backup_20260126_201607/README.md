# AGTR Merkezi - Frontend

Half-Life & Counter-Strike 1.6 temalı gaming platform frontend uygulaması.

## 🎮 Özellikler

### ✅ Tamamlanan Sayfalar
- **Auth**: Login, Register (2FA + OAuth desteği)
- **Servers**: My Servers, Server Panel (RCON), Server Rent, Server List
- **Forum**: Home, Category, Topic (Tepki sistemi, bookmark)
- **Admin**: Dashboard (Real-time stats)
- **User**: Profile (3 tab: Hesap, Güvenlik, Entegrasyonlar)

### 🎨 Tasarım
- **Lambda (λ)** branding
- **Half-Life HUD** inspired UI
- **Neon effects** (Orange, Cyan, Purple, Green)
- **Terminal aesthetics** (RCON konsolu)
- **Cyberpunk** color palette
- **Responsive** (Mobile, Tablet, Desktop)

### 🔌 API Entegrasyonu
- Axios client with interceptors
- Auth API (14 endpoints)
- Servers API (50+ endpoints)
- Forum API (35+ endpoints)
- Automatic token refresh

## 🚀 Kurulum

### Gereksinimler
- Node.js 18+
- npm 9+

### Adımlar

```bash
# 1. Bağımlılıkları yükle
npm install

# 2. Development server başlat (http://localhost:5173)
npm run dev

# 3. Production build
npm run build

# 4. Preview production build
npm run preview
```

## 📁 Proje Yapısı

```
frontend/
├── public/              # Static dosyalar
├── src/
│   ├── api/            # API clients
│   │   ├── client.js   # Axios instance
│   │   ├── auth.js     # Auth endpoints
│   │   ├── servers.js  # Server endpoints
│   │   └── forum.js    # Forum endpoints
│   ├── assets/
│   │   └── styles/
│   │       └── main.css # Global styles
│   ├── components/
│   │   └── Navbar.vue  # Main navigation
│   ├── stores/         # Pinia stores
│   │   ├── auth.js     # Auth state
│   │   └── servers.js  # Server state
│   ├── views/          # Pages
│   │   ├── auth/
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   ├── server/
│   │   │   ├── MyServers.vue
│   │   │   ├── ServerPanel.vue
│   │   │   ├── ServerRent.vue
│   │   │   └── ServerList.vue
│   │   ├── forum/
│   │   │   ├── ForumHome.vue
│   │   │   ├── ForumCategory.vue
│   │   │   └── ForumTopic.vue
│   │   ├── admin/
│   │   │   └── AdminDashboard.vue
│   │   └── user/
│   │       └── Profile.vue
│   ├── router/
│   │   └── index.js    # Vue Router config
│   ├── App.vue         # Root component
│   └── main.js         # Entry point
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🎯 Navigasyon

### Ana Menü
- **Ana Sayfa** (`/`) - Lambda hero, stats
- **Sunucular** (`/servers`) - Public server browser
- **Forum** (`/forum`) - Community forums
- **Kirala** (`/servers/rent`) - Server rental

### Kullanıcı Menüsü (Giriş yapıldığında)
- **Profilim** (`/profile`)
- **Sunucularım** (`/servers/my`)
- **Admin Panel** (`/admin`) - Sadece adminler

## 🔑 Özellik Detayları

### 1. RCON Konsolu (ServerPanel.vue)
- Terminal-style HEV interface
- Quick command buttons
- Real-time output
- Auto-scroll
- Command history

### 2. Server Browser (ServerList.vue)
- Live server list
- Filters (game type, search)
- Sort (players, ping, name)
- Pagination
- Steam connect integration

### 3. Forum
- Category-based organization
- Reaction system (5 emojis)
- Bookmark support
- Pin/Lock topics
- Markdown content

### 4. Server Rental
- 3 package tiers
- Period discounts (3mo 5%, 6mo 10%, 12mo 15%)
- Add-ons (backup, MySQL, support, plugins)
- Dynamic pricing
- Wallet / Card payment

### 5. Admin Dashboard
- Real-time system monitoring
- Live activity feed
- Stats cards
- Quick actions menu

## 🌐 API Endpoints

### Auth
```
POST /api/auth/login
POST /api/auth/register
POST /api/auth/logout
POST /api/auth/2fa/verify
GET  /api/auth/oauth/steam
```

### Servers
```
GET    /api/servers          # Public list
GET    /api/v2/servers/my    # User's servers
GET    /api/v2/servers/:id   # Server detail
POST   /api/v2/servers/:id/start
POST   /api/v2/servers/:id/stop
POST   /api/v2/servers/:id/restart
POST   /api/v2/servers/:id/rcon
GET    /api/v2/servers/:id/players
POST   /api/v2/servers/:id/admins
```

### Forum
```
GET    /api/forum/categories
GET    /api/forum/topics
GET    /api/forum/topics/:id
POST   /api/forum/topics/:id/replies
POST   /api/forum/topics/:id/react
```

## 🎨 Tema Renkleri

```javascript
// Lambda Orange - Primary
#FF6B35

// HEV Cyan - Info/Tech
#00F5FF

// Xen Purple - Accent
#B537F2

// Combine Green - Success
#39FF14

// Combine Red - Error
#FF0040
```

## 📦 Build Çıktısı

```
Total Size: ~320KB (uncompressed)
Gzipped: ~120KB
Build Time: ~3-4s

Main Chunks:
- vue-core: 95KB
- index: 55KB
- icons: 22KB
- ServerPanel: 16KB
- ServerRent: 15KB
```

## 🔧 Geliştirme Notları

### Vite Dev Proxy
Development sırasında `/api` ve `/static` istekleri otomatik olarak `http://localhost:8000`'e yönlendirilir.

### Font Kullanımı
- **font-lambda**: Orbitron (Başlıklar, butonlar)
- **font-hev**: Share Tech Mono (Terminal, kod)
- **font-body**: Electrolize (Body text)

### Tailwind Classes
```html
<!-- Lambda Orange Neon -->
<div class="neon-orange">λ</div>

<!-- HEV Terminal Style -->
<div class="hev-terminal">root@agtr:~$</div>

<!-- Cyberpunk Card -->
<div class="bg-cyber-panel border border-cyber-border">...</div>
```

## 🐛 Sorun Giderme

### Port 5173 kullanımda
```bash
# Port değiştir
npm run dev -- --port 3000
```

### Build hatası
```bash
# node_modules temizle
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 📝 Lisans

© 2024 AGTR Merkezi. Tüm hakları saklıdır.
