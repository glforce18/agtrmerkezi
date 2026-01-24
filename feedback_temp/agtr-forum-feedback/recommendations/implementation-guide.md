# AGTR Merkezi - Forum Öncelikli Tasarım İmplementasyon Rehberi

**Son Güncelleme:** 23 Ocak 2026  
**Tahmini Süre:** 6-7 saat  
**Zorluk:** Orta

---

## 🎯 Genel Bakış

Bu rehber, AGTR Merkezi'nin ana sayfasını forum odaklı hale getirmek için gereken tüm adımları içerir.

### Hedef
- Forum görünürlüğünü %30'dan %60'a çıkarmak
- Real-time aktivite akışı eklemek
- Kullanıcı etkileşimini artırmak

### Değişiklik Yapılacak Dosyalar
```
frontend/src/
├── views/Home.vue                    # 🔴 Büyük değişiklik
├── components/
│   ├── layout/Navbar.vue             # 🟡 Orta değişiklik
│   ├── forum/
│   │   └── LiveActivityFeed.vue      # 🟢 Yeni dosya
│   └── sidebar/
│       ├── OnlineUsersWidget.vue     # 🟢 Yeni dosya
│       └── CompactServersWidget.vue  # 🟢 Yeni dosya
└── assets/styles/
    └── forum-home.css                # 🟢 Yeni dosya

app/
├── api/routes/forum.py               # 🟡 Yeni endpointler
├── api/websocket/forum.py            # 🟢 Yeni dosya
└── services/forum_service.py         # 🟡 WebSocket entegrasyonu
```

---

## 📋 Faz 1: Frontend Layout (2-3 saat)

### Adım 1.1: Yeni Componentleri Oluştur

#### LiveActivityFeed.vue
```bash
# Dosya konumu
touch frontend/src/components/forum/LiveActivityFeed.vue
```

**İçerik:** `code-examples/02-live-activity.vue` dosyasındaki kodu kopyala.

**Test:**
```javascript
// Test prop'ları
const testActivities = [
  {
    id: 1,
    type: "reply",
    user: { username: "TestUser", avatar: "/avatar.jpg", level: 5 },
    action: "Test konusuna yanıt verdi",
    time: "5 saniye önce",
    topic_id: 123
  }
]
```

#### OnlineUsersWidget.vue
```bash
touch frontend/src/components/sidebar/OnlineUsersWidget.vue
```

**İçerik:** `code-examples/04-online-users-widget.vue` dosyasındaki kodu kopyala.

#### CompactServersWidget.vue
```bash
touch frontend/src/components/sidebar/CompactServersWidget.vue
```

**İçerik:** `code-examples/05-compact-servers.vue` dosyasındaki kodu kopyala.

---

### Adım 1.2: Home.vue'yu Güncelle

```bash
# Mevcut dosyayı yedekle
cp frontend/src/views/Home.vue frontend/src/views/Home.vue.backup

# Yeni içeriği kopyala
# code-examples/01-home-layout.vue → frontend/src/views/Home.vue
```

**Değişiklik Özeti:**
1. ✅ Hero section kompaktlaştırıldı
2. ✅ Grid layout eklendi (60% / 40%)
3. ✅ Yeni componentler import edildi
4. ✅ WebSocket bağlantısı eklendi

**Test:**
```bash
cd frontend
npm run dev
# Tarayıcıda http://localhost:5173 aç
# Layout'un doğru göründüğünden emin ol
```

---

### Adım 1.3: Navbar'ı Güncelle

```bash
# Mevcut dosyayı yedekle
cp frontend/src/components/layout/Navbar.vue frontend/src/components/layout/Navbar.vue.backup

# Forum link güncelleme kısmını ekle
```

**Değişiklikler:**
1. ✅ Forum linkine `.nav-link-forum` class ekle
2. ✅ Notification badge ekle
3. ✅ Online indicator ekle

**CSS Eklemeleri:**
```css
/* Navbar.vue <style> bloğuna ekle */
.nav-link-forum {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white !important;
  padding: 10px 20px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
  animation: forum-pulse 3s infinite;
}

@keyframes forum-pulse {
  0%, 100% { box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3); }
  50% { box-shadow: 0 6px 20px rgba(249, 115, 22, 0.6); }
}
```

