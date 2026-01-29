# 🚀 AGTR Merkezi - Deployment Kılavuzu
## Subscription System v1.0

**Hazırlayan:** Claude Code Assistant
**Tarih:** 2026-01-29
**Versiyon:** 1.0.0

---

## 📋 Ön Gereksinimler

### Sistem Gereksinimleri
- Python 3.10+
- MySQL 8.0+
- Node.js 18+
- Redis 6+
- 2GB+ RAM
- 10GB+ Disk

### Python Bağımlılıkları
```bash
pip install -r requirements.txt
# Yeni eklenenler:
# - python-dateutil
# - apscheduler
```

### Backup
```bash
# ÖNCE MUTLAKA BACKUP ALIN!
mysqldump -u agtrmerkezi_user -p agtrmerkezi > backup_$(date +%Y%m%d).sql
```

---

## 🎯 Deployment Adımları

### 1️⃣ Pre-Deployment Kontroller

```bash
cd /var/www/agtrmerkezi

# Syntax check
python3 -m py_compile app/services/*.py
python3 -m py_compile app/tasks/*.py
python3 -m py_compile app/api/*.py

# Test çalıştır
./run_tests.sh
```

### 2️⃣ Database Migration

```bash
cd /var/www/agtrmerkezi/migrations

# Migration çalıştır (otomatik backup alır)
./run_migration.sh

# Doğrulama
mysql -u agtrmerkezi_user -p agtrmerkezi -e "
  SELECT COUNT(*) as subscription_count FROM subscriptions;
  SELECT COUNT(*) as history_count FROM subscription_billing_history;
"
```

### 3️⃣ Backend Deployment

```bash
cd /var/www/agtrmerkezi

# Dependencies güncelle
pip install -r requirements.txt

# Servis durdur
systemctl stop agtrmerkezi

# Kod güncellemelerini kontrol et
git status  # veya manuel kontrol

# Servis başlat
systemctl start agtrmerkezi

# Log kontrol
tail -f /var/log/agtrmerkezi/app.log
```

### 4️⃣ Scheduler Kontrolü

```bash
# Scheduler loglarını kontrol et
tail -f /var/log/agtrmerkezi/scheduler.log

# Job'ların kayıtlı olduğunu doğrula
# Log'da şu satırları aramalısınız:
# - "Subscription billing job registered"
# - "Expiry notification job registered"
# - "Status sync job registered"
# - "Resource monitoring job registered"
```

### 5️⃣ Frontend Build & Deploy

```bash
cd /var/www/agtrmerkezi/frontend

# Dependencies güncelle
npm install

# Production build
npm run build

# Build output kontrol
ls -lh dist/

# Static files backend'e kopyalandı mı kontrol et
ls -lh /var/www/agtrmerkezi/static/dist/
```

### 6️⃣ Post-Deployment Verification

```bash
# 1. API Health Check
curl -X GET http://localhost:8000/health

# 2. Subscription API test
curl -X GET http://localhost:8000/api/subscriptions/my-subscriptions \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Scheduler status
# İlk billing job: Ertesi gün saat 03:00
# İlk notification job: Ertesi gün saat 09:00
```

---

## 🔄 Kademeli Rollout (Önerilen)

### Faz 1: %10 Kullanıcı (İlk 3 Gün)
```bash
# Feature flag ile kademeli açılış
# app/core/config.py içinde:
SUBSCRIPTION_ENABLED_PERCENTAGE = 10

# Sadece yeni sunucu kiralamalarına uygulanır
# Mevcut sunucular etkilenmez
```

### Faz 2: %50 Kullanıcı (Gün 4-7)
```bash
SUBSCRIPTION_ENABLED_PERCENTAGE = 50
```

### Faz 3: %100 Kullanıcı (Gün 8+)
```bash
SUBSCRIPTION_ENABLED_PERCENTAGE = 100
```

---

## 📊 Monitoring

