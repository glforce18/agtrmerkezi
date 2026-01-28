from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User, UserPreference

router = APIRouter(prefix="/api/v2/preferences")


@router.get("", response_model=Dict[str, Any])
async def get_preferences(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Get current user's panel preferences
    """
    # Check if preferences exist
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()

    if not pref:
        # Create default preferences
        pref = UserPreference(
            user_id=current_user.id,
            theme="dark",
            language="tr",
            panel_layout={},
            tab_order=[],
            hidden_tabs=[],
            theme_schedule={},
            quick_actions=[
                "open-command-palette",
                "open-console",
                "restart-server",
                "open-players",
                "quick-command",
                "open-settings",
            ],
            notification_settings={},
            timezone="Europe/Istanbul",
            tour_completed=False,
        )
        db.add(pref)
        await db.commit()
        await db.refresh(pref)

    return {
        "theme": pref.theme,
        "language": pref.language,
        "panel_layout": pref.panel_layout or {},
        "tab_order": pref.tab_order or [],
        "hidden_tabs": pref.hidden_tabs or [],
        "theme_schedule": pref.theme_schedule or {},
        "quick_actions": pref.quick_actions or [],
        "notification_settings": pref.notification_settings or {},
        "timezone": pref.timezone,
        "tour_completed": pref.tour_completed or False,
    }


@router.put("", response_model=Dict[str, Any])
async def update_preferences(
    preferences: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user's panel preferences
    """
    # Get existing preferences
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()

    if not pref:
        # Create new preferences
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    # Update fields
    if "theme" in preferences:
        pref.theme = preferences["theme"]
    if "language" in preferences:
        pref.language = preferences["language"]
    if "panel_layout" in preferences:
        pref.panel_layout = preferences["panel_layout"]
    if "tab_order" in preferences:
        pref.tab_order = preferences["tab_order"]
    if "hidden_tabs" in preferences:
        pref.hidden_tabs = preferences["hidden_tabs"]
    if "theme_schedule" in preferences:
        pref.theme_schedule = preferences["theme_schedule"]
    if "quick_actions" in preferences:
        pref.quick_actions = preferences["quick_actions"]
    if "notification_settings" in preferences:
        pref.notification_settings = preferences["notification_settings"]
    if "timezone" in preferences:
        pref.timezone = preferences["timezone"]
    if "tour_completed" in preferences:
        pref.tour_completed = preferences["tour_completed"]

    await db.commit()
    await db.refresh(pref)

    return {
        "success": True,
        "message": "Preferences updated successfully",
        "preferences": {
            "theme": pref.theme,
            "language": pref.language,
            "panel_layout": pref.panel_layout or {},
            "tab_order": pref.tab_order or [],
            "hidden_tabs": pref.hidden_tabs or [],
            "quick_actions": pref.quick_actions or [],
        },
    }


@router.post("/reset", response_model=Dict[str, Any])
async def reset_preferences(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Reset preferences to defaults
    """
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    pref = result.scalar_one_or_none()

    if pref:
        pref.theme = "dark"
        pref.language = "tr"
        pref.panel_layout = {}
        pref.tab_order = []
        pref.hidden_tabs = []
        pref.theme_schedule = {}
        pref.quick_actions = [
            "open-command-palette",
            "open-console",
            "restart-server",
            "open-players",
            "quick-command",
            "open-settings",
        ]
        pref.notification_settings = {}
        pref.tour_completed = False

        await db.commit()

    return {"success": True, "message": "Preferences reset to defaults"}
