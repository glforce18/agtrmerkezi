# ============================================
# AGTR v6.0 - Content Filter & Auto-Moderation
# Dosya: app/core/content_filter.py
# Forum icerik moderasyonu, kara liste ve spam tespiti
# ============================================

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ==================== DEFAULT CONFIGURATION ====================

# Varsayilan yasakli kelimeler (admin panelden yapilandirilabilir)
# Bu liste sadece baslangic icin, gercek liste veritabanindan yuklenir
DEFAULT_BLACKLIST_WORDS: List[str] = [
    # Placeholder - Admin panelden yapilandirilacak
]

# Spam desenleri
SPAM_PATTERNS = [
    (r'(https?://\S+){3,}', 'Cok fazla URL'),  # 3+ URLs
    (r'(.)\1{5,}', 'Tekrarlanan karakterler'),  # Repeated characters (aaaaaa)
    (r'[A-Z]{10,}', 'Tum harfler buyuk'),  # ALL CAPS (10+ chars)
    (r'(.{3,})\1{3,}', 'Tekrarlanan metin'),  # Repeated text patterns
]

# Yavaslatma (rate limit) ayarlari
RATE_LIMIT_TOPICS_PER_HOUR = 5
RATE_LIMIT_REPLIES_PER_MINUTE = 3

# Uyari sistemi ayarlari
MAX_WARNINGS_BEFORE_BAN = 3
WARNING_EXPIRY_DAYS = 30
DEFAULT_BAN_DURATION_HOURS = 24


# ==================== CONTENT FILTER CLASS ====================

class ContentFilter:
    """Forum icerik filtreleme ve moderasyon sistemi"""

    def __init__(self, db: Session = None):
        self.db = db
        self._blacklist_cache: List[str] = []
        self._blacklist_loaded = False
        self._cache_expires_at: Optional[datetime] = None
        self._cache_ttl = 300  # 5 dakika

    def _load_blacklist_from_db(self) -> List[str]:
        """Kara listeyi veritabanindan yukle"""
        if not self.db:
            return DEFAULT_BLACKLIST_WORDS

        try:
            from app.models.database import ContentBlacklist

            words = self.db.query(ContentBlacklist.word).filter(
                ContentBlacklist.is_active == True
            ).all()

            return [w[0].lower() for w in words]
        except Exception as e:
            logger.error(f"Kara liste yukleme hatasi: {e}")
            return DEFAULT_BLACKLIST_WORDS

    def get_blacklist(self) -> List[str]:
        """Cache'li kara liste getir"""
        now = datetime.utcnow()

        if (not self._blacklist_loaded or
            self._cache_expires_at is None or
            now > self._cache_expires_at):
            self._blacklist_cache = self._load_blacklist_from_db()
            self._blacklist_loaded = True
            self._cache_expires_at = now + timedelta(seconds=self._cache_ttl)

        return self._blacklist_cache

    def invalidate_cache(self):
        """Cache'i temizle (kara liste guncellendiginde cagrilir)"""
        self._blacklist_loaded = False
        self._cache_expires_at = None

    def check_content(self, content: str) -> Tuple[bool, List[str]]:
        """
        Icerigi ihlaller icin kontrol et.
        Returns: (is_clean, list_of_violations)
        """
        violations = []
        content_lower = content.lower()

        # Kara liste kontrolu
        blacklist = self.get_blacklist()
        for word in blacklist:
            if word in content_lower:
                # Kelimeyi kismi goster (gizlilik icin)
                masked = word[:2] + '*' * (len(word) - 2) if len(word) > 2 else '***'
                violations.append(f"Yasakli kelime: {masked}")

        # Spam desenleri kontrolu
        for pattern, description in SPAM_PATTERNS:
            if re.search(pattern, content):
                violations.append(f"Spam tespit edildi: {description}")

        return len(violations) == 0, violations

    def filter_content(self, content: str) -> str:
        """Yasakli kelimeleri yildizla degistir"""
        blacklist = self.get_blacklist()
        filtered = content

        for word in blacklist:
            # Case-insensitive degistirme
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            filtered = pattern.sub('*' * len(word), filtered)

        return filtered

    def check_rate_limit(self, user_id: int, action: str = "topic") -> Tuple[bool, str]:
        """
        Rate limit kontrolu.
        Returns: (is_allowed, message)
        """
        if not self.db:
            return True, ""

        try:
            from app.models.database import ForumTopic, ForumReply

            now = datetime.utcnow()

            if action == "topic":
                # Son 1 saatte acilan konu sayisi
                one_hour_ago = now - timedelta(hours=1)
                count = self.db.query(ForumTopic).filter(
                    ForumTopic.author_id == user_id,
                    ForumTopic.created_at >= one_hour_ago
                ).count()

                if count >= RATE_LIMIT_TOPICS_PER_HOUR:
                    return False, f"Saatte en fazla {RATE_LIMIT_TOPICS_PER_HOUR} konu acabilirsiniz"

            elif action == "reply":
                # Son 1 dakikada yazilan yanit sayisi
                one_min_ago = now - timedelta(minutes=1)
                count = self.db.query(ForumReply).filter(
                    ForumReply.user_id == user_id,
                    ForumReply.created_at >= one_min_ago
                ).count()

                if count >= RATE_LIMIT_REPLIES_PER_MINUTE:
                    return False, f"Dakikada en fazla {RATE_LIMIT_REPLIES_PER_MINUTE} yanit yazabilirsiniz"

            return True, ""
        except Exception as e:
            logger.error(f"Rate limit kontrol hatasi: {e}")
            return True, ""  # Hata durumunda izin ver


