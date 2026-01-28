"""
AGTR Merkezi v6.0 - Scheduler API
Zamanlanmis gorev yonetimi API'leri
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_required
from app.models.connection import get_db
from app.models.database import (
    GameServer,
    IntervalUnit,
    ScheduledTaskExecution,
    ScheduleType,
    ServerScheduledTask,
    TaskType,
    User,
)
from app.services.server_scheduler import scheduler_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v2/servers/{server_id}/scheduler", tags=["Scheduler"])


# ============================================
# Pydantic Schemas
# ============================================


class TaskCreateRequest(BaseModel):
    """Gorev olusturma istegi"""

    task_name: str
    task_type: TaskType
    schedule_type: ScheduleType
    cron_minute: Optional[str] = None
    cron_hour: Optional[str] = None
    cron_day: Optional[str] = None
    cron_month: Optional[str] = None
    cron_day_of_week: Optional[str] = None
    interval_value: Optional[int] = None
    interval_unit: Optional[IntervalUnit] = None
    scheduled_time: Optional[datetime] = None
    task_config: Optional[dict] = {}
    is_enabled: bool = True


class TaskUpdateRequest(BaseModel):
    """Gorev guncelleme istegi"""

    task_name: Optional[str] = None
    schedule_type: Optional[ScheduleType] = None
    cron_minute: Optional[str] = None
    cron_hour: Optional[str] = None
    cron_day: Optional[str] = None
    cron_month: Optional[str] = None
    cron_day_of_week: Optional[str] = None
    interval_value: Optional[int] = None
    interval_unit: Optional[IntervalUnit] = None
    scheduled_time: Optional[datetime] = None
    task_config: Optional[dict] = None
    is_enabled: Optional[bool] = None


# ============================================
# Helper Functions
# ============================================


async def verify_server_ownership(server_id: int, current_user: User, db: Session) -> GameServer:
    """
    Sunucu sahipligini dogrula

    Admin/Superadmin kullanıcılar tüm sunuculara erişebilir
    """
    from app.models.database import UserRole

    server = db.query(GameServer).filter(GameServer.id == server_id).first()

    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # Admin bypass - admin kullanıcılar tüm sunuculara erişebilir
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        return server

    # Normal kullanıcı - sadece kendi sunucusu
    if server.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return server


# ============================================
# API Endpoints
# ============================================


@router.get("/tasks")
async def list_tasks(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Tum zamanlanmis gorevleri listele"""
    await verify_server_ownership(server_id, current_user, db)

    tasks = db.query(ServerScheduledTask).filter(ServerScheduledTask.server_id == server_id).all()

    return [
        {
            "id": t.id,
            "task_name": t.task_name,
            "task_type": t.task_type.value,
            "schedule_type": t.schedule_type.value,
            "cron_minute": t.cron_minute,
            "cron_hour": t.cron_hour,
            "cron_day": t.cron_day,
            "cron_month": t.cron_month,
            "cron_day_of_week": t.cron_day_of_week,
            "interval_value": t.interval_value,
            "interval_unit": t.interval_unit.value if t.interval_unit else None,
            "scheduled_time": t.scheduled_time.isoformat() if t.scheduled_time else None,
            "task_config": t.task_config,
            "is_enabled": t.is_enabled,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "last_run": t.last_run.isoformat() if t.last_run else None,
            "next_run": t.next_run.isoformat() if t.next_run else None,
        }
        for t in tasks
    ]


