"""
OAuth2 Social Authentication
Steam, Discord, Google providers
"""

import logging
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class OAuth2Provider:
    """Base OAuth2 provider"""

    def __init__(self, name: str, client_id: str, client_secret: str,
                 authorize_url: str, token_url: str, userinfo_url: str):
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.userinfo_url = userinfo_url

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """Generate authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": self.get_scopes()
        }
        return f"{self.authorize_url}?{urlencode(params)}"

    def get_scopes(self) -> str:
        """Get OAuth scopes"""
        return ""

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri
                },
                headers={"Accept": "application/json"}
            )

            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange authorization code"
                )

            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from provider"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if response.status_code != 200:
                logger.error(f"Userinfo fetch failed: {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch user info"
                )

            return response.json()

    def normalize_user_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize provider-specific user data"""
        raise NotImplementedError("Subclasses must implement normalize_user_data")


class SteamOAuth2Provider(OAuth2Provider):
    """Steam OpenID Connect provider"""

    def __init__(self):
        super().__init__(
            name="steam",
            client_id="",  # Steam uses OpenID, not OAuth2
            client_secret="",
            authorize_url="https://steamcommunity.com/openid/login",
            token_url="",
            userinfo_url="https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
        )

    @property
    def api_key(self) -> str:
        """Get Steam API key at runtime"""
        return getattr(settings, 'STEAM_API_KEY', '')

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """Steam OpenID authorization URL"""
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": redirect_uri,
            "openid.realm": settings.BASE_URL,
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select"
        }
        return f"{self.authorize_url}?{urlencode(params)}"

    async def verify_openid_response(self, params: Dict[str, str]) -> Optional[str]:
        """Verify Steam OpenID response and extract Steam ID"""
        logger.info(f"Steam OpenID params: {list(params.keys())}")

        openid_mode = params.get("openid.mode")
        if openid_mode != "id_res":
            logger.error(f"Steam OpenID mode invalid: {openid_mode}")
            return None

        # Verify signature
        verify_params = {**params}
        verify_params["openid.mode"] = "check_authentication"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.authorize_url,
                    data=verify_params
                )
                logger.info(f"Steam verification response: {response.status_code} - {response.text[:200]}")

                if "is_valid:true" not in response.text:
                    logger.error(f"Steam OpenID verification failed: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Steam OpenID verification error: {type(e).__name__}: {str(e)}")
            return None

        # Extract Steam ID from claimed_id
        claimed_id = params.get("openid.claimed_id", "")
        logger.info(f"Steam claimed_id: {claimed_id}")

        if claimed_id:
            steam_id = claimed_id.split("/")[-1]
            logger.info(f"Extracted Steam ID: {steam_id}")
            return steam_id

        logger.error("No claimed_id in Steam OpenID response")
        return None

    async def get_user_info(self, steam_id: str) -> Dict[str, Any]:
        """Get Steam user info"""
        logger.info(f"Getting Steam user info for: {steam_id}")

        if not self.api_key:
            logger.error("Steam API key not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Steam API key not configured"
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.userinfo_url,
                    params={
                        "key": self.api_key,
                        "steamids": steam_id
                    }
                )
                logger.info(f"Steam API response: {response.status_code}")

                data = response.json()
                players = data.get("response", {}).get("players", [])

                if not players:
                    logger.error(f"Steam user not found: {steam_id}, response: {data}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Steam user not found"
                    )

                logger.info(f"Steam user found: {players[0].get('personaname')}")
                return players[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Steam API error: {type(e).__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Steam API error: {str(e)}"
            )

    def normalize_user_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Steam user data"""
        return {
            "provider": "steam",
            "provider_id": raw_data.get("steamid"),
            "username": raw_data.get("personaname"),
            "display_name": raw_data.get("personaname"),
            "avatar": raw_data.get("avatarfull"),
            "profile_url": raw_data.get("profileurl"),
            "email": None  # Steam doesn't provide email
        }


class DiscordOAuth2Provider(OAuth2Provider):
    """Discord OAuth2 provider"""

    def __init__(self):
        super().__init__(
            name="discord",
            client_id=getattr(settings, 'DISCORD_CLIENT_ID', ''),
            client_secret=getattr(settings, 'DISCORD_CLIENT_SECRET', ''),
            authorize_url="https://discord.com/api/oauth2/authorize",
            token_url="https://discord.com/api/oauth2/token",
            userinfo_url="https://discord.com/api/users/@me"
        )

    def get_scopes(self) -> str:
        """Discord scopes"""
        return "identify email"

    def normalize_user_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Discord user data"""
        avatar_hash = raw_data.get("avatar")
        discord_id = raw_data.get("id")

        avatar_url = None
        if avatar_hash:
            avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.png"

        return {
            "provider": "discord",
            "provider_id": discord_id,
            "username": raw_data.get("username"),
            "display_name": raw_data.get("global_name") or raw_data.get("username"),
            "avatar": avatar_url,
            "email": raw_data.get("email"),
            "verified": raw_data.get("verified", False)
        }


class GoogleOAuth2Provider(OAuth2Provider):
    """Google OAuth2 provider"""

    def __init__(self):
        super().__init__(
            name="google",
            client_id=getattr(settings, 'GOOGLE_CLIENT_ID', ''),
            client_secret=getattr(settings, 'GOOGLE_CLIENT_SECRET', ''),
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo"
        )

    def get_scopes(self) -> str:
        """Google scopes"""
        return "openid email profile"

    def normalize_user_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Google user data"""
        return {
            "provider": "google",
            "provider_id": raw_data.get("id"),
            "username": raw_data.get("email", "").split("@")[0],
            "display_name": raw_data.get("name"),
            "avatar": raw_data.get("picture"),
            "email": raw_data.get("email"),
            "verified": raw_data.get("verified_email", False)
        }


# Provider instances
steam_provider = SteamOAuth2Provider()
discord_provider = DiscordOAuth2Provider()
google_provider = GoogleOAuth2Provider()


def get_provider(provider_name: str) -> OAuth2Provider:
    """Get OAuth2 provider by name"""
    providers = {
        "steam": steam_provider,
        "discord": discord_provider,
        "google": google_provider
    }

    provider = providers.get(provider_name)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown OAuth provider: {provider_name}"
        )

    return provider


async def authenticate_with_provider(
    provider_name: str,
    code: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    openid_params: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Authenticate user with OAuth2 provider

    Returns normalized user data
    """
    provider = get_provider(provider_name)

    try:
        if provider_name == "steam":
            # Steam uses OpenID
            if not openid_params:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Steam requires OpenID parameters"
                )

            steam_id = await provider.verify_openid_response(openid_params)
            if not steam_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Steam authentication failed"
                )

            user_info = await provider.get_user_info(steam_id)

        else:
            # Standard OAuth2 flow
            if not code or not redirect_uri:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OAuth2 requires code and redirect_uri"
                )

            # Exchange code for token
            token_data = await provider.exchange_code(code, redirect_uri)
            access_token = token_data.get("access_token")

            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to obtain access token"
                )

            # Get user info
            user_info = await provider.get_user_info(access_token)

        # Normalize user data
        normalized_data = provider.normalize_user_data(user_info)

        return normalized_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )
