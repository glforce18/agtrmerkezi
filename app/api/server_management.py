"""
🖥️ AGTR Server Management API
Backup System, Resource Monitor, Scheduled Tasks, FTP Manager
"""
import os
import shutil
import subprocess
from datetime import datetime, timedelta
from typing import Optional

import psutil
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User, UserRole

router = APIRouter()

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVERS_PATH = settings.HLDS_PATH
BACKUPS_PATH = "/var/www/backups/servers"
MAX_BACKUPS_PER_SERVER = 5

# ============================================================================
# DATABASE TABLES
# ============================================================================

def ensure_management_tables(db: Session):
    """Yönetim tablolarını oluştur"""
    try:
        # Sunucu backupları
        db.execute(text("""CREATE TABLE IF NOT EXISTS server_backups (
            id INT AUTO_INCREMENT PRIMARY KEY,
            server_id INT NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_size BIGINT,
            backup_type ENUM('manual', 'auto', 'pre_update') DEFAULT 'manual',
            status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
            notes TEXT,
            created_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_server (server_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Resource monitoring
        db.execute(text("""CREATE TABLE IF NOT EXISTS resource_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            server_id INT NOT NULL,
            cpu_percent FLOAT,
            memory_mb FLOAT,
            memory_percent FLOAT,
            disk_mb FLOAT,
            disk_percent FLOAT,
            network_in_kb FLOAT,
            network_out_kb FLOAT,
            player_count INT,
            recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_server_time (server_id, recorded_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Scheduled tasks
        db.execute(text("""CREATE TABLE IF NOT EXISTS scheduled_tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            server_id INT,
            task_type VARCHAR(50) NOT NULL,
            task_name VARCHAR(100),
            schedule_type ENUM('once', 'daily', 'weekly', 'monthly') DEFAULT 'daily',
            schedule_time TIME,
            schedule_day INT,
            command TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            last_run DATETIME,
            next_run DATETIME,
            created_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_server (server_id),
            INDEX idx_next_run (next_run)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Task execution logs
        db.execute(text("""CREATE TABLE IF NOT EXISTS task_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            task_id INT NOT NULL,
            server_id INT,
            status ENUM('success', 'failed', 'running') DEFAULT 'running',
            output TEXT,
            error_message TEXT,
            started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            INDEX idx_task (task_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Server uptime
        db.execute(text("""CREATE TABLE IF NOT EXISTS server_uptime (
            id INT AUTO_INCREMENT PRIMARY KEY,
            server_id INT NOT NULL,
            status ENUM('online', 'offline', 'restarting') NOT NULL,
            recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_server_time (server_id, recorded_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        db.commit()
    except Exception:
        db.rollback()


# ============================================================================
# BACKUP SYSTEM
# ============================================================================

@router.get("/backups")
async def list_backups(
    server_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Backup listesi"""
    ensure_management_tables(db)
    
    q = "SELECT * FROM server_backups WHERE 1=1"
    p = {}
    
    if server_id:
        q += " AND server_id = :sid"
        p["sid"] = server_id
    
    # Normal kullanıcı sadece kendi sunucularını görebilir
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        q += " AND server_id IN (SELECT id FROM game_servers WHERE user_id = :uid)"
        p["uid"] = current_user.id
    
    q += " ORDER BY created_at DESC LIMIT 100"
    
    rows = db.execute(text(q), p).fetchall()
    backups = [{
        "id": r[0], "server_id": r[1], "filename": r[2],
        "file_size": r[4], "backup_type": r[5], "status": r[6],
        "notes": r[7], "created_at": r[9].isoformat() if r[9] else None
    } for r in rows]
    
    return {"success": True, "backups": backups}


@router.post("/backups/create")
async def create_backup(
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """➕ Backup oluştur"""
    ensure_management_tables(db)
    
    server_id = data.get("server_id")
    notes = data.get("notes", "")
    backup_type = data.get("type", "manual")
    
    # Sunucu kontrolü
    server = db.execute(text("""
        SELECT id, name, user_id, server_path FROM game_servers WHERE id = :id
    """), {"id": server_id}).fetchone()
    
    if not server:
        raise HTTPException(404, "Sunucu bulunamadı")
    
    # Yetki kontrolü
    if server[2] != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    # Backup kaydı oluştur
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"server_{server_id}_{timestamp}.tar.gz"
    file_path = os.path.join(BACKUPS_PATH, str(server_id), filename)
    
    r = db.execute(text("""
        INSERT INTO server_backups (server_id, filename, file_path, backup_type, notes, created_by)
        VALUES (:sid, :fn, :fp, :bt, :notes, :uid)
    """), {
        "sid": server_id, "fn": filename, "fp": file_path,
        "bt": backup_type, "notes": notes, "uid": current_user.id
    })
    backup_id = r.lastrowid
    db.commit()
    
    # Background'da backup oluştur
    background_tasks.add_task(create_backup_task, db, backup_id, server[3], file_path)
    
    return {"success": True, "backup_id": backup_id, "message": "Backup işlemi başlatıldı"}


async def create_backup_task(db: Session, backup_id: int, server_path: str, output_path: str):
    """Backup oluşturma görevi"""
    try:
        # Dizin oluştur
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # tar.gz oluştur
        result = subprocess.run(
            ["tar", "-czf", output_path, "-C", os.path.dirname(server_path), os.path.basename(server_path)],
            capture_output=True, timeout=600
        )
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_path)
            db.execute(text("""
                UPDATE server_backups SET status = 'completed', file_size = :size WHERE id = :id
            """), {"id": backup_id, "size": file_size})
        else:
            db.execute(text("""
                UPDATE server_backups SET status = 'failed', notes = CONCAT(COALESCE(notes, ''), ' Error: ', :err) WHERE id = :id
            """), {"id": backup_id, "err": result.stderr.decode()[:500]})
        
        db.commit()
        
        # Eski backupları temizle
        await cleanup_old_backups(db, backup_id)
        
    except Exception as e:
        db.execute(text("""
            UPDATE server_backups SET status = 'failed', notes = CONCAT(COALESCE(notes, ''), ' Error: ', :err) WHERE id = :id
        """), {"id": backup_id, "err": str(e)[:500]})
        db.commit()


async def cleanup_old_backups(db: Session, backup_id: int):
    """Eski backupları temizle"""
    backup = db.execute(text("SELECT server_id FROM server_backups WHERE id = :id"), {"id": backup_id}).fetchone()
    if not backup:
        return
    
    # En eski backupları bul
    old_backups = db.execute(text("""
        SELECT id, file_path FROM server_backups 
        WHERE server_id = :sid AND status = 'completed'
        ORDER BY created_at DESC
        LIMIT 100 OFFSET :offset
    """), {"sid": backup[0], "offset": MAX_BACKUPS_PER_SERVER}).fetchall()
    
    for ob in old_backups:
        try:
            if os.path.exists(ob[1]):
                os.remove(ob[1])
            db.execute(text("DELETE FROM server_backups WHERE id = :id"), {"id": ob[0]})
        except Exception:
            pass
    
    db.commit()


@router.get("/backups/{backup_id}/download")
async def download_backup(
    backup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📥 Backup indir"""
    backup = db.execute(text("""
        SELECT b.*, s.user_id FROM server_backups b
        JOIN game_servers s ON b.server_id = s.id
        WHERE b.id = :id
    """), {"id": backup_id}).fetchone()
    
    if not backup:
        raise HTTPException(404, "Backup bulunamadı")
    
    if backup[10] != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    if not os.path.exists(backup[3]):
        raise HTTPException(404, "Backup dosyası bulunamadı")
    
    return FileResponse(backup[3], filename=backup[2], media_type="application/gzip")


@router.post("/backups/{backup_id}/restore")
async def restore_backup(
    backup_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🔄 Backup'tan geri yükle"""
    backup = db.execute(text("""
        SELECT b.*, s.user_id, s.server_path FROM server_backups b
        JOIN game_servers s ON b.server_id = s.id
        WHERE b.id = :id
    """), {"id": backup_id}).fetchone()
    
    if not backup:
        raise HTTPException(404, "Backup bulunamadı")
    
    if backup[10] != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    # Background'da restore
    background_tasks.add_task(restore_backup_task, backup[3], backup[11])
    
    return {"success": True, "message": "Geri yükleme başlatıldı"}


async def restore_backup_task(backup_path: str, server_path: str):
    """Backup geri yükleme görevi"""
    try:
        # Önce mevcut sunucuyu yedekle
        temp_backup = f"{server_path}.temp_backup"
        if os.path.exists(server_path):
            shutil.move(server_path, temp_backup)
        
        # Backup'ı aç
        result = subprocess.run(
            ["tar", "-xzf", backup_path, "-C", os.path.dirname(server_path)],
            capture_output=True, timeout=600
        )
        
        if result.returncode == 0:
            # Başarılı, temp backup'ı sil
            if os.path.exists(temp_backup):
                shutil.rmtree(temp_backup)
        else:
            # Hata, eski halini geri getir
            if os.path.exists(temp_backup):
                if os.path.exists(server_path):
                    shutil.rmtree(server_path)
                shutil.move(temp_backup, server_path)
    except Exception as e:
        print(f"Restore error: {e}")


# ============================================================================
# RESOURCE MONITOR
# ============================================================================

@router.get("/resources/{server_id}")
async def get_server_resources(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Sunucu kaynak kullanımı"""
    ensure_management_tables(db)
    
    # Son kayıtları al
    rows = db.execute(text("""
        SELECT * FROM resource_logs WHERE server_id = :sid
        ORDER BY recorded_at DESC LIMIT 60
    """), {"sid": server_id}).fetchall()
    
    if not rows:
        return {"success": True, "resources": [], "current": None}
    
    resources = [{
        "cpu": r[2], "memory_mb": r[3], "memory_percent": r[4],
        "disk_mb": r[5], "disk_percent": r[6],
        "network_in": r[7], "network_out": r[8], "players": r[9],
        "recorded_at": r[10].isoformat() if r[10] else None
    } for r in rows]
    
    return {"success": True, "resources": resources, "current": resources[0] if resources else None}


@router.get("/resources/{server_id}/live")
async def get_live_resources(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Anlık kaynak kullanımı"""
    # Sunucu process ID'sini bul
    server = db.execute(text("""
        SELECT server_path, port FROM game_servers WHERE id = :id
    """), {"id": server_id}).fetchone()
    
    if not server:
        raise HTTPException(404, "Sunucu bulunamadı")
    
    try:
        # Process bul
        port = server[1]
        process = None
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if str(port) in cmdline and ('hlds' in cmdline.lower() or 'srcds' in cmdline.lower()):
                    process = proc
                    break
            except Exception:
                continue
        
        if process:
            cpu = process.cpu_percent(interval=0.5)
            mem = process.memory_info()
            
            return {
                "success": True,
                "live": {
                    "pid": process.pid,
                    "cpu_percent": cpu,
                    "memory_mb": mem.rss / (1024 * 1024),
                    "status": "online"
                }
            }
        else:
            return {"success": True, "live": {"status": "offline"}}
    except Exception as e:
        return {"success": True, "live": {"status": "unknown", "error": str(e)}}


async def record_resources(db: Session, server_id: int, cpu: float, memory_mb: float, 
                          memory_pct: float, players: int = 0):
    """Kaynak kullanımını kaydet"""
    ensure_management_tables(db)
    db.execute(text("""
        INSERT INTO resource_logs (server_id, cpu_percent, memory_mb, memory_percent, player_count)
        VALUES (:sid, :cpu, :mem, :mempct, :players)
    """), {"sid": server_id, "cpu": cpu, "mem": memory_mb, "mempct": memory_pct, "players": players})
    db.commit()


# ============================================================================
# SCHEDULED TASKS
# ============================================================================

@router.get("/tasks")
async def list_scheduled_tasks(
    server_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📋 Zamanlanmış görevler"""
    ensure_management_tables(db)
    
    q = "SELECT * FROM scheduled_tasks WHERE 1=1"
    p = {}
    
    if server_id:
        q += " AND server_id = :sid"
        p["sid"] = server_id
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        q += " AND server_id IN (SELECT id FROM game_servers WHERE user_id = :uid)"
        p["uid"] = current_user.id
    
    q += " ORDER BY next_run"
    
    rows = db.execute(text(q), p).fetchall()
    tasks = [{
        "id": r[0], "server_id": r[1], "task_type": r[2], "task_name": r[3],
        "schedule_type": r[4], "schedule_time": str(r[5]) if r[5] else None,
        "is_active": bool(r[8]), "last_run": r[9].isoformat() if r[9] else None,
        "next_run": r[10].isoformat() if r[10] else None
    } for r in rows]
    
    return {"success": True, "tasks": tasks}


@router.post("/tasks")
async def create_scheduled_task(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """➕ Zamanlanmış görev oluştur"""
    ensure_management_tables(db)
    
    server_id = data.get("server_id")
    task_type = data.get("task_type")  # restart, backup, command
    task_name = data.get("task_name", "")
    schedule_type = data.get("schedule_type", "daily")
    schedule_time = data.get("schedule_time", "04:00")
    schedule_day = data.get("schedule_day")
    command = data.get("command")
    
    # Sunucu yetki kontrolü
    if server_id:
        server = db.execute(text("SELECT user_id FROM game_servers WHERE id = :id"), {"id": server_id}).fetchone()
        if not server:
            raise HTTPException(404, "Sunucu bulunamadı")
        if server[0] != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            raise HTTPException(403, "Yetkiniz yok")
    
    # Next run hesapla
    now = datetime.now()
    time_parts = schedule_time.split(":")
    next_run = now.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=0, microsecond=0)
    
    if next_run <= now:
        if schedule_type == "daily":
            next_run += timedelta(days=1)
        elif schedule_type == "weekly":
            next_run += timedelta(weeks=1)
    
    r = db.execute(text("""
        INSERT INTO scheduled_tasks (server_id, task_type, task_name, schedule_type, 
            schedule_time, schedule_day, command, next_run, created_by)
        VALUES (:sid, :type, :name, :stype, :stime, :sday, :cmd, :next, :uid)
    """), {
        "sid": server_id, "type": task_type, "name": task_name, "stype": schedule_type,
        "stime": schedule_time, "sday": schedule_day, "cmd": command,
        "next": next_run, "uid": current_user.id
    })
    db.commit()
    
    return {"success": True, "task_id": r.lastrowid, "message": "Görev oluşturuldu"}


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🗑️ Görevi sil"""
    task = db.execute(text("""
        SELECT t.*, s.user_id FROM scheduled_tasks t
        LEFT JOIN game_servers s ON t.server_id = s.id
        WHERE t.id = :id
    """), {"id": task_id}).fetchone()
    
    if not task:
        raise HTTPException(404, "Görev bulunamadı")
    
    # Yetki kontrolü
    if task[14] and task[14] != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    db.execute(text("DELETE FROM scheduled_tasks WHERE id = :id"), {"id": task_id})
    db.commit()
    
    return {"success": True, "message": "Görev silindi"}


@router.post("/tasks/{task_id}/run")
async def run_task_now(
    task_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """▶️ Görevi şimdi çalıştır"""
    task = db.execute(text("SELECT * FROM scheduled_tasks WHERE id = :id"), {"id": task_id}).fetchone()
    
    if not task:
        raise HTTPException(404, "Görev bulunamadı")
    
    background_tasks.add_task(execute_task, db, task_id)
    
    return {"success": True, "message": "Görev başlatıldı"}


async def execute_task(db: Session, task_id: int):
    """Görevi çalıştır"""
    task = db.execute(text("SELECT * FROM scheduled_tasks WHERE id = :id"), {"id": task_id}).fetchone()
    if not task:
        return
    
    # Log başlat
    log_r = db.execute(text("""
        INSERT INTO task_logs (task_id, server_id, status) VALUES (:tid, :sid, 'running')
    """), {"tid": task_id, "sid": task[1]})
    log_id = log_r.lastrowid
    db.commit()
    
    try:
        output = ""
        
        if task[2] == "restart":
            # Sunucu restart
            result = subprocess.run(
                [f"{settings.HLDS_PATH}/server_manager.sh", "restart", str(task[1])],
                capture_output=True, timeout=120
            )
            output = result.stdout.decode()
            result.stderr.decode()
            
        elif task[2] == "backup":
            # Backup oluştur
            # create_backup_task çağır
            output = "Backup görevi başlatıldı"
            
        elif task[2] == "command":
            # Özel komut
            result = subprocess.run(
                task[7].split(), capture_output=True, timeout=60
            )
            output = result.stdout.decode()
            result.stderr.decode()
        
        # Başarılı
        db.execute(text("""
            UPDATE task_logs SET status = 'success', output = :out, completed_at = NOW()
            WHERE id = :id
        """), {"id": log_id, "out": output[:5000]})
        
        # Last run güncelle ve next run hesapla
        now = datetime.now()
        if task[4] == "daily":
            next_run = now + timedelta(days=1)
        elif task[4] == "weekly":
            next_run = now + timedelta(weeks=1)
        elif task[4] == "monthly":
            next_run = now + timedelta(days=30)
        else:
            next_run = None
        
        db.execute(text("""
            UPDATE scheduled_tasks SET last_run = NOW(), next_run = :next WHERE id = :id
        """), {"id": task_id, "next": next_run})
        
    except Exception as e:
        db.execute(text("""
            UPDATE task_logs SET status = 'failed', error_message = :err, completed_at = NOW()
            WHERE id = :id
        """), {"id": log_id, "err": str(e)[:1000]})
    
    db.commit()


# ============================================================================
# SERVER UPTIME
# ============================================================================

@router.get("/uptime/{server_id}")
async def get_server_uptime(
    server_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """📊 Sunucu uptime raporu"""
    ensure_management_tables(db)
    
    since = datetime.now() - timedelta(days=days)
    
    rows = db.execute(text("""
        SELECT status, recorded_at FROM server_uptime
        WHERE server_id = :sid AND recorded_at > :since
        ORDER BY recorded_at
    """), {"sid": server_id, "since": since}).fetchall()
    
    if not rows:
        return {"success": True, "uptime_percent": 0, "records": []}
    
    # Uptime hesapla
    total_minutes = days * 24 * 60
    online_minutes = 0
    last_status = None
    last_time = since
    
    for status, recorded_at in rows:
        if last_status == "online":
            online_minutes += (recorded_at - last_time).total_seconds() / 60
        last_status = status
        last_time = recorded_at
    
    # Son kayıttan şimdiye kadar
    if last_status == "online":
        online_minutes += (datetime.now() - last_time).total_seconds() / 60
    
    uptime_percent = (online_minutes / total_minutes) * 100 if total_minutes > 0 else 0
    
    return {
        "success": True,
        "uptime_percent": round(uptime_percent, 2),
        "online_hours": round(online_minutes / 60, 1),
        "total_hours": days * 24,
        "days": days
    }


# ============================================================================
# STATS
# ============================================================================

@router.get("/stats")
async def management_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Yönetim istatistikleri"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_management_tables(db)
    
    stats = {}
    
    # Toplam backup sayısı
    stats["total_backups"] = db.execute(text("SELECT COUNT(*) FROM server_backups")).fetchone()[0]
    
    # Backup boyutu
    stats["total_backup_size_mb"] = db.execute(text(
        "SELECT COALESCE(SUM(file_size), 0) / 1048576 FROM server_backups WHERE status = 'completed'"
    )).fetchone()[0]
    
    # Aktif görev sayısı
    stats["active_tasks"] = db.execute(text(
        "SELECT COUNT(*) FROM scheduled_tasks WHERE is_active = TRUE"
    )).fetchone()[0]
    
    # Bugün çalışan görevler
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    stats["tasks_today"] = db.execute(text(
        "SELECT COUNT(*) FROM task_logs WHERE started_at > :today"
    ), {"today": today}).fetchone()[0]
    
    return {"success": True, "stats": stats}
