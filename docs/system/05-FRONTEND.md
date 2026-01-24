# Frontend Dokümantasyonu

## Teknoloji Stack

```
Vue.js 3.x (Composition API)
Vite 5.x (Build Tool)
Naive UI (Component Library)
Pinia (State Management)
Vue Router 4.x (Routing)
Lucide Icons (Icon Library)
```

---

## Dizin Yapısı

```
frontend/
├── src/
│   ├── views/              # Sayfa bileşenleri
│   │   ├── Home.vue        # Ana sayfa
│   │   ├── Forum.vue       # Forum ana sayfa
│   │   ├── ForumCategory.vue
│   │   ├── ForumTopic.vue
│   │   ├── Jackpot.vue     # Jackpot oyunu
│   │   ├── Servers.vue     # Sunucu listesi
│   │   ├── Profile.vue     # Kullanıcı profili
│   │   ├── Wallet.vue      # Cüzdan
│   │   ├── Login.vue       # Giriş
│   │   ├── Register.vue    # Kayıt
│   │   └── admin/          # Admin sayfaları
│   │       ├── Dashboard.vue
│   │       ├── Users.vue
│   │       ├── Forum.vue
│   │       ├── Servers.vue
│   │       └── SystemHealth.vue
│   │
│   ├── components/         # Yeniden kullanılabilir bileşenler
│   │   ├── layout/
│   │   │   ├── Navbar.vue
│   │   │   └── Footer.vue
│   │   ├── forum/
│   │   │   ├── ForumTopicCard.vue
│   │   │   ├── ForumPostCard.vue
│   │   │   ├── ForumSidebar.vue
│   │   │   ├── PopularTopicsSection.vue
│   │   │   └── RecentTopicsSection.vue
│   │   ├── game/
│   │   │   ├── AchievementPopup.vue
│   │   │   ├── LevelUp.vue
│   │   │   └── GamingHUD.vue
│   │   ├── social/
│   │   │   ├── FriendsList.vue
│   │   │   └── ChatWindow.vue
│   │   └── ui/
│   │       ├── Skeleton.vue
│   │       ├── EmptyState.vue
│   │       └── ToastContainer.vue
│   │
│   ├── services/           # API servisleri
│   │   ├── api.js          # Axios instance
│   │   ├── auth.js         # Auth service
│   │   └── websocket.js    # WebSocket manager
│   │
│   ├── stores/             # Pinia store'ları
│   │   ├── auth.js         # Auth state
│   │   ├── user.js         # User state
│   │   └── notifications.js
│   │
│   ├── router/             # Vue Router
│   │   └── index.js
│   │
│   ├── assets/             # Statik dosyalar
│   │   └── styles/
│   │       ├── forum.css
│   │       ├── jackpot.css
│   │       └── ui-enhancements.css
│   │
│   ├── App.vue             # Root component
│   ├── main.js             # Entry point
│   └── style.css           # Global stiller
│
├── public/                 # Public assets
├── index.html
├── vite.config.js
└── package.json
```

---

## Temel Componentler

### Layout Components

#### Navbar.vue
```
┌──────────────────────────────────────────────────────────┐
│  🔶 AGTR    Forum  Sunucular  Jackpot  |  🔔  👤 User   │
└──────────────────────────────────────────────────────────┘
```
- Responsive tasarım (mobile hamburger menu)
- Kullanıcı dropdown menu
- Bildirim merkezi
- Canlı online sayısı

#### Footer.vue
```
┌──────────────────────────────────────────────────────────┐
│  © 2024 AGTR Merkezi  |  Discord  |  Steam  |  Privacy  │
└──────────────────────────────────────────────────────────┘
```

### Forum Components

#### ForumTopicCard.vue
```vue
<template>
  <div class="topic-card">
    <div class="topic-author">
      <img :src="topic.author.avatar" />
      <span>{{ topic.author.username }}</span>
      <LevelBadge :level="topic.author.level" />
    </div>
    <div class="topic-content">
      <h3>{{ topic.title }}</h3>
      <p>{{ topic.preview }}</p>
    </div>
    <div class="topic-stats">
      <span>👁 {{ topic.view_count }}</span>
      <span>💬 {{ topic.reply_count }}</span>
      <span>❤️ {{ topic.like_count }}</span>
    </div>
  </div>
</template>
```

**Props:**
| Prop | Tip | Açıklama |
|------|-----|----------|
| topic | Object | Konu verisi |
| compact | Boolean | Kompakt görünüm |
| showCategory | Boolean | Kategori göster |

#### PopularTopicsSection.vue
Ana sayfada popüler konuları gösterir.

#### RecentTopicsSection.vue
Ana sayfada son konuları gösterir.

### Game Components

#### AchievementPopup.vue
Başarı kazanıldığında gösterilen popup.

#### LevelUp.vue
Seviye atlandığında animasyonlu kutlama.

#### GamingHUD.vue
Oyun tarzı bilgi paneli (XP bar, level, coins).

### UI Components

#### Skeleton.vue
Loading durumunda gösterilen placeholder.

```vue
<Skeleton type="card" :count="3" />
<Skeleton type="text" width="200px" />
<Skeleton type="avatar" size="40" />
```

#### EmptyState.vue
Boş liste durumunda gösterilen mesaj.

---

## Sayfa Yapıları

