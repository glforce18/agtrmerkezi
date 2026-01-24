# ============================================
# AGTR v6.0 - Anti-Farming System
# Dosya: app/core/anti_farming.py
# Prevent reputation farming, spam, and abuse
# ============================================

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ============ Cooldown Settings ============

# Reaction cooldowns (prevent same-user reaction spam)
REACTION_COOLDOWN_SAME_USER = 60  # 1 minute between reactions from same user on same content
REACTION_COOLDOWN_SAME_CONTENT = 5  # 5 seconds between any reactions on same content

# Content creation cooldowns
TOPIC_CREATION_COOLDOWN = 300  # 5 minutes between topics (same user)
REPLY_CREATION_COOLDOWN = 10  # 10 seconds between replies (same user)
LIKE_COOLDOWN = 2  # 2 seconds between likes (prevent spam clicking)

# Quality gate thresholds
MIN_TOPIC_LENGTH = 20  # Minimum characters for topic content
MIN_REPLY_LENGTH = 3  # Minimum characters for reply
MIN_TOPIC_TITLE_LENGTH = 5  # Minimum title length

# Farming detection thresholds
MAX_LIKES_PER_DAY = 100  # Max likes user can give per day
MAX_REPLIES_PER_TOPIC = 10  # Max replies per topic per user
MAX_TOPICS_PER_DAY = 20  # Max topics per day
MAX_REPUTATION_PER_DAY = 500  # Max reputation gain per day

# Duplicate detection
DUPLICATE_CONTENT_WINDOW = 24  # Hours to check for duplicate content
DUPLICATE_SIMILARITY_THRESHOLD = 0.9  # 90% similarity = duplicate


# ============ Cooldown Checks ============


async def check_reaction_cooldown(
    user_id: int, target_user_id: int, content_type: str, content_id: int, db: Session
) -> Tuple[bool, int]:
    """
    Check if user can react to content (cooldown + farming detection)

    Args:
        user_id: User giving reaction
        target_user_id: Content owner
        content_type: "topic" or "reply"
        content_id: Content ID
        db: Database session

    Returns:
        Tuple of (can_react, seconds_until_allowed)
    """
    from app.models.database import ForumReaction

    # Don't allow self-reaction spam
    if user_id == target_user_id:
        # Check last reaction to own content
        last_self_reaction = (
            db.query(ForumReaction)
            .filter(
                ForumReaction.user_id == user_id,
                ForumReaction.content_type == content_type,
            )
            .order_by(ForumReaction.created_at.desc())
            .first()
        )

        if last_self_reaction:
            time_since = (datetime.utcnow() - last_self_reaction.created_at).total_seconds()
            if time_since < REACTION_COOLDOWN_SAME_USER * 2:  # 2x cooldown for self
                return False, int(REACTION_COOLDOWN_SAME_USER * 2 - time_since)

    # Check last reaction from this user to this specific content
    last_reaction = (
        db.query(ForumReaction)
        .filter(
            ForumReaction.user_id == user_id,
            ForumReaction.content_type == content_type,
            ForumReaction.content_id == content_id,
        )
        .order_by(ForumReaction.created_at.desc())
        .first()
    )

    if last_reaction:
        time_since = (datetime.utcnow() - last_reaction.created_at).total_seconds()
        if time_since < REACTION_COOLDOWN_SAME_USER:
            return False, int(REACTION_COOLDOWN_SAME_USER - time_since)

    # Check daily reaction limit
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    reactions_today = (
        db.query(func.count(ForumReaction.id))
        .filter(ForumReaction.user_id == user_id, ForumReaction.created_at >= today_start)
        .scalar()
    )

    if reactions_today >= MAX_LIKES_PER_DAY:
        logger.warning(f"User {user_id} exceeded daily reaction limit ({reactions_today})")
        return False, 86400  # Try again tomorrow

    return True, 0


