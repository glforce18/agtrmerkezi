"""
AGTR Merkezi v5.0 - Background Tasks
APScheduler ile zamanlanmis gorevler
"""

import logging
from datetime import datetime, timedelta
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# Global scheduler
scheduler = AsyncIOScheduler()


class TaskManager:
    """Gorev yoneticisi"""
    
    def __init__(self):
        self.tasks = {}
        self.task_history = []
    
    def add_task(self, task_id: str, func: Callable, trigger, **kwargs):
        """Yeni gorev ekle"""
        job = scheduler.add_job(
            func,
            trigger=trigger,
            id=task_id,
            replace_existing=True,
            **kwargs
        )
        # next_run_time attribute sadece scheduler başladıktan sonra mevcut olur
        try:
            next_run = job.next_run_time if hasattr(job, 'next_run_time') else None
        except AttributeError:
            next_run = None

        self.tasks[task_id] = {
            "func": func.__name__,
            "trigger": str(trigger),
            "next_run": next_run,
            "created_at": datetime.utcnow()
        }
        logger.info(f"Task added: {task_id}")
        return job
    
    def remove_task(self, task_id: str):
        """Gorevi kaldir"""
        try:
            scheduler.remove_job(task_id)
            if task_id in self.tasks:
                del self.tasks[task_id]
            logger.info(f"Task removed: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Task remove error: {e}")
            return False
    
    def get_tasks(self) -> list:
        """Tum gorevleri listele"""
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time,
                "trigger": str(job.trigger)
            })
        return jobs
    
    def log_execution(self, task_id: str, status: str, duration_ms: int = 0, error: str = None):
        """Gorev calisma logu"""
        self.task_history.append({
            "task_id": task_id,
            "status": status,
            "duration_ms": duration_ms,
            "error": error,
            "executed_at": datetime.utcnow()
        })
        # Son 1000 kayit tut
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-1000:]


task_manager = TaskManager()


# ==================== BUILT-IN TASKS ====================

async def cleanup_expired_sessions():
    """Suresi dolmus session'lari temizle"""
    from app.models.connection import SessionLocal
    from app.models.database import UserSession
    
    start = datetime.utcnow()
    db = SessionLocal()
    try:
        expired = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        
        duration = (datetime.utcnow() - start).total_seconds() * 1000
        task_manager.log_execution("cleanup_sessions", "success", int(duration))
        logger.info(f"Cleaned up {expired} expired sessions")
    except Exception as e:
        db.rollback()
        task_manager.log_execution("cleanup_sessions", "failed", error=str(e))
        logger.error(f"Session cleanup error: {e}")
    finally:
        db.close()


async def cleanup_old_logs():
    """30 gunluk loglari temizle"""
    from app.models.connection import SessionLocal
    from app.models.database import AuditLog, SystemLog
    
    start = datetime.utcnow()
    cutoff = datetime.utcnow() - timedelta(days=30)
    db = SessionLocal()
    try:
        system_deleted = db.query(SystemLog).filter(SystemLog.created_at < cutoff).delete()
        audit_deleted = db.query(AuditLog).filter(AuditLog.created_at < cutoff).delete()
        db.commit()
        
        duration = (datetime.utcnow() - start).total_seconds() * 1000
        task_manager.log_execution("cleanup_logs", "success", int(duration))
        logger.info(f"Cleaned up {system_deleted + audit_deleted} old logs")
    except Exception as e:
        db.rollback()
        task_manager.log_execution("cleanup_logs", "failed", error=str(e))
        logger.error(f"Log cleanup error: {e}")
    finally:
        db.close()


async def check_expiring_servers():
    """Suresi dolmak uzere olan sunuculari kontrol et"""
    from app.models.connection import SessionLocal
    from app.models.database import GameServer, Notification, ServerStatus
    
    start = datetime.utcnow()
    warning_date = datetime.utcnow() + timedelta(days=3)
    db = SessionLocal()
    try:
        expiring = db.query(GameServer).filter(
            GameServer.status == ServerStatus.RUNNING,
            GameServer.expires_at <= warning_date,
            GameServer.expires_at > datetime.utcnow()
        ).all()
        
        for server in expiring:
            # Bildirim olustur
            existing = db.query(Notification).filter(
                Notification.user_id == server.user_id,
                Notification.type == "server_expiring",
                Notification.created_at > datetime.utcnow() - timedelta(days=1)
            ).first()
            
            if not existing:
                notification = Notification(
                    user_id=server.user_id,
                    type="server_expiring",
                    title="Sunucu Suresi Doluyor",
                    message=f"{server.name} sunucunuzun suresi {server.expires_at.strftime('%d.%m.%Y')} tarihinde doluyor.",
                    link=f"/panel/servers/{server.id}"
                )
                db.add(notification)
        
        db.commit()
        duration = (datetime.utcnow() - start).total_seconds() * 1000
        task_manager.log_execution("check_expiring", "success", int(duration))
        logger.info(f"Checked {len(expiring)} expiring servers")
    except Exception as e:
        db.rollback()
        task_manager.log_execution("check_expiring", "failed", error=str(e))
        logger.error(f"Expiring servers check error: {e}")
    finally:
        db.close()


