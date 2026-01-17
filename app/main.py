"""
AGTR Merkezi - Ana Uygulama
Half-Life & CS 1.6 Gaming Community Platform
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func

from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging

# Setup logging
setup_logging(
    json_format=not settings.DEBUG,
    log_level="DEBUG" if settings.DEBUG else "INFO"
)
logger = get_logger(__name__)
from app.api import (
    admin,
    analytics,
    assets,
    auth,
    banners,
    discord_bot,
    forum,
    media,
    notifications,
    payment_gateway,
    payments,
    plugin_market,
    security,
    server_management,
    servers,
    smart_media,
    social,
    system,
    tournament,
    user,
    websocket,
)
from app.routers import vue_app
from app.api.admin import forum_categories as admin_forum_categories
from app.api.admin import forum_topics as admin_forum_topics
from app.core.security import get_current_user, hash_password
from app.models.connection import get_db, init_db
from app.models.database import (
    Announcement,
    ForumCategory,
    ForumPost,
    ForumTopic,
    GameServer,
    GameType,
    ServerPackage,
    ServerStatus,
    SiteSettings,
    User,
    UserRole,
    UserStatus,
)

# Core Engine - Self Healing
try:
    from app.core.engine import run_startup_checks
    run_startup_checks()
except Exception as e:
    print(f"[UYARI] Core Engine: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yasam dongusu"""
    print("=" * 50)
    print("AGTR Merkezi v7.0 Real-time baslatiliyor...")
    print("=" * 50)

    init_db()
    print("[OK] Veritabani tablolari hazir")

    create_default_data()
    print("[OK] Varsayilan veriler yuklendi")

    # Redis baslat
    try:
        from app.core.redis_manager import redis_manager
        await redis_manager.connect()
        print("[OK] Redis baglantisi kuruldu")
    except Exception as e:
        print(f"[UYARI] Redis baglantisi kurulamadi: {e}")

    # Scheduler baslat
    try:
        from app.tasks.scheduler import task_scheduler
        task_scheduler.start()
        print("[OK] Scheduler baslatildi")
    except Exception as e:
        print(f"[UYARI] Scheduler baslatilamadi: {e}")

    # WebSocket heartbeat cleanup task
    try:
        from app.core.websocket_manager import heartbeat_cleanup_task
        import asyncio
        asyncio.create_task(heartbeat_cleanup_task())
        print("[OK] WebSocket heartbeat task baslatildi")
    except Exception as e:
        print(f"[UYARI] WebSocket task baslatilamadi: {e}")

    print("=" * 50)
    print(f"Site adresi: {settings.BASE_URL}")
    print("=" * 50)

    yield

    # Cleanup
    try:
        from app.core.redis_manager import redis_manager
        await redis_manager.disconnect()
        print("[OK] Redis baglantisi kapatildi")
    except Exception as e:
        print(f"[UYARI] Redis cleanup hatasi: {e}")
    
    # Scheduler durdur
    try:
        from app.tasks.scheduler import task_scheduler
        task_scheduler.stop()
        print("[OK] Scheduler durduruldu")
    except:
        pass
    
    print("AGTR Merkezi kapatiliyor...")