async def check_topic_creation_cooldown(user_id: int, db: Session) -> Tuple[bool, int]:
    """
    Check if user can create a topic

    Returns:
        Tuple of (can_create, seconds_until_allowed)
    """
    from app.models.forum import ForumTopic

    # Check last topic creation
    last_topic = (
        db.query(ForumTopic)
        .filter(ForumTopic.author_id == user_id)
        .order_by(ForumTopic.created_at.desc())
        .first()
    )

    if last_topic:
        time_since = (datetime.utcnow() - last_topic.created_at).total_seconds()
        if time_since < TOPIC_CREATION_COOLDOWN:
            return False, int(TOPIC_CREATION_COOLDOWN - time_since)

    # Check daily topic limit
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    topics_today = (
        db.query(func.count(ForumTopic.id))
        .filter(ForumTopic.author_id == user_id, ForumTopic.created_at >= today_start)
        .scalar()
    )

    if topics_today >= MAX_TOPICS_PER_DAY:
        logger.warning(f"User {user_id} exceeded daily topic limit ({topics_today})")
        return False, 86400

    return True, 0


async def check_reply_creation_cooldown(
    user_id: int, topic_id: int, db: Session
) -> Tuple[bool, int]:
    """
    Check if user can create a reply

    Returns:
        Tuple of (can_reply, seconds_until_allowed)
    """
    from app.models.forum import ForumReply

    # Check last reply (any topic)
    last_reply = (
        db.query(ForumReply)
        .filter(ForumReply.user_id == user_id)
        .order_by(ForumReply.created_at.desc())
        .first()
    )

    if last_reply:
        time_since = (datetime.utcnow() - last_reply.created_at).total_seconds()
        if time_since < REPLY_CREATION_COOLDOWN:
            return False, int(REPLY_CREATION_COOLDOWN - time_since)

    # Check replies in this specific topic
    replies_in_topic = (
        db.query(func.count(ForumReply.id))
        .filter(ForumReply.user_id == user_id, ForumReply.topic_id == topic_id)
        .scalar()
    )

    if replies_in_topic >= MAX_REPLIES_PER_TOPIC:
        logger.warning(
            f"User {user_id} exceeded reply limit in topic {topic_id} ({replies_in_topic})"
        )
        return False, -1  # No cooldown, just hard limit

    return True, 0


# ============ Quality Gates ============


def check_content_quality(content: str, content_type: str = "reply") -> Tuple[bool, Optional[str]]:
    """
    Check if content meets quality standards

    Args:
        content: Content to check
        content_type: "topic" or "reply"

    Returns:
        Tuple of (passes_quality, failure_reason)
    """
    if not content:
        return False, "Icerik bos olamaz"

    # Length check
    min_length = MIN_TOPIC_LENGTH if content_type == "topic" else MIN_REPLY_LENGTH
    if len(content.strip()) < min_length:
        return False, f"Icerik en az {min_length} karakter olmalidir"

    # Check for spam patterns (all caps, excessive punctuation)
    if content.isupper() and len(content) > 20:
        return False, "Tum buyuk harf kullanmayin"

    # Check for excessive repeated characters
    import re

    if re.search(r"(.)\1{5,}", content):  # Same char repeated 6+ times
        return False, "Asiri tekrar eden karakterler"

    # Check for excessive punctuation
    punctuation_count = sum(1 for c in content if c in "!?.,;:")
    if punctuation_count > len(content) * 0.3:  # More than 30% punctuation
        return False, "Asiri noktalama isareti"

    return True, None


def check_topic_title_quality(title: str) -> Tuple[bool, Optional[str]]:
    """Check topic title quality"""
    if not title:
        return False, "Baslik bos olamaz"

    if len(title.strip()) < MIN_TOPIC_TITLE_LENGTH:
        return False, f"Baslik en az {MIN_TOPIC_TITLE_LENGTH} karakter olmalidir"

    if title.isupper() and len(title) > 10:
        return False, "Baslikta tum buyuk harf kullanmayin"

    # Check if title is just punctuation/numbers
    import re

    if not re.search(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]", title):
        return False, "Baslik anlamli kelimeler icermeli"

    return True, None


# ============ Duplicate Detection ============