async def update_server_stats():
    """Sunucu istatistiklerini guncelle"""
    from app.models.connection import SessionLocal
    from app.models.database import GameServer, ServerStatus
    
    start = datetime.utcnow()
    db = SessionLocal()
    try:
        active_servers = db.query(GameServer).filter(
            GameServer.status == ServerStatus.RUNNING
        ).all()
        
        for server in active_servers:
            # Burada gercek sunucu sorgulamasi yapilabilir
            # Simdilik placeholder
            pass
        
        duration = (datetime.utcnow() - start).total_seconds() * 1000
        task_manager.log_execution("update_stats", "success", int(duration))
    except Exception as e:
        task_manager.log_execution("update_stats", "failed", error=str(e))
        logger.error(f"Stats update error: {e}")
    finally:
        db.close()


async def daily_report():
    """Gunluk rapor olustur"""
    from sqlalchemy import func

    from app.models.connection import SessionLocal
    from app.models.database import Payment, PaymentStatus, User

    start = datetime.utcnow()
    yesterday = datetime.utcnow() - timedelta(days=1)
    db = SessionLocal()
    try:
        new_users = db.query(User).filter(User.created_at >= yesterday).count()
        new_payments = db.query(func.sum(Payment.amount)).filter(
            Payment.created_at >= yesterday,
            Payment.status == PaymentStatus.COMPLETED
        ).scalar() or 0

        logger.info(f"Daily Report - New Users: {new_users}, Revenue: {new_payments} TL")

        duration = (datetime.utcnow() - start).total_seconds() * 1000
        task_manager.log_execution("daily_report", "success", int(duration))
    except Exception as e:
        task_manager.log_execution("daily_report", "failed", error=str(e))
        logger.error(f"Daily report error: {e}")
    finally:
        db.close()


async def scan_community_servers():
    """Topluluk sunucularini tara - HL, CS 1.6, AG"""
    from app.models.connection import SessionLocal
    from app.services.server_scraper import run_scraper_task

    start = datetime.utcnow()
    db = SessionLocal()
    try:
        logger.info("Community server scan starting...")
        result = await run_scraper_task(["ag", "cs16", "hldm"], db)

        duration = (datetime.utcnow() - start).total_seconds() * 1000
        task_manager.log_execution("scan_servers", "success", int(duration))

        found = result.get("total_found", 0)
        added = result.get("db_stats", {}).get("added", 0)
        updated = result.get("db_stats", {}).get("updated", 0)
        logger.info(f"Server scan complete - Found: {found}, Added: {added}, Updated: {updated}")

    except Exception as e:
        task_manager.log_execution("scan_servers", "failed", error=str(e))
        logger.error(f"Server scan error: {e}")
    finally:
        db.close()


def init_scheduler():
    """Scheduler'i baslat ve varsayilan gorevleri ekle"""
    # Önce scheduler'ı başlat
    scheduler.start()
    logger.info("Scheduler started")

    # Sonra görevleri ekle (scheduler başladıktan sonra next_run_time mevcut olur)
    # Her saat session temizligi
    task_manager.add_task(
        "cleanup_sessions",
        cleanup_expired_sessions,
        IntervalTrigger(hours=1)
    )

    # Her gun gece 3'te log temizligi
    task_manager.add_task(
        "cleanup_logs",
        cleanup_old_logs,
        CronTrigger(hour=3, minute=0)
    )

    # Her 6 saatte sunucu suresi kontrolu
    task_manager.add_task(
        "check_expiring",
        check_expiring_servers,
        IntervalTrigger(hours=6)
    )

    # Her 5 dakikada sunucu stats
    task_manager.add_task(
        "update_stats",
        update_server_stats,
        IntervalTrigger(minutes=5)
    )

    # Her gun sabah 9'da rapor
    task_manager.add_task(
        "daily_report",
        daily_report,
        CronTrigger(hour=9, minute=0)
    )

    # Her 30 dakikada topluluk sunucularini tara
    task_manager.add_task(
        "scan_servers",
        scan_community_servers,
        IntervalTrigger(minutes=30)
    )

    logger.info("All background tasks initialized")


def shutdown_scheduler():
    """Scheduler'i durdur"""
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")


# ==================== SCHEDULER WRAPPER ====================

class TaskScheduler:
    """Kolay kullanim icin scheduler wrapper"""
    
    def __init__(self):
        self.is_running = False
    
    def start(self):
        """Scheduler'i baslat"""
        if not self.is_running:
            init_scheduler()
            self.is_running = True
    
    def stop(self):
        """Scheduler'i durdur"""
        if self.is_running:
            shutdown_scheduler()
            self.is_running = False
    
    def get_jobs(self):
        """Aktif gorevleri getir"""
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in scheduler.get_jobs()
        ]


# Global instance
task_scheduler = TaskScheduler()
