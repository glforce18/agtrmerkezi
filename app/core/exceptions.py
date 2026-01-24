# ============================================
# AGTR v6.0 - Custom Exception Hierarchy
# Dosya: app/core/exceptions.py
# Custom exception classes for better error handling
# ============================================

from typing import Any, Dict, Optional


class AGTRException(Exception):
    """Base exception for all AGTR custom exceptions"""

    def __init__(
        self,
        message: str,
        error_code: str = "AGTR_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dict for API response"""
        return {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            },
        }


# ============ Forum Exceptions ============


class ForumException(AGTRException):
    """Base exception for forum-related errors"""

    def __init__(self, message: str, error_code: str = "FORUM_ERROR", **kwargs):
        super().__init__(message, error_code, status_code=400, **kwargs)


class TopicNotFoundException(ForumException):
    """Topic not found"""

    def __init__(self, topic_id: Any = None):
        super().__init__(
            message="Konu bulunamadi",
            error_code="TOPIC_NOT_FOUND",
            details={"topic_id": topic_id} if topic_id else {},
        )
        self.status_code = 404


class CategoryNotFoundException(ForumException):
    """Category not found"""

    def __init__(self, category_id: Any = None):
        super().__init__(
            message="Kategori bulunamadi",
            error_code="CATEGORY_NOT_FOUND",
            details={"category_id": category_id} if category_id else {},
        )
        self.status_code = 404


class ReplyNotFoundException(ForumException):
    """Reply not found"""

    def __init__(self, reply_id: Any = None):
        super().__init__(
            message="Yanit bulunamadi",
            error_code="REPLY_NOT_FOUND",
            details={"reply_id": reply_id} if reply_id else {},
        )
        self.status_code = 404


class TopicLockedException(ForumException):
    """Topic is locked"""

    def __init__(self, topic_id: Any = None):
        super().__init__(
            message="Bu konu kilitli, yanit yazilamaz",
            error_code="TOPIC_LOCKED",
            details={"topic_id": topic_id} if topic_id else {},
        )
        self.status_code = 403


class InsufficientPermissionsException(ForumException):
    """User doesn't have permission"""

    def __init__(self, action: str = None):
        super().__init__(
            message="Bu islemi yapmak icin yetkiniz yok",
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"action": action} if action else {},
        )
        self.status_code = 403


class RateLimitExceededException(ForumException):
    """Rate limit exceeded"""

    def __init__(self, action: str, retry_after: int = None):
        message = f"Cok fazla {action} islemi yapiyorsunuz"
        if retry_after:
            message += f", {retry_after} saniye sonra tekrar deneyin"

        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"action": action, "retry_after": retry_after},
        )
        self.status_code = 429


class ContentValidationException(ForumException):
    """Content validation failed"""

    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"{field}: {reason}",
            error_code="CONTENT_VALIDATION_ERROR",
            details={"field": field, "reason": reason},
        )


class SpamDetectedException(ForumException):
    """Content detected as spam"""

    def __init__(self, severity: int = None):
        super().__init__(
            message="Icerik spam olarak tespit edildi",
            error_code="SPAM_DETECTED",
            details={"severity": severity} if severity else {},
        )
        self.status_code = 403


class DuplicateContentException(ForumException):
    """Duplicate topic/reply detected"""

    def __init__(self, content_type: str = "content"):
        super().__init__(
            message=f"Ayni {content_type} zaten mevcut",
            error_code="DUPLICATE_CONTENT",
            details={"content_type": content_type},
        )
        self.status_code = 409


# ============ Poll Exceptions ============


class PollException(ForumException):
    """Base exception for poll-related errors"""

    def __init__(self, message: str, error_code: str = "POLL_ERROR", **kwargs):
        super().__init__(message, error_code, **kwargs)


class PollNotFoundException(PollException):
    """Poll not found"""

    def __init__(self, poll_id: Any = None):
        super().__init__(
            message="Anket bulunamadi",
            error_code="POLL_NOT_FOUND",
            details={"poll_id": poll_id} if poll_id else {},
        )
        self.status_code = 404


class PollExpiredException(PollException):
    """Poll has expired"""

    def __init__(self):
        super().__init__(message="Anket sona ermis", error_code="POLL_EXPIRED")
        self.status_code = 410


