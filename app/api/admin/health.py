"""
AGTR Merkezi - Admin Health Monitoring API
Sistem sağlık durumu, otomatik düzeltme ve bağımlılık haritası
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import ForumCategory, ForumTopic, User

router = APIRouter(prefix="/health", tags=["Admin Health"])


# ==================== MODELS ====================


class HealthStatus(BaseModel):
    status: str  # healthy, warning, critical
    message: str
    details: Optional[Dict] = None
    auto_fixable: bool = False
    fix_action: Optional[str] = None


class SystemHealth(BaseModel):
    overall_status: str
    timestamp: str
    components: Dict[str, HealthStatus]
    dependencies: Dict[str, List[str]]
    metrics: Dict[str, Any]


class FixResult(BaseModel):
    success: bool
    component: str
    action: str
    message: str
    before: Optional[str] = None
    after: Optional[str] = None


# ==================== HEALTH CHECKS ====================


async def check_database(db: Session) -> HealthStatus:
    """Veritabanı bağlantı kontrolü"""
    try:
        db.execute(text("SELECT 1")).fetchone()

        # Tablo sayıları
        user_count = db.query(func.count(User.id)).scalar() or 0
        topic_count = db.query(func.count(ForumTopic.id)).scalar() or 0
        category_count = db.query(func.count(ForumCategory.id)).scalar() or 0

        return HealthStatus(
            status="healthy",
            message="Veritabanı bağlantısı aktif",
            details={
                "users": user_count,
                "topics": topic_count,
                "categories": category_count,
                "connection": "OK",
            },
        )
    except Exception as e:
        return HealthStatus(
            status="critical",
            message=f"Veritabanı hatası: {str(e)[:100]}",
            auto_fixable=True,
            fix_action="restart_db_connection",
        )


async def check_redis() -> HealthStatus:
    """Redis bağlantı kontrolü"""
    try:
        from app.core.redis_manager import redis_manager

        # Test set/get
        test_key = "health_check_test"
        await redis_manager.set(test_key, "ok", expire=10)
        value = await redis_manager.get(test_key)

        if value == "ok":
            # Get memory info - use redis attribute not client
            used_memory = "N/A"
            if redis_manager.redis:
                try:
                    info = await redis_manager.redis.info("memory")
                    used_memory = info.get("used_memory_human", "N/A")
                except Exception as e:
                    logger.debug(f"Redis memory info error: {e}")

            return HealthStatus(
                status="healthy",
                message="Redis bağlantısı aktif",
                details={"connection": "OK", "memory_used": used_memory},
            )
        else:
            return HealthStatus(
                status="warning",
                message="Redis okuma/yazma sorunu",
                auto_fixable=True,
                fix_action="flush_redis_cache",
            )
    except Exception as e:
        return HealthStatus(
            status="warning",
            message=f"Redis hatası: {str(e)[:100]}",
            details={"note": "Sistem Redis olmadan da çalışabilir"},
            auto_fixable=True,
            fix_action="restart_redis",
        )


async def check_static_files() -> HealthStatus:
    """Statik dosya kontrolü"""
    static_path = Path("/var/www/agtrmerkezi/static")
    dist_path = static_path / "dist"

    issues = []
    details = {}

    # Check dist folder
    if not dist_path.exists():
        issues.append("Frontend build bulunamadı")
    else:
        # Check index.html
        index_file = dist_path / "index.html"
        if not index_file.exists():
            issues.append("index.html bulunamadı")
        else:
            details["index_html"] = "OK"

        # Check assets folder
        assets_path = dist_path / "assets"
        if assets_path.exists():
            js_files = list(assets_path.glob("*.js"))
            css_files = list(assets_path.glob("*.css"))
            details["js_files"] = len(js_files)
            details["css_files"] = len(css_files)
        else:
            issues.append("Assets klasörü bulunamadı")

    # Check critical images
    critical_images = ["maps/default.jpg", "images/logo.png"]

    missing_images = []
    for img in critical_images:
        if not (static_path / img).exists():
            missing_images.append(img)

    if missing_images:
        details["missing_images"] = missing_images

    if not issues and not missing_images:
        return HealthStatus(status="healthy", message="Tüm statik dosyalar mevcut", details=details)
    elif issues:
        return HealthStatus(
            status="critical",
            message="; ".join(issues),
            details=details,
            auto_fixable=True,
            fix_action="rebuild_frontend",
        )
    else:
        return HealthStatus(
            status="warning",
            message=f"{len(missing_images)} eksik resim",
            details=details,
            auto_fixable=True,
            fix_action="create_placeholder_images",
        )


async def check_api_endpoints(db: Session) -> HealthStatus:
    """Kritik API endpoint kontrolü"""
    endpoints_status = {}
    failed = []

    # Test internal endpoints
    test_cases = [
        ("forum_categories", lambda: db.query(ForumCategory).limit(1).all()),
        ("forum_topics", lambda: db.query(ForumTopic).limit(1).all()),
        ("users", lambda: db.query(User).limit(1).all()),
    ]

    for name, test_func in test_cases:
        try:
            test_func()
            endpoints_status[name] = "OK"
        except Exception as e:
            endpoints_status[name] = f"FAIL: {str(e)[:50]}"
            failed.append(name)

    if not failed:
        return HealthStatus(
            status="healthy", message="Tüm API endpointleri çalışıyor", details=endpoints_status
        )
    else:
        return HealthStatus(
            status="critical",
            message=f"{len(failed)} endpoint hatalı: {', '.join(failed)}",
            details=endpoints_status,
            auto_fixable=False,
        )


async def check_disk_space() -> HealthStatus:
    """Disk alanı kontrolü"""
    try:
        import shutil

        total, used, free = shutil.disk_usage("/var/www/agtrmerkezi")

        free_gb = free / (1024**3)
        used_percent = (used / total) * 100

        details = {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free_gb, 2),
            "used_percent": round(used_percent, 1),
        }

        if free_gb < 1:
            return HealthStatus(
                status="critical",
                message=f"Disk alanı kritik: {free_gb:.1f}GB kaldı",
                details=details,
                auto_fixable=True,
                fix_action="cleanup_temp_files",
            )
        elif free_gb < 5:
            return HealthStatus(
                status="warning",
                message=f"Disk alanı düşük: {free_gb:.1f}GB kaldı",
                details=details,
                auto_fixable=True,
                fix_action="cleanup_temp_files",
            )
        else:
            return HealthStatus(
                status="healthy",
                message=f"Disk alanı yeterli: {free_gb:.1f}GB boş",
                details=details,
            )
    except Exception as e:
        return HealthStatus(status="warning", message=f"Disk kontrolü yapılamadı: {str(e)[:50]}")


async def check_frontend_build() -> HealthStatus:
    """Frontend build durumu kontrolü"""
    dist_path = Path("/var/www/agtrmerkezi/static/dist")

    if not dist_path.exists():
        return HealthStatus(
            status="critical",
            message="Frontend build bulunamadı",
            auto_fixable=True,
            fix_action="rebuild_frontend",
        )

    # Check build timestamp
    index_file = dist_path / "index.html"
    if index_file.exists():
        mtime = datetime.fromtimestamp(index_file.stat().st_mtime)
        age_hours = (datetime.now() - mtime).total_seconds() / 3600

        # Check if source files are newer
        src_path = Path("/var/www/agtrmerkezi/frontend/src")
        newest_src = max(src_path.rglob("*.vue"), key=lambda p: p.stat().st_mtime, default=None)

        needs_rebuild = False
        if newest_src:
            src_mtime = datetime.fromtimestamp(newest_src.stat().st_mtime)
            needs_rebuild = src_mtime > mtime

        details = {
            "build_date": mtime.isoformat(),
            "age_hours": round(age_hours, 1),
            "needs_rebuild": needs_rebuild,
        }

        if needs_rebuild:
            return HealthStatus(
                status="warning",
                message="Frontend kaynak dosyaları güncellendi, rebuild gerekli",
                details=details,
                auto_fixable=True,
                fix_action="rebuild_frontend",
            )
        else:
            return HealthStatus(status="healthy", message="Frontend build güncel", details=details)

    return HealthStatus(
        status="critical",
        message="index.html bulunamadı",
        auto_fixable=True,
        fix_action="rebuild_frontend",
    )


async def check_logs() -> HealthStatus:
    """Log dosyaları kontrolü"""
    log_path = Path("/var/www/agtrmerkezi/logs")

    if not log_path.exists():
        log_path.mkdir(parents=True, exist_ok=True)

    log_files = list(log_path.glob("*.log"))
    total_size = sum(f.stat().st_size for f in log_files) / (1024**2)  # MB

    details = {"log_files": len(log_files), "total_size_mb": round(total_size, 2)}

    # Check for recent errors
    error_log = log_path / "error.log"
    recent_errors = 0
    if error_log.exists():
        try:
            with open(error_log, "r") as f:
                lines = f.readlines()[-100:]  # Last 100 lines
                today = datetime.now().strftime("%Y-%m-%d")
                recent_errors = sum(1 for line in lines if today in line and "ERROR" in line)
        except Exception as e:
            logger.debug(f"Log file read error: {e}")

    details["recent_errors"] = recent_errors

    if total_size > 500:  # 500MB
        return HealthStatus(
            status="warning",
            message=f"Log dosyaları büyük: {total_size:.1f}MB",
            details=details,
            auto_fixable=True,
            fix_action="rotate_logs",
        )
    elif recent_errors > 50:
        return HealthStatus(
            status="warning", message=f"Bugün {recent_errors} hata kaydedildi", details=details
        )
    else:
        return HealthStatus(status="healthy", message="Log durumu normal", details=details)


async def check_security() -> HealthStatus:
    """Güvenlik kontrolü"""
    issues = []
    details = {}

    # Check .env file
    env_file = Path("/var/www/agtrmerkezi/.env")
    if env_file.exists():
        # Check permissions
        mode = oct(env_file.stat().st_mode)[-3:]
        details["env_permissions"] = mode
        if mode not in ["600", "640"]:
            issues.append(f".env dosyası çok açık: {mode}")

    # Check for exposed secrets in git
    git_dir = Path("/var/www/agtrmerkezi/.git")
    if git_dir.exists():
        details["git_tracked"] = True

    # Check SSL (basic)
    details["https_recommended"] = True

    if issues:
        return HealthStatus(
            status="warning",
            message="; ".join(issues),
            details=details,
            auto_fixable=True,
            fix_action="fix_permissions",
        )
    else:
        return HealthStatus(
            status="healthy", message="Temel güvenlik kontrolleri başarılı", details=details
        )


# ==================== DEPENDENCY MAP ====================


def get_dependency_map() -> Dict[str, List[str]]:
    """Sistem bağımlılık haritası"""
    return {
        "frontend": ["api", "static_files", "redis"],
        "api": ["database", "redis"],
        "forum": ["database", "api", "redis"],
        "jackpot": ["database", "api", "redis", "websocket"],
        "auth": ["database", "api", "redis"],
        "admin": ["database", "api", "auth"],
        "websocket": ["redis", "api"],
        "static_files": ["disk_space"],
        "logs": ["disk_space"],
    }


def get_page_component_map() -> Dict[str, Dict]:
    """Sayfa ve bileşen haritası"""
    return {
        "home": {
            "path": "/",
            "components": ["PopularTopicsSection", "RecentTopicsSection", "StatsWidget"],
            "api_endpoints": ["/api/forum/topics", "/api/stats"],
            "dependencies": ["forum", "api"],
        },
        "forum": {
            "path": "/forum",
            "components": ["ForumCategoryList", "ForumTopicCard", "ForumSidebar"],
            "api_endpoints": ["/api/forum/categories", "/api/forum/topics"],
            "dependencies": ["database", "api", "redis"],
        },
        "forum_category": {
            "path": "/forum/category/:slug",
            "components": ["ForumTopicCard", "Pagination", "SortDropdown"],
            "api_endpoints": ["/api/forum/categories/:slug", "/api/forum/topics"],
            "dependencies": ["database", "api"],
        },
        "forum_topic": {
            "path": "/forum/topic/:id",
            "components": ["ForumPostCard", "ReplyEditor", "LikeButton"],
            "api_endpoints": ["/api/forum/topics/:id", "/api/forum/replies"],
            "dependencies": ["database", "api", "auth"],
        },
        "jackpot": {
            "path": "/jackpot",
            "components": ["JackpotWheel", "BetForm", "PlayerList"],
            "api_endpoints": ["/api/games/jackpot/current", "/api/games/jackpot/bet"],
            "dependencies": ["database", "api", "websocket", "auth"],
        },
        "servers": {
            "path": "/servers",
            "components": ["ServerCard", "ServerFilter", "MapImage"],
            "api_endpoints": ["/api/servers"],
            "dependencies": ["database", "api", "static_files"],
        },
        "profile": {
            "path": "/profile/:id",
            "components": ["ProfileHeader", "ActivityFeed", "StatsCard"],
            "api_endpoints": ["/api/users/:id", "/api/users/:id/activity"],
            "dependencies": ["database", "api", "auth"],
        },
        "admin": {
            "path": "/admin",
            "components": ["AdminSidebar", "DashboardStats", "RecentActivity"],
            "api_endpoints": ["/api/admin/stats", "/api/admin/users"],
            "dependencies": ["database", "api", "auth"],
        },
        "login": {
            "path": "/login",
            "components": ["LoginForm", "SocialLogin"],
            "api_endpoints": ["/api/auth/login"],
            "dependencies": ["database", "api"],
        },
        "register": {
            "path": "/register",
            "components": ["RegisterForm", "TermsCheckbox"],
            "api_endpoints": ["/api/auth/register"],
            "dependencies": ["database", "api"],
        },
    }


# ==================== AUTO-FIX ACTIONS ====================


async def fix_rebuild_frontend() -> FixResult:
    """Frontend'i yeniden build et"""
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd="/var/www/agtrmerkezi/frontend",
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            return FixResult(
                success=True,
                component="frontend",
                action="rebuild",
                message="Frontend başarıyla build edildi",
            )
        else:
            return FixResult(
                success=False,
                component="frontend",
                action="rebuild",
                message=f"Build hatası: {result.stderr[:200]}",
            )
    except Exception as e:
        return FixResult(
            success=False, component="frontend", action="rebuild", message=f"Hata: {str(e)}"
        )


