"""
AGTR Merkezi - Admin Statistics API
Steam-linked user statistics and platform analytics
"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import (
    ForumPost,
    ForumTopic,
    GameServer,
    LoginHistory,
    OAuthAccount,
    Payment,
    PaymentStatus,
    ServerStatus,
    User,
    UserStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stats", tags=["Admin Stats"])


@router.get("/users/overview")
async def get_user_stats(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Kullanici istatistikleri genel bakis"""
    # Total users
    total_users = db.query(func.count(User.id)).scalar() or 0

    # Steam linked users
    steam_linked = (
        db.query(func.count(User.id)).filter(User.steam_id != None, User.steam_id != "").scalar()
        or 0
    )

    # Email verified users
    email_verified = db.query(func.count(User.id)).filter(User.email_verified == True).scalar() or 0

    # Active users (status = active)
    active_users = (
        db.query(func.count(User.id)).filter(User.status == UserStatus.ACTIVE).scalar() or 0
    )

    # Banned users
    banned_users = (
        db.query(func.count(User.id)).filter(User.status == UserStatus.BANNED).scalar() or 0
    )

    # Users with 2FA enabled
    two_fa_enabled = (
        db.query(func.count(User.id)).filter(User.two_factor_enabled == True).scalar() or 0
    )

    # Users registered today
    today = datetime.utcnow().date()
    today_registrations = (
        db.query(func.count(User.id)).filter(func.date(User.created_at) == today).scalar() or 0
    )

    # Users registered this week
    week_start = datetime.utcnow() - timedelta(days=7)
    week_registrations = (
        db.query(func.count(User.id)).filter(User.created_at >= week_start).scalar() or 0
    )

    # Users registered this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_registrations = (
        db.query(func.count(User.id)).filter(User.created_at >= month_start).scalar() or 0
    )

    # Average balance
    avg_balance = db.query(func.avg(User.balance)).scalar() or 0
    avg_balance_coin = db.query(func.avg(User.balance_coin)).scalar() or 0

    return {
        "total_users": total_users,
        "steam_linked": steam_linked,
        "steam_percentage": round(steam_linked / total_users * 100, 1) if total_users > 0 else 0,
        "non_steam_users": total_users - steam_linked,
        "email_verified": email_verified,
        "email_verified_percentage": (
            round(email_verified / total_users * 100, 1) if total_users > 0 else 0
        ),
        "active_users": active_users,
        "banned_users": banned_users,
        "two_fa_enabled": two_fa_enabled,
        "two_fa_percentage": round(two_fa_enabled / total_users * 100, 1) if total_users > 0 else 0,
        "registrations": {
            "today": today_registrations,
            "this_week": week_registrations,
            "this_month": month_registrations,
        },
        "average_balance": {
            "real": round(float(avg_balance), 2),
            "coin": round(float(avg_balance_coin), 2),
        },
    }


