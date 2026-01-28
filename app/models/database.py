"""
AGTR Merkezi - Veritabani Modelleri
Tum SQLAlchemy modelleri + Otomatik Denetleyici Sistem
"""

import enum
import logging
from datetime import date as Date
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.orm import backref, declarative_base, relationship, sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

Base = declarative_base()


# ==================== ENUM VALIDATION ====================


def validate_enum_value(value, enum_class, column_name: str):
    """Validate that a value is a valid enum member"""
    if value is None:
        return value
    if isinstance(value, enum_class):
        return value
    if isinstance(value, str):
        try:
            return enum_class(value)
        except ValueError:
            valid_values = [e.value for e in enum_class]
            raise ValueError(
                f"Invalid value '{value}' for {column_name}. " f"Valid values are: {valid_values}"
            )
    raise ValueError(
        f"Invalid type {type(value).__name__} for {column_name}. "
        f"Expected {enum_class.__name__} or string."
    )


def create_enum_validator(enum_class, column_name: str):
    """Create a validator function for enum columns"""

    def validator(target, value, oldvalue, initiator):
        if value is None:
            return value
        return validate_enum_value(value, enum_class, column_name)

    return validator


# ==================== DATABASE ENGINE & SESSION ====================

_engine = None
_SessionLocal = None


def get_engine(database_url: str = None):
    """Database engine singleton with connection pool"""
    global _engine
    if _engine is None:
        if database_url is None:
            from app.core.config import settings

            database_url = settings.DATABASE_URL

        _engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False,
        )
    return _engine


def get_session_local(engine=None):
    """SessionLocal singleton"""
    global _SessionLocal
    if _SessionLocal is None:
        if engine is None:
            engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


# ==================== DATABASE HEALTH CHECK ====================


def check_database_connection() -> dict:
    """Database baglanti kontrolu"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "message": "Database baglantisi basarili"}
    except Exception as e:
        logger.error(f"Database baglanti hatasi: {e}")
        return {"status": "unhealthy", "message": str(e)}


def check_table_exists(table_name: str) -> bool:
    """Tablo var mi kontrol et"""
    try:
        engine = get_engine()
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        logger.error(f"Tablo kontrol hatasi: {e}")
        return False


def get_missing_tables() -> list:
    """Eksik tablolari bul"""
    try:
        engine = get_engine()
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        required_tables = set(Base.metadata.tables.keys())
        return list(required_tables - existing_tables)
    except Exception as e:
        logger.error(f"Eksik tablo kontrol hatasi: {e}")
        return []


def get_missing_columns(table_name: str) -> list:
    """Tablodaki eksik kolonlari bul"""
    try:
        engine = get_engine()
        inspector = inspect(engine)

        if table_name not in inspector.get_table_names():
            return []

        existing_columns = {col["name"] for col in inspector.get_columns(table_name)}

        if table_name not in Base.metadata.tables:
            return []

        required_columns = {col.name for col in Base.metadata.tables[table_name].columns}
        return list(required_columns - existing_columns)
    except Exception as e:
        logger.error(f"Eksik kolon kontrol hatasi ({table_name}): {e}")
        return []


# ==================== AUTO REPAIR SYSTEM ====================


def create_missing_tables() -> dict:
    """Eksik tablolari olustur"""
    results = {"created": [], "errors": []}
    try:
        engine = get_engine()
        missing = get_missing_tables()

        if not missing:
            return {"created": [], "errors": [], "message": "Tum tablolar mevcut"}

        for table_name in missing:
            try:
                if table_name in Base.metadata.tables:
                    Base.metadata.tables[table_name].create(engine)
                    results["created"].append(table_name)
                    logger.info(f"Tablo olusturuldu: {table_name}")
            except Exception as e:
                results["errors"].append({"table": table_name, "error": str(e)})
                logger.error(f"Tablo olusturma hatasi ({table_name}): {e}")

        return results
    except Exception as e:
        logger.error(f"Tablo olusturma genel hatasi: {e}")
        return {"created": [], "errors": [str(e)]}


def add_missing_columns() -> dict:
    """Eksik kolonlari ekle"""
    results = {"added": [], "errors": []}
    try:
        engine = get_engine()
        inspector = inspect(engine)

        for table_name in inspector.get_table_names():
            if table_name not in Base.metadata.tables:
                continue

            missing_cols = get_missing_columns(table_name)

            for col_name in missing_cols:
                try:
                    col = Base.metadata.tables[table_name].columns[col_name]
                    col_type = col.type.compile(engine.dialect)

                    # Default deger belirle
                    default = ""
                    if col.default is not None:
                        if hasattr(col.default, "arg"):
                            if callable(col.default.arg):
                                default = ""
                            else:
                                default = f" DEFAULT '{col.default.arg}'"

                    nullable = "" if col.nullable else " NOT NULL"

                    # Nullable olmayan kolonlara default ekle
                    if not col.nullable and not default:
                        if "INT" in col_type.upper():
                            default = " DEFAULT 0"
                        elif "VARCHAR" in col_type.upper() or "TEXT" in col_type.upper():
                            default = " DEFAULT ''"
                        elif "FLOAT" in col_type.upper() or "DOUBLE" in col_type.upper():
                            default = " DEFAULT 0.0"
                        elif "BOOL" in col_type.upper() or "TINYINT" in col_type.upper():
                            default = " DEFAULT 0"
                        else:
                            nullable = ""  # NULL'a izin ver

                    alter_sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col_name}` {col_type}{nullable}{default}"

                    with engine.connect() as conn:
                        conn.execute(text(alter_sql))
                        conn.commit()

                    results["added"].append(f"{table_name}.{col_name}")
                    logger.info(f"Kolon eklendi: {table_name}.{col_name}")

                except Exception as e:
                    results["errors"].append(
                        {"column": f"{table_name}.{col_name}", "error": str(e)}
                    )
                    logger.error(f"Kolon ekleme hatasi ({table_name}.{col_name}): {e}")

        return results
    except Exception as e:
        logger.error(f"Kolon ekleme genel hatasi: {e}")
        return {"added": [], "errors": [str(e)]}


def repair_database() -> dict:
    """Tam database onarimi - eksik tablo ve kolonlari ekle"""
    logger.info("Database onarim basladi...")

    results = {
        "connection": check_database_connection(),
        "tables": create_missing_tables(),
        "columns": add_missing_columns(),
        "status": "completed",
    }

    # Hata varsa status'u guncelle
    if results["connection"]["status"] == "unhealthy":
        results["status"] = "failed"
    elif results["tables"]["errors"] or results["columns"]["errors"]:
        results["status"] = "completed_with_errors"

    logger.info(f"Database onarim tamamlandi: {results['status']}")
    return results


def init_database(database_url: str = None) -> dict:
    """Database'i baslat - tum tablolari olustur, eksikleri tamamla"""
    try:
        engine = get_engine(database_url)

        # Tum tablolari olustur (varsa atla)
        Base.metadata.create_all(bind=engine)
        logger.info("Database tablolari kontrol edildi/olusturuldu")

        # Eksik kolonlari ekle
        col_result = add_missing_columns()

        return {
            "status": "success",
            "message": "Database basariyla basladi",
            "columns_added": col_result["added"],
            "errors": col_result["errors"],
        }
    except Exception as e:
        logger.error(f"Database baslama hatasi: {e}")
        return {"status": "error", "message": str(e)}


def get_database_stats() -> dict:
    """Database istatistikleri"""
    try:
        engine = get_engine()
        inspector = inspect(engine)

        stats = {"tables": {}, "total_tables": 0, "total_rows": 0}

        for table_name in inspector.get_table_names():
            try:
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
                    count = result.scalar()
                    stats["tables"][table_name] = count
                    stats["total_rows"] += count
            except Exception:
                stats["tables"][table_name] = -1

        stats["total_tables"] = len(stats["tables"])
        return stats
    except Exception as e:
        logger.error(f"Database istatistik hatasi: {e}")
        return {"error": str(e)}


# ==================== ENUMS ====================


class UserRole(enum.Enum):
    """Legacy role enum - use Role table for new system"""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


# ==================== ROLE & PERMISSION SYSTEM ====================


class Role(Base):
    """Discord-like role system"""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # "sunucu_sahibi", "bas_admin", etc.
    display_name = Column(String(100), nullable=False)  # "Sunucu Sahibi", "Baş Admin"
    color = Column(String(7), default="#ffffff")  # Hex color for display
    icon = Column(String(50))  # Icon name or emoji
    priority = Column(Integer, default=0)  # Higher = more important (for display order)

    # Permissions (JSON for flexibility)
    permissions = Column(JSON, default=dict)

    # System flags
    is_default = Column(Boolean, default=False)  # Given to all new users
    is_system = Column(Boolean, default=False)  # Cannot be deleted (admin, user)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_roles = relationship(
        "UserRoleAssignment", back_populates="role", cascade="all, delete-orphan"
    )


class UserRoleAssignment(Base):
    """User to Role mapping - can assign by user_id, steam_id, or username"""

    __tablename__ = "user_role_assignments"

    id = Column(Integer, primary_key=True, index=True)

    # Can assign by any of these
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    steam_id = Column(String(50), nullable=True, index=True)  # Assign by Steam ID
    username_pattern = Column(String(100), nullable=True)  # Assign by username (supports wildcards)

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)

    assigned_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    reason = Column(String(255))  # Why this role was assigned

    # Relationships
    role = relationship("Role", back_populates="user_roles")
    user = relationship("User", foreign_keys=[user_id], backref="role_assignments")
    assigner = relationship("User", foreign_keys=[assigned_by])

    __table_args__ = (
        Index("ix_user_role_steam", "steam_id"),
        Index("ix_user_role_user", "user_id"),
    )


