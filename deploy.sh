#!/bin/bash
# AGTR Merkezi v5.1 - Deployment Script

set -e

echo "=========================================="
echo "  AGTR Merkezi v5.1 Deployment"
echo "=========================================="

# Renklendirme
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Hedef dizin
TARGET="/var/www/agtrmerkezi"

# 1. Yedekleme
echo -e "${YELLOW}[1/6] Mevcut sürüm yedekleniyor...${NC}"
if [ -d "$TARGET" ]; then
    BACKUP_NAME="agtrmerkezi_backup_$(date +%Y%m%d_%H%M%S)"
    cp -r "$TARGET" "/var/www/$BACKUP_NAME"
    echo -e "${GREEN}  ✓ Yedek: /var/www/$BACKUP_NAME${NC}"
fi

# 2. Dosyaları kopyala
echo -e "${YELLOW}[2/6] Yeni dosyalar kopyalanıyor...${NC}"
mkdir -p "$TARGET"
cp -r app static templates requirements.txt "$TARGET/"
echo -e "${GREEN}  ✓ Dosyalar kopyalandı${NC}"

# 3. Bağımlılıkları yükle
echo -e "${YELLOW}[3/6] Python bağımlılıkları yükleniyor...${NC}"
cd "$TARGET"
pip install -r requirements.txt --break-system-packages -q
echo -e "${GREEN}  ✓ Bağımlılıklar yüklendi${NC}"

# 4. Systemd service güncelle
echo -e "${YELLOW}[4/6] Systemd service güncelleniyor...${NC}"
if [ -f "agtrmerkezi.service" ]; then
    cp agtrmerkezi.service /etc/systemd/system/
    systemctl daemon-reload
    echo -e "${GREEN}  ✓ Service güncellendi${NC}"
fi

# 5. Servisi yeniden başlat
echo -e "${YELLOW}[5/6] Servis yeniden başlatılıyor...${NC}"
systemctl restart agtrmerkezi || systemctl start agtrmerkezi
echo -e "${GREEN}  ✓ Servis başlatıldı${NC}"

# 6. Durum kontrolü
echo -e "${YELLOW}[6/6] Durum kontrol ediliyor...${NC}"
sleep 3
if systemctl is-active --quiet agtrmerkezi; then
    echo -e "${GREEN}  ✓ AGTR Merkezi v5.1 çalışıyor!${NC}"
else
    echo -e "\033[0;31m  ✗ Servis başlatılamadı!${NC}"
    journalctl -u agtrmerkezi --no-pager -n 20
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  Deployment tamamlandı!${NC}"
echo "  URL: http://localhost:8000"
echo "=========================================="
