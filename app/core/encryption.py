# ============================================
# AGTR v6.0 - Encryption & Security
# Dosya: app/core/encryption.py
# Content encryption, device ID validation, secure tokens
# ============================================

import base64
import hashlib
import hmac
import secrets
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


class EncryptionService:
    """
    Encryption service for sensitive data
    Uses Fernet (symmetric encryption) from cryptography library
    """

    def __init__(self, secret_key: str):
        """
        Initialize encryption service

        Args:
            secret_key: Base secret key (will be hashed to generate Fernet key)
        """
        # Generate Fernet key from secret
        key_hash = hashlib.sha256(secret_key.encode()).digest()
        self.fernet_key = base64.urlsafe_b64encode(key_hash)
        self.cipher = Fernet(self.fernet_key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext

        Args:
            plaintext: Text to encrypt

        Returns:
            Encrypted text (base64 encoded)
        """
        if not plaintext:
            return ""

        encrypted_bytes = self.cipher.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted_bytes).decode()

    def decrypt(self, ciphertext: str) -> Optional[str]:
        """
        Decrypt ciphertext

        Args:
            ciphertext: Encrypted text

        Returns:
            Decrypted text or None if decryption fails
        """
        if not ciphertext:
            return None

        try:
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except (InvalidToken, Exception):
            return None


# ============ Device ID Validation ============


def generate_device_id(user_id: int, user_agent: str, ip_address: str, secret: str) -> str:
    """
    Generate secure device ID based on user context

    Args:
        user_id: User ID
        user_agent: Browser user agent
        ip_address: Client IP address
        secret: Server secret key

    Returns:
        Secure device ID (32 chars hex)
    """
    # Combine user context
    context = f"{user_id}:{user_agent}:{ip_address}:{secret}"

    # Hash with SHA256
    device_hash = hashlib.sha256(context.encode()).hexdigest()

    return device_hash[:32]


def validate_device_id(
    device_id: str, user_id: int, user_agent: str, ip_address: str, secret: str
) -> bool:
    """
    Validate device ID matches user context

    Args:
        device_id: Device ID to validate
        user_id: User ID
        user_agent: Browser user agent
        ip_address: Client IP address
        secret: Server secret key

    Returns:
        True if device ID is valid
    """
    if not device_id or len(device_id) != 32:
        return False

    expected_device_id = generate_device_id(user_id, user_agent, ip_address, secret)

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(device_id, expected_device_id)


def generate_session_device_id(session_id: str, secret: str) -> str:
    """
    Generate device ID from session (fallback if user not authenticated)

    Args:
        session_id: Session ID
        secret: Server secret key

    Returns:
        Device ID
    """
    context = f"{session_id}:{secret}"
    device_hash = hashlib.sha256(context.encode()).hexdigest()
    return device_hash[:32]


# ============ Secure Token Generation ============


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token

    Args:
        length: Token length in bytes (will be hex encoded to 2x chars)

    Returns:
        Secure token (hex string)
    """
    return secrets.token_hex(length)


def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return generate_secure_token(32)


def generate_api_key() -> str:
    """Generate API key"""
    return generate_secure_token(32)


# ============ Password Hashing Helpers ============


def hash_password_simple(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Simple password hashing (use app.core.security.hash_password for production)

    Args:
        password: Password to hash
        salt: Optional salt (will be generated if not provided)

    Returns:
        Tuple of (hashed_password, salt)
    """
    if not salt:
        salt = secrets.token_hex(16)

    # SHA256 with salt (NOT recommended for production, use bcrypt instead)
    password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

    return password_hash, salt


def verify_password_simple(password: str, password_hash: str, salt: str) -> bool:
    """
    Verify password against simple hash

    Args:
        password: Password to verify
        password_hash: Stored hash
        salt: Stored salt

    Returns:
        True if password matches
    """
    expected_hash, _ = hash_password_simple(password, salt)
    return hmac.compare_digest(password_hash, expected_hash)


# ============ Content Integrity ============


def generate_content_hash(content: str) -> str:
    """
    Generate hash of content for integrity checking

    Args:
        content: Content to hash

    Returns:
        Content hash (SHA256 hex)
    """
    return hashlib.sha256(content.encode()).hexdigest()


def verify_content_integrity(content: str, expected_hash: str) -> bool:
    """
    Verify content hasn't been tampered with

    Args:
        content: Content to verify
        expected_hash: Expected hash

    Returns:
        True if content is intact
    """
    actual_hash = generate_content_hash(content)
    return hmac.compare_digest(actual_hash, expected_hash)


# ============ Singleton Instance ============

_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get singleton encryption service instance

    Returns:
        EncryptionService instance
    """
    global _encryption_service

    if _encryption_service is None:
        from app.core.config import settings

        _encryption_service = EncryptionService(settings.SECRET_KEY)

    return _encryption_service


# ============ Convenience Functions ============


def encrypt_content(plaintext: str) -> str:
    """Encrypt content using singleton service"""
    return get_encryption_service().encrypt(plaintext)


def decrypt_content(ciphertext: str) -> Optional[str]:
    """Decrypt content using singleton service"""
    return get_encryption_service().decrypt(ciphertext)