---

### Adım 1.4: CSS Dosyası Ekle

```bash
mkdir -p frontend/src/assets/styles
touch frontend/src/assets/styles/forum-home.css
```

**İçerik:** Tüm custom CSS'leri buraya ekle (animasyonlar, hover efektleri vb.)

**main.js'e import et:**
```javascript
// frontend/src/main.js
import './assets/styles/forum-home.css'
```

---

## 📋 Faz 2: Backend API (1-2 saat)

### Adım 2.1: Forum API Endpointleri Ekle

```bash
# app/api/routes/forum.py dosyasını aç
```

**Eklenecek Endpointler:**
1. ✅ `GET /forum/live-activity`
2. ✅ `GET /forum/trending`
3. ✅ `GET /forum/online-users`
4. ✅ `GET /forum/stats`
5. ✅ `GET /forum/unread-count`

**Kod:** `code-examples/07-forum-api.py` dosyasındaki endpoint'leri kopyala.

---

### Adım 2.2: Helper Fonksiyonları Ekle

```python
# app/api/routes/forum.py'nin sonuna ekle

def get_time_ago(dt: datetime) -> str:
    """Datetime'ı 'X saniye önce' formatına çevir"""
    now = datetime.utcnow()
    diff = now - dt
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} saniye önce"
    elif seconds < 3600:
        return f"{int(seconds / 60)} dakika önce"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} saat önce"
    elif seconds < 604800:
        return f"{int(seconds / 86400)} gün önce"
    else:
        return dt.strftime("%d.%m.%Y")
```

---

### Adım 2.3: Test API Endpointleri

```bash
# Uvicorn başlat
cd /var/www/agtrmerkezi
source venv/bin/activate
uvicorn app.main:app --reload

# Başka bir terminalde test et
curl http://localhost:8000/api/forum/stats
curl http://localhost:8000/api/forum/online-users
curl http://localhost:8000/api/forum/trending?days=7
```

**Beklenen Yanıt:**
```json
{
  "onlineUsers": 5,
  "totalTopics": 123,
  "topicsToday": 4,
  "activeServers": 0
}
```

---

## 📋 Faz 3: WebSocket Entegrasyonu (2 saat)

### Adım 3.1: WebSocket Endpoint Oluştur

```bash
mkdir -p app/api/websocket
touch app/api/websocket/__init__.py
touch app/api/websocket/forum.py
```

**İçerik:** `code-examples/07-forum-api.py` dosyasındaki WebSocket kodunu kopyala.

---

### Adım 3.2: WebSocket'i Main App'e Ekle

```python
# app/main.py

from app.api.websocket import forum as forum_ws

# WebSocket route'u ekle
app.include_router(forum_ws.router)
```

---

### Adım 3.3: Frontend WebSocket Service

```bash
touch frontend/src/services/websocket.js
```

**İçerik:**
```javascript
export class ForumLiveSocket {
  constructor() {
    this.ws = null
    this.reconnectDelay = 5000
    this.maxReconnectDelay = 30000
    this.reconnectAttempts = 0
  }

  connect() {
    this.ws = new WebSocket('wss://agtrmerkezi.com/ws/forum-live')
    
    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.reconnectDelay = 5000
    }
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    this.ws.onclose = () => {
      console.log('WebSocket closed, reconnecting...')
      this.reconnect()
    }
  }

  reconnect() {
    this.reconnectAttempts++
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    )
    
    setTimeout(() => {
      this.connect()
    }, delay)
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
    }
  }
}
```

---

### Adım 3.4: WebSocket Test

```bash
# Browser Console'da test et
const ws = new WebSocket('ws://localhost:8000/ws/forum-live')
ws.onmessage = (event) => console.log(JSON.parse(event.data))
```

---

## 📋 Faz 4: Entegrasyon & Test (1 saat)

### Adım 4.1: Component Entegrasyonu Test