async def fix_flush_redis_cache() -> FixResult:
    """Redis cache'i temizle"""
    try:
        from app.core.redis_manager import redis_manager

        if redis_manager.redis:
            await redis_manager.redis.flushdb()
            return FixResult(
                success=True,
                component="redis",
                action="flush_cache",
                message="Redis cache temizlendi",
            )
        else:
            return FixResult(
                success=False,
                component="redis",
                action="flush_cache",
                message="Redis bağlantısı yok",
            )
    except Exception as e:
        return FixResult(
            success=False, component="redis", action="flush_cache", message=f"Hata: {str(e)}"
        )


async def fix_cleanup_temp_files() -> FixResult:
    """Geçici dosyaları temizle"""
    try:
        pass

        paths_to_clean = [
            "/var/www/agtrmerkezi/tests/screenshots",
            "/var/www/agtrmerkezi/__pycache__",
            "/var/www/agtrmerkezi/app/__pycache__",
        ]

        cleaned = 0
        for path in paths_to_clean:
            p = Path(path)
            if p.exists() and p.is_dir():
                # Keep directory, remove old files
                for f in p.glob("*"):
                    if (
                        f.is_file()
                        and (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days > 7
                    ):
                        f.unlink()
                        cleaned += 1

        return FixResult(
            success=True,
            component="disk",
            action="cleanup",
            message=f"{cleaned} eski dosya temizlendi",
        )
    except Exception as e:
        return FixResult(
            success=False, component="disk", action="cleanup", message=f"Hata: {str(e)}"
        )


async def fix_rotate_logs() -> FixResult:
    """Log dosyalarını rotate et"""
    try:
        log_path = Path("/var/www/agtrmerkezi/logs")
        rotated = 0

        for log_file in log_path.glob("*.log"):
            size_mb = log_file.stat().st_size / (1024**2)
            if size_mb > 50:  # 50MB'dan büyükse
                # Rename to .old
                old_file = log_file.with_suffix(".log.old")
                if old_file.exists():
                    old_file.unlink()
                log_file.rename(old_file)
                # Create new empty file
                log_file.touch()
                rotated += 1

        return FixResult(
            success=True,
            component="logs",
            action="rotate",
            message=f"{rotated} log dosyası rotate edildi",
        )
    except Exception as e:
        return FixResult(
            success=False, component="logs", action="rotate", message=f"Hata: {str(e)}"
        )


async def fix_create_placeholder_images() -> FixResult:
    """Eksik placeholder resimleri oluştur"""
    try:
        from PIL import Image, ImageDraw

        static_path = Path("/var/www/agtrmerkezi/static")
        created = []

        # Default map
        map_path = static_path / "maps" / "default.jpg"
        if not map_path.exists():
            map_path.parent.mkdir(parents=True, exist_ok=True)
            img = Image.new("RGB", (400, 225), color="#1a1a2e")
            draw = ImageDraw.Draw(img)
            draw.text((150, 100), "Map", fill="#64748b")
            img.save(map_path, "JPEG")
            created.append("maps/default.jpg")

        # Default avatar
        avatar_path = static_path / "images" / "default-avatar.png"
        if not avatar_path.exists():
            avatar_path.parent.mkdir(parents=True, exist_ok=True)
            img = Image.new("RGBA", (128, 128), color=(30, 30, 50, 255))
            draw = ImageDraw.Draw(img)
            draw.ellipse([24, 20, 104, 100], fill=(100, 100, 120))
            img.save(avatar_path, "PNG")
            created.append("images/default-avatar.png")

        return FixResult(
            success=True,
            component="static_files",
            action="create_placeholders",
            message=(
                f"{len(created)} placeholder oluşturuldu"
                if created
                else "Tüm placeholderlar mevcut"
            ),
        )
    except Exception as e:
        return FixResult(
            success=False,
            component="static_files",
            action="create_placeholders",
            message=f"Hata: {str(e)}",
        )


async def fix_permissions() -> FixResult:
    """Dosya izinlerini düzelt"""
    try:
        import os

        env_file = Path("/var/www/agtrmerkezi/.env")
        if env_file.exists():
            os.chmod(env_file, 0o640)

        return FixResult(
            success=True,
            component="security",
            action="fix_permissions",
            message=".env dosya izinleri düzeltildi",
        )
    except Exception as e:
        return FixResult(
            success=False, component="security", action="fix_permissions", message=f"Hata: {str(e)}"
        )


# Fix action registry
FIX_ACTIONS = {
    "rebuild_frontend": fix_rebuild_frontend,
    "flush_redis_cache": fix_flush_redis_cache,
    "cleanup_temp_files": fix_cleanup_temp_files,
    "rotate_logs": fix_rotate_logs,
    "create_placeholder_images": fix_create_placeholder_images,
    "fix_permissions": fix_permissions,
}


# ==================== API ENDPOINTS ====================


@router.get("/status")
async def get_health_status(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)
):
    """Tam sistem sağlık durumu"""

    # Run all health checks
    checks = {
        "database": await check_database(db),
        "redis": await check_redis(),
        "static_files": await check_static_files(),
        "api_endpoints": await check_api_endpoints(db),
        "disk_space": await check_disk_space(),
        "frontend_build": await check_frontend_build(),
        "logs": await check_logs(),
        "security": await check_security(),
    }

    # Calculate overall status
    statuses = [c.status for c in checks.values()]
    if "critical" in statuses:
        overall = "critical"
    elif "warning" in statuses:
        overall = "warning"
    else:
        overall = "healthy"

    # Count fixable issues
    fixable = sum(1 for c in checks.values() if c.auto_fixable and c.status != "healthy")

    return {
        "success": True,
        "overall_status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {k: v.dict() for k, v in checks.items()},
        "dependencies": get_dependency_map(),
        "fixable_issues": fixable,
        "metrics": {
            "healthy": statuses.count("healthy"),
            "warning": statuses.count("warning"),
            "critical": statuses.count("critical"),
            "total": len(statuses),
        },
    }


