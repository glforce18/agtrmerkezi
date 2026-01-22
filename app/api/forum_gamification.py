# ============================================
# AGTR v6.0 - Forum Gamification API
# Dosya: app/api/forum_gamification.py
# Badge System, Reputation, and CAPTCHA Endpoints
# ============================================

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_current_user_required
from app.models.connection import get_db
from app.models.database import User

router = APIRouter(prefix="/forum", tags=["forum-gamification"])
logger = logging.getLogger(__name__)


# ============ Pydantic Schemas ============

class CaptchaVerify(BaseModel):
    token: str
    answer: str


# ============ Badge System Endpoints ============

@router.get("/badges")
async def get_all_badges(db: Session = Depends(get_db)):
    """Tum forum rozetlerini listele"""
    from app.services.forum_gamification import get_forum_gamification_service

    service = get_forum_gamification_service(db)
    badges = service.get_all_badges()
    return {"badges": badges}


@router.get("/badges/my")
async def get_my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Kullanicinin kazandigi rozetleri getir"""
    from app.services.forum_gamification import get_forum_gamification_service

    service = get_forum_gamification_service(db)
    badges = service.get_user_badges(current_user.id)

    # Also check and potentially award new badges
    try:
        new_badges = await service.check_and_award_badges(current_user.id)
        if new_badges:
            return {
                "badges": badges + new_badges,
                "new_badges": new_badges,
                "message": f"{len(new_badges)} yeni rozet kazandiniz!"
            }
    except Exception as e:
        logger.error(f"Badge check error: {e}")

    return {"badges": badges}


@router.get("/badges/user/{user_id}")
async def get_user_badges(user_id: int, db: Session = Depends(get_db)):
    """Belirli bir kullanicinin rozetlerini getir"""
    from app.services.forum_gamification import get_forum_gamification_service

    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")

    service = get_forum_gamification_service(db)
    badges = service.get_user_badges(user_id)
    return {
        "user_id": user_id,
        "username": user.username,
        "badges": badges
    }


# ============ Reputation System Endpoints ============

@router.get("/reputation/leaderboard")
async def get_reputation_leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Reputation siralamasini getir (Top 10 varsayilan)"""
    from app.services.forum_gamification import get_forum_gamification_service

    service = get_forum_gamification_service(db)
    leaderboard = service.get_reputation_leaderboard(limit)
    return {"leaderboard": leaderboard, "limit": limit}


@router.get("/reputation/my")
async def get_my_reputation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Kullanicinin reputation bilgisini getir"""
    # Get user's rank
    higher_count = db.query(func.count(User.id)).filter(
        User.reputation > (current_user.reputation or 0)
    ).scalar() or 0
    rank = higher_count + 1

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "reputation": current_user.reputation or 0,
        "rank": rank
    }


# ============ CAPTCHA Endpoints ============

@router.post("/captcha/generate")
async def generate_forum_captcha(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Yeni kullanicilar icin CAPTCHA olustur"""
    from app.services.forum_gamification import (
        generate_captcha,
        user_requires_captcha
    )

    # Check if user actually needs CAPTCHA
    needs_captcha = await user_requires_captcha(db, current_user.id)
    if not needs_captcha:
        return {
            "required": False,
            "message": "CAPTCHA gerekli degil"
        }

    captcha = await generate_captcha()
    return {
        "required": True,
        "question": captcha["question"],
        "token": captcha["token"],
        "expires_in": captcha["expires_in"]
    }


@router.post("/captcha/verify")
async def verify_forum_captcha(
    data: CaptchaVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """CAPTCHA dogrula"""
    from app.services.forum_gamification import verify_captcha

    is_valid = await verify_captcha(data.token, data.answer)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="CAPTCHA yanlis. Lutfen tekrar deneyin."
        )

    return {"valid": True, "message": "CAPTCHA dogrulandi"}


@router.get("/captcha/required")
async def check_captcha_required(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Kullanicinin CAPTCHA'ya ihtiyaci var mi kontrol et"""
    from app.services.forum_gamification import user_requires_captcha

    required = await user_requires_captcha(db, current_user.id)
    return {"required": required}
