"""
AGTR Merkezi - Common API Utilities
Standardized error handling, responses, and validation
"""

import logging
from datetime import datetime
from typing import Any, Dict, Generic, Optional, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ============================================
# Standard Response Models
# ============================================


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""

    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response"""

    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""

    success: bool = True
    data: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# Standard Error Handlers
# ============================================


class APIError(HTTPException):
    """Base API error class"""

    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Optional[str] = None,
        code: Optional[str] = None,
    ):
        super().__init__(status_code=status_code, detail=message)
        self.message = message
        self.error_detail = detail
        self.error_code = code


class BadRequestError(APIError):
    """400 Bad Request"""

    def __init__(self, message: str = "Bad request", detail: Optional[str] = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, detail, "BAD_REQUEST")


class UnauthorizedError(APIError):
    """401 Unauthorized"""

    def __init__(self, message: str = "Unauthorized", detail: Optional[str] = None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, detail, "UNAUTHORIZED")


class ForbiddenError(APIError):
    """403 Forbidden"""

    def __init__(self, message: str = "Forbidden", detail: Optional[str] = None):
        super().__init__(status.HTTP_403_FORBIDDEN, message, detail, "FORBIDDEN")


class NotFoundError(APIError):
    """404 Not Found"""

    def __init__(self, message: str = "Resource not found", detail: Optional[str] = None):
        super().__init__(status.HTTP_404_NOT_FOUND, message, detail, "NOT_FOUND")


class ConflictError(APIError):
    """409 Conflict"""

    def __init__(self, message: str = "Resource conflict", detail: Optional[str] = None):
        super().__init__(status.HTTP_409_CONFLICT, message, detail, "CONFLICT")


class ServerError(APIError):
    """500 Internal Server Error"""

    def __init__(self, message: str = "Internal server error", detail: Optional[str] = None):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, message, detail, "SERVER_ERROR")


# ============================================
# Common Validation Functions
# ============================================


def validate_server_ownership(server, user):
    """Validate user owns the server"""
    if server.owner_id != user.id and not user.is_admin:
        raise ForbiddenError("Bu sunucuya erişim yetkiniz yok")
    return True


def validate_server_status(server, required_status: str):
    """Validate server is in required status"""
    if server.status != required_status:
        raise BadRequestError(
            f"Sunucu {required_status} durumunda olmalı", f"Mevcut durum: {server.status}"
        )
    return True


def validate_pagination(page: int, per_page: int) -> tuple[int, int]:
    """Validate and normalize pagination parameters"""
    page = max(1, page)
    per_page = min(max(1, per_page), 100)  # Max 100 items per page
    return page, per_page


# ============================================
# Response Helpers
# ============================================


def success_response(data: Any = None, message: Optional[str] = None) -> Dict:
    """Create standard success response"""
    response = {"success": True}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    return response


def error_response(message: str, detail: Optional[str] = None, code: Optional[str] = None) -> Dict:
    """Create standard error response"""
    response = {"success": False, "error": message}
    if detail:
        response["detail"] = detail
    if code:
        response["code"] = code
    return response


def paginated_response(data: list, total: int, page: int, per_page: int) -> Dict:
    """Create paginated response"""
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    return {
        "success": True,
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
        },
    }


# ============================================
# Logging Helpers
# ============================================


def log_api_call(endpoint: str, user_id: Optional[int], params: Dict = None):
    """Log API call for monitoring"""
    logger.info(
        f"API Call: {endpoint}",
        extra={"user_id": user_id, "params": params, "timestamp": datetime.utcnow().isoformat()},
    )


def log_api_error(endpoint: str, error: Exception, user_id: Optional[int] = None):
    """Log API error for debugging"""
    logger.error(
        f"API Error: {endpoint} - {str(error)}",
        extra={
            "user_id": user_id,
            "error_type": type(error).__name__,
            "timestamp": datetime.utcnow().isoformat(),
        },
        exc_info=True,
    )


# ============================================
# Common Filters
# ============================================


class CommonFilters(BaseModel):
    """Common query filters"""

    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")
    search: Optional[str] = Field(None, max_length=100, description="Search query")


class DateRangeFilter(BaseModel):
    """Date range filter"""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    def validate_range(self):
        """Validate date range"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise BadRequestError("Başlangıç tarihi bitiş tarihinden sonra olamaz")
        return True
