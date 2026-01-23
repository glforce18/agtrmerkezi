"""
AGTR Merkezi - Veritabani Baglanti Yonetimi
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.database import Base, add_missing_columns

logger = logging.getLogger(__name__)

# Engine olustur - Optimize edilmis Connection Pool ile
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,  # Varsayilan: 20
    max_overflow=settings.DB_MAX_OVERFLOW,  # Varsayilan: 30
    pool_pre_ping=True,  # Her baglantiyi kullanmadan once kontrol et (kopuk baglantiyi tespit eder)
    pool_recycle=settings.DB_POOL_RECYCLE,  # Varsayilan: 3600 (1 saat)
    pool_timeout=30,  # Havuzdan baglanti almayi 30 saniye bekle
    echo=settings.DEBUG,
    # Performance optimizations
    execution_options={
        "stream_results": True,  # Buyuk sonuc setleri icin streaming
    },
    # Connection arguments
    connect_args={
        "connect_timeout": 10,  # MySQL baglanti timeout (saniye)
        "read_timeout": 30,  # MySQL okuma timeout
        "write_timeout": 30,  # MySQL yazma timeout
    }
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Veritabani tablolarini olustur ve eksik kolonlari ekle"""
    # Yeni tablolari olustur
    Base.metadata.create_all(bind=engine)
    logger.info("Veritabani tablolari olusturuldu")
    
    # Eksik kolonlari ekle (mevcut tablolara)
    try:
        result = add_missing_columns()
        if result["added"]:
            logger.info(f"Eksik kolonlar eklendi: {result['added']}")
        if result["errors"]:
            logger.warning(f"Kolon ekleme hatalari: {result['errors']}")
    except Exception as e:
        logger.error(f"Kolon kontrolu hatasi: {e}")


def drop_db():
    """Veritabani tablolarini sil (dikkatli kullan!)"""
    Base.metadata.drop_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection icin veritabani session'i
    FastAPI route'larinda kullanilir
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"DB session hatasi: {e}")
        raise
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager ile veritabani session'i
    Background task'larda kullanilir
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ==================== REDIS ====================

_redis_pool = None


def get_redis_pool():
    """Redis connection pool olustur"""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
            socket_timeout=5.0,  # 5 saniye okuma/yazma timeout
            socket_connect_timeout=3.0,  # 3 saniye baglanti timeout
            retry_on_timeout=True,  # Timeout durumunda yeniden dene
            health_check_interval=30  # 30 saniyede bir baglanti kontrolu
        )
        logger.info("Redis connection pool olusturuldu (timeout: 5s, connect_timeout: 3s)")
    return _redis_pool


def get_redis() -> redis.Redis:
    """Redis client getir"""
    return redis.Redis(connection_pool=get_redis_pool())


def check_redis_connection() -> bool:
    """Redis baglanti kontrolu"""
    try:
        client = get_redis()
        client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis baglanti hatasi: {e}")
        return False


def redis_get(key: str) -> Optional[str]:
    """Redis'ten deger al"""
    try:
        client = get_redis()
        return client.get(key)
    except Exception as e:
        logger.error(f"Redis get hatasi: {e}")
        return None


def redis_set(key: str, value: str, expire: int = None) -> bool:
    """Redis'e deger yaz"""
    try:
        client = get_redis()
        if expire:
            client.setex(key, expire, value)
        else:
            client.set(key, value)
        return True
    except Exception as e:
        logger.error(f"Redis set hatasi: {e}")
        return False


def redis_delete(key: str) -> bool:
    """Redis'ten sil"""
    try:
        client = get_redis()
        client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Redis delete hatasi: {e}")
        return False


def redis_exists(key: str) -> bool:
    """Redis'te var mi kontrol"""
    try:
        client = get_redis()
        return client.exists(key) > 0
    except Exception as e:
        logger.error(f"Redis exists hatasi: {e}")
        return False


def redis_incr(key: str, expire: int = None) -> int:
    """Redis sayaci artir"""
    try:
        client = get_redis()
        val = client.incr(key)
        if expire and val == 1:
            client.expire(key, expire)
        return val
    except Exception as e:
        logger.error(f"Redis incr hatasi: {e}")
        return 0
