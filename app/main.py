"""
AGTR Merkezi - Ana Uygulama
Half-Life & CS 1.6 Gaming Community Platform
Vue.js SPA + FastAPI Backend
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging

# Setup logging
setup_logging(json_format=not settings.DEBUG, log_level="DEBUG" if settings.DEBUG else "INFO")
logger = get_logger(__name__)

from app.api import forum  # New modular forum API
from app.api import servers_unified  # New unified server API
from app.api import (
    activities,
    admin,
    analytics,
    analytics_enhanced,
    anticheat,
    assets,
    auth,
    banners,
    command_quotas,
    crash_stats,
    discord_bot,
    filemanager,
    forum_v2,
    game_assets,
    game_integration,
    games,
    leaderboard,
    maintenance,
    media,
    metrics,
    notifications,
    payment_gateway,
    payments,
    player_management,
    plugin_market,
    plugins,
    plugins_enhanced,
    profile_customization,
    rcon_limits,
    scheduler,
    scraper,
    security,
    server_management,
    server_v2,
    servers,
    smart_media,
    social,
    stats,
    system,
    templates,
    tournament,
    user,
    user_favorites,
    user_preferences,
    wallet,
    websocket,
    websocket_progress,
)
from app.api.admin import forum_categories as admin_forum_categories
from app.api.admin import forum_topics as admin_forum_topics
from app.api.admin import pages as admin_pages
from app.core.security import hash_password
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
    logger.warning(f"Core Engine: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü"""
    logger.info("=" * 50)
    logger.info("AGTR Merkezi v7.0 - Vue.js SPA Edition")
    logger.info("=" * 50)

    init_db()
    logger.info("Veritabanı tabloları hazır")

    create_default_data()
    logger.info("Varsayılan veriler yüklendi")

    # Halflife (Anti-Cheat) veritabanı bağlantısı
    try:
        from app.models.connection import init_halflife_db

        init_halflife_db()
        logger.info("Halflife (Anti-Cheat) veritabanı bağlantısı kuruldu")
    except Exception as e:
        logger.error(f"Halflife veritabanı bağlantısı kurulamadı: {e}", exc_info=True)

    # Redis başlat
    try:
        from app.core.redis_manager import redis_manager

        await redis_manager.connect()
        logger.info("Redis bağlantısı kuruldu")
    except Exception as e:
        logger.error(f"Redis bağlantısı kurulamadı: {e}", exc_info=True)

    # Scheduler başlat
    try:
        from app.tasks.scheduler import task_scheduler

        task_scheduler.start()
        logger.info("Scheduler başlatıldı")
    except Exception as e:
        logger.error(f"Scheduler başlatılamadı: {e}", exc_info=True)

    # Server Scheduler başlat (zamanlanmış görevler)
    try:
        from app.services.server_scheduler import scheduler_service

        scheduler_service.start()
        logger.info("Server scheduler başlatıldı")
    except Exception as e:
        logger.error(f"Server scheduler başlatılamadı: {e}", exc_info=True)

    # WebSocket heartbeat cleanup task
    try:
        import asyncio

        from app.core.websocket_manager import heartbeat_cleanup_task

        asyncio.create_task(heartbeat_cleanup_task())
        logger.info("WebSocket heartbeat task başlatıldı")
    except Exception as e:
        logger.warning(f"WebSocket task başlatılamadı: {e}")

    # Jackpot Manager başlat
    try:
        from app.tasks.jackpot_manager import start_jackpot_manager

        await start_jackpot_manager()
        logger.info("Jackpot manager başlatıldı")
    except Exception as e:
        logger.warning(f"Jackpot manager başlatılamadı: {e}")

    # Server Tasks başlat (izleme, auto-restart, istatistik)
    try:
        from app.tasks.server_tasks import start_server_tasks

        await start_server_tasks()
        logger.info("Server tasks başlatıldı")
    except Exception as e:
        logger.warning(f"Server tasks başlatılamadı: {e}")

    # Forum Tasks başlat (badge checking, reputation sync, cleanup)
    try:
        from app.tasks.forum_tasks import start_forum_tasks

        await start_forum_tasks()
        logger.info("Forum tasks başlatıldı")
    except Exception as e:
        logger.warning(f"Forum tasks başlatılamadı: {e}")

    logger.info("=" * 50)
    logger.info(f"API: {settings.BASE_URL}/api")
    logger.info(f"Docs: {settings.BASE_URL}/api/docs")
    logger.info("=" * 50)

    yield

    # Cleanup
    try:
        from app.core.redis_manager import redis_manager

        await redis_manager.disconnect()
        logger.info("Redis bağlantısı kapatıldı")
    except Exception as e:
        logger.warning(f"Redis cleanup hatası: {e}")

    try:
        from app.tasks.scheduler import task_scheduler

        task_scheduler.stop()
        logger.info("Scheduler durduruldu")
    except Exception:
        pass

    # Jackpot Manager durdur
    try:
        from app.tasks.jackpot_manager import stop_jackpot_manager

        await stop_jackpot_manager()
        logger.info("Jackpot manager durduruldu")
    except Exception:
        pass

    # Server Tasks durdur
    try:
        from app.tasks.server_tasks import stop_server_tasks

        await stop_server_tasks()
        logger.info("Server tasks durduruldu")
    except Exception:
        pass

    # Forum Tasks durdur
    try:
        from app.tasks.forum_tasks import stop_forum_tasks

        await stop_forum_tasks()
        logger.info("Forum tasks durduruldu")
    except Exception:
        pass

    logger.info("AGTR Merkezi kapatılıyor...")