# Default permissions structure
DEFAULT_PERMISSIONS = {
    # Admin Panel
    "admin.access": False,
    "admin.users.view": False,
    "admin.users.edit": False,
    "admin.users.ban": False,
    "admin.users.delete": False,
    "admin.roles.manage": False,
    "admin.servers.view": False,
    "admin.servers.edit": False,
    "admin.servers.delete": False,
    "admin.payments.view": False,
    "admin.payments.manage": False,
    "admin.settings.view": False,
    "admin.settings.edit": False,
    "admin.announcements.manage": False,
    # Forum
    "forum.post": True,
    "forum.edit_own": True,
    "forum.delete_own": True,
    "forum.edit_any": False,
    "forum.delete_any": False,
    "forum.pin": False,
    "forum.lock": False,
    "forum.moderate": False,
    # Servers
    "servers.create": False,
    "servers.manage_own": True,
    "servers.manage_any": False,
    # Shop
    "shop.purchase": True,
    "shop.discount": False,  # Gets discounts
    # Jackpot
    "jackpot.play": True,
    "jackpot.high_limit": False,  # Can bet higher amounts
    # Special
    "bypass_cooldowns": False,
    "see_hidden": False,
    "impersonate": False,
}


class UserStatus(enum.Enum):
    ACTIVE = "active"
    BANNED = "banned"
    SUSPENDED = "suspended"
    PENDING = "pending"


class GameType(enum.Enum):
    HLDM = "hldm"
    AG = "ag"
    CS16 = "cs16"


class ServerStatus(enum.Enum):
    PENDING = "pending"
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    DELETED = "deleted"
    CANCELLED = "cancelled"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(enum.Enum):
    IYZICO = "iyzico"
    PAYTR = "paytr"
    BANK_TRANSFER = "bank_transfer"
    BALANCE = "balance"


class TicketStatus(enum.Enum):
    OPEN = "open"
    ANSWERED = "answered"
    WAITING = "waiting"
    CLOSED = "closed"


class TicketPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# ==================== USER MODELS ====================


def _get_default_email_notifications() -> dict:
    """Return default email notification settings - callable for SQLAlchemy default"""
    return {
        "server_expiring": True,
        "payment_received": True,
        "forum_replies": True,
        "mentions": True,
        "announcements": False,
        "weekly_digest": False,
    }


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    avatar = Column(String(255))
    steam_id = Column(String(50), unique=True, index=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    balance = Column(Float, default=0.0)  # TL bakiye (gerçek para)
    balance_coin = Column(Float, default=0.0)  # Coin bakiye (sanal para)
    post_count = Column(Integer, default=0)
    forum_post_count = Column(Integer, default=0)  # Forum post sayisi
    reputation = Column(Integer, default=0)

    # Leaderboard / Oyun istatistikleri
    elo = Column(Integer, default=1000)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    kd_ratio = Column(Float, default=0.0)

    # Email bildirimleri tercihleri - use callable to avoid mutable default sharing
    email_notifications = Column(JSON, default=_get_default_email_notifications, nullable=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    last_seen = Column(DateTime)  # Son aktivite zamanı (online status için)
    last_ip = Column(String(45))

    # 2FA alanlari
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32))
    two_factor_backup_codes = Column(JSON)

    # Guvenlik alanlari
    login_attempts = Column(Integer, default=0)
    lockout_until = Column(DateTime)
    password_changed_at = Column(DateTime)
    must_change_password = Column(Boolean, default=False)
    reset_token = Column(String(64), index=True)
    reset_token_expires = Column(DateTime)

    # Profil alanlari
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(64), index=True)
    email_verification_sent_at = Column(DateTime)
    bio = Column(Text)
    username_changed = Column(Boolean, default=False)  # Kullanici adi degistirildi mi (1 hak)

    # Relationships
    servers = relationship("GameServer", back_populates="owner", lazy="dynamic")
    payments = relationship("Payment", back_populates="user", lazy="dynamic")
    topics = relationship(
        "ForumTopic", back_populates="author", foreign_keys="ForumTopic.author_id", lazy="dynamic"
    )
    posts = relationship(
        "ForumPost", back_populates="author", foreign_keys="ForumPost.author_id", lazy="dynamic"
    )
    notifications = relationship("Notification", backref="user", lazy="dynamic")
    # Forum Reply relationship (ForumReply tablosu icin)
    forum_replies = relationship("ForumReply", back_populates="author", lazy="dynamic")

    # Security relationships (AŞAMA 4)
    two_factor_auth = relationship("TwoFactorAuth", back_populates="user", uselist=False)
    backup_codes = relationship("BackupCode", back_populates="user", lazy="dynamic")
    oauth_accounts = relationship("OAuthAccount", back_populates="user", lazy="dynamic")
    security_events = relationship(
        "SecurityEvent", foreign_keys="SecurityEvent.user_id", back_populates="user", lazy="dynamic"
    )
    login_history = relationship("LoginHistory", back_populates="user", lazy="dynamic")
    device_sessions = relationship("DeviceSession", back_populates="user", lazy="dynamic")
    gdpr_requests = relationship(
        "GDPRRequest", foreign_keys="GDPRRequest.user_id", back_populates="user", lazy="dynamic"
    )
    download_history = relationship("DownloadHistory", back_populates="user", lazy="dynamic")
    user_activities = relationship("UserActivity", back_populates="user", lazy="dynamic")
    favorite_servers = relationship(
        "UserFavoriteServer", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def is_online(self):
        """Son 5 dakika icinde aktifse online say"""
        if not self.last_login:
            return False
        from datetime import timedelta

        return datetime.utcnow() - self.last_login < timedelta(minutes=5)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    device_type = Column(String(50))  # desktop, mobile, tablet
    location = Column(String(100))  # IP-based location
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime)  # Oturum iptal zamani
    created_at = Column(DateTime, default=func.now())


# ==================== SERVER MODELS ====================


class ServerPackage(Base):
    __tablename__ = "server_packages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    game_type = Column(Enum(GameType), nullable=False)
    slots = Column(Integer, nullable=False)
    features = Column(JSON)
    description = Column(Text)
    price_monthly = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class GameServer(Base):
    __tablename__ = "game_servers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    game_type = Column(Enum(GameType), nullable=False)
    ip_address = Column(String(45), nullable=False)
    port = Column(Integer, nullable=False)
    slots = Column(Integer, nullable=False)
    rcon_password = Column(String(50))
    sv_password = Column(String(50))
    panel_password = Column(String(128))  # Server panel access password
    package_id = Column(Integer, ForeignKey("server_packages.id"))
    is_custom_package = Column(Boolean, default=False)
    features = Column(JSON)
    custom_domain = Column(String(100), unique=True)
    status = Column(Enum(ServerStatus), default=ServerStatus.PENDING)
    current_map = Column(String(64))
    current_players = Column(Integer, default=0)
    expires_at = Column(DateTime)
    auto_renew = Column(Boolean, default=False)
    auto_restart = Column(Boolean, default=True)
    crash_count = Column(Integer, default=0)
    last_crash = Column(DateTime)
    restart_backoff_until = Column(DateTime)  # Exponential backoff timer
    monthly_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_started = Column(DateTime)

    # New columns for server panel v6.0
    unique_code = Column(String(20), unique=True)  # AGTR-2026-00001 format
    mod_type = Column(String(50))  # ag, ag_openag, cstrike, valve, valvenewvalve
    server_path = Column(String(500))  # /home/gameservers/servers/server_X
    screen_name = Column(String(50))  # screen session name
    process_pid = Column(Integer)  # running process PID
    last_heartbeat = Column(DateTime)  # last monitoring check
    installation_id = Column(Integer)  # installation record reference

    # Owner Steam ID for quick lookup (denormalized for performance)
    owner_steam_id = Column(String(50), index=True)  # STEAM_0:0:123456 format

    __table_args__ = (
        UniqueConstraint("ip_address", "port", name="uq_server_ip_port"),
        Index("ix_game_servers_owner_steam_id", "owner_steam_id"),
    )

    # Relationships
    owner = relationship("User", back_populates="servers")
    package = relationship("ServerPackage", backref="servers")


class ServerAction(Base):
    __tablename__ = "server_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(50), nullable=False)
    details = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.now())


# ==================== SERVER PANEL v6.0 MODELS ====================


class InstallationStatus(enum.Enum):
    PENDING = "PENDING"
    INSTALLING = "INSTALLING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AdminAuthType(enum.Enum):
    STEAM = "STEAM"
    IP = "IP"
    NAME = "NAME"


class BanType(enum.Enum):
    STEAM = "STEAM"
    IP = "IP"
    BOTH = "BOTH"


class CommandType(enum.Enum):
    RCON = "RCON"
    CONSOLE = "CONSOLE"
    SCHEDULED = "SCHEDULED"
    SYSTEM = "SYSTEM"


class RotationType(enum.Enum):
    SEQUENTIAL = "SEQUENTIAL"
    RANDOM = "RANDOM"
    VOTE = "VOTE"


class OwnershipAction(enum.Enum):
    CREATED = "CREATED"
    TRANSFERRED = "TRANSFERRED"
    EXPIRED = "EXPIRED"
    DELETED = "DELETED"
    RENEWED = "RENEWED"
    SUSPENDED = "SUSPENDED"
    UNSUSPENDED = "UNSUSPENDED"


class TaskType(enum.Enum):
    """Zamanlanmis gorev tipi"""

    RESTART = "restart"
    MAP_CHANGE = "map_change"
    BACKUP = "backup"
    ANNOUNCEMENT = "announcement"
    RCON_COMMAND = "rcon_command"


class ScheduleType(enum.Enum):
    """Zamanlama tipi"""

    CRON = "cron"
    INTERVAL = "interval"
    ONE_TIME = "one_time"


class IntervalUnit(enum.Enum):
    """Aralik birimi"""

    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"


class ServerInstallation(Base):
    """Sunucu kurulum takibi"""

    __tablename__ = "server_installations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    unique_code = Column(String(20), unique=True, nullable=False)
    status = Column(Enum(InstallationStatus), default=InstallationStatus.PENDING)
    progress_percent = Column(Integer, default=0)
    current_step = Column(String(100))
    total_steps = Column(Integer, default=8)
    error_message = Column(Text)
    template_type = Column(String(50))
    celery_task_id = Column(String(100))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    server = relationship("GameServer", backref="installation")
    user = relationship("User", backref="server_installations")


class ServerOwnershipHistory(Base):
    """Sunucu sahiplik gecmisi"""

    __tablename__ = "server_ownership_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    unique_code = Column(String(20))
    action = Column(Enum(OwnershipAction), nullable=False)
    details = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    server = relationship("GameServer", backref="ownership_history")
    user = relationship("User", backref="server_ownership_history")


