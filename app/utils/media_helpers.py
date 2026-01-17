# ============================================
# AGTR Merkezi - Media Helper Functions
# Dosya: app/utils/media_helpers.py
# ============================================

from pathlib import Path
from typing import Optional

STATIC_DIR = Path("/var/www/agtrmerkezi/static")
IMAGES_DIR = STATIC_DIR / "images"


def get_game_logo(game_type: str) -> str:
    """Oyun logosunu getir"""
    # Önce SVG logolarını dene (yeni profesyonel logolar)
    game_logos_svg = {
        "hldm": "/static/images/games/hldm/logo.svg",
        "ag": "/static/images/games/ag/logo.svg",
        "cs16": "/static/images/games/cs16/logo.svg"
    }

    # PNG fallback
    game_logos_png = {
        "hldm": "/static/images/games/hldm/logo.png",
        "ag": "/static/images/games/ag/logo.png",
        "cs16": "/static/images/games/cs16/logo.png"
    }

    game_key = game_type.lower()

    # Önce SVG kontrol et
    if game_key in game_logos_svg:
        svg_path = STATIC_DIR / game_logos_svg[game_key].lstrip("/static/")
        if svg_path.exists():
            return game_logos_svg[game_key]

    # Sonra PNG kontrol et
    if game_key in game_logos_png:
        png_path = STATIC_DIR / game_logos_png[game_key].lstrip("/static/")
        if png_path.exists():
            return game_logos_png[game_key]

    # Yoksa placeholder döndür (games klasöründen)
    return f"/static/images/games/placeholder-{game_type}.svg"


def get_forum_icon(category_slug: str, icon_class: Optional[str] = None) -> dict:
    """Forum kategori ikonunu getir"""
    # Özel görsel varsa
    custom_icon_path = IMAGES_DIR / "forum" / category_slug

    if custom_icon_path.exists():
        for ext in [".png", ".jpg", ".svg", ".webp"]:
            icon_file = list(custom_icon_path.glob(f"*{ext}"))
            if icon_file:
                relative_path = icon_file[0].relative_to(STATIC_DIR)
                return {
                    "type": "image",
                    "url": f"/static/{relative_path.as_posix()}"
                }

    # Font Awesome ikonu varsa
    if icon_class:
        return {
            "type": "icon",
            "class": icon_class
        }

    # Varsayılan ikon
    return {
        "type": "icon",
        "class": "fas fa-comments"
    }


def get_site_logo() -> str:
    """Site logosunu getir"""
    # Önce SiteSettings'den kontrol et
    try:
        from app.models.connection import get_session_local
        from app.models.database import SiteSettings

        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            settings = db.query(SiteSettings).first()
            if settings and settings.logo_url:
                return settings.logo_url
        finally:
            db.close()
    except Exception:
        pass

    # Yoksa dosya sisteminden kontrol et
    logo_dir = IMAGES_DIR / "site" / "logo"

    if logo_dir.exists():
        for ext in [".svg", ".png", ".jpg"]:
            logo_files = list(logo_dir.glob(f"*{ext}"))
            if logo_files:
                latest = max(logo_files, key=lambda f: f.stat().st_mtime)
                relative_path = latest.relative_to(STATIC_DIR)
                return f"/static/{relative_path.as_posix()}"

    # Varsayılan logo
    return "/static/images/logo.svg"


def get_site_favicon() -> str:
    """Site favicon'unu getir"""
    favicon_dir = IMAGES_DIR / "site" / "favicon"

    if favicon_dir.exists():
        for ext in [".png", ".ico", ".svg"]:
            favicon_files = list(favicon_dir.glob(f"*{ext}"))
            if favicon_files:
                latest = max(favicon_files, key=lambda f: f.stat().st_mtime)
                relative_path = latest.relative_to(STATIC_DIR)
                return f"/static/{relative_path.as_posix()}"

    return "/static/images/favicon.svg"


def get_game_display_name(game_type: str) -> str:
    """Oyun görünen adını getir"""
    names = {
        "hldm": "Half-Life",
        "ag": "Half-Life AG",
        "cs16": "Counter-Strike 1.6"
    }
    return names.get(game_type.lower(), game_type.upper())