def create_default_data():
    """Varsayılan verileri oluştur"""
    from app.models.connection import SessionLocal

    db = SessionLocal()

    try:
        # Superadmin kontrolü
        logger.debug("Superadmin kontrolü yapılıyor...")
        admin_user = db.query(User).filter(User.role == UserRole.SUPERADMIN).first()
        if not admin_user:
            admin_user = User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                role=UserRole.SUPERADMIN,
                status=UserStatus.ACTIVE,
                balance=1000.0,
            )
            db.add(admin_user)
            logger.info(f"Superadmin oluşturuldu: {settings.DEFAULT_ADMIN_USERNAME}")
        else:
            logger.debug(f"Mevcut superadmin bulundu: {admin_user.username}")

        # Forum kategorileri
        logger.debug("Forum kategorileri kontrol ediliyor...")
        category_count = db.query(ForumCategory).count()
        if category_count == 0:
            categories = [
                ForumCategory(
                    name="Genel",
                    slug="genel",
                    description="Genel konular",
                    icon="💬",
                    color="#3b82f6",
                ),
                ForumCategory(
                    name="Half-Life",
                    slug="half-life",
                    description="Half-Life tartismalari",
                    icon="🎮",
                    color="#f97316",
                ),
                ForumCategory(
                    name="Counter-Strike",
                    slug="counter-strike",
                    description="CS 1.6 tartismalari",
                    icon="🔫",
                    color="#22c55e",
                ),
                ForumCategory(
                    name="Teknik Destek",
                    slug="teknik-destek",
                    description="Teknik yardim",
                    icon="🔧",
                    color="#8b5cf6",
                ),
                ForumCategory(
                    name="Duyurular",
                    slug="duyurular",
                    description="Resmi duyurular",
                    icon="📢",
                    color="#ef4444",
                ),
            ]
            db.add_all(categories)
            logger.info(f"Forum kategorileri oluşturuldu: {len(categories)} kategori")
        else:
            logger.debug(f"Mevcut forum kategorileri: {category_count}")

        # Sunucu paketleri
        logger.debug("Sunucu paketleri kontrol ediliyor...")
        package_count = db.query(ServerPackage).count()
        if package_count == 0:
            packages = [
                # CS 1.6
                ServerPackage(
                    slug="cs16_starter",
                    name="CS 1.6 Starter",
                    game_type=GameType.CS16,
                    slots=12,
                    features=["basic_plugins"],
                    price_monthly=50.0,
                    description="Baslangic CS 1.6",
                    display_order=1,
                ),
                ServerPackage(
                    slug="cs16_pro",
                    name="CS 1.6 Pro",
                    game_type=GameType.CS16,
                    slots=20,
                    features=["basic_plugins", "rcon_access", "anticheat"],
                    price_monthly=80.0,
                    description="Rekabetci CS 1.6",
                    display_order=2,
                ),
                ServerPackage(
                    slug="cs16_ultimate",
                    name="CS 1.6 Ultimate",
                    game_type=GameType.CS16,
                    slots=32,
                    features=[
                        "basic_plugins",
                        "rcon_access",
                        "anticheat",
                        "custom_domain",
                        "priority_support",
                    ],
                    price_monthly=120.0,
                    description="Profesyonel CS 1.6",
                    display_order=3,
                ),
                # AG
                ServerPackage(
                    slug="ag_starter",
                    name="AG Starter",
                    game_type=GameType.AG,
                    slots=12,
                    features=["basic_plugins"],
                    price_monthly=50.0,
                    description="Baslangic AG",
                    display_order=4,
                ),
                ServerPackage(
                    slug="ag_pro",
                    name="AG Pro",
                    game_type=GameType.AG,
                    slots=20,
                    features=["basic_plugins", "rcon_access", "anticheat"],
                    price_monthly=80.0,
                    description="Rekabetci AG",
                    display_order=5,
                ),
                ServerPackage(
                    slug="ag_ultimate",
                    name="AG Ultimate",
                    game_type=GameType.AG,
                    slots=32,
                    features=[
                        "basic_plugins",
                        "rcon_access",
                        "anticheat",
                        "custom_domain",
                        "priority_support",
                    ],
                    price_monthly=120.0,
                    description="Profesyonel AG",
                    display_order=6,
                ),
                # HLDM
                ServerPackage(
                    slug="hldm_starter",
                    name="HLDM Starter",
                    game_type=GameType.HLDM,
                    slots=12,
                    features=["basic_plugins"],
                    price_monthly=50.0,
                    description="Baslangic HLDM",
                    display_order=7,
                ),
                ServerPackage(
                    slug="hldm_pro",
                    name="HLDM Pro",
                    game_type=GameType.HLDM,
                    slots=20,
                    features=["basic_plugins", "rcon_access", "anticheat"],
                    price_monthly=80.0,
                    description="Rekabetci HLDM",
                    display_order=8,
                ),
                ServerPackage(
                    slug="hldm_ultimate",
                    name="HLDM Ultimate",
                    game_type=GameType.HLDM,
                    slots=32,
                    features=[
                        "basic_plugins",
                        "rcon_access",
                        "anticheat",
                        "custom_domain",
                        "priority_support",
                    ],
                    price_monthly=120.0,
                    description="Profesyonel HLDM",
                    display_order=9,
                ),
            ]
            db.add_all(packages)
            logger.info(f"Sunucu paketleri oluşturuldu: {len(packages)} paket")
        else:
            logger.debug(f"Mevcut sunucu paketleri: {package_count}")

        # Site ayarlari
        logger.debug("Site ayarları kontrol ediliyor...")
        site_settings_count = db.query(SiteSettings).count()
        if site_settings_count == 0:
            site_settings = SiteSettings(
                site_name="AGTR Merkezi",
                site_description="Turkiye'nin en iyi Half-Life ve CS 1.6 platformu",
            )
            db.add(site_settings)
            logger.info("Site ayarları oluşturuldu")
        else:
            logger.debug("Mevcut site ayarları bulundu")

        # Varsayılan roller
        logger.debug("Varsayılan roller kontrol ediliyor...")
        try:
            from app.api.roles import initialize_default_roles

            initialize_default_roles(db)
            logger.debug("Varsayılan roller işlendi")
        except Exception as role_error:
            logger.warning(f"Varsayılan rol oluşturma uyarısı: {role_error}")

        db.commit()
        logger.debug("Varsayılan veriler başarıyla kaydedildi")

    except Exception as e:
        logger.error(f"Varsayılan veri oluşturma hatası: {type(e).__name__}: {e}", exc_info=True)
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
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Exception Handler Middleware (must be first to catch all exceptions)
from app.middleware.exception_handler import register_exception_handler