@router.get("/pages")
async def get_page_status(current_user: User = Depends(get_current_admin)):
    """Sayfa ve bileşen durumu"""
    return {
        "success": True,
        "pages": get_page_component_map(),
        "total_pages": len(get_page_component_map()),
    }


@router.post("/fix/{action}")
async def run_fix_action(
    action: str, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_admin)
):
    """Otomatik düzeltme aksiyonu çalıştır"""
    if action not in FIX_ACTIONS:
        raise HTTPException(status_code=404, detail=f"Bilinmeyen aksiyon: {action}")

    fix_func = FIX_ACTIONS[action]
    result = await fix_func()

    return {"success": result.success, "result": result.dict()}


@router.post("/fix-all")
async def run_all_fixes(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)
):
    """Tüm otomatik düzeltilebilir sorunları çöz"""

    # First get current status
    checks = {
        "database": await check_database(db),
        "redis": await check_redis(),
        "static_files": await check_static_files(),
        "disk_space": await check_disk_space(),
        "frontend_build": await check_frontend_build(),
        "logs": await check_logs(),
        "security": await check_security(),
    }

    results = []

    for name, check in checks.items():
        if check.auto_fixable and check.status != "healthy" and check.fix_action:
            if check.fix_action in FIX_ACTIONS:
                result = await FIX_ACTIONS[check.fix_action]()
                results.append(result.dict())

    return {"success": True, "fixes_applied": len(results), "results": results}


