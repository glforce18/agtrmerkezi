#!/bin/bash

# ============================================
# AGTR v6.0 Forum Modülü - Otomatik Kurulum
# ============================================

set -e  # Hata olursa dur

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Değişkenler
AGTR_PATH="/var/www/agtrmerkezi"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_USER="root"
DB_PASS="sedatim"
DB_NAME="agtrmerkezi"

echo -e "${BLUE}"
echo "============================================"
echo "  AGTR v6.0 Forum Modülü Kurulumu"
echo "============================================"
echo -e "${NC}"

# Kontroller
echo -e "${YELLOW}[1/9] Kontroller yapılıyor...${NC}"

if [ ! -d "$AGTR_PATH" ]; then
    echo -e "${RED}HATA: $AGTR_PATH bulunamadı!${NC}"
    exit 1
fi

if [ ! -d "$SCRIPT_DIR/app" ]; then
    echo -e "${RED}HATA: Kurulum dosyaları bulunamadı! Script'i agtr_v6_full klasöründen çalıştırın.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Kontroller başarılı${NC}"

# Backup
echo -e "${YELLOW}[2/9] Yedek alınıyor...${NC}"
BACKUP_DIR="$AGTR_PATH/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Önemli dosyaları yedekle
[ -f "$AGTR_PATH/app/main.py" ] && cp "$AGTR_PATH/app/main.py" "$BACKUP_DIR/"
[ -f "$AGTR_PATH/app/models/__init__.py" ] && cp "$AGTR_PATH/app/models/__init__.py" "$BACKUP_DIR/"
[ -f "$AGTR_PATH/app/models/user.py" ] && cp "$AGTR_PATH/app/models/user.py" "$BACKUP_DIR/"
[ -d "$AGTR_PATH/app/routes" ] && cp -r "$AGTR_PATH/app/routes" "$BACKUP_DIR/"

echo -e "${GREEN}✓ Yedek alındı: $BACKUP_DIR${NC}"

# Dosyaları kopyala
echo -e "${YELLOW}[3/9] Dosyalar kopyalanıyor...${NC}"

# Dizinleri oluştur
mkdir -p "$AGTR_PATH/app/api/admin"
mkdir -p "$AGTR_PATH/app/models"
mkdir -p "$AGTR_PATH/templates/admin"
mkdir -p "$AGTR_PATH/templates/user"
mkdir -p "$AGTR_PATH/static/css"
mkdir -p "$AGTR_PATH/static/js"

# API dosyaları
cp "$SCRIPT_DIR/app/api/forum.py" "$AGTR_PATH/app/api/"
cp "$SCRIPT_DIR/app/api/admin/forum_categories.py" "$AGTR_PATH/app/api/admin/"
cp "$SCRIPT_DIR/app/api/admin/forum_topics.py" "$AGTR_PATH/app/api/admin/"

# Model
cp "$SCRIPT_DIR/app/models/forum.py" "$AGTR_PATH/app/models/"

# Templates
cp "$SCRIPT_DIR/templates/admin/"*.html "$AGTR_PATH/templates/admin/"
cp "$SCRIPT_DIR/templates/user/"*.html "$AGTR_PATH/templates/user/"

# Static
cp "$SCRIPT_DIR/static/css/agtr-ui.css" "$AGTR_PATH/static/css/"
cp "$SCRIPT_DIR/static/js/agtr-ui.js" "$AGTR_PATH/static/js/"

echo -e "${GREEN}✓ Dosyalar kopyalandı${NC}"

# Router'ları ekle
echo -e "${YELLOW}[4/9] Router'lar ekleniyor...${NC}"

MAIN_PY="$AGTR_PATH/app/main.py"

# Forum router import kontrolü
if ! grep -q "from app.api.forum import" "$MAIN_PY" 2>/dev/null; then
    # İlk import satırından sonra ekle
    sed -i '/^from fastapi/a \
# Forum API routers\
from app.api.forum import router as forum_router\
from app.api.admin.forum_categories import router as forum_categories_router\
from app.api.admin.forum_topics import router as forum_topics_router' "$MAIN_PY"
    echo -e "${GREEN}  ✓ Import'lar eklendi${NC}"
else
    echo -e "${BLUE}  → Import'lar zaten mevcut${NC}"
fi

# Router include kontrolü
if ! grep -q "forum_router" "$MAIN_PY" | grep -q "include_router" 2>/dev/null; then
    # app = FastAPI() satırından sonra veya dosya sonuna ekle
    if grep -q "app.include_router" "$MAIN_PY"; then
        # Mevcut include_router satırlarının sonuna ekle
        LAST_INCLUDE=$(grep -n "app.include_router" "$MAIN_PY" | tail -1 | cut -d: -f1)
        sed -i "${LAST_INCLUDE}a\\