def create_default_data():
    """Varsayilan verileri olustur"""
    from app.models.connection import SessionLocal
    db = SessionLocal()
    
    try:
        # Superadmin kontrolu - yoksa olustur, varsa sifreyi guncelle
        admin_user = db.query(User).filter(User.role == UserRole.SUPERADMIN).first()
        if not admin_user:
            admin_user = User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                display_name="Admin",
                role=UserRole.SUPERADMIN
            )
            db.add(admin_user)
            db.flush()
            logger.info(f"Superadmin olusturuldu ({settings.DEFAULT_ADMIN_USERNAME})")
        else:
            # Mevcut admin'in sifresi ve kullanici adini guncelle
            admin_user.username = settings.DEFAULT_ADMIN_USERNAME
            admin_user.password_hash = hash_password(settings.DEFAULT_ADMIN_PASSWORD)
            logger.info(f"Superadmin guncellendi ({settings.DEFAULT_ADMIN_USERNAME})")
        
        # Forum kategorileri
        if db.query(ForumCategory).count() == 0:
            categories = [
                ForumCategory(
                    name="Duyurular",
                    slug="duyurular",
                    description="Site duyurulari",
                    icon="📢",
                    display_order=1
                ),
                ForumCategory(
                    name="Half-Life / AG",
                    slug="half-life-ag",
                    description="Adrenaline Gamer tartismalari",
                    icon="🎮",
                    display_order=2
                ),
                ForumCategory(
                    name="Counter-Strike 1.6",
                    slug="cs16",
                    description="CS 1.6 tartismalari",
                    icon="🔫",
                    display_order=3
                ),
                ForumCategory(
                    name="Sunucu Destek",
                    slug="sunucu-destek",
                    description="Sunucu kurulum ve sorunlar",
                    icon="🖥️",
                    display_order=4
                ),
                ForumCategory(
                    name="Genel Sohbet",
                    slug="genel-sohbet",
                    description="Her sey hakkinda",
                    icon="💬",
                    display_order=5
                ),
            ]
            db.add_all(categories)
            print("  -> Forum kategorileri olusturuldu")
        
        # Sunucu paketleri
        if db.query(ServerPackage).count() == 0:
            packages = [
                ServerPackage(
                    slug="ag_starter",
                    name="AG Starter",
                    game_type=GameType.AG,
                    slots=12,
                    features=["basic_plugins", "rcon_access"],
                    price_monthly=50.0,
                    description="Yeni baslayanlar icin ideal",
                    display_order=1
                ),
                ServerPackage(
                    slug="ag_pro",
                    name="AG Pro",
                    game_type=GameType.AG,
                    slots=20,
                    features=["basic_plugins", "rcon_access", "anticheat", "amvp"],
                    price_monthly=100.0,
                    description="Rekabetci oyuncular icin",
                    is_popular=True,
                    display_order=2
                ),
                ServerPackage(
                    slug="ag_ultimate",
                    name="AG Ultimate",
                    game_type=GameType.AG,
                    slots=32,
                    features=["basic_plugins", "rcon_access", "anticheat", "amvp", "custom_domain", "priority_support", "auto_backup"],
                    price_monthly=150.0,
                    description="Profesyonel takimlar icin",
                    display_order=3
                ),
                ServerPackage(
                    slug="cs16_starter",
                    name="CS 1.6 Starter",
                    game_type=GameType.CS16,
                    slots=16,
                    features=["basic_plugins", "rcon_access"],
                    price_monthly=45.0,
                    description="Klasik CS deneyimi",
                    display_order=4
                ),
                ServerPackage(
                    slug="cs16_pro",
                    name="CS 1.6 Pro",
                    game_type=GameType.CS16,
                    slots=24,
                    features=["basic_plugins", "rcon_access", "anticheat", "statsme"],
                    price_monthly=90.0,
                    description="Public sunucular icin",
                    display_order=5
                ),
                ServerPackage(
                    slug="cs16_ultimate",
                    name="CS 1.6 Ultimate",
                    game_type=GameType.CS16,
                    slots=32,
                    features=["basic_plugins", "rcon_access", "anticheat", "statsme", "custom_domain", "priority_support", "auto_backup"],
                    price_monthly=140.0,
                    description="Buyuk topluluklar icin",
                    display_order=6
                ),
                # HLDM Paketleri
                ServerPackage(
                    slug="hldm_starter",
                    name="HLDM Starter",
                    game_type=GameType.HLDM,
                    slots=12,
                    features=["basic_plugins", "rcon_access"],
                    price_monthly=40.0,
                    description="Half-Life Deathmatch baslangic",
                    display_order=7
                ),
                ServerPackage(
                    slug="hldm_pro",
                    name="HLDM Pro",
                    game_type=GameType.HLDM,
                    slots=20,
                    features=["basic_plugins", "rcon_access", "anticheat"],
                    price_monthly=80.0,
                    description="Rekabetci HLDM",
                    display_order=8
                ),
                ServerPackage(
                    slug="hldm_ultimate",
                    name="HLDM Ultimate",
                    game_type=GameType.HLDM,
                    slots=32,
                    features=["basic_plugins", "rcon_access", "anticheat", "custom_domain", "priority_support"],
                    price_monthly=120.0,
                    description="Profesyonel HLDM",
                    display_order=9
                ),
            ]
            db.add_all(packages)
            print("  -> Sunucu paketleri olusturuldu")
        
        # Site ayarlari
        if db.query(SiteSettings).count() == 0:
            site_settings = SiteSettings(
                site_name="AGTR Merkezi",
                site_description="Turkiye'nin en iyi Half-Life ve CS 1.6 platformu"
            )
            db.add(site_settings)
            print("  -> Site ayarlari olusturuldu")
        
        db.commit()
        
    except Exception as e:
        print(f"  [HATA] Varsayilan veri olusturma hatasi: {e}")
        db.rollback()
    finally:
        db.close()


# FastAPI uygulamasi
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None
)

# CORS middleware - Production'da spesifik originler
cors_origins = ["*"] if settings.DEBUG else [
    "https://agtrmerkezi.com",
    "https://www.agtrmerkezi.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# GZip Compression - Response sıkıştırma (500 byte üzeri)
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=6)

# Security Headers - Modern güvenlik başlıkları
from app.middleware.security_headers import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)

# Cache Control - Static dosyalar için cache headers
from app.middleware.cache_control import CacheControlMiddleware

app.add_middleware(CacheControlMiddleware)

# Rate Limit middleware (DDoS korumasi)
from app.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware)

# CSRF Protection middleware
from app.middleware.csrf import CSRFMiddleware

app.add_middleware(CSRFMiddleware)

# Admin Access Control middleware
from app.middleware.admin_access import AdminAccessMiddleware

app.add_middleware(AdminAccessMiddleware)

# Static dosyalar
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Media helpers import
try:
    from app.utils.media_helpers import (
        get_banner,
        get_forum_icon,
        get_game_color,
        get_game_display_name,
        get_game_logo,
        get_og_image,
        get_package_icon,
        get_site_favicon,
        get_site_logo,
        get_user_avatar,
        get_vip_icon,
    )
except ImportError:
    # Fallback if helpers not available
    def get_game_logo(game_type): return f"/static/images/games/{game_type}/logo.svg"
    def get_forum_icon(slug, icon=None): return {"type": "icon", "class": icon or "fas fa-comments"}
    def get_site_logo(): return "/static/images/logo.svg"
    def get_site_favicon(): return "/static/images/favicon.svg"
    def get_game_display_name(game_type): return game_type.upper()
    def get_game_color(game_type): return "#6c757d"
    def get_vip_icon(tier="vip"): return "/static/images/vip.svg"
    def get_package_icon(package_slug): return "/static/images/package.svg"
    def get_banner(category="general"): return "/static/images/banner.jpg"
    def get_og_image(): return "/static/images/logo.svg"
    def get_user_avatar(user_id=None, username=None): return "/static/images/avatar.svg"
    def get_game_color(game_type): return "#6c757d"