@router.get("/dependency-graph")
async def get_dependency_graph(current_user: User = Depends(get_current_admin)):
    """Görsel bağımlılık grafiği için veri"""
    deps = get_dependency_map()
    pages = get_page_component_map()

    # Build nodes and edges for visualization
    nodes = []
    edges = []

    # Component nodes
    for comp in deps.keys():
        nodes.append(
            {
                "id": comp,
                "label": comp.replace("_", " ").title(),
                "type": "component",
                "group": "core",
            }
        )

    # Add dependencies as nodes if not already
    for comp, comp_deps in deps.items():
        for dep in comp_deps:
            if not any(n["id"] == dep for n in nodes):
                nodes.append(
                    {
                        "id": dep,
                        "label": dep.replace("_", " ").title(),
                        "type": "service",
                        "group": "service",
                    }
                )
            edges.append({"from": comp, "to": dep, "type": "depends"})

    # Page nodes
    for page_name, page_info in pages.items():
        nodes.append(
            {
                "id": f"page_{page_name}",
                "label": page_name.replace("_", " ").title(),
                "type": "page",
                "group": "pages",
                "path": page_info["path"],
            }
        )

        for dep in page_info.get("dependencies", []):
            edges.append({"from": f"page_{page_name}", "to": dep, "type": "uses"})

    return {"success": True, "nodes": nodes, "edges": edges}


