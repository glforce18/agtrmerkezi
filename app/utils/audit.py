"""
AGTR Merkezi - Audit Logging Utilities
Tekrar eden audit log fonksiyonlarını merkezi hale getirir
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.database import AuditLog, User


def log_audit(
    db: Session,
    user: Optional[User],
    action: str,
    category: str = "general",
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success"
) -> AuditLog:
    """
    Merkezi audit logging fonksiyonu

    Args:
        db: Database session
        user: Kullanıcı nesnesi (opsiyonel)
        action: Yapılan işlem (örn: "login", "server_created")
        category: Kategori (örn: "auth", "server", "payment")
        details: Detay bilgisi (opsiyonel)
        ip_address: IP adresi (opsiyonel)
        user_agent: User agent string (opsiyonel)
        status: İşlem durumu ("success", "failed", "warning")

    Returns:
        AuditLog: Oluşturulan log kaydı
    """
    try:
        audit = AuditLog(
            user_id=user.id if user else None,
            username=user.username if user else "system",
            action=action,
            category=category,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            created_at=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        return audit
    except Exception as e:
        db.rollback()
        # Log hatası bile olsa uygulamayı durdurmayalım
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Audit log kaydetme hatası: {e}")
        return None


def log_admin_action(
    db: Session,
    admin: User,
    action: str,
    details: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Admin işlemlerini logla

    Args:
        db: Database session
        admin: Admin kullanıcısı
        action: Yapılan işlem
        details: Detay bilgisi
        ip_address: IP adresi

    Returns:
        AuditLog: Oluşturulan log kaydı
    """
    return log_audit(
        db=db,
        user=admin,
        action=action,
        category="admin",
        details=details,
        ip_address=ip_address,
        status="success"
    )


def log_auth_attempt(
    db: Session,
    username: str,
    success: bool,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    failure_reason: Optional[str] = None
) -> AuditLog:
    """
    Giriş denemelerini logla

    Args:
        db: Database session
        username: Kullanıcı adı
        success: Başarılı mı?
        ip_address: IP adresi
        user_agent: User agent string
        failure_reason: Başarısızlık nedeni

    Returns:
        AuditLog: Oluşturulan log kaydı
    """
    action = "login_success" if success else "login_failed"
    details = failure_reason if failure_reason else None
    status = "success" if success else "failed"

    # Kullanıcı bilgilerini almaya çalış (başarılı girişlerde)
    user = None
    if success:
        from app.models.database import User as UserModel
        user = db.query(UserModel).filter(UserModel.username == username).first()

    return log_audit(
        db=db,
        user=user,
        action=action,
        category="auth",
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status
    )


def log_payment_action(
    db: Session,
    user: User,
    action: str,
    amount: Optional[float] = None,
    payment_id: Optional[int] = None,
    details: Optional[str] = None
) -> AuditLog:
    """
    Ödeme işlemlerini logla

    Args:
        db: Database session
        user: Kullanıcı
        action: İşlem (örn: "payment_created", "payment_completed")
        amount: Tutar
        payment_id: Ödeme ID
        details: Detay bilgisi

    Returns:
        AuditLog: Oluşturulan log kaydı
    """
    detail_parts = []
    if amount:
        detail_parts.append(f"Amount: {amount} TL")
    if payment_id:
        detail_parts.append(f"Payment ID: {payment_id}")
    if details:
        detail_parts.append(details)

    full_details = " | ".join(detail_parts) if detail_parts else None

    return log_audit(
        db=db,
        user=user,
        action=action,
        category="payment",
        details=full_details,
        status="success"
    )


def log_server_action(
    db: Session,
    user: User,
    action: str,
    server_id: Optional[int] = None,
    server_name: Optional[str] = None,
    details: Optional[str] = None
) -> AuditLog:
    """
    Sunucu işlemlerini logla

    Args:
        db: Database session
        user: Kullanıcı
        action: İşlem (örn: "server_created", "server_started")
        server_id: Sunucu ID
        server_name: Sunucu adı
        details: Detay bilgisi

    Returns:
        AuditLog: Oluşturulan log kaydı
    """
    detail_parts = []
    if server_id:
        detail_parts.append(f"Server ID: {server_id}")
    if server_name:
        detail_parts.append(f"Server: {server_name}")
    if details:
        detail_parts.append(details)

    full_details = " | ".join(detail_parts) if detail_parts else None

    return log_audit(
        db=db,
        user=user,
        action=action,
        category="server",
        details=full_details,
        status="success"
    )