### Log Dosyaları
```bash
# Ana uygulama
tail -f /var/log/agtrmerkezi/app.log

# Scheduler (background jobs)
tail -f /var/log/agtrmerkezi/scheduler.log

# Nginx (web server)
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Önemli Metrikler

**İlk 24 Saat:**
- [ ] Yeni subscription oluşturma sayısı
- [ ] API hata oranı (< %1 olmalı)
- [ ] Database query performansı
- [ ] Email teslimat oranı

**İlk 7 Gün:**
- [ ] Billing başarı oranı (> %95)
- [ ] Grace period oranı
- [ ] Suspension oranı
- [ ] User satisfaction

**İlk 30 Gün:**
- [ ] Tüm success metrics (FINAL_IMPLEMENTATION_REPORT.md'de)

---

## ⚠️ Troubleshooting

### Sorun 1: Migration Başarısız
```bash
# Rollback yap
cd /var/www/agtrmerkezi/migrations
./rollback_migration.sh

# Backup'tan geri yükle
mysql -u agtrmerkezi_user -p agtrmerkezi < /var/backups/agtrmerkezi/backup_*.sql
```

### Sorun 2: Scheduler Çalışmıyor
```bash
# Scheduler logunu kontrol et
tail -100 /var/log/agtrmerkezi/scheduler.log

# Manuel job test
cd /var/www/agtrmerkezi
python3 -c "from app.tasks.billing_job import process_subscription_billing; process_subscription_billing()"
```

### Sorun 3: Email Gönderilmiyor
```bash
# Email service test
python3 -c "
from app.services.email import EmailService
service = EmailService()
# Test email gönder
"

# SMTP ayarlarını kontrol et
cat app/core/config.py | grep SMTP
```

### Sorun 4: Yüksek Database Load
```bash
# Index'leri kontrol et
mysql -u agtrmerkezi_user -p agtrmerkezi -e "
  SHOW INDEX FROM subscriptions;
  SHOW INDEX FROM subscription_billing_history;
"

# Slow query log
mysql -u agtrmerkezi_user -p -e "
  SET GLOBAL slow_query_log = 'ON';
  SET GLOBAL long_query_time = 1;
"
```

---

## 🔙 Rollback Plan

### Acil Rollback (Kritik Hata Durumunda)

```bash
# 1. Scheduler'ı durdur
systemctl stop agtrmerkezi

# 2. Database rollback
cd /var/www/agtrmerkezi/migrations
./rollback_migration.sh

# 3. Veya backup'tan geri yükle
mysql -u agtrmerkezi_user -p agtrmerkezi < /var/backups/agtrmerkezi/backup_*.sql

# 4. Eski kodu geri al (git kullanıyorsanız)
git revert HEAD
# veya
git checkout PREVIOUS_COMMIT

# 5. Servisi başlat
systemctl start agtrmerkezi
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Backup alındı
- [ ] Testler çalıştırıldı (./run_tests.sh)
- [ ] Syntax check yapıldı
- [ ] Rollback planı hazır

### Deployment
- [ ] Migration başarılı
- [ ] Backend deploy edildi
- [ ] Frontend build edildi
- [ ] Scheduler çalışıyor
- [ ] Loglar kontrol edildi

### Post-Deployment
- [ ] API endpoint'ler çalışıyor
- [ ] Email gönderimi test edildi
- [ ] İlk subscription oluşturuldu
- [ ] Monitoring setup yapıldı

### İlk 24 Saat
- [ ] Hata oranları normal
- [ ] Database performansı iyi
- [ ] Email delivery > %98
- [ ] Kullanıcı şikayeti yok

---

## 📞 Acil Durum İletişim

**Kritik hata durumunda:**
1. Servisi durdur: `systemctl stop agtrmerkezi`
2. Rollback yap
3. Logları kaydet
4. Teknik ekibe bildir

---

## 🎉 Başarı Kriterleri

Deployment başarılı sayılır:
- ✅ Tüm testler geçti
- ✅ Migration hatasız tamamlandı
- ✅ Scheduler job'ları çalışıyor
- ✅ İlk 24 saatte kritik hata yok
- ✅ Email delivery > %95
- ✅ API response time < 500ms

---

**Son Güncelleme:** 2026-01-29
**Deployment Durumu:** HAZIR ✅
