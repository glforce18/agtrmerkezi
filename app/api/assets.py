"""
🖼️ AGTR Asset Manager API
Logo, görsel ve animasyon yönetimi (rembg olmadan)
"""
import io
import os
import re
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from PIL import Image
    PIL_OK = True
except ImportError:
    PIL_OK = False

from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User

router = APIRouter()

UPLOAD_DIR = Path("static/uploads/assets")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp"
}


def slugify(t):
    """Türkçe destekli slug"""
    if not t:
        return "asset"
    for tr, en in {'ç':'c','ğ':'g','ı':'i','ö':'o','ş':'s','ü':'u',
                   'Ç':'C','Ğ':'G','İ':'I','Ö':'O','Ş':'S','Ü':'U'}.items():
        t = t.replace(tr, en)
    return re.sub(r'[\s_]+', '-', re.sub(r'[^a-zA-Z0-9\s-]', '', t)).lower().strip('-')[:50] or "asset"


def ensure_table(db):
    """Tablo oluştur"""
    try:
        db.execute(text("""CREATE TABLE IF NOT EXISTS site_assets(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            slug VARCHAR(255),
            description TEXT,
            asset_type VARCHAR(50) DEFAULT 'other',
            original_path VARCHAR(500),
            processed_path VARCHAR(500),
            thumbnail_path VARCHAR(500),
            file_size INT,
            width INT,
            height INT,
            is_animated BOOLEAN DEFAULT FALSE,
            animation_type VARCHAR(50),
            animation_duration FLOAT DEFAULT 2.0,
            uploaded_by INT,
            status VARCHAR(20) DEFAULT 'ready',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        db.commit()
    except Exception:
        db.rollback()


@router.post("/upload")
async def upload_asset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    asset_type: str = Form("other"),
    remove_background: bool = Form(False),
    animation_type: str = Form(""),
    animation_duration: float = Form(2.0),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user)
):
    """📤 Asset yükle"""
    try:
        ensure_table(db)
        
        # Dosya tipi kontrolü
        if file.content_type not in ALLOWED:
            return JSONResponse(
                status_code=400,
                content={"success": False, "detail": "Geçersiz dosya tipi. PNG, JPG, GIF, WEBP kabul edilir."}
            )
        
        # Dosya içeriğini oku
        contents = await file.read()
        
        # Boyut kontrolü
        if len(contents) > MAX_SIZE:
            return JSONResponse(
                status_code=400,
                content={"success": False, "detail": "Dosya çok büyük (max 10MB)"}
            )
        
        # Dosya isimleri
        slug = slugify(name)
        uid = uuid.uuid4().hex[:8]
        base = f"{slug}_{uid}"
        
        orig_p = UPLOAD_DIR / f"{base}_original.png"
        proc_p = UPLOAD_DIR / f"{base}_processed.png"
        thumb_p = UPLOAD_DIR / f"{base}_thumb.png"
        
        w, h = 0, 0
        
        if PIL_OK:
            try:
                img = Image.open(io.BytesIO(contents))
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                w, h = img.width, img.height
                
                # Original kaydet
                img.save(orig_p, "PNG")
                
                # Processed (max 800px)
                proc = img.copy()
                if proc.width > 800:
                    proc.thumbnail((800, 800), Image.Resampling.LANCZOS)
                proc.save(proc_p, "PNG")
                
                # Thumbnail (200px)
                thumb = img.copy()
                thumb.thumbnail((200, 200), Image.Resampling.LANCZOS)
                thumb.save(thumb_p, "PNG")
            except Exception:
                # PIL hatası, raw kaydet
                for p in [orig_p, proc_p, thumb_p]:
                    with open(p, 'wb') as f:
                        f.write(contents)
        else:
            # PIL yok, raw kaydet
            for p in [orig_p, proc_p, thumb_p]:
                with open(p, 'wb') as f:
                    f.write(contents)
        
        is_anim = bool(animation_type and animation_type.strip())
        
        # Database'e kaydet
        r = db.execute(text("""
            INSERT INTO site_assets (name, slug, description, asset_type, original_path, 
                processed_path, thumbnail_path, file_size, width, height, is_animated, 
                animation_type, animation_duration, uploaded_by, status)
            VALUES (:n, :s, :d, :t, :op, :pp, :tp, :fs, :w, :h, :ia, :at, :ad, :ub, 'ready')
        """), {
            "n": name, "s": slug, "d": description, "t": asset_type,
            "op": str(orig_p), "pp": str(proc_p), "tp": str(thumb_p),
            "fs": len(contents), "w": w, "h": h, "ia": is_anim,
            "at": animation_type if is_anim else None, "ad": animation_duration,
            "ub": current_user.id
        })
        db.commit()
        
        return {
            "success": True,
            "message": "Asset başarıyla yüklendi",
            "asset": {"id": r.lastrowid, "name": name, "slug": slug}
        }
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"success": False, "detail": str(e)})


@router.get("/list")
async def list_assets(
    asset_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """📋 Asset listesi"""
    try:
        ensure_table(db)
        q = "SELECT * FROM site_assets WHERE status = 'ready'"
        p = {}
        
        if asset_type:
            q += " AND asset_type = :t"
            p["t"] = asset_type
        
        if search:
            q += " AND name LIKE :s"
            p["s"] = f"%{search}%"
        
        q += " ORDER BY created_at DESC LIMIT 100"
        
        rows = db.execute(text(q), p).fetchall()
        
        assets = [{
            "id": r[0],
            "name": r[1],
            "slug": r[2],
            "description": r[3],
            "asset_type": r[4],
            "thumbnail_url": f"/api/assets/file/{r[0]}/thumbnail",
            "processed_url": f"/api/assets/file/{r[0]}/processed",
            "original_url": f"/api/assets/file/{r[0]}/original",
            "file_size": r[8],
            "width": r[9],
            "height": r[10],
            "is_animated": bool(r[11]),
            "animation_type": r[12],
            "animation_duration": r[13]
        } for r in rows]
        
        return {"success": True, "total": len(assets), "assets": assets}
    except Exception as e:
        return {"success": True, "total": 0, "assets": [], "error": str(e)}


@router.get("/file/{asset_id}/{file_type}")
async def get_file(asset_id: int, file_type: str, db: Session = Depends(get_db)):
    """📁 Asset dosyası"""
    r = db.execute(text(
        "SELECT original_path, processed_path, thumbnail_path FROM site_assets WHERE id = :id"
    ), {"id": asset_id}).fetchone()
    
    if not r:
        raise HTTPException(404, "Asset bulunamadı")
    
    idx = {"original": 0, "processed": 1, "thumbnail": 2}.get(file_type, 1)
    path = r[idx]
    
    if not path or not os.path.exists(path):
        # Fallback
        for fb in [r[1], r[0]]:
            if fb and os.path.exists(fb):
                path = fb
                break
        else:
            raise HTTPException(404, "Dosya bulunamadı")
    
    return FileResponse(path, media_type="image/png")


@router.get("/{asset_id}")
async def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """🔍 Asset detayı"""
    r = db.execute(text("SELECT * FROM site_assets WHERE id = :id"), {"id": asset_id}).fetchone()
    
    if not r:
        raise HTTPException(404, "Asset bulunamadı")
    
    return {
        "success": True,
        "asset": {
            "id": r[0], "name": r[1], "slug": r[2], "description": r[3],
            "asset_type": r[4], "file_size": r[8], "width": r[9], "height": r[10],
            "is_animated": bool(r[11]), "animation_type": r[12], "animation_duration": r[13]
        }
    }


@router.put("/{asset_id}")
async def update_asset(
    asset_id: int,
    data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user)
):
    """✏️ Asset güncelle"""
    r = db.execute(text("SELECT id FROM site_assets WHERE id = :id"), {"id": asset_id}).fetchone()
    if not r:
        raise HTTPException(404, "Asset bulunamadı")
    
    updates = []
    params = {"id": asset_id}
    
    if "name" in data:
        updates.append("name = :n")
        params["n"] = data["name"]
    if "description" in data:
        updates.append("description = :d")
        params["d"] = data["description"]
    if "asset_type" in data:
        updates.append("asset_type = :t")
        params["t"] = data["asset_type"]
    if "animation_type" in data:
        updates.append("animation_type = :at")
        params["at"] = data["animation_type"]
    if "animation_duration" in data:
        updates.append("animation_duration = :ad")
        params["ad"] = data["animation_duration"]
    
    if updates:
        db.execute(text(f"UPDATE site_assets SET {', '.join(updates)} WHERE id = :id"), params)
        db.commit()
    
    return {"success": True, "message": "Asset güncellendi"}


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user)
):
    """🗑️ Asset sil"""
    r = db.execute(text(
        "SELECT original_path, processed_path, thumbnail_path FROM site_assets WHERE id = :id"
    ), {"id": asset_id}).fetchone()
    
    if not r:
        raise HTTPException(404, "Asset bulunamadı")
    
    # Dosyaları sil
    for p in r:
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass
    
    # DB'den sil
    db.execute(text("DELETE FROM site_assets WHERE id = :id"), {"id": asset_id})
    db.commit()
    
    return {"success": True, "message": "Asset silindi"}