\\
# Forum routers\\
app.include_router(forum_router, prefix=\"/api\")\\
app.include_router(forum_categories_router, prefix=\"/api\")\\
app.include_router(forum_topics_router, prefix=\"/api\")" "$MAIN_PY"
    else
        # Dosya sonuna ekle
        echo '
# Forum routers
app.include_router(forum_router, prefix="/api")
app.include_router(forum_categories_router, prefix="/api")
app.include_router(forum_topics_router, prefix="/api")' >> "$MAIN_PY"
    fi
    echo -e "${GREEN}  ✓ Router'lar eklendi${NC}"
else
    echo -e "${BLUE}  → Router'lar zaten mevcut${NC}"
fi

# Model import ekle
echo -e "${YELLOW}[5/9] Model import'ları ekleniyor...${NC}"

MODELS_INIT="$AGTR_PATH/app/models/__init__.py"

if [ -f "$MODELS_INIT" ]; then
    if ! grep -q "ForumCategory" "$MODELS_INIT" 2>/dev/null; then
        echo '
# Forum models
from app.models.forum import ForumCategory, ForumTopic, ForumReply' >> "$MODELS_INIT"
        echo -e "${GREEN}  ✓ Model import'ları eklendi${NC}"
    else
        echo -e "${BLUE}  → Model import'ları zaten mevcut${NC}"
    fi
else
    # __init__.py yoksa oluştur
    cat > "$MODELS_INIT" << 'EOF'
# Models
from app.models.forum import ForumCategory, ForumTopic, ForumReply
EOF
    echo -e "${GREEN}  ✓ __init__.py oluşturuldu${NC}"
fi

# User model'e relationship ekle
echo -e "${YELLOW}[6/9] User model güncelleniyor...${NC}"

USER_MODEL="$AGTR_PATH/app/models/user.py"

if [ -f "$USER_MODEL" ]; then
    if ! grep -q "forum_topics" "$USER_MODEL" 2>/dev/null; then
        # Class'ın sonuna relationship ekle
        # "class User" bul ve relationship ekle
        sed -i '/class User/,/^class\|^$/{
            /^class [^U]/!{
                /^$/i\
    # Forum relationships\
    forum_topics = relationship("ForumTopic", back_populates="author")\
    forum_replies = relationship("ForumReply", back_populates="author")
            }
        }' "$USER_MODEL"
        
        # Eğer sed işe yaramadıysa manuel ekle
        if ! grep -q "forum_topics" "$USER_MODEL" 2>/dev/null; then
            echo -e "${YELLOW}  ! User model'e manuel ekleme gerekiyor${NC}"
            echo -e "${YELLOW}    Şunu ekleyin: forum_topics = relationship(\"ForumTopic\", back_populates=\"author\")${NC}"
            echo -e "${YELLOW}                 forum_replies = relationship(\"ForumReply\", back_populates=\"author\")${NC}"
        else
            echo -e "${GREEN}  ✓ User model güncellendi${NC}"
        fi
    else
        echo -e "${BLUE}  → User model zaten güncel${NC}"
    fi
else
    echo -e "${YELLOW}  ! User model bulunamadı, manuel ekleme gerekiyor${NC}"
fi

# Base template'lere UI ekle
echo -e "${YELLOW}[7/9] Base template'ler güncelleniyor...${NC}"

update_base_template() {
    local TEMPLATE_FILE="$1"
    local TEMPLATE_NAME="$2"
    
    if [ -f "$TEMPLATE_FILE" ]; then
        # CSS kontrolü
        if ! grep -q "agtr-ui.css" "$TEMPLATE_FILE" 2>/dev/null; then
            # </head> öncesine CSS ekle
            sed -i '/<\/head>/i \    <link rel="stylesheet" href="{{ url_for('\''static'\'', path='\''css/agtr-ui.css'\'') }}">' "$TEMPLATE_FILE"
            echo -e "${GREEN}  ✓ $TEMPLATE_NAME CSS eklendi${NC}"
        fi
        
        # JS kontrolü
        if ! grep -q "agtr-ui.js" "$TEMPLATE_FILE" 2>/dev/null; then
            # </body> öncesine JS ekle
            sed -i '/<\/body>/i \    <script src="{{ url_for('\''static'\'', path='\''js/agtr-ui.js'\'') }}"></script>' "$TEMPLATE_FILE"
            echo -e "${GREEN}  ✓ $TEMPLATE_NAME JS eklendi${NC}"
        fi
    else
        echo -e "${YELLOW}  ! $TEMPLATE_NAME bulunamadı${NC}"
    fi
}

update_base_template "$AGTR_PATH/templates/admin/base.html" "Admin base.html"
update_base_template "$AGTR_PATH/templates/user/base.html" "User base.html"

# Database migration
echo -e "${YELLOW}[8/9] Database migration çalıştırılıyor...${NC}"

if [ -f "$SCRIPT_DIR/migration.sql" ]; then
    mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$SCRIPT_DIR/migration.sql" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✓ Database migration başarılı${NC}"
    else
        echo -e "${YELLOW}  ! Migration hatası, manuel çalıştırın: mysql -u$DB_USER -p $DB_NAME < migration.sql${NC}"
    fi
else
    echo -e "${YELLOW}  ! migration.sql bulunamadı${NC}"
fi

# Forum route'ları ekle
echo -e "${YELLOW}[9/9] Forum route'ları ekleniyor...${NC}"

