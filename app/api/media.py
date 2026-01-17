# ============================================
# AGTR Merkezi - Media Management API
# Dosya: app/api/media.py
# Logo, ikon ve görsel yönetimi
# ============================================

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.security import get_current_admin
from app.models.database import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/media", tags=["Media"])

# Upload dizinleri
UPLOAD_DIR = Path("/var/www/agtrmerkezi/static/images")
GAMES_DIR = UPLOAD_DIR / "games"
FORUM_DIR = UPLOAD_DIR / "forum"
SITE_DIR = UPLOAD_DIR / "site"
BANNERS_DIR = UPLOAD_DIR / "banners"
PLAYER_MODELS_DIR = UPLOAD_DIR / "player_models"
PACKAGE_ICONS_DIR = UPLOAD_DIR / "package_icons"
VIP_ICONS_DIR = UPLOAD_DIR / "vip_icons"

# İzin verilen dosya türleri
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (büyük banner'lar için artırıldı)


# ============ Pydantic Schemas ============

class MediaResponse(BaseModel):
    url: str
    filename: str
    size: int
    uploaded_at: str


class GameLogoConfig(BaseModel):
    game_type: str  # hldm, ag, cs16
    logo_url: str
    icon_url: Optional[str] = None


class ForumIconConfig(BaseModel):
    category_id: int
    icon_class: Optional[str] = None  # Font Awesome class
    custom_icon_url: Optional[str] = None


# ============ Helper Functions ============

def get_file_extension(filename: str) -> str:
    """Dosya uzantısını al"""
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str) -> bool:
    """Dosya türü izinli mi?"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """Benzersiz dosya adı oluştur"""
    ext = get_file_extension(original_filename)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name


async def save_upload_file(upload_file: UploadFile, destination_dir: Path) -> dict:
    """Dosyayı kaydet"""
    logger.info(f"📦 save_upload_file çağrıldı - File: {upload_file.filename}, Dest: {destination_dir}")

    # Dosya boyutu kontrolü
    content = await upload_file.read()
    logger.info(f"📏 Dosya okundu - Boyut: {len(content)} bytes")

    if len(content) > MAX_FILE_SIZE:
        logger.error(f"❌ Dosya çok büyük: {len(content)} > {MAX_FILE_SIZE}")
        raise HTTPException(status_code=400, detail="Dosya boyutu 5MB'dan büyük olamaz")

    # Dosya türü kontrolü
    if not is_allowed_file(upload_file.filename):
        logger.error(f"❌ İzin verilmeyen dosya türü: {upload_file.filename}")
        raise HTTPException(
            status_code=400,
            detail=f"İzin verilen formatlar: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Klasör oluştur
    destination_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 Klasör hazırlandı: {destination_dir}")

    # Benzersiz dosya adı
    filename = generate_unique_filename(upload_file.filename)
    file_path = destination_dir / filename
    logger.info(f"💾 Dosya kaydedilecek: {file_path}")

    # Dosyayı kaydet
    with open(file_path, "wb") as f:
        f.write(content)
    logger.info(f"✅ Dosya kaydedildi")

    # URL oluştur
    relative_path = file_path.relative_to(Path("/var/www/agtrmerkezi/static"))
    url = f"/static/{relative_path.as_posix()}"
    logger.info(f"🔗 URL oluşturuldu: {url}")

    return {
        "url": url,
        "filename": filename,
        "size": len(content),
        "uploaded_at": datetime.now().isoformat()
    }


# ============ Oyun Logo API ============

@router.post("/games/upload", response_model=MediaResponse)
async def upload_game_logo(
    file: UploadFile = File(...),
    game_type: str = Form(...),
    current_user: User = Depends(get_current_admin)
):
    """Oyun logosu yükle"""
    if game_type not in ["hldm", "ag", "cs16"]:
        raise HTTPException(status_code=400, detail="Geçersiz oyun türü")

    result = await save_upload_file(file, GAMES_DIR / game_type)
    return result


@router.get("/games/list")
async def list_game_logos():
    """Mevcut oyun logolarını listele"""
    logos = {}

    for game_type in ["hldm", "ag", "cs16"]:
        game_dir = GAMES_DIR / game_type
        if game_dir.exists():
            files = []
            for ext in ALLOWED_EXTENSIONS:
                files.extend(game_dir.glob(f"*{ext}"))

            if files:
                # En son yüklenen dosyayı al
                latest = max(files, key=lambda f: f.stat().st_mtime)
                relative_path = latest.relative_to(Path("/var/www/agtrmerkezi/static"))
                logos[game_type] = f"/static/{relative_path.as_posix()}"

    return logos


# ============ Forum İkon API ============

@router.post("/forum/upload", response_model=MediaResponse)
async def upload_forum_icon(
    file: UploadFile = File(...),
    category_slug: str = Form(...),
    current_user: User = Depends(get_current_admin)
):
    """Forum kategori ikonu yükle"""
    result = await save_upload_file(file, FORUM_DIR / category_slug)
    return result


@router.get("/forum/list")
async def list_forum_icons():
    """Forum ikonlarını listele"""
    icons = {}

    if FORUM_DIR.exists():
        for category_dir in FORUM_DIR.iterdir():
            if category_dir.is_dir():
                files = []
                for ext in ALLOWED_EXTENSIONS:
                    files.extend(category_dir.glob(f"*{ext}"))

                if files:
                    latest = max(files, key=lambda f: f.stat().st_mtime)
                    relative_path = latest.relative_to(Path("/var/www/agtrmerkezi/static"))
                    icons[category_dir.name] = f"/static/{relative_path.as_posix()}"

    return icons


# ============ Site Logo/Favicon API ============

@router.post("/site/upload", response_model=MediaResponse)
async def upload_site_media(
    file: UploadFile = File(...),
    media_type: str = Form(...),  # logo, favicon, banner
    current_user: User = Depends(get_current_admin)
):
    """Site görseli yükle (logo, favicon, banner)"""
    logger.info(f"🚀 Site media upload başladı - User: {current_user.username}, Type: {media_type}, File: {file.filename}")

    if media_type not in ["logo", "favicon", "banner", "og-image"]:
        logger.error(f"❌ Geçersiz medya türü: {media_type}")
        raise HTTPException(status_code=400, detail="Geçersiz medya türü")

    try:
        result = await save_upload_file(file, SITE_DIR / media_type)
        logger.info(f"✅ Upload başarılı: {result['url']}")
        return result
    except Exception as e:
        logger.error(f"❌ Upload hatası: {str(e)}")
        raise


@router.get("/site/list")
async def list_site_media():
    """Site görsellerini listele"""
    media = {}

    for media_type in ["logo", "favicon", "banner", "og-image"]:
        media_dir = SITE_DIR / media_type
        if media_dir.exists():
            files = []
            for ext in ALLOWED_EXTENSIONS:
                files.extend(media_dir.glob(f"*{ext}"))

            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                relative_path = latest.relative_to(Path("/var/www/agtrmerkezi/static"))
                media[media_type] = f"/static/{relative_path.as_posix()}"

    return media


# ============ Genel Dosya Yönetimi ============

@router.delete("/delete")
async def delete_media(
    url: str,
    current_user: User = Depends(get_current_admin)
):
    """Görsel dosyasını sil"""
    # URL'den dosya yolunu çıkar
    if not url.startswith("/static/"):
        raise HTTPException(status_code=400, detail="Geçersiz URL")

    file_path = Path("/var/www/agtrmerkezi") / url.lstrip("/")

    # Güvenlik kontrolü - sadece images altındaki dosyalar silinebilir
    if not str(file_path).startswith(str(UPLOAD_DIR)):
        raise HTTPException(status_code=403, detail="Bu dosya silinemez")

    if file_path.exists():
        file_path.unlink()
        return {"success": True, "message": "Dosya silindi"}
    else:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")


@router.get("/default-icons")
async def get_default_icons():
    """Varsayılan Font Awesome ikonları"""
    return {
        "game_icons": {
            "hldm": "fas fa-gamepad",
            "ag": "fas fa-running",
            "cs16": "fas fa-crosshairs"
        },
        "forum_icons": [
            "fas fa-comments",
            "fas fa-question-circle",
            "fas fa-bullhorn",
            "fas fa-users",
            "fas fa-trophy",
            "fas fa-bug",
            "fas fa-lightbulb",
            "fas fa-star",
            "fas fa-fire",
            "fas fa-crown",
            "fas fa-shield-alt",
            "fas fa-code"
        ]
    }


# ============ Banner API ============

@router.post("/banners/upload", response_model=MediaResponse)
async def upload_banner(
    file: UploadFile = File(...),
    category: str = Form(default="general"),  # general, homepage, campaign, promo
    current_user: User = Depends(get_current_admin)
):
    """Banner yükle"""
    logger.info(f"🎨 Banner upload - Category: {category}, File: {file.filename}")

    result = await save_upload_file(file, BANNERS_DIR / category)
    logger.info(f"✅ Banner uploaded: {result['url']}")
    return result


@router.get("/banners/list")
async def list_banners():
    """Tüm banner'ları listele"""
    banners = {}

    if BANNERS_DIR.exists():
        for category_dir in BANNERS_DIR.iterdir():
            if category_dir.is_dir():
                files = []
                for ext in ALLOWED_EXTENSIONS:
                    files.extend(category_dir.glob(f"*{ext}"))

                if files:
                    banners[category_dir.name] = [
                        {
                            "url": f"/static/{f.relative_to(Path('/var/www/agtrmerkezi/static')).as_posix()}",
                            "filename": f.name,
                            "size": f.stat().st_size,
                            "modified": f.stat().st_mtime
                        }
                        for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
                    ]

    return banners


