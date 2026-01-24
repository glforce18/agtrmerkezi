# ============================================
# AGTR v6.0 - Forum Advanced Services
# Dosya: app/services/forum_advanced.py
# 20 Yeni Forum Ozelligi - Backend Servisleri
# ============================================

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DraftNotFoundException,
    DraftSaveException,
    InvalidPollOptionsException,
    PollAlreadyExistsException,
    PollExpiredException,
    PollNotFoundException,
)
from app.core.redis_manager import redis_manager

logger = logging.getLogger(__name__)


# ============ 1. Reactions Service ============
class ForumReactionService:
    """Tepki sistemi - Like, Love, Laugh, Thinking, Solution, Played"""

    REACTION_TYPES = ["like", "love", "laugh", "thinking", "solution", "played"]
    REACTION_ICONS = {
        "like": "👍",
        "love": "❤️",
        "laugh": "😄",
        "thinking": "🤔",
        "solution": "✅",
        "played": "🎮",
    }

    def __init__(self, db: Session):
        self.db = db

    def add_reaction(
        self, user_id: int, content_type: str, content_id: int, reaction_type: str
    ) -> Dict:
        """Tepki ekle veya guncelle"""
        from app.models.database import ForumReaction, ReactionType

        if reaction_type not in self.REACTION_TYPES:
            raise ValueError(f"Gecersiz tepki tipi: {reaction_type}")

        if content_type not in ["topic", "reply"]:
            raise ValueError(f"Gecersiz icerik tipi: {content_type}")

        # Mevcut tepki var mi kontrol et
        existing = (
            self.db.query(ForumReaction)
            .filter(
                ForumReaction.user_id == user_id,
                ForumReaction.content_type == content_type,
                ForumReaction.content_id == content_id,
            )
            .first()
        )

        if existing:
            # Ayni tepki ise kaldir
            if existing.reaction_type.value == reaction_type:
                self.db.delete(existing)
                self.db.commit()
                return {"action": "removed", "reaction": reaction_type}
            # Farkli tepki ise guncelle
            existing.reaction_type = ReactionType(reaction_type)
            existing.created_at = datetime.utcnow()
            self.db.commit()
            return {"action": "updated", "reaction": reaction_type}

        # Yeni tepki ekle
        new_reaction = ForumReaction(
            user_id=user_id,
            content_type=content_type,
            content_id=content_id,
            reaction_type=ReactionType(reaction_type),
        )
        self.db.add(new_reaction)
        self.db.commit()

        # Icerik sahibine bildirim gonder
        self._notify_reaction(content_type, content_id, user_id, reaction_type)

        return {"action": "added", "reaction": reaction_type}

    def get_reactions(self, content_type: str, content_id: int) -> Dict:
        """Bir icerigin tum tepkilerini getir"""
        from app.models.database import ForumReaction

        reactions = (
            self.db.query(ForumReaction.reaction_type, func.count(ForumReaction.id).label("count"))
            .filter(
                ForumReaction.content_type == content_type, ForumReaction.content_id == content_id
            )
            .group_by(ForumReaction.reaction_type)
            .all()
        )

        result = {r: 0 for r in self.REACTION_TYPES}
        for r_type, count in reactions:
            result[r_type.value] = count

        return {"reactions": result, "total": sum(result.values()), "icons": self.REACTION_ICONS}

    def get_user_reaction(self, user_id: int, content_type: str, content_id: int) -> Optional[str]:
        """Kullanicinin verdigini tepkiyi getir"""
        from app.models.database import ForumReaction

        reaction = (
            self.db.query(ForumReaction)
            .filter(
                ForumReaction.user_id == user_id,
                ForumReaction.content_type == content_type,
                ForumReaction.content_id == content_id,
            )
            .first()
        )

        return reaction.reaction_type.value if reaction else None

    def get_reaction_users(
        self, content_type: str, content_id: int, reaction_type: str, limit: int = 20
    ) -> List[Dict]:
        """Belirli bir tepkiyi veren kullanicilari getir"""
        from app.models.database import ForumReaction, ReactionType, User

        users = (
            self.db.query(User)
            .join(ForumReaction, ForumReaction.user_id == User.id)
            .filter(
                ForumReaction.content_type == content_type,
                ForumReaction.content_id == content_id,
                ForumReaction.reaction_type == ReactionType(reaction_type),
            )
            .limit(limit)
            .all()
        )

        return [{"id": u.id, "username": u.username, "avatar": u.avatar} for u in users]

    def _notify_reaction(
        self, content_type: str, content_id: int, reactor_id: int, reaction_type: str
    ):
        """Tepki bildirimi gonder"""
        try:
            from app.models.database import Notification, User
            from app.models.forum import ForumReply, ForumTopic

            # Icerik sahibini bul
            if content_type == "topic":
                content = self.db.query(ForumTopic).filter(ForumTopic.id == content_id).first()
                owner_id = content.author_id if content else None
                content_title = content.title[:50] if content else ""
            else:
                content = self.db.query(ForumReply).filter(ForumReply.id == content_id).first()
                owner_id = content.user_id if content else None
                content_title = content.content[:50] if content else ""

            if not owner_id or owner_id == reactor_id:
                return

            reactor = self.db.query(User).filter(User.id == reactor_id).first()

            notification = Notification(
                user_id=owner_id,
                type="reaction",
                title=f"{reactor.username} icerigine tepki verdi",
                message=f"{self.REACTION_ICONS.get(reaction_type, '')} {content_title}...",
                data=json.dumps(
                    {
                        "content_type": content_type,
                        "content_id": content_id,
                        "reaction_type": reaction_type,
                        "reactor_id": reactor_id,
                    }
                ),
            )
            self.db.add(notification)
            self.db.commit()
        except Exception as e:
            logger.error(f"Tepki bildirimi gonderilemedi: {e}")