register_exception_handler(app)

# CORS middleware
cors_origins = (
    [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    if settings.DEBUG
    else [
        "https://agtrmerkezi.com",
        "https://www.agtrmerkezi.com",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# GZip Compression
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=500, compresslevel=6)

# Security Headers
from app.middleware.security_headers import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)

# Cache Control
from app.middleware.cache_control import CacheControlMiddleware

app.add_middleware(CacheControlMiddleware)

# Rate Limit
from app.middleware.rate_limit import RateLimitMiddleware

# Rate limit - test için yüksek limitler
app.add_middleware(RateLimitMiddleware, requests_per_minute=1000, requests_per_second=100)

# CSRF Protection
from app.middleware.csrf import CSRFMiddleware

app.add_middleware(CSRFMiddleware)

# Admin Access Control
from app.middleware.admin_access import AdminAccessMiddleware

app.add_middleware(AdminAccessMiddleware)

# Static files - for uploads and legacy assets
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ==================== API ROUTERS ====================

# Core APIs
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(user_favorites.router, prefix="/api", tags=["User Favorites"])
app.include_router(user_preferences.router, tags=["User Preferences"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["Wallet"])
app.include_router(games.router, prefix="/api/games", tags=["Games"])
app.include_router(leaderboard.router, prefix="/api", tags=["Leaderboard & ELO"])
app.include_router(game_integration.router, prefix="/api", tags=["Game Integration"])

# Role Management
from app.api import roles

app.include_router(roles.router, prefix="/api/roles", tags=["Roles"])

# ==================== NEW UNIFIED APIs (v3) ====================
# Modular Forum API - Replaces massive forum.py
app.include_router(forum.router, tags=["Forum v3 - Modular"])

# Unified Server API - Merges servers.py + server_v2.py
app.include_router(servers_unified.router, tags=["Servers v3 - Unified"])

# ==================== LEGACY APIs (Deprecated) ====================
# TODO: Remove after frontend migration complete
app.include_router(servers.router, prefix="/api/servers", tags=["Game Servers - LEGACY"])
app.include_router(metrics.router, tags=["Server Metrics"])
app.include_router(crash_stats.router, tags=["Crash Detection"])
app.include_router(command_quotas.router, tags=["Command Quotas"])
app.include_router(templates.router, tags=["Template Cache"])
app.include_router(plugins_enhanced.router, tags=["Plugin Management"])
app.include_router(analytics_enhanced.router, tags=["Advanced Analytics"])

# Legacy Forum APIs - TODO: Remove after migration
app.include_router(forum.router, prefix="/api/forum", tags=["Forum - LEGACY"])
app.include_router(forum_v2.router, prefix="/api", tags=["Forum v2 - Advanced Features - LEGACY"])
from app.api import forum_gamification

app.include_router(forum_gamification.router, prefix="/api", tags=["Forum Gamification"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])

# Admin APIs
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(admin_forum_categories.router, prefix="/api", tags=["Admin Forum"])
app.include_router(admin_forum_topics.router, prefix="/api", tags=["Admin Forum"])
app.include_router(admin_pages.router, tags=["Admin Pages"])

# Feature APIs
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(websocket_progress.router, tags=["Installation Progress"])
app.include_router(system.router, prefix="/api", tags=["System"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(payment_gateway.router, prefix="/api/payment", tags=["Payment Gateway"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(server_management.router, prefix="/api/management", tags=["Server Management"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["Maintenance"])
app.include_router(
    profile_customization.router,
    prefix="/api/profile/customization",
    tags=["Profile Customization"],
)

# Extended APIs
app.include_router(discord_bot.router, prefix="/api/discord", tags=["Discord Bot"])
app.include_router(tournament.router, prefix="/api/tournament", tags=["Tournament"])
app.include_router(plugin_market.router, prefix="/api/plugins", tags=["Plugin Market"])
app.include_router(media.router, tags=["Media Management"])
app.include_router(smart_media.router, tags=["Smart Media"])
app.include_router(banners.router, tags=["Banners & Advertisements"])

# Community Servers & Scraper
app.include_router(scraper.router, prefix="/api/community", tags=["Community Servers"])

# Game Assets & Scrapers
app.include_router(game_assets.router, prefix="/api", tags=["Game Assets"])

# Legacy Server Management v2 - TODO: Remove after migration
app.include_router(server_v2.router, tags=["Server Management v2 - LEGACY"])
app.include_router(scheduler.router, tags=["Scheduler"])
app.include_router(stats.router, tags=["Stats"])
app.include_router(filemanager.router, tags=["FileManager"])
app.include_router(plugins.router, tags=["Plugin Manager"])
app.include_router(rcon_limits.router, tags=["RCON Rate Limits"])
app.include_router(player_management.router, tags=["Player Management"])

# Anti-Cheat API (AGTR Anti-Cheat Integration)
app.include_router(anticheat.router, tags=["Anti-Cheat"])


# ==================== HEALTH & STATUS ====================


@app.get("/api/health")
async def health_check():
    """API health check"""
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/api/stats")
async def public_stats(db: Session = Depends(get_db)):
    """Public statistics"""

    return {
        "total_users": db.query(User).filter(User.status == UserStatus.ACTIVE).count(),
        "total_servers": db.query(GameServer).count(),
        "active_servers": db.query(GameServer)
        .filter(GameServer.status == ServerStatus.RUNNING)
        .count(),
        "total_topics": db.query(ForumTopic).count(),
        "total_posts": db.query(ForumPost).count(),
    }


@app.get("/api/announcements")
async def get_announcements(db: Session = Depends(get_db)):
    """Get active announcements"""
    announcements = (
        db.query(Announcement)
        .filter(Announcement.is_active == True)
        .order_by(Announcement.created_at.desc())
        .limit(5)
        .all()
    )

    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "type": a.type,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in announcements
    ]


@app.get("/api/packages")
async def get_packages(db: Session = Depends(get_db)):
    """Get available server packages"""
    packages = (
        db.query(ServerPackage)
        .filter(ServerPackage.is_active == True)
        .order_by(ServerPackage.display_order)
        .all()
    )

    return [
        {
            "id": p.id,
            "slug": p.slug,
            "name": p.name,
            "game_type": p.game_type.value,
            "slots": p.slots,
            "features": p.features,
            "price": p.price_monthly,
            "description": p.description,
        }
        for p in packages
    ]


@app.get("/api/leaderboard")
async def get_leaderboard(game: str = None, db: Session = Depends(get_db)):
    """Get player leaderboard"""
    query = db.query(User).filter(User.status == UserStatus.ACTIVE)

    # Order by some score metric (placeholder)
    users = query.order_by(User.balance.desc()).limit(50).all()

    return [
        {
            "rank": i + 1,
            "username": u.username,
            "score": int(u.balance or 0),
            "avatar": f"https://api.dicebear.com/7.x/initials/svg?seed={u.username}",
        }
        for i, u in enumerate(users)
    ]


@app.get("/api/public/settings")
async def get_public_settings(db: Session = Depends(get_db)):
    """Get public site settings (branding, logo, etc.) - no auth required"""
    site = db.query(SiteSettings).first()

    if not site:
        # Return defaults
        return {
            "site_name": "AGTR Merkezi",
            "site_description": "Half-Life & CS 1.6 Gaming Platform",
            "logo_url": "/logo-navbar.png",
            "logo_dark_url": "",
            "logo_mobile_url": "",
            "logo_width": "auto",
            "logo_height": "36",
            "logo_text": "AGTR",
            "logo_subtitle": "MERKEZİ",
            "show_logo_text": False,
            "footer_logo_url": "",
            "footer_logo_width": "auto",
            "footer_logo_height": "48",
            "favicon_url": "/favicon.ico",
            "primary_color": "#f97316",
            "secondary_color": "#3b82f6",
            "discord_url": "",
            "maintenance_mode": False,
        }

    return {
        "site_name": site.site_name or "AGTR Merkezi",
        "site_description": site.site_description or "",
        "logo_url": site.logo_url or "/logo-navbar.png",
        "logo_dark_url": site.logo_dark_url or "",
        "logo_mobile_url": site.logo_mobile_url or "",
        "logo_width": site.logo_width or "auto",
        "logo_height": site.logo_height or "36",
        "logo_text": site.logo_text or "AGTR",
        "logo_subtitle": site.logo_subtitle or "MERKEZİ",
        "show_logo_text": site.show_logo_text or False,
        "footer_logo_url": site.footer_logo_url or "",
        "footer_logo_width": site.footer_logo_width or "auto",
        "footer_logo_height": site.footer_logo_height or "48",
        "favicon_url": site.favicon_url or "/favicon.ico",
        "primary_color": site.primary_color or "#f97316",
        "secondary_color": site.secondary_color or "#3b82f6",
        "discord_url": site.discord_url or "",
        "maintenance_mode": site.maintenance_mode or False,
    }


# ==================== SPA FRONTEND ====================


# Serve Vue.js SPA - must be last!
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve Vue.js SPA for all non-API routes"""
    import os

    # Check if it's a static file request
    static_file = f"static/dist/{full_path}"
    if os.path.isfile(static_file):
        return FileResponse(static_file)

    # Check assets folder
    assets_file = f"static/dist/assets/{full_path}"
    if os.path.isfile(assets_file):
        return FileResponse(assets_file)

    # For all other routes, serve index.html (SPA routing)
    index_path = "static/dist/index.html"
    if os.path.isfile(index_path):
        return FileResponse(index_path)

    # Fallback to static folder root
    return FileResponse("static/dist/index.html")
