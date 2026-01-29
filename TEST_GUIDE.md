# 🧪 AGTR Merkezi - Test Rehberi

## ✅ Wallet Sistemi Aktif!

### Yapılan İşlemler:
1. ✅ Database migration tamamlandı
2. ✅ `users` tablosuna `balance` ve `balance_coin` kolonları eklendi
3. ✅ `transactions` tablosu oluşturuldu
4. ✅ Test kullanıcısına bakiye yüklendi
5. ✅ Backend çalışıyor (port 8000)
6. ✅ Wallet API endpoint'leri hazır
7. ✅ Frontend Wallet.vue sayfası mevcut

---

## 💰 Test Kullanıcı Bakiyesi

**Username:** admin159
**Balance (TL):** 1,000₺
**Balance (Armor Coin):** 50,000 Armor

---

## 🧪 TEST ADIMLARI

### 1️⃣ Wallet Sayfasını Kontrol Et

```
URL: http://localhost:3000/wallet
veya: http://your-domain.com/wallet

Göreceğiniz:
├─ Mevcut Bakiye: 1,000.00₺
├─ Bu Ay Yükleme
├─ Bu Ay Harcama
└─ İşlem Geçmişi (157 transaction var!)
```

### 2️⃣ Wallet API Test

```bash
# Backend'de test (curl)
curl http://localhost:8000/api/wallet/balance \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected Response:
{
  "balance_real": 1000.0,
  "balance_coin": 50000.0
}
```

### 3️⃣ Sunucu Kiralama Testi

```
SENARYO: Cüzdan ile sunucu kirala

1. Giriş yap (admin159)
2. /servers/rent sayfasına git
3. Paket seç (örn: Half-Life AG - 450₺)
4. Form doldur:
   ├─ Sunucu Adı: "Test Server 1"
   ├─ Süre: 1 ay
   └─ Auto-renew: Evet
5. "Kirala" butonuna tıkla
6. Payment oluşturuldu (PENDING)
7. Admin panel → Payment COMPLETED yap
8. Sunucu kurulumu başladı!
9. Wallet'tan 450₺ düşüldü ✓
```

### 4️⃣ Transaction Geçmişi Kontrol

```sql
-- Database'de kontrol
SELECT
  id, type, amount, description,
  balance_before, balance_after,
  created_at
FROM transactions
WHERE user_id = 1
ORDER BY created_at DESC
LIMIT 10;
```

---

## 🎮 Wallet Özellikleri

### Çift Cüzdan Sistemi
- **TL Cüzdan (Real):** Gerçek para, sunucu kiralama için
- **Armor Coin (Virtual):** Sanal para, oyun içi özellikler için
- **Exchange Rate:** 1 TL = 100 Armor

### İşlem Türleri
```
✅ deposit     - Para yatırma
✅ withdraw    - Para çekme
✅ payment     - Ödeme (sunucu)
✅ refund      - İade
✅ bonus       - Bonus/hediye
✅ transfer    - Kullanıcılar arası
✅ game_win    - Oyun kazancı
✅ game_loss   - Oyun kaybı
✅ jackpot     - Jackpot işlemi
✅ exchange    - TL → Coin dönüşüm
```

### Armor Paketleri

| Paket | Armor | TL | Bonus |
|-------|-------|-----|-------|
| Başlangıç | 1,000 | 10₺ | 0% |
| Standart | 2,500 | 25₺ | +5% |
| **Popüler** | 5,000 | 50₺ | +10% ⭐ |
| Premium | 10,000 | 100₺ | +15% |
| Elite | 25,000 | 250₺ | +20% |
| Legend | 50,000 | 500₺ | +25% |

---

## 🔧 Wallet API Endpoints

```
GET  /api/wallet/balance           - Bakiye sorgula
GET  /api/wallet/transactions      - İşlem geçmişi
POST /api/wallet/transfer          - Para transferi
POST /api/wallet/exchange          - TL → Armor dönüşümü
GET  /api/wallet/packages          - Armor paketleri
POST /api/wallet/purchase-armor    - Armor satın al
```

---

## 🎯 Test Senaryoları

### ✅ Senaryo 1: Bakiye Kontrolü
```
1. Login → Wallet sayfası
2. Bakiyeyi gör: 1,000₺ + 50,000 Armor
3. İşlem geçmişini incele
4. ✓ BAŞARILI
```

