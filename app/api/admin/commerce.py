"""
AGTR Merkezi - Admin Commerce API
Package and payment management
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.common import (
    BadRequestError,
    NotFoundError,
    log_api_call,
    paginated_response,
    success_response,
)
from app.api.servers import (
    create_physical_server,
    delete_physical_server,
    start_physical_server,
)
from app.core.security import get_current_admin
from app.models.connection import get_db
from app.models.database import (
    AuditLog,
    BankTransfer,
    GameServer,
    GameType,
    Notification,
    Payment,
    PaymentMethod,
    PaymentStatus,
    ServerPackage,
    ServerStatus,
    SystemLog,
    Transaction,
    User,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== REQUEST MODELS ====================


class PackageCreateRequest(BaseModel):
    slug: str
    name: str
    game_type: str
    slots: int
    features: list[str] = []
    description: str = ""
    price_monthly: float
    display_order: int = 0


class PackageUpdateRequest(BaseModel):
    name: Optional[str] = None
    slots: Optional[int] = None
    features: Optional[list[str]] = None
    description: Optional[str] = None
    price_monthly: Optional[float] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class PaymentRejectRequest(BaseModel):
    reason: str


# ==================== PAYMENT ENDPOINTS ====================


@router.get("/payments", response_model=dict)
async def list_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """List payments with pagination"""
    try:
        log_api_call("admin_list_payments", admin.id)

        query = db.query(Payment)

        if status:
            try:
                status_enum = PaymentStatus(status)
                query = query.filter(Payment.status == status_enum)
            except ValueError:
                pass

        total = query.count()
        payments = (
            query.order_by(desc(Payment.created_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        result = []
        for p in payments:
            user = db.query(User).filter(User.id == p.user_id).first()
            result.append(
                {
                    "id": p.id,
                    "username": user.username if user else "N/A",
                    "amount": p.amount,
                    "method": p.method.value if p.method else None,
                    "status": p.status.value,
                    "reference_code": p.reference_code,
                    "description": p.description,
                    "created_at": p.created_at.isoformat(),
                    "completed_at": p.completed_at.isoformat() if p.completed_at else None,
                }
            )

        return paginated_response(result, total, page, per_page)

    except Exception as e:
        logger.error(f"Error listing payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payments/pending", response_model=dict)
async def list_pending_payments(
    db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """List pending payments"""
    try:
        payments = (
            db.query(Payment)
            .filter(Payment.status == PaymentStatus.PENDING)
            .order_by(Payment.created_at.desc())
            .all()
        )

        result = []
        for p in payments:
            user = db.query(User).filter(User.id == p.user_id).first()
            bank_transfer = db.query(BankTransfer).filter(BankTransfer.payment_id == p.id).first()

            result.append(
                {
                    "id": p.id,
                    "username": user.username if user else "N/A",
                    "user_email": user.email if user else "N/A",
                    "amount": p.amount,
                    "method": p.method.value if p.method else None,
                    "reference_code": p.reference_code,
                    "description": p.description,
                    "created_at": p.created_at.isoformat(),
                    "bank_transfer": (
                        {
                            "sender_name": bank_transfer.sender_name,
                            "sender_iban": bank_transfer.sender_iban,
                            "notes": bank_transfer.notes,
                        }
                        if bank_transfer
                        else None
                    ),
                }
            )

        return success_response(data={"payments": result})

    except Exception as e:
        logger.error(f"Error listing pending payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/{payment_id}/approve")
async def approve_payment(
    payment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Approve payment and setup server"""
    try:
        payment = (
            db.query(Payment)
            .filter(Payment.id == payment_id, Payment.status == PaymentStatus.PENDING)
            .first()
        )

        if not payment:
            raise NotFoundError("Bekleyen ödeme bulunamadı")

        user = db.query(User).filter(User.id == payment.user_id).first()
        if not user:
            raise NotFoundError("Kullanıcı bulunamadı")

        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.utcnow()

        # Server order
        if payment.server_id:
            server = db.query(GameServer).filter(GameServer.id == payment.server_id).first()
            if server:
                # Balance payment
                if payment.method == PaymentMethod.BALANCE or payment.method is None:
                    if user.balance >= payment.amount:
                        balance_before = user.balance
                        user.balance -= payment.amount

                        transaction = Transaction(
                            user_id=user.id,
                            type="payment",
                            amount=-payment.amount,
                            description=f"Sunucu ödemesi: {server.name}",
                            payment_id=payment.id,
                            balance_before=balance_before,
                            balance_after=user.balance,
                        )
                        db.add(transaction)
                    else:
                        log_warn = SystemLog(
                            level="warning",
                            category="payment",
                            message=f"Yetersiz bakiye: {user.username}",
                            user_id=admin.id,
                        )
                        db.add(log_warn)

                # Extend server expiration
                if server.expires_at and server.expires_at > datetime.utcnow():
                    server.expires_at = server.expires_at + timedelta(days=30 * payment.months)
                else:
                    server.expires_at = datetime.utcnow() + timedelta(days=30 * payment.months)
                server.status = ServerStatus.RUNNING

                # Create physical server
                game_type = server.game_type.value
                create_result = create_physical_server(
                    server.id,
                    server.ip_address,
                    server.port,
                    game_type,
                    server.slots,
                    server.rcon_password,
                    server.name,
                )

                if create_result["success"]:
                    start_physical_server(server.id)

                # Notification
                notification = Notification(
                    user_id=user.id,
                    type="server",
                    title="Sunucunuz Aktif!",
                    message=f"{server.name} sunucunuz başarıyla kuruldu.",
                    link=f"/panel/servers/{server.id}",
                )
                db.add(notification)
        else:
            # Balance deposit
            balance_before = user.balance
            user.balance += payment.amount

            transaction = Transaction(
                user_id=user.id,
                type="deposit",
                amount=payment.amount,
                description=f"Bakiye yükleme: {payment.reference_code}",
                payment_id=payment.id,
                balance_before=balance_before,
                balance_after=user.balance,
            )
            db.add(transaction)

            notification = Notification(
                user_id=user.id,
                type="payment",
                title="Bakiye Yüklendi",
                message=f"{payment.amount} TL bakiye eklendi.",
                link="/panel/balance",
            )
            db.add(notification)

        # Update bank transfer
        bank_transfer = db.query(BankTransfer).filter(BankTransfer.payment_id == payment_id).first()
        if bank_transfer:
            bank_transfer.approved_by = admin.id
            bank_transfer.approved_at = datetime.utcnow()

        # Audit log
        client_ip = request.client.host if request.client else "unknown"
        audit = AuditLog(
            user_id=admin.id,
            action="payment_approve",
            entity_type="payment",
            entity_id=payment_id,
            ip_address=client_ip,
        )
        db.add(audit)

        db.commit()

        return success_response(message="Ödeme onaylandı", data={"new_balance": user.balance})

    except (NotFoundError, BadRequestError):
        raise
    except Exception as e:
        logger.error(f"Error approving payment: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/{payment_id}/reject")
