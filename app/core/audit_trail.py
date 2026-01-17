"""
Admin Audit Trail System
Comprehensive logging of all administrative actions
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import Session
from fastapi import Request

from app.core.database import Base
from app.core.geolocation import GeolocationService

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Admin actions to audit"""
    # User Management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_BAN = "user_ban"
    USER_UNBAN = "user_unban"
    USER_ROLE_CHANGE = "user_role_change"
    USER_PASSWORD_RESET = "user_password_reset"

    # Server Management
    SERVER_CREATE = "server_create"
    SERVER_UPDATE = "server_update"
    SERVER_DELETE = "server_delete"
    SERVER_RESTART = "server_restart"
    SERVER_MAINTENANCE = "server_maintenance"

    # Content Moderation
    PLUGIN_APPROVE = "plugin_approve"
    PLUGIN_REJECT = "plugin_reject"
    PLUGIN_DELETE = "plugin_delete"
    MAP_APPROVE = "map_approve"
    MAP_REJECT = "map_reject"
    MAP_DELETE = "map_delete"
    COMMENT_DELETE = "comment_delete"
    REPORT_RESOLVE = "report_resolve"

    # System Configuration
    CONFIG_UPDATE = "config_update"
    FEATURE_TOGGLE = "feature_toggle"
    ANNOUNCEMENT_CREATE = "announcement_create"
    ANNOUNCEMENT_UPDATE = "announcement_update"
    ANNOUNCEMENT_DELETE = "announcement_delete"

    # Security Actions
    IP_BAN = "ip_ban"
    IP_UNBAN = "ip_unban"
    SECURITY_EVENT_RESOLVE = "security_event_resolve"
    RATE_LIMIT_RESET = "rate_limit_reset"
    SESSION_TERMINATE = "session_terminate"

    # GDPR Actions
    GDPR_EXPORT = "gdpr_export"
    GDPR_DELETE = "gdpr_delete"
    GDPR_ANONYMIZE = "gdpr_anonymize"

    # Other
    BACKUP_CREATE = "backup_create"
    BACKUP_RESTORE = "backup_restore"
    DATABASE_MIGRATION = "database_migration"
    CACHE_CLEAR = "cache_clear"


class AuditSeverity(str, Enum):
    """Severity levels for audit events"""
    INFO = "info"              # Normal operations
    WARNING = "warning"        # Potentially sensitive actions
    CRITICAL = "critical"      # High-impact actions (deletions, bans)
    EMERGENCY = "emergency"    # System-wide impacts


