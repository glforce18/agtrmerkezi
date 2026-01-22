# ============================================
# AGTR v6.0 - Admin API Package
# Dosya: app/api/admin/__init__.py
# ============================================

# Submodules
from . import forum_categories, forum_topics, forum_moderation

# Main admin router from _main.py
from ._main import router

# Include forum moderation router
router.include_router(forum_moderation.router)

__all__ = ['router', 'forum_categories', 'forum_topics', 'forum_moderation']
