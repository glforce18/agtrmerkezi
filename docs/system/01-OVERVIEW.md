# AGTR Merkezi - Sistem Dokümantasyonu

## Genel Bakış

AGTR Merkezi, Türkiye'nin en büyük Counter-Strike 1.6 ve Half-Life topluluğu için geliştirilmiş modern bir web platformudur.

### Temel Özellikler

- **Forum Sistemi**: Kategori bazlı tartışma platformu
- **Sunucu Yönetimi**: Oyun sunucusu kiralama ve yönetimi
- **Jackpot Oyunu**: Provably Fair bahis sistemi
- **Klan Sistemi**: Oyuncu grupları ve turnuvalar
- **Cüzdan Sistemi**: Coin ve TL bazlı ödeme altyapısı
- **Admin Paneli**: Kapsamlı yönetim arayüzü

---

## Teknoloji Yığını

### Backend
```
Python 3.13
FastAPI (Web Framework)
SQLAlchemy (ORM)
PostgreSQL/MySQL (Database)
Redis (Cache & Pub/Sub)
Uvicorn (ASGI Server)
```

### Frontend
```
Vue.js 3 (Composition API)
Vite (Build Tool)
Naive UI (Component Library)
Pinia (State Management)
Vue Router (Routing)
Lucide Icons (Icon Library)
```

### Altyapı
```
Nginx (Reverse Proxy)
Systemd (Process Manager)
Let's Encrypt (SSL)
```

---

## Dizin Yapısı

```
/var/www/agtrmerkezi/
├── app/                    # Backend uygulaması
│   ├── api/               # API endpoint'leri
│   │   ├── admin/        # Admin API'leri
│   │   ├── auth.py       # Kimlik doğrulama
│   │   ├── forum.py      # Forum API
│   │   ├── games.py      # Oyun API (Jackpot)
│   │   ├── servers.py    # Sunucu API
│   │   ├── users.py      # Kullanıcı API
│   │   ├── wallet.py     # Cüzdan API
│   │   └── websocket.py  # WebSocket
│   ├── core/             # Çekirdek modüller
│   │   ├── config.py     # Ayarlar
│   │   ├── security.py   # Güvenlik
│   │   └── redis_manager.py
│   ├── models/           # Veritabanı modelleri
│   │   ├── database.py   # Ana modeller
│   │   └── connection.py # DB bağlantısı
│   ├── services/         # İş mantığı
│   │   ├── jackpot.py
│   │   └── wallet.py
│   └── main.py           # Uygulama girişi
│
├── frontend/              # Vue.js uygulaması
│   ├── src/
│   │   ├── views/        # Sayfa bileşenleri
│   │   ├── components/   # Yeniden kullanılabilir bileşenler
│   │   ├── services/     # API servisleri
│   │   ├── stores/       # Pinia store'ları
│   │   └── router/       # Vue Router
│   └── package.json
│
├── static/                # Statik dosyalar
│   ├── dist/             # Frontend build çıktısı
│   ├── maps/             # Harita resimleri
│   └── images/           # Genel resimler
│
├── scripts/               # Yardımcı scriptler
│   └── visual_tests.py   # Test suite
│
└── tests/                 # Test sonuçları
    ├── screenshots/
    └── results/
```

---

## Sistem Metrikleri (Güncel)

| Metrik | Değer |
|--------|-------|
| Toplam Kullanıcı | 5 |
| Forum Konuları | 12 |
| Forum Kategorileri | 17 |
| Disk Kullanımı | %75.4 |
| Boş Disk | 20GB |
| Redis Memory | 921KB |

---

## Erişim Noktaları

- **Ana Site**: https://agtrmerkezi.com
- **API Base**: https://agtrmerkezi.com/api
- **Admin Panel**: https://agtrmerkezi.com/admin
- **WebSocket**: wss://agtrmerkezi.com/ws

---

## Versiyon Bilgisi

- **Platform Versiyonu**: 6.0 Pro
- **Son Güncelleme**: 2026-01-23
- **Python**: 3.13
- **Node.js**: 20.x
- **Vue.js**: 3.x