# ============ 2. Polls Service ============
class ForumPollService:
    """Anket sistemi"""

    def __init__(self, db: Session):
        self.db = db

    def create_poll(
        self,
        topic_id: int,
        question: str,
        options: List[str],
        allow_multiple: bool = False,
        is_anonymous: bool = False,
        ends_at: Optional[datetime] = None,
    ) -> Dict:
        """Yeni anket olustur"""
        from app.models.database import ForumPoll, ForumPollOption

        if len(options) < 2:
            raise InvalidPollOptionsException("En az 2 secenek gerekli")
        if len(options) > 10:
            raise InvalidPollOptionsException("En fazla 10 secenek olabilir")

        # Konu basina tek anket
        existing = self.db.query(ForumPoll).filter(ForumPoll.topic_id == topic_id).first()
        if existing:
            raise PollAlreadyExistsException(topic_id=topic_id)

        poll = ForumPoll(
            topic_id=topic_id,
            question=question,
            allow_multiple=allow_multiple,
            is_anonymous=is_anonymous,
            ends_at=ends_at,
            total_votes=0,
        )
        self.db.add(poll)
        self.db.flush()

        for idx, option_text in enumerate(options):
            option = ForumPollOption(
                poll_id=poll.id, option_text=option_text.strip(), order_index=idx, vote_count=0
            )
            self.db.add(option)

        self.db.commit()

        return self.get_poll(poll.id)

    def vote(self, poll_id: int, user_id: int, option_ids: List[int]) -> Dict:
        """Oy ver"""
        from app.models.database import ForumPoll, ForumPollOption, ForumPollVote

        poll = self.db.query(ForumPoll).filter(ForumPoll.id == poll_id).first()
        if not poll:
            raise PollNotFoundException(poll_id=poll_id)

        if poll.ends_at and poll.ends_at < datetime.utcnow():
            raise PollExpiredException()

        # Coklu secim kontrolu
        if not poll.allow_multiple and len(option_ids) > 1:
            raise InvalidPollOptionsException("Bu ankette sadece 1 secenek secilebilir")

        # Mevcut oylari sil - atomic decrement ile
        existing_votes = (
            self.db.query(ForumPollVote)
            .filter(ForumPollVote.poll_id == poll_id, ForumPollVote.user_id == user_id)
            .all()
        )

        old_option_ids = []
        for v in existing_votes:
            old_option_ids.append(v.option_id)
            self.db.delete(v)

        # Eski oy sayilarini atomik olarak azalt
        if old_option_ids:
            self.db.execute(
                text(
                    "UPDATE forum_poll_options SET vote_count = GREATEST(0, vote_count - 1) "
                    "WHERE id IN :option_ids"
                ),
                {"option_ids": tuple(old_option_ids)},
            )

        # Yeni oylari ekle - atomic increment ile
        valid_option_ids = []
        for option_id in option_ids:
            # Validate option exists
            option_exists = (
                self.db.query(ForumPollOption.id)
                .filter(ForumPollOption.id == option_id, ForumPollOption.poll_id == poll_id)
                .first()
            )
            if not option_exists:
                continue

            vote = ForumPollVote(poll_id=poll_id, option_id=option_id, user_id=user_id)
            self.db.add(vote)
            valid_option_ids.append(option_id)

        # Yeni oy sayilarini atomik olarak artir
        if valid_option_ids:
            self.db.execute(
                text(
                    "UPDATE forum_poll_options SET vote_count = vote_count + 1 WHERE id IN :option_ids"
                ),
                {"option_ids": tuple(valid_option_ids)},
            )

        # Toplam oy sayisini atomik olarak guncelle (recalculate from votes table)
        self.db.execute(
            text(
                "UPDATE forum_polls SET total_votes = "
                "(SELECT COUNT(DISTINCT user_id) FROM forum_poll_votes WHERE poll_id = :poll_id) "
                "WHERE id = :poll_id"
            ),
            {"poll_id": poll_id},
        )

        self.db.commit()

        return self.get_poll(poll_id, user_id)

    def get_poll(self, poll_id: int, user_id: Optional[int] = None) -> Optional[Dict]:
        """Anket detaylarini getir"""
        from app.models.database import ForumPoll, ForumPollOption, ForumPollVote

        poll = self.db.query(ForumPoll).filter(ForumPoll.id == poll_id).first()
        if not poll:
            return None

        options = (
            self.db.query(ForumPollOption)
            .filter(ForumPollOption.poll_id == poll_id)
            .order_by(ForumPollOption.order_index)
            .all()
        )

        # Kullanicinin oylari
        user_votes = []
        if user_id:
            user_votes = [
                v.option_id
                for v in self.db.query(ForumPollVote)
                .filter(ForumPollVote.poll_id == poll_id, ForumPollVote.user_id == user_id)
                .all()
            ]

        is_ended = poll.ends_at and poll.ends_at < datetime.utcnow()

        return {
            "id": poll.id,
            "topic_id": poll.topic_id,
            "question": poll.question,
            "allow_multiple": poll.allow_multiple,
            "is_anonymous": poll.is_anonymous,
            "ends_at": poll.ends_at.isoformat() if poll.ends_at else None,
            "is_ended": is_ended,
            "total_votes": poll.total_votes,
            "options": [
                {
                    "id": o.id,
                    "text": o.option_text,
                    "vote_count": o.vote_count,
                    "percentage": round(
                        (o.vote_count / poll.total_votes * 100) if poll.total_votes > 0 else 0, 1
                    ),
                    "voted": o.id in user_votes,
                }
                for o in options
            ],
            "user_voted": len(user_votes) > 0,
            "user_votes": user_votes,
            "created_at": poll.created_at.isoformat(),
        }

    def get_poll_by_topic(self, topic_id: int, user_id: Optional[int] = None) -> Optional[Dict]:
        """Konuya ait anketi getir"""
        from app.models.database import ForumPoll

        poll = self.db.query(ForumPoll).filter(ForumPoll.topic_id == topic_id).first()
        if not poll:
            return None

        return self.get_poll(poll.id, user_id)