class ServerMetrics(Base):
    """Sunucu kaynak kullanimi metrikleri (CPU, RAM, Network)"""

    __tablename__ = "server_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(
        Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Resource metrics
    cpu_percent = Column(Float, comment="Process CPU usage (0-100 per core)")
    memory_mb = Column(Float, comment="Process RSS memory in MB")
    network_in_mbps = Column(Float, nullable=True, comment="Network input in Mbps")
    network_out_mbps = Column(Float, nullable=True, comment="Network output in Mbps")

    # Process health
    process_status = Column(String(20), comment="running, zombie, sleeping, etc.")
    player_count = Column(Integer, default=0, comment="Current player count from A2S query")

    # Timestamp
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)

    # Composite index for time-series queries
    __table_args__ = (
        Index("idx_metrics_server_time", "server_id", "timestamp"),
        {"comment": "Server resource metrics for monitoring and alerting"},
    )

    # Relationships
    server = relationship("GameServer", backref="metrics")


class CommandQuota(Base):
    """Daily command usage quotas per user"""

    __tablename__ = "command_quotas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    command_type = Column(String(50), nullable=False, comment="ban, kick, restart, etc.")
    usage_count = Column(Integer, nullable=False, default=0, comment="Commands used today")
    quota_date = Column(Date, nullable=False, comment="Date of quota (UTC)")

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("user_id", "command_type", "quota_date", name="uq_user_command_date"),
        Index("idx_quota_date", "quota_date"),
        Index("idx_user_command", "user_id", "command_type"),
        {"comment": "Daily command usage quotas per user"},
    )

    # Relationships
    user = relationship("User", backref="command_quotas")


class SystemAlert(Base):
    """System alerts and notifications"""

    __tablename__ = "system_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False, comment="info, warning, error, critical")
    title = Column(String(255), nullable=False, comment="Alert title")
    message = Column(Text, nullable=False, comment="Alert message")
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_resolved = Column(Boolean, default=False, nullable=False, comment="Alert resolved")
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_alert_level_created", "level", "created_at"),
        Index("idx_alert_server", "server_id"),
        Index("idx_alert_resolved", "is_resolved", "created_at"),
        {"comment": "System alerts and notifications"},
    )

    # Relationships
    server = relationship("GameServer", backref="alerts")
    user = relationship("User", backref="alerts")


class ServerAdminEntry(Base):
    """AMXModX admin kayitlari"""

    __tablename__ = "server_admin_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    steam_id = Column(String(50), nullable=False)
    name = Column(String(100))
    flags = Column(String(50), default="abcdefghijklmnopqrstu")
    password = Column(String(100))
    access_level = Column(Integer, default=0)
    auth_type = Column(Enum(AdminAuthType), default=AdminAuthType.STEAM)
    added_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("server_id", "steam_id", name="uq_server_admin"),)

    # Relationships
    server = relationship("GameServer", backref="admin_entries")
    added_by_user = relationship("User", backref="added_server_admins")


class ServerBan(Base):
    """Sunucu ban kayitlari"""

    __tablename__ = "server_bans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    steam_id = Column(String(50))
    ip_address = Column(String(45))
    name = Column(String(100))
    reason = Column(String(500))
    banned_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    banned_by_admin = Column(String(100))
    duration_minutes = Column(Integer, default=0)  # 0 = permanent
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    ban_type = Column(Enum(BanType), default=BanType.STEAM)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    server = relationship("GameServer", backref="bans")
    banned_by_user = relationship("User", backref="issued_bans")


class ServerConsoleHistory(Base):
    """RCON komut gecmisi"""

    __tablename__ = "server_console_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    command = Column(String(500), nullable=False)
    response = Column(Text)
    command_type = Column(Enum(CommandType), default=CommandType.RCON)
    execution_time_ms = Column(Integer)
    ip_address = Column(String(45))
    is_success = Column(Boolean, default=True)
    error_message = Column(String(500))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    server = relationship("GameServer", backref="console_history")
    user = relationship("User", backref="console_commands")


class ServerStatsHourly(Base):
    """Saatlik sunucu istatistikleri"""

    __tablename__ = "server_stats_hourly"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    hour_timestamp = Column(DateTime, nullable=False)
    avg_players = Column(Float, default=0)
    max_players = Column(Integer, default=0)
    min_players = Column(Integer, default=0)
    unique_players = Column(Integer, default=0)
    total_joins = Column(Integer, default=0)
    total_leaves = Column(Integer, default=0)
    map_changes = Column(Integer, default=0)
    most_played_map = Column(String(64))
    cpu_usage_avg = Column(Float)
    ram_usage_avg = Column(Float)
    uptime_percent = Column(Float, default=100)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("server_id", "hour_timestamp", name="uq_server_hour"),)

    # Relationships
    server = relationship("GameServer", backref="hourly_stats")


class ServerStatsDaily(Base):
    """Gunluk sunucu istatistikleri"""

    __tablename__ = "server_stats_daily"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(
        Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date = Column(DateTime, nullable=False, index=True)

    total_players = Column(Integer, default=0)
    unique_players = Column(Integer, default=0)
    avg_players = Column(Float, default=0.0)
    max_players = Column(Integer, default=0)
    peak_hour = Column(Integer)  # 0-23

    total_playtime_minutes = Column(Integer, default=0)
    avg_session_minutes = Column(Float, default=0.0)

    most_played_map = Column(String(64))
    map_playtime_json = Column(JSON)  # {"de_dust2": 120, "de_inferno": 80}

    created_at = Column(DateTime, default=func.now())

    __table_args__ = (Index("idx_server_date", "server_id", "date", unique=True),)

    # Relationships
    server = relationship("GameServer", backref="daily_stats")


class ServerStatsWeekly(Base):
    """Haftalik sunucu istatistikleri"""

    __tablename__ = "server_stats_weekly"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(
        Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    week_start = Column(DateTime, nullable=False, index=True)  # Pazartesi

    total_players = Column(Integer, default=0)
    unique_players = Column(Integer, default=0)
    avg_players = Column(Float, default=0.0)
    max_players = Column(Integer, default=0)

    total_playtime_hours = Column(Float, default=0.0)
    avg_session_minutes = Column(Float, default=0.0)

    retention_rate = Column(Float)  # % geri donen oyuncular
    new_players = Column(Integer, default=0)
    returning_players = Column(Integer, default=0)

    created_at = Column(DateTime, default=func.now())

    __table_args__ = (Index("idx_server_week", "server_id", "week_start", unique=True),)

    # Relationships
    server = relationship("GameServer", backref="weekly_stats")


class PlayerSession(Base):
    """Oyuncu oturum kayitlari"""

    __tablename__ = "player_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(
        Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    player_name = Column(String(100))
    steam_id = Column(String(50), index=True)

    join_time = Column(DateTime, nullable=False)
    leave_time = Column(DateTime)
    duration_minutes = Column(Integer)

    map_name = Column(String(64))

    created_at = Column(DateTime, default=func.now())

    __table_args__ = (Index("idx_session_time", "server_id", "join_time"),)

    # Relationships
    server = relationship("GameServer", backref="player_sessions")


class ServerQuickCommand(Base):
    """Hizli RCON komutlari"""

    __tablename__ = "server_quick_commands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    command = Column(String(500), nullable=False)
    description = Column(String(255))
    icon = Column(String(50))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    server = relationship("GameServer", backref="quick_commands")
    creator = relationship("User", backref="created_quick_commands")


class ServerMapPool(Base):
    """Harita havuzlari"""

    __tablename__ = "server_map_pools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    maps = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False)
    rotation_type = Column(Enum(RotationType), default=RotationType.SEQUENTIAL)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    server = relationship("GameServer", backref="map_pools")
    creator = relationship("User", backref="created_map_pools")


class ServerScheduledTask(Base):
    """Zamanlanmis sunucu gorevleri"""

    __tablename__ = "server_scheduled_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    task_name = Column(String(100), nullable=False)
    task_type = Column(Enum(TaskType), nullable=False)
    schedule_type = Column(Enum(ScheduleType), nullable=False)

    # Cron zamanlama
    cron_minute = Column(String(20))  # "*/30", "0", "15"
    cron_hour = Column(String(20))  # "*/6", "3", "12"
    cron_day = Column(String(20))  # "*", "1", "15"
    cron_month = Column(String(20))  # "*", "1-6"
    cron_day_of_week = Column(String(20))  # "0-6", "1,3,5"

    # Aralik zamanlama
    interval_value = Column(Integer)
    interval_unit = Column(Enum(IntervalUnit))

    # Tek sefer zamanlama
    scheduled_time = Column(DateTime)

    # Gorev yapilandirmasi (JSON)
    task_config = Column(JSON)  # {"map": "de_dust2"}, {"message": "Sunucu 5dk icinde restart"}

    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    last_run = Column(DateTime)
    next_run = Column(DateTime)

    # APScheduler job ID
    apscheduler_job_id = Column(String(100), unique=True)

    # Relationships
    server = relationship("GameServer", backref="scheduled_tasks")
    creator = relationship("User", backref="created_scheduled_tasks")
    executions = relationship(
        "ScheduledTaskExecution", back_populates="task", cascade="all, delete-orphan"
    )


class ScheduledTaskExecution(Base):
    """Zamanlanmis gorev calisma gecmisi"""

    __tablename__ = "scheduled_task_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("server_scheduled_tasks.id", ondelete="CASCADE"))
    executed_at = Column(DateTime, default=func.now())
    status = Column(String(20))  # success, failed, skipped
    result_message = Column(Text)
    execution_time_ms = Column(Integer)

    # Relationships
    task = relationship("ServerScheduledTask", back_populates="executions")


# ==================== PAYMENT MODELS ====================


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # Changed to SET NULL for soft delete protection
    amount = Column(Float, nullable=False)
    original_amount = Column(Float)  # Indirim oncesi tutar
    discount_amount = Column(Float, default=0)  # Indirim miktari
    method = Column(Enum(PaymentMethod))
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    external_id = Column(String(100))
    reference_code = Column(String(50), unique=True)
    description = Column(String(255))
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="SET NULL"))
    months = Column(Integer, default=1)
    ip_address = Column(String(45))
    payment_metadata = Column(JSON)
    coupon_id = Column(Integer, ForeignKey("coupons.id", ondelete="SET NULL"))
    coupon_code = Column(String(50))  # Kullanilan kupon kodu
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    cancelled_at = Column(DateTime)  # Iptal zamani
    deleted_at = Column(DateTime, nullable=True)  # Soft delete timestamp
    is_deleted = Column(Boolean, default=False)  # Soft delete flag

    # Relationships
    user = relationship("User", back_populates="payments")
    server = relationship("GameServer", backref="payments")


