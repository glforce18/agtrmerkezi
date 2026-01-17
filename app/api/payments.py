"""
AGTR Merkezi - Payments API
Kupon, Fatura, Transaction History, Otomatik Yenileme destekli
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, field_validator
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import generate_reference_code, get_current_user_required
from app.models.connection import get_db
from app.models.database import (
    AuditLog,
    BankTransfer,
    Coupon,
    GameServer,
    Invoice,
    Notification,
    Payment,
    PaymentMethod,
    PaymentStatus,
    ServerStatus,
    Transaction,
    User,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== HELPER FUNCTIONS ====================

def log_audit(db: Session, user_id: int, action: str, entity_type: str = None,
              entity_id: int = None, old_values: dict = None, new_values: dict = None,
              ip_address: str = None):
    """Audit log kaydi"""
    try:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        db.add(audit)
    except Exception as e:
        logger.error(f"Audit log hatasi: {e}")


def create_notification(db: Session, user_id: int, type: str, title: str,
                        message: str, link: str = None):
    """Bildirim olustur"""
    try:
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            link=link
        )
        db.add(notification)
    except Exception as e:
        logger.error(f"Notification hatasi: {e}")


def create_transaction(db: Session, user_id: int, type: str, amount: float,
                       description: str, payment_id: int = None, balance_before: float = 0,
                       balance_after: float = 0):
    """Transaction kaydi olustur"""
    try:
        transaction = Transaction(
            user_id=user_id,
            type=type,
            amount=amount,
            description=description,
            payment_id=payment_id,
            balance_before=balance_before,
            balance_after=balance_after
        )
        db.add(transaction)
    except Exception as e:
        logger.error(f"Transaction hatasi: {e}")


class PaymentMethodSelect(BaseModel):
    payment_id: int
    method: str
    coupon_code: Optional[str] = None


class BankTransferInfo(BaseModel):
    payment_id: int
    sender_name: str
    sender_iban: Optional[str] = None
    notes: Optional[str] = None
    
    @field_validator("sender_name")
    @classmethod
    def validate_sender_name(cls, v):
        if len(v) < 3:
            raise ValueError("Gonderen adi en az 3 karakter olmali")
        if len(v) > 100:
            raise ValueError("Gonderen adi en fazla 100 karakter olmali")
        return v.strip()


class BalanceAddRequest(BaseModel):
    amount: float
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v < settings.MIN_BALANCE_AMOUNT:
            raise ValueError(f"Minimum yukleme tutari {settings.MIN_BALANCE_AMOUNT} TL")
        if v > settings.MAX_BALANCE_AMOUNT:
            raise ValueError(f"Maksimum yukleme tutari {settings.MAX_BALANCE_AMOUNT} TL")
        return round(v, 2)


class CouponApplyRequest(BaseModel):
    payment_id: int
    coupon_code: str


class AutoRenewRequest(BaseModel):
    server_id: int
    enabled: bool


@router.get("/my-payments")
async def my_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    status: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user_required)
):
    """Odeme gecmisi"""
    query = db.query(Payment).filter(Payment.user_id == current_user.id)
    
    if status:
        try:
            status_enum = PaymentStatus(status)
            query = query.filter(Payment.status == status_enum)
        except:
            pass
    
    total = query.count()
    payments = query.order_by(desc(Payment.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "payments": [{
            "id": p.id,
            "amount": p.amount,
            "original_amount": p.original_amount,
            "discount_amount": p.discount_amount,
            "method": p.method.value if p.method else None,
            "status": p.status.value,
            "reference_code": p.reference_code,
            "description": p.description,
            "coupon_code": p.coupon_code,
            "server_id": p.server_id,
            "created_at": p.created_at.isoformat(),
            "completed_at": p.completed_at.isoformat() if p.completed_at else None
        } for p in payments],
        "balance": current_user.balance,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


@router.post("/select-method")
async def select_payment_method(data: PaymentMethodSelect, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Odeme yontemi sec"""
    payment = db.query(Payment).filter(Payment.id == data.payment_id, Payment.user_id == current_user.id, Payment.status == PaymentStatus.PENDING).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Bekleyen odeme bulunamadi")
    
    try:
        method = PaymentMethod(data.method)
    except ValueError:
        raise HTTPException(status_code=400, detail="Gecersiz odeme yontemi")
    
    client_ip = request.client.host if request.client else None
    payment.method = method
    payment.ip_address = client_ip
    
    # Kupon uygula (varsa)
    if data.coupon_code and not payment.coupon_code:
        coupon = db.query(Coupon).filter(
            Coupon.code == data.coupon_code.upper(),
            Coupon.is_active == True
        ).first()
        
        if coupon:
            # Kupon gecerliligi kontrol
            now = datetime.utcnow()
            if coupon.valid_from and coupon.valid_from > now:
                pass  # Henuz gecerli degil
            elif coupon.valid_until and coupon.valid_until < now:
                pass  # Suresi dolmus
            elif coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
                pass  # Kullanim limiti dolmus
            elif coupon.min_amount and payment.amount < coupon.min_amount:
                pass  # Minimum tutar saglanmadi
            else:
                # Kupon gecerli, uygula
                payment.original_amount = payment.amount
                payment.coupon_code = coupon.code
                payment.coupon_id = coupon.id
                
                if coupon.discount_type == "percent":
                    discount = payment.amount * (coupon.discount_value / 100)
                    if coupon.max_discount:
                        discount = min(discount, coupon.max_discount)
                else:
                    discount = coupon.discount_value
                
                payment.discount_amount = round(discount, 2)
                payment.amount = round(payment.amount - discount, 2)
                
                coupon.usage_count += 1
    
    if method == PaymentMethod.BALANCE:
        if current_user.balance < payment.amount:
            raise HTTPException(status_code=400, detail=f"Yetersiz bakiye. Mevcut: {current_user.balance} TL, Gerekli: {payment.amount} TL")
        
        balance_before = current_user.balance
        current_user.balance -= payment.amount
        balance_after = current_user.balance
        
        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.utcnow()
        
        # Transaction kaydet
        create_transaction(db, current_user.id, "payment", -payment.amount,
                          payment.description, payment.id, balance_before, balance_after)
        
        # Sunucu varsa aktif et
        if payment.server_id:
            server = db.query(GameServer).filter(GameServer.id == payment.server_id).first()
            if server:
                server.status = ServerStatus.RUNNING
                server.expires_at = datetime.utcnow() + timedelta(days=30 * payment.months)
                
                # Fatura olustur
                create_invoice(db, payment, current_user)
        
        # Audit log
        log_audit(db, current_user.id, "payment_balance", "payment", payment.id,
                  new_values={"amount": payment.amount, "method": "balance"},
                  ip_address=client_ip)
        
        # Bildirim
        create_notification(db, current_user.id, "payment",
                           "Odeme Tamamlandi",
                           f"{payment.amount} TL tutarindaki odemeniz bakiyeden alindi.",
                           f"/payments/{payment.id}")
        
        db.commit()
        
        logger.info(f"Bakiye odemesi: {current_user.username} - {payment.amount} TL")
        
        return {"success": True, "message": "Odeme bakiyeden alindi", "new_balance": current_user.balance}
    
    elif method == PaymentMethod.BANK_TRANSFER:
        log_audit(db, current_user.id, "payment_bank_selected", "payment", payment.id,
                  new_values={"amount": payment.amount, "method": "bank_transfer"},
                  ip_address=client_ip)
        
        db.commit()
        return {
            "success": True,
            "bank_accounts": settings.BANK_ACCOUNTS,
            "reference_code": payment.reference_code,
            "amount": payment.amount,
            "original_amount": payment.original_amount,
            "discount_amount": payment.discount_amount,
            "message": "Lutfen asagidaki hesaplardan birine odemenizi yapin"
        }
    
    db.commit()
    return {"success": True, "method": method.value}


