# ============================================
# AGTR v6.0 - Forum Gamification Services
# Dosya: app/services/forum_gamification.py
# Badge System, Reputation, and CAPTCHA
# ============================================

import hashlib
import logging
import random
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ============ Reputation Constants ============
REPUTATION_TOPIC_CREATE = 5
REPUTATION_REPLY_CREATE = 2
REPUTATION_LIKE_RECEIVED = 1
REPUTATION_REPORTED_CONTENT = -10  # When confirmed as bad content

# ============ Badge Definitions ============
# These are the default badges to be created in the database
DEFAULT_BADGES = [
    {
        "name": "Ilk Adim",
        "slug": "ilk-adim",
        "description": "Ilk konunu olustur",
        "icon": "star",
        "color": "#4CAF50",
        "requirement_type": "topics_count",
        "requirement_value": 1
    },
    {
        "name": "Yardımsever",
        "slug": "yardimsever",
        "description": "10 yanit yaz",
        "icon": "heart",
        "color": "#2196F3",
        "requirement_type": "replies_count",
        "requirement_value": 10
    },
    {
        "name": "Populer",
        "slug": "populer",
        "description": "100 begeni al",
        "icon": "thumbs-up",
        "color": "#FF9800",
        "requirement_type": "likes_received",
        "requirement_value": 100
    },
    {
        "name": "Uzman",
        "slug": "uzman",
        "description": "50 konu olustur",
        "icon": "award",
        "color": "#9C27B0",
        "requirement_type": "topics_count",
        "requirement_value": 50
    },
    {
        "name": "Efsane",
        "slug": "efsane",
        "description": "500 yanit yaz",
        "icon": "crown",
        "color": "#F44336",
        "requirement_type": "replies_count",
        "requirement_value": 500
    }
]

# CAPTCHA settings
CAPTCHA_TTL = 300  # 5 minutes
NEW_USER_POST_THRESHOLD = 5  # Users with fewer than this many posts need CAPTCHA