**Test Checklist:**
- [ ] Home.vue doğru render oluyor mu?
- [ ] LiveActivityFeed WebSocket'ten veri alıyor mu?
- [ ] OnlineUsers widget çalışıyor mu?
- [ ] CompactServers widget çalışıyor mu?
- [ ] Navbar forum linki vurgulu mu?

---

### Adım 4.2: Responsive Test

**Cihazlar:**
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

**Chrome DevTools ile test et:**
```
F12 → Toggle Device Toolbar → Test her cihazda
```

---

### Adım 4.3: Performance Test

```bash
# Lighthouse audit
npm run build
npx serve -s dist

# Chrome DevTools
# Lighthouse → Run Audit
```

**Hedef Skorlar:**
- Performance: >85
- Accessibility: >90
- Best Practices: >90
- SEO: >90

---

## 📋 Faz 5: Deployment (30 dakika)

### Adım 5.1: Production Build

```bash
cd frontend
npm run build

# Build sonucu /static/dist/ klasörüne kopyala
```

---

### Adım 5.2: Backend Restart

```bash
# Systemd service restart
sudo systemctl restart agtrmerkezi

# Nginx reload
sudo nginx -t
sudo systemctl reload nginx
```

---

### Adım 5.3: Production Test

```bash
# Site açılıyor mu?
curl -I https://agtrmerkezi.com

# WebSocket çalışıyor mu?
# Browser console'da test et

# API endpointleri çalışıyor mu?
curl https://agtrmerkezi.com/api/forum/stats
```

---

## ✅ Final Checklist

### Fonksiyonel
- [ ] Ana sayfa yeni layout ile açılıyor
- [ ] Forum %60 alan kaplıyor
- [ ] Canlı aktivite akışı çalışıyor
- [ ] WebSocket bağlantısı stabil
- [ ] Online kullanıcılar gösteriliyor
- [ ] Sunucular kompakt şekilde görünüyor
- [ ] Navbar forum linki vurgulu

### Teknik
- [ ] API endpointleri 200 dönüyor
- [ ] Cache çalışıyor (Redis)
- [ ] WebSocket reconnection çalışıyor
- [ ] Hata logları temiz
- [ ] Memory leak yok

### UX/UI
- [ ] Responsive tasarım çalışıyor
- [ ] Animasyonlar smooth
- [ ] Loading states var
- [ ] Error handling var
- [ ] Accessibility uygun

### Performance
- [ ] Lighthouse >85
- [ ] Initial load <2s
- [ ] API response <500ms
- [ ] WebSocket latency <100ms

---

## 🐛 Troubleshooting

### Sorun: WebSocket bağlanmıyor

**Çözüm:**
```bash
# Nginx WebSocket config kontrol et
sudo nano /etc/nginx/sites-available/agtrmerkezi.com

# WebSocket proxy ayarları olmalı:
location /ws/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

### Sorun: API endpoint 404 veriyor

**Çözüm:**
```python
# app/main.py - router include edilmiş mi kontrol et
from app.api.routes import forum

app.include_router(forum.router, prefix="/api")
```

---

### Sorun: CSS yüklenmiyor

**Çözüm:**
```javascript
// main.js - import var mı kontrol et
import './assets/styles/forum-home.css'
```

---

## 📊 Başarı Metrikleri

### 1 Hafta Sonra Kontrol Et:
- Forum ziyaret oranı: Hedef >50% (+177%)
- Ortalama oturum süresi: Hedef >6 dakika (+87%)
- Günlük aktif kullanıcı: Hedef >500 (+56%)
- Forum konu sayısı: Hedef >25/gün (+108%)

### 1 Ay Sonra Kontrol Et:
- Community engagement: Hedef +200%
- Sunucu doluluk oranı: Hedef >70% (+66%)
- Kullanıcı retention: Hedef >40%

---

## 🎉 Tebrikler!

Forum odaklı tasarım başarıyla implemente edildi. Kullanıcı geri bildirimlerini takip et ve gerekirse ince ayarlar yap.

**Sonraki Adımlar:**
1. A/B testing düşün
2. Analytics ekle
3. Kullanıcı feedback topla
4. Gamification özellikleri genişlet