class BankTransfer(Base):
    __tablename__ = "bank_transfers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    sender_name = Column(String(100))
    sender_iban = Column(String(50))
    receipt_image = Column(String(255))
    notes = Column(Text)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    created_at = Column(DateTime, default=func.now())


# ==================== FORUM MODELS ====================


class ForumCategory(Base):
    __tablename__ = "forum_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    color = Column(String(20))
    parent_id = Column(Integer, ForeignKey("forum_categories.id"))
    game_slug = Column(String(50), nullable=True, index=True)  # cs16, halflife vb.
    display_order = Column(Integer, default=0)
    is_visible = Column(Boolean, default=True)
    min_role_to_view = Column(Enum(UserRole), default=UserRole.USER)
    min_role_to_post = Column(Enum(UserRole), default=UserRole.USER)
    topic_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)
    last_topic_id = Column(Integer)  # Son konu ID
    last_post_at = Column(DateTime)  # Son post zamani
    is_locked = Column(Boolean, default=False)  # Kilitli kategori
    is_hidden = Column(Boolean, default=False)  # Gizli kategori
    created_at = Column(DateTime, default=func.now())

    # Relationships
    topics = relationship("ForumTopic", back_populates="category", lazy="dynamic")

    @property
    def last_topic(self):
        """Son konu"""
        return self.topics.order_by(ForumTopic.created_at.desc()).first()


class ForumTopic(Base):
    __tablename__ = "forum_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(
        Integer, ForeignKey("forum_categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(200), nullable=False)
    slug = Column(String(220), nullable=False, index=True)
    content = Column(Text)  # Konu icerigi
    is_active = Column(Boolean, default=True, index=True)  # Aktif/silindi - siralama icin index
    is_pinned = Column(Boolean, default=False, index=True)  # Pinned topics siralama icin
    is_sticky = Column(Boolean, default=False)  # Sticky topics
    is_locked = Column(Boolean, default=False, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    is_solved = Column(Boolean, default=False)  # Cozulmus konu
    view_count = Column(Integer, default=0, index=True)  # Popular topics siralama icin
    reply_count = Column(Integer, default=0)
    likes = Column(Integer, default=0)  # Begeni sayisi
    last_post_id = Column(Integer)
    last_post_at = Column(DateTime, index=True)  # Son aktivite siralama icin
    last_post_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    last_reply_id = Column(Integer)  # Son yanit ID
    last_reply_at = Column(DateTime)  # Son yanit zamani
    created_at = Column(DateTime, default=func.now(), index=True)  # Yeni konular siralama icin
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Edit tracking
    edited_at = Column(DateTime)
    edited_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Composite indexes for common queries
    __table_args__ = (
        # Kategori + is_active + is_pinned + created_at (kategori sayfalari icin)
        Index(
            "ix_forum_topics_category_active_pinned",
            "category_id",
            "is_active",
            "is_pinned",
            "created_at",
        ),
        # is_active + view_count (populer konular icin)
        Index("ix_forum_topics_active_views", "is_active", "view_count"),
        # is_active + created_at (yeni konular icin)
        Index("ix_forum_topics_active_created", "is_active", "created_at"),
    )

    # user_id alias for backward compatibility
    @property
    def user_id(self):
        return self.author_id

    # Relationships
    author = relationship("User", back_populates="topics", foreign_keys=[author_id])
    category = relationship("ForumCategory", back_populates="topics")
    posts = relationship("ForumPost", back_populates="topic", lazy="dynamic")
    last_poster = relationship("User", foreign_keys=[last_post_by])
    editor = relationship("User", foreign_keys=[edited_by])


class ForumPost(Base):
    __tablename__ = "forum_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime)
    edited_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    edit_reason = Column(String(200))
    like_count = Column(Integer, default=0)
    is_first_post = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    author = relationship("User", back_populates="posts", foreign_keys=[author_id])
    topic = relationship("ForumTopic", back_populates="posts")
    editor = relationship("User", foreign_keys=[edited_by])


class ForumPostLike(Base):
    __tablename__ = "forum_post_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_post_like"),)


class ForumReply(Base):
    """Forum Yaniti - forum_replies tablosu"""

    __tablename__ = "forum_replies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(
        Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_reply_id = Column(
        Integer, ForeignKey("forum_replies.id", ondelete="SET NULL"), index=True
    )  # Nested replies
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_best_answer = Column(Boolean, default=False)  # Best answer feature
    likes = Column(Integer, default=0)  # Begeni sayisi
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Edit tracking
    edited_at = Column(DateTime)

    # Composite index for topic replies query (topic_id + is_active + created_at)
    __table_args__ = (
        Index("ix_forum_replies_topic_active_created", "topic_id", "is_active", "created_at"),
    )

    # Relationships
    topic = relationship("ForumTopic", backref="replies")
    author = relationship("User", back_populates="forum_replies")
    parent_reply = relationship("ForumReply", remote_side=[id], backref="child_replies")

    # Alias for backward compatibility (some code uses reply.user instead of reply.author)
    @property
    def user(self):
        return self.author

    # Alias for consistency with old code
    @property
    def is_solution(self):
        return self.is_best_answer


class ForumReportStatus(enum.Enum):
    """Forum report status"""

    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ForumReport(Base):
    """Forum content reports - spam, harassment etc."""

    __tablename__ = "forum_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_type = Column(String(20), nullable=False)  # "topic" or "reply"
    content_id = Column(Integer, nullable=False)  # topic_id or reply_id
    reason = Column(String(50), nullable=False)  # spam, harassment, inappropriate, other
    details = Column(Text)  # Additional details from reporter
    status = Column(Enum(ForumReportStatus), default=ForumReportStatus.PENDING)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at = Column(DateTime)
    resolution_notes = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Unique constraint to prevent duplicate reports from same user
    __table_args__ = (
        UniqueConstraint("reporter_id", "content_type", "content_id", name="uq_forum_report"),
        Index("idx_forum_report_content", "content_type", "content_id"),
        Index("idx_forum_report_status", "status"),
    )

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])


# ==================== FORUM TAG SYSTEM ====================


class ForumTag(Base):
    """Forum etiketleri"""

    __tablename__ = "forum_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(20), default="#6b7280")
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    topic_tags = relationship("ForumTopicTag", back_populates="tag", cascade="all, delete-orphan")


class ForumTopicTag(Base):
    """Konu-Etiket iliskisi"""

    __tablename__ = "forum_topic_tags"

    topic_id = Column(Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("forum_tags.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    topic = relationship("ForumTopic", backref="topic_tags")
    tag = relationship("ForumTag", back_populates="topic_tags")


# ==================== FORUM MENTION SYSTEM ====================


class ForumMention(Base):
    """Forum mentionlari - @kullanici_adi"""

    __tablename__ = "forum_mentions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mentioned_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_type = Column(String(20), nullable=False)  # topic, reply
    content_id = Column(Integer, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="mentions_received")
    mentioner = relationship("User", foreign_keys=[mentioned_by], backref="mentions_made")

    __table_args__ = (
        Index("idx_mention_user", "user_id", "is_read"),
        Index("idx_mention_content", "content_type", "content_id"),
    )


# ==================== FORUM SUBSCRIPTION SYSTEM ====================


class ForumSubscription(Base):
    """Forum konu abonelikleri"""

    __tablename__ = "forum_subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id = Column(
        Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", backref="forum_subscriptions")
    topic = relationship("ForumTopic", backref="subscriptions")

    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_forum_subscription"),)


# ==================== FORUM BADGE SYSTEM ====================


class ForumBadge(Base):
    """Forum rozet/badge tanimlari"""

    __tablename__ = "forum_badges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(50))  # Icon name (e.g., "star", "heart", "crown")
    color = Column(String(20))  # Hex color (e.g., "#FF6B00")
    requirement_type = Column(String(50))  # topics_count, replies_count, likes_received, etc.
    requirement_value = Column(Integer)  # Threshold value to earn badge
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user_badges = relationship("UserForumBadge", back_populates="badge")


class UserForumBadge(Base):
    """Kullanicilarin kazandigi rozetler"""

    __tablename__ = "user_forum_badges"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    badge_id = Column(Integer, ForeignKey("forum_badges.id", ondelete="CASCADE"), primary_key=True)
    earned_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", backref="forum_badges")
    badge = relationship("ForumBadge", back_populates="user_badges")


# ==================== SUPPORT MODELS ====================


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # Changed to SET NULL for soft delete protection
    subject = Column(String(200), nullable=False)
    status = Column(String(20), default="open")  # open, pending, resolved, closed
    priority = Column(String(20), default="medium")  # low, medium, high
    category = Column(String(50), default="other")  # technical, billing, account, other
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="SET NULL"))
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete timestamp
    is_deleted = Column(Boolean, default=False)  # Soft delete flag

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="tickets")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(
        Integer, ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    content = Column(Text, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_staff_reply = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    author_name = Column(String(100))
    attachment = Column(String(255))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    ticket = relationship("SupportTicket", backref="messages")


# ==================== SYSTEM MODELS ====================


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.now())


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(220), unique=True, index=True)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    show_on_homepage = Column(Boolean, default=True)
    type = Column(String(20), default="info")  # info, warning, success, danger
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)