# ==================== WARNING SYSTEM ====================

class WarningSystem:
    """Kullanici uyari ve ceza sistemi"""

    def __init__(self, db: Session):
        self.db = db

    def add_warning(
        self,
        user_id: int,
        reason: str,
        warned_by: Optional[int] = None,
        auto_ban: bool = True
    ) -> Dict:
        """
        Kullaniciya uyari ekle.
        Maksimum uyari sayisina ulasilirsa otomatik ban uygular.
        """
        try:
            from app.models.database import UserWarning, ForumBan

            now = datetime.utcnow()
            expires_at = now + timedelta(days=WARNING_EXPIRY_DAYS)

            # Uyari olustur
            warning = UserWarning(
                user_id=user_id,
                reason=reason,
                warned_by=warned_by,
                expires_at=expires_at
            )
            self.db.add(warning)
            self.db.commit()

            # Aktif uyari sayisini kontrol et
            active_warnings = self.get_active_warning_count(user_id)

            result = {
                "warning_id": warning.id,
                "active_warnings": active_warnings,
                "max_warnings": MAX_WARNINGS_BEFORE_BAN,
                "banned": False
            }

            # Otomatik ban kontrolu
            if auto_ban and active_warnings >= MAX_WARNINGS_BEFORE_BAN:
                ban_result = self.ban_user(
                    user_id=user_id,
                    reason=f"Otomatik ban: {MAX_WARNINGS_BEFORE_BAN} uyari limiti asildi",
                    banned_by=warned_by,
                    duration_hours=DEFAULT_BAN_DURATION_HOURS
                )
                result["banned"] = True
                result["ban_expires_at"] = ban_result.get("expires_at")

            return result

        except Exception as e:
            logger.error(f"Uyari ekleme hatasi: {e}")
            self.db.rollback()
            raise

    def get_active_warning_count(self, user_id: int) -> int:
        """Aktif (suresi dolmamis) uyari sayisini getir"""
        try:
            from app.models.database import UserWarning

            now = datetime.utcnow()
            count = self.db.query(UserWarning).filter(
                UserWarning.user_id == user_id,
                UserWarning.expires_at > now
            ).count()

            return count
        except Exception as e:
            logger.error(f"Uyari sayisi getirme hatasi: {e}")
            return 0

    def get_user_warnings(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """Kullanici uyarilarini getir"""
        try:
            from app.models.database import UserWarning, User

            query = self.db.query(UserWarning).filter(
                UserWarning.user_id == user_id
            )

            if active_only:
                query = query.filter(UserWarning.expires_at > datetime.utcnow())

            warnings = query.order_by(UserWarning.created_at.desc()).all()

            result = []
            for w in warnings:
                warned_by_user = None
                if w.warned_by:
                    warned_by_user = self.db.query(User).filter(User.id == w.warned_by).first()

                result.append({
                    "id": w.id,
                    "reason": w.reason,
                    "warned_by": warned_by_user.username if warned_by_user else "Sistem",
                    "expires_at": w.expires_at.isoformat() if w.expires_at else None,
                    "created_at": w.created_at.isoformat() if w.created_at else None,
                    "is_active": w.expires_at > datetime.utcnow() if w.expires_at else False
                })

            return result
        except Exception as e:
            logger.error(f"Uyari listesi getirme hatasi: {e}")
            return []

    def remove_warning(self, warning_id: int) -> bool:
        """Uyariyi kaldir"""
        try:
            from app.models.database import UserWarning

            warning = self.db.query(UserWarning).filter(
                UserWarning.id == warning_id
            ).first()

            if warning:
                self.db.delete(warning)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Uyari kaldirma hatasi: {e}")
            self.db.rollback()
            return False

    def ban_user(
        self,
        user_id: int,
        reason: str,
        banned_by: Optional[int] = None,
        duration_hours: int = DEFAULT_BAN_DURATION_HOURS
    ) -> Dict:
        """Kullaniciyi forumdan banla"""
        try:
            from app.models.database import ForumBan

            now = datetime.utcnow()
            expires_at = now + timedelta(hours=duration_hours)

            # Mevcut aktif ban var mi kontrol et
            existing_ban = self.db.query(ForumBan).filter(
                ForumBan.user_id == user_id,
                ForumBan.expires_at > now
            ).first()

            if existing_ban:
                # Mevcut ban'i guncelle (sureyi uzat)
                if expires_at > existing_ban.expires_at:
                    existing_ban.expires_at = expires_at
                    existing_ban.reason = reason
                    existing_ban.banned_by = banned_by
                    self.db.commit()

                return {
                    "ban_id": existing_ban.id,
                    "expires_at": existing_ban.expires_at.isoformat(),
                    "extended": True
                }

            # Yeni ban olustur
            ban = ForumBan(
                user_id=user_id,
                reason=reason,
                banned_by=banned_by,
                expires_at=expires_at
            )
            self.db.add(ban)
            self.db.commit()

            return {
                "ban_id": ban.id,
                "expires_at": expires_at.isoformat(),
                "extended": False
            }
        except Exception as e:
            logger.error(f"Ban ekleme hatasi: {e}")
            self.db.rollback()
            raise

    def unban_user(self, user_id: int) -> bool:
        """Kullanicinin banini kaldir"""
        try:
            from app.models.database import ForumBan

            # Tum aktif banlari kaldir
            deleted = self.db.query(ForumBan).filter(
                ForumBan.user_id == user_id,
                ForumBan.expires_at > datetime.utcnow()
            ).delete()

            self.db.commit()
            return deleted > 0
        except Exception as e:
            logger.error(f"Ban kaldirma hatasi: {e}")
            self.db.rollback()
            return False

    def check_ban_status(self, user_id: int) -> Tuple[bool, Optional[Dict]]:
        """
        Kullanicinin ban durumunu kontrol et.
        Returns: (is_banned, ban_info)
        """
        try:
            from app.models.database import ForumBan

            now = datetime.utcnow()
            ban = self.db.query(ForumBan).filter(
                ForumBan.user_id == user_id,
                ForumBan.expires_at > now
            ).first()

            if ban:
                return True, {
                    "ban_id": ban.id,
                    "reason": ban.reason,
                    "expires_at": ban.expires_at.isoformat(),
                    "remaining_hours": (ban.expires_at - now).total_seconds() / 3600
                }

            return False, None
        except Exception as e:
            logger.error(f"Ban durumu kontrol hatasi: {e}")
            return False, None


# ==================== BLACKLIST MANAGEMENT ====================

class BlacklistManager:
    """Kara liste yonetimi (admin islemleri)"""

    def __init__(self, db: Session):
        self.db = db

    def add_word(
        self,
        word: str,
        category: str = "general",
        added_by: Optional[int] = None
    ) -> Dict:
        """Kara listeye kelime ekle"""
        try:
            from app.models.database import ContentBlacklist

            word_lower = word.lower().strip()

            # Mevcut mu kontrol et
            existing = self.db.query(ContentBlacklist).filter(
                ContentBlacklist.word == word_lower
            ).first()

            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    self.db.commit()
                    return {"id": existing.id, "word": word_lower, "reactivated": True}
                return {"id": existing.id, "word": word_lower, "exists": True}

            # Yeni ekle
            blacklist_entry = ContentBlacklist(
                word=word_lower,
                category=category,
                added_by=added_by
            )
            self.db.add(blacklist_entry)
            self.db.commit()

            return {"id": blacklist_entry.id, "word": word_lower, "created": True}
        except Exception as e:
            logger.error(f"Kara liste kelime ekleme hatasi: {e}")
            self.db.rollback()
            raise

    def remove_word(self, word_id: int) -> bool:
        """Kara listeden kelime kaldir (soft delete)"""
        try:
            from app.models.database import ContentBlacklist

            entry = self.db.query(ContentBlacklist).filter(
                ContentBlacklist.id == word_id
            ).first()

            if entry:
                entry.is_active = False
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Kara liste kelime kaldirma hatasi: {e}")
            self.db.rollback()
            return False

    def delete_word(self, word_id: int) -> bool:
        """Kara listeden kelimeyi kalici sil"""
        try:
            from app.models.database import ContentBlacklist

            deleted = self.db.query(ContentBlacklist).filter(
                ContentBlacklist.id == word_id
            ).delete()

            self.db.commit()
            return deleted > 0
        except Exception as e:
            logger.error(f"Kara liste kelime silme hatasi: {e}")
            self.db.rollback()
            return False

    def get_all_words(
        self,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict]:
        """Tum kara liste kelimelerini getir"""
        try:
            from app.models.database import ContentBlacklist, User

            query = self.db.query(ContentBlacklist)

            if active_only:
                query = query.filter(ContentBlacklist.is_active == True)

            if category:
                query = query.filter(ContentBlacklist.category == category)

            words = query.order_by(ContentBlacklist.created_at.desc()).all()

            result = []
            for w in words:
                added_by_user = None
                if w.added_by:
                    added_by_user = self.db.query(User).filter(User.id == w.added_by).first()

                result.append({
                    "id": w.id,
                    "word": w.word,
                    "category": w.category,
                    "is_active": w.is_active,
                    "added_by": added_by_user.username if added_by_user else None,
                    "created_at": w.created_at.isoformat() if w.created_at else None
                })

            return result
        except Exception as e:
            logger.error(f"Kara liste getirme hatasi: {e}")
            return []

    def get_categories(self) -> List[str]:
        """Mevcut kategorileri getir"""
        try:
            from app.models.database import ContentBlacklist

            categories = self.db.query(ContentBlacklist.category).distinct().all()
            return [c[0] for c in categories if c[0]]
        except Exception as e:
            logger.error(f"Kategori listesi getirme hatasi: {e}")
            return ["general"]

    def bulk_add_words(
        self,
        words: List[str],
        category: str = "general",
        added_by: Optional[int] = None
    ) -> Dict:
        """Toplu kelime ekle"""
        added = 0
        skipped = 0
        errors = []

        for word in words:
            try:
                result = self.add_word(word, category, added_by)
                if result.get("created"):
                    added += 1
                else:
                    skipped += 1
            except Exception as e:
                errors.append({"word": word, "error": str(e)})

        return {
            "added": added,
            "skipped": skipped,
            "errors": errors
        }


# ==================== HELPER FUNCTIONS ====================

def get_content_filter(db: Session = None) -> ContentFilter:
    """ContentFilter instance getir"""
    return ContentFilter(db)


def get_warning_system(db: Session) -> WarningSystem:
    """WarningSystem instance getir"""
    return WarningSystem(db)


def get_blacklist_manager(db: Session) -> BlacklistManager:
    """BlacklistManager instance getir"""
    return BlacklistManager(db)


def check_and_process_content(
    db: Session,
    content: str,
    user_id: int,
    action: str = "topic",
    auto_warn: bool = True,
    auto_filter: bool = False
) -> Dict:
    """
    Icerik kontrolu ve isleme (tum kontrolleri birlestir)

    Args:
        db: Database session
        content: Kontrol edilecek icerik
        user_id: Kullanici ID
        action: "topic" veya "reply"
        auto_warn: Ihlal durumunda otomatik uyari ver
        auto_filter: Yasakli kelimeleri filtrele (reddetme yerine)

    Returns:
        {
            "allowed": bool,
            "filtered_content": str,
            "violations": list,
            "warning_added": bool,
            "banned": bool,
            "message": str
        }
    """
    result = {
        "allowed": True,
        "filtered_content": content,
        "violations": [],
        "warning_added": False,
        "banned": False,
        "message": ""
    }

    # Ban kontrolu
    warning_system = get_warning_system(db)
    is_banned, ban_info = warning_system.check_ban_status(user_id)

    if is_banned:
        result["allowed"] = False
        result["banned"] = True
        remaining = round(ban_info["remaining_hours"], 1)
        result["message"] = f"Forum erimisiniz {remaining} saat sure ile askiya alinmistir. Sebep: {ban_info['reason']}"
        return result

    # Rate limit kontrolu
    content_filter = get_content_filter(db)
    rate_ok, rate_msg = content_filter.check_rate_limit(user_id, action)

    if not rate_ok:
        result["allowed"] = False
        result["message"] = rate_msg
        return result

    # Icerik kontrolu
    is_clean, violations = content_filter.check_content(content)
    result["violations"] = violations

    if not is_clean:
        if auto_filter:
            # Filtreleme modu: yasakli kelimeleri degistir
            result["filtered_content"] = content_filter.filter_content(content)
            result["allowed"] = True
            result["message"] = "Icerik filtrelendi"
        else:
            # Reddetme modu
            result["allowed"] = False
            result["message"] = "Icerik kurallara uygun degil: " + ", ".join(violations)

            # Otomatik uyari
            if auto_warn:
                warning_result = warning_system.add_warning(
                    user_id=user_id,
                    reason=f"Uygunsuz icerik: {', '.join(violations[:3])}"
                )
                result["warning_added"] = True
                result["banned"] = warning_result.get("banned", False)

                if result["banned"]:
                    result["message"] += f". {MAX_WARNINGS_BEFORE_BAN} uyari limitini astiniz, {DEFAULT_BAN_DURATION_HOURS} saat forum erimisiniz askiya alindi."

    return result