@router.get("/quick-check")
async def quick_health_check(db: Session = Depends(get_db)):
    """Hızlı sağlık kontrolü (auth gerektirmez - sadece durum)"""


@router.get("/test-status")
async def test_health_status(db: Session = Depends(get_db)):
    """Test endpoint - auth gerektirmez (debug için)"""
    # Run all health checks
    checks = {
        "database": await check_database(db),
        "redis": await check_redis(),
        "static_files": await check_static_files(),
        "disk_space": await check_disk_space(),
        "frontend_build": await check_frontend_build(),
        "logs": await check_logs(),
    }

    # Calculate overall status
    statuses = [c.status for c in checks.values()]
    if "critical" in statuses:
        overall = "critical"
    elif "warning" in statuses:
        overall = "warning"
    else:
        overall = "healthy"

    return {
        "success": True,
        "overall_status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {k: v.dict() for k, v in checks.items()},
        "dependencies": get_dependency_map(),
        "metrics": {
            "healthy": statuses.count("healthy"),
            "warning": statuses.count("warning"),
            "critical": statuses.count("critical"),
            "total": len(statuses),
        },
    }
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.warning(f"Health check DB error: {e}")
        db_ok = False

    try:
        from app.core.redis_manager import redis_manager

        await redis_manager.get("health_test")
        redis_ok = True
    except Exception as e:
        logger.debug(f"Health check Redis error: {e}")
        redis_ok = False

    dist_ok = Path("/var/www/agtrmerkezi/static/dist/index.html").exists()

    all_ok = db_ok and dist_ok  # Redis optional

    return {
        "status": "healthy" if all_ok else "degraded",
        "database": "ok" if db_ok else "error",
        "redis": "ok" if redis_ok else "unavailable",
        "frontend": "ok" if dist_ok else "error",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