class PollAlreadyExistsException(PollException):
    """Poll already exists for topic"""

    def __init__(self, topic_id: Any = None):
        super().__init__(
            message="Bu konuda zaten bir anket var",
            error_code="POLL_ALREADY_EXISTS",
            details={"topic_id": topic_id} if topic_id else {},
        )
        self.status_code = 409


class InvalidPollOptionsException(PollException):
    """Invalid poll options"""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Gecersiz anket secenekleri: {reason}",
            error_code="INVALID_POLL_OPTIONS",
            details={"reason": reason},
        )


class AlreadyVotedException(PollException):
    """User already voted"""

    def __init__(self):
        super().__init__(message="Bu ankete zaten oy verdiniz", error_code="ALREADY_VOTED")
        self.status_code = 409


# ============ Draft Exceptions ============


class DraftException(ForumException):
    """Base exception for draft-related errors"""

    def __init__(self, message: str, error_code: str = "DRAFT_ERROR", **kwargs):
        super().__init__(message, error_code, **kwargs)


class DraftNotFoundException(DraftException):
    """Draft not found"""

    def __init__(self):
        super().__init__(message="Taslak bulunamadi", error_code="DRAFT_NOT_FOUND")
        self.status_code = 404


class DraftSaveException(DraftException):
    """Failed to save draft"""

    def __init__(self, reason: str = None):
        super().__init__(
            message="Taslak kaydedilemedi",
            error_code="DRAFT_SAVE_ERROR",
            details={"reason": reason} if reason else {},
        )


# ============ Authentication Exceptions ============


class AuthenticationException(AGTRException):
    """Base exception for authentication errors"""

    def __init__(self, message: str, error_code: str = "AUTH_ERROR", **kwargs):
        super().__init__(message, error_code, status_code=401, **kwargs)


class SteamRequiredException(AuthenticationException):
    """Steam account required for this action"""

    def __init__(self, action: str = None):
        super().__init__(
            message="Bu islem icin Steam hesabi baglantisi gerekli",
            error_code="STEAM_REQUIRED",
            details={"action": action} if action else {},
        )
        self.status_code = 403


class EmailVerificationRequiredException(AuthenticationException):
    """Email verification required"""

    def __init__(self):
        super().__init__(
            message="Bu islem icin email dogrulamasi gerekli", error_code="EMAIL_VERIFICATION_REQUIRED"
        )
        self.status_code = 403


# ============ Database Exceptions ============


class DatabaseException(AGTRException):
    """Base exception for database errors"""

    def __init__(self, message: str = "Veritabani hatasi", error_code: str = "DATABASE_ERROR", **kwargs):
        super().__init__(message, error_code, status_code=500, **kwargs)


class DatabaseConnectionException(DatabaseException):
    """Database connection failed"""

    def __init__(self):
        super().__init__(message="Veritabani baglantisi kurulamadi", error_code="DB_CONNECTION_ERROR")


class DatabaseQueryException(DatabaseException):
    """Database query failed"""

    def __init__(self, query_type: str = None):
        super().__init__(
            message="Veritabani sorgusu basarisiz",
            error_code="DB_QUERY_ERROR",
            details={"query_type": query_type} if query_type else {},
        )


# ============ Cache Exceptions ============


class CacheException(AGTRException):
    """Base exception for cache errors"""

    def __init__(self, message: str = "Cache hatasi", error_code: str = "CACHE_ERROR", **kwargs):
        # Cache errors should not break the application - log and continue
        super().__init__(message, error_code, status_code=500, **kwargs)


class CacheConnectionException(CacheException):
    """Cache connection failed"""

    def __init__(self):
        super().__init__(message="Cache baglantisi kurulamadi", error_code="CACHE_CONNECTION_ERROR")


# ============ Validation Exceptions ============


class ValidationException(AGTRException):
    """Base exception for validation errors"""

    def __init__(
        self, message: str = "Dogrulama hatasi", error_code: str = "VALIDATION_ERROR", **kwargs
    ):
        super().__init__(message, error_code, status_code=422, **kwargs)


class InvalidInputException(ValidationException):
    """Invalid input data"""

    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"{field}: {reason}",
            error_code="INVALID_INPUT",
            details={"field": field, "reason": reason},
        )