# Add media helpers to Jinja2 globals
templates.env.globals['get_game_logo'] = get_game_logo
templates.env.globals['get_forum_icon'] = get_forum_icon
templates.env.globals['get_site_logo'] = get_site_logo
templates.env.globals['get_site_favicon'] = get_site_favicon
templates.env.globals['get_game_display_name'] = get_game_display_name
templates.env.globals['get_game_color'] = get_game_color
templates.env.globals['get_vip_icon'] = get_vip_icon
templates.env.globals['get_package_icon'] = get_package_icon
templates.env.globals['get_banner'] = get_banner
templates.env.globals['get_og_image'] = get_og_image
templates.env.globals['get_user_avatar'] = get_user_avatar

# Jinja2 custom filters
def timeago_filter(dt):
    """Zaman farkini insan okunabilir formata cevirir"""
    if not dt:
        return "Bilinmiyor"
    from datetime import datetime
    now = datetime.utcnow()
    diff = now - dt
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Az önce"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} dakika önce"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} saat önce"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} gün önce"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} hafta önce"
    else:
        return dt.strftime("%d.%m.%Y")

templates.env.filters["timeago"] = timeago_filter

# API router'lari
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(forum.router, prefix="/api/forum", tags=["Forum"])
app.include_router(servers.router, prefix="/api/servers", tags=["Game Servers"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(system.router, prefix="/api", tags=["System"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])

# v5.5 Pro - Yeni API'ler
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(payment_gateway.router, prefix="/api/payment", tags=["Payment Gateway"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(server_management.router, prefix="/api/management", tags=["Server Management"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(discord_bot.router, prefix="/api/discord", tags=["Discord Bot"])
app.include_router(tournament.router, prefix="/api/tournament", tags=["Tournament"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(plugin_market.router, prefix="/api/plugins", tags=["Plugin Market"])
app.include_router(media.router, tags=["Media Management"])
app.include_router(smart_media.router, tags=["Smart Media"])

# Vue.js 3 SPA
app.include_router(vue_app.router, tags=["Vue App"])
app.include_router(banners.router, tags=["Banners & Advertisements"])

# Admin Forum Submodules
app.include_router(admin_forum_categories.router, tags=["Admin Forum"])
app.include_router(admin_forum_topics.router, tags=["Admin Forum"])


# ==================== PUBLIC PAGES ====================

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Ana sayfa - Vue.js SPA"""
    import os
    index_path = "/var/www/agtrmerkezi/static/dist/index.html"

    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)

    return HTMLResponse(content="<h1>Vue app not built</h1><p>Run: cd frontend && npm run build</p>", status_code=500)


@app.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Giris sayfasi"""
    if current_user:
        return RedirectResponse(url="/panel", status_code=302)
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "current_user": None,
        "settings": settings
    })


@app.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Kayit sayfasi"""
    if current_user:
        return RedirectResponse(url="/panel", status_code=302)
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "current_user": None,
        "settings": settings
    })


@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Sifremi unuttum sayfasi"""
    if current_user:
        return RedirectResponse(url="/panel", status_code=302)
    return templates.TemplateResponse("auth/forgot-password.html", {
        "request": request,
        "current_user": None,
        "settings": settings
    })


@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(
    request: Request,
    token: str = "",
    current_user: User = Depends(get_current_user)
):
    """Sifre sifirlama sayfasi"""
    if current_user:
        return RedirectResponse(url="/panel", status_code=302)
    return templates.TemplateResponse("auth/reset-password.html", {
        "request": request,
        "current_user": None,
        "token": token,
        "settings": settings
    })


@app.get("/panel", response_class=HTMLResponse)
async def user_panel(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanici paneli"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    user_servers = db.query(GameServer).filter(
        GameServer.owner_id == current_user.id,
        GameServer.status != ServerStatus.DELETED
    ).all()
    
    return templates.TemplateResponse("user/panel.html", {
        "request": request,
        "current_user": current_user,
        "servers": user_servers,
        "settings": settings
    })


@app.get("/panel/servers", response_class=HTMLResponse)
async def user_servers_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanici sunuculari sayfasi"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    user_servers = db.query(GameServer).filter(
        GameServer.owner_id == current_user.id,
        GameServer.status != ServerStatus.DELETED
    ).all()
    
    return templates.TemplateResponse("user/servers.html", {
        "request": request,
        "current_user": current_user,
        "servers": user_servers,
        "settings": settings
    })


@app.get("/panel/settings", response_class=HTMLResponse)
async def user_settings_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanici ayarlari sayfasi"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("user/settings.html", {
        "request": request,
        "current_user": current_user,
        "settings": settings
    })


@app.get("/panel/server/{server_id}", response_class=HTMLResponse)
async def user_server_detail(
    request: Request,
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tekil sunucu detay sayfasi"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.owner_id == current_user.id
    ).first()
    
    if not server:
        return templates.TemplateResponse("errors/404.html", {
            "request": request,
            "current_user": current_user,
            "settings": settings
        }, status_code=404)
    
    return templates.TemplateResponse("user/server.html", {
        "request": request,
        "current_user": current_user,
        "server": server,
        "settings": settings
    })


@app.get("/panel/balance", response_class=HTMLResponse)
async def user_balance_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bakiye sayfasi"""
    from app.models.database import Payment, PaymentStatus, Transaction
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Son islemler
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).limit(20).all()
    
    # Bekleyen ödemeler
    pending_payments = db.query(Payment).filter(
        Payment.user_id == current_user.id,
        Payment.status == PaymentStatus.PENDING
    ).all()
    
    return templates.TemplateResponse("user/balance.html", {
        "request": request,
        "current_user": current_user,
        "transactions": transactions,
        "pending_payments": pending_payments,
        "settings": settings
    })


@app.get("/panel/invoices", response_class=HTMLResponse)
async def user_invoices_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Faturalar sayfasi"""
    from app.models.database import Invoice
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id
    ).order_by(Invoice.created_at.desc()).all()
    
    return templates.TemplateResponse("user/invoices.html", {
        "request": request,
        "current_user": current_user,
        "invoices": invoices,
        "settings": settings
    })


@app.get("/forum", response_class=HTMLResponse)
async def forum_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Forum ana sayfasi"""
    from datetime import datetime, timedelta
    
    categories = db.query(ForumCategory).filter(
        ForumCategory.is_visible == True,
        ForumCategory.parent_id == None
    ).order_by(ForumCategory.display_order).all()
    
    # Sabitlenmis konular (author ile birlikte)
    pinned_topics = db.query(ForumTopic).options(
        joinedload(ForumTopic.author),
        joinedload(ForumTopic.category)
    ).filter(
        ForumTopic.is_pinned == True
    ).order_by(ForumTopic.created_at.desc()).limit(5).all()
    
    # Son konular (author ile birlikte)
    recent_topics = db.query(ForumTopic).options(
        joinedload(ForumTopic.author),
        joinedload(ForumTopic.category)
    ).order_by(
        ForumTopic.last_post_at.desc()
    ).limit(10).all()
    
    # İstatistikler
    total_topics = db.query(ForumTopic).count()
    total_posts = db.query(ForumPost).count()
    total_members = db.query(User).count()
    
    # Online kullanıcılar (son 5 dk)
    five_min_ago = datetime.now() - timedelta(minutes=5)
    online_users = db.query(User).filter(User.last_login >= five_min_ago).limit(20).all()
    online_count = len(online_users)
    
    # Top contributors
    top_contributors = db.query(User).order_by(User.post_count.desc()).limit(5).all()
    
    return templates.TemplateResponse("forum/index.html", {
        "request": request,
        "current_user": current_user,
        "categories": categories,
        "pinned_topics": pinned_topics,
        "recent_topics": recent_topics,
        "total_topics": total_topics,
        "total_posts": total_posts,
        "total_members": total_members,
        "online_count": online_count,
        "online_users": online_users,
        "top_contributors": top_contributors,
        "settings": settings
    })


@app.get("/forum/category/{slug}", response_class=HTMLResponse)
async def forum_category_page(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Forum kategori sayfasi"""
    category = db.query(ForumCategory).filter(ForumCategory.slug == slug).first()
    if not category:
        return RedirectResponse(url="/forum", status_code=302)
    
    topics = db.query(ForumTopic).filter(
        ForumTopic.category_id == category.id
    ).order_by(ForumTopic.is_pinned.desc(), ForumTopic.created_at.desc()).all()
    
    return templates.TemplateResponse("forum/category.html", {
        "request": request,
        "current_user": current_user,
        "category": category,
        "topics": topics,
        "settings": settings
    })


@app.get("/forum/topic/{slug}", response_class=HTMLResponse)
async def forum_topic_page(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Forum konu sayfasi"""
    topic = db.query(ForumTopic).options(
        joinedload(ForumTopic.author),
        joinedload(ForumTopic.category)
    ).filter(ForumTopic.slug == slug).first()
    if not topic:
        return RedirectResponse(url="/forum", status_code=302)
    
    # Goruntulenme sayisini artir
    topic.view_count = (topic.view_count or 0) + 1
    db.commit()
    
    posts = db.query(ForumPost).options(
        joinedload(ForumPost.author)
    ).filter(
        ForumPost.topic_id == topic.id
    ).order_by(ForumPost.created_at).all()
    
    return templates.TemplateResponse("forum/topic.html", {
        "request": request,
        "current_user": current_user,
        "topic": topic,
        "posts": posts,
        "settings": settings
    })


@app.get("/forum/new", response_class=HTMLResponse)
async def forum_new_topic_page(
    request: Request,
    category: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Yeni konu olusturma sayfasi"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    categories = db.query(ForumCategory).filter(ForumCategory.is_visible == True).all()
    
    return templates.TemplateResponse("forum/new.html", {
        "request": request,
        "current_user": current_user,
        "categories": categories,
        "selected_category": category,
        "settings": settings
    })


@app.get("/servers", response_class=HTMLResponse)
async def servers_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sunucu paketleri sayfasi"""
    packages = db.query(ServerPackage).filter(
        ServerPackage.is_active == True
    ).order_by(ServerPackage.display_order).all()
    
    return templates.TemplateResponse("shop/servers.html", {
        "request": request,
        "current_user": current_user,
        "packages": packages,
        "settings": settings
    })


@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(
    request: Request,
    game: str = "ag",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Oyuncu siralama sayfasi"""
    # Simdilik User tablosundan, gercek implementasyonda ag_players tablosundan cekilecek
    players = db.query(User).filter(User.post_count > 0).order_by(User.reputation.desc()).limit(50).all()
    
    # Oyun bazli oyuncu sayilari (simdilik statik, gercek database entegrasyonu lazim)
    ag_players = db.query(User).count()  # TODO: ag_players tablosundan
    cs_players = 0  # TODO: cs_players tablosundan
    hldm_players = 0  # TODO: hldm_players tablosundan
    
    return templates.TemplateResponse("leaderboard.html", {
        "request": request,
        "current_user": current_user,
        "players": players,
        "game": game,
        "ag_players": ag_players,
        "cs_players": cs_players,
        "hldm_players": hldm_players,
        "settings": settings
    })


@app.get("/members", response_class=HTMLResponse)
async def members_page(
    request: Request,
    q: str = None,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Uye listesi sayfasi"""
    from datetime import datetime, timedelta
    
    query = db.query(User)
    if q:
        query = query.filter(User.username.ilike(f"%{q}%"))
    
    total = query.count()
    per_page = 24
    total_pages = (total + per_page - 1) // per_page
    
    members = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    # Bu ay katılanlar
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = db.query(User).filter(User.created_at >= month_start).count()
    
    # Çevrimiçi (son 5 dakikada aktif)
    five_min_ago = datetime.now() - timedelta(minutes=5)
    online_count = db.query(User).filter(User.last_login >= five_min_ago).count()
    
    return templates.TemplateResponse("members.html", {
        "request": request,
        "current_user": current_user,
        "members": members,
        "query": q,
        "page": page,
        "total_pages": total_pages,
        "new_this_month": new_this_month,
        "online_count": online_count,
        "settings": settings
    })


@app.get("/profile/{username}", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanici profil sayfasi"""
    profile_user = db.query(User).filter(User.username == username).first()
    if not profile_user:
        return templates.TemplateResponse("errors/404.html", {
            "request": request,
            "current_user": current_user,
            "settings": settings
        }, status_code=404)
    
    # Kullanici forum istatistikleri
    from app.models.database import ForumPost, ForumTopic
    topic_count = db.query(ForumTopic).filter(ForumTopic.author_id == profile_user.id).count()
    post_count = db.query(ForumPost).filter(ForumPost.author_id == profile_user.id).count()
    
    # Kullanici sunuculari
    user_servers = db.query(GameServer).filter(
        GameServer.owner_id == profile_user.id,
        GameServer.status == ServerStatus.RUNNING
    ).limit(5).all()
    server_count = db.query(GameServer).filter(
        GameServer.owner_id == profile_user.id,
        GameServer.status != ServerStatus.DELETED
    ).count()
    
    # Son aktiviteler
    recent_topics = db.query(ForumTopic).filter(
        ForumTopic.author_id == profile_user.id
    ).order_by(ForumTopic.created_at.desc()).limit(5).all()
    
    recent_posts = db.query(ForumPost).filter(
        ForumPost.author_id == profile_user.id,
        ForumPost.is_first_post == False
    ).order_by(ForumPost.created_at.desc()).limit(5).all()
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "current_user": current_user,
        "profile_user": profile_user,
        "topic_count": topic_count,
        "post_count": post_count,
        "server_count": server_count,
        "user_servers": user_servers,
        "recent_topics": recent_topics,
        "recent_posts": recent_posts,
        "is_online": profile_user.is_online,
        "activities": recent_topics[:3] + recent_posts[:2],  # Son aktiviteler
        "achievements": [],  # TODO: Implement achievements system
        "settings": settings
    })


# ==================== ADMIN PAGES ====================

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin paneli ana sayfa"""
    from datetime import datetime

    from app.models.database import Payment, PaymentStatus
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/panel", status_code=302)
    
    # Bu ay başlangıcı
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # İstatistikler
    stats = {
        "total_users": db.query(User).count(),
        "total_servers": db.query(GameServer).count(),
        "active_servers": db.query(GameServer).filter(GameServer.status == ServerStatus.RUNNING).count(),
        "total_revenue": db.query(func.sum(Payment.amount)).filter(Payment.status == PaymentStatus.COMPLETED).scalar() or 0,
        "monthly_revenue": db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.created_at >= month_start
        ).scalar() or 0,
        "pending_payments": db.query(Payment).filter(Payment.status == PaymentStatus.PENDING).count()
    }
    
    return templates.TemplateResponse("admin/index.html", {
        "request": request,
        "current_user": current_user,
        "stats": stats,
        "settings": settings
    })


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Kullanici yonetimi"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/panel", status_code=302)
    
    users = db.query(User).order_by(User.id.desc()).all()
    
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "current_user": current_user,
        "users": users,
        "settings": settings
    })


@app.get("/admin/servers", response_class=HTMLResponse)
async def admin_servers_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Sunucu yonetimi"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/panel", status_code=302)
    
    servers = db.query(GameServer).order_by(GameServer.id.desc()).all()
    
    return templates.TemplateResponse("admin/servers.html", {
        "request": request,
        "current_user": current_user,
        "servers": servers,
        "settings": settings
    })


