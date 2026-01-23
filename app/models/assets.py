"""
AGTR Merkezi - Site Asset Modelleri
Logo, görsel, animasyon yönetimi
"""

import enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base


class AssetType(enum.Enum):
    LOGO = "logo"
    ICON = "icon"
    BANNER = "banner"
    MASCOT = "mascot"
    BACKGROUND = "background"
    ANIMATION = "animation"
    OTHER = "other"


class AssetStatus(enum.Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class SiteAsset(Base):
    """Site görselleri ve logoları"""
    __tablename__ = "site_assets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Dosya bilgileri
    original_filename = Column(String(255))
    original_path = Column(String(500))  # Orijinal yüklenen dosya
    processed_path = Column(String(500))  # Arka planı silinmiş PNG
    thumbnail_path = Column(String(500))  # Küçük önizleme
    
    # Metadata
    asset_type = Column(Enum(AssetType), default=AssetType.OTHER)
    status = Column(Enum(AssetStatus), default=AssetStatus.PROCESSING)
    mime_type = Column(String(50))
    file_size = Column(Integer)  # bytes
    width = Column(Integer)
    height = Column(Integer)
    
    # Arka plan silme
    bg_removed = Column(Boolean, default=False)
    bg_color = Column(String(20))  # Orijinal arka plan rengi (tespit edilirse)
    
    # Animasyon ayarları
    is_animated = Column(Boolean, default=False)
    animation_type = Column(String(50))  # bounce, pulse, rotate, float, glow
    animation_duration = Column(Float, default=2.0)  # saniye
    animation_css = Column(Text)  # Özel CSS animasyonu
    
    # Kullanım yerleri
    usage_locations = Column(JSON, default=list)  # ["header", "footer", "home_hero"]
    
    # Yönetim
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # İlişkiler
    uploader = relationship("User", backref="uploaded_assets")


class FAQItem(Base):
    """SSS (Sıkça Sorulan Sorular)"""
    __tablename__ = "faq_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String(500), nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), default="Genel")
    icon = Column(String(50))  # Emoji veya icon class
    
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class StaticPage(Base):
    """Statik sayfalar (TOS, Gizlilik, İletişim vs)"""
    __tablename__ = "static_pages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    meta_description = Column(String(300))
    
    is_active = Column(Boolean, default=True)
    show_in_footer = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))


class ContactMessage(Base):
    """İletişim formu mesajları"""
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)

    ip_address = Column(String(45))
    user_agent = Column(String(500))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    is_read = Column(Boolean, default=False)
    is_replied = Column(Boolean, default=False)
    replied_at = Column(DateTime)
    replied_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    reply_content = Column(Text)

    created_at = Column(DateTime, default=func.now())


# ============================================
# OYUN ASSET MODELLERI (Scraper Sistemi)
# ============================================

class GameAssetType(enum.Enum):
    """Oyun asset turleri"""
    BANNER = 'banner'
    HERO = 'hero'
    LOGO = 'logo'
    ICON = 'icon'
    GRID = 'grid'
    SCREENSHOT = 'screenshot'
    MAP = 'map'
    WEAPON = 'weapon'
    SKIN = 'skin'
    TEAM_LOGO = 'team_logo'


class AnimationCategory(enum.Enum):
    """Animasyon kategorileri"""
    LOADING = 'loading'
    SUCCESS = 'success'
    ERROR = 'error'
    GAME = 'game'
    UI = 'ui'
    CELEBRATION = 'celebration'


class AnimationFormat(enum.Enum):
    """Animasyon formatlari"""
    LOTTIE = 'lottie'
    GIF = 'gif'
    WEBP = 'webp'
    MP4 = 'mp4'


class GameAsset(Base):
    """
    Oyun Asset Modeli
    CS 1.6, Half-Life vb. oyunlara ait gorseller
    """
    __tablename__ = 'game_assets'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Oyun bilgisi
    game_slug = Column(String(50), nullable=False, index=True)  # cs16, halflife
    game_name = Column(String(100))

    # Asset bilgisi
    asset_type = Column(
        Enum(GameAssetType, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    description = Column(Text)

    # Dosya bilgisi
    file_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500))
    original_filename = Column(String(200))
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    mime_type = Column(String(50))

    # Kaynak bilgisi
    source = Column(String(50))  # steamgriddb, gamebanana, manual
    source_url = Column(String(500))
    source_id = Column(String(100))

    # Metadata
    tags = Column(JSON, default=list)
    is_animated = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Istatistikler
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        # Sistem yolunu URL'e cevir
        base_path = '/var/www/agtrmerkezi'
        file_url = self.file_path.replace(base_path, '') if self.file_path else None
        thumb_url = self.thumbnail_path.replace(base_path, '') if self.thumbnail_path else None

        return {
            'id': self.id,
            'game_slug': self.game_slug,
            'asset_type': self.asset_type.value if self.asset_type else None,
            'name': self.name,
            'file_path': file_url,
            'thumbnail_path': thumb_url,
            'width': self.width,
            'height': self.height,
            'is_featured': self.is_featured
        }


class AnimationAsset(Base):
    """
    Animasyon Asset Modeli
    Lottie, GIF vb. animasyonlar
    """
    __tablename__ = 'animation_assets'

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    category = Column(
        Enum(AnimationCategory, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    # Dosya bilgisi
    file_format = Column(
        Enum(AnimationFormat, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    file_path = Column(String(500), nullable=False)
    preview_path = Column(String(500))
    file_size = Column(Integer)

    # Animasyon ozellikleri
    duration_ms = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    loop = Column(Boolean, default=True)

    # Kaynak
    source = Column(String(50))
    source_url = Column(String(500))
    author = Column(String(100))
    license = Column(String(100))

    # Metadata
    tags = Column(JSON, default=list)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    use_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        base_path = '/var/www/agtrmerkezi'
        file_url = self.file_path.replace(base_path, '') if self.file_path else None
        preview_url = self.preview_path.replace(base_path, '') if self.preview_path else None

        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'category': self.category.value if self.category else None,
            'file_format': self.file_format.value if self.file_format else None,
            'file_path': file_url,
            'preview_path': preview_url,
            'duration_ms': self.duration_ms,
            'loop': self.loop
        }


class MapAsset(Base):
    """
    Harita Asset Modeli
    CS 1.6 ve HL haritalari
    """
    __tablename__ = 'map_assets'

    id = Column(Integer, primary_key=True, autoincrement=True)

    game_slug = Column(String(50), nullable=False, index=True)
    map_name = Column(String(100), nullable=False)  # de_dust2
    map_slug = Column(String(100), nullable=False)
    display_name = Column(String(200))  # Dust 2
    description = Column(Text)

    # Harita tipi
    map_type = Column(String(20))  # de_, cs_, fy_, aim_

    # Gorseller
    thumbnail_path = Column(String(500))
    overview_path = Column(String(500))  # Radar gorseli
    screenshots = Column(JSON, default=list)

    # Kaynak
    source = Column(String(50))
    source_url = Column(String(500))

    # Ozellikler
    popularity_score = Column(Integer, default=0)
    is_official = Column(Boolean, default=False)
    is_competitive = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        base_path = '/var/www/agtrmerkezi'
        thumb_url = self.thumbnail_path.replace(base_path, '') if self.thumbnail_path else None
        overview_url = self.overview_path.replace(base_path, '') if self.overview_path else None

        return {
            'id': self.id,
            'game_slug': self.game_slug,
            'map_name': self.map_name,
            'display_name': self.display_name or self.map_name,
            'map_type': self.map_type,
            'thumbnail_path': thumb_url,
            'overview_path': overview_url,
            'is_official': self.is_official,
            'is_competitive': self.is_competitive,
            'popularity_score': self.popularity_score
        }