# ============ Player Models API ============

@router.post("/player-models/upload", response_model=MediaResponse)
async def upload_player_model(
    file: UploadFile = File(...),
    game_type: str = Form(...),  # cs16, hldm
    current_user: User = Depends(get_current_admin)
):
    """Player model görseli yükle"""
    logger.info(f"👤 Player model upload - Game: {game_type}, File: {file.filename}")

    if game_type not in ["cs16", "hldm"]:
        raise HTTPException(status_code=400, detail="Geçersiz oyun türü (cs16 veya hldm)")

    result = await save_upload_file(file, PLAYER_MODELS_DIR / game_type)
    logger.info(f"✅ Player model uploaded: {result['url']}")
    return result


@router.get("/player-models/list")
async def list_player_models():
    """Player model görsellerini listele"""
    models = {}

    if PLAYER_MODELS_DIR.exists():
        for game_dir in PLAYER_MODELS_DIR.iterdir():
            if game_dir.is_dir():
                files = []
                for ext in ALLOWED_EXTENSIONS:
                    files.extend(game_dir.glob(f"*{ext}"))

                if files:
                    models[game_dir.name] = [
                        {
                            "url": f"/static/{f.relative_to(Path('/var/www/agtrmerkezi/static')).as_posix()}",
                            "filename": f.name,
                            "size": f.stat().st_size,
                            "modified": f.stat().st_mtime
                        }
                        for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
                    ]

    return models