@router.get("/users/steam-breakdown")
async def get_steam_breakdown(
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """Steam hesap baglantisi detayli dagilimi"""
    total_users = db.query(func.count(User.id)).scalar() or 0

    # Steam linked users
    steam_linked = (
        db.query(func.count(User.id)).filter(User.steam_id != None, User.steam_id != "").scalar()
        or 0
    )

    # OAuth accounts by provider
    oauth_providers = (
        db.query(OAuthAccount.provider, func.count(OAuthAccount.id))
        .group_by(OAuthAccount.provider)
        .all()
    )

    oauth_breakdown = {provider: count for provider, count in oauth_providers}

    # Steam users who also have verified email
    steam_with_email = (
        db.query(func.count(User.id))
        .filter(User.steam_id != None, User.steam_id != "", User.email_verified == True)
        .scalar()
        or 0
    )

    # Steam users who have made payments
    steam_paying_users = (
        db.query(func.count(func.distinct(Payment.user_id)))
        .join(User, User.id == Payment.user_id)
        .filter(
            User.steam_id != None, User.steam_id != "", Payment.status == PaymentStatus.COMPLETED
        )
        .scalar()
        or 0
    )

    # Non-Steam paying users
    non_steam_paying_users = (
        db.query(func.count(func.distinct(Payment.user_id)))
        .join(User, User.id == Payment.user_id)
        .filter(
            or_(User.steam_id == None, User.steam_id == ""),
            Payment.status == PaymentStatus.COMPLETED,
        )
        .scalar()
        or 0
    )

    # Steam users with servers
    steam_server_owners = (
        db.query(func.count(func.distinct(GameServer.owner_id)))
        .join(User, User.id == GameServer.owner_id)
        .filter(
            User.steam_id != None, User.steam_id != "", GameServer.status != ServerStatus.DELETED
        )
        .scalar()
        or 0
    )

    # Role distribution for Steam users
    steam_role_distribution = (
        db.query(User.role, func.count(User.id))
        .filter(User.steam_id != None, User.steam_id != "")
        .group_by(User.role)
        .all()
    )

    role_breakdown = {role.value: count for role, count in steam_role_distribution}

    return {
        "total_users": total_users,
        "steam_linked": steam_linked,
        "steam_percentage": round(steam_linked / total_users * 100, 1) if total_users > 0 else 0,
        "non_steam_users": total_users - steam_linked,
        "oauth_providers": oauth_breakdown,
        "steam_with_verified_email": steam_with_email,
        "steam_engagement": {
            "paying_users": steam_paying_users,
            "server_owners": steam_server_owners,
            "paying_percentage": (
                round(steam_paying_users / steam_linked * 100, 1) if steam_linked > 0 else 0
            ),
        },
        "non_steam_engagement": {
            "paying_users": non_steam_paying_users,
            "paying_percentage": (
                round(non_steam_paying_users / (total_users - steam_linked) * 100, 1)
                if (total_users - steam_linked) > 0
                else 0
            ),
        },
        "steam_role_distribution": role_breakdown,
    }


@router.get("/users/registrations")
async def get_registration_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Gunluk kayit istatistikleri"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Daily registrations
    daily_registrations = []
    steam_daily = []
    non_steam_daily = []

    for i in range(days):
        day = (datetime.utcnow() - timedelta(days=days - 1 - i)).date()

        # Total registrations for the day
        day_count = (
            db.query(func.count(User.id)).filter(func.date(User.created_at) == day).scalar() or 0
        )

        # Steam registrations for the day
        steam_count = (
            db.query(func.count(User.id))
            .filter(func.date(User.created_at) == day, User.steam_id != None, User.steam_id != "")
            .scalar()
            or 0
        )

        daily_registrations.append({"date": str(day), "count": day_count})

        steam_daily.append({"date": str(day), "count": steam_count})

        non_steam_daily.append({"date": str(day), "count": day_count - steam_count})

    # Weekly summary
    weekly_total = sum(r["count"] for r in daily_registrations[-7:])
    weekly_steam = sum(r["count"] for r in steam_daily[-7:])

    # Monthly summary
    monthly_total = sum(
        r["count"] for r in daily_registrations[-30:] if len(daily_registrations) >= 30
    ) or sum(r["count"] for r in daily_registrations)
    monthly_steam = sum(r["count"] for r in steam_daily[-30:] if len(steam_daily) >= 30) or sum(
        r["count"] for r in steam_daily
    )

    return {
        "period_days": days,
        "daily_registrations": daily_registrations,
        "steam_registrations": steam_daily,
        "non_steam_registrations": non_steam_daily,
        "summary": {
            "weekly": {
                "total": weekly_total,
                "steam": weekly_steam,
                "non_steam": weekly_total - weekly_steam,
                "steam_percentage": (
                    round(weekly_steam / weekly_total * 100, 1) if weekly_total > 0 else 0
                ),
            },
            "monthly": {
                "total": monthly_total,
                "steam": monthly_steam,
                "non_steam": monthly_total - monthly_steam,
                "steam_percentage": (
                    round(monthly_steam / monthly_total * 100, 1) if monthly_total > 0 else 0
                ),
            },
        },
    }


@router.get("/activity/overview")
async def get_activity_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Platform aktivite istatistikleri"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Active users (logged in within the period)
    active_in_period = (
        db.query(func.count(User.id)).filter(User.last_login >= start_date).scalar() or 0
    )

    # Steam users active in period
    steam_active = (
        db.query(func.count(User.id))
        .filter(User.last_login >= start_date, User.steam_id != None, User.steam_id != "")
        .scalar()
        or 0
    )

    # Login history stats
    total_logins = (
        db.query(func.count(LoginHistory.id))
        .filter(LoginHistory.created_at >= start_date, LoginHistory.is_successful == True)
        .scalar()
        or 0
    )

    # Logins by type
    login_types = (
        db.query(LoginHistory.login_type, func.count(LoginHistory.id))
        .filter(LoginHistory.created_at >= start_date, LoginHistory.is_successful == True)
        .group_by(LoginHistory.login_type)
        .all()
    )

    login_type_breakdown = {login_type: count for login_type, count in login_types}

    # Forum activity
    new_topics = (
        db.query(func.count(ForumTopic.id)).filter(ForumTopic.created_at >= start_date).scalar()
        or 0
    )

    new_posts = (
        db.query(func.count(ForumPost.id)).filter(ForumPost.created_at >= start_date).scalar() or 0
    )

    # Forum activity by Steam users
    steam_topics = (
        db.query(func.count(ForumTopic.id))
        .join(User, User.id == ForumTopic.author_id)
        .filter(ForumTopic.created_at >= start_date, User.steam_id != None, User.steam_id != "")
        .scalar()
        or 0
    )

    steam_posts = (
        db.query(func.count(ForumPost.id))
        .join(User, User.id == ForumPost.author_id)
        .filter(ForumPost.created_at >= start_date, User.steam_id != None, User.steam_id != "")
        .scalar()
        or 0
    )

    # Payment activity
    completed_payments = (
        db.query(func.count(Payment.id))
        .filter(Payment.completed_at >= start_date, Payment.status == PaymentStatus.COMPLETED)
        .scalar()
        or 0
    )

    total_revenue = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.completed_at >= start_date, Payment.status == PaymentStatus.COMPLETED)
        .scalar()
        or 0
    )

    # Revenue from Steam users
    steam_revenue = (
        db.query(func.sum(Payment.amount))
        .join(User, User.id == Payment.user_id)
        .filter(
            Payment.completed_at >= start_date,
            Payment.status == PaymentStatus.COMPLETED,
            User.steam_id != None,
            User.steam_id != "",
        )
        .scalar()
        or 0
    )

    # Server activity
    new_servers = (
        db.query(func.count(GameServer.id)).filter(GameServer.created_at >= start_date).scalar()
        or 0
    )

    running_servers = (
        db.query(func.count(GameServer.id))
        .filter(GameServer.status == ServerStatus.RUNNING)
        .scalar()
        or 0
    )

    return {
        "period_days": days,
        "user_activity": {
            "active_users": active_in_period,
            "steam_active": steam_active,
            "non_steam_active": active_in_period - steam_active,
            "steam_active_percentage": (
                round(steam_active / active_in_period * 100, 1) if active_in_period > 0 else 0
            ),
            "total_logins": total_logins,
            "login_types": login_type_breakdown,
        },
        "forum_activity": {
            "new_topics": new_topics,
            "new_posts": new_posts,
            "steam_user_topics": steam_topics,
            "steam_user_posts": steam_posts,
            "steam_forum_percentage": (
                round((steam_topics + steam_posts) / (new_topics + new_posts) * 100, 1)
                if (new_topics + new_posts) > 0
                else 0
            ),
        },
        "financial_activity": {
            "completed_payments": completed_payments,
            "total_revenue": float(total_revenue),
            "steam_user_revenue": float(steam_revenue) if steam_revenue else 0,
            "non_steam_revenue": float(total_revenue - (steam_revenue or 0)),
            "steam_revenue_percentage": (
                round(float(steam_revenue or 0) / float(total_revenue) * 100, 1)
                if total_revenue > 0
                else 0
            ),
        },
        "server_activity": {"new_servers": new_servers, "running_servers": running_servers},
    }


