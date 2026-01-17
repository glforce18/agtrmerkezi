# AGTR v5.5 Pro - Yeni Özellikler Kurulum Rehberi

## 📦 İçerik

Bu paket 5 yeni API modülü içeriyor:

### 1. 🔐 Security API (`app/api/security.py`)
- IP Whitelist/Blacklist
- Brute Force Koruması
- Audit Log (Admin işlem kaydı)
- Session Yönetimi
- Şifre Politikası

### 2. 💰 Payment Gateway API (`app/api/payment_gateway.py`)
- PayTR Entegrasyonu
- iyzico Entegrasyonu
- Bakiye Sistemi (Cüzdan)
- Kupon Sistemi
- Havale/EFT Onay
- Otomatik Fatura

### 3. 🎮 Social API (`app/api/social.py`)
- Discord OAuth
- Steam OAuth
- Klan/Takım Sistemi
- Başarım Sistemi
- Arkadaş Listesi

### 4. 🖥️ Server Management API (`app/api/server_management.py`)
- Backup Sistemi
- Resource Monitor
- Zamanlanmış Görevler
- Uptime Raporu

### 5. 📊 Analytics API (`app/api/analytics.py`)
- Dashboard Grafikleri
- Oyuncu İstatistikleri
- Gelir Raporları
- Export (CSV/JSON)

---

## 🚀 Kurulum

### 1. ZIP'i aç
```bash
cd /var/www/agtrmerkezi
unzip -o agtr_v55_features.zip
```

### 2. main.py'a router'ları ekle

`app/main.py` dosyasında:

**Import satırlarına ekle:**
```python
from app.api import security, payment_gateway, social, server_management, analytics
```

**Router satırlarına ekle:**
```python
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(payment_gateway.router, prefix="/api/payment", tags=["Payment"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(server_management.router, prefix="/api/management", tags=["Management"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
```

### 3. Environment Variables (.env)

```bash
# PayTR
PAYTR_MERCHANT_ID=your_merchant_id
PAYTR_MERCHANT_KEY=your_merchant_key
PAYTR_MERCHANT_SALT=your_merchant_salt

# iyzico
IYZICO_API_KEY=your_api_key
IYZICO_SECRET_KEY=your_secret_key
IYZICO_BASE_URL=https://sandbox-api.iyzipay.com

# Discord
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=https://agtrmerkezi.com/api/social/discord/callback

# Steam
STEAM_API_KEY=your_steam_api_key
STEAM_REALM=https://agtrmerkezi.com
```

### 4. Servisi yeniden başlat
```bash
systemctl restart agtrmerkezi
```

---

## 📡 Yeni API Endpoints

### Security
- `GET /api/security/ip-rules` - IP kuralları
- `POST /api/security/ip-rules` - IP kuralı ekle
- `GET /api/security/login-attempts` - Giriş denemeleri
- `GET /api/security/audit-logs` - Audit logları
- `GET /api/security/sessions` - Aktif oturumlar
- `GET /api/security/stats` - Güvenlik istatistikleri

### Payment
- `GET /api/payment/balance` - Bakiye
- `GET /api/payment/balance/history` - Bakiye geçmişi
- `POST /api/payment/paytr/create` - PayTR ödeme başlat
- `POST /api/payment/iyzico/create` - iyzico ödeme başlat
- `GET /api/payment/coupons` - Kuponlar
- `POST /api/payment/coupons/validate` - Kupon doğrula
- `GET /api/payment/bank-transfers` - Havale bildirimleri
- `GET /api/payment/invoices` - Faturalar

### Social
- `GET /api/social/discord/login` - Discord ile giriş
- `GET /api/social/steam/login` - Steam ile giriş
- `GET /api/social/connections` - Bağlı hesaplar
- `GET /api/social/clans` - Klan listesi
- `POST /api/social/clans` - Klan oluştur
- `GET /api/social/achievements` - Başarımlar
- `GET /api/social/friends` - Arkadaşlar

### Management
- `GET /api/management/backups` - Backup listesi
- `POST /api/management/backups/create` - Backup oluştur
- `GET /api/management/resources/{server_id}` - Kaynak kullanımı
- `GET /api/management/tasks` - Zamanlanmış görevler
- `GET /api/management/uptime/{server_id}` - Uptime raporu

### Analytics
- `GET /api/analytics/dashboard` - Dashboard verileri
- `GET /api/analytics/dashboard/charts` - Grafikler
- `GET /api/analytics/players` - Oyuncu istatistikleri
- `GET /api/analytics/revenue` - Gelir raporu
- `GET /api/analytics/export/users` - Kullanıcı export
- `GET /api/analytics/export/revenue` - Gelir export

---

## ✅ Test

```bash
# Security
curl http://localhost:8000/api/security/stats

# Payment
curl http://localhost:8000/api/payment/coupons

# Social
curl http://localhost:8000/api/social/clans

# Analytics
curl http://localhost:8000/api/analytics/dashboard
```
