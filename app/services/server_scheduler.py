"""
AGTR Merkezi v6.0 - Server Scheduler Service
Zamanlanmis gorev yonetimi ve APScheduler entegrasyonu
"""

import logging
import time
from datetime import datetime
from typing import Tuple

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.models.connection import SessionLocal
from app.models.database import (
    ScheduledTaskExecution,
    ScheduleType,
    ServerScheduledTask,
    TaskType,
)

logger = logging.getLogger(__name__)


class ServerSchedulerService:
    """
    Sunucu zamanlanmis gorev servisi

    APScheduler ile entegre calisir ve zamanlanmis gorevleri yonetir.
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        logger.info("ServerSchedulerService initialized")

    def start(self):
        """Scheduler'i baslat ve tum gorevleri yukle"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("APScheduler started")

        self.load_all_tasks()
        logger.info("All scheduled tasks loaded")

    def shutdown(self):
        """Scheduler'i kapat"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("APScheduler shutdown")

    def load_all_tasks(self):
        """Veritabanindan tum aktif gorevleri yukle"""
        db = SessionLocal()
        try:
            tasks = (
                db.query(ServerScheduledTask).filter(ServerScheduledTask.is_enabled == True).all()
            )

            for task in tasks:
                try:
                    self._add_job_to_scheduler(task)
                except Exception as e:
                    logger.error(f"Failed to load task {task.id}: {e}")
        finally:
            db.close()

    def _add_job_to_scheduler(self, task: ServerScheduledTask):
        """
        Gorevi APScheduler'a ekle

        Args:
            task: ServerScheduledTask instance
        """
        job_id = f"server_{task.server_id}_task_{task.id}"

        # Mevcut job'i kaldir
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        # Trigger olustur
        trigger = None

        if task.schedule_type == ScheduleType.CRON:
            trigger = CronTrigger(
                minute=task.cron_minute or "*",
                hour=task.cron_hour or "*",
                day=task.cron_day or "*",
                month=task.cron_month or "*",
                day_of_week=task.cron_day_of_week or "*",
            )
        elif task.schedule_type == ScheduleType.INTERVAL:
            if task.interval_unit and task.interval_value:
                kwargs = {task.interval_unit.value: task.interval_value}
                trigger = IntervalTrigger(**kwargs)
        elif task.schedule_type == ScheduleType.ONE_TIME:
            if task.scheduled_time:
                trigger = DateTrigger(run_date=task.scheduled_time)

        if not trigger:
            logger.warning(f"Invalid trigger for task {task.id}")
            return

        # Job ekle
        self.scheduler.add_job(
            self._execute_task, trigger=trigger, id=job_id, args=[task.id], replace_existing=True
        )

        # Job ID'yi kaydet
        db = SessionLocal()
        try:
            db_task = (
                db.query(ServerScheduledTask).filter(ServerScheduledTask.id == task.id).first()
            )
            if db_task:
                db_task.apscheduler_job_id = job_id

                # Sonraki calisma zamanini guncelle
                job = self.scheduler.get_job(job_id)
                if job and job.next_run_time:
                    db_task.next_run = job.next_run_time

                db.commit()
                logger.info(f"Task {task.id} added to scheduler with job_id {job_id}")
        except Exception as e:
            logger.error(f"Failed to update task {task.id}: {e}")
            db.rollback()
        finally:
            db.close()

    async def _execute_task(self, task_id: int):
        """
        Zamanlanmis gorevi calistir

        Args:
            task_id: Task ID
        """
        db = SessionLocal()
        start_time = time.time()

        try:
            task = db.query(ServerScheduledTask).filter(ServerScheduledTask.id == task_id).first()

            if not task or not task.is_enabled:
                logger.warning(f"Task {task_id} not found or disabled")
                return

            server = task.server
            if not server:
                self._log_execution(db, task_id, "failed", "Server not found")
                return

            if server.status.value != "online":
                self._log_execution(db, task_id, "skipped", "Server not online")
                return

            # Gorev tipine gore calistir
            result = None

            if task.task_type == TaskType.RESTART:
                result = await self._execute_restart(server)
            elif task.task_type == TaskType.MAP_CHANGE:
                result = await self._execute_map_change(server, task.task_config)
            elif task.task_type == TaskType.BACKUP:
                result = await self._execute_backup(server)
            elif task.task_type == TaskType.ANNOUNCEMENT:
                result = await self._execute_announcement(server, task.task_config)
            elif task.task_type == TaskType.RCON_COMMAND:
                result = await self._execute_rcon_command(server, task.task_config)
            else:
                result = (False, "Unknown task type")

            success, message = result
            status = "success" if success else "failed"

            # Son calisma zamanini guncelle
            task.last_run = datetime.utcnow()

            # Sonraki calisma zamanini guncelle
            job = self.scheduler.get_job(task.apscheduler_job_id)
            if job and job.next_run_time:
                task.next_run = job.next_run_time

            # Calisma logunu kaydet
            execution_time = int((time.time() - start_time) * 1000)
            self._log_execution(db, task_id, status, message, execution_time)

            db.commit()

            logger.info(f"Task {task_id} executed: {status} - {message}")

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_execution(db, task_id, "failed", str(e), execution_time)
            db.rollback()
            logger.error(f"Task {task_id} execution error: {e}", exc_info=True)
        finally:
            db.close()

    def _log_execution(self, db, task_id: int, status: str, message: str, execution_time: int = 0):
        """
        Gorev calisma logunu kaydet

        Args:
            db: Database session
            task_id: Task ID
            status: Durum (success, failed, skipped)
            message: Mesaj
            execution_time: Calisma suresi (ms)
        """
        execution = ScheduledTaskExecution(
            task_id=task_id, status=status, result_message=message, execution_time_ms=execution_time
        )
        db.add(execution)

    async def _execute_restart(self, server) -> Tuple[bool, str]:
        """Sunucu restart"""
        try:
            from app.services.server_control import ServerControlService

            control = ServerControlService()
            success = await control.restart_server(server.id)
            return (success, "Server restarted" if success else "Failed to restart")
        except Exception as e:
            logger.error(f"Restart error: {e}")
            return (False, f"Restart error: {str(e)}")

    async def _execute_map_change(self, server, config: dict) -> Tuple[bool, str]:
        """Harita degistir"""
        try:
            from app.services.rcon import RCONService

            map_name = config.get("map", "de_dust2") if config else "de_dust2"
            rcon = RCONService()
            success = await rcon.send_command(server.id, f"changelevel {map_name}")
            return (success, f"Changed to {map_name}" if success else "Failed to change map")
        except Exception as e:
            logger.error(f"Map change error: {e}")
            return (False, f"Map change error: {str(e)}")

    async def _execute_backup(self, server) -> Tuple[bool, str]:
        """Yedekleme yap"""
        try:
            from app.services.server_config import ServerConfigService

            config_service = ServerConfigService()
            success = config_service.create_full_backup(server.id)
            return (success, "Backup created" if success else "Failed to create backup")
        except Exception as e:
            logger.error(f"Backup error: {e}")
            return (False, f"Backup error: {str(e)}")

    async def _execute_announcement(self, server, config: dict) -> Tuple[bool, str]:
        """Duyuru gonder"""
        try:
            from app.services.rcon import RCONService

            message = config.get("message", "") if config else ""
            if not message:
                return (False, "No message specified")

            rcon = RCONService()
            success = await rcon.send_command(server.id, f'say "{message}"')
            return (success, "Announcement sent" if success else "Failed to send")
        except Exception as e:
            logger.error(f"Announcement error: {e}")
            return (False, f"Announcement error: {str(e)}")

    async def _execute_rcon_command(self, server, config: dict) -> Tuple[bool, str]:
        """RCON komutu calistir"""
        try:
            from app.services.rcon import RCONService

            command = config.get("command", "") if config else ""
            if not command:
                return (False, "No command specified")

            rcon = RCONService()
            success = await rcon.send_command(server.id, command)
            return (success, "Command executed" if success else "Failed to execute")
        except Exception as e:
            logger.error(f"RCON command error: {e}")
            return (False, f"RCON error: {str(e)}")

    def create_task(self, task: ServerScheduledTask) -> Tuple[bool, str]:
        """
        Yeni gorev olustur ve scheduler'a ekle

        Args:
            task: ServerScheduledTask instance

        Returns:
            (basari, mesaj)
        """
        try:
            self._add_job_to_scheduler(task)
            return (True, "Task scheduled successfully")
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return (False, f"Failed to schedule: {str(e)}")

    def update_task(self, task: ServerScheduledTask) -> Tuple[bool, str]:
        """
        Gorevi guncelle ve yeniden zamanla

        Args:
            task: ServerScheduledTask instance

        Returns:
            (basari, mesaj)
        """
        return self.create_task(task)  # Yeniden zamanla

    def delete_task(self, task: ServerScheduledTask) -> Tuple[bool, str]:
        """
        Gorevi scheduler'dan kaldir

        Args:
            task: ServerScheduledTask instance

        Returns:
            (basari, mesaj)
        """
        if task.apscheduler_job_id:
            try:
                self.scheduler.remove_job(task.apscheduler_job_id)
                logger.info(f"Task {task.id} removed from scheduler")
                return (True, "Task removed from scheduler")
            except Exception as e:
                logger.error(f"Failed to remove task: {e}")
                return (False, f"Failed to remove: {str(e)}")
        return (True, "Task not in scheduler")


# Global instance
scheduler_service = ServerSchedulerService()