class SiteSettings(Base):
    """Site genel ayarlari - tek satir"""

    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_name = Column(String(100), default="AGTR Merkezi")
    site_description = Column(Text, default="Half-Life & CS 1.6 Gaming Platform")
    contact_email = Column(String(100), default="info@agtrmerkezi.com")
    discord_url = Column(String(255))
    maintenance_mode = Column(Boolean, default=False)
    registration_enabled = Column(Boolean, default=True)

    # Fiyatlandirma
    price_per_slot = Column(Float, default=5.0)
    discount_3_month = Column(Float, default=0.10)
    discount_6_month = Column(Float, default=0.15)
    discount_12_month = Column(Float, default=0.25)

    # Tema ayarlari
    theme_settings = Column(JSON, default={})

    # Branding / Logo ayarlari
    logo_url = Column(String(500), default="/logo-navbar.png")
    logo_dark_url = Column(String(500))
    logo_mobile_url = Column(String(500))
    logo_width = Column(String(20), default="auto")
    logo_height = Column(String(20), default="36")
    logo_text = Column(String(50), default="AGTR")
    logo_subtitle = Column(String(50), default="MERKEZİ")
    show_logo_text = Column(Boolean, default=False)
    footer_logo_url = Column(String(500))
    footer_logo_width = Column(String(20), default="auto")
    footer_logo_height = Column(String(20), default="48")
    favicon_url = Column(String(500), default="/favicon.ico")
    primary_color = Column(String(20), default="#f97316")
    secondary_color = Column(String(20), default="#3b82f6")

    # Timestamps
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# ==================== AUDIT LOG ====================


class AuditLog(Base):
    """Admin ve kullanici islemlerini logla"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))  # user, server, payment, etc.
    entity_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=func.now(), index=True)


# ==================== PLUGIN SYSTEM ====================


class Plugin(Base):
    """Admin tarafindan eklenen plugin havuzu"""

    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    version = Column(String(20))
    author = Column(String(100))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    game_type = Column(Enum(GameType))
    category = Column(String(50))  # admin, fun, stats, etc.
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    requires_config = Column(Boolean, default=False)
    config_template = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ServerPlugin(Base):
    """Sunucuya yuklu pluginler"""

    __tablename__ = "server_plugins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    plugin_id = Column(Integer, ForeignKey("plugins.id", ondelete="CASCADE"))
    custom_plugin_name = Column(String(100))
    custom_plugin_file = Column(String(255))
    is_enabled = Column(Boolean, default=True)
    config_values = Column(JSON)
    installed_at = Column(DateTime, default=func.now())
    installed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Plugin status tracking columns
    status = Column(String(20), default="active")  # active, inactive, error, loading
    last_error = Column(Text, nullable=True)
    last_checked = Column(DateTime, nullable=True)
    error_count = Column(Integer, default=0)

    __table_args__ = (UniqueConstraint("server_id", "plugin_id", name="uq_server_plugin"),)


# ==================== SCHEDULED TASKS ====================


class ScheduledTask(Base):
    """Zamanlanmis gorevler"""

    __tablename__ = "scheduled_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    task_type = Column(String(50), nullable=False)  # restart, command, backup, message
    name = Column(String(100), nullable=False)
    schedule_type = Column(String(20), nullable=False)  # once, daily, weekly, cron
    schedule_value = Column(String(100))  # cron expression veya time
    command = Column(Text)
    is_enabled = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    run_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class TaskLog(Base):
    """Zamanlanmis gorev loglari"""

    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("scheduled_tasks.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)  # success, failed, skipped
    output = Column(Text)
    error_message = Column(Text)
    duration_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now())


# ==================== NOTIFICATIONS ====================


class Notification(Base):
    """Kullanici bildirimleri"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # server, payment, ticket, system
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500))
    is_read = Column(Boolean, default=False)
    is_email_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), index=True)
    read_at = Column(DateTime)


# ==================== RESOURCE MONITORING ====================


class ResourceLog(Base):
    """Sunucu kaynak kullanim loglari"""

    __tablename__ = "resource_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    cpu_percent = Column(Float)
    memory_mb = Column(Float)
    player_count = Column(Integer)
    map_name = Column(String(50))
    created_at = Column(DateTime, default=func.now(), index=True)


# ==================== BACKUP SYSTEM ====================


class BackupLog(Base):
    """Yedekleme loglari"""

    __tablename__ = "backup_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"))
    backup_type = Column(String(20), nullable=False)  # full, config, database
    file_path = Column(String(500))
    file_size = Column(Integer)
    status = Column(String(20), nullable=False)  # success, failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)


# ==================== RCON SYSTEM ====================


class RconLog(Base):
    """RCON komut loglari"""

    __tablename__ = "rcon_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    command = Column(String(500), nullable=False)
    response = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.now(), index=True)


# ==================== SERVER CONFIG HISTORY ====================


class ConfigHistory(Base):
    """server.cfg degisiklik gecmisi"""

    __tablename__ = "config_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    config_type = Column(String(50), nullable=False)  # server.cfg, mapcycle.txt, etc.
    old_content = Column(Text)
    new_content = Column(Text)
    created_at = Column(DateTime, default=func.now())


# ==================== USER FAVORITES ====================


class UserFavorite(Base):
    """Kullanici favori sunuculari (game_servers icin)"""

    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    server_id = Column(Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "server_id", name="uq_user_favorite"),)


class UserFavoriteServer(Base):
    """Kullanici favori sunuculari - Community sunuculari icin (cihazlar arasi senkronizasyon)"""

    __tablename__ = "user_favorite_servers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    server_id = Column(Integer, nullable=False)  # Can be community server ID or any server ID
    server_ip = Column(String(50))  # Store IP for quick access
    server_port = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Unique constraint - one favorite per user per server
    __table_args__ = (
        UniqueConstraint("user_id", "server_id", name="uq_user_server_favorite"),
        Index("idx_user_favorites_user", "user_id"),
    )

    user = relationship("User", back_populates="favorite_servers")


# ==================== USER PREFERENCES ====================