@app.get("/admin/payments", response_class=HTMLResponse)
async def admin_payments_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Odeme yonetimi"""
    from datetime import datetime

    from app.models.database import Payment, PaymentStatus
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/panel", status_code=302)
    
    payments = db.query(Payment).order_by(Payment.id.desc()).all()
    
    # Stats hesapla
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    # Bu ay
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.COMPLETED,
        Payment.created_at >= month_start
    ).scalar() or 0
    
    pending_count = db.query(Payment).filter(
        Payment.status == PaymentStatus.PENDING
    ).count()
    
    stats = {
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "pending_count": pending_count
    }
    
    return templates.TemplateResponse("admin/payments.html", {
        "request": request,
        "current_user": current_user,
        "payments": payments,
        "stats": stats,
        "settings": settings
    })


@app.get("/admin/packages", response_class=HTMLResponse)
async def admin_packages_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Paket yonetimi"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/panel", status_code=302)
    
    packages = db.query(ServerPackage).order_by(ServerPackage.display_order).all()
    
    return templates.TemplateResponse("admin/packages.html", {
        "request": request,
        "current_user": current_user,
        "packages": packages,
        "settings": settings
    })


@app.get("/admin/announcements", response_class=HTMLResponse)
async def admin_announcements_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Duyuru yonetimi"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/panel", status_code=302)
    
    announcements = db.query(Announcement).order_by(Announcement.id.desc()).all()
    
    return templates.TemplateResponse("admin/announcements.html", {
        "request": request,
        "current_user": current_user,
        "announcements": announcements,
        "settings": settings
    })


@app.get("/test-logos", response_class=HTMLResponse)
async def test_logos_page(request: Request):
    """Test - Logo galerisi ve kullanım örnekleri"""
    return templates.TemplateResponse("test-logos.html", {
        "request": request,
        "page_title": "Logo Galerisi"
    })


@app.get("/media-guide", response_class=HTMLResponse)
async def media_usage_guide(request: Request):
    """Akilli medya kullanim kilavuzu"""
    return templates.TemplateResponse("media-usage-examples.html", {
        "request": request,
        "page_title": "Medya Kullanım Kılavuzu"
    })


@app.get("/admin/logo", response_class=HTMLResponse)
async def admin_logo_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Logo ayarlari (Redirect to Smart Media)"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/admin", status_code=302)

    # Yeni akıllı medya sistemine yönlendir
    return RedirectResponse(url="/admin/smart-media", status_code=302)


@app.post("/api/admin/settings/logo")
async def save_logo_url(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Logo URL'sini kaydet"""
    logger.info(f"💾 Logo URL kaydetme isteği - User: {current_user.username if current_user else 'None'}")

    if not current_user or current_user.role.value not in ["admin", "superadmin"]:
        logger.error(f"❌ Yetki hatası - User: {current_user.username if current_user else 'None'}, Role: {current_user.role.value if current_user else 'None'}")
        raise HTTPException(status_code=403, detail="Yetkiniz yok")

    data = await request.json()
    logo_url = data.get("logo_url")
    logger.info(f"📝 Kaydedilecek logo URL: {logo_url}")

    if not logo_url:
        logger.error("❌ Logo URL eksik")
        raise HTTPException(status_code=400, detail="Logo URL gerekli")

    # Settings kaydını güncelle
    settings = db.query(SiteSettings).first()
    if not settings:
        logger.info("⚠️ SiteSettings kaydı yok, oluşturuluyor...")
        settings = SiteSettings()
        db.add(settings)

    settings.logo_url = logo_url
    db.commit()
    logger.info(f"✅ Logo URL kaydedildi: {logo_url}")

    return {"success": True, "logo_url": logo_url}


