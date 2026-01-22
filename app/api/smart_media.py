"""
AGTR Merkezi - Smart Media Upload API
Akıllı logo/banner algılama ve otomatik yerleştirme
"""

import io
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image
from pydantic import BaseModel

from app.core.security import get_current_admin
from app.models.database import User

router = APIRouter(prefix="/api/smart-media", tags=["Smart Media"])

# Upload dizinleri
STATIC_DIR = Path("/var/www/agtrmerkezi/static/images")

# Akıllı kategori tanıma patterns (Genişletilmiş)
CATEGORY_PATTERNS = {
    'cs16': ['cs', 'counter', 'strike', 'cs16', 'cs1.6', 'cstrike'],
    'hldm': ['half', 'life', 'hl', 'hldm', 'lambda', 'gordon', 'crowbar'],
    'ag': ['ag', 'adrenaline', 'gamer', 'aghl'],
    'vip': ['vip', 'premium', 'ultimate', 'badge', 'crown', 'gold', 'platinum'],
    'player': ['player', 'model', 'character', 'terrorist', 'ct', 'skin'],
    'banner': ['banner', 'hero', 'promo', 'kampanya', 'slide', 'carousel'],
    'logo': ['logo', 'brand', 'icon', 'emblem'],
    'forum': ['forum', 'category', 'topic', 'discussion'],
    'package': ['package', 'plan', 'server', 'hosting'],
    'favicon': ['favicon', 'fav', 'ico'],
    'og': ['og', 'social', 'share', 'preview'],
    'avatar': ['avatar', 'profile', 'user'],
}


class SmartUploadResponse(BaseModel):
    success: bool
    category: str
    subcategory: Optional[str]
    files: List[dict]
    message: str


def detect_category(filename: str) -> tuple:
    """Dosya adından akıllıca kategori belirle"""
    filename_lower = filename.lower()

    # Önce kesin eşleşmeleri kontrol et
    for category, keywords in CATEGORY_PATTERNS.items():
        for keyword in keywords:
            if keyword in filename_lower:
                # Alt kategori belirle
                subcategory = None
                if category in ['cs16', 'hldm', 'ag']:
                    subcategory = category  # Oyun logoları için
                elif 'vip' in filename_lower:
                    subcategory = 'vip'
                elif 'premium' in filename_lower:
                    subcategory = 'premium'
                elif 'ultimate' in filename_lower:
                    subcategory = 'ultimate'

                return (category, subcategory)

    # Varsayılan: banner
    return ('banner', 'general')