### Home.vue
```
┌─────────────────────────────────────────────────────────┐
│                     HERO SECTION                         │
│  Logo + Stats (Animated Counters)                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────┐  ┌─────────────────────────┐  │
│  │  🔥 Popüler Konular │  │   📝 Son Konular        │  │
│  │  ─────────────────  │  │   ─────────────────     │  │
│  │  Topic Card 1       │  │   Topic Card 1          │  │
│  │  Topic Card 2       │  │   Topic Card 2          │  │
│  │  Topic Card 3       │  │   Topic Card 3          │  │
│  └─────────────────────┘  └─────────────────────────┘  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│               KATEGORI KARTLARI                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ CS 1.6  │ │Half-Life│ │ Destek  │ │Turnuva  │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
└─────────────────────────────────────────────────────────┘
```

### Forum.vue
```
┌─────────────────────────────────────────────────────────┐
│  SIDEBAR          │           MAIN CONTENT              │
│  ─────────        │           ────────────              │
│  📂 Kategoriler   │  [Sort] [Filter] [+ Yeni Konu]     │
│  • Duyurular      │  ─────────────────────────────     │
│  • Genel          │  Topic Card                        │
│  • CS 1.6         │  Topic Card                        │
│  • Half-Life      │  Topic Card                        │
│  • Destek         │  Topic Card                        │
│  ─────────        │  ─────────────────────────────     │
│  📊 İstatistik    │  [Pagination]                      │
└─────────────────────────────────────────────────────────┘
```

### Jackpot.vue
```
┌─────────────────────────────────────────────────────────┐
│                    JACKPOT SPINNER                       │
│                  ┌──────────────┐                       │
│                  │    15,000    │                       │
│                  │     COIN     │                       │
│                  └──────────────┘                       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Player Bets (Circular visualization)           │   │
│  │  🟠 Player1: 500 (3.3%)                         │   │
│  │  🟣 Player2: 1000 (6.7%)                        │   │
│  │  🟢 Player3: 13500 (90%)                        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────┐                                       │
│  │ Bet Amount  │  [Place Bet]                         │
│  └─────────────┘                                       │
├─────────────────────────────────────────────────────────┤
│                    RECENT ROUNDS                         │
└─────────────────────────────────────────────────────────┘
```

---

## State Management (Pinia)

### auth.js Store
```javascript
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: false
  }),

  actions: {
    async login(credentials) { ... },
    async logout() { ... },
    async fetchUser() { ... }
  },

  getters: {
    isAdmin: (state) => state.user?.role === 'admin',
    userLevel: (state) => state.user?.level || 0
  }
})
```

### user.js Store
```javascript
export const useUserStore = defineStore('user', {
  state: () => ({
    profile: null,
    wallet: { coin: 0, tl: 0, bonus: 0 },
    notifications: []
  }),

  actions: {
    async fetchProfile() { ... },
    async fetchWallet() { ... },
    async updateProfile(data) { ... }
  }
})
```

---

## Router Yapısı

```javascript
const routes = [
  // Public
  { path: '/', component: Home },
  { path: '/forum', component: Forum },
  { path: '/forum/:categorySlug', component: ForumCategory },
  { path: '/forum/topic/:id', component: ForumTopic },
  { path: '/servers', component: Servers },
  { path: '/jackpot', component: Jackpot },

  // Auth Required
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/wallet', component: Wallet, meta: { requiresAuth: true } },

  // Admin
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', component: AdminDashboard },
      { path: 'users', component: AdminUsers },
      { path: 'forum', component: AdminForum },
      { path: 'health', component: SystemHealth }
    ]
  }
]
```

---

## API Service

### api.js
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// Request interceptor - Auth token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - Error handling
api.interceptors.response.use(
  response => response.data,  // Direkt data döner
  error => {
    if (error.response?.status === 401) {
      // Token expired, logout
      useAuthStore().logout()
    }
    return Promise.reject(error)
  }
)

export default api
```

**Önemli:** api.js `response.data` döndürür, bu yüzden frontend'de `response.data.success` yerine `response.success` kullanılır.

---

## CSS Değişkenleri

```css
:root {
  /* Colors */
  --primary: #f97316;
  --primary-light: #fb923c;
  --secondary: #8b5cf6;

  /* Background */
  --bg-dark: #0a0a0a;
  --bg-card: rgba(255, 255, 255, 0.05);
  --bg-glass: rgba(255, 255, 255, 0.1);

  /* Text */
  --text-primary: #ffffff;
  --text-secondary: #a1a1aa;

  /* Gaming Accents */
  --neon-green: #39ff14;
  --neon-blue: #00d4ff;
  --neon-purple: #bf00ff;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  --radius-xl: 24px;
}
```

---

## Animasyonlar

### Hover Efektleri
```css
.card-hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(249, 115, 22, 0.15);
}
```

### Skeleton Loading
```css
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton {
  background: linear-gradient(90deg,
    var(--bg-card) 25%,
    var(--bg-glass) 50%,
    var(--bg-card) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

### Page Transitions
```css
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
```

---

## Build & Deploy

### Development
```bash
cd frontend
npm install
npm run dev
```

### Production Build
```bash
npm run build
# Output: /static/dist/
```

### Environment
```bash
# .env.development
VITE_API_URL=/api

# .env.production
VITE_API_URL=/api
```
