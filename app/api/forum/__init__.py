"""
AGTR Merkezi - Forum API Module
Modular forum system with clean separation of concerns
"""

from fastapi import APIRouter

from app.api.forum import categories, moderation, replies, stats, topics

# Create main forum router
router = APIRouter(prefix="/api/forum", tags=["Forum"])

# Include sub-routers
router.include_router(categories.router, prefix="/categories", tags=["Forum - Categories"])
router.include_router(topics.router, prefix="/topics", tags=["Forum - Topics"])
router.include_router(replies.router, prefix="/replies", tags=["Forum - Replies"])
router.include_router(moderation.router, prefix="/moderation", tags=["Forum - Moderation"])
router.include_router(stats.router, tags=["Forum - Stats"])

__all__ = ["router"]