@router.get("/users/recent")
async def get_recent_users(
    limit: int = Query(20, ge=1, le=100),
    steam_only: bool = False,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Son kaydolan kullanicilar listesi"""
    query = db.query(User)

    if steam_only:
        query = query.filter(User.steam_id != None, User.steam_id != "")

    users = query.order_by(User.created_at.desc()).limit(limit).all()

    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "steam_id": u.steam_id,
                "has_steam": bool(u.steam_id),
                "email_verified": u.email_verified,
                "status": u.status.value,
                "role": u.role.value,
                "balance": u.balance,
                "balance_coin": u.balance_coin,
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": len(users),
        "steam_only_filter": steam_only,
    }


@router.get("/users/top-spenders")
async def get_top_spenders(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """En cok harcama yapan kullanicilar"""
    start_date = datetime.utcnow() - timedelta(days=days)

    top_spenders = (
        db.query(
            User.id,
            User.username,
            User.steam_id,
            User.email,
            func.sum(Payment.amount).label("total_spent"),
            func.count(Payment.id).label("payment_count"),
        )
        .join(Payment, Payment.user_id == User.id)
        .filter(Payment.status == PaymentStatus.COMPLETED, Payment.completed_at >= start_date)
        .group_by(User.id, User.username, User.steam_id, User.email)
        .order_by(func.sum(Payment.amount).desc())
        .limit(limit)
        .all()
    )

    return {
        "period_days": days,
        "top_spenders": [
            {
                "id": user_id,
                "username": username,
                "steam_id": steam_id,
                "has_steam": bool(steam_id),
                "email": email,
                "total_spent": float(total_spent),
                "payment_count": payment_count,
            }
            for user_id, username, steam_id, email, total_spent, payment_count in top_spenders
        ],
    }