# Audit Log Model
class AuditLog(Base):
    """Audit log database model"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, nullable=False, index=True)
    admin_username = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    target_type = Column(String(50), nullable=True)  # user, server, plugin, etc.
    target_id = Column(Integer, nullable=True)
    target_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # Before/after values
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    geo_location = Column(JSON, nullable=True)
    audit_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog {self.id}: {self.admin_username} - {self.action}>"


class AuditTrailManager:
    """Audit trail manager"""

    # Severity mapping
    SEVERITY_MAP = {
        # Critical actions
        AuditAction.USER_DELETE: AuditSeverity.CRITICAL,
        AuditAction.USER_BAN: AuditSeverity.CRITICAL,
        AuditAction.SERVER_DELETE: AuditSeverity.CRITICAL,
        AuditAction.PLUGIN_DELETE: AuditSeverity.CRITICAL,
        AuditAction.MAP_DELETE: AuditSeverity.CRITICAL,
        AuditAction.IP_BAN: AuditSeverity.CRITICAL,
        AuditAction.GDPR_DELETE: AuditSeverity.CRITICAL,
        AuditAction.BACKUP_RESTORE: AuditSeverity.EMERGENCY,
        AuditAction.DATABASE_MIGRATION: AuditSeverity.EMERGENCY,

        # Warning actions
        AuditAction.USER_UPDATE: AuditSeverity.WARNING,
        AuditAction.USER_ROLE_CHANGE: AuditSeverity.WARNING,
        AuditAction.USER_PASSWORD_RESET: AuditSeverity.WARNING,
        AuditAction.CONFIG_UPDATE: AuditSeverity.WARNING,
        AuditAction.GDPR_EXPORT: AuditSeverity.WARNING,

        # Default to INFO for others
    }

    @staticmethod
    async def log_action(
        db: Session,
        admin_user_id: int,
        admin_username: str,
        action: AuditAction,
        request: Optional[Request] = None,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        target_name: Optional[str] = None,
        description: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        audit_metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Log admin action to audit trail

        Args:
            db: Database session
            admin_user_id: ID of admin performing action
            admin_username: Username of admin
            action: AuditAction enum
            request: FastAPI request object (for IP, user agent)
            target_type: Type of target (user, server, plugin, etc.)
            target_id: ID of target
            target_name: Name/title of target
            description: Human-readable description
            changes: Dict of before/after values
            audit_metadata: Additional data

        Returns:
            Created AuditLog instance
        """
        # Determine severity
        severity = AuditTrailManager.SEVERITY_MAP.get(action, AuditSeverity.INFO)

        # Extract request data
        ip_address = None
        user_agent = None
        geo_location = None

        if request:
            ip_address = GeolocationService.get_client_ip(request)
            user_agent = request.headers.get("User-Agent")

            # Get geolocation
            geo = await GeolocationService.get_location(ip_address)
            if geo:
                geo_location = {
                    "country": geo.get("country"),
                    "countryCode": geo.get("countryCode"),
                    "city": geo.get("city"),
                    "region": geo.get("regionName")
                }

        # Create audit log
        audit_log = AuditLog(
            admin_user_id=admin_user_id,
            admin_username=admin_username,
            action=action.value,
            severity=severity.value,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            description=description,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            geo_location=geo_location,
            audit_metadata=audit_metadata
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        # Log to application logger
        log_message = (
            f"AUDIT: {admin_username} ({admin_user_id}) performed {action.value} "
            f"on {target_type} {target_id} ({target_name}) from {ip_address}"
        )

        if severity == AuditSeverity.CRITICAL or severity == AuditSeverity.EMERGENCY:
            logger.critical(log_message)
        elif severity == AuditSeverity.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return audit_log

    @staticmethod
    def get_logs(
        db: Session,
        admin_user_id: Optional[int] = None,
        action: Optional[AuditAction] = None,
        severity: Optional[AuditSeverity] = None,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Query audit logs with filters

        Returns list of AuditLog instances
        """
        query = db.query(AuditLog)

        # Apply filters
        if admin_user_id:
            query = query.filter(AuditLog.admin_user_id == admin_user_id)

        if action:
            query = query.filter(AuditLog.action == action.value)

        if severity:
            query = query.filter(AuditLog.severity == severity.value)

        if target_type:
            query = query.filter(AuditLog.target_type == target_type)

        if target_id:
            query = query.filter(AuditLog.target_id == target_id)

        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)

        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        # Order by most recent first
        query = query.order_by(AuditLog.created_at.desc())

        # Pagination
        logs = query.limit(limit).offset(offset).all()

        return logs

    @staticmethod
    def get_user_action_history(
        db: Session,
        user_id: int,
        limit: int = 50
    ) -> List[AuditLog]:
        """
        Get all admin actions performed on a specific user

        Useful for viewing user's moderation history
        """
        logs = db.query(AuditLog).filter(
            AuditLog.target_type == "user",
            AuditLog.target_id == user_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()

        return logs

    @staticmethod
    def get_admin_activity_stats(
        db: Session,
        admin_user_id: int
    ) -> Dict[str, Any]:
        """
        Get activity statistics for an admin

        Returns:
            {
                "total_actions": int,
                "actions_by_type": {...},
                "actions_by_severity": {...},
                "first_action": datetime,
                "last_action": datetime
            }
        """
        from sqlalchemy import func

        logs = db.query(AuditLog).filter(
            AuditLog.admin_user_id == admin_user_id
        ).all()

        if not logs:
            return {
                "total_actions": 0,
                "actions_by_type": {},
                "actions_by_severity": {},
                "first_action": None,
                "last_action": None
            }

        # Count by action type
        actions_by_type = {}
        actions_by_severity = {}

        for log in logs:
            actions_by_type[log.action] = actions_by_type.get(log.action, 0) + 1
            actions_by_severity[log.severity] = actions_by_severity.get(log.severity, 0) + 1

        return {
            "total_actions": len(logs),
            "actions_by_type": actions_by_type,
            "actions_by_severity": actions_by_severity,
            "first_action": logs[-1].created_at if logs else None,
            "last_action": logs[0].created_at if logs else None
        }

    @staticmethod
    def export_logs_csv(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """
        Export audit logs to CSV format

        Returns CSV string
        """
        import csv
        from io import StringIO

        logs = AuditTrailManager.get_logs(
            db,
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "ID", "Timestamp", "Admin ID", "Admin Username", "Action",
            "Severity", "Target Type", "Target ID", "Target Name",
            "Description", "IP Address", "Country", "City"
        ])

        # Data
        for log in logs:
            writer.writerow([
                log.id,
                log.created_at.isoformat(),
                log.admin_user_id,
                log.admin_username,
                log.action,
                log.severity,
                log.target_type or "",
                log.target_id or "",
                log.target_name or "",
                log.description or "",
                log.ip_address or "",
                log.geo_location.get("country", "") if log.geo_location else "",
                log.geo_location.get("city", "") if log.geo_location else ""
            ])

        return output.getvalue()


# Decorator for automatic audit logging
def audit_action(
    action: AuditAction,
    target_type: Optional[str] = None,
    get_target_id: Optional[callable] = None,
    get_target_name: Optional[callable] = None,
    description: Optional[str] = None
):
    """
    Decorator for automatic audit logging

    Usage:
        @audit_action(
            action=AuditAction.USER_BAN,
            target_type="user",
            get_target_id=lambda kwargs: kwargs.get("user_id"),
            get_target_name=lambda kwargs: kwargs.get("username"),
            description="User banned by admin"
        )
        async def ban_user(user_id: int, username: str, admin: User, db: Session):
            # ... ban logic ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Execute function first
            result = await func(*args, **kwargs)

            # Extract necessary data
            db = kwargs.get("db")
            admin = kwargs.get("admin") or kwargs.get("current_user")
            request = kwargs.get("request")

            if db and admin:
                target_id = get_target_id(kwargs) if get_target_id else None
                target_name = get_target_name(kwargs) if get_target_name else None

                # Log action
                await AuditTrailManager.log_action(
                    db=db,
                    admin_user_id=admin.id,
                    admin_username=admin.username,
                    action=action,
                    request=request,
                    target_type=target_type,
                    target_id=target_id,
                    target_name=target_name,
                    description=description
                )

            return result

        return wrapper
    return decorator


# Global audit manager instance
audit_manager = AuditTrailManager()
