"""
🏥 AGTR System API - Health Check & Auto-Fix
"""
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from app.core.engine import healer, health_checker, logger
except:
    logger = healer = health_checker = None

from app.models.connection import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """🏥 Basit sağlık kontrolü"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "5.4 Pro"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@router.get("/health/detailed")
async def detailed_health(db: Session = Depends(get_db)):
    """🔬 Detaylı sağlık kontrolü"""
    if health_checker:
        return await health_checker.full_check(db)
    return {"status": "unknown", "message": "Health checker yüklenmedi"}


@router.post("/fix/all")
async def run_fixes(background_tasks: BackgroundTasks):
    """💊 Otomatik düzeltmeleri çalıştır"""
    if healer:
        background_tasks.add_task(healer.run_all)
        return {"success": True, "message": "Düzeltmeler başlatıldı"}
    return {"success": False, "error": "Healer yüklenmedi"}


@router.get("/fix/report")
async def fix_report():
    """📋 Son düzeltme raporu"""
    if healer:
        return {"fixes": healer.fixes, "count": len(healer.fixes)}
    return {"fixes": [], "count": 0}
