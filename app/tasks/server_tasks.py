"""
AGTR Merkezi v6.0 - Server Background Tasks
Sunucu izleme, auto-restart, istatistik ve temizlik gorevleri
"""

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.connection import SessionLocal
from app.models.database import (
    GameServer,
    InstallationStatus,
    ServerBan,
    ServerInstallation,
    ServerStatsHourly,
    ServerStatus,
)
from app.services import AMXXAdminService, ServerControlService
from app.services.monitor import ServerQuery

logger = logging.getLogger(__name__)


class ServerTaskManager:
    """Sunucu arkaplan gorevleri yoneticisi"""

    # Task intervalleri (saniye)
    MONITOR_INTERVAL = 30
    STATS_INTERVAL = 3600  # 1 saat
    AUTO_RESTART_INTERVAL = 60
    CLEANUP_INTERVAL = 86400  # 24 saat
    ADMIN_CHECK_INTERVAL = 3600  # 1 saat
    METRICS_COLLECTION_INTERVAL = 300  # 5 dakika
    METRICS_ARCHIVAL_INTERVAL = 86400  # 24 saat (runs at 3 AM)
    TEMPLATE_CACHE_UPDATE_INTERVAL = 86400  # 24 saat (runs at 3 AM)

    def __init__(self):
        self.is_running = False
        self._tasks = []

    def get_db(self) -> Session:
        """Veritabani oturumu al"""
        return SessionLocal()

    async def monitor_servers_task(self):
        """
        Tum sunuculari izle ve durumlarini guncelle

        Her 30 saniyede bir calisir
        """
        db = self.get_db()
        try:
            # Aktif sunuculari al
            servers = (
                db.query(GameServer)
                .filter(GameServer.status.in_([ServerStatus.RUNNING, ServerStatus.CREATING]))
                .all()
            )

            control_service = ServerControlService(db)

            for server in servers:
                try:
                    # Screen kontrolu
                    is_running = await control_service.is_running(server.id)

                    if server.status == ServerStatus.RUNNING:
                        if is_running:
                            # A2S query ile bilgileri guncelle
                            query = ServerQuery(server.ip_address, server.port)
                            info = await query.query_info()

                            if info:
                                server.current_players = info.get("players", 0)
                                server.current_map = info.get("map")
                                server.last_heartbeat = datetime.utcnow()
                        else:
                            # Calismiyorsa crash olmus olabilir
                            logger.warning(f"Sunucu calismiyor: {server.id} ({server.unique_code})")
                            server.status = ServerStatus.STOPPED

                    elif server.status == ServerStatus.CREATING:
                        # Kurulum tamamlanmis mi kontrol et
                        installation = (
                            db.query(ServerInstallation)
                            .filter(ServerInstallation.server_id == server.id)
                            .order_by(ServerInstallation.created_at.desc())
                            .first()
                        )

                        if installation:
                            if installation.status == InstallationStatus.COMPLETED:
                                server.status = ServerStatus.STOPPED
                            elif installation.status == InstallationStatus.FAILED:
                                server.status = ServerStatus.STOPPED

                    db.commit()

                except Exception as e:
                    logger.error(f"Sunucu izleme hatasi ({server.id}): {e}")

            logger.debug(f"Monitor: {len(servers)} sunucu kontrol edildi")

        except Exception as e:
            logger.error(f"Monitor task hatasi: {e}")
        finally:
            db.close()

    async def auto_restart_crashed_task(self):
        """
        Coken sunuculari otomatik yeniden baslat (respawn storm detection ile)

        Her 60 saniyede bir calisir
        """
        db = self.get_db()
        try:
            from app.services.respawn_monitor import RespawnMonitor

            # Auto-restart aktif ve STOPPED sunucular
            servers = (
                db.query(GameServer)
                .filter(GameServer.auto_restart == True, GameServer.status == ServerStatus.STOPPED)
                .all()
            )

            control_service = ServerControlService(db)
            respawn_monitor = RespawnMonitor(db)
            restarted = 0
            blocked = 0

            for server in servers:
                try:
                    # Check if in backoff period
                    if respawn_monitor.is_in_backoff_period(server):
                        blocked += 1
                        continue

                    # Check if storm detected (auto-restart disabled)
                    if respawn_monitor.is_storm_detected(server):
                        blocked += 1
                        logger.warning(
                            f"Crash storm detected for server {server.id}, auto-restart disabled"
                        )
                        continue

                    # Screen kontrolu
                    if not await control_service.is_running(server.id):
                        result = await control_service.check_and_restart_crashed(server.id)

                        if result.get("restarted"):
                            restarted += 1
                            # Reset crash tracking on successful restart
                            respawn_monitor.reset_crash_tracking(server)
                            logger.info(f"Auto-restart: {server.id} ({server.unique_code})")

                except Exception as e:
                    logger.error(f"Auto-restart hatasi ({server.id}): {e}")

            if restarted > 0 or blocked > 0:
                logger.info(
                    f"Auto-restart: {restarted} sunucu baslatildi, {blocked} sunucu backoff/storm blocked"
                )

        except Exception as e:
            logger.error(f"Auto-restart task hatasi: {e}")
        finally:
            db.close()

    async def record_hourly_stats_task(self):
        """
        Saatlik istatistikleri kaydet

        Her saat basinda calisir
        """
        db = self.get_db()
        try:
            # Aktif sunuculari al
            servers = db.query(GameServer).filter(GameServer.status == ServerStatus.RUNNING).all()

            hour_timestamp = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

            for server in servers:
                try:
                    # A2S query
                    query = ServerQuery(server.ip_address, server.port)
                    info = await query.query_info()

                    current_players = 0
                    current_map = None

                    if info:
                        current_players = info.get("players", 0)
                        current_map = info.get("map")

                    # Mevcut kaydi kontrol et
                    existing = (
                        db.query(ServerStatsHourly)
                        .filter(
                            ServerStatsHourly.server_id == server.id,
                            ServerStatsHourly.hour_timestamp == hour_timestamp,
                        )
                        .first()
                    )

                    if existing:
                        # Guncelle
                        existing.avg_players = (existing.avg_players + current_players) / 2
                        existing.max_players = max(existing.max_players or 0, current_players)
                        existing.min_players = min(existing.min_players or 0, current_players)
                        if current_map:
                            existing.most_played_map = current_map
                    else:
                        # Yeni kayit
                        stats = ServerStatsHourly(
                            server_id=server.id,
                            hour_timestamp=hour_timestamp,
                            avg_players=float(current_players),
                            max_players=current_players,
                            min_players=current_players,
                            unique_players=current_players,
                            most_played_map=current_map,
                            uptime_percent=100.0,
                            created_at=datetime.utcnow(),
                        )
                        db.add(stats)

                    db.commit()

                except Exception as e:
                    logger.error(f"Stats kayit hatasi ({server.id}): {e}")

            logger.info(f"Stats: {len(servers)} sunucu icin istatistik kaydedildi")

        except Exception as e:
            logger.error(f"Stats task hatasi: {e}")
        finally:
            db.close()

    async def cleanup_expired_task(self):
        """
        Suresi dolan sunuculari ve kayitlari temizle

        Gunluk calisir
        """
        db = self.get_db()
        try:
            now = datetime.utcnow()

            # 1. Suresi dolan sunuculari durdur
            expired_servers = (
                db.query(GameServer)
                .filter(
                    GameServer.expires_at != None,
                    GameServer.expires_at < now,
                    GameServer.status != ServerStatus.EXPIRED,
                )
                .all()
            )

            control_service = ServerControlService(db)

            for server in expired_servers:
                try:
                    # Durdur
                    await control_service.stop_server(server.id)
                    server.status = ServerStatus.EXPIRED
                    logger.info(f"Sunucu suresi doldu: {server.id} ({server.unique_code})")
                except Exception as e:
                    logger.error(f"Expired server stop hatasi ({server.id}): {e}")

            db.commit()

            # 2. Suresi dolan adminleri temizle
            admin_service = AMXXAdminService(db)
            expired_admins = admin_service.check_expired_admins()

            # 3. Suresi dolan banlari temizle
            expired_bans = (
                db.query(ServerBan)
                .filter(
                    ServerBan.expires_at != None,
                    ServerBan.expires_at < now,
                    ServerBan.is_active == True,
                )
                .all()
            )

            for ban in expired_bans:
                ban.is_active = False

            db.commit()

            # 4. 30 gunluk eski istatistikleri temizle
            old_stats_cutoff = now - timedelta(days=30)
            deleted_stats = (
                db.query(ServerStatsHourly)
                .filter(ServerStatsHourly.hour_timestamp < old_stats_cutoff)
                .delete()
            )

            db.commit()

            # 5. 30 gunluk eski command quota kayitlarini temizle
            from app.services.command_quota_service import CommandQuotaService

            quota_service = CommandQuotaService(db)
            deleted_quotas = quota_service.cleanup_old_quotas(days_to_keep=30)

            logger.info(
                f"Cleanup: {len(expired_servers)} expired server, "
                f"{expired_admins} expired admin, "
                f"{len(expired_bans)} expired ban, "
                f"{deleted_stats} old stats, "
                f"{deleted_quotas} old quotas"
            )

        except Exception as e:
            logger.error(f"Cleanup task hatasi: {e}")
        finally:
            db.close()

    async def check_installation_status_task(self):
        """
        Bekleyen kurulumlari kontrol et

        Her 30 saniyede calisir
        """
        db = self.get_db()
        try:
            # Takili kalmis kurulumlari bul (30 dakikadan uzun)
            timeout = datetime.utcnow() - timedelta(minutes=30)

            stuck_installations = (
                db.query(ServerInstallation)
                .filter(
                    ServerInstallation.status == InstallationStatus.INSTALLING,
                    ServerInstallation.started_at < timeout,
                )
                .all()
            )

            for installation in stuck_installations:
                installation.status = InstallationStatus.FAILED
                installation.error_message = "Kurulum zaman asimina ugradi"

                # Sunucu durumunu guncelle
                server = (
                    db.query(GameServer).filter(GameServer.id == installation.server_id).first()
                )
                if server:
                    server.status = ServerStatus.STOPPED

                logger.warning(f"Kurulum timeout: {installation.id}")

            db.commit()

        except Exception as e:
            logger.error(f"Installation check hatasi: {e}")
        finally:
            db.close()

    async def collect_metrics_task(self):
        """
        Tum calisir sunucularin kaynak metriklerini topla

        Her 5 dakikada calisir
        CPU, RAM, network, player count tracking
        """
        db = self.get_db()
        try:
            from app.services.monitor import server_monitor

            # Running ve Creating sunuculari al
            running_servers = (
                db.query(GameServer)
                .filter(GameServer.status.in_([ServerStatus.RUNNING, ServerStatus.CREATING]))
                .all()
            )

            collected = 0

            for server in running_servers:
                try:
                    # Metrics topla
                    await server_monitor.collect_server_metrics(server, db)
                    collected += 1
                except Exception as e:
                    logger.error(f"Metrics collection failed for server {server.id}: {e}")

            logger.debug(f"Metrics: {collected}/{len(running_servers)} sunucu icin metrik toplandı")

        except Exception as e:
            logger.error(f"Metrics collection task hatasi: {e}")
        finally:
            db.close()

    async def archive_metrics_task(self):
        """
        Eski metrikleri arsivle ve temizle

        Gunluk calisir (3 AM):
        - Onceki gunun verilerini saatlik agrega et
        - 7 gunluk eski ham verileri sil
        """
        db = self.get_db()
        try:
            from app.services.metrics_archiver import run_daily_archival

            result = await run_daily_archival(db)

            logger.info(
                f"Metrics archival: aggregated {result['aggregated_date']}, "
                f"deleted {result['deleted_rows']} rows, "
                f"table: {result['table_stats']['total_rows']} rows"
            )

        except Exception as e:
            logger.error(f"Metrics archival task hatasi: {e}")
        finally:
            db.close()

    async def update_template_caches_task(self):
        """
        Template cache'lerini guncelle

        DISABLED: Cache system temporarily disabled, using direct rsync instead
        """
        logger.info("Template cache update: DISABLED (using direct rsync)")
        return

    async def start(self):
        """Tum gorevleri baslat"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("Server tasks baslatiliyor...")

        # Gorevleri zamanla
        self._tasks = [
            asyncio.create_task(
                self._run_periodic(
                    self.monitor_servers_task, self.MONITOR_INTERVAL, "monitor_servers"
                )
            ),
            asyncio.create_task(
                self._run_periodic(
                    self.auto_restart_crashed_task, self.AUTO_RESTART_INTERVAL, "auto_restart"
                )
            ),
            asyncio.create_task(
                self._run_periodic(
                    self.record_hourly_stats_task, self.STATS_INTERVAL, "record_stats"
                )
            ),
            asyncio.create_task(
                self._run_periodic(self.cleanup_expired_task, self.CLEANUP_INTERVAL, "cleanup")
            ),
            asyncio.create_task(
                self._run_periodic(self.check_installation_status_task, 30, "installation_check")
            ),
            asyncio.create_task(
                self._run_periodic(
                    self.collect_metrics_task,
                    self.METRICS_COLLECTION_INTERVAL,
                    "collect_metrics",
                )
            ),
            asyncio.create_task(
                self._run_periodic(
                    self.archive_metrics_task,
                    self.METRICS_ARCHIVAL_INTERVAL,
                    "archive_metrics",
                )
            ),
            asyncio.create_task(
                self._run_periodic(
                    self.update_template_caches_task,
                    self.TEMPLATE_CACHE_UPDATE_INTERVAL,
                    "template_cache_update",
                )
            ),
        ]

        logger.info("Server tasks baslatildi")

    async def stop(self):
        """Tum gorevleri durdur"""
        self.is_running = False

        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._tasks = []
        logger.info("Server tasks durduruldu")

    async def _run_periodic(self, func, interval: int, name: str):
        """Periyodik gorev calistir"""
        while self.is_running:
            try:
                await func()
            except Exception as e:
                logger.error(f"Periodic task error ({name}): {e}")

            await asyncio.sleep(interval)


# Global instance
server_task_manager = ServerTaskManager()


async def start_server_tasks():
    """Server task'larini baslat"""
    await server_task_manager.start()


async def stop_server_tasks():
    """Server task'larini durdur"""
    await server_task_manager.stop()


# Manuel task calistirma fonksiyonlari


async def run_monitor_now():
    """Monitor task'ini hemen calistir"""
    manager = ServerTaskManager()
    await manager.monitor_servers_task()


async def run_cleanup_now():
    """Cleanup task'ini hemen calistir"""
    manager = ServerTaskManager()
    await manager.cleanup_expired_task()


async def run_stats_now():
    """Stats task'ini hemen calistir"""
    manager = ServerTaskManager()
    await manager.record_hourly_stats_task()