class ForumGamificationService:
    """Service for forum gamification features"""

    def __init__(self, db: Session):
        self.db = db

    # ============ Reputation Methods ============

    def add_reputation(self, user_id: int, amount: int, reason: str = "") -> int:
        """Add (or subtract) reputation to a user"""
        from app.models.database import User

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return 0

        old_rep = user.reputation or 0
        new_rep = old_rep + amount

        # Reputation cannot go below 0
        if new_rep < 0:
            new_rep = 0

        user.reputation = new_rep
        self.db.commit()

        logger.info(f"User {user_id} reputation changed: {old_rep} -> {new_rep} ({amount:+d}) - {reason}")
        return new_rep

    def get_reputation_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users by reputation"""
        from app.models.database import User

        users = self.db.query(User).filter(
            User.reputation > 0
        ).order_by(
            User.reputation.desc()
        ).limit(limit).all()

        return [
            {
                "rank": idx + 1,
                "user_id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "avatar": user.avatar,
                "reputation": user.reputation or 0
            }
            for idx, user in enumerate(users)
        ]

    # ============ Badge Methods ============

    async def check_and_award_badges(self, user_id: int) -> List[Dict]:
        """Check if user has earned any new badges and award them"""
        from app.models.database import ForumBadge, UserForumBadge, User
        from app.models.forum import ForumTopic, ForumReply

        awarded = []

        # Get user stats
        topics_count = self.db.query(func.count(ForumTopic.id)).filter(
            ForumTopic.author_id == user_id,
            ForumTopic.is_active == True
        ).scalar() or 0

        replies_count = self.db.query(func.count(ForumReply.id)).filter(
            ForumReply.user_id == user_id,
            ForumReply.is_active == True
        ).scalar() or 0

        # Get likes received (assuming ForumPostLike exists)
        likes_received = 0
        try:
            from app.models.database import ForumPostLike, ForumPost
            likes_received = self.db.query(func.count(ForumPostLike.id)).join(
                ForumPost, ForumPost.id == ForumPostLike.post_id
            ).filter(
                ForumPost.author_id == user_id
            ).scalar() or 0
        except Exception:
            pass

        stats = {
            "topics_count": topics_count,
            "replies_count": replies_count,
            "likes_received": likes_received
        }

        # Get user's existing badges
        existing_badge_ids = set(
            row[0] for row in self.db.query(UserForumBadge.badge_id).filter(
                UserForumBadge.user_id == user_id
            ).all()
        )

        # Check all badges
        badges = self.db.query(ForumBadge).all()
        for badge in badges:
            if badge.id in existing_badge_ids:
                continue

            # Check if user meets requirement
            stat_value = stats.get(badge.requirement_type, 0)
            if stat_value >= badge.requirement_value:
                # Award badge
                user_badge = UserForumBadge(
                    user_id=user_id,
                    badge_id=badge.id
                )
                self.db.add(user_badge)
                awarded.append({
                    "id": badge.id,
                    "name": badge.name,
                    "slug": badge.slug,
                    "description": badge.description,
                    "icon": badge.icon,
                    "color": badge.color
                })
                logger.info(f"User {user_id} awarded badge: {badge.name}")

        if awarded:
            self.db.commit()

        return awarded

    def get_user_badges(self, user_id: int) -> List[Dict]:
        """Get all badges earned by a user"""
        from app.models.database import ForumBadge, UserForumBadge

        badges = self.db.query(
            ForumBadge,
            UserForumBadge.earned_at
        ).join(
            UserForumBadge, UserForumBadge.badge_id == ForumBadge.id
        ).filter(
            UserForumBadge.user_id == user_id
        ).order_by(
            UserForumBadge.earned_at.desc()
        ).all()

        return [
            {
                "id": badge.id,
                "name": badge.name,
                "slug": badge.slug,
                "description": badge.description,
                "icon": badge.icon,
                "color": badge.color,
                "earned_at": earned_at.isoformat() if earned_at else None
            }
            for badge, earned_at in badges
        ]

    def get_all_badges(self) -> List[Dict]:
        """Get all available badges"""
        from app.models.database import ForumBadge

        badges = self.db.query(ForumBadge).order_by(
            ForumBadge.requirement_value
        ).all()

        return [
            {
                "id": badge.id,
                "name": badge.name,
                "slug": badge.slug,
                "description": badge.description,
                "icon": badge.icon,
                "color": badge.color,
                "requirement_type": badge.requirement_type,
                "requirement_value": badge.requirement_value
            }
            for badge in badges
        ]


# ============ CAPTCHA Functions ============

async def generate_captcha() -> Dict:
    """Generate a simple math CAPTCHA for new users"""
    from app.core.redis_manager import redis_manager

    # Generate simple math question
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operator = random.choice(['+', '-'])

    if operator == '+':
        answer = num1 + num2
        question = f"{num1} + {num2} = ?"
    else:
        # Ensure positive result
        if num1 < num2:
            num1, num2 = num2, num1
        answer = num1 - num2
        question = f"{num1} - {num2} = ?"

    # Generate token
    token = secrets.token_urlsafe(32)

    # Store answer in Redis with TTL
    cache_key = f"forum:captcha:{token}"
    try:
        await redis_manager.set(cache_key, str(answer), expire=CAPTCHA_TTL)
    except Exception as e:
        logger.error(f"Failed to store CAPTCHA: {e}")
        raise

    return {
        "question": question,
        "token": token,
        "expires_in": CAPTCHA_TTL
    }


async def verify_captcha(token: str, answer: str) -> bool:
    """Verify CAPTCHA answer"""
    from app.core.redis_manager import redis_manager

    if not token or not answer:
        return False

    cache_key = f"forum:captcha:{token}"
    try:
        stored_answer = await redis_manager.get(cache_key)
        if not stored_answer:
            return False

        # Delete the token after use (one-time use)
        await redis_manager.delete(cache_key)

        return str(stored_answer).strip() == str(answer).strip()
    except Exception as e:
        logger.error(f"CAPTCHA verification error: {e}")
        return False


async def get_user_forum_post_count(user_id: int) -> int:
    """Get user's total forum post count from Redis or calculate"""
    from app.core.redis_manager import redis_manager

    cache_key = f"forum:user_posts:{user_id}"

    try:
        cached = await redis_manager.get(cache_key)
        if cached:
            return int(cached)
    except Exception:
        pass

    # Return 0 if cache miss - will be calculated in endpoint
    return 0


async def update_user_forum_post_count(db: Session, user_id: int) -> int:
    """Update and cache user's forum post count"""
    from app.core.redis_manager import redis_manager
    from app.models.forum import ForumTopic, ForumReply

    topics_count = db.query(func.count(ForumTopic.id)).filter(
        ForumTopic.author_id == user_id,
        ForumTopic.is_active == True
    ).scalar() or 0

    replies_count = db.query(func.count(ForumReply.id)).filter(
        ForumReply.user_id == user_id,
        ForumReply.is_active == True
    ).scalar() or 0

    total = topics_count + replies_count

    # Cache for 1 hour
    cache_key = f"forum:user_posts:{user_id}"
    try:
        await redis_manager.set(cache_key, str(total), expire=3600)
    except Exception:
        pass

    return total


async def user_requires_captcha(db: Session, user_id: int) -> bool:
    """Check if user needs to solve CAPTCHA for posting"""
    post_count = await get_user_forum_post_count(user_id)
    if post_count >= NEW_USER_POST_THRESHOLD:
        return False

    # Cache miss - calculate from database
    post_count = await update_user_forum_post_count(db, user_id)
    return post_count < NEW_USER_POST_THRESHOLD


# ============ Helper to get service instance ============

def get_forum_gamification_service(db: Session) -> ForumGamificationService:
    """Get ForumGamificationService instance"""
    return ForumGamificationService(db)
