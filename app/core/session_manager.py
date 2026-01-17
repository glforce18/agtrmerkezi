"""
Session Management & Device Tracking
Comprehensive session lifecycle and trusted device management
"""

import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from user_agents import parse

from sqlalchemy.orm import Session
from fastapi import Request

from app.core.redis_manager import redis_manager
from app.core.geolocation import GeolocationService
from app.models.database import DeviceSession, LoginHistory

logger = logging.getLogger(__name__)


class DeviceFingerprint:
    """Device fingerprinting utilities"""

    @staticmethod
    def generate_device_id(request: Request) -> str:
        """
        Generate unique device ID based on browser fingerprint

        Args:
            request: FastAPI request

        Returns:
            Device ID hash
        """
        # Collect fingerprint components
        user_agent = request.headers.get("User-Agent", "")
        accept_language = request.headers.get("Accept-Language", "")
        accept_encoding = request.headers.get("Accept-Encoding", "")

        # Create fingerprint string
        fingerprint = f"{user_agent}|{accept_language}|{accept_encoding}"

        # Hash to create device ID
        device_id = hashlib.sha256(fingerprint.encode()).hexdigest()

        return device_id

    @staticmethod
    def parse_user_agent(user_agent: str) -> Dict[str, Any]:
        """
        Parse user agent string

        Returns:
            {
                "device_type": "mobile|desktop|tablet|bot",
                "os": "Windows 10",
                "browser": "Chrome 120",
                "is_mobile": bool,
                "is_tablet": bool,
                "is_bot": bool
            }
        """
        ua = parse(user_agent)

        device_type = "desktop"
        if ua.is_mobile:
            device_type = "mobile"
        elif ua.is_tablet:
            device_type = "tablet"
        elif ua.is_bot:
            device_type = "bot"

        return {
            "device_type": device_type,
            "os": f"{ua.os.family} {ua.os.version_string}",
            "browser": f"{ua.browser.family} {ua.browser.version_string}",
            "is_mobile": ua.is_mobile,
            "is_tablet": ua.is_tablet,
            "is_bot": ua.is_bot,
            "device_name": DeviceFingerprint.generate_device_name(ua)
        }

    @staticmethod
    def generate_device_name(ua) -> str:
        """Generate human-readable device name"""
        if ua.is_mobile:
            return f"{ua.device.brand or 'Mobile'} {ua.device.model or 'Device'}"
        elif ua.is_tablet:
            return f"{ua.device.brand or 'Tablet'} {ua.device.model or 'Device'}"
        else:
            return f"{ua.os.family} - {ua.browser.family}"


