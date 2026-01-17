# ============================================
# AGTR v6.0 - Forum Models (Re-export)
# Dosya: app/models/forum.py
# Bu dosya database.py'deki forum modellerini re-export eder
# ============================================

from app.models.database import (
    Base,
    ForumCategory,
    ForumPost,
    ForumPostLike,
    ForumReply,
    ForumTopic,
)

__all__ = [
    'Base',
    'ForumCategory',
    'ForumTopic',
    'ForumPost',
    'ForumPostLike',
    'ForumReply'
]
