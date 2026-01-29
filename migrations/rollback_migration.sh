#!/bin/bash
# Rollback Script - Subscription System Migration

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}"
echo "╔════════════════════════════════════════════╗"
echo "║   ROLLBACK - Subscription Migration        ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

DB_NAME="agtrmerkezi"
DB_USER="agtrmerkezi_user"

echo -e "${YELLOW}⚠  Bu işlem subscription sistemini geri alacak!${NC}"
echo ""
read -p "Emin misiniz? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Rollback iptal edildi"
    exit 0
fi

echo -e "\n${YELLOW}Rollback çalıştırılıyor...${NC}"

mysql -u $DB_USER -p $DB_NAME << 'EOSQL'
START TRANSACTION;

-- Foreign key'leri kaldır
ALTER TABLE payments DROP FOREIGN KEY IF EXISTS payments_ibfk_subscription;
ALTER TABLE payments DROP COLUMN IF EXISTS subscription_id;

-- Son ödeme tarihini kaldır
ALTER TABLE game_servers DROP COLUMN IF EXISTS last_payment_date;

-- Tabloları sil
DROP TABLE IF EXISTS subscription_billing_history;
DROP TABLE IF EXISTS subscriptions;

COMMIT;
EOSQL

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Rollback başarılı${NC}"
else
    echo -e "${RED}✗ Rollback başarısız${NC}"
    exit 1
fi

echo -e "\n${GREEN}Subscription sistemi geri alındı${NC}"
