# ============================================
# AGTR v6.0 - Admin API Package
# Dosya: app/api/admin/__init__.py
# ============================================

# Submodules
from . import commerce  # NEW: Payments & Packages
from . import content  # NEW: Announcements & Settings
from . import (
    dashboard,
    forum_categories,
    forum_moderation,
    forum_topics,
    health,
    pages,
    servers,
    stats,
    users,
)

# Main admin router from _main.py
from ._main import router

# Include user management router
router.include_router(users.router)

# Include server management router
router.include_router(servers.router)

# Include dashboard router
router.include_router(dashboard.router)

# Include pages router
router.include_router(pages.router)

# Include forum moderation router
router.include_router(forum_moderation.router)

# Include stats router
router.include_router(stats.router)

# Include health monitoring router
router.include_router(health.router)

# Include commerce router (NEW: payments & packages)
router.include_router(commerce.router)

# Include content router (NEW: announcements & settings)
router.include_router(content.router)

__all__ = [
    "router",
    "commerce",
    "content",
    "dashboard",
    "forum_categories",
    "forum_moderation",
    "forum_topics",
    "health",
    "pages",
    "servers",
    "stats",
    "users",
]
