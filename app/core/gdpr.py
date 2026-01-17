"""
GDPR Compliance Tools
Data export, deletion, and anonymization for user privacy rights
"""

import logging
import json
import os
import zipfile
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.models.database import (
    User, GDPRRequest, Server, ServerAdmin, Plugin, Map,
    DownloadHistory, UserActivity, LoginHistory, BackupCode,
    TwoFactorAuth, OAuthAccount, SecurityEvent, DeviceSession
)
from app.core.audit_trail import AuditTrailManager, AuditAction

logger = logging.getLogger(__name__)


class GDPRManager:
    """GDPR compliance manager"""

    EXPORT_DIR = "/var/www/agtrmerkezi/gdpr_exports"

    @staticmethod
    def _ensure_export_dir():
        """Ensure export directory exists"""
        Path(GDPRManager.EXPORT_DIR).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _model_to_dict(instance) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dict"""
        if instance is None:
            return {}

        mapper = inspect(instance.__class__)
        data = {}

        for column in mapper.columns:
            value = getattr(instance, column.name)

            # Handle datetime serialization
            if isinstance(value, datetime):
                value = value.isoformat()

            # Skip sensitive fields
            if column.name in ['password_hash', 'secret', 'code_hash']:
                value = "[REDACTED]"

            data[column.name] = value

        return data

    @staticmethod
    async def export_user_data(db: Session, user_id: int) -> str:
        """
        Export all user data to JSON/ZIP

        Returns path to export file
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError(f"User {user_id} not found")

        GDPRManager._ensure_export_dir()

        # Prepare export data
        export_data = {
            "export_info": {
                "user_id": user_id,
                "exported_at": datetime.utcnow().isoformat(),
                "export_version": "1.0",
                "gdpr_compliant": True
            },
            "user_profile": GDPRManager._model_to_dict(user),
            "servers_owned": [],
            "servers_admin": [],
            "plugins_uploaded": [],
            "maps_uploaded": [],
            "downloads": [],
            "activities": [],
            "login_history": [],
            "security_events": [],
            "device_sessions": [],
            "two_factor_auth": None,
            "oauth_accounts": []
        }

        # Servers owned
        servers = db.query(Server).filter(Server.owner_id == user_id).all()
        export_data["servers_owned"] = [GDPRManager._model_to_dict(s) for s in servers]

        # Servers where user is admin
        server_admins = db.query(ServerAdmin).filter(ServerAdmin.user_id == user_id).all()
        export_data["servers_admin"] = [GDPRManager._model_to_dict(sa) for sa in server_admins]

        # Plugins
        plugins = db.query(Plugin).filter(Plugin.uploader_id == user_id).all()
        export_data["plugins_uploaded"] = [GDPRManager._model_to_dict(p) for p in plugins]

        # Maps
        maps = db.query(Map).filter(Map.uploader_id == user_id).all()
        export_data["maps_uploaded"] = [GDPRManager._model_to_dict(m) for m in maps]

        # Downloads
        downloads = db.query(DownloadHistory).filter(DownloadHistory.user_id == user_id).all()
        export_data["downloads"] = [GDPRManager._model_to_dict(d) for d in downloads]

        # Activities
        activities = db.query(UserActivity).filter(UserActivity.user_id == user_id).all()
        export_data["activities"] = [GDPRManager._model_to_dict(a) for a in activities]

        # Login history
        logins = db.query(LoginHistory).filter(LoginHistory.user_id == user_id).all()
        export_data["login_history"] = [GDPRManager._model_to_dict(l) for l in logins]

        # Security events
        events = db.query(SecurityEvent).filter(SecurityEvent.user_id == user_id).all()
        export_data["security_events"] = [GDPRManager._model_to_dict(e) for e in events]

        # Device sessions
        devices = db.query(DeviceSession).filter(DeviceSession.user_id == user_id).all()
        export_data["device_sessions"] = [GDPRManager._model_to_dict(d) for d in devices]

        # 2FA
        two_factor = db.query(TwoFactorAuth).filter(TwoFactorAuth.user_id == user_id).first()
        if two_factor:
            export_data["two_factor_auth"] = GDPRManager._model_to_dict(two_factor)

        # OAuth accounts
        oauth_accounts = db.query(OAuthAccount).filter(OAuthAccount.user_id == user_id).all()
        export_data["oauth_accounts"] = [GDPRManager._model_to_dict(o) for o in oauth_accounts]

        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"user_{user_id}_export_{timestamp}"

        # Save JSON
        json_path = os.path.join(GDPRManager.EXPORT_DIR, f"{filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        # Create ZIP with JSON
        zip_path = os.path.join(GDPRManager.EXPORT_DIR, f"{filename}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(json_path, f"{filename}.json")

        # Remove JSON (keep only ZIP)
        os.remove(json_path)

        logger.info(f"GDPR export created for user {user_id}: {zip_path}")

        return zip_path

    @staticmethod
    async def delete_user_data(
        db: Session,
        user_id: int,
        admin_user_id: int,
        keep_content: bool = False
    ) -> Dict[str, Any]:
        """
        Delete user data (GDPR right to erasure)

        Args:
            user_id: User to delete
            admin_user_id: Admin performing deletion
            keep_content: If True, keep plugins/maps but anonymize ownership

        Returns:
            Summary of deleted data
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError(f"User {user_id} not found")

        summary = {
            "user_id": user_id,
            "username": user.username,
            "deleted_at": datetime.utcnow().isoformat(),
            "keep_content": keep_content,
            "deleted_records": {}
        }

        # 1. Delete or anonymize plugins
        plugins = db.query(Plugin).filter(Plugin.uploader_id == user_id).all()
        if keep_content:
            for plugin in plugins:
                plugin.uploader_id = None  # Anonymize
            summary["deleted_records"]["plugins_anonymized"] = len(plugins)
        else:
            count = len(plugins)
            for plugin in plugins:
                db.delete(plugin)
            summary["deleted_records"]["plugins_deleted"] = count

        # 2. Delete or anonymize maps
        maps = db.query(Map).filter(Map.uploader_id == user_id).all()
        if keep_content:
            for map_obj in maps:
                map_obj.uploader_id = None  # Anonymize
            summary["deleted_records"]["maps_anonymized"] = len(maps)
        else:
            count = len(maps)
            for map_obj in maps:
                db.delete(map_obj)
            summary["deleted_records"]["maps_deleted"] = count

        # 3. Delete servers (CASCADE will handle server_admins, server_stats, etc.)
        servers = db.query(Server).filter(Server.owner_id == user_id).all()
        summary["deleted_records"]["servers_deleted"] = len(servers)
        for server in servers:
            db.delete(server)

        # 4. Delete server admin roles
        server_admins = db.query(ServerAdmin).filter(ServerAdmin.user_id == user_id).all()
        summary["deleted_records"]["server_admin_roles_deleted"] = len(server_admins)
        for sa in server_admins:
            db.delete(sa)

        # 5. Delete download history
        downloads = db.query(DownloadHistory).filter(DownloadHistory.user_id == user_id).all()
        summary["deleted_records"]["downloads_deleted"] = len(downloads)
        for download in downloads:
            db.delete(download)

        # 6. Delete activities
        activities = db.query(UserActivity).filter(UserActivity.user_id == user_id).all()
        summary["deleted_records"]["activities_deleted"] = len(activities)
        for activity in activities:
            db.delete(activity)

        # 7. Delete login history
        logins = db.query(LoginHistory).filter(LoginHistory.user_id == user_id).all()
        summary["deleted_records"]["login_history_deleted"] = len(logins)
        for login in logins:
            db.delete(login)

        # 8. Anonymize security events (keep for audit purposes)
        events = db.query(SecurityEvent).filter(SecurityEvent.user_id == user_id).all()
        summary["deleted_records"]["security_events_anonymized"] = len(events)
        for event in events:
            event.user_id = None

        # 9. Delete device sessions
        devices = db.query(DeviceSession).filter(DeviceSession.user_id == user_id).all()
        summary["deleted_records"]["device_sessions_deleted"] = len(devices)
        for device in devices:
            db.delete(device)

        # 10. Delete 2FA
        two_factor = db.query(TwoFactorAuth).filter(TwoFactorAuth.user_id == user_id).first()
        if two_factor:
            db.delete(two_factor)
            summary["deleted_records"]["2fa_deleted"] = 1

        # 11. Delete backup codes
        backup_codes = db.query(BackupCode).filter(BackupCode.user_id == user_id).all()
        summary["deleted_records"]["backup_codes_deleted"] = len(backup_codes)
        for code in backup_codes:
            db.delete(code)

        # 12. Delete OAuth accounts
        oauth_accounts = db.query(OAuthAccount).filter(OAuthAccount.user_id == user_id).all()
        summary["deleted_records"]["oauth_accounts_deleted"] = len(oauth_accounts)
        for oauth in oauth_accounts:
            db.delete(oauth)

        # 13. Finally, delete user account
        db.delete(user)

        # Commit all deletions
        db.commit()

        logger.critical(f"User {user_id} ({user.username}) data deleted by admin {admin_user_id}")

        return summary

    @staticmethod
    async def anonymize_user_data(
        db: Session,
        user_id: int,
        admin_user_id: int
    ) -> Dict[str, Any]:
        """
        Anonymize user data (GDPR alternative to deletion)

        Keeps content but removes personally identifiable information
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError(f"User {user_id} not found")

        original_username = user.username
        original_email = user.email

        # Generate anonymous identifiers
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        anon_username = f"deleted_user_{user_id}_{timestamp}"
        anon_email = f"deleted_{user_id}@anonymized.local"

        # Anonymize user profile
        user.username = anon_username
        user.email = anon_email
        user.first_name = "Deleted"
        user.last_name = "User"
        user.avatar_url = None
        user.bio = None
        user.discord_url = None
        user.steam_url = None
        user.youtube_url = None
        user.last_ip = None

        # Disable account
        user.is_active = False

        # Delete sensitive data
        two_factor = db.query(TwoFactorAuth).filter(TwoFactorAuth.user_id == user_id).first()
        if two_factor:
            db.delete(two_factor)

        db.query(BackupCode).filter(BackupCode.user_id == user_id).delete()
        db.query(OAuthAccount).filter(OAuthAccount.user_id == user_id).delete()
        db.query(LoginHistory).filter(LoginHistory.user_id == user_id).delete()
        db.query(DeviceSession).filter(DeviceSession.user_id == user_id).delete()

        # Anonymize security events
        db.query(SecurityEvent).filter(
            SecurityEvent.user_id == user_id
        ).update({"user_id": None})

        db.commit()

        summary = {
            "user_id": user_id,
            "original_username": original_username,
            "original_email": original_email,
            "anonymized_username": anon_username,
            "anonymized_at": datetime.utcnow().isoformat(),
            "content_preserved": True
        }

        logger.warning(f"User {user_id} ({original_username}) anonymized by admin {admin_user_id}")

        return summary

    @staticmethod
    async def create_gdpr_request(
        db: Session,
        user_id: int,
        request_type: str,
        request_data: Optional[Dict] = None
    ) -> GDPRRequest:
        """
        Create GDPR request

        Args:
            user_id: User making request
            request_type: export, delete, anonymize
            request_data: Additional request data

        Returns:
            GDPRRequest instance
        """
        request = GDPRRequest(
            user_id=user_id,
            request_type=request_type,
            status="pending",
            request_data=request_data
        )

        db.add(request)
        db.commit()
        db.refresh(request)

        logger.info(f"GDPR {request_type} request created for user {user_id}")

        return request

    @staticmethod
    async def process_gdpr_request(
        db: Session,
        request_id: int,
        admin_user_id: int
    ) -> Dict[str, Any]:
        """
        Process pending GDPR request

        Returns processing result
        """
        request = db.query(GDPRRequest).filter(GDPRRequest.id == request_id).first()

        if not request:
            raise ValueError(f"GDPR request {request_id} not found")

        if request.status != "pending":
            raise ValueError(f"Request already {request.status}")

        # Update status
        request.status = "processing"
        request.processed_by = admin_user_id
        request.processed_at = datetime.utcnow()
        db.commit()

        result = {}

        try:
            if request.request_type == "export":
                # Export data
                export_path = await GDPRManager.export_user_data(db, request.user_id)
                request.result_file_path = export_path
                result["export_path"] = export_path

            elif request.request_type == "delete":
                # Delete data
                keep_content = request.request_data.get("keep_content", False) if request.request_data else False
                summary = await GDPRManager.delete_user_data(
                    db,
                    request.user_id,
                    admin_user_id,
                    keep_content=keep_content
                )
                result["deletion_summary"] = summary

            elif request.request_type == "anonymize":
                # Anonymize data
                summary = await GDPRManager.anonymize_user_data(
                    db,
                    request.user_id,
                    admin_user_id
                )
                result["anonymization_summary"] = summary

            # Mark as completed
            request.status = "completed"
            request.completed_at = datetime.utcnow()
            db.commit()

            logger.info(f"GDPR request {request_id} completed by admin {admin_user_id}")

        except Exception as e:
            # Mark as failed
            request.status = "failed"
            db.commit()

            logger.error(f"GDPR request {request_id} failed: {e}")
            raise

        return result

    @staticmethod
    def get_user_requests(db: Session, user_id: int) -> List[GDPRRequest]:
        """Get all GDPR requests for user"""
        return db.query(GDPRRequest).filter(
            GDPRRequest.user_id == user_id
        ).order_by(GDPRRequest.created_at.desc()).all()

    @staticmethod
    def get_pending_requests(db: Session) -> List[GDPRRequest]:
        """Get all pending GDPR requests (for admin)"""
        return db.query(GDPRRequest).filter(
            GDPRRequest.status == "pending"
        ).order_by(GDPRRequest.created_at.asc()).all()


# Global GDPR manager instance
gdpr_manager = GDPRManager()
