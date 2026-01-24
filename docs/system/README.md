# AGTR Merkezi - Sistem Dokümantasyonu

## Hakkında

AGTR Merkezi, Türkiye'nin en büyük Counter-Strike 1.6 ve Half-Life topluluğu için geliştirilmiş modern bir web platformudur.

---

## Dokümantasyon İçeriği

| Dosya | Açıklama |
|-------|----------|
| [01-OVERVIEW.md](01-OVERVIEW.md) | Genel bakış, teknoloji stack, dizin yapısı |
| [02-ARCHITECTURE.md](02-ARCHITECTURE.md) | Sistem mimarisi, katmanlar, request flow |
| [03-DATABASE.md](03-DATABASE.md) | Veritabanı şeması, ER diyagramı, enum'lar |
| [04-API.md](04-API.md) | API endpoint'leri, request/response örnekleri |
| [05-FRONTEND.md](05-FRONTEND.md) | Vue.js componentleri, store yapısı, routing |
| [06-CONFIG.md](06-CONFIG.md) | Nginx, systemd, env ayarları |

---

## Hızlı Başlangıç

### Gereksinimler
- Python 3.13+
- Node.js 20+
- PostgreSQL 14+
- Redis 7+
- Nginx

### Kurulum
```bash
# Backend
cd /var/www/agtrmerkezi
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm run build

# Service başlat
sudo systemctl start agtrmerkezi
sudo systemctl restart nginx
```

---

## Sistem Özeti

```
┌─────────────────────────────────────────────────────────────┐
│                        AGTR MERKEZİ                          │
│                     Platform Versiyonu: 6.0                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  FRONTEND          │  BACKEND           │  DATABASE          │
│  ─────────         │  ─────────         │  ─────────         │
│  Vue.js 3          │  FastAPI           │  PostgreSQL        │
│  Vite 5            │  SQLAlchemy        │  Redis             │
│  Naive UI          │  Uvicorn           │                    │
│  Pinia             │  Python 3.13       │                    │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ANA ÖZELLİKLER                                              │
│  • Forum Sistemi (Kategoriler, Konular, Yanıtlar)           │
│  • Jackpot Oyunu (Provably Fair)                            │
│  • Sunucu Kiralama                                          │
│  • Cüzdan Sistemi (Coin + TL)                               │
│  • Klan Sistemi                                             │
│  • Admin Paneli                                              │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  İSTATİSTİKLER                                               │
│  • Kullanıcılar: 5                                          │
│  • Forum Konuları: 12                                        │
│  • Kategoriler: 17                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Erişim Noktaları

| Servis | URL |
|--------|-----|
| Ana Site | https://agtrmerkezi.com |
| API | https://agtrmerkezi.com/api |
| Admin | https://agtrmerkezi.com/admin |
| WebSocket | wss://agtrmerkezi.com/ws |

---

## Destek

Sorular ve sorunlar için:
- GitHub Issues
- Discord Sunucusu
- E-posta: destek@agtrmerkezi.com

---

*Son Güncelleme: 2026-01-23*
