# ============================================
# AGTR v6.0 - Forum Background Tasks
# Dosya: app/tasks/forum_tasks.py
# Badge checking, reputation sync, cleanup tasks
# ============================================

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.connection import SessionLocal

logger = logging.getLogger(__name__)


class ForumTaskManager:
    """Forum arkaplan gorevleri yoneticisi"""

    # Task intervalleri (saniye)
    BADGE_CHECK_INTERVAL = 60  # 1 dakika (badge checking siralanmis)
    REPUTATION_SYNC_INTERVAL = 300  # 5 dakika
    CLEANUP_INTERVAL = 3600  # 1 saat

    def __init__(self):
        self.is_running = False
        self._tasks = []
        self._badge_queue = asyncio.Queue()

    def get_db(self) -> Session:
        """Veritabani oturumu al"""
        return SessionLocal()

    async def enqueue_badge_check(self, user_id: int):
        """
        Kullanici badge kontrolunu kuyruga ekle

        Args:
            user_id: Kontrol edilecek kullanici ID
        """
        await self._badge_queue.put(user_id)
        logger.debug(f"Badge check queued for user {user_id}")

    async def process_badge_queue_task(self):
        """
        Badge kontrol kuyruğunu isle

        Surekli calisir, kuyruktaki kullanicilarin rozetlerini kontrol eder
        """
        from app.services.forum_gamification import get_gamification_service

        while self.is_running:
            try:
                # Kuyruktan kullanici al (max 5 saniye bekle)
                try:
                    user_id = await asyncio.wait_for(self._badge_queue.get(), timeout=5.0)
                except asyncio.TimeoutError:
                    continue

                # Badge kontrolu yap
                db = self.get_db()
                try:
                    service = get_gamification_service(db)
                    badges_earned = await service.check_and_award_badges(user_id)

                    if badges_earned:
                        logger.info(
                            f"Background: User {user_id} earned {len(badges_earned)} badges: "
                            f"{[b['name'] for b in badges_earned]}"
                        )

                except Exception as e:
                    logger.error(f"Badge check error for user {user_id}: {e}")
                finally:
                    db.close()
                    self._badge_queue.task_done()

            except Exception as e:
                logger.error(f"Badge queue processing error: {e}")
                await asyncio.sleep(1)

    async def periodic_badge_check_task(self):
        """
        Periyodik badge kontrolu

        Active kullanicilarin rozetlerini duzenli kontrol eder
        (Son 24 saatte activity olan kullanicilar)
        """
        db = self.get_db()
        try:
            pass

            from app.models.forum import ForumReply, ForumTopic

            # Son 24 saatte konu/yanit olusturan kullanicilar
            yesterday = datetime.utcnow() - timedelta(hours=24)

            active_users = set()

            # Konu olusturanlar
            topic_authors = (
                db.query(ForumTopic.author_id)
                .filter(ForumTopic.created_at >= yesterday, ForumTopic.is_active == True)
                .distinct()
                .all()
            )
            active_users.update(row[0] for row in topic_authors)

            # Yanit yazanlar
            reply_authors = (
                db.query(ForumReply.user_id)
                .filter(ForumReply.created_at >= yesterday, ForumReply.is_active == True)
                .distinct()
                .all()
            )
            active_users.update(row[0] for row in reply_authors)

            logger.info(f"Periodic badge check: {len(active_users)} active users")

            # Her kullanici icin badge kontrolu kuyruga ekle
            for user_id in active_users:
                await self.enqueue_badge_check(user_id)

        except Exception as e:
            logger.error(f"Periodic badge check error: {e}")
        finally:
            db.close()

    async def reputation_sync_task(self):
        """
        Reputation senkronizasyonu

        ForumReputationLog'daki puanlari User tablosundaki
        forum_reputation ile senkronize eder
        """
        db = self.get_db()
        try:
            from sqlalchemy import func

            from app.models.database import ForumReputationLog, User

            # Her kullanici icin toplam reputation hesapla
            reputation_sums = (
                db.query(ForumReputationLog.user_id, func.sum(ForumReputationLog.points))
                .group_by(ForumReputationLog.user_id)
                .all()
            )

            synced_count = 0
            for user_id, total_reputation in reputation_sums:
                user = db.query(User).filter(User.id == user_id).first()
                if user and user.forum_reputation != total_reputation:
                    user.forum_reputation = int(total_reputation)
                    synced_count += 1

            if synced_count > 0:
                db.commit()
                logger.info(f"Reputation sync: {synced_count} users updated")

        except Exception as e:
            logger.error(f"Reputation sync error: {e}")
        finally:
            db.close()

    async def cleanup_task(self):
        """
        Forum temizlik gorevleri

        - Eski inactive konulari arsivle
        - Eski draft'lari temizle
        - Soft-deleted icerikleri kalici sil (30 gun sonra)
        """
        db = self.get_db()
        try:
            from app.models.database import ForumDraft
            from app.models.forum import ForumReply, ForumTopic

            # 1. 90 gunluk eski draft'lari sil
            old_drafts_cutoff = datetime.utcnow() - timedelta(days=90)
            deleted_drafts = (
                db.query(ForumDraft).filter(ForumDraft.updated_at < old_drafts_cutoff).delete()
            )

            # 2. Soft-deleted konulari kalici sil (30 gun sonra)
            deleted_topics_cutoff = datetime.utcnow() - timedelta(days=30)
            topics_to_delete = (
                db.query(ForumTopic)
                .filter(
                    ForumTopic.is_active == False,
                    ForumTopic.updated_at < deleted_topics_cutoff,
                )
                .all()
            )

            for topic in topics_to_delete:
                # Yanıtları da sil
                db.query(ForumReply).filter(ForumReply.topic_id == topic.id).delete()
                db.delete(topic)

            # 3. Orphan replies (konusu silinmis yanitlar)
            orphan_reply_ids = (
                db.query(ForumReply.id)
                .outerjoin(ForumTopic, ForumReply.topic_id == ForumTopic.id)
                .filter(ForumTopic.id == None)
                .all()
            )
            orphan_replies = 0
            if orphan_reply_ids:
                orphan_reply_ids = [r.id for r in orphan_reply_ids]
                orphan_replies = (
                    db.query(ForumReply)
                    .filter(ForumReply.id.in_(orphan_reply_ids))
                    .delete(synchronize_session=False)
                )

            db.commit()

            logger.info(
                f"Forum cleanup: {deleted_drafts} drafts, "
                f"{len(topics_to_delete)} topics, "
                f"{orphan_replies} orphan replies"
            )

        except Exception as e:
            logger.error(f"Forum cleanup error: {e}")
        finally:
            db.close()

    async def start(self):
        """Tum gorevleri baslat"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("Forum tasks baslatiliyor...")

        # Gorevleri zamanla
        self._tasks = [
            # Badge queue processor (surekli calisir)
            asyncio.create_task(self.process_badge_queue_task()),
            # Periyodik badge check (active users)
            asyncio.create_task(
                self._run_periodic(
                    self.periodic_badge_check_task,
                    self.BADGE_CHECK_INTERVAL,
                    "periodic_badge_check",
                )
            ),
            # Reputation sync
            asyncio.create_task(
                self._run_periodic(
                    self.reputation_sync_task, self.REPUTATION_SYNC_INTERVAL, "reputation_sync"
                )
            ),
            # Cleanup
            asyncio.create_task(
                self._run_periodic(self.cleanup_task, self.CLEANUP_INTERVAL, "forum_cleanup")
            ),
        ]

        logger.info("Forum tasks baslatildi")

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
        logger.info("Forum tasks durduruldu")

    async def _run_periodic(self, func, interval: int, name: str):
        """Periyodik gorev calistir"""
        while self.is_running:
            try:
                await func()
            except Exception as e:
                logger.error(f"Periodic task error ({name}): {e}")

            await asyncio.sleep(interval)


# Global instance
forum_task_manager = ForumTaskManager()


async def start_forum_tasks():
    """Forum task'larini baslat"""
    await forum_task_manager.start()


async def stop_forum_tasks():
    """Forum task'larini durdur"""
    await forum_task_manager.stop()


async def enqueue_badge_check(user_id: int):
    """
    Convenience function to enqueue badge check

    Usage:
        from app.tasks.forum_tasks import enqueue_badge_check
        await enqueue_badge_check(user_id)
    """
    await forum_task_manager.enqueue_badge_check(user_id)


# Manuel task calistirma fonksiyonlari


async def run_reputation_sync_now():
    """Reputation sync task'ini hemen calistir"""
    manager = ForumTaskManager()
    await manager.reputation_sync_task()


async def run_forum_cleanup_now():
    """Forum cleanup task'ini hemen calistir"""
    manager = ForumTaskManager()
    await manager.cleanup_task()