@router.post("/tasks")
async def create_task(
    server_id: int,
    task_data: TaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Yeni zamanlanmis gorev olustur"""
    await verify_server_ownership(server_id, current_user, db)

    # Yeni gorev olustur
    task = ServerScheduledTask(
        server_id=server_id,
        created_by=current_user.id,
        task_name=task_data.task_name,
        task_type=task_data.task_type,
        schedule_type=task_data.schedule_type,
        cron_minute=task_data.cron_minute,
        cron_hour=task_data.cron_hour,
        cron_day=task_data.cron_day,
        cron_month=task_data.cron_month,
        cron_day_of_week=task_data.cron_day_of_week,
        interval_value=task_data.interval_value,
        interval_unit=task_data.interval_unit,
        scheduled_time=task_data.scheduled_time,
        task_config=task_data.task_config,
        is_enabled=task_data.is_enabled,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    # Scheduler'a ekle
    if task.is_enabled:
        success, msg = scheduler_service.create_task(task)
        if not success:
            logger.error(f"Failed to schedule task {task.id}: {msg}")
            raise HTTPException(status_code=500, detail=msg)

    logger.info(f"Task {task.id} created for server {server_id} by user {current_user.id}")

    return {
        "success": True,
        "task_id": task.id,
        "message": "Task created successfully",
    }


@router.get("/tasks/{task_id}")
async def get_task(
    server_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Gorev detayini getir"""
    await verify_server_ownership(server_id, current_user, db)

    task = (
        db.query(ServerScheduledTask)
        .filter(ServerScheduledTask.id == task_id, ServerScheduledTask.server_id == server_id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": task.id,
        "task_name": task.task_name,
        "task_type": task.task_type.value,
        "schedule_type": task.schedule_type.value,
        "cron_minute": task.cron_minute,
        "cron_hour": task.cron_hour,
        "cron_day": task.cron_day,
        "cron_month": task.cron_month,
        "cron_day_of_week": task.cron_day_of_week,
        "interval_value": task.interval_value,
        "interval_unit": task.interval_unit.value if task.interval_unit else None,
        "scheduled_time": task.scheduled_time.isoformat() if task.scheduled_time else None,
        "task_config": task.task_config,
        "is_enabled": task.is_enabled,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "last_run": task.last_run.isoformat() if task.last_run else None,
        "next_run": task.next_run.isoformat() if task.next_run else None,
    }


@router.put("/tasks/{task_id}")
async def update_task(
    server_id: int,
    task_id: int,
    task_data: TaskUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Gorevi guncelle"""
    await verify_server_ownership(server_id, current_user, db)

    task = (
        db.query(ServerScheduledTask)
        .filter(ServerScheduledTask.id == task_id, ServerScheduledTask.server_id == server_id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Guncellemeleri uygula
    update_data = task_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    # Scheduler'da guncelle
    if task.is_enabled:
        success, msg = scheduler_service.update_task(task)
        if not success:
            logger.error(f"Failed to update task {task.id}: {msg}")
            raise HTTPException(status_code=500, detail=msg)
    else:
        # Devre disi birakildiysa scheduler'dan kaldir
        scheduler_service.delete_task(task)

    logger.info(f"Task {task.id} updated by user {current_user.id}")

    return {
        "success": True,
        "message": "Task updated successfully",
    }


@router.delete("/tasks/{task_id}")
async def delete_task(
    server_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Gorevi sil"""
    await verify_server_ownership(server_id, current_user, db)

    task = (
        db.query(ServerScheduledTask)
        .filter(ServerScheduledTask.id == task_id, ServerScheduledTask.server_id == server_id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Scheduler'dan kaldir
    scheduler_service.delete_task(task)

    # Veritabanindan sil (cascade ile executions da silinir)
    db.delete(task)
    db.commit()

    logger.info(f"Task {task.id} deleted by user {current_user.id}")

    return {
        "success": True,
        "message": "Task deleted successfully",
    }


@router.get("/tasks/{task_id}/executions")
async def get_task_executions(
    server_id: int,
    task_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Gorev calisma gecmisini getir"""
    await verify_server_ownership(server_id, current_user, db)

    # Gorev dogrulama
    task = (
        db.query(ServerScheduledTask)
        .filter(ServerScheduledTask.id == task_id, ServerScheduledTask.server_id == server_id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Calisma gecmisini getir
    executions = (
        db.query(ScheduledTaskExecution)
        .filter(ScheduledTaskExecution.task_id == task_id)
        .order_by(ScheduledTaskExecution.executed_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": e.id,
            "executed_at": e.executed_at.isoformat() if e.executed_at else None,
            "status": e.status,
            "result_message": e.result_message,
            "execution_time_ms": e.execution_time_ms,
        }
        for e in executions
    ]


@router.post("/tasks/{task_id}/execute")
async def execute_task_now(
    server_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    """Gorevi hemen calistir (manuel calistirma)"""
    await verify_server_ownership(server_id, current_user, db)

    task = (
        db.query(ServerScheduledTask)
        .filter(ServerScheduledTask.id == task_id, ServerScheduledTask.server_id == server_id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Manuel calistir
    try:
        pass

        await scheduler_service._execute_task(task_id)
        logger.info(f"Task {task_id} manually executed by user {current_user.id}")
        return {
            "success": True,
            "message": "Task executed successfully",
        }
    except Exception as e:
        logger.error(f"Failed to execute task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")