async def reject_payment(
    payment_id: int,
    data: PaymentRejectRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Reject payment"""
    try:
        payment = (
            db.query(Payment)
            .filter(Payment.id == payment_id, Payment.status == PaymentStatus.PENDING)
            .first()
        )

        if not payment:
            raise NotFoundError("Bekleyen ödeme bulunamadı")

        payment.status = PaymentStatus.CANCELLED

        # Cancel server if exists
        if payment.server_id:
            server = db.query(GameServer).filter(GameServer.id == payment.server_id).first()
            if server:
                server.status = ServerStatus.DELETED
                delete_physical_server(server.id)

        # Update bank transfer
        bank_transfer = db.query(BankTransfer).filter(BankTransfer.payment_id == payment_id).first()
        if bank_transfer:
            bank_transfer.rejection_reason = data.reason

        # Log
        log = SystemLog(
            level="warning",
            category="payment",
            message=f"Ödeme reddedildi: {payment.reference_code}",
            user_id=admin.id,
        )
        db.add(log)
        db.commit()

        return success_response(message="Ödeme reddedildi")

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error rejecting payment: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PACKAGE ENDPOINTS ====================


@router.get("/packages", response_model=dict)
async def list_packages(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """List server packages"""
    try:
        packages = db.query(ServerPackage).order_by(ServerPackage.display_order).all()

        return success_response(
            data={
                "packages": [
                    {
                        "id": p.id,
                        "slug": p.slug,
                        "name": p.name,
                        "game_type": p.game_type.value,
                        "slots": p.slots,
                        "features": p.features or [],
                        "description": p.description,
                        "price_monthly": p.price_monthly,
                        "is_active": p.is_active,
                        "display_order": p.display_order,
                    }
                    for p in packages
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error listing packages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/packages")
async def create_package(
    data: PackageCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Create new package"""
    try:
        existing = db.query(ServerPackage).filter(ServerPackage.slug == data.slug).first()
        if existing:
            raise BadRequestError("Bu slug zaten kullanılıyor")

        try:
            game_type = GameType(data.game_type)
        except ValueError:
            raise BadRequestError("Geçersiz oyun tipi")

        package = ServerPackage(
            slug=data.slug,
            name=data.name,
            game_type=game_type,
            slots=data.slots,
            features=data.features,
            description=data.description,
            price_monthly=data.price_monthly,
            display_order=data.display_order,
        )
        db.add(package)
        db.commit()

        return success_response(message="Paket oluşturuldu", data={"package_id": package.id})

    except (BadRequestError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Error creating package: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/packages/{package_id}")
async def update_package(
    package_id: int,
    data: PackageUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update package"""
    try:
        package = db.query(ServerPackage).filter(ServerPackage.id == package_id).first()
        if not package:
            raise NotFoundError("Paket bulunamadı")

        if data.name is not None:
            package.name = data.name
        if data.slots is not None:
            package.slots = data.slots
        if data.features is not None:
            package.features = data.features
        if data.description is not None:
            package.description = data.description
        if data.price_monthly is not None:
            package.price_monthly = data.price_monthly
        if data.is_active is not None:
            package.is_active = data.is_active
        if data.display_order is not None:
            package.display_order = data.display_order

        db.commit()
        return success_response(message="Paket güncellendi")

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error updating package: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/packages/{package_id}")
async def delete_package(
    package_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    """Deactivate package"""
    try:
        package = db.query(ServerPackage).filter(ServerPackage.id == package_id).first()
        if not package:
            raise NotFoundError("Paket bulunamadı")

        active_servers = (
            db.query(GameServer)
            .filter(
                GameServer.package_id == package_id,
                GameServer.status.notin_([ServerStatus.DELETED, ServerStatus.EXPIRED]),
            )
            .count()
        )

        if active_servers > 0:
            raise BadRequestError(f"Bu pakete bağlı {active_servers} aktif sunucu var")

        package.is_active = False
        db.commit()

        return success_response(message="Paket deaktif edildi")

    except (NotFoundError, BadRequestError):
        raise
    except Exception as e:
        logger.error(f"Error deleting package: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