def get_game_color(game_type: str) -> str:
    """Oyun teması rengini getir"""
    colors = {
        "hldm": "#ff6b35",  # Turuncu-kırmızı
        "ag": "#00d9ff",    # Mavi
        "cs16": "#ffa500"   # Sarı-turuncu
    }
    return colors.get(game_type.lower(), "#6c757d")


def get_vip_icon(tier: str = "vip") -> str:
    """VIP tier ikonu getir"""
    tier = tier.lower()
    icon_dir = IMAGES_DIR / "vip_icons" / tier

    if icon_dir.exists():
        for ext in [".svg", ".png", ".webp"]:
            icon_files = list(icon_dir.glob(f"*{ext}"))
            if icon_files:
                latest = max(icon_files, key=lambda f: f.stat().st_mtime)
                relative_path = latest.relative_to(STATIC_DIR)
                return f"/static/{relative_path.as_posix()}"

    # Varsayılan VIP ikonu
    return f"/static/images/vip-{tier}.svg"


def get_package_icon(package_slug: str) -> str:
    """Paket ikonu getir"""
    icon_dir = IMAGES_DIR / "package_icons"

    if icon_dir.exists():
        # Paket adıyla eşleşen dosyayı ara
        for ext in [".png", ".webp", ".svg"]:
            icon_files = list(icon_dir.glob(f"{package_slug}*{ext}"))
            if icon_files:
                relative_path = icon_files[0].relative_to(STATIC_DIR)
                return f"/static/{relative_path.as_posix()}"

    # Varsayılan paket ikonu
    return "/static/images/package-default.svg"


def get_banner(category: str = "general") -> str:
    """Banner görseli getir"""
    banner_dir = IMAGES_DIR / "banners" / category

    if banner_dir.exists():
        for ext in [".jpg", ".png", ".webp"]:
            banner_files = list(banner_dir.glob(f"*{ext}"))
            if banner_files:
                latest = max(banner_files, key=lambda f: f.stat().st_mtime)
                relative_path = latest.relative_to(STATIC_DIR)
                return f"/static/{relative_path.as_posix()}"

    # Varsayılan banner
    return "/static/images/banner-default.jpg"


def get_og_image() -> str:
    """OG/Social share görseli getir"""
    og_dir = IMAGES_DIR / "site" / "og"

    if og_dir.exists():
        for ext in [".jpg", ".png"]:
            og_files = list(og_dir.glob(f"*{ext}"))
            if og_files:
                latest = max(og_files, key=lambda f: f.stat().st_mtime)
                relative_path = latest.relative_to(STATIC_DIR)
                return f"/static/{relative_path.as_posix()}"

    # Varsayılan OG image
    return get_site_logo()


def get_user_avatar(user_id: int = None, username: str = None, avatar_path: str = None) -> str:
    """Kullanıcı avatar'ı getir

    Args:
        user_id: Kullanıcı ID'si
        username: Kullanıcı adı
        avatar_path: DB'den gelen avatar path (avatars/user_123_abc.png)

    Returns:
        Avatar URL'i
    """
    # Önce DB'den gelen path'i kontrol et
    if avatar_path:
        # Eğer path zaten /static ile başlıyorsa direkt döndür
        if avatar_path.startswith('/static/'):
            return avatar_path
        # Yoksa static/images/ ekle
        avatar_file = IMAGES_DIR / avatar_path
        if avatar_file.exists():
            return f"/static/images/{avatar_path}"
        # Dosya yoksa default döndür
        return "/static/images/default-avatar.svg"

    # User ID veya username ile ara
    if user_id or username:
        avatar_dir = IMAGES_DIR / "avatars"
        if avatar_dir.exists():
            # User ID ile eşleşen avatar ara (user_123_*.png)
            search_pattern = f"user_{user_id or username}*"
            for ext in [".png", ".webp", ".jpg"]:
                avatar_files = list(avatar_dir.glob(f"{search_pattern}{ext}"))
                if avatar_files:
                    # En yeni dosyayı al
                    latest = max(avatar_files, key=lambda f: f.stat().st_mtime)
                    relative_path = latest.relative_to(STATIC_DIR)
                    return f"/static/{relative_path.as_posix()}"

    # Varsayılan avatar
    return "/static/images/default-avatar.svg"