class SessionManager:
    """Session lifecycle management"""

    # Session TTL
    SESSION_TTL = 86400 * 30  # 30 days
    REMEMBER_ME_TTL = 86400 * 90  # 90 days

    # Session key prefixes
    SESSION_KEY_PREFIX = "session:"
    USER_SESSIONS_PREFIX = "user_sessions:"

    @staticmethod
    def _get_session_key(session_id: str) -> str:
        """Get Redis key for session"""
        return f"{SessionManager.SESSION_KEY_PREFIX}{session_id}"

    @staticmethod
    def _get_user_sessions_key(user_id: int) -> str:
        """Get Redis key for user's active sessions"""
        return f"{SessionManager.USER_SESSIONS_PREFIX}{user_id}"

    @staticmethod
    async def create_session(
        user_id: int,
        request: Request,
        remember_me: bool = False
    ) -> str:
        """
        Create new session

        Args:
            user_id: User ID
            request: FastAPI request
            remember_me: Extend session TTL

        Returns:
            Session ID
        """
        # Generate session ID
        session_id = secrets.token_urlsafe(32)

        # Parse device info
        user_agent = request.headers.get("User-Agent", "")
        device_info = DeviceFingerprint.parse_user_agent(user_agent)

        # Get IP and location
        ip_address = GeolocationService.get_client_ip(request)
        geo = await GeolocationService.get_location(ip_address)

        # Session data
        session_data = {
            "user_id": user_id,
            "session_id": session_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "device_type": device_info["device_type"],
            "os": device_info["os"],
            "browser": device_info["browser"],
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "geo_location": {
                "country": geo.get("country") if geo else None,
                "city": geo.get("city") if geo else None
            },
            "remember_me": remember_me
        }

        # Store session
        ttl = SessionManager.REMEMBER_ME_TTL if remember_me else SessionManager.SESSION_TTL
        session_key = SessionManager._get_session_key(session_id)
        await redis_manager.set(session_key, str(session_data), ttl=ttl)

        # Add to user's active sessions
        user_sessions_key = SessionManager._get_user_sessions_key(user_id)
        await redis_manager.sadd(user_sessions_key, session_id)
        await redis_manager.expire(user_sessions_key, SessionManager.REMEMBER_ME_TTL)

        logger.info(f"Session created for user {user_id}: {session_id}")

        return session_id

    @staticmethod
    async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        session_key = SessionManager._get_session_key(session_id)
        session_data = await redis_manager.get(session_key)

        if session_data:
            return eval(session_data)  # Convert string back to dict

        return None

    @staticmethod
    async def update_session_activity(session_id: str):
        """Update last activity timestamp"""
        session_data = await SessionManager.get_session(session_id)

        if session_data:
            session_data["last_activity"] = datetime.utcnow().isoformat()

            session_key = SessionManager._get_session_key(session_id)
            ttl = SessionManager.REMEMBER_ME_TTL if session_data.get("remember_me") else SessionManager.SESSION_TTL
            await redis_manager.set(session_key, str(session_data), ttl=ttl)

    @staticmethod
    async def delete_session(session_id: str):
        """Delete session"""
        # Get session to find user_id
        session_data = await SessionManager.get_session(session_id)

        if session_data:
            user_id = session_data["user_id"]

            # Remove from user's sessions
            user_sessions_key = SessionManager._get_user_sessions_key(user_id)
            await redis_manager.srem(user_sessions_key, session_id)

        # Delete session
        session_key = SessionManager._get_session_key(session_id)
        await redis_manager.delete(session_key)

        logger.info(f"Session deleted: {session_id}")

    @staticmethod
    async def get_user_sessions(user_id: int) -> List[Dict[str, Any]]:
        """Get all active sessions for user"""
        user_sessions_key = SessionManager._get_user_sessions_key(user_id)
        session_ids = await redis_manager.smembers(user_sessions_key)

        sessions = []
        for session_id in session_ids:
            session_data = await SessionManager.get_session(session_id)
            if session_data:
                sessions.append(session_data)

        return sessions

    @staticmethod
    async def delete_all_user_sessions(user_id: int, except_session: Optional[str] = None):
        """
        Delete all sessions for user

        Args:
            user_id: User ID
            except_session: Optional session to keep (current session)
        """
        sessions = await SessionManager.get_user_sessions(user_id)

        for session in sessions:
            session_id = session["session_id"]

            # Skip current session if specified
            if except_session and session_id == except_session:
                continue

            await SessionManager.delete_session(session_id)

        logger.info(f"All sessions deleted for user {user_id}")

    @staticmethod
    async def get_session_count(user_id: int) -> int:
        """Get number of active sessions for user"""
        user_sessions_key = SessionManager._get_user_sessions_key(user_id)
        count = await redis_manager.scard(user_sessions_key)
        return count