@app.get("/admin/media", response_class=HTMLResponse)
async def admin_media_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Gorsel yonetimi (Redirect to Smart Media)"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/admin", status_code=302)

    # Yeni akıllı medya sistemine yönlendir
    return RedirectResponse(url="/admin/smart-media", status_code=302)


@app.get("/admin/smart-media", response_class=HTMLResponse)
async def admin_smart_media_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Akilli medya yonetimi (ultra-comfortable upload)"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/admin", status_code=302)

    return templates.TemplateResponse("admin/smart-media.html", {
        "request": request,
        "current_user": current_user,
        "page_title": "Akıllı Medya Yönetimi"
    })


@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Site ayarlari"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value != "superadmin":
        return RedirectResponse(url="/admin", status_code=302)
    
    site_settings = db.query(SiteSettings).first()
    
    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "current_user": current_user,
        "site_settings": site_settings,
        "settings": settings
    })


@app.get("/admin/theme", response_class=HTMLResponse)
async def admin_theme_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Tema ayarlari"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value != "superadmin":
        return RedirectResponse(url="/admin", status_code=302)
    
    return templates.TemplateResponse("admin/theme.html", {
        "request": request,
        "current_user": current_user,
        "settings": settings
    })


@app.get("/admin/content", response_class=HTMLResponse)
async def admin_content_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Icerik yonetimi"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/panel", status_code=302)
    
    return templates.TemplateResponse("admin/content.html", {
        "request": request,
        "current_user": current_user,
        "settings": settings
    })