def create_invoice(db: Session, payment: Payment, user: User):
    """Fatura olustur"""
    try:
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m')}-{payment.id:06d}"
        
        invoice = Invoice(
            payment_id=payment.id,
            user_id=user.id,
            invoice_number=invoice_number,
            amount=payment.amount,
            tax_amount=round(payment.amount * 0.20, 2),  # %20 KDV
            total_amount=round(payment.amount * 1.20, 2),
            billing_name=user.display_name,
            billing_email=user.email,
            status="issued"
        )
        db.add(invoice)
        logger.info(f"Fatura olusturuldu: {invoice_number}")
    except Exception as e:
        logger.error(f"Fatura olusturma hatasi: {e}")


@router.post("/bank-transfer-notify")
async def notify_bank_transfer(data: BankTransferInfo, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    payment = db.query(Payment).filter(
        Payment.id == data.payment_id,
        Payment.user_id == current_user.id,
        Payment.method == PaymentMethod.BANK_TRANSFER,
        Payment.status == PaymentStatus.PENDING
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Bekleyen havale odemesi bulunamadi")
    
    # Mevcut bildirim varsa guncelle
    existing = db.query(BankTransfer).filter(BankTransfer.payment_id == payment.id).first()
    if existing:
        existing.sender_name = data.sender_name
        existing.sender_iban = data.sender_iban
        existing.notes = data.notes
    else:
        bank_transfer = BankTransfer(
            payment_id=payment.id,
            sender_name=data.sender_name,
            sender_iban=data.sender_iban,
            notes=data.notes
        )
        db.add(bank_transfer)
    
    db.commit()
    return {"success": True, "message": "Havale bildiriminiz alindi. Onay bekleniyor."}


@router.post("/add-balance")
async def add_balance(data: BalanceAddRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    if data.amount < 10:
        raise HTTPException(status_code=400, detail="Minimum yukleme tutari 10 TL")
    if data.amount > 10000:
        raise HTTPException(status_code=400, detail="Maksimum yukleme tutari 10000 TL")
    
    payment = Payment(
        user_id=current_user.id,
        amount=data.amount,
        status=PaymentStatus.PENDING,
        reference_code=generate_reference_code("BAL"),
        description=f"Bakiye Yukleme - {data.amount} TL"
    )
    db.add(payment)
    db.commit()
    
    return {
        "success": True,
        "payment_id": payment.id,
        "reference_code": payment.reference_code,
        "amount": payment.amount
    }


@router.get("/payment/{payment_id}")
async def get_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Odeme detayi"""
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.user_id == current_user.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Odeme bulunamadi")
    
    # Fatura bilgisi
    invoice = db.query(Invoice).filter(Invoice.payment_id == payment_id).first()
    
    return {
        "payment": {
            "id": payment.id,
            "amount": payment.amount,
            "original_amount": payment.original_amount,
            "discount_amount": payment.discount_amount,
            "method": payment.method.value if payment.method else None,
            "status": payment.status.value,
            "reference_code": payment.reference_code,
            "description": payment.description,
            "coupon_code": payment.coupon_code,
            "server_id": payment.server_id,
            "months": payment.months,
            "created_at": payment.created_at.isoformat(),
            "completed_at": payment.completed_at.isoformat() if payment.completed_at else None
        },
        "invoice": {
            "invoice_number": invoice.invoice_number,
            "amount": invoice.amount,
            "tax_amount": invoice.tax_amount,
            "total_amount": invoice.total_amount,
            "status": invoice.status
        } if invoice else None
    }


# ==================== COUPON ====================

@router.post("/apply-coupon")
async def apply_coupon(data: CouponApplyRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Kupon uygula"""
    payment = db.query(Payment).filter(
        Payment.id == data.payment_id,
        Payment.user_id == current_user.id,
        Payment.status == PaymentStatus.PENDING
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Bekleyen odeme bulunamadi")
    
    if payment.coupon_code:
        raise HTTPException(status_code=400, detail="Bu odemeye zaten kupon uygulanmis")
    
    coupon = db.query(Coupon).filter(
        Coupon.code == data.coupon_code.upper(),
        Coupon.is_active == True
    ).first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Gecersiz kupon kodu")
    
    # Gecerlilik kontrolleri
    now = datetime.utcnow()
    if coupon.valid_from and coupon.valid_from > now:
        raise HTTPException(status_code=400, detail="Bu kupon henuz gecerli degil")
    
    if coupon.valid_until and coupon.valid_until < now:
        raise HTTPException(status_code=400, detail="Bu kuponun suresi dolmus")
    
    if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
        raise HTTPException(status_code=400, detail="Bu kuponun kullanim limiti dolmus")
    
    if coupon.min_amount and payment.amount < coupon.min_amount:
        raise HTTPException(status_code=400, detail=f"Bu kupon minimum {coupon.min_amount} TL odeme icin gecerli")
    
    # Kullanici daha once kullanmis mi?
    if coupon.single_use_per_user:
        used = db.query(Payment).filter(
            Payment.user_id == current_user.id,
            Payment.coupon_id == coupon.id,
            Payment.status == PaymentStatus.COMPLETED
        ).first()
        if used:
            raise HTTPException(status_code=400, detail="Bu kuponu daha once kullandiniz")
    
    # Kuponu uygula
    payment.original_amount = payment.amount
    payment.coupon_code = coupon.code
    payment.coupon_id = coupon.id
    
    if coupon.discount_type == "percent":
        discount = payment.amount * (coupon.discount_value / 100)
        if coupon.max_discount:
            discount = min(discount, coupon.max_discount)
    else:
        discount = min(coupon.discount_value, payment.amount)
    
    payment.discount_amount = round(discount, 2)
    payment.amount = round(payment.original_amount - discount, 2)
    
    coupon.usage_count += 1
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "coupon_apply", "payment", payment.id,
              new_values={"coupon_code": coupon.code, "discount": discount},
              ip_address=client_ip)
    
    db.commit()
    
    logger.info(f"Kupon uygulandi: {coupon.code} -> {current_user.username}")
    
    return {
        "success": True,
        "message": f"Kupon uygulandi! {discount} TL indirim",
        "original_amount": payment.original_amount,
        "discount_amount": payment.discount_amount,
        "new_amount": payment.amount
    }


@router.delete("/remove-coupon/{payment_id}")
async def remove_coupon(payment_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Kuponu kaldir"""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == current_user.id,
        Payment.status == PaymentStatus.PENDING
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Bekleyen odeme bulunamadi")
    
    if not payment.coupon_code:
        raise HTTPException(status_code=400, detail="Bu odemede kupon yok")
    
    # Kupon kullanim sayisini dusur
    if payment.coupon_id:
        coupon = db.query(Coupon).filter(Coupon.id == payment.coupon_id).first()
        if coupon and coupon.usage_count > 0:
            coupon.usage_count -= 1
    
    old_coupon = payment.coupon_code
    payment.amount = payment.original_amount
    payment.original_amount = None
    payment.discount_amount = None
    payment.coupon_code = None
    payment.coupon_id = None
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "coupon_remove", "payment", payment_id,
              old_values={"coupon_code": old_coupon}, ip_address=client_ip)
    
    db.commit()
    
    return {"success": True, "message": "Kupon kaldirildi", "amount": payment.amount}


# ==================== TRANSACTIONS ====================

@router.get("/transactions")
async def get_transactions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Islem gecmisi (bakiye hareketleri)"""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    if type:
        query = query.filter(Transaction.type == type)
    
    total = query.count()
    transactions = query.order_by(desc(Transaction.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "transactions": [{
            "id": t.id,
            "type": t.type,
            "amount": t.amount,
            "description": t.description,
            "balance_before": t.balance_before,
            "balance_after": t.balance_after,
            "payment_id": t.payment_id,
            "created_at": t.created_at.isoformat()
        } for t in transactions],
        "current_balance": current_user.balance,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


# ==================== INVOICES ====================

@router.get("/invoices")
async def get_invoices(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Fatura listesi"""
    query = db.query(Invoice).filter(Invoice.user_id == current_user.id)
    
    total = query.count()
    invoices = query.order_by(desc(Invoice.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "invoices": [{
            "id": i.id,
            "invoice_number": i.invoice_number,
            "amount": i.amount,
            "tax_amount": i.tax_amount,
            "total_amount": i.total_amount,
            "status": i.status,
            "payment_id": i.payment_id,
            "created_at": i.created_at.isoformat()
        } for i in invoices],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }


@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Fatura detayi"""
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Fatura bulunamadi")
    
    payment = db.query(Payment).filter(Payment.id == invoice.payment_id).first()
    
    return {
        "invoice": {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "amount": invoice.amount,
            "tax_amount": invoice.tax_amount,
            "total_amount": invoice.total_amount,
            "billing_name": invoice.billing_name,
            "billing_email": invoice.billing_email,
            "billing_address": invoice.billing_address,
            "billing_tax_number": invoice.billing_tax_number,
            "status": invoice.status,
            "created_at": invoice.created_at.isoformat()
        },
        "payment": {
            "id": payment.id,
            "description": payment.description,
            "method": payment.method.value if payment.method else None,
            "reference_code": payment.reference_code
        } if payment else None
    }


# ==================== AUTO RENEW ====================

@router.post("/auto-renew")
async def toggle_auto_renew(data: AutoRenewRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Otomatik yenileme ac/kapa"""
    server = db.query(GameServer).filter(
        GameServer.id == data.server_id,
        GameServer.owner_id == current_user.id
    ).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="Sunucu bulunamadi")
    
    old_value = server.auto_renew
    server.auto_renew = data.enabled
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "auto_renew_toggle", "server", server.id,
              old_values={"auto_renew": old_value},
              new_values={"auto_renew": data.enabled},
              ip_address=client_ip)
    
    db.commit()
    
    status = "aktif" if data.enabled else "deaktif"
    logger.info(f"Otomatik yenileme {status}: server_{server.id} - {current_user.username}")
    
    return {
        "success": True,
        "message": f"Otomatik yenileme {status} edildi",
        "auto_renew": server.auto_renew
    }


# ==================== CANCEL PAYMENT ====================

@router.post("/cancel/{payment_id}")
async def cancel_payment(payment_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_required)):
    """Bekleyen odemeyi iptal et"""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == current_user.id,
        Payment.status == PaymentStatus.PENDING
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Iptal edilebilir odeme bulunamadi")
    
    # Kupon kullanim sayisini dusur
    if payment.coupon_id:
        coupon = db.query(Coupon).filter(Coupon.id == payment.coupon_id).first()
        if coupon and coupon.usage_count > 0:
            coupon.usage_count -= 1
    
    payment.status = PaymentStatus.CANCELLED
    payment.cancelled_at = datetime.utcnow()
    
    # Sunucu varsa pending'e al
    if payment.server_id:
        server = db.query(GameServer).filter(GameServer.id == payment.server_id).first()
        if server and server.status == ServerStatus.PENDING:
            server.status = ServerStatus.CANCELLED
    
    client_ip = request.client.host if request.client else None
    log_audit(db, current_user.id, "payment_cancel", "payment", payment_id,
              ip_address=client_ip)
    
    db.commit()
    
    logger.info(f"Odeme iptal: #{payment_id} - {current_user.username}")
    
    return {"success": True, "message": "Odeme iptal edildi"}