# ============ 3. Templates Service ============
class ForumTemplateService:
    """Konu sablonlari"""

    def __init__(self, db: Session):
        self.db = db

    def get_templates(self, category_id: Optional[int] = None) -> List[Dict]:
        """Sablonlari listele"""
        from app.models.database import ForumTopicTemplate

        query = self.db.query(ForumTopicTemplate).filter(ForumTopicTemplate.is_active == True)

        if category_id:
            query = query.filter(
                or_(
                    ForumTopicTemplate.category_id == category_id,
                    ForumTopicTemplate.category_id == None,
                )
            )

        templates = query.order_by(ForumTopicTemplate.name).all()

        def parse_required_fields(rf):
            if not rf:
                return []
            if isinstance(rf, list):
                return rf
            if isinstance(rf, str):
                try:
                    return json.loads(rf)
                except Exception:
                    return []
            return []

        return [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "title_template": t.title_template,
                "content_template": t.content_template,
                "required_fields": parse_required_fields(t.required_fields),
                "category_id": getattr(t, "category_id", None),
            }
            for t in templates
        ]

    def create_template(
        self,
        name: str,
        title_template: str,
        content_template: str,
        description: Optional[str] = None,
        required_fields: Optional[List[str]] = None,
        category_id: Optional[int] = None,
        created_by: Optional[int] = None,
    ) -> Dict:
        """Yeni sablon olustur (admin only)"""
        from app.models.database import ForumTopicTemplate

        template = ForumTopicTemplate(
            name=name,
            description=description,
            title_template=title_template,
            content_template=content_template,
            required_fields=json.dumps(required_fields or []),
            category_id=category_id,
            created_by=created_by,
            is_active=True,
        )
        self.db.add(template)
        self.db.commit()

        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "title_template": template.title_template,
            "content_template": template.content_template,
            "required_fields": required_fields or [],
        }

    def delete_template(self, template_id: int) -> bool:
        """Sablon sil (admin only)"""
        from app.models.database import ForumTopicTemplate

        template = (
            self.db.query(ForumTopicTemplate).filter(ForumTopicTemplate.id == template_id).first()
        )
        if template:
            template.is_active = False
            self.db.commit()
            return True
        return False