# Forum routes dosyası oluştur
FORUM_ROUTES="$AGTR_PATH/app/routes/forum.py"

if [ ! -f "$FORUM_ROUTES" ]; then
    mkdir -p "$AGTR_PATH/app/routes"
    cat > "$FORUM_ROUTES" << 'EOF'
# ============================================
# AGTR v6.0 - Forum Page Routes
# ============================================

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.security import get_current_user_optional, get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter(tags=["forum-pages"])
templates = Jinja2Templates(directory="templates")


# ============ Admin Routes ============

@router.get("/admin/forum-categories", response_class=HTMLResponse)
async def admin_forum_categories(request: Request, current_user: User = Depends(get_current_admin_user)):
    return templates.TemplateResponse("admin/forum_categories.html", {"request": request, "user": current_user})


@router.get("/admin/forum-topics", response_class=HTMLResponse)
async def admin_forum_topics(request: Request, current_user: User = Depends(get_current_admin_user)):
    return templates.TemplateResponse("admin/forum_topics.html", {"request": request, "user": current_user})


# ============ User Routes ============

@router.get("/forum", response_class=HTMLResponse)
async def forum_index(request: Request, current_user: User = Depends(get_current_user_optional)):
    return templates.TemplateResponse("user/forum.html", {"request": request, "user": current_user})


@router.get("/forum/category/{category_slug}", response_class=HTMLResponse)
async def forum_category(request: Request, category_slug: str, current_user: User = Depends(get_current_user_optional)):
    return templates.TemplateResponse("user/forum_category.html", {
        "request": request, 
        "user": current_user,
        "category_slug": category_slug
    })


@router.get("/forum/topic/{topic_slug}", response_class=HTMLResponse)
async def forum_topic(request: Request, topic_slug: str, current_user: User = Depends(get_current_user_optional)):
    return templates.TemplateResponse("user/forum_topic.html", {
        "request": request, 
        "user": current_user,
        "topic_slug": topic_slug
    })


@router.get("/forum/new", response_class=HTMLResponse)
async def forum_new_topic(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("user/forum_new.html", {"request": request, "user": current_user})


@router.get("/forum/all", response_class=HTMLResponse)
async def forum_all_topics(request: Request, current_user: User = Depends(get_current_user_optional)):
    return templates.TemplateResponse("user/forum_category.html", {
        "request": request, 
        "user": current_user,
        "category_slug": "all"
    })
EOF
    echo -e "${GREEN}  ✓ Forum routes dosyası oluşturuldu${NC}"
    
    # main.py'e forum routes ekle
    if ! grep -q "from app.routes.forum" "$MAIN_PY" 2>/dev/null; then
        sed -i '/^from fastapi/a from app.routes.forum import router as forum_pages_router' "$MAIN_PY"
        
        # include_router ekle
        if grep -q "app.include_router" "$MAIN_PY"; then
            LAST_INCLUDE=$(grep -n "app.include_router" "$MAIN_PY" | tail -1 | cut -d: -f1)
            sed -i "${LAST_INCLUDE}a app.include_router(forum_pages_router)" "$MAIN_PY"
        fi
        echo -e "${GREEN}  ✓ Forum routes main.py'e eklendi${NC}"
    fi
else
    echo -e "${BLUE}  → Forum routes zaten mevcut${NC}"
fi

# Restart
echo ""
echo -e "${YELLOW}Servis yeniden başlatılıyor...${NC}"
systemctl restart agtrmerkezi 2>/dev/null || echo -e "${YELLOW}! Servis restart edilemedi, manuel yapın: sudo systemctl restart agtrmerkezi${NC}"

# Özet
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  KURULUM TAMAMLANDI!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Eklenen özellikler:"
echo -e "  ${GREEN}✓${NC} Forum Kategori Yönetimi (Admin)"
echo -e "  ${GREEN}✓${NC} Forum Konu Yönetimi (Admin)"
echo -e "  ${GREEN}✓${NC} Forum Ana Sayfa (User)"
echo -e "  ${GREEN}✓${NC} Kategori/Konu/Yanıt Sayfaları (User)"
echo -e "  ${GREEN}✓${NC} Toast/Modal UI Sistemi"
echo ""
echo -e "Erişim adresleri:"
echo -e "  Admin: ${BLUE}/admin/forum-categories${NC}"
echo -e "  Admin: ${BLUE}/admin/forum-topics${NC}"
echo -e "  User:  ${BLUE}/forum${NC}"
echo ""
echo -e "Yedek konumu: ${YELLOW}$BACKUP_DIR${NC}"
echo ""

# Manuel kontrol gereken yerler
echo -e "${YELLOW}Manuel kontrol gereken yerler:${NC}"
echo -e "  1. User model'de forum_topics/forum_replies relationship'leri var mı?"
echo -e "  2. Admin sidebar'a forum linkleri eklenmiş mi?"
echo -e "  3. User navbar'a forum linki eklenmiş mi?"
echo ""
echo -e "Sorun olursa yedekten geri dön: ${YELLOW}cp $BACKUP_DIR/* $AGTR_PATH/app/${NC}"
