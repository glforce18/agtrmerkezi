"""
AGTR Merkezi - Forum Puan Sistemi
Forum aktivitelerinden Coin kazanma
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.database import User, WalletType, TransactionType
from app.services.wallet import get_wallet_service

logger = logging.getLogger(__name__)


# Puan ayarları (Armor cinsinden)
REWARD_TOPIC_CREATE = 10.0  # Konu açma: 10 Armor
REWARD_REPLY_CREATE = 5.0   # Yorum yapma: 5 Armor
REWARD_LIKE_RECEIVED = 1.0  # Beğeni alma: 1 Armor
REWARD_FIRST_TOPIC = 50.0   # İlk konu bonusu: 50 Armor
REWARD_FIRST_REPLY = 25.0   # İlk yorum bonusu: 25 Armor
REWARD_BEST_ANSWER = 25.0   # En iyi cevap: 25 Armor

# Günlük limitler
DAILY_TOPIC_LIMIT = 10   # Günde max 10 konu
DAILY_REPLY_LIMIT = 50   # Günde max 50 yorum
DAILY_LIKE_LIMIT = 20    # Günde max 20 beğeni ödülü


class ForumRewardService:
    """Forum puan servisi"""

    def __init__(self, db: Session):
        self.db = db
        self.wallet = get_wallet_service(db)

    def reward_topic_create(
        self,
        user_id: int,
        topic_id: int,
        ip_address: str = None
    ) -> Optional[float]:
        """
        Konu açma ödülü
        Returns: Verilen ödül miktarı veya None (limit aşıldıysa)
        """
        try:
            # Günlük limit kontrolü
            if self._check_daily_limit(user_id, "topic"):
                logger.debug(f"User {user_id} günlük konu limitine ulaştı")
                return None

            # İlk konu kontrolü
            from app.models.forum import ForumTopic
            topic_count = self.db.query(ForumTopic).filter(
                ForumTopic.user_id == user_id
            ).count()

            reward = REWARD_TOPIC_CREATE
            description = f"Forum konu açma ödülü (#{topic_id})"

            # İlk konu bonusu
            if topic_count == 1:
                reward += REWARD_FIRST_TOPIC
                description = f"İlk forum konusu bonusu (#{topic_id})"

            # Ödül ver
            self.wallet.add_balance(
                user_id=user_id,
                amount=reward,
                wallet_type=WalletType.COIN,
                transaction_type=TransactionType.BONUS.value,
                description=description,
                reference_id=str(topic_id),
                reference_type="forum_topic",
                ip_address=ip_address
            )

            logger.info(f"Forum ödülü: user={user_id}, topic={topic_id}, amount={reward}")
            return reward

        except Exception as e:
            logger.error(f"Forum topic reward error: {e}")
            return None

    def reward_reply_create(
        self,
        user_id: int,
        reply_id: int,
        topic_id: int,
        ip_address: str = None
    ) -> Optional[float]:
        """
        Yorum yapma ödülü
        Returns: Verilen ödül miktarı veya None (limit aşıldıysa)
        """
        try:
            # Günlük limit kontrolü
            if self._check_daily_limit(user_id, "reply"):
                logger.debug(f"User {user_id} günlük yorum limitine ulaştı")
                return None

            # İlk yorum kontrolü
            from app.models.forum import ForumReply
            reply_count = self.db.query(ForumReply).filter(
                ForumReply.user_id == user_id
            ).count()

            reward = REWARD_REPLY_CREATE
            description = f"Forum yorum ödülü (konu #{topic_id})"

            # İlk yorum bonusu
            if reply_count == 1:
                reward += REWARD_FIRST_REPLY
                description = f"İlk forum yorumu bonusu (konu #{topic_id})"

            # Ödül ver
            self.wallet.add_balance(
                user_id=user_id,
                amount=reward,
                wallet_type=WalletType.COIN,
                transaction_type=TransactionType.BONUS.value,
                description=description,
                reference_id=str(reply_id),
                reference_type="forum_reply",
                ip_address=ip_address
            )

            logger.info(f"Forum ödülü: user={user_id}, reply={reply_id}, amount={reward}")
            return reward

        except Exception as e:
            logger.error(f"Forum reply reward error: {e}")
            return None

    def reward_like_received(
        self,
        user_id: int,
        post_id: int,
        liker_id: int
    ) -> Optional[float]:
        """
        Beğeni alma ödülü (beğenen değil, beğenilen kişiye)
        Returns: Verilen ödül miktarı veya None
        """
        try:
            # Kendi postunu beğenemez
            if user_id == liker_id:
                return None

            # Günlük limit kontrolü
            if self._check_daily_limit(user_id, "like"):
                return None

            reward = REWARD_LIKE_RECEIVED
            description = f"Forum beğeni ödülü (post #{post_id})"

            self.wallet.add_balance(
                user_id=user_id,
                amount=reward,
                wallet_type=WalletType.COIN,
                transaction_type=TransactionType.BONUS.value,
                description=description,
                reference_id=str(post_id),
                reference_type="forum_like"
            )

            logger.info(f"Forum beğeni ödülü: user={user_id}, post={post_id}")
            return reward

        except Exception as e:
            logger.error(f"Forum like reward error: {e}")
            return None

    def reward_best_answer(
        self,
        user_id: int,
        reply_id: int,
        topic_id: int
    ) -> Optional[float]:
        """
        En iyi cevap seçilme ödülü
        Returns: Verilen ödül miktarı veya None
        """
        try:
            reward = REWARD_BEST_ANSWER
            description = f"En iyi cevap ödülü (konu #{topic_id})"

            self.wallet.add_balance(
                user_id=user_id,
                amount=reward,
                wallet_type=WalletType.COIN,
                transaction_type=TransactionType.BONUS.value,
                description=description,
                reference_id=str(reply_id),
                reference_type="forum_best_answer"
            )

            logger.info(f"Best answer ödülü: user={user_id}, reply={reply_id}, topic={topic_id}")
            return reward

        except Exception as e:
            logger.error(f"Forum best answer reward error: {e}")
            return None

    def _check_daily_limit(self, user_id: int, reward_type: str) -> bool:
        """
        Günlük limit kontrolü
        Returns: True if limit reached
        """
        from datetime import datetime, timedelta
        from app.models.database import Transaction

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Reference type'a göre filtrele
        ref_type_map = {
            "topic": "forum_topic",
            "reply": "forum_reply",
            "like": "forum_like"
        }
        limit_map = {
            "topic": DAILY_TOPIC_LIMIT,
            "reply": DAILY_REPLY_LIMIT,
            "like": DAILY_LIKE_LIMIT
        }

        ref_type = ref_type_map.get(reward_type)
        limit = limit_map.get(reward_type, 0)

        if not ref_type:
            return False

        # Bugünkü işlem sayısını say
        count = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.reference_type == ref_type,
            Transaction.created_at >= today_start
        ).count()

        return count >= limit

    def get_user_forum_stats(self, user_id: int) -> dict:
        """Kullanıcının forum istatistiklerini getir"""
        from datetime import datetime, timedelta
        from app.models.database import Transaction

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Bugünkü ödüller
        today_topic_rewards = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.reference_type == "forum_topic",
            Transaction.created_at >= today_start
        ).count()

        today_reply_rewards = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.reference_type == "forum_reply",
            Transaction.created_at >= today_start
        ).count()

        today_like_rewards = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.reference_type == "forum_like",
            Transaction.created_at >= today_start
        ).count()

        # Toplam kazanılan
        from sqlalchemy import func
        total_earned = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.reference_type.in_(["forum_topic", "forum_reply", "forum_like"])
        ).scalar() or 0

        return {
            "today": {
                "topics": today_topic_rewards,
                "topics_remaining": max(0, DAILY_TOPIC_LIMIT - today_topic_rewards),
                "replies": today_reply_rewards,
                "replies_remaining": max(0, DAILY_REPLY_LIMIT - today_reply_rewards),
                "likes": today_like_rewards,
                "likes_remaining": max(0, DAILY_LIKE_LIMIT - today_like_rewards)
            },
            "total_earned": total_earned,
            "rewards": {
                "topic": REWARD_TOPIC_CREATE,
                "reply": REWARD_REPLY_CREATE,
                "like": REWARD_LIKE_RECEIVED
            }
        }


def get_forum_reward_service(db: Session) -> ForumRewardService:
    """Forum reward service instance oluştur"""
    return ForumRewardService(db)