class DeviceManager:
    """Trusted device management"""

    @staticmethod
    async def register_device(
        db: Session,
        user_id: int,
        request: Request,
        trust_device: bool = False
    ) -> DeviceSession:
        """
        Register device session

        Args:
            db: Database session
            user_id: User ID
            request: FastAPI request
            trust_device: Mark device as trusted

        Returns:
            DeviceSession instance
        """
        # Generate device ID
        device_id = DeviceFingerprint.generate_device_id(request)

        # Check if device exists
        device = db.query(DeviceSession).filter(
            DeviceSession.user_id == user_id,
            DeviceSession.device_id == device_id
        ).first()

        # Parse device info
        user_agent = request.headers.get("User-Agent", "")
        device_info = DeviceFingerprint.parse_user_agent(user_agent)
        ip_address = GeolocationService.get_client_ip(request)

        if device:
            # Update existing device
            device.last_active_at = datetime.utcnow()
            device.ip_address = ip_address

            if trust_device and not device.is_trusted:
                device.is_trusted = True
                device.trusted_at = datetime.utcnow()

        else:
            # Create new device
            device = DeviceSession(
                user_id=user_id,
                device_id=device_id,
                device_name=device_info["device_name"],
                device_type=device_info["device_type"],
                os=device_info["os"],
                browser=device_info["browser"],
                ip_address=ip_address,
                is_trusted=trust_device,
                trusted_at=datetime.utcnow() if trust_device else None
            )
            db.add(device)

        db.commit()
        db.refresh(device)

        logger.info(f"Device registered for user {user_id}: {device_id} (trusted: {trust_device})")

        return device

    @staticmethod
    def get_user_devices(db: Session, user_id: int) -> List[DeviceSession]:
        """Get all devices for user"""
        devices = db.query(DeviceSession).filter(
            DeviceSession.user_id == user_id
        ).order_by(DeviceSession.last_active_at.desc()).all()

        return devices

    @staticmethod
    def is_device_trusted(db: Session, user_id: int, request: Request) -> bool:
        """Check if current device is trusted"""
        device_id = DeviceFingerprint.generate_device_id(request)

        device = db.query(DeviceSession).filter(
            DeviceSession.user_id == user_id,
            DeviceSession.device_id == device_id,
            DeviceSession.is_trusted == True
        ).first()

        return device is not None

    @staticmethod
    def revoke_device_trust(db: Session, device_id: int):
        """Revoke trust from device"""
        device = db.query(DeviceSession).filter(DeviceSession.id == device_id).first()

        if device:
            device.is_trusted = False
            device.trusted_at = None
            db.commit()

            logger.info(f"Device trust revoked: {device_id}")

    @staticmethod
    def delete_device(db: Session, device_id: int):
        """Delete device"""
        device = db.query(DeviceSession).filter(DeviceSession.id == device_id).first()

        if device:
            db.delete(device)
            db.commit()

            logger.info(f"Device deleted: {device_id}")


class LoginHistoryManager:
    """Login history tracking"""

    @staticmethod
    async def record_login(
        db: Session,
        user_id: int,
        request: Request,
        login_type: str = "password",
        provider: Optional[str] = None,
        is_successful: bool = True,
        failure_reason: Optional[str] = None
    ):
        """
        Record login attempt

        Args:
            db: Database session
            user_id: User ID
            request: FastAPI request
            login_type: password, oauth, 2fa
            provider: OAuth provider (if applicable)
            is_successful: Login success status
            failure_reason: Reason for failure (if applicable)
        """
        # Parse device info
        user_agent = request.headers.get("User-Agent", "")
        device_info = DeviceFingerprint.parse_user_agent(user_agent)

        # Get IP and location
        ip_address = GeolocationService.get_client_ip(request)
        geo = await GeolocationService.get_location(ip_address)

        geo_location = None
        if geo:
            geo_location = {
                "country": geo.get("country"),
                "countryCode": geo.get("countryCode"),
                "city": geo.get("city"),
                "region": geo.get("regionName")
            }

        # Create login history record
        login = LoginHistory(
            user_id=user_id,
            login_type=login_type,
            provider=provider,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_info["device_type"],
            os=device_info["os"],
            browser=device_info["browser"],
            geo_location=geo_location,
            is_successful=is_successful,
            failure_reason=failure_reason
        )

        db.add(login)
        db.commit()

        if is_successful:
            logger.info(f"Login recorded for user {user_id} via {login_type}")
        else:
            logger.warning(f"Failed login for user {user_id}: {failure_reason}")

    @staticmethod
    def get_user_login_history(
        db: Session,
        user_id: int,
        limit: int = 50
    ) -> List[LoginHistory]:
        """Get login history for user"""
        history = db.query(LoginHistory).filter(
            LoginHistory.user_id == user_id
        ).order_by(LoginHistory.created_at.desc()).limit(limit).all()

        return history

    @staticmethod
    def get_failed_login_count(
        db: Session,
        user_id: int,
        since: datetime
    ) -> int:
        """Get number of failed logins since timestamp"""
        count = db.query(LoginHistory).filter(
            LoginHistory.user_id == user_id,
            LoginHistory.is_successful == False,
            LoginHistory.created_at >= since
        ).count()

        return count


# Global instances
session_manager = SessionManager()
device_manager = DeviceManager()
login_history_manager = LoginHistoryManager()
