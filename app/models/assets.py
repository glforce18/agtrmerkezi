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
