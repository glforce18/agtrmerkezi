"""
AGTR Merkezi - Ana Uygulama
Half-Life & CS 1.6 Gaming Community Platform
Vue.js SPA + FastAPI Backend
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
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
    game_integration,
    games,
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
    wallet,
    websocket,
)
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
    Role,
    ServerPackage,
    ServerStatus,
    SiteSettings,
    User,
    UserRole,
    UserRoleAssignment,
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
    print("AGTR Merkezi v7.0 - Vue.js SPA Edition")
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

    # Jackpot Manager baslat (devre disi - model uyumsuzlugu)
    # TODO: JackpotGame modeline uyumlu hale getir
    # try:
    #     from app.tasks.jackpot_manager import start_jackpot_manager
    #     import asyncio
    #     asyncio.create_task(start_jackpot_manager())
    #     print("[OK] Jackpot manager baslatildi")
    # except Exception as e:
    #     print(f"[UYARI] Jackpot manager baslatilamadi: {e}")
    print("[BILGI] Jackpot manager devre disi (model guncelleniyor)")

    print("=" * 50)
    print(f"API: {settings.BASE_URL}/api")
    print(f"Docs: {settings.BASE_URL}/api/docs")
    print("=" * 50)

    yield

    # Cleanup
    try:
        from app.core.redis_manager import redis_manager
        await redis_manager.disconnect()
        print("[OK] Redis baglantisi kapatildi")
    except Exception as e:
        print(f"[UYARI] Redis cleanup hatasi: {e}")

    try:
        from app.tasks.scheduler import task_scheduler
        task_scheduler.stop()
        print("[OK] Scheduler durduruldu")
    except Exception:
        pass

    # Jackpot Manager durdur
    try:
        from app.tasks.jackpot_manager import stop_jackpot_manager
        await stop_jackpot_manager()
        print("[OK] Jackpot manager durduruldu")
    except Exception:
        pass

    print("AGTR Merkezi kapatiliyor...")


def create_default_data():
    """Varsayilan verileri olustur"""
    from app.models.connection import SessionLocal
    db = SessionLocal()

    try:
        # Superadmin kontrolu
        admin_user = db.query(User).filter(User.role == UserRole.SUPERADMIN).first()
        if not admin_user:
            admin_user = User(
                username=settings.DEFAULT_ADMIN_USERNAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                role=UserRole.SUPERADMIN,
                status=UserStatus.ACTIVE,
                balance=1000.0
            )
            db.add(admin_user)
            print("  -> Superadmin olusturuldu")

        # Forum kategorileri
        if db.query(ForumCategory).count() == 0:
            categories = [
                ForumCategory(name="Genel", slug="genel", description="Genel konular", icon="message-circle", color="#3b82f6"),
                ForumCategory(name="Half-Life", slug="half-life", description="Half-Life tartismalari", icon="crosshair", color="#f97316"),
                ForumCategory(name="Counter-Strike", slug="counter-strike", description="CS 1.6 tartismalari", icon="target", color="#22c55e"),
                ForumCategory(name="Teknik Destek", slug="teknik-destek", description="Teknik yardim", icon="help-circle", color="#8b5cf6"),
                ForumCategory(name="Duyurular", slug="duyurular", description="Resmi duyurular", icon="megaphone", color="#ef4444", is_announcement=True),
            ]
            db.add_all(categories)
            print("  -> Forum kategorileri olusturuldu")

        # Sunucu paketleri
        if db.query(ServerPackage).count() == 0:
            packages = [
                # CS 1.6
                ServerPackage(slug="cs16_starter", name="CS 1.6 Starter", game_type=GameType.CS16, slots=12, features=["basic_plugins"], price_monthly=50.0, description="Baslangic CS 1.6", display_order=1),
                ServerPackage(slug="cs16_pro", name="CS 1.6 Pro", game_type=GameType.CS16, slots=20, features=["basic_plugins", "rcon_access", "anticheat"], price_monthly=80.0, description="Rekabetci CS 1.6", display_order=2),
                ServerPackage(slug="cs16_ultimate", name="CS 1.6 Ultimate", game_type=GameType.CS16, slots=32, features=["basic_plugins", "rcon_access", "anticheat", "custom_domain", "priority_support"], price_monthly=120.0, description="Profesyonel CS 1.6", display_order=3),
                # AG
                ServerPackage(slug="ag_starter", name="AG Starter", game_type=GameType.AG, slots=12, features=["basic_plugins"], price_monthly=50.0, description="Baslangic AG", display_order=4),
                ServerPackage(slug="ag_pro", name="AG Pro", game_type=GameType.AG, slots=20, features=["basic_plugins", "rcon_access", "anticheat"], price_monthly=80.0, description="Rekabetci AG", display_order=5),
                ServerPackage(slug="ag_ultimate", name="AG Ultimate", game_type=GameType.AG, slots=32, features=["basic_plugins", "rcon_access", "anticheat", "custom_domain", "priority_support"], price_monthly=120.0, description="Profesyonel AG", display_order=6),
                # HLDM
                ServerPackage(slug="hldm_starter", name="HLDM Starter", game_type=GameType.HLDM, slots=12, features=["basic_plugins"], price_monthly=50.0, description="Baslangic HLDM", display_order=7),
                ServerPackage(slug="hldm_pro", name="HLDM Pro", game_type=GameType.HLDM, slots=20, features=["basic_plugins", "rcon_access", "anticheat"], price_monthly=80.0, description="Rekabetci HLDM", display_order=8),
                ServerPackage(slug="hldm_ultimate", name="HLDM Ultimate", game_type=GameType.HLDM, slots=32, features=["basic_plugins", "rcon_access", "anticheat", "custom_domain", "priority_support"], price_monthly=120.0, description="Profesyonel HLDM", display_order=9),
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

        # Varsayilan roller
        from app.api.roles import initialize_default_roles
        initialize_default_roles(db)
        print("  -> Varsayilan roller olusturuldu")

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

# CORS middleware
cors_origins = ["*"] if settings.DEBUG else [
    "https://agtrmerkezi.com",
    "https://www.agtrmerkezi.com",
    "http://localhost:3000",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
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
app.add_middleware(RateLimitMiddleware)

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
app.include_router(wallet.router, prefix="/api/wallet", tags=["Wallet"])
app.include_router(games.router, prefix="/api/games", tags=["Games"])
app.include_router(game_integration.router, prefix="/api", tags=["Game Integration"])

# Role Management
from app.api import roles
app.include_router(roles.router, prefix="/api/roles", tags=["Roles"])
app.include_router(servers.router, prefix="/api/servers", tags=["Game Servers"])
app.include_router(forum.router, prefix="/api/forum", tags=["Forum"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])

# Admin APIs
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(admin_forum_categories.router, tags=["Admin Forum"])
app.include_router(admin_forum_topics.router, tags=["Admin Forum"])

# Feature APIs
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(system.router, prefix="/api", tags=["System"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(payment_gateway.router, prefix="/api/payment", tags=["Payment Gateway"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(server_management.router, prefix="/api/management", tags=["Server Management"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])

# Extended APIs
app.include_router(discord_bot.router, prefix="/api/discord", tags=["Discord Bot"])
app.include_router(tournament.router, prefix="/api/tournament", tags=["Tournament"])
app.include_router(plugin_market.router, prefix="/api/plugins", tags=["Plugin Market"])
app.include_router(media.router, tags=["Media Management"])
app.include_router(smart_media.router, tags=["Smart Media"])
app.include_router(banners.router, tags=["Banners & Advertisements"])


# ==================== HEALTH & STATUS ====================

@app.get("/api/health")
async def health_check():
    """API health check"""
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/api/stats")
async def public_stats(db: Session = Depends(get_db)):
    """Public statistics"""
    from app.models.database import Payment, PaymentStatus

    return {
        "total_users": db.query(User).filter(User.status == UserStatus.ACTIVE).count(),
        "total_servers": db.query(GameServer).count(),
        "active_servers": db.query(GameServer).filter(GameServer.status == ServerStatus.RUNNING).count(),
        "total_topics": db.query(ForumTopic).count(),
        "total_posts": db.query(ForumPost).count(),
    }


@app.get("/api/announcements")
async def get_announcements(db: Session = Depends(get_db)):
    """Get active announcements"""
    announcements = db.query(Announcement).filter(
        Announcement.is_active == True
    ).order_by(Announcement.created_at.desc()).limit(5).all()

    return [{
        "id": a.id,
        "title": a.title,
        "content": a.content,
        "type": a.type,
        "created_at": a.created_at.isoformat() if a.created_at else None
    } for a in announcements]


@app.get("/api/packages")
async def get_packages(db: Session = Depends(get_db)):
    """Get available server packages"""
    packages = db.query(ServerPackage).filter(
        ServerPackage.is_active == True
    ).order_by(ServerPackage.display_order).all()

    return [{
        "id": p.id,
        "slug": p.slug,
        "name": p.name,
        "game_type": p.game_type.value,
        "slots": p.slots,
        "features": p.features,
        "price": p.price_monthly,
        "description": p.description
    } for p in packages]


@app.get("/api/leaderboard")
async def get_leaderboard(game: str = None, db: Session = Depends(get_db)):
    """Get player leaderboard"""
    query = db.query(User).filter(User.status == UserStatus.ACTIVE)

    # Order by some score metric (placeholder)
    users = query.order_by(User.balance.desc()).limit(50).all()

    return [{
        "rank": i + 1,
        "username": u.username,
        "score": int(u.balance or 0),
        "avatar": f"https://api.dicebear.com/7.x/initials/svg?seed={u.username}"
    } for i, u in enumerate(users)]