@app.get("/admin/coupons", response_class=HTMLResponse)
async def admin_coupons_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Kupon yonetimi"""
    from app.models.database import Coupon
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/panel", status_code=302)
    
    coupons = db.query(Coupon).order_by(Coupon.id.desc()).all()
    
    return templates.TemplateResponse("admin/coupons.html", {
        "request": request,
        "current_user": current_user,
        "coupons": coupons,
        "settings": settings
    })


@app.get("/admin/forum", response_class=HTMLResponse)
async def admin_forum_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Forum yonetimi"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/panel", status_code=302)
    
    categories = db.query(ForumCategory).order_by(ForumCategory.display_order).all()
    
    return templates.TemplateResponse("admin/forum.html", {
        "request": request,
        "current_user": current_user,
        "categories": categories,
        "settings": settings
    })


@app.get("/admin/reports", response_class=HTMLResponse)
async def admin_reports_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Raporlar"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin"]:
        return RedirectResponse(url="/panel", status_code=302)
    
    return templates.TemplateResponse("admin/reports.html", {
        "request": request,
        "current_user": current_user,
        "stats": {},
        "settings": settings
    })


@app.get("/admin/security", response_class=HTMLResponse)
async def admin_security_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Guvenlik"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value != "superadmin":
        return RedirectResponse(url="/admin", status_code=302)
    
    return templates.TemplateResponse("admin/security.html", {
        "request": request,
        "current_user": current_user,
        "banned_ips": [],
        "settings": settings
    })


@app.get("/admin/tickets", response_class=HTMLResponse)
async def admin_tickets_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin - Destek Talepleri"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if current_user.role.value not in ["admin", "superadmin", "moderator"]:
        return RedirectResponse(url="/", status_code=302)
    
    from app.models.database import SupportTicket
    
    tickets = db.query(SupportTicket).order_by(SupportTicket.updated_at.desc()).limit(100).all()
    
    # Stats
    stats = {
        "total": db.query(SupportTicket).count(),
        "open": db.query(SupportTicket).filter(SupportTicket.status == "open").count(),
        "pending": db.query(SupportTicket).filter(SupportTicket.status == "pending").count(),
        "resolved": db.query(SupportTicket).filter(SupportTicket.status == "resolved").count()
    }
    
    return templates.TemplateResponse("admin/tickets.html", {
        "request": request,
        "current_user": current_user,
        "tickets": tickets,
        "stats": stats
    })


# ==================== SEARCH API ====================

@app.get("/api/search")
async def search_api(
    q: str,
    db: Session = Depends(get_db)
):
    """Global arama API"""
    from app.services.search import SearchService
    search = SearchService(db)
    return search.search_all(q)


# ==================== NOTIFICATION API ====================

@app.get("/api/notifications/count")
async def notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Okunmamis bildirim sayisi"""
    if not current_user:
        return {"count": 0}
    
    from app.models.database import Notification
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"count": count}


