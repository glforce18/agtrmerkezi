"""
Steam OAuth Authentication
"""

import logging
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.models.connection import get_db
from app.models.database import User, UserRole, UserStatus

router = APIRouter()
logger = logging.getLogger(__name__)

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
STEAM_API_KEY = settings.STEAM_API_KEY if hasattr(settings, "STEAM_API_KEY") else None


def steamid64_to_steamid(steamid64: str) -> str:
    """Convert SteamID64 to classic STEAM_0:X:XXXXXXX format"""
    try:
        steamid64_int = int(steamid64)
        # Calculate Y (0 or 1)
        y = steamid64_int % 2
        # Calculate Z
        z = (steamid64_int - 76561197960265728 - y) // 2
        return f"STEAM_0:{y}:{z}"
    except (ValueError, TypeError):
        logger.error(f"Invalid SteamID64: {steamid64}")
        return steamid64


def get_steam_login_url(return_url: str) -> str:
    """Generate Steam OpenID login URL"""
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": return_url,
        "openid.realm": settings.BASE_URL,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    return f"{STEAM_OPENID_URL}?{urlencode(params)}"


def validate_steam_response(params: dict) -> Optional[str]:
    """Validate Steam OpenID response and extract Steam ID"""
    # Change mode to check_authentication
    validation_params = dict(params)
    validation_params["openid.mode"] = "check_authentication"

    try:
        response = httpx.post(STEAM_OPENID_URL, data=validation_params, timeout=10.0)
        response_text = response.text

        if "is_valid:true" not in response_text:
            logger.warning("Steam validation failed: Invalid response")
            return None

        # Extract Steam ID from claimed_id
        claimed_id = params.get("openid.claimed_id", "")
        steam_id_match = re.search(r"https://steamcommunity.com/openid/id/(\d+)", claimed_id)

        if steam_id_match:
            return steam_id_match.group(1)

        logger.warning("Could not extract Steam ID from claimed_id")
        return None

    except Exception as e:
        logger.error(f"Steam validation error: {e}")
        return None


async def get_steam_user_info(steam_id: str) -> Optional[dict]:
    """Fetch user info from Steam API"""
    if not STEAM_API_KEY:
        logger.warning("STEAM_API_KEY not configured")
        return None

    try:
        url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        params = {"key": STEAM_API_KEY, "steamids": steam_id}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            data = response.json()

            players = data.get("response", {}).get("players", [])
            if players:
                return players[0]

        logger.warning(f"No player data found for Steam ID: {steam_id}")
        return None

    except Exception as e:
        logger.error(f"Error fetching Steam user info: {e}")
        return None


@router.get("/login")
async def steam_login(request: Request):
    """Initiate Steam login"""
    # Redirect URL after Steam authentication
    return_url = f"{settings.BASE_URL}/api/auth/steam/callback"

    # Generate and redirect to Steam login
    steam_url = get_steam_login_url(return_url)
    return RedirectResponse(url=steam_url)


@router.get("/callback")
async def steam_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Steam OpenID callback"""
    try:
        # Get all query parameters
        params = dict(request.query_params)

        # Validate Steam response
        steam_id64 = validate_steam_response(params)

        if not steam_id64:
            logger.error("Steam authentication failed: Invalid response")
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/?error=steam_auth_failed")

        # Convert SteamID64 to classic STEAM_0 format for game servers
        steam_id = steamid64_to_steamid(steam_id64)
        logger.info(f"Steam login: SteamID64={steam_id64}, GameID={steam_id}")

        # Get Steam user info (uses SteamID64 for API)
        steam_info = await get_steam_user_info(steam_id64)

        # Find or create user (search by game Steam ID)
        user = db.query(User).filter(User.steam_id == steam_id).first()

        if user:
            # Update existing user with latest Steam data
            if steam_info:
                user.steam_avatar = steam_info.get("avatarfull")
                user.steam_personaname = steam_info.get("personaname")
                user.steam_profileurl = steam_info.get("profileurl")
                user.steam_realname = steam_info.get("realname")
                user.avatar = steam_info.get("avatarfull")  # Update main avatar too

            user.last_login = datetime.utcnow()
            db.commit()
            logger.info(f"User logged in via Steam: {user.username} (Game ID: {steam_id})")

        else:
            # Create new user
            username = f"steam_{steam_id}"
            if steam_info:
                # Use Steam persona name as display name
                personaname = steam_info.get("personaname", username)
                # Create a safe username from persona name
                safe_username = re.sub(r"[^a-zA-Z0-9_]", "", personaname.lower())[:30]
                if not safe_username:
                    safe_username = username

                # Check if username exists, append number if needed
                base_username = safe_username
                counter = 1
                while db.query(User).filter(User.username == safe_username).first():
                    safe_username = f"{base_username}{counter}"
                    counter += 1

                username = safe_username

            user = User(
                username=username,
                email=None,  # Steam users don't need email
                password_hash="",  # No password for Steam users
                display_name=steam_info.get("personaname") if steam_info else username,
                steam_id=steam_id,
                steam_avatar=steam_info.get("avatarfull") if steam_info else None,
                steam_personaname=steam_info.get("personaname") if steam_info else None,
                steam_profileurl=steam_info.get("profileurl") if steam_info else None,
                steam_realname=steam_info.get("realname") if steam_info else None,
                avatar=steam_info.get("avatarfull") if steam_info else None,
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                last_login=datetime.utcnow(),
                email_verified=True,  # Steam users are pre-verified
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"New user created via Steam: {user.username} (Game ID: {steam_id})")

        # Create access token and session
        access_token = create_access_token(data={"sub": str(user.id)})

        # Import create_session from security
        from app.core.security import create_session

        session = create_session(db, user.id, access_token, request)

        # Ensure session is committed before redirect
        db.refresh(session)
        logger.info(f"Session created for user {user.id}: {session.id}")

        # Redirect to frontend with token
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.error(f"Steam callback error: {e}", exc_info=True)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/?error=steam_callback_error")


@router.get("/profile/{steam_id}")
async def get_steam_profile(steam_id: str):
    """Get Steam profile info (public endpoint)"""
    steam_info = await get_steam_user_info(steam_id)

    if not steam_info:
        raise HTTPException(status_code=404, detail="Steam profile not found")

    return {
        "steam_id": steam_id,
        "personaname": steam_info.get("personaname"),
        "avatar": steam_info.get("avatarfull"),
        "profileurl": steam_info.get("profileurl"),
        "realname": steam_info.get("realname"),
    }
