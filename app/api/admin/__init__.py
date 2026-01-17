# ============================================
# AGTR v6.0 - Admin API Package
# Dosya: app/api/admin/__init__.py
# ============================================

# Submodules
from . import forum_categories, forum_topics

# Main admin router from _main.py
from ._main import router

__all__ = ['router', 'forum_categories', 'forum_topics']