@app.get("/api/notifications")
async def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanici bildirimleri"""
    if not current_user:
        return {"notifications": [], "unread_count": 0}
    
    from app.models.database import Notification
    notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(20).all()
    
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {
        "notifications": [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "url": n.link,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in notifs
        ],
        "unread_count": unread_count
    }


@app.post("/api/notifications/read-all")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tum bildirimleri okundu isaretle"""
    if not current_user:
        return {"success": False}
    
    from app.models.database import Notification
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    return {"success": True}


@app.post("/api/notifications/{notif_id}/read")
async def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tek bildirimi okundu isaretle"""
    if not current_user:
        return {"success": False}
    
    from app.models.database import Notification
    notif = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.user_id == current_user.id
    ).first()
    
    if notif:
        notif.is_read = True
        db.commit()
    
    return {"success": True}


# ==================== PUBLIC DETAIL PAGES ====================

@app.get("/announcements/{announcement_id}", response_class=HTMLResponse)
async def announcement_detail_page(
    request: Request,
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Duyuru detay sayfasi"""
    announcement = db.query(Announcement).filter(
        Announcement.id == announcement_id,
        Announcement.is_active == True
    ).first()
    
    if not announcement:
        return templates.TemplateResponse("errors/404.html", {
            "request": request,
            "current_user": current_user,
            "settings": settings
        }, status_code=404)
    
    # Diger duyurular (sidebar icin)
    other_announcements = db.query(Announcement).filter(
        Announcement.is_active == True,
        Announcement.id != announcement_id
    ).order_by(Announcement.created_at.desc()).limit(5).all()
    
    return templates.TemplateResponse("announcements/detail.html", {
        "request": request,
        "current_user": current_user,
        "announcement": announcement,
        "other_announcements": other_announcements,
        "settings": settings
    })