def optimize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """Görsel optimizasyonu"""
    # RGBA'ya çevir (transparanlık için)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Boyut optimizasyonu
    if image.width > max_size or image.height > max_size:
        ratio = min(max_size/image.width, max_size/image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    return image


@router.post("/upload", response_model=SmartUploadResponse)
async def smart_upload(
    files: List[UploadFile] = File(...),
    force_category: Optional[str] = Form(None),
    current_user: User = Depends(get_current_admin)
):
    """
    Akıllı çoklu dosya yükleme
    - Otomatik kategori algılama
    - Otomatik optimizasyon
    - Hem PNG hem WebP oluşturma
    """

    uploaded_files = []
    detected_category = None
    detected_subcategory = None

    for upload_file in files:
        try:
            # Dosyayı oku
            content = await upload_file.read()
            image = Image.open(io.BytesIO(content))

            # Kategori belirle
            if force_category:
                category = force_category
                subcategory = None
            else:
                category, subcategory = detect_category(upload_file.filename)

            if not detected_category:
                detected_category = category
                detected_subcategory = subcategory

            # Optimize et
            image = optimize_image(image)

            # Hedef klasör belirle
            if category in ['cs16', 'hldm', 'ag']:
                dest_dir = STATIC_DIR / "games" / category
            elif category == 'vip':
                tier = subcategory or 'vip'
                dest_dir = STATIC_DIR / "vip_icons" / tier
            elif category == 'player':
                game = subcategory or 'cs16'
                dest_dir = STATIC_DIR / "player_models" / game
            elif category == 'banner':
                dest_dir = STATIC_DIR / "banners" / (subcategory or 'general')
            elif category == 'forum':
                dest_dir = STATIC_DIR / "forum"
            elif category == 'package':
                dest_dir = STATIC_DIR / "package_icons"
            elif category == 'favicon':
                dest_dir = STATIC_DIR / "site" / "favicon"
            elif category == 'og':
                dest_dir = STATIC_DIR / "site" / "og"
            elif category == 'avatar':
                dest_dir = STATIC_DIR / "avatars"
            else:
                dest_dir = STATIC_DIR / "site" / "logo"

            dest_dir.mkdir(parents=True, exist_ok=True)

            # Dosya adı oluştur
            base_name = Path(upload_file.filename).stem
            safe_name = re.sub(r'[^a-z0-9-]', '-', base_name.lower())

            # PNG kaydet
            png_path = dest_dir / f"{safe_name}.png"
            image.save(png_path, 'PNG', optimize=True, compress_level=9)

            # WebP kaydet
            webp_path = dest_dir / f"{safe_name}.webp"
            image.save(webp_path, 'WEBP', quality=85, method=6)

            # URL'leri oluştur
            relative_png = png_path.relative_to(STATIC_DIR.parent)
            relative_webp = webp_path.relative_to(STATIC_DIR.parent)

            uploaded_files.append({
                "filename": upload_file.filename,
                "category": category,
                "subcategory": subcategory,
                "png_url": f"/{relative_png.as_posix()}",
                "webp_url": f"/{relative_webp.as_posix()}",
                "size": {
                    "width": image.width,
                    "height": image.height
                }
            })

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Dosya işlenemedi: {str(e)}")

    return SmartUploadResponse(
        success=True,
        category=detected_category,
        subcategory=detected_subcategory,
        files=uploaded_files,
        message=f"{len(uploaded_files)} dosya başarıyla yüklendi ve optimize edildi!"
    )


@router.post("/upload-from-clipboard")
async def upload_from_clipboard(
    image_data: str = Form(...),
    filename: str = Form(default="clipboard"),
    category: Optional[str] = Form(None),
    current_user: User = Depends(get_current_admin)
):
    """Clipboard'dan (Ctrl+V) görsel yükleme"""

    try:
        import base64

        # Base64 decode
        if ',' in image_data:
            image_data = image_data.split(',')[1]

        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))

        # Kategori belirle
        if not category:
            category, subcategory = detect_category(filename)
        else:
            subcategory = None

        # Optimize et
        image = optimize_image(image)

        # Hedef klasör (aynı mantık)
        if category in ['cs16', 'hldm', 'ag']:
            dest_dir = STATIC_DIR / "games" / category
        elif category == 'vip':
            dest_dir = STATIC_DIR / "vip_icons" / (subcategory or 'vip')
        elif category == 'player':
            dest_dir = STATIC_DIR / "player_models" / (subcategory or 'cs16')
        elif category == 'banner':
            dest_dir = STATIC_DIR / "banners" / (subcategory or 'general')
        elif category == 'forum':
            dest_dir = STATIC_DIR / "forum"
        elif category == 'package':
            dest_dir = STATIC_DIR / "package_icons"
        elif category == 'favicon':
            dest_dir = STATIC_DIR / "site" / "favicon"
        elif category == 'og':
            dest_dir = STATIC_DIR / "site" / "og"
        elif category == 'avatar':
            dest_dir = STATIC_DIR / "avatars"
        else:
            dest_dir = STATIC_DIR / "site" / "logo"

        dest_dir.mkdir(parents=True, exist_ok=True)

        # Timestamp ile unique dosya adı
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"clipboard_{timestamp}"

        # Kaydet
        png_path = dest_dir / f"{base_name}.png"
        webp_path = dest_dir / f"{base_name}.webp"

        image.save(png_path, 'PNG', optimize=True, compress_level=9)
        image.save(webp_path, 'WEBP', quality=85, method=6)

        return {
            "success": True,
            "png_url": f"/static/images/{png_path.relative_to(STATIC_DIR)}",
            "webp_url": f"/static/images/{webp_path.relative_to(STATIC_DIR)}",
            "category": category,
            "message": "Clipboard'dan görsel yüklendi!"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/gallery")
async def get_smart_gallery():
    """Tüm görselleri kategorize ederek listele"""

    gallery = {
        "games": {},
        "vip": {},
        "players": {},
        "banners": {},
        "forum": [],
        "packages": [],
        "site": [],
        "avatars": []
    }

    # Oyun logoları
    for game in ['cs16', 'hldm', 'ag']:
        game_dir = STATIC_DIR / "games" / game
        if game_dir.exists():
            files = []
            for ext in ['.png', '.webp', '.jpg', '.svg']:
                files.extend(game_dir.glob(f"*{ext}"))

            gallery['games'][game] = [
                {
                    "url": f"/static/images/{f.relative_to(STATIC_DIR)}",
                    "filename": f.name,
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime
                }
                for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
            ]

    # VIP icons
    vip_dir = STATIC_DIR / "vip_icons"
    if vip_dir.exists():
        for tier_dir in vip_dir.iterdir():
            if tier_dir.is_dir():
                files = []
                for ext in ['.png', '.webp', '.svg']:
                    files.extend(tier_dir.glob(f"*{ext}"))

                gallery['vip'][tier_dir.name] = [
                    {
                        "url": f"/static/images/{f.relative_to(STATIC_DIR)}",
                        "filename": f.name,
                        "size": f.stat().st_size
                    }
                    for f in files
                ]

    # Player models
    player_dir = STATIC_DIR / "player_models"
    if player_dir.exists():
        for game_dir in player_dir.iterdir():
            if game_dir.is_dir():
                files = []
                for ext in ['.png', '.webp', '.jpg']:
                    files.extend(game_dir.glob(f"*{ext}"))

                gallery['players'][game_dir.name] = [
                    {
                        "url": f"/static/images/{f.relative_to(STATIC_DIR)}",
                        "filename": f.name,
                        "size": f.stat().st_size
                    }
                    for f in files
                ]

    # Banners
    banner_dir = STATIC_DIR / "banners"
    if banner_dir.exists():
        for cat_dir in banner_dir.iterdir():
            if cat_dir.is_dir():
                files = []
                for ext in ['.png', '.webp', '.jpg']:
                    files.extend(cat_dir.glob(f"*{ext}"))

                gallery['banners'][cat_dir.name] = [
                    {
                        "url": f"/static/images/{f.relative_to(STATIC_DIR)}",
                        "filename": f.name,
                        "size": f.stat().st_size
                    }
                    for f in files
                ]

    # Forum icons
    forum_dir = STATIC_DIR / "forum"
    if forum_dir.exists():
        files = []
        for ext in ['.png', '.webp', '.svg', '.jpg']:
            files.extend(forum_dir.glob(f"*{ext}"))
        gallery['forum'] = [
            {
                "url": f"/static/images/{f.relative_to(STATIC_DIR)}",
                "filename": f.name,
                "size": f.stat().st_size
            }
            for f in files
        ]

    # Package icons
    package_dir = STATIC_DIR / "package_icons"
    if package_dir.exists():
        files = []
        for ext in ['.png', '.webp', '.svg']:
            files.extend(package_dir.glob(f"*{ext}"))
        gallery['packages'] = [
            {
                "url": f"/static/images/{f.relative_to(STATIC_DIR)}",
                "filename": f.name,
                "size": f.stat().st_size
            }
            for f in files
        ]

    # Site logos/favicons
    site_dir = STATIC_DIR / "site"
    if site_dir.exists():
        files = []
        for ext in ['.png', '.webp', '.svg', '.ico']:
            files.extend(site_dir.rglob(f"*{ext}"))
        gallery['site'] = [
            {
                "url": f"/static/images/{f.relative_to(STATIC_DIR)}",
                "filename": f.name,
                "size": f.stat().st_size
            }
            for f in files
        ]

    # Avatars
    avatar_dir = STATIC_DIR / "avatars"
    if avatar_dir.exists():
        files = []
        for ext in ['.png', '.webp', '.jpg']:
            files.extend(avatar_dir.glob(f"*{ext}"))
        gallery['avatars'] = [
            {
                "url": f"/static/images/{f.relative_to(STATIC_DIR)}",
                "filename": f.name,
                "size": f.stat().st_size
            }
            for f in files
        ]

    return gallery


@router.delete("/delete")
async def delete_media(
    url: str,
    current_user: User = Depends(get_current_admin)
):
    """Görsel sil"""

    if not url.startswith("/static/"):
        raise HTTPException(status_code=400, detail="Geçersiz URL")

    file_path = (Path("/var/www/agtrmerkezi") / url.lstrip("/")).resolve()

    # Güvenlik kontrolü
    if not str(file_path).startswith(str(STATIC_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Bu dosya silinemez")

    if file_path.exists():
        file_path.unlink()

        # WebP/PNG eşini de sil
        if file_path.suffix == '.png':
            webp_path = file_path.with_suffix('.webp')
            if webp_path.exists():
                webp_path.unlink()
        elif file_path.suffix == '.webp':
            png_path = file_path.with_suffix('.png')
            if png_path.exists():
                png_path.unlink()

        return {"success": True, "message": "Dosya silindi"}
    else:
        raise HTTPException(status_code=404, detail="Dosya bulunamadı")