def calculate_content_similarity(content1: str, content2: str) -> float:
    """
    Calculate similarity between two content strings

    Returns:
        Similarity score (0.0 to 1.0)
    """
    if not content1 or not content2:
        return 0.0

    # Simple word-based similarity
    from app.core.text_normalization import normalize_text_aggressive

    normalized1 = normalize_text_aggressive(content1)
    normalized2 = normalize_text_aggressive(content2)

    words1 = set(normalized1.split())
    words2 = set(normalized2.split())

    if not words1 or not words2:
        return 0.0

    # Jaccard similarity
    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


async def check_duplicate_content(
    user_id: int, content: str, content_type: str, db: Session
) -> Tuple[bool, Optional[int]]:
    """
    Check if user has posted similar content recently

    Args:
        user_id: User ID
        content: Content to check
        content_type: "topic" or "reply"
        db: Database session

    Returns:
        Tuple of (is_duplicate, duplicate_id)
    """
    # Get recent content from this user
    time_threshold = datetime.utcnow() - timedelta(hours=DUPLICATE_CONTENT_WINDOW)

    if content_type == "topic":
        from app.models.forum import ForumTopic

        recent_content = (
            db.query(ForumTopic.id, ForumTopic.content)
            .filter(ForumTopic.author_id == user_id, ForumTopic.created_at >= time_threshold)
            .limit(20)
            .all()
        )
    else:
        from app.models.forum import ForumReply

        recent_content = (
            db.query(ForumReply.id, ForumReply.content)
            .filter(ForumReply.user_id == user_id, ForumReply.created_at >= time_threshold)
            .limit(20)
            .all()
        )

    # Check similarity
    for content_id, existing_content in recent_content:
        similarity = calculate_content_similarity(content, existing_content)
        if similarity >= DUPLICATE_SIMILARITY_THRESHOLD:
            logger.warning(
                f"Duplicate content detected for user {user_id}: "
                f"similarity={similarity:.2f} with {content_type} {content_id}"
            )
            return True, content_id

    return False, None


# ============ Reputation Farming Detection ============


async def check_reputation_farming(user_id: int, db: Session) -> Tuple[bool, str]:
    """
    Check if user is farming reputation

    Returns:
        Tuple of (is_farming, reason)
    """
    from app.models.database import ForumReputationLog

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Check daily reputation gain
    reputation_today = (
        db.query(func.sum(ForumReputationLog.points))
        .filter(
            ForumReputationLog.user_id == user_id,
            ForumReputationLog.created_at >= today_start,
            ForumReputationLog.points > 0,  # Only positive gains
        )
        .scalar()
        or 0
    )

    if reputation_today >= MAX_REPUTATION_PER_DAY:
        return (
            True,
            f"Gunluk reputation limiti asildi ({reputation_today}/{MAX_REPUTATION_PER_DAY})",
        )

    # Check for suspicious patterns (e.g., all points from same user)
    top_source = (
        db.query(ForumReputationLog.source_user_id, func.count(ForumReputationLog.id))
        .filter(
            ForumReputationLog.user_id == user_id,
            ForumReputationLog.created_at >= today_start,
            ForumReputationLog.source_user_id.isnot(None),
        )
        .group_by(ForumReputationLog.source_user_id)
        .order_by(func.count(ForumReputationLog.id).desc())
        .first()
    )

    if top_source and top_source[1] > 20:  # More than 20 actions from same user
        return True, f"Ayni kullanicidan cok fazla puan ({top_source[1]} islem)"

    return False, ""


# ============ First Topic Bonus Quality Gate ============


def check_first_topic_quality(content: str, title: str) -> bool:
    """
    Check if first topic deserves the bonus reward

    Args:
        content: Topic content
        title: Topic title

    Returns:
        True if quality is sufficient for bonus
    """
    # Title quality
    if len(title.strip()) < 10:
        return False

    # Content quality
    if len(content.strip()) < 50:  # First topic should be substantial
        return False

    # Check it's not spam
    passes_quality, _ = check_content_quality(content, "topic")
    if not passes_quality:
        return False

    return True
