#!/bin/bash
# Database Migration Runner - Safe Execution
# AGTR Merkezi - Subscription System Migration

set -e  # Exit on error

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║   AGTR Merkezi - Database Migration       ║"
echo "║   Subscription System v1.0                 ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Database bilgileri
DB_HOST="127.0.0.1"
DB_PORT="3306"
DB_NAME="agtrmerkezi"
DB_USER="agtrmerkezi_user"

# Backup dizini
BACKUP_DIR="/var/backups/agtrmerkezi"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_pre_subscription_$TIMESTAMP.sql"

# Dizin oluştur
mkdir -p $BACKUP_DIR

echo -e "${YELLOW}⚠  UYARI: Bu işlem veritabanını değiştirecektir!${NC}"
echo ""
echo "Migration Detayları:"
echo "  - Yeni tablolar: subscriptions, subscription_billing_history"
echo "  - Mevcut veriler: Otomatik migrate edilecek"
echo "  - Rollback: Hazır (gerekirse geri alınabilir)"
echo ""

# Onay iste
read -p "Devam etmek istiyor musunuz? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}❌ Migration iptal edildi${NC}"
    exit 1
fi

# 1. Database bağlantısını test et
echo -e "\n${BLUE}1. Database Bağlantısı Test Ediliyor...${NC}"
if mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p -e "USE $DB_NAME;" 2>/dev/null; then
    echo -e "${GREEN}✓ Bağlantı başarılı${NC}"
else
    echo -e "${RED}✗ Bağlantı başarısız${NC}"
    echo "Lütfen database bilgilerini kontrol edin"
    exit 1
fi

# 2. Backup al
echo -e "\n${BLUE}2. Backup Alınıyor...${NC}"
echo "Backup dosyası: $BACKUP_FILE"

mysqldump -h $DB_HOST -P $DB_PORT -u $DB_USER -p \
    --single-transaction \
    --routines \
    --triggers \
    $DB_NAME > $BACKUP_FILE

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo -e "${GREEN}✓ Backup başarılı ($BACKUP_SIZE)${NC}"
else
    echo -e "${RED}✗ Backup başarısız${NC}"
    exit 1
fi

# 3. Migration dosyasını kontrol et
echo -e "\n${BLUE}3. Migration Dosyası Kontrol Ediliyor...${NC}"
MIGRATION_FILE="/var/www/agtrmerkezi/migrations/add_subscription_tables.sql"

if [ -f "$MIGRATION_FILE" ]; then
    echo -e "${GREEN}✓ Migration dosyası bulundu${NC}"
    LINES=$(wc -l < $MIGRATION_FILE)
    echo "  Toplam satır: $LINES"
else
    echo -e "${RED}✗ Migration dosyası bulunamadı: $MIGRATION_FILE${NC}"
    exit 1
fi

# 4. Migration'ı çalıştır
echo -e "\n${BLUE}4. Migration Çalıştırılıyor...${NC}"
echo -e "${YELLOW}⏳ Lütfen bekleyin...${NC}"

mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p $DB_NAME < $MIGRATION_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migration başarılı${NC}"
else
    echo -e "${RED}✗ Migration başarısız${NC}"
    echo -e "${YELLOW}Backup'tan geri yükleniyor...${NC}"

    mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p $DB_NAME < $BACKUP_FILE

    echo -e "${RED}Migration başarısız oldu ve geri alındı${NC}"
    exit 1
fi

# 5. Verification
echo -e "\n${BLUE}5. Verification (Doğrulama)...${NC}"

# Tablolar oluşturuldu mu?
SUBS_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p -N -e \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$DB_NAME' AND table_name='subscriptions';" 2>/dev/null)

HISTORY_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p -N -e \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$DB_NAME' AND table_name='subscription_billing_history';" 2>/dev/null)

if [ "$SUBS_COUNT" = "1" ] && [ "$HISTORY_COUNT" = "1" ]; then
    echo -e "${GREEN}✓ Tablolar başarıyla oluşturuldu${NC}"
else
    echo -e "${RED}✗ Tablolar oluşturulamadı${NC}"
    exit 1
fi

# Kayıt sayıları
SUB_RECORDS=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p -N -e \
    "SELECT COUNT(*) FROM $DB_NAME.subscriptions;" 2>/dev/null)

echo -e "${GREEN}✓ Subscription kayıtları: $SUB_RECORDS${NC}"

# 6. Özet
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Migration Tamamlandı!             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""
echo "✅ Başarılı İşlemler:"
echo "  - Backup alındı: $BACKUP_FILE"
echo "  - Migration çalıştırıldı"
echo "  - Tablolar oluşturuldu: subscriptions, subscription_billing_history"
echo "  - Mevcut veriler migrate edildi: $SUB_RECORDS kayıt"
echo ""
echo "📝 Sonraki Adımlar:"
echo "  1. Backend'i yeniden başlat: systemctl restart agtrmerkezi"
echo "  2. Scheduler'ı kontrol et: tail -f /var/log/agtrmerkezi/scheduler.log"
echo "  3. Test et: /var/www/agtrmerkezi/run_tests.sh"
echo ""
echo -e "${GREEN}🎉 Migration başarıyla tamamlandı!${NC}"