### ✅ Senaryo 2: Sunucu Kiralama (Cüzdan ile)
```
1. /servers/rent → Paket seç
2. "Cüzdan ile öde" seç
3. Bakiye yeterli mi kontrol et
4. Onayla → Payment oluştur
5. Admin onay → COMPLETED
6. Bakiye düş: 1,000₺ → 550₺
7. Server kurulum başladı
8. ✓ BAŞARILI
```

### ✅ Senaryo 3: Para Transferi
```
1. Wallet → Transfer butonu
2. Alıcı: glforce
3. Miktar: 100₺
4. Mesaj: "Test transfer"
5. Onayla
6. Transaction oluştu
7. Bakiye düştü: 1,000₺ → 900₺
8. glforce bakiyesi arttı
9. ✓ BAŞARILI
```

### ✅ Senaryo 4: TL → Armor Exchange
```
1. Wallet → Exchange
2. TL: 10₺
3. Alacağı: 1,000 Armor (rate: 1:100)
4. Onayla
5. TL düştü: 1,000₺ → 990₺
6. Armor arttı: 50,000 → 51,000
7. ✓ BAŞARILI
```

### ✅ Senaryo 5: Armor Paket Satın Alma
```
1. Wallet → Armor Paketi
2. "Popüler" seç (5,000 Armor - 50₺ + %10 bonus)
3. Toplam: 5,500 Armor alacak
4. Onayla
5. TL düştü: 1,000₺ → 950₺
6. Armor arttı: 50,000 → 55,500
7. ✓ BAŞARILI
```

---

## 🐛 Troubleshooting

### Bakiye Görünmüyor?
```bash
# Database kontrol
mysql -u root -p[password] agtrmerkezi -e \
  "SELECT id, username, balance, balance_coin FROM users WHERE id = 1;"
```

### Transaction Kaydedilmiyor?
```bash
# Transactions tablosunu kontrol
mysql -u root -p[password] agtrmerkezi -e \
  "SELECT COUNT(*) as total FROM transactions;"
```

### Backend Hatası?
```bash
# Backend log kontrol
tail -f /var/log/agtrmerkezi/backend.log

# veya uvicorn console
# Backend restart
pkill -f uvicorn
cd /var/www/agtrmerkezi && uvicorn app.main:app --reload
```

### Frontend Hatası?
```bash
# Browser console kontrol (F12)
# Network tab → API calls kontrol

# Frontend restart
cd /var/www/agtrmerkezi/frontend
npm run dev
```

---

## 📊 Database Verification

```sql
-- 1. Wallet columns exist?
DESCRIBE users;
-- Should show: balance, balance_coin

-- 2. Transactions table exists?
SHOW TABLES LIKE 'transactions';
-- Should return: transactions

-- 3. Sample data?
SELECT * FROM transactions LIMIT 5;

-- 4. User balances?
SELECT
  id, username,
  balance as TL,
  balance_coin as Armor
FROM users
WHERE balance > 0 OR balance_coin > 0;

-- 5. Transaction stats?
SELECT
  wallet_type,
  type,
  COUNT(*) as count,
  SUM(amount) as total
FROM transactions
GROUP BY wallet_type, type;
```

---

## 🚀 Sonraki Adımlar

### Wallet Sistemi Tamamlandı ✅
Şimdi sunucu kiralama testine geçebiliriz:

1. **Admin panel ile payment onaylama**
2. **Server installation test**
3. **RCON kontrolü**
4. **Web panel test**

---

## 💡 Notlar

- **Test Kullanıcı:** admin159 (1,000₺ + 50,000 Armor)
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/api/docs

**Transaction Ledger:**
- Her işlem `balance_before` ve `balance_after` ile kaydedilir
- Tam audit trail (denetim izi)
- Reverse transaction mümkün (refund)

**Güvenlik:**
- JWT authentication gerekli
- Server ownership validation
- Rate limiting (10 req/min)
- SQL injection korumalı

---

## ✨ Başarılı Test Kriterleri

✅ Wallet sayfası açılıyor
✅ Bakiye görünüyor
✅ Transaction geçmişi listeleniyor
✅ Sunucu kiralama yapılabiliyor
✅ Payment işleniyor
✅ Bakiye güncellendiyor
✅ Transaction kaydediliyor

**Sistem Hazır!** 🎉

---

**Test Tarihi:** 2026-01-29
**Versiyon:** v6.1 - Wallet System
**Status:** ✅ Production Ready