@app.get("/server/{server_id}", response_class=HTMLResponse)
async def public_server_detail_page(
    request: Request,
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Public sunucu detay sayfasi"""
    server = db.query(GameServer).filter(
        GameServer.id == server_id,
        GameServer.status == ServerStatus.RUNNING
    ).first()
    
    if not server:
        return templates.TemplateResponse("errors/404.html", {
            "request": request,
            "current_user": current_user,
            "settings": settings
        }, status_code=404)
    
    # Sunucu sahibi bilgisi
    owner = db.query(User).filter(User.id == server.owner_id).first()
    
    return templates.TemplateResponse("servers/detail.html", {
        "request": request,
        "current_user": current_user,
        "server": server,
        "owner": owner,
        "settings": settings
    })


# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 sayfasi"""
    return templates.TemplateResponse("errors/404.html", {
        "request": request,
        "current_user": None,
        "settings": settings
    }, status_code=404)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """500 sayfasi"""
    return templates.TemplateResponse("errors/500.html", {
        "request": request,
        "current_user": None,
        "settings": settings
    }, status_code=500)


# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


# ==================== EXPORT API ====================

@app.get("/api/admin/export")
async def admin_export_data(
    type: str = "all",
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin veri export"""
    from fastapi.responses import Response

    from app.services.import_export import ImportExportService
    
    if not current_user or current_user.role.value not in ["admin", "superadmin"]:
        return {"error": "Yetkisiz"}
    
    service = ImportExportService(db)
    
    if type == "users":
        data = service.export_users(format)
    elif type == "servers":
        data = service.export_servers(format)
    elif type == "payments":
        data = service.export_payments(format)
    elif type == "forum":
        data = service.export_forum(format)
    else:
        data = service.export_all()
    
    content_type = "text/csv" if format == "csv" else "application/json"
    return Response(content=data, media_type=content_type)


# ==================== HEALTH CHECK ====================
@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Sistem sağlık kontrolü"""
    import psutil
    import redis as redis_lib
    
    health = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # Database check
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        health["checks"]["database"] = {"status": "ok"}
    except Exception as e:
        health["checks"]["database"] = {"status": "error", "message": str(e)}
        health["status"] = "degraded"
    
    # Redis check
    try:
        r = redis_lib.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)
        r.ping()
        health["checks"]["redis"] = {"status": "ok"}
    except Exception as e:
        health["checks"]["redis"] = {"status": "unavailable", "message": str(e)}
    
    # Disk check
    try:
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        health["checks"]["disk"] = {
            "status": "ok" if disk_percent < 90 else "warning",
            "used_percent": disk_percent,
            "free_gb": round(disk.free / (1024**3), 2)
        }
        if disk_percent >= 95:
            health["status"] = "degraded"
    except Exception as e:
        health["checks"]["disk"] = {"status": "error", "message": str(e)}
    
    # Memory check
    try:
        memory = psutil.virtual_memory()
        health["checks"]["memory"] = {
            "status": "ok" if memory.percent < 90 else "warning",
            "used_percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2)
        }
    except Exception as e:
        health["checks"]["memory"] = {"status": "error", "message": str(e)}
    
    # CPU check
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        health["checks"]["cpu"] = {
            "status": "ok" if cpu_percent < 90 else "warning",
            "used_percent": cpu_percent
        }
    except Exception as e:
        health["checks"]["cpu"] = {"status": "error", "message": str(e)}
    
    status_code = 200 if health["status"] == "healthy" else 503
    return JSONResponse(content=health, status_code=status_code)


# ==================== SITEMAP ====================
@app.get("/sitemap.xml")
async def sitemap(request: Request, db: Session = Depends(get_db)):
    """XML Sitemap oluştur"""
    from fastapi.responses import Response
    
    base_url = str(request.base_url).rstrip('/')
    
    # Static sayfalar
    static_pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "daily"},
        {"loc": "/forum", "priority": "0.9", "changefreq": "hourly"},
        {"loc": "/servers", "priority": "0.8", "changefreq": "daily"},
        {"loc": "/leaderboard", "priority": "0.7", "changefreq": "daily"},
        {"loc": "/members", "priority": "0.6", "changefreq": "daily"},
        {"loc": "/login", "priority": "0.5", "changefreq": "monthly"},
        {"loc": "/register", "priority": "0.5", "changefreq": "monthly"},
    ]
    
    # Dinamik sayfalar - Forum konuları
    topics = db.query(ForumTopic).filter(
        ForumTopic.is_visible == True
    ).order_by(ForumTopic.updated_at.desc()).limit(100).all()
    
    # Dinamik sayfalar - Duyurular
    announcements = db.query(Announcement).filter(
        Announcement.is_active == True
    ).order_by(Announcement.created_at.desc()).limit(50).all()
    
    # Dinamik sayfalar - Kullanıcı profilleri
    users = db.query(User).filter(
        User.status == UserStatus.ACTIVE
    ).order_by(User.created_at.desc()).limit(100).all()
    
    # XML oluştur
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Static sayfalar
    for page in static_pages:
        xml_content += f'''  <url>
    <loc>{base_url}{page["loc"]}</loc>
    <changefreq>{page["changefreq"]}</changefreq>
    <priority>{page["priority"]}</priority>
  </url>\n'''
    
    # Forum konuları
    for topic in topics:
        lastmod = topic.updated_at.strftime("%Y-%m-%d") if topic.updated_at else ""
        xml_content += f'''  <url>
    <loc>{base_url}/forum/topic/{topic.slug}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
  </url>\n'''
    
    # Duyurular
    for ann in announcements:
        if ann.slug:
            lastmod = ann.created_at.strftime("%Y-%m-%d") if ann.created_at else ""
            xml_content += f'''  <url>
    <loc>{base_url}/announcements/{ann.slug}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>\n'''
    
    # Kullanıcı profilleri
    for user in users:
        xml_content += f'''  <url>
    <loc>{base_url}/profile/{user.username}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.4</priority>
  </url>\n'''
    
    xml_content += '</urlset>'
    
    return Response(content=xml_content, media_type="application/xml")


# ==================== ROBOTS.TXT ====================
@app.get("/robots.txt")
async def robots(request: Request):
    """Robots.txt"""
    from fastapi.responses import PlainTextResponse
    
    base_url = str(request.base_url).rstrip('/')
    
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /panel/
Disallow: /api/
Disallow: /ws/

Sitemap: {base_url}/sitemap.xml
"""
    return PlainTextResponse(content=content)


# ==================== OFFLINE PAGE ====================
@app.get("/offline.html", response_class=HTMLResponse)
async def offline_page(request: Request):
    """PWA Offline sayfası"""
    return templates.TemplateResponse("offline.html", {"request": request})


# ==================== VUE.JS SPA CATCH-ALL ====================
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, full_path: str):
    """
    Catch-all route for Vue.js SPA
    Serves the Vue.js app for all routes not handled by API endpoints
    """
    import os

    # Skip API, admin API, WebSocket, and static file routes
    if full_path.startswith(('api/', 'ws/', 'static/', 'admin/api/')):
        return HTMLResponse(content="<h1>404 Not Found</h1>", status_code=404)

    # Serve Vue.js SPA index.html
    index_path = "/var/www/agtrmerkezi/static/dist/index.html"
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)

    return HTMLResponse(
        content="<h1>Vue app not built</h1><p>Run: cd /var/www/agtrmerkezi/frontend && npm run build</p>",
        status_code=500
    )