# ============ VIP/Premium Icons API ============

@router.post("/vip-icons/upload", response_model=MediaResponse)
async def upload_vip_icon(
    file: UploadFile = File(...),
    tier: str = Form(default="vip"),  # vip, premium, ultimate
    current_user: User = Depends(get_current_admin)
):
    """VIP/Premium ikon yükle"""
    logger.info(f"👑 VIP icon upload - Tier: {tier}, File: {file.filename}")

    result = await save_upload_file(file, VIP_ICONS_DIR / tier)
    logger.info(f"✅ VIP icon uploaded: {result['url']}")
    return result


@router.get("/vip-icons/list")
async def list_vip_icons():
    """VIP/Premium ikonları listele"""
    icons = {}

    if VIP_ICONS_DIR.exists():
        for tier_dir in VIP_ICONS_DIR.iterdir():
            if tier_dir.is_dir():
                files = []
                for ext in ALLOWED_EXTENSIONS:
                    files.extend(tier_dir.glob(f"*{ext}"))

                if files:
                    icons[tier_dir.name] = [
                        {
                            "url": f"/static/{f.relative_to(Path('/var/www/agtrmerkezi/static')).as_posix()}",
                            "filename": f.name,
                            "size": f.stat().st_size,
                            "modified": f.stat().st_mtime
                        }
                        for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
                    ]

    return icons


# ============ Package Icons/Banners API ============

@router.post("/package-media/upload", response_model=MediaResponse)
async def upload_package_media(
    file: UploadFile = File(...),
    media_type: str = Form(...),  # icon, banner
    package_slug: str = Form(default="general"),
    current_user: User = Depends(get_current_admin)
):
    """Paket görseli (icon/banner) yükle"""
    logger.info(f"📦 Package media upload - Type: {media_type}, Package: {package_slug}, File: {file.filename}")

    if media_type not in ["icon", "banner"]:
        raise HTTPException(status_code=400, detail="media_type 'icon' veya 'banner' olmalı")

    result = await save_upload_file(file, PACKAGE_ICONS_DIR / media_type / package_slug)
    logger.info(f"✅ Package media uploaded: {result['url']}")
    return result


@router.get("/package-media/list")
async def list_package_media():
    """Paket görsellerini listele"""
    media = {"icons": {}, "banners": {}}

    if PACKAGE_ICONS_DIR.exists():
        for media_type in ["icon", "banner"]:
            type_dir = PACKAGE_ICONS_DIR / media_type
            if type_dir.exists():
                for package_dir in type_dir.iterdir():
                    if package_dir.is_dir():
                        files = []
                        for ext in ALLOWED_EXTENSIONS:
                            files.extend(package_dir.glob(f"*{ext}"))

                        if files:
                            media[media_type + "s"][package_dir.name] = [
                                {
                                    "url": f"/static/{f.relative_to(Path('/var/www/agtrmerkezi/static')).as_posix()}",
                                    "filename": f.name,
                                    "size": f.stat().st_size,
                                    "modified": f.stat().st_mtime
                                }
                                for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
                            ]

    return media


# ============ All Media Listing ============

@router.get("/all")
async def list_all_media():
    """Tüm görselleri kategorilere göre listele"""
    return {
        "site": await list_site_media(),
        "games": await list_game_logos(),
        "forum": await list_forum_icons(),
        "banners": await list_banners(),
        "player_models": await list_player_models(),
        "vip_icons": await list_vip_icons(),
        "package_media": await list_package_media()
    }
