# ============================================
# AGTR v6.0 - Exception Handler Middleware
# Dosya: app/middleware/exception_handler.py
# Global exception handling for consistent API responses
# ============================================

import logging
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from app.core.exceptions import AGTRException, CacheException, DatabaseException

logger = logging.getLogger(__name__)


async def agtr_exception_handler(request: Request, call_next: Callable):
    """
    Global exception handler middleware
    Catches all exceptions and returns consistent JSON responses
    """
    try:
        response = await call_next(request)
        return response

    except AGTRException as e:
        # Our custom exceptions - already formatted
        logger.warning(
            f"AGTR Exception: {e.error_code} - {e.message}",
            extra={
                "error_code": e.error_code,
                "status_code": e.status_code,
                "details": e.details,
                "path": request.url.path,
            },
        )
        return JSONResponse(status_code=e.status_code, content=e.to_dict())

    except IntegrityError as e:
        # Database integrity constraint violation
        logger.error(f"Database IntegrityError: {str(e)}", exc_info=True)

        # Try to extract meaningful error message
        error_msg = str(e.orig) if hasattr(e, "orig") else str(e)

        if "Duplicate entry" in error_msg:
            message = "Bu kayit zaten mevcut"
            error_code = "DUPLICATE_ENTRY"
        elif "foreign key constraint" in error_msg.lower():
            message = "Iliskili kayit bulunamadi"
            error_code = "FOREIGN_KEY_ERROR"
        else:
            message = "Veritabani kisitlama hatasi"
            error_code = "INTEGRITY_ERROR"

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"success": False, "error": {"code": error_code, "message": message}},
        )

    except OperationalError as e:
        # Database connection/operational errors
        logger.error(f"Database OperationalError: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_UNAVAILABLE",
                    "message": "Veritabani servisine ulasilamiyor",
                },
            },
        )

    except SQLAlchemyError as e:
        # Other database errors
        logger.error(f"SQLAlchemy error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {"code": "DATABASE_ERROR", "message": "Veritabani hatasi olustu"},
            },
        )

    except CacheException as e:
        # Cache errors - log but don't fail the request
        logger.warning(f"Cache error (non-fatal): {e.message}", extra={"details": e.details})
        # Continue processing without cache
        response = await call_next(request)
        return response

    except ValueError as e:
        # Invalid input values
        logger.warning(f"ValueError: {str(e)}", extra={"path": request.url.path})
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {"code": "INVALID_VALUE", "message": str(e)},
            },
        )

    except Exception as e:
        # Unexpected errors - log full stack trace
        logger.error(
            f"Unexpected error: {str(e)}",
            exc_info=True,
            extra={"path": request.url.path, "method": request.method},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Beklenmeyen bir hata olustu",
                },
            },
        )


def register_exception_handler(app):
    """Register exception handler middleware with FastAPI app"""
    app.middleware("http")(agtr_exception_handler)
