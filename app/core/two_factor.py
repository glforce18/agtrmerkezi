"""
Two-Factor Authentication (2FA)
TOTP-based 2FA with backup codes
"""

import logging
import secrets
from datetime import datetime
from typing import List, Optional, Tuple

import pyotp
import qrcode
import qrcode.image.svg
from io import BytesIO
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.database import User, TwoFactorAuth, BackupCode

logger = logging.getLogger(__name__)


class TwoFactorManager:
    """2FA Management"""

    @staticmethod
    def generate_secret() -> str:
        """Generate new TOTP secret"""
        return pyotp.random_base32()

    @staticmethod
    def generate_provisioning_uri(secret: str, username: str, issuer: str = "AGTR Merkezi") -> str:
        """Generate TOTP provisioning URI for QR code"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=username,
            issuer_name=issuer
        )

    @staticmethod
    def generate_qr_code(provisioning_uri: str, format: str = "png") -> bytes:
        """
        Generate QR code image

        Args:
            provisioning_uri: TOTP provisioning URI
            format: 'png' or 'svg'

        Returns:
            QR code image bytes
        """
        if format == "svg":
            factory = qrcode.image.svg.SvgPathImage
            img = qrcode.make(provisioning_uri, image_factory=factory)
            buffer = BytesIO()
            img.save(buffer)
            return buffer.getvalue()
        else:
            # PNG format
            img = qrcode.make(provisioning_uri)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return buffer.getvalue()

    @staticmethod
    def verify_totp(secret: str, token: str, window: int = 1) -> bool:
        """
        Verify TOTP token

        Args:
            secret: TOTP secret
            token: 6-digit code from authenticator app
            window: Time window to allow (default 1 = ±30 seconds)

        Returns:
            True if valid, False otherwise
        """
        if not token or len(token) != 6 or not token.isdigit():
            return False

        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=window)

    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        Generate backup codes

        Args:
            count: Number of codes to generate (default 10)

        Returns:
            List of backup codes (format: XXXX-XXXX-XXXX)
        """
        codes = []
        for _ in range(count):
            # Generate 12-character code
            code = secrets.token_hex(6).upper()
            # Format as XXXX-XXXX-XXXX
            formatted = f"{code[0:4]}-{code[4:8]}-{code[8:12]}"
            codes.append(formatted)

        return codes

    @staticmethod
    def enable_2fa(db: Session, user: User) -> Tuple[str, List[str], bytes]:
        """
        Enable 2FA for user

        Returns:
            (secret, backup_codes, qr_code_png)
        """
        # Generate secret
        secret = TwoFactorManager.generate_secret()

        # Generate backup codes
        backup_codes = TwoFactorManager.generate_backup_codes()

        # Create 2FA record
        two_factor = TwoFactorAuth(
            user_id=user.id,
            secret=secret,
            is_enabled=False,  # User must verify before enabling
            backup_codes_generated=datetime.utcnow()
        )
        db.add(two_factor)

        # Store backup codes (hashed)
        for code in backup_codes:
            backup_code = BackupCode(
                user_id=user.id,
                code_hash=hash_password(code),  # Hash for security
                is_used=False
            )
            db.add(backup_code)

        db.commit()

        # Generate QR code
        provisioning_uri = TwoFactorManager.generate_provisioning_uri(
            secret,
            user.username
        )
        qr_code = TwoFactorManager.generate_qr_code(provisioning_uri)

        logger.info(f"2FA setup initiated for user {user.id}")

        return secret, backup_codes, qr_code

    @staticmethod
    def verify_and_enable_2fa(db: Session, user: User, token: str) -> bool:
        """
        Verify TOTP token and enable 2FA

        Returns:
            True if verified and enabled, False otherwise
        """
        two_factor = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id
        ).first()

        if not two_factor or not two_factor.secret:
            return False

        # Verify token
        if not TwoFactorManager.verify_totp(two_factor.secret, token):
            logger.warning(f"Invalid 2FA verification attempt for user {user.id}")
            return False

        # Enable 2FA
        two_factor.is_enabled = True
        two_factor.verified_at = datetime.utcnow()
        db.commit()

        logger.info(f"2FA enabled for user {user.id}")

        return True

    @staticmethod
    def disable_2fa(db: Session, user: User):
        """Disable 2FA for user"""
        two_factor = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id
        ).first()

        if two_factor:
            db.delete(two_factor)

        # Delete backup codes
        db.query(BackupCode).filter(
            BackupCode.user_id == user.id
        ).delete()

        db.commit()

        logger.info(f"2FA disabled for user {user.id}")

    @staticmethod
    def verify_2fa_login(db: Session, user: User, token: str) -> bool:
        """
        Verify 2FA during login

        Supports both TOTP and backup codes

        Returns:
            True if valid, False otherwise
        """
        two_factor = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id,
            TwoFactorAuth.is_enabled == True
        ).first()

        if not two_factor:
            return False

        # Check if it's a backup code (format: XXXX-XXXX-XXXX)
        if "-" in token:
            return TwoFactorManager.verify_backup_code(db, user, token)

        # Verify TOTP
        if TwoFactorManager.verify_totp(two_factor.secret, token):
            # Update last used
            two_factor.last_used_at = datetime.utcnow()
            db.commit()
            return True

        logger.warning(f"Invalid 2FA login attempt for user {user.id}")
        return False

    @staticmethod
    def verify_backup_code(db: Session, user: User, code: str) -> bool:
        """
        Verify and consume backup code

        Returns:
            True if valid, False otherwise
        """
        # Get all unused backup codes
        backup_codes = db.query(BackupCode).filter(
            BackupCode.user_id == user.id,
            BackupCode.is_used == False
        ).all()

        for backup_code in backup_codes:
            if verify_password(code, backup_code.code_hash):
                # Mark as used
                backup_code.is_used = True
                backup_code.used_at = datetime.utcnow()
                db.commit()

                logger.info(f"Backup code used for user {user.id}")
                return True

        logger.warning(f"Invalid backup code attempt for user {user.id}")
        return False

    @staticmethod
    def get_backup_codes_status(db: Session, user: User) -> dict:
        """
        Get backup codes status

        Returns:
            {
                "total": int,
                "used": int,
                "remaining": int
            }
        """
        backup_codes = db.query(BackupCode).filter(
            BackupCode.user_id == user.id
        ).all()

        total = len(backup_codes)
        used = sum(1 for code in backup_codes if code.is_used)
        remaining = total - used

        return {
            "total": total,
            "used": used,
            "remaining": remaining
        }

    @staticmethod
    def regenerate_backup_codes(db: Session, user: User) -> List[str]:
        """
        Regenerate backup codes

        Deletes old codes and generates new ones

        Returns:
            List of new backup codes
        """
        # Delete old codes
        db.query(BackupCode).filter(
            BackupCode.user_id == user.id
        ).delete()

        # Generate new codes
        new_codes = TwoFactorManager.generate_backup_codes()

        # Store new codes
        for code in new_codes:
            backup_code = BackupCode(
                user_id=user.id,
                code_hash=hash_password(code),
                is_used=False
            )
            db.add(backup_code)

        # Update 2FA record
        two_factor = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id
        ).first()

        if two_factor:
            two_factor.backup_codes_generated = datetime.utcnow()

        db.commit()

        logger.info(f"Backup codes regenerated for user {user.id}")

        return new_codes

    @staticmethod
    def is_2fa_enabled(db: Session, user: User) -> bool:
        """Check if 2FA is enabled for user"""
        two_factor = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user.id,
            TwoFactorAuth.is_enabled == True
        ).first()

        return two_factor is not None


# Global instance
two_factor_manager = TwoFactorManager()