# ============ 4. Drafts Service ============
class ForumDraftService:
    """Taslak otomatik kaydetme"""

    DRAFT_TTL = 7 * 24 * 60 * 60  # 7 gun

    def __init__(self, db: Session):
        self.db = db

    async def save_draft(
        self,
        user_id: int,
        draft_type: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category_id: Optional[int] = None,
        topic_id: Optional[int] = None,
        poll_data: Optional[Dict] = None,
        device_id: Optional[str] = None,
    ) -> Dict:
        """Taslak kaydet (Redis + DB hibrit)"""
        from app.models.database import ForumDraft

        # Mevcut taslak var mi?
        existing = (
            self.db.query(ForumDraft)
            .filter(
                ForumDraft.user_id == user_id,
                ForumDraft.draft_type == draft_type,
                ForumDraft.topic_id == topic_id if topic_id else ForumDraft.topic_id == None,
            )
            .first()
        )

        poll_json = json.dumps(poll_data) if poll_data else None

        if existing:
            existing.title = title
            existing.content = content
            existing.category_id = category_id
            existing.poll_data = poll_json
            existing.device_id = device_id
            existing.updated_at = datetime.utcnow()
        else:
            existing = ForumDraft(
                user_id=user_id,
                draft_type=draft_type,
                title=title,
                content=content,
                category_id=category_id,
                topic_id=topic_id,
                poll_data=poll_json,
                device_id=device_id,
            )
            self.db.add(existing)

        self.db.commit()

        # Redis'e de kaydet (hizli erisim icin)
        cache_key = f"forum:draft:{user_id}:{draft_type}:{topic_id or 0}"
        try:
            await redis_manager.set(
                cache_key,
                json.dumps(
                    {
                        "id": existing.id,
                        "title": title,
                        "content": content,
                        "category_id": category_id,
                        "poll_data": poll_data,
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                ),
                expire=self.DRAFT_TTL,
            )
        except Exception as e:
            logger.warning(f"Redis draft save failed: {e}")

        return {"id": existing.id, "saved": True, "updated_at": existing.updated_at.isoformat()}

    async def get_draft(
        self, user_id: int, draft_type: str, topic_id: Optional[int] = None
    ) -> Optional[Dict]:
        """Taslak getir"""
        from app.models.database import ForumDraft

        # Once Redis'ten dene
        cache_key = f"forum:draft:{user_id}:{draft_type}:{topic_id or 0}"
        try:
            cached = await redis_manager.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

        # DB'den getir
        draft = (
            self.db.query(ForumDraft)
            .filter(
                ForumDraft.user_id == user_id,
                ForumDraft.draft_type == draft_type,
                ForumDraft.topic_id == topic_id if topic_id else ForumDraft.topic_id == None,
            )
            .first()
        )

        if not draft:
            return None

        return {
            "id": draft.id,
            "title": draft.title,
            "content": draft.content,
            "category_id": draft.category_id,
            "topic_id": draft.topic_id,
            "poll_data": json.loads(draft.poll_data) if draft.poll_data else None,
            "updated_at": draft.updated_at.isoformat(),
        }

    async def delete_draft(
        self, user_id: int, draft_type: str, topic_id: Optional[int] = None
    ) -> bool:
        """Taslak sil"""
        from app.models.database import ForumDraft

        draft = (
            self.db.query(ForumDraft)
            .filter(
                ForumDraft.user_id == user_id,
                ForumDraft.draft_type == draft_type,
                ForumDraft.topic_id == topic_id if topic_id else ForumDraft.topic_id == None,
            )
            .first()
        )

        if draft:
            self.db.delete(draft)
            self.db.commit()

        # Redis'ten de sil
        cache_key = f"forum:draft:{user_id}:{draft_type}:{topic_id or 0}"
        try:
            await redis_manager.delete(cache_key)
        except Exception:
            pass

        return True

    def get_all_drafts(self, user_id: int) -> List[Dict]:
        """Kullanicinin tum taslaklarini getir"""
        from app.models.database import ForumDraft

        drafts = (
            self.db.query(ForumDraft)
            .filter(ForumDraft.user_id == user_id)
            .order_by(ForumDraft.updated_at.desc())
            .all()
        )

        return [
            {
                "id": d.id,
                "draft_type": d.draft_type,
                "title": d.title,
                "content": (
                    d.content[:100] + "..." if d.content and len(d.content) > 100 else d.content
                ),
                "category_id": d.category_id,
                "topic_id": d.topic_id,
                "updated_at": d.updated_at.isoformat(),
            }
            for d in drafts
        ]


# ============ 5. Spam Filter Service ============
class ForumSpamFilterService:
    """Spam filtreleme ve moderasyon"""

    def __init__(self, db: Session):
        self.db = db
        self._rules_cache = None
        self._cache_time = None

    def _load_rules(self) -> List[Dict]:
        """Kurallari yukle ve cache'le"""
        from app.models.database import SpamFilterRule

        # 5 dakika cache
        if (
            self._rules_cache
            and self._cache_time
            and (datetime.utcnow() - self._cache_time).seconds < 300
        ):
            return self._rules_cache

        rules = self.db.query(SpamFilterRule).filter(SpamFilterRule.is_active == True).all()

        self._rules_cache = [
            {
                "id": r.id,
                "rule_type": r.rule_type,
                "pattern": r.pattern,
                "action": r.action,
                "severity": r.severity,
            }
            for r in rules
        ]
        self._cache_time = datetime.utcnow()

        return self._rules_cache

    def check_content(self, content: str, user_id: int) -> Dict:
        """Icerigi spam/zararlı icerik icin kontrol et"""
        from app.models.database import SpamLog

        rules = self._load_rules()
        violations = []
        total_severity = 0

        content_lower = content.lower()

        for rule in rules:
            matched = False

            if rule["rule_type"] == "keyword":
                # Basit kelime eslesmesi
                if rule["pattern"].lower() in content_lower:
                    matched = True

            elif rule["rule_type"] == "regex":
                # Regex eslesmesi
                try:
                    if re.search(rule["pattern"], content, re.IGNORECASE):
                        matched = True
                except re.error:
                    pass

            elif rule["rule_type"] == "link_pattern":
                # Link kontrolu
                links = re.findall(r"https?://[^\s]+", content)
                for link in links:
                    if rule["pattern"].lower() in link.lower():
                        matched = True
                        break

            if matched:
                violations.append(
                    {
                        "rule_id": rule["id"],
                        "rule_type": rule["rule_type"],
                        "action": rule["action"],
                        "severity": rule["severity"],
                    }
                )
                total_severity += rule["severity"]

        # Sonucu logla
        if violations:
            log = SpamLog(
                user_id=user_id,
                content_preview=content[:200],
                matched_rules=json.dumps([v["rule_id"] for v in violations]),
                action_taken=violations[0]["action"] if violations else "none",
                severity_score=total_severity,
            )
            self.db.add(log)
            self.db.commit()

        # Karar ver
        should_block = any(v["action"] == "block" for v in violations)
        should_review = any(v["action"] == "review" for v in violations) and not should_block

        return {
            "passed": not should_block,
            "needs_review": should_review,
            "violations": len(violations),
            "severity_score": total_severity,
            "message": "Icerik spam olarak engellendi" if should_block else None,
        }

    def add_rule(
        self,
        rule_type: str,
        pattern: str,
        action: str = "review",
        severity: int = 1,
        created_by: Optional[int] = None,
    ) -> Dict:
        """Yeni kural ekle (admin only)"""
        from app.models.database import SpamFilterRule

        rule = SpamFilterRule(
            rule_type=rule_type,
            pattern=pattern,
            action=action,
            severity=severity,
            created_by=created_by,
            is_active=True,
        )
        self.db.add(rule)
        self.db.commit()

        # Cache'i temizle
        self._rules_cache = None

        return {"id": rule.id, "rule_type": rule_type, "pattern": pattern, "action": action}

    def get_rules(self) -> List[Dict]:
        """Tum kurallari getir (admin only)"""
        return self._load_rules()

    def delete_rule(self, rule_id: int) -> bool:
        """Kural sil (admin only)"""
        from app.models.database import SpamFilterRule

        rule = self.db.query(SpamFilterRule).filter(SpamFilterRule.id == rule_id).first()
        if rule:
            rule.is_active = False
            self.db.commit()
            self._rules_cache = None
            return True
        return False


# ============ 6. Advanced Search Service ============
class ForumSearchService:
    """Gelismis arama"""

    def __init__(self, db: Session):
        self.db = db

    async def search(
        self, query: str, filters: Optional[Dict] = None, page: int = 1, limit: int = 20
    ) -> Dict:
        """Gelismis arama yap"""
        from app.models.database import ForumTag, ForumTopicTag, User
        from app.models.forum import ForumTopic

        filters = filters or {}
        offset = (page - 1) * limit

        # Temel sorgu
        base_query = self.db.query(ForumTopic).filter(ForumTopic.is_active == True)

        # Arama metni
        if query:
            search_pattern = f"%{query}%"
            base_query = base_query.filter(
                or_(
                    ForumTopic.title.ilike(search_pattern), ForumTopic.content.ilike(search_pattern)
                )
            )

        # Kategori filtresi
        if filters.get("category_id"):
            base_query = base_query.filter(ForumTopic.category_id == filters["category_id"])

        # Yazar filtresi
        if filters.get("author_id"):
            base_query = base_query.filter(ForumTopic.author_id == filters["author_id"])

        # Tarih filtresi
        if filters.get("date_from"):
            base_query = base_query.filter(ForumTopic.created_at >= filters["date_from"])
        if filters.get("date_to"):
            base_query = base_query.filter(ForumTopic.created_at <= filters["date_to"])

        # Tag filtresi
        if filters.get("tags"):
            tag_names = filters["tags"]
            tag_ids = self.db.query(ForumTag.id).filter(ForumTag.name.in_(tag_names)).all()
            tag_ids = [t[0] for t in tag_ids]
            if tag_ids:
                topic_ids = (
                    self.db.query(ForumTopicTag.topic_id)
                    .filter(ForumTopicTag.tag_id.in_(tag_ids))
                    .distinct()
                    .all()
                )
                topic_ids = [t[0] for t in topic_ids]
                base_query = base_query.filter(ForumTopic.id.in_(topic_ids))

        # Cozulmus filtresi
        if filters.get("is_solved") is not None:
            base_query = base_query.filter(ForumTopic.is_solved == filters["is_solved"])

        # Siralama
        sort = filters.get("sort", "relevance")
        if sort == "newest":
            base_query = base_query.order_by(ForumTopic.created_at.desc())
        elif sort == "oldest":
            base_query = base_query.order_by(ForumTopic.created_at.asc())
        elif sort == "most_replies":
            base_query = base_query.order_by(ForumTopic.reply_count.desc())
        elif sort == "most_views":
            base_query = base_query.order_by(ForumTopic.view_count.desc())
        else:  # relevance - yeniler ve populerler one
            base_query = base_query.order_by(
                (ForumTopic.view_count + ForumTopic.reply_count * 10).desc(),
                ForumTopic.created_at.desc(),
            )

        # Toplam
        total = base_query.count()

        # Sonuclar
        topics = base_query.offset(offset).limit(limit).all()

        results = []
        for topic in topics:
            author = self.db.query(User).filter(User.id == topic.author_id).first()
            results.append(
                {
                    "id": topic.id,
                    "title": topic.title,
                    "content_preview": (
                        topic.content[:200] + "..." if len(topic.content) > 200 else topic.content
                    ),
                    "author": {
                        "id": author.id if author else None,
                        "username": author.username if author else "Anonim",
                    },
                    "category_id": topic.category_id,
                    "reply_count": topic.reply_count,
                    "view_count": topic.view_count,
                    "is_solved": topic.is_solved,
                    "created_at": topic.created_at.isoformat(),
                }
            )

        return {
            "results": results,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    def get_similar_topics(self, title: str, content: str, limit: int = 5) -> List[Dict]:
        """Benzer konulari bul (konu olusturma sirasinda)"""
        from app.models.database import User
        from app.models.forum import ForumTopic

        # Basit kelime tabanli benzerlik
        words = set(re.findall(r"\w+", (title + " " + content).lower()))
        words = {w for w in words if len(w) > 3}  # Kisa kelimeleri at

        if not words:
            return []

        # Her kelime icin arama yap
        search_pattern = "|".join(words)

        topics = (
            self.db.query(ForumTopic)
            .filter(
                ForumTopic.is_active == True,
                or_(
                    ForumTopic.title.op("REGEXP")(search_pattern),
                    ForumTopic.content.op("REGEXP")(search_pattern),
                ),
            )
            .order_by(ForumTopic.view_count.desc())
            .limit(limit * 2)
            .all()
        )

        # Benzerlik skoru hesapla
        scored = []
        for topic in topics:
            topic_words = set(re.findall(r"\w+", (topic.title + " " + topic.content).lower()))
            common = len(words & topic_words)
            if common > 0:
                scored.append((topic, common))

        # Skora gore sirala
        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for topic, score in scored[:limit]:
            author = self.db.query(User).filter(User.id == topic.author_id).first()
            results.append(
                {
                    "id": topic.id,
                    "title": topic.title,
                    "reply_count": topic.reply_count,
                    "is_solved": topic.is_solved,
                    "similarity_score": score,
                    "author_username": author.username if author else "Anonim",
                }
            )

        return results


# ============ 7. Reputation Service (Enhanced) ============
class ForumReputationService:
    """Gelismis itibar sistemi"""

    LEVEL_THRESHOLDS = [
        (0, "Yeni Uye"),
        (50, "Aktif Uye"),
        (200, "Degerli Uye"),
        (500, "Uzman"),
        (1000, "Master"),
        (2500, "Efsane"),
        (5000, "Guru"),
        (10000, "Legend"),
    ]

    def __init__(self, db: Session):
        self.db = db

    def get_reputation_details(self, user_id: int) -> Dict:
        """Kullanici itibar detaylarini getir"""
        from app.models.database import ForumReputation

        rep = self.db.query(ForumReputation).filter(ForumReputation.user_id == user_id).first()

        if not rep:
            # Yeni kayit olustur
            rep = ForumReputation(
                user_id=user_id,
                total_points=0,
                level=1,
                topics_created=0,
                replies_given=0,
                likes_received=0,
                likes_given=0,
                solutions_marked=0,
            )
            self.db.add(rep)
            self.db.commit()

        points = getattr(rep, "total_points", 0) or 0

        # Level hesapla
        level_name = "Yeni Uye"
        next_threshold = 50
        for threshold, name in self.LEVEL_THRESHOLDS:
            if points >= threshold:
                level_name = name
            else:
                next_threshold = threshold
                break

        progress = (points / next_threshold * 100) if next_threshold > 0 else 100

        return {
            "user_id": user_id,
            "points": points,
            "level": getattr(rep, "level", 1) or 1,
            "level_name": level_name,
            "next_level_at": next_threshold,
            "progress_percent": min(100, round(progress, 1)),
            "stats": {
                "topics_count": getattr(rep, "topics_created", 0) or 0,
                "replies_count": getattr(rep, "replies_given", 0) or 0,
                "likes_received": getattr(rep, "likes_received", 0) or 0,
                "likes_given": getattr(rep, "likes_given", 0) or 0,
                "best_answers": getattr(rep, "solutions_marked", 0) or 0,
            },
            "weekly_activity": getattr(rep, "helpful_count", 0) or 0,
        }

    def add_points(self, user_id: int, points: int, reason: str) -> int:
        """Puan ekle ve logla"""
        from app.models.database import ForumReputation, ForumReputationLog

        rep = self.db.query(ForumReputation).filter(ForumReputation.user_id == user_id).first()

        if not rep:
            rep = ForumReputation(user_id=user_id, total_points=0, level=1)
            self.db.add(rep)

        old_points = getattr(rep, "total_points", 0) or 0
        rep.total_points = max(0, old_points + points)

        # Level guncelle
        new_level = 1
        for idx, (threshold, name) in enumerate(self.LEVEL_THRESHOLDS):
            if rep.total_points >= threshold:
                new_level = idx + 1
        rep.level = new_level

        # Log kaydet
        try:
            log = ForumReputationLog(
                user_id=user_id, points_change=points, reason=reason, new_total=rep.total_points
            )
            self.db.add(log)
        except Exception:
            pass

        self.db.commit()

        return rep.total_points

    def update_stat(self, user_id: int, stat_name: str, increment: int = 1):
        """Istatistik guncelle"""
        from app.models.database import ForumReputation

        rep = self.db.query(ForumReputation).filter(ForumReputation.user_id == user_id).first()

        if not rep:
            rep = ForumReputation(user_id=user_id, total_points=0, level=1)
            self.db.add(rep)

        if hasattr(rep, stat_name):
            current = getattr(rep, stat_name) or 0
            setattr(rep, stat_name, current + increment)

        self.db.commit()

    def get_leaderboard(self, timeframe: str = "all", limit: int = 10) -> List[Dict]:
        """Liderlik tablosu"""
        from app.models.database import ForumReputation, User

        query = self.db.query(ForumReputation, User).join(User, User.id == ForumReputation.user_id)

        if timeframe == "weekly":
            query = query.order_by(ForumReputation.helpful_count.desc())
        else:
            query = query.order_by(ForumReputation.total_points.desc())

        results = query.limit(limit).all()

        return [
            {
                "rank": idx + 1,
                "user_id": rep.user_id,
                "username": user.username,
                "avatar": user.avatar,
                "points": getattr(rep, "total_points", 0) or 0,
                "level": getattr(rep, "level", 1) or 1,
                "level_name": self._get_level_name(getattr(rep, "total_points", 0) or 0),
            }
            for idx, (rep, user) in enumerate(results)
        ]

    def _get_level_name(self, points: int) -> str:
        """Puandan level ismi getir"""
        if not points:
            points = 0
        level_name = "Yeni Uye"
        for threshold, name in self.LEVEL_THRESHOLDS:
            if points >= threshold:
                level_name = name
            else:
                break
        return level_name


# ============ 8. Bookmark Service ============
class ForumBookmarkService:
    """Yer imi sistemi"""

    def __init__(self, db: Session):
        self.db = db

    def toggle_bookmark(self, user_id: int, topic_id: int) -> Dict:
        """Yer imi ekle/kaldir (race-condition safe)"""
        from sqlalchemy.exc import IntegrityError

        from app.models.database import ForumBookmark

        # Try to delete first - if exists, it will be removed
        deleted = (
            self.db.query(ForumBookmark)
            .filter(ForumBookmark.user_id == user_id, ForumBookmark.topic_id == topic_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()

        if deleted > 0:
            return {"bookmarked": False}

        # If not deleted, try to insert - handle race condition with unique constraint
        try:
            bookmark = ForumBookmark(user_id=user_id, topic_id=topic_id)
            self.db.add(bookmark)
            self.db.commit()
            return {"bookmarked": True}
        except IntegrityError:
            # Race condition: another request already inserted
            self.db.rollback()
            # Double check current state
            existing = (
                self.db.query(ForumBookmark)
                .filter(ForumBookmark.user_id == user_id, ForumBookmark.topic_id == topic_id)
                .first()
            )
            return {"bookmarked": existing is not None}

    def get_bookmarks(self, user_id: int, page: int = 1, limit: int = 20) -> Dict:
        """Kullanicinin yer imlerini getir"""
        from app.models.database import ForumBookmark
        from app.models.forum import ForumTopic

        offset = (page - 1) * limit

        query = (
            self.db.query(ForumBookmark, ForumTopic)
            .join(ForumTopic, ForumTopic.id == ForumBookmark.topic_id)
            .filter(ForumBookmark.user_id == user_id, ForumTopic.is_active == True)
            .order_by(ForumBookmark.created_at.desc())
        )

        total = query.count()
        results = query.offset(offset).limit(limit).all()

        bookmarks = []
        for bm, topic in results:
            bookmarks.append(
                {
                    "id": bm.id,
                    "topic_id": topic.id,
                    "topic_title": topic.title,
                    "reply_count": topic.reply_count,
                    "last_activity": topic.updated_at.isoformat() if topic.updated_at else None,
                    "bookmarked_at": bm.created_at.isoformat(),
                }
            )

        return {
            "bookmarks": bookmarks,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit,
        }

    def is_bookmarked(self, user_id: int, topic_id: int) -> bool:
        """Konu yer imlerinde mi?"""
        from app.models.database import ForumBookmark

        return (
            self.db.query(ForumBookmark)
            .filter(ForumBookmark.user_id == user_id, ForumBookmark.topic_id == topic_id)
            .first()
            is not None
        )


# ============ Helper Functions ============


def get_reaction_service(db: Session) -> ForumReactionService:
    return ForumReactionService(db)


def get_poll_service(db: Session) -> ForumPollService:
    return ForumPollService(db)


def get_template_service(db: Session) -> ForumTemplateService:
    return ForumTemplateService(db)


def get_draft_service(db: Session) -> ForumDraftService:
    return ForumDraftService(db)


def get_spam_filter_service(db: Session) -> ForumSpamFilterService:
    return ForumSpamFilterService(db)


def get_search_service(db: Session) -> ForumSearchService:
    return ForumSearchService(db)


def get_reputation_service(db: Session) -> ForumReputationService:
    return ForumReputationService(db)


def get_bookmark_service(db: Session) -> ForumBookmarkService:
    return ForumBookmarkService(db)