class UserPreference(Base):
    """Kullanici tercihleri - tema, dil, panel layout vs."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    # Theme & Language
    theme = Column(String(20), default="dark")
    language = Column(String(10), default="tr")
    theme_schedule = Column(JSON, comment="Auto theme switching schedule")
    timezone = Column(String(50), default="Europe/Istanbul")

    # Layout preferences (NEW)
    panel_layout = Column(JSON, comment="Custom panel layout")
    tab_order = Column(JSON, comment="Preferred tab order")
    hidden_tabs = Column(JSON, comment="Hidden tabs")

    # Dashboard widgets
    dashboard_widgets = Column(JSON)
    quick_actions = Column(JSON, comment="FAB quick actions")

    # Notifications
    notifications_email = Column(Boolean, default=True)
    notifications_panel = Column(Boolean, default=True)
    notification_settings = Column(JSON, comment="Detailed notification preferences")

    # Tour guide
    tour_completed = Column(Boolean, default=False, comment="Tour guide completed")

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref=backref("preferences", uselist=False))


# ==================== COUPON ====================
class Coupon(Base):
    """Kupon/Indirim kodlari"""

    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200))
    discount_type = Column(String(20), default="percent")
    discount_value = Column(Float, nullable=False)
    max_discount = Column(Float)
    min_amount = Column(Float)
    usage_limit = Column(Integer)
    usage_count = Column(Integer, default=0)
    single_use_per_user = Column(Boolean, default=True)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


# ==================== INVOICE ====================
class Invoice(Base):
    """Faturalar"""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    invoice_number = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    billing_name = Column(String(100))
    billing_email = Column(String(100))
    billing_address = Column(Text)
    billing_tax_number = Column(String(50))
    status = Column(String(20), default="issued")
    created_at = Column(DateTime, default=func.now())


# ==================== TRANSACTION ====================
class WalletType(enum.Enum):
    """Cüzdan türleri"""

    REAL = "real"  # TL bakiye
    COIN = "coin"  # Sanal para


class TransactionType(enum.Enum):
    """İşlem türleri"""

    DEPOSIT = "deposit"  # Para yatırma
    WITHDRAW = "withdraw"  # Para çekme
    PAYMENT = "payment"  # Ödeme (sunucu kiralama vb.)
    REFUND = "refund"  # İade
    BONUS = "bonus"  # Bonus/hediye
    TRANSFER = "transfer"  # Transfer (kullanıcılar arası)
    GAME_WIN = "game_win"  # Oyun kazancı
    GAME_LOSS = "game_loss"  # Oyun kaybı
    JACKPOT = "jackpot"  # Jackpot işlemi
    EXCHANGE = "exchange"  # TL -> Coin dönüşüm


class Transaction(Base):
    """Bakiye islemleri - Çift cüzdan ledger sistemi"""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    wallet_type = Column(Enum(WalletType), default=WalletType.REAL, nullable=False)
    type = Column(String(50), nullable=False)  # TransactionType value
    amount = Column(Float, nullable=False)
    description = Column(String(500))
    reference_id = Column(String(100), index=True)  # Ödeme ID, oyun ID vb.
    reference_type = Column(String(50))  # payment, game, transfer vb.

    # Ledger bilgileri
    balance_before = Column(Float, default=0)
    balance_after = Column(Float, default=0)

    # Transfer işlemleri için
    target_user_id = Column(Integer, ForeignKey("users.id"))

    # Meta bilgiler
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    extra_data = Column(JSON)  # Ek bilgiler (metadata rezerve kelime)

    # Tarihler
    created_at = Column(DateTime, default=func.now())

    # Index
    __table_args__ = (
        Index("idx_tx_user_wallet", "user_id", "wallet_type"),
        Index("idx_tx_user_type", "user_id", "type"),
        Index("idx_tx_created", "created_at"),
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="transactions")
    target_user = relationship("User", foreign_keys=[target_user_id])


# ==================== BANNER/ADVERTISEMENT ====================
class BannerPosition(enum.Enum):
    """Banner pozisyonlari"""

    HOME_HERO = "home_hero"  # Anasayfa hero section
    HOME_MIDDLE = "home_middle"  # Anasayfa ortası
    HOME_BOTTOM = "home_bottom"  # Anasayfa altı
    SIDEBAR = "sidebar"  # Yan panel
    FORUM_TOP = "forum_top"  # Forum üstü
    SHOP_TOP = "shop_top"  # Shop üstü
    BETWEEN_POSTS = "between_posts"  # Forum postları arası


class BannerType(enum.Enum):
    """Banner türleri"""

    IMAGE = "image"  # Görsel banner
    HTML = "html"  # HTML/custom content
    VIDEO = "video"  # Video banner


class Banner(Base):
    """Banner/Reklam yönetimi"""

    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # Banner adı (admin için)
    title = Column(String(200))  # Gösterilecek başlık (opsiyonel)
    description = Column(Text)  # Banner açıklaması (opsiyonel)

    # Banner içeriği
    type = Column(Enum(BannerType), default=BannerType.IMAGE)
    image_url = Column(String(500))  # Görsel URL'i
    video_url = Column(String(500))  # Video URL'i
    html_content = Column(Text)  # Custom HTML içeriği

    # Link ve hedef
    link_url = Column(String(500))  # Tıklanınca gidilecek link
    link_target = Column(String(20), default="_self")  # _self, _blank
    link_text = Column(String(100))  # CTA button metni

    # Pozisyon ve görüntüleme
    position = Column(Enum(BannerPosition), nullable=False)
    display_order = Column(Integer, default=0)  # Sıralama (küçükten büyüğe)
    width = Column(Integer)  # Genişlik (px, opsiyonel)
    height = Column(Integer)  # Yükseklik (px, opsiyonel)

    # Zamanlama
    start_date = Column(DateTime)  # Başlangıç tarihi
    end_date = Column(DateTime)  # Bitiş tarihi
    is_active = Column(Boolean, default=True)  # Aktif/pasif

    # Hedefleme
    target_pages = Column(JSON)  # Hangi sayfalarda gösterilecek (null = hepsi)
    target_roles = Column(JSON)  # Hangi kullanıcı rollerine (null = hepsi)

    # İstatistikler
    impressions = Column(Integer, default=0)  # Gösterim sayısı
    clicks = Column(Integer, default=0)  # Tıklama sayısı

    # Sponsor/Reklam bilgisi
    is_advertisement = Column(Boolean, default=False)  # Reklam mı kendi bannerimiz mi?
    sponsor_name = Column(String(100))  # Sponsor adı
    sponsor_contact = Column(String(200))  # Sponsor iletişim

    # Meta
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])


# ==================== SECURITY MODELS (AŞAMA 4) ====================


class TwoFactorAuth(Base):
    """Two-Factor Authentication"""

    __tablename__ = "two_factor_auth"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    secret = Column(String(255), nullable=False)
    is_enabled = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    last_used_at = Column(DateTime)
    backup_codes_generated = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="two_factor_auth")


class BackupCode(Base):
    """Backup codes for 2FA"""

    __tablename__ = "backup_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code_hash = Column(String(255), nullable=False)
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    user = relationship("User", back_populates="backup_codes")


class OAuthAccount(Base):
    """OAuth/Social accounts"""

    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)  # steam, discord, google
    provider_id = Column(String(255), nullable=False)
    provider_username = Column(String(255))
    provider_email = Column(String(255))
    provider_avatar = Column(String(500))
    access_token = Column(Text)  # Encrypted
    refresh_token = Column(Text)  # Encrypted
    expires_at = Column(DateTime)
    linked_at = Column(DateTime, default=func.now())
    last_used_at = Column(DateTime)

    __table_args__ = (UniqueConstraint("provider", "provider_id", name="uq_oauth_provider_id"),)

    # Relationship
    user = relationship("User", back_populates="oauth_accounts")


class SecurityEvent(Base):
    """Security events and suspicious activity"""

    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    event_type = Column(String(100), nullable=False)  # failed_login, suspicious_ip, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    geo_location = Column(JSON)  # Country, city, etc.
    event_metadata = Column(JSON)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="security_events")
    resolver = relationship("User", foreign_keys=[resolved_by])


class LoginHistory(Base):
    """Login history tracking"""

    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    login_type = Column(String(50), nullable=False)  # password, oauth, 2fa
    provider = Column(String(50))  # For OAuth logins
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    device_type = Column(String(50))  # mobile, desktop, tablet
    os = Column(String(100))
    browser = Column(String(100))
    geo_location = Column(JSON)
    is_successful = Column(Boolean, default=True)
    failure_reason = Column(String(255))
    created_at = Column(DateTime, default=func.now())

    # Relationship
    user = relationship("User", back_populates="login_history")


class DeviceSession(Base):
    """Device sessions and trusted devices"""

    __tablename__ = "device_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(255), nullable=False)  # Unique device identifier
    device_name = Column(String(255))
    device_type = Column(String(50))
    os = Column(String(100))
    browser = Column(String(100))
    ip_address = Column(String(50))
    is_trusted = Column(Boolean, default=False)
    trusted_at = Column(DateTime)
    last_active_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "device_id", name="uq_user_device"),)

    # Relationship
    user = relationship("User", back_populates="device_sessions")


class GDPRRequest(Base):
    """GDPR data requests"""

    __tablename__ = "gdpr_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    request_type = Column(String(50), nullable=False)  # export, delete, anonymize
    status = Column(String(50), nullable=False)  # pending, processing, completed, failed
    request_data = Column(JSON)
    result_file_path = Column(String(500))
    processed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())
    processed_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="gdpr_requests")
    processor = relationship("User", foreign_keys=[processed_by])


class DownloadHistory(Base):
    """Download history (for GDPR export)"""

    __tablename__ = "download_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    resource_type = Column(String(50))  # plugin, map, etc.
    resource_id = Column(Integer)
    downloaded_at = Column(DateTime, default=func.now())

    # Relationship
    user = relationship("User", back_populates="download_history")


class UserActivity(Base):
    """User activity log (for GDPR export)"""

    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    activity_type = Column(String(100))
    description = Column(Text)
    activity_metadata = Column(JSON)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    user = relationship("User", back_populates="user_activities")


# ==================== CMS MODELS ====================


class SiteImage(Base):
    """Site görselleri yönetimi - admin panelden yüklenen tüm görseller"""

    __tablename__ = "site_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # Görsel adı
    slug = Column(String(100), unique=True, nullable=False, index=True)  # Benzersiz slug
    category = Column(String(50), default="general")  # logo, icon, banner, mascot, upload

    # Dosya bilgileri
    file_path = Column(String(500), nullable=False)  # static/images/...
    file_name = Column(String(255), nullable=False)  # Orijinal dosya adı
    file_size = Column(Integer)  # Bytes
    file_type = Column(String(50))  # image/png, image/jpeg
    width = Column(Integer)  # Piksel
    height = Column(Integer)  # Piksel

    # Açıklama
    alt_text = Column(String(200))  # SEO için alt text
    description = Column(Text)

    # Kullanım yerleri
    usage_locations = Column(JSON, default=list)  # ["navbar", "footer", "hero"]

    # Meta
    is_active = Column(Boolean, default=True)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship
    uploader = relationship("User", foreign_keys=[uploaded_by])


class PageContent(Base):
    """Sayfa içerik yönetimi - CMS benzeri"""

    __tablename__ = "page_contents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    page_slug = Column(String(100), nullable=False, index=True)  # home, about, contact
    section_slug = Column(String(100), nullable=False)  # hero, features, footer

    # İçerik
    title = Column(String(200))
    subtitle = Column(String(300))
    content = Column(Text)  # HTML/Markdown içerik

    # Görseller
    image_url = Column(String(500))
    background_image_url = Column(String(500))

    # Link/CTA
    cta_text = Column(String(100))  # Call to action butonu metni
    cta_link = Column(String(500))  # CTA linki

    # Ayarlar
    settings = Column(JSON, default=dict)  # Ek ayarlar (renk, animasyon vb.)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Meta
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("page_slug", "section_slug", name="uq_page_section"),)


# ==================== JACKPOT SYSTEM MODELS ====================


class JackpotStatus(enum.Enum):
    """Jackpot durumları"""

    WAITING = "waiting"  # Oyuncu bekleniyor
    ACTIVE = "active"  # Oyun aktif, bahisler alınıyor
    ROLLING = "rolling"  # Çekiliş yapılıyor
    COMPLETED = "completed"  # Tamamlandı
    CANCELLED = "cancelled"  # İptal edildi


class JackpotGame(Base):
    """Jackpot oyun turları"""

    __tablename__ = "jackpot_games"

    id = Column(Integer, primary_key=True, autoincrement=True)
    round_number = Column(Integer, nullable=False, unique=True)  # Tur numarası
    status = Column(Enum(JackpotStatus), default=JackpotStatus.WAITING)

    # Havuz bilgileri
    total_pot = Column(Float, default=0)  # Toplam havuz (Armor cinsinden)
    participant_count = Column(Integer, default=0)  # Katılımcı sayısı

    # Kazanan bilgileri
    winner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    winner_ticket = Column(Float)  # Kazanan bilet numarası
    win_chance = Column(Float)  # Kazanma şansı (%)

    # Çekiliş bilgileri
    roll_value = Column(Float)  # Random roll değeri
    roll_animation_seed = Column(String(100))  # Animasyon için seed

    # Komisyon
    house_cut_percent = Column(Float, default=5.0)  # Komisyon yüzdesi
    house_cut_amount = Column(Float, default=0)  # Komisyon miktarı

    # Zamanlar
    started_at = Column(DateTime)  # Oyun başlangıcı
    betting_ends_at = Column(DateTime)  # Bahis bitiş zamanı
    rolled_at = Column(DateTime)  # Çekiliş zamanı
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    winner = relationship("User", foreign_keys=[winner_id])
    bets = relationship("JackpotBet", back_populates="game", cascade="all, delete-orphan")


class JackpotBet(Base):
    """Jackpot bahisleri"""

    __tablename__ = "jackpot_bets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("jackpot_games.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Bahis bilgileri
    amount = Column(Float, nullable=False)  # Armor miktarı
    ticket_start = Column(Float, nullable=False)  # Bilet aralığı başlangıcı
    ticket_end = Column(Float, nullable=False)  # Bilet aralığı bitişi
    chance_percent = Column(Float)  # Kazanma şansı (%)

    # Sonuç
    is_winner = Column(Boolean, default=False)

    # Meta
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_jackpot_bet_game", "game_id"),
        Index("idx_jackpot_bet_user", "user_id"),
    )

    # Relationships
    game = relationship("JackpotGame", back_populates="bets")
    user = relationship("User")


class JackpotHistory(Base):
    """Jackpot geçmişi (istatistikler için)"""

    __tablename__ = "jackpot_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # İstatistikler
    total_games_played = Column(Integer, default=0)
    total_wagered = Column(Float, default=0)  # Toplam bahis (Armor)
    total_won = Column(Float, default=0)  # Toplam kazanç (Armor)
    total_lost = Column(Float, default=0)  # Toplam kayıp (Armor)
    biggest_win = Column(Float, default=0)  # En büyük kazanç
    win_count = Column(Integer, default=0)  # Kazanma sayısı

    # Son güncelleme
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User")


# ==================== ARMOR (COIN) EXCHANGE ====================


class ArmorExchangeRate(Base):
    """TL -> Armor dönüşüm oranları"""

    __tablename__ = "armor_exchange_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tl_amount = Column(Float, nullable=False)  # TL miktarı
    armor_amount = Column(Float, nullable=False)  # Karşılık gelen Armor
    bonus_percent = Column(Float, default=0)  # Bonus yüzdesi

    # Paket bilgileri
    name = Column(String(100))  # "Başlangıç Paketi", "Mega Paket"
    description = Column(String(500))
    is_featured = Column(Boolean, default=False)  # Öne çıkan

    # Geçerlilik
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)

    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


# ==================== COMMUNITY SERVERS (SCRAPED) ====================


class CommunityServer(Base):
    """Taranan topluluk sunuculari - Scraper tarafindan eklenir"""

    __tablename__ = "community_servers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(45), nullable=False)
    port = Column(Integer, nullable=False)
    name = Column(String(200))
    game_type = Column(Enum(GameType), nullable=False)
    game_dir = Column(String(50))  # valve, ag, cstrike, tfc

    # Durum bilgileri
    current_map = Column(String(64))
    current_players = Column(Integer, default=0)
    max_players = Column(Integer, default=0)
    ping = Column(Integer, default=999)
    is_online = Column(Boolean, default=True)
    password_protected = Column(Boolean, default=False)

    # Metadata
    country = Column(String(3))  # TR, US, DE vs.
    region = Column(String(50))  # Europe, Asia vs.
    tags = Column(JSON, default=list)  # ["competitive", "public", "24/7"]

    # Kaynak bilgisi
    source = Column(String(50), default="scraper")  # scraper, manual, gametracker, user
    is_verified = Column(Boolean, default=False)  # Admin onaylı mı?
    is_featured = Column(Boolean, default=False)  # Öne çıkan sunucu

    # Kullanici tarafindan eklenen sunucular icin
    submitted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=True)  # Kullanici aciklamasi

    # İstatistikler
    total_queries = Column(Integer, default=0)
    avg_players = Column(Float, default=0)
    uptime_percent = Column(Float, default=100)

    # Zamanlar
    first_seen = Column(DateTime, default=func.now())
    last_seen = Column(DateTime, default=func.now())
    last_query = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("ip_address", "port", name="uq_community_server_addr"),
        Index("idx_community_server_game", "game_type"),
        Index("idx_community_server_online", "is_online"),
        Index("idx_community_server_country", "country"),
        Index("idx_community_server_submitted_by", "submitted_by"),
    )

    # Relationship
    submitter = relationship("User", foreign_keys=[submitted_by], backref="submitted_servers")

    @property
    def address(self) -> str:
        return f"{self.ip_address}:{self.port}"


class ServerScanLog(Base):
    """Sunucu tarama loglari"""

    __tablename__ = "server_scan_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_type = Column(String(50), nullable=False)  # full, partial, single
    game_types = Column(JSON)  # ["ag", "cs16", "hldm"]
    total_scanned = Column(Integer, default=0)
    online_found = Column(Integer, default=0)
    new_servers = Column(Integer, default=0)
    updated_servers = Column(Integer, default=0)
    duration_seconds = Column(Float)
    error_count = Column(Integer, default=0)
    error_messages = Column(JSON)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    triggered_by = Column(String(50))  # scheduler, manual, api

    @property
    def success_rate(self) -> float:
        if self.total_scanned == 0:
            return 0
        return (self.online_found / self.total_scanned) * 100


# ==================== CONTENT MODERATION SYSTEM ====================


class ContentBlacklist(Base):
    """Forum icerik kara listesi - yasakli kelimeler"""

    __tablename__ = "content_blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), default="general")  # general, spam, slur, advertising
    is_active = Column(Boolean, default=True)
    added_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())

    # Relationship
    adder = relationship("User", foreign_keys=[added_by])


class UserWarning(Base):
    """Kullanici uyarilari"""

    __tablename__ = "user_warnings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reason = Column(String(255), nullable=False)
    warned_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    expires_at = Column(DateTime)  # Uyarinin gecerlilik suresi
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="warnings")
    warner = relationship("User", foreign_keys=[warned_by])

    __table_args__ = (Index("idx_warning_user_expires", "user_id", "expires_at"),)


class ForumBan(Base):
    """Forum banlari (soft ban - sadece forum erisimi engellenir)"""

    __tablename__ = "forum_bans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reason = Column(String(255), nullable=False)
    banned_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    expires_at = Column(DateTime, nullable=False)  # Ban bitis zamani
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="forum_bans")
    banner = relationship("User", foreign_keys=[banned_by])

    __table_args__ = (Index("idx_forum_ban_user_expires", "user_id", "expires_at"),)


class ModerationLog(Base):
    """Moderasyon islem loglari"""

    __tablename__ = "moderation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(50), nullable=False)  # warn, ban, unban, filter, delete
    target_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    moderator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    reason = Column(String(500))
    details = Column(JSON)  # Ek detaylar (silinen icerik, vb.)
    content_type = Column(String(50))  # topic, reply
    content_id = Column(Integer)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.now(), index=True)

    # Relationships
    target_user = relationship("User", foreign_keys=[target_user_id])
    moderator = relationship("User", foreign_keys=[moderator_id])


# ==================== FORUM REACTION SYSTEM ====================


class ReactionType(enum.Enum):
    """Tepki türleri"""

    LIKE = "like"  # 👍
    LOVE = "love"  # ❤️
    LAUGH = "laugh"  # 😂
    THINKING = "thinking"  # 🤔
    SOLUTION = "solution"  # ✅
    PLAYED = "played"  # 🎮


class ForumReaction(Base):
    """Forum tepkileri - çoklu tepki desteği"""

    __tablename__ = "forum_reactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content_type = Column(String(20), nullable=False)  # topic, reply
    content_id = Column(Integer, nullable=False)
    reaction_type = Column(Enum(ReactionType), nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "user_id", "content_type", "content_id", "reaction_type", name="uq_forum_reaction"
        ),
        Index("idx_reaction_content", "content_type", "content_id"),
    )

    user = relationship("User", backref="forum_reactions")


# ==================== FORUM POLL SYSTEM ====================


class ForumPoll(Base):
    """Forum anketleri"""

    __tablename__ = "forum_polls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(
        Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    question = Column(String(500), nullable=False)
    is_multiple_choice = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)
    ends_at = Column(DateTime)  # NULL = süresiz
    total_votes = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    topic = relationship("ForumTopic", backref=backref("poll", uselist=False))
    options = relationship("ForumPollOption", back_populates="poll", cascade="all, delete-orphan")


class ForumPollOption(Base):
    """Anket seçenekleri"""

    __tablename__ = "forum_poll_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poll_id = Column(
        Integer, ForeignKey("forum_polls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text = Column(String(200), nullable=False)
    vote_count = Column(Integer, default=0)
    display_order = Column(Integer, default=0)

    poll = relationship("ForumPoll", back_populates="options")
    votes = relationship("ForumPollVote", back_populates="option", cascade="all, delete-orphan")


class ForumPollVote(Base):
    """Anket oyları"""

    __tablename__ = "forum_poll_votes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    poll_id = Column(
        Integer, ForeignKey("forum_polls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    option_id = Column(
        Integer, ForeignKey("forum_poll_options.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint("poll_id", "option_id", "user_id", name="uq_poll_vote"),
        Index("idx_poll_vote_user", "poll_id", "user_id"),
    )

    option = relationship("ForumPollOption", back_populates="votes")
    user = relationship("User", backref="poll_votes")


# ==================== FORUM TOPIC TEMPLATES ====================


class ForumTopicTemplate(Base):
    """Konu şablonları"""

    __tablename__ = "forum_topic_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    icon = Column(String(50))
    color = Column(String(20), default="#6b7280")
    title_template = Column(String(200))  # "[BUG] {title}" gibi
    content_template = Column(Text)  # Markdown içerik şablonu
    required_fields = Column(JSON)  # ["platform", "game_version"] gibi
    category_ids = Column(JSON)  # Bu şablon hangi kategorilerde kullanılabilir
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())

    creator = relationship("User", backref="created_templates")


# ==================== FORUM DRAFT SYSTEM ====================


class ForumDraft(Base):
    """Taslaklar - cross-device sync için"""

    __tablename__ = "forum_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    draft_type = Column(String(20), nullable=False)  # new_topic, reply, edit_topic, edit_reply
    category_id = Column(Integer, ForeignKey("forum_categories.id", ondelete="CASCADE"))
    topic_id = Column(Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"))
    reply_id = Column(Integer, ForeignKey("forum_replies.id", ondelete="CASCADE"))
    title = Column(String(200))
    content = Column(Text)
    tags = Column(JSON)  # ["tag1", "tag2"]
    poll_data = Column(JSON)  # Anket varsa
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (Index("idx_draft_user_type", "user_id", "draft_type"),)

    user = relationship("User", backref="forum_drafts")


# ==================== FORUM REPUTATION SYSTEM ====================


class ForumReputation(Base):
    """Forum itibar puanları"""

    __tablename__ = "forum_reputation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    topics_created = Column(Integer, default=0)
    replies_given = Column(Integer, default=0)
    likes_received = Column(Integer, default=0)
    likes_given = Column(Integer, default=0)
    solutions_marked = Column(Integer, default=0)  # Yanıtları çözüm olarak işaretlenme
    helpful_count = Column(Integer, default=0)
    spam_count = Column(Integer, default=0)  # Negatif
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", backref=backref("forum_reputation", uselist=False))


class ForumReputationLog(Base):
    """İtibar değişiklik logları"""

    __tablename__ = "forum_reputation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    points = Column(Integer, nullable=False)  # + veya -
    reason = Column(
        String(100), nullable=False
    )  # topic_created, reply_liked, solution_marked, spam_reported
    source_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    content_type = Column(String(20))
    content_id = Column(Integer)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", foreign_keys=[user_id])
    source_user = relationship("User", foreign_keys=[source_user_id])


# ==================== FORUM SPAM FILTER ====================


class SpamFilterRule(Base):
    """Spam filtre kuralları"""

    __tablename__ = "spam_filter_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_type = Column(String(50), nullable=False)  # keyword, regex, link_pattern, flood
    pattern = Column(String(500), nullable=False)
    action = Column(String(20), default="block")  # block, flag, warn
    is_active = Column(Boolean, default=True)
    hit_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now())

    creator = relationship("User")


class SpamLog(Base):
    """Spam tespit logları"""

    __tablename__ = "spam_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_id = Column(Integer, ForeignKey("spam_filter_rules.id", ondelete="SET NULL"))
    content_type = Column(String(20), nullable=False)
    content_preview = Column(String(500))
    action_taken = Column(String(20), nullable=False)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", backref="spam_logs")
    rule = relationship("SpamFilterRule")


# ==================== FORUM BOOKMARK SYSTEM ====================


class ForumBookmark(Base):
    """Konu yer imleri"""

    __tablename__ = "forum_bookmarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id = Column(Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_forum_bookmark"),)

    user = relationship("User", backref="forum_bookmarks")
    topic = relationship("ForumTopic", backref="bookmarks")


# ==================== FORUM TOPIC LIKE (separate from reactions) ====================


class ForumTopicLike(Base):
    """Konu beğenileri"""

    __tablename__ = "forum_topic_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("topic_id", "user_id", name="uq_topic_like"),)


class TemplateCache(Base):
    """Cached game server templates for fast installation"""

    __tablename__ = "template_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mod_type = Column(String(50), nullable=False, unique=True, comment="ag, cs16, hldm, etc.")
    template_name = Column(String(100), nullable=False, comment="Display name")
    version = Column(String(50), nullable=True, comment="Template version")
    file_path = Column(String(500), nullable=False, comment="Path to cached tar.gz")
    file_size_mb = Column(Float, nullable=True, comment="Archive size in MB")
    checksum = Column(String(64), nullable=True, comment="SHA256 checksum")
    is_active = Column(Boolean, default=True, nullable=False, comment="Template is ready to use")
    last_validated = Column(DateTime, nullable=True, comment="Last validation check")
    last_updated = Column(DateTime, nullable=True, comment="Last cache update")
    download_url = Column(String(500), nullable=True, comment="Optional: external download URL")
    extra_data = Column(JSON, nullable=True, comment="Extra template info")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_template_active", "is_active", "mod_type"),
        {"comment": "Cached game server templates for fast installation"},
    )


class ForumReplyLike(Base):
    """Yanıt beğenileri"""

    __tablename__ = "forum_reply_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reply_id = Column(Integer, ForeignKey("forum_replies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("reply_id", "user_id", name="uq_reply_like"),)


# ==================== AUTO-UPDATE SYSTEM ====================


class ServerUpdateLog(Base):
    """Server update history and status tracking"""

    __tablename__ = "server_update_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(
        Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    component = Column(String(50), nullable=False, comment="CS 1.6, AMXModX, Metamod, Plugin")
    status = Column(String(20), nullable=False, comment="started, completed, failed, error")
    message = Column(Text, comment="Update message or error details")
    version_before = Column(String(50), comment="Version before update")
    version_after = Column(String(50), comment="Version after update")
    updated_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    server = relationship("GameServer", backref="update_logs")
    user = relationship("User", backref="update_logs")

    # Indexes
    __table_args__ = (
        Index("idx_update_server_status", "server_id", "status"),
        Index("idx_update_component", "component"),
    )


# ==================== DDOS PROTECTION SYSTEM ====================


class DDoSAttackLog(Base):
    """DDoS attack detection and mitigation logs"""

    __tablename__ = "ddos_attack_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(
        Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    attack_type = Column(String(50), nullable=False, comment="SYN flood, UDP flood, etc.")
    peak_packets_per_second = Column(Integer, comment="Peak PPS during attack")
    peak_gbps = Column(Float, comment="Peak bandwidth in Gbps")
    duration_seconds = Column(Integer, comment="Attack duration")
    blocked_ips_count = Column(Integer, default=0, comment="Number of IPs blocked")
    detected_at = Column(DateTime, default=func.now(), nullable=False)
    mitigated = Column(Boolean, default=False, comment="Was attack successfully mitigated")
    mitigation_method = Column(String(100), comment="IP block, rate limit, etc.")

    # Relationships
    server = relationship("GameServer", backref="ddos_attacks")

    # Indexes
    __table_args__ = (
        Index("idx_ddos_server_detected", "server_id", "detected_at"),
        Index("idx_ddos_mitigated", "mitigated"),
    )


class IPBlockList(Base):
    """Blocked IP addresses for DDoS protection"""

    __tablename__ = "ip_block_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String(45), nullable=False, index=True, comment="IPv4 or IPv6 address")
    reason = Column(String(200), nullable=False, comment="Reason for blocking")
    blocked_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), comment="Admin who blocked"
    )
    blocked_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, comment="NULL = permanent block")
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    unblocked_at = Column(DateTime, comment="When IP was unblocked")
    server_id = Column(
        Integer,
        ForeignKey("game_servers.id", ondelete="CASCADE"),
        index=True,
        comment="Specific server or NULL for global",
    )
    auto_blocked = Column(Boolean, default=False, comment="Automatically blocked by DDoS detection")

    # Relationships
    blocked_by_user = relationship("User", backref="blocked_ips")
    server = relationship("GameServer", backref="blocked_ips")

    # Indexes
    __table_args__ = (
        Index("idx_ip_active", "ip_address", "is_active"),
        Index("idx_ip_expires", "expires_at"),
    )


# ==================== PLAYER MANAGEMENT SYSTEM ====================


class PlayerHistory(Base):
    """Player connection and activity history"""

    __tablename__ = "player_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(
        Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    steam_id = Column(String(32), nullable=False, index=True, comment="Steam ID")
    name = Column(String(100), nullable=False, comment="Player name at connection")
    ip_address = Column(String(45), comment="IP address")
    connected_at = Column(DateTime, default=func.now(), nullable=False)
    disconnected_at = Column(DateTime, comment="NULL if still connected")
    duration_seconds = Column(Integer, comment="Session duration")
    map_played = Column(String(64), comment="Map during session")
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    score = Column(Integer, default=0)

    # Relationships
    server = relationship("GameServer", backref="player_history")

    # Indexes
    __table_args__ = (
        Index("idx_player_steam", "steam_id", "server_id"),
        Index("idx_player_date", "connected_at"),
    )


class PlayerNote(Base):
    """Admin notes for players"""

    __tablename__ = "player_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(
        Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    steam_id = Column(String(32), nullable=False, index=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    server = relationship("GameServer", backref="player_notes")
    admin = relationship("User", backref="player_notes")

    # Indexes
    __table_args__ = (Index("idx_note_player", "steam_id", "server_id"),)


class PlayerTag(Base):
    """Tags/labels for players"""

    __tablename__ = "player_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(
        Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    steam_id = Column(String(32), nullable=False, index=True)
    tag = Column(String(50), nullable=False, comment="VIP, Skilled, Toxic, etc.")
    color = Column(String(7), default="#3b82f6", comment="Hex color")
    added_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    server = relationship("GameServer", backref="player_tags")
    admin = relationship("User", backref="player_tags")

    # Indexes
    __table_args__ = (
        Index("idx_tag_player", "steam_id", "server_id"),
        UniqueConstraint("server_id", "steam_id", "tag", name="uq_player_tag"),
    )


# ==================== SERVER TEMPLATE SYSTEM ====================


class ServerTemplate(Base):
    """Server configuration templates"""

    __tablename__ = "server_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="Template name")
    description = Column(Text, comment="Template description")
    game_type = Column(Enum(GameType), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_public = Column(Boolean, default=False, comment="Available to all users")
    is_official = Column(Boolean, default=False, comment="Official AGTR template")

    # Template data (JSON)
    config_data = Column(JSON, comment="server.cfg content")
    plugins = Column(JSON, comment="List of plugins to install")
    maps = Column(JSON, comment="Map list")
    cvars = Column(JSON, comment="Console variables")
    addons = Column(JSON, comment="Additional addons/mods")

    # Metadata
    use_count = Column(Integer, default=0, comment="Times used")
    rating = Column(Float, default=0.0, comment="Average rating")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", backref="server_templates")

    # Indexes
    __table_args__ = (
        Index("idx_template_game", "game_type", "is_public"),
        Index("idx_template_official", "is_official"),
    )


# ==================== ADMIN ACTIVITY TRACKING ====================


class AdminActivity(Base):
    """Real-time admin activity for collaborative mode"""

    __tablename__ = "admin_activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    server_id = Column(
        Integer, ForeignKey("game_servers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Activity details
    action_type = Column(
        String(50), nullable=False, comment="viewing_console, editing_config, etc."
    )
    current_tab = Column(String(50), comment="Active tab")
    details = Column(JSON, comment="Additional activity details")

    # Timestamps
    started_at = Column(DateTime, default=func.now(), nullable=False)
    last_active = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="admin_activities")
    server = relationship("GameServer", backref="admin_activities")

    # Indexes
    __table_args__ = (
        Index("idx_activity_server", "server_id", "last_active"),
        Index("idx_activity_user", "user_id", "server_id"),
    )


# ==================== ENUM VALIDATION EVENT LISTENERS ====================
# Register validators for critical enum columns to ensure data integrity

from sqlalchemy import event

# User model enum validators
event.listen(User.role, "set", create_enum_validator(UserRole, "User.role"), propagate=True)
event.listen(User.status, "set", create_enum_validator(UserStatus, "User.status"), propagate=True)

# GameServer model enum validators
event.listen(
    GameServer.game_type,
    "set",
    create_enum_validator(GameType, "GameServer.game_type"),
    propagate=True,
)
event.listen(
    GameServer.status,
    "set",
    create_enum_validator(ServerStatus, "GameServer.status"),
    propagate=True,
)

# Payment model enum validators
event.listen(
    Payment.method, "set", create_enum_validator(PaymentMethod, "Payment.method"), propagate=True
)
event.listen(
    Payment.status, "set", create_enum_validator(PaymentStatus, "Payment.status"), propagate=True
)

# ServerPackage model enum validator
event.listen(
    ServerPackage.game_type,
    "set",
    create_enum_validator(GameType, "ServerPackage.game_type"),
    propagate=True,
)

logger.debug("Enum validation event listeners registered")
