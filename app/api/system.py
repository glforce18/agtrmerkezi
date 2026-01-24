"""
🏥 AGTR System API - Health Check & Auto-Fix
"""

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from app.core.engine import healer, health_checker, logger
except ImportError:
    logger = healer = health_checker = None

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import User

router = APIRouter()


def require_admin(user: User):
    """Admin yetkisi kontrolü"""
    if user.role.value not in ["admin", "superadmin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin yetkisi gerekli")


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """🏥 Basit sağlık kontrolü"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "5.4 Pro",
        }
    except Exception as e:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})


@router.get("/health/detailed")
async def detailed_health(db: Session = Depends(get_db)):
    """🔬 Detaylı sağlık kontrolü"""
    if health_checker:
        return await health_checker.full_check(db)
    return {"status": "unknown", "message": "Health checker yüklenmedi"}


@router.post("/fix/all")
async def run_fixes(
    background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user_required)
):
    """💊 Otomatik düzeltmeleri çalıştır (Admin only)"""
    require_admin(current_user)
    if healer:
        background_tasks.add_task(healer.run_all)
        return {"success": True, "message": "Düzeltmeler başlatıldı"}
    return {"success": False, "error": "Healer yüklenmedi"}


@router.get("/fix/report")
async def fix_report(current_user: User = Depends(get_current_user_required)):
    """📋 Son düzeltme raporu (Admin only)"""
    require_admin(current_user)
    if healer:
        return {"fixes": healer.fixes, "count": len(healer.fixes)}
    return {"fixes": [], "count": 0}


class ErrorItem(BaseModel):
    message: Optional[str] = None
    stack: Optional[str] = None
    url: Optional[str] = None
    userAgent: Optional[str] = None
    extra: Optional[Any] = None

    @field_validator("message", "stack", "url", "userAgent")
    @classmethod
    def limit_string_length(cls, v):
        if v and len(v) > 2000:
            return v[:2000]
        return v


class ErrorReport(BaseModel):
    errors: Optional[list] = []

    @field_validator("errors")
    @classmethod
    def limit_errors(cls, v):
        if v and len(v) > 10:
            return v[:10]
        return v


@router.post("/errors/report")
async def report_client_error(report: ErrorReport = None):
    """📋 Client-side hata raporlama endpoint'i (Rate limited)"""
    if not report or not report.errors:
        return {"success": True, "message": "No errors to report"}

    # Max 5 error log
    if logger:
        for err in report.errors[:5]:
            if isinstance(err, dict):
                msg = str(err.get("message", "Unknown"))[:200]
                url = str(err.get("url", "Unknown"))[:200]
                logger.warning(f"Client error: {msg} at {url}")
    return {"success": True, "message": "Error reported"}
