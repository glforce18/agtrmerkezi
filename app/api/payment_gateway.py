"""
💰 AGTR Payment Gateway API
PayTR, iyzico, Bakiye Sistemi, Kupon, Otomatik Fatura
"""
import base64
import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User

router = APIRouter()

# ============================================================================
# CONFIGURATION (Env'den alınacak)
# ============================================================================

PAYTR_MERCHANT_ID = os.getenv("PAYTR_MERCHANT_ID", "")
PAYTR_MERCHANT_KEY = os.getenv("PAYTR_MERCHANT_KEY", "")
PAYTR_MERCHANT_SALT = os.getenv("PAYTR_MERCHANT_SALT", "")

IYZICO_API_KEY = os.getenv("IYZICO_API_KEY", "")
IYZICO_SECRET_KEY = os.getenv("IYZICO_SECRET_KEY", "")
IYZICO_BASE_URL = os.getenv("IYZICO_BASE_URL", "https://sandbox-api.iyzipay.com")

# ============================================================================
# DATABASE TABLES
# ============================================================================

def ensure_payment_tables(db: Session):
    """Ödeme tablolarını oluştur"""
    try:
        # Kullanıcı bakiyeleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS user_balances (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            balance DECIMAL(10,2) DEFAULT 0,
            total_deposited DECIMAL(10,2) DEFAULT 0,
            total_spent DECIMAL(10,2) DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Bakiye hareketleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS balance_transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            transaction_type ENUM('deposit', 'withdraw', 'payment', 'refund', 'bonus') NOT NULL,
            description VARCHAR(255),
            reference_id VARCHAR(100),
            reference_type VARCHAR(50),
            balance_before DECIMAL(10,2),
            balance_after DECIMAL(10,2),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user (user_id),
            INDEX idx_type (transaction_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Kuponlar
        db.execute(text("""CREATE TABLE IF NOT EXISTS coupons (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(50) NOT NULL UNIQUE,
            discount_type ENUM('percent', 'fixed') NOT NULL,
            discount_value DECIMAL(10,2) NOT NULL,
            min_amount DECIMAL(10,2) DEFAULT 0,
            max_uses INT DEFAULT NULL,
            used_count INT DEFAULT 0,
            user_id INT DEFAULT NULL,
            valid_from DATETIME DEFAULT CURRENT_TIMESTAMP,
            valid_until DATETIME,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_code (code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Kupon kullanımları
        db.execute(text("""CREATE TABLE IF NOT EXISTS coupon_uses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            coupon_id INT NOT NULL,
            user_id INT NOT NULL,
            order_id INT,
            discount_amount DECIMAL(10,2),
            used_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_coupon (coupon_id),
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Faturalar
        db.execute(text("""CREATE TABLE IF NOT EXISTS invoices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            invoice_no VARCHAR(50) NOT NULL UNIQUE,
            user_id INT NOT NULL,
            order_id INT,
            subtotal DECIMAL(10,2) NOT NULL,
            discount DECIMAL(10,2) DEFAULT 0,
            tax DECIMAL(10,2) DEFAULT 0,
            total DECIMAL(10,2) NOT NULL,
            status ENUM('draft', 'sent', 'paid', 'cancelled') DEFAULT 'draft',
            billing_name VARCHAR(255),
            billing_address TEXT,
            billing_tax_no VARCHAR(50),
            notes TEXT,
            pdf_path VARCHAR(500),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            paid_at DATETIME,
            INDEX idx_user (user_id),
            INDEX idx_invoice_no (invoice_no)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Fatura kalemleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS invoice_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            invoice_id INT NOT NULL,
            description VARCHAR(255) NOT NULL,
            quantity INT DEFAULT 1,
            unit_price DECIMAL(10,2) NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            INDEX idx_invoice (invoice_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Ödeme işlemleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS payment_transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            gateway VARCHAR(50) NOT NULL,
            transaction_id VARCHAR(255),
            merchant_oid VARCHAR(100) NOT NULL UNIQUE,
            amount DECIMAL(10,2) NOT NULL,
            currency VARCHAR(10) DEFAULT 'TRY',
            status ENUM('pending', 'success', 'failed', 'refunded') DEFAULT 'pending',
            payment_type VARCHAR(50),
            installment INT DEFAULT 1,
            card_last4 VARCHAR(4),
            error_message TEXT,
            raw_response JSON,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            INDEX idx_user (user_id),
            INDEX idx_merchant_oid (merchant_oid),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Havale/EFT bildirimleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS bank_transfers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            bank_name VARCHAR(100),
            sender_name VARCHAR(255),
            reference_no VARCHAR(100),
            transfer_date DATE,
            notes TEXT,
            status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
            admin_note TEXT,
            processed_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            processed_at DATETIME,
            INDEX idx_user (user_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        db.commit()
    except:
        db.rollback()


# ============================================================================
# BAKİYE SİSTEMİ
# ============================================================================

@router.get("/balance")
async def get_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """💰 Bakiye bilgisi"""
    ensure_payment_tables(db)
    
    balance = db.execute(text("""
        SELECT balance, total_deposited, total_spent FROM user_balances WHERE user_id = :uid
    """), {"uid": current_user.id}).fetchone()
    
    if not balance:
        db.execute(text("INSERT INTO user_balances (user_id) VALUES (:uid)"), {"uid": current_user.id})
        db.commit()
        return {"success": True, "balance": 0, "total_deposited": 0, "total_spent": 0}
    
    return {
        "success": True,
        "balance": float(balance[0]),
        "total_deposited": float(balance[1]),
        "total_spent": float(balance[2])
    }


@router.get("/balance/history")
async def balance_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Bakiye geçmişi"""
    ensure_payment_tables(db)
    
    rows = db.execute(text("""
        SELECT * FROM balance_transactions 
        WHERE user_id = :uid ORDER BY created_at DESC LIMIT :lim
    """), {"uid": current_user.id, "lim": limit}).fetchall()
    
    transactions = [{
        "id": r[0], "amount": float(r[2]), "type": r[3],
        "description": r[4], "balance_after": float(r[8]) if r[8] else None,
        "created_at": r[9].isoformat() if r[9] else None
    } for r in rows]
    
    return {"success": True, "transactions": transactions}


async def add_balance(db: Session, user_id: int, amount: float, trans_type: str, 
                     description: str = None, ref_id: str = None, ref_type: str = None):
    """Bakiye ekle/çıkar"""
    ensure_payment_tables(db)
    
    # Mevcut bakiye
    current = db.execute(text(
        "SELECT balance FROM user_balances WHERE user_id = :uid FOR UPDATE"
    ), {"uid": user_id}).fetchone()
    
    if not current:
        db.execute(text("INSERT INTO user_balances (user_id) VALUES (:uid)"), {"uid": user_id})
        current_balance = 0
    else:
        current_balance = float(current[0])
    
    new_balance = current_balance + amount
    
    # Bakiye güncelle
    if amount > 0:
        db.execute(text("""
            UPDATE user_balances SET balance = balance + :amt, total_deposited = total_deposited + :amt
            WHERE user_id = :uid
        """), {"amt": amount, "uid": user_id})
    else:
        db.execute(text("""
            UPDATE user_balances SET balance = balance + :amt, total_spent = total_spent + :spent
            WHERE user_id = :uid
        """), {"amt": amount, "spent": abs(amount), "uid": user_id})
    
    # Transaction kaydı
    db.execute(text("""
        INSERT INTO balance_transactions (user_id, amount, transaction_type, description,
            reference_id, reference_type, balance_before, balance_after)
        VALUES (:uid, :amt, :type, :desc, :ref_id, :ref_type, :before, :after)
    """), {
        "uid": user_id, "amt": amount, "type": trans_type, "desc": description,
        "ref_id": ref_id, "ref_type": ref_type, "before": current_balance, "after": new_balance
    })
    
    db.commit()
    return new_balance


# ============================================================================
# KUPON SİSTEMİ
# ============================================================================

@router.get("/coupons")
async def list_coupons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Kuponları listele (Admin)"""
    if current_user.role.value < 2:  # Admin değilse
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_payment_tables(db)
    
    rows = db.execute(text("""
        SELECT * FROM coupons ORDER BY created_at DESC LIMIT 100
    """)).fetchall()
    
    coupons = [{
        "id": r[0], "code": r[1], "discount_type": r[2],
        "discount_value": float(r[3]), "min_amount": float(r[4]),
        "max_uses": r[5], "used_count": r[6], "is_active": bool(r[9]),
        "valid_until": r[8].isoformat() if r[8] else None
    } for r in rows]
    
    return {"success": True, "coupons": coupons}


@router.post("/coupons")
async def create_coupon(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """➕ Kupon oluştur"""
    if current_user.role.value < 2:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_payment_tables(db)
    
    code = data.get("code", "").upper().strip()
    discount_type = data.get("discount_type", "percent")
    discount_value = data.get("discount_value", 0)
    min_amount = data.get("min_amount", 0)
    max_uses = data.get("max_uses")
    valid_days = data.get("valid_days", 30)
    
    if not code:
        code = f"AGTR{uuid.uuid4().hex[:6].upper()}"
    
    valid_until = datetime.now() + timedelta(days=valid_days) if valid_days else None
    
    try:
        db.execute(text("""
            INSERT INTO coupons (code, discount_type, discount_value, min_amount, max_uses, valid_until)
            VALUES (:code, :dt, :dv, :min, :max, :valid)
        """), {
            "code": code, "dt": discount_type, "dv": discount_value,
            "min": min_amount, "max": max_uses, "valid": valid_until
        })
        db.commit()
        return {"success": True, "code": code, "message": "Kupon oluşturuldu"}
    except:
        db.rollback()
        return JSONResponse(status_code=400, content={"success": False, "detail": "Bu kod zaten var"})


@router.post("/coupons/validate")
async def validate_coupon(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ Kupon doğrula"""
    ensure_payment_tables(db)
    
    code = data.get("code", "").upper().strip()
    amount = data.get("amount", 0)
    
    coupon = db.execute(text("""
        SELECT * FROM coupons WHERE code = :code AND is_active = TRUE
    """), {"code": code}).fetchone()
    
    if not coupon:
        return {"success": False, "valid": False, "message": "Kupon bulunamadı"}
    
    # Süre kontrolü
    if coupon[8] and coupon[8] < datetime.now():
        return {"success": False, "valid": False, "message": "Kupon süresi dolmuş"}
    
    # Kullanım limiti
    if coupon[5] and coupon[6] >= coupon[5]:
        return {"success": False, "valid": False, "message": "Kupon kullanım limiti dolmuş"}
    
    # Minimum tutar
    if amount < float(coupon[4]):
        return {"success": False, "valid": False, "message": f"Minimum {coupon[4]} TL sipariş gerekli"}
    
    # Kullanıcı daha önce kullanmış mı
    used = db.execute(text("""
        SELECT id FROM coupon_uses WHERE coupon_id = :cid AND user_id = :uid
    """), {"cid": coupon[0], "uid": current_user.id}).fetchone()
    
    if used:
        return {"success": False, "valid": False, "message": "Bu kuponu zaten kullandınız"}
    
    # İndirim hesapla
    if coupon[2] == "percent":
        discount = amount * (float(coupon[3]) / 100)
    else:
        discount = float(coupon[3])
    
    discount = min(discount, amount)  # Tutardan fazla indirim olamaz
    
    return {
        "success": True,
        "valid": True,
        "coupon_id": coupon[0],
        "discount_type": coupon[2],
        "discount_value": float(coupon[3]),
        "discount_amount": round(discount, 2),
        "final_amount": round(amount - discount, 2)
    }


# ============================================================================
# PAYTR ENTEGRASYONU
# ============================================================================

@router.post("/paytr/create")
async def create_paytr_payment(
    data: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """💳 PayTR ödeme başlat"""
    ensure_payment_tables(db)
    
    amount = data.get("amount", 0)
    if amount < 10:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Minimum 10 TL"})
    
    merchant_oid = f"AGTR{current_user.id}_{int(datetime.now().timestamp())}"
    
    # Kullanıcı bilgileri
    user_ip = request.client.host
    email = current_user.email or "user@agtrmerkezi.com"
    
    # PayTR için gerekli parametreler
    payment_amount = int(amount * 100)  # Kuruş cinsinden
    
    # Basket (JSON)
    basket = json.dumps([[
        "Bakiye Yükleme",
        str(amount),
        1
    ]])
    basket_b64 = base64.b64encode(basket.encode()).decode()
    
    # Hash oluştur
    hash_str = f"{PAYTR_MERCHANT_ID}{user_ip}{merchant_oid}{email}{payment_amount}basket{0}{0}TRYTR{PAYTR_MERCHANT_SALT}"
    paytr_token = base64.b64encode(
        hmac.new(PAYTR_MERCHANT_KEY.encode(), hash_str.encode(), hashlib.sha256).digest()
    ).decode()
    
    # DB'ye kaydet
    db.execute(text("""
        INSERT INTO payment_transactions (user_id, gateway, merchant_oid, amount, status)
        VALUES (:uid, 'paytr', :oid, :amt, 'pending')
    """), {"uid": current_user.id, "oid": merchant_oid, "amt": amount})
    db.commit()
    
    return {
        "success": True,
        "merchant_oid": merchant_oid,
        "amount": amount,
        "paytr_token": paytr_token,
        "user_basket": basket_b64,
        # Frontend bu bilgilerle iframe oluşturacak
    }


@router.post("/paytr/callback")
async def paytr_callback(request: Request, db: Session = Depends(get_db)):
    """📥 PayTR callback"""
    form = await request.form()
    
    merchant_oid = form.get("merchant_oid")
    status = form.get("status")
    total_amount = form.get("total_amount")
    hash_val = form.get("hash")
    
    # Hash doğrula
    hash_str = f"{merchant_oid}{PAYTR_MERCHANT_SALT}{status}{total_amount}"
    calculated = base64.b64encode(
        hmac.new(PAYTR_MERCHANT_KEY.encode(), hash_str.encode(), hashlib.sha256).digest()
    ).decode()
    
    if hash_val != calculated:
        return HTMLResponse("HASH_ERROR")
    
    # İşlemi bul
    tx = db.execute(text(
        "SELECT id, user_id, amount FROM payment_transactions WHERE merchant_oid = :oid"
    ), {"oid": merchant_oid}).fetchone()
    
    if not tx:
        return HTMLResponse("ORDER_NOT_FOUND")
    
    if status == "success":
        # Bakiye ekle
        await add_balance(db, tx[1], float(tx[2]), "deposit", "PayTR ile yükleme", merchant_oid, "paytr")
        
        db.execute(text("""
            UPDATE payment_transactions SET status = 'success', completed_at = NOW()
            WHERE merchant_oid = :oid
        """), {"oid": merchant_oid})
    else:
        db.execute(text("""
            UPDATE payment_transactions SET status = 'failed', error_message = :err
            WHERE merchant_oid = :oid
        """), {"oid": merchant_oid, "err": form.get("failed_reason_msg", "Ödeme başarısız")})
    
    db.commit()
    return HTMLResponse("OK")


# ============================================================================
# IYZICO ENTEGRASYONU
# ============================================================================

@router.post("/iyzico/create")
async def create_iyzico_payment(
    data: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """💳 iyzico ödeme başlat"""
    ensure_payment_tables(db)
    
    amount = data.get("amount", 0)
    if amount < 10:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Minimum 10 TL"})
    
    conversation_id = f"AGTR{current_user.id}_{int(datetime.now().timestamp())}"
    
    # DB'ye kaydet
    db.execute(text("""
        INSERT INTO payment_transactions (user_id, gateway, merchant_oid, amount, status)
        VALUES (:uid, 'iyzico', :oid, :amt, 'pending')
    """), {"uid": current_user.id, "oid": conversation_id, "amt": amount})
    db.commit()
    
    # iyzico API çağrısı burada yapılacak
    # Şimdilik placeholder
    
    return {
        "success": True,
        "conversation_id": conversation_id,
        "amount": amount,
        "checkout_url": f"{IYZICO_BASE_URL}/checkout?id={conversation_id}"
    }


# ============================================================================
# HAVALE/EFT
# ============================================================================

@router.post("/bank-transfer")
async def create_bank_transfer(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🏦 Havale/EFT bildirimi"""
    ensure_payment_tables(db)
    
    amount = data.get("amount", 0)
    bank_name = data.get("bank_name", "")
    sender_name = data.get("sender_name", "")
    reference_no = data.get("reference_no", "")
    transfer_date = data.get("transfer_date")
    notes = data.get("notes", "")
    
    if amount < 10:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Minimum 10 TL"})
    
    db.execute(text("""
        INSERT INTO bank_transfers (user_id, amount, bank_name, sender_name, reference_no, transfer_date, notes)
        VALUES (:uid, :amt, :bank, :sender, :ref, :date, :notes)
    """), {
        "uid": current_user.id, "amt": amount, "bank": bank_name,
        "sender": sender_name, "ref": reference_no, "date": transfer_date, "notes": notes
    })
    db.commit()
    
    return {"success": True, "message": "Havale bildirimi alındı. Onay sonrası bakiyenize eklenecektir."}


@router.get("/bank-transfers")
async def list_bank_transfers(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Havale bildirimleri"""
    ensure_payment_tables(db)
    
    # Admin tüm bildirimleri görebilir
    if current_user.role.value >= 2:
        q = "SELECT bt.*, u.username FROM bank_transfers bt LEFT JOIN users u ON bt.user_id = u.id WHERE 1=1"
        p = {}
    else:
        q = "SELECT * FROM bank_transfers WHERE user_id = :uid"
        p = {"uid": current_user.id}
    
    if status:
        q += " AND status = :st"
        p["st"] = status
    
    q += " ORDER BY created_at DESC LIMIT 100"
    
    rows = db.execute(text(q), p).fetchall()
    transfers = [{
        "id": r[0], "amount": float(r[2]), "bank_name": r[3],
        "sender_name": r[4], "reference_no": r[5], "status": r[8],
        "created_at": r[11].isoformat() if r[11] else None
    } for r in rows]
    
    return {"success": True, "transfers": transfers}


@router.post("/bank-transfers/{transfer_id}/approve")
async def approve_bank_transfer(
    transfer_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """✅ Havale onayla"""
    if current_user.role.value < 2:
        raise HTTPException(403, "Yetkiniz yok")
    
    transfer = db.execute(text(
        "SELECT user_id, amount, status FROM bank_transfers WHERE id = :id"
    ), {"id": transfer_id}).fetchone()
    
    if not transfer:
        raise HTTPException(404, "Bildirim bulunamadı")
    
    if transfer[2] != "pending":
        return JSONResponse(status_code=400, content={"success": False, "detail": "Bu bildirim zaten işlenmiş"})
    
    action = data.get("action", "approve")
    admin_note = data.get("admin_note", "")
    
    if action == "approve":
        # Bakiye ekle
        await add_balance(db, transfer[0], float(transfer[1]), "deposit", 
                         "Havale/EFT ile yükleme", str(transfer_id), "bank_transfer")
        
        db.execute(text("""
            UPDATE bank_transfers SET status = 'approved', admin_note = :note,
            processed_by = :admin, processed_at = NOW() WHERE id = :id
        """), {"id": transfer_id, "note": admin_note, "admin": current_user.id})
    else:
        db.execute(text("""
            UPDATE bank_transfers SET status = 'rejected', admin_note = :note,
            processed_by = :admin, processed_at = NOW() WHERE id = :id
        """), {"id": transfer_id, "note": admin_note, "admin": current_user.id})
    
    db.commit()
    return {"success": True, "message": f"Bildirim {'onaylandı' if action == 'approve' else 'reddedildi'}"}


# ============================================================================
# FATURA SİSTEMİ
# ============================================================================

@router.get("/invoices")
async def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Faturalar"""
    ensure_payment_tables(db)
    
    if current_user.role.value >= 2:
        q = "SELECT i.*, u.username FROM invoices i LEFT JOIN users u ON i.user_id = u.id ORDER BY i.created_at DESC LIMIT 100"
        rows = db.execute(text(q)).fetchall()
    else:
        rows = db.execute(text("""
            SELECT * FROM invoices WHERE user_id = :uid ORDER BY created_at DESC LIMIT 50
        """), {"uid": current_user.id}).fetchall()
    
    invoices = [{
        "id": r[0], "invoice_no": r[1], "total": float(r[7]),
        "status": r[8], "created_at": r[14].isoformat() if r[14] else None
    } for r in rows]
    
    return {"success": True, "invoices": invoices}


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔍 Fatura detayı"""
    invoice = db.execute(text(
        "SELECT * FROM invoices WHERE id = :id"
    ), {"id": invoice_id}).fetchone()
    
    if not invoice:
        raise HTTPException(404, "Fatura bulunamadı")
    
    if invoice[2] != current_user.id and current_user.role.value < 2:
        raise HTTPException(403, "Yetkiniz yok")
    
    items = db.execute(text(
        "SELECT * FROM invoice_items WHERE invoice_id = :id"
    ), {"id": invoice_id}).fetchall()
    
    return {
        "success": True,
        "invoice": {
            "id": invoice[0], "invoice_no": invoice[1],
            "subtotal": float(invoice[4]), "discount": float(invoice[5]),
            "tax": float(invoice[6]), "total": float(invoice[7]),
            "status": invoice[8], "billing_name": invoice[9],
            "billing_address": invoice[10]
        },
        "items": [{
            "description": i[2], "quantity": i[3],
            "unit_price": float(i[4]), "total": float(i[5])
        } for i in items]
    }


async def create_invoice(db: Session, user_id: int, items: list, billing_info: dict = None):
    """Fatura oluştur"""
    ensure_payment_tables(db)
    
    # Fatura numarası
    year = datetime.now().year
    count = db.execute(text(
        "SELECT COUNT(*) FROM invoices WHERE YEAR(created_at) = :y"
    ), {"y": year}).fetchone()[0]
    invoice_no = f"AGTR{year}{count + 1:05d}"
    
    # Hesaplamalar
    subtotal = sum(i["quantity"] * i["unit_price"] for i in items)
    discount = billing_info.get("discount", 0) if billing_info else 0
    tax = (subtotal - discount) * 0.20  # %20 KDV
    total = subtotal - discount + tax
    
    # Fatura oluştur
    r = db.execute(text("""
        INSERT INTO invoices (invoice_no, user_id, subtotal, discount, tax, total, status,
            billing_name, billing_address, billing_tax_no)
        VALUES (:no, :uid, :sub, :disc, :tax, :total, 'draft', :name, :addr, :taxno)
    """), {
        "no": invoice_no, "uid": user_id, "sub": subtotal, "disc": discount,
        "tax": tax, "total": total,
        "name": billing_info.get("name") if billing_info else None,
        "addr": billing_info.get("address") if billing_info else None,
        "taxno": billing_info.get("tax_no") if billing_info else None
    })
    invoice_id = r.lastrowid
    
    # Fatura kalemleri
    for item in items:
        db.execute(text("""
            INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, total)
            VALUES (:iid, :desc, :qty, :price, :total)
        """), {
            "iid": invoice_id, "desc": item["description"],
            "qty": item["quantity"], "price": item["unit_price"],
            "total": item["quantity"] * item["unit_price"]
        })
    
    db.commit()
    return invoice_id, invoice_no


# ============================================================================
# ÖDEME İSTATİSTİKLERİ
# ============================================================================

@router.get("/stats")
async def payment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Ödeme istatistikleri"""
    if current_user.role.value < 2:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_payment_tables(db)
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today.replace(day=1)
    
    stats = {}
    
    # Bugünkü gelir
    stats["today_revenue"] = float(db.execute(text("""
        SELECT COALESCE(SUM(amount), 0) FROM payment_transactions 
        WHERE status = 'success' AND completed_at > :today
    """), {"today": today}).fetchone()[0])
    
    # Aylık gelir
    stats["monthly_revenue"] = float(db.execute(text("""
        SELECT COALESCE(SUM(amount), 0) FROM payment_transactions 
        WHERE status = 'success' AND completed_at > :month
    """), {"month": month_start}).fetchone()[0])
    
    # Bekleyen havale
    stats["pending_transfers"] = db.execute(text(
        "SELECT COUNT(*) FROM bank_transfers WHERE status = 'pending'"
    )).fetchone()[0]
    
    # Aktif kupon sayısı
    stats["active_coupons"] = db.execute(text(
        "SELECT COUNT(*) FROM coupons WHERE is_active = TRUE"
    )).fetchone()[0]
    
    return {"success": True, "stats": stats}
