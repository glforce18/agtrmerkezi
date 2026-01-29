"""
AGTR Merkezi v5.0 - Ana Konfigurasyon Dosyasi
Tum sistem ayarlari
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Uygulama ayarlari"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # Uygulama bilgileri
    APP_NAME: str = "AGTR Merkezi"
    APP_VERSION: str = "5.1.0"
    APP_DESCRIPTION: str = "Half-Life & CS 1.6 Gaming Community Platform"
    DEBUG: bool = False
    # SECRET_KEY must be set in .env file - no default for security
    SECRET_KEY: str = ""

    # Default Admin Credentials - must be set in .env file
    DEFAULT_ADMIN_USERNAME: str = ""
    DEFAULT_ADMIN_EMAIL: str = ""
    DEFAULT_ADMIN_PASSWORD: str = ""

    # API Versiyonlama
    API_V1_PREFIX: str = "/api/v1"
    API_CURRENT_VERSION: str = "v1"

    # Domain ayarlari
    DOMAIN: str = "agtrmerkezi.com"
    BASE_URL: str = "http://127.0.0.1:8000"  # Backend URL
    FRONTEND_URL: str = "http://127.0.0.1:5173"  # Frontend URL (Vite dev server)

    @property
    def SITE_URL(self) -> str:
        """BASE_URL alias for compatibility"""
        return self.BASE_URL

    # Veritabani ayarlari - DB_PASSWORD must be set in .env
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "agtrmerkezi_user"
    DB_PASSWORD: str = ""  # Required: Set in .env file
    DB_NAME: str = "agtrmerkezi"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_RECYCLE: int = 3600

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    # Redis ayarlari
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""  # Optional: Set in .env file if Redis requires authentication
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 20

    # WebSocket ayarlari
    WS_MAX_CONNECTIONS: int = 100

    # Game server ayarlari
    GAME_SERVER_IPS: List[str] = [
        "185.171.25.137",
        "185.171.25.138",
        "185.171.25.139",
        "185.171.25.140",
    ]
    MAIN_SERVER_IP: str = "185.171.25.137"
    GAME_PORT_START: int = 27018
    GAME_PORT_END: int = 27050
    PORTS_PER_IP: int = 33  # 27018-27050 = 33 ports per IP

    # Paths
    HLDS_PATH: str = "/home/gameservers"
    REHLDS_PATH: str = "/home/gameservers/rehlds"

    # Varsayilan fiyatlar
    PRICE_PER_SLOT: float = 5.0
    DISCOUNT_3_MONTH: float = 0.10
    DISCOUNT_6_MONTH: float = 0.15
    DISCOUNT_12_MONTH: float = 0.25

    # Ek ozellik fiyatlari
    PRICE_ANTICHEAT: float = 20.0
    PRICE_CUSTOM_DOMAIN: float = 10.0
    PRICE_PRIORITY_SUPPORT: float = 15.0
    PRICE_AUTO_BACKUP: float = 5.0
    PRICE_AMVP_PLUGIN: float = 25.0

    # Bakiye limitleri
    BALANCE_MIN_AMOUNT: float = 10.0  # Minimum yukleme tutari
    BALANCE_MAX_AMOUNT: float = 10000.0  # Maksimum yukleme tutari
    ARMOR_RATE: int = 100  # Armor exchange rate

    # Guvenlik ayarlari
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 gun
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_MIN_LENGTH: int = 6
    PASSWORD_REQUIRE_UPPERCASE: bool = False
    PASSWORD_REQUIRE_LOWERCASE: bool = False
    PASSWORD_REQUIRE_DIGIT: bool = False
    PASSWORD_REQUIRE_SPECIAL: bool = False

    # Session ayarlari
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"
    SESSION_MAX_AGE: int = 86400  # 1 gun

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_SECOND: int = 10
    RATE_LIMIT_ENABLED: bool = True

    # Login/Brute Force Korumasi
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    # 2FA Ayarlari
    TWO_FACTOR_ENABLED: bool = True
    TWO_FACTOR_ISSUER: str = "AGTR Merkezi"
    TWO_FACTOR_REQUIRED_FOR_ADMIN: bool = False
    TWO_FACTOR_BACKUP_CODES_COUNT: int = 10

    # OAuth Ayarlari
    STEAM_API_KEY: str = ""
    STEAM_REALM: str = "https://agtrmerkezi.com"
    DISCORD_CLIENT_ID: str = ""
    DISCORD_CLIENT_SECRET: str = ""
    DISCORD_REDIRECT_URI: str = "https://agtrmerkezi.com/api/social/discord/callback"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_STATE_EXPIRE_MINUTES: int = 10

    # Email Ayarlari
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@agtrmerkezi.com"
    SMTP_FROM_NAME: str = "AGTR Merkezi"
    SMTP_TLS: bool = True
    EMAIL_ENABLED: bool = False

    # Discord Webhook
    DISCORD_WEBHOOK_URL: str = ""
    DISCORD_WEBHOOK_ENABLED: bool = False

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    TELEGRAM_ENABLED: bool = False

    # Scraper API Keys
    STEAMGRIDDB_API_KEY: str = ""  # https://www.steamgriddb.com/profile/preferences/api

    # Forum ayarlari
    FORUM_POSTS_PER_PAGE: int = 20
    FORUM_TOPICS_PER_PAGE: int = 25
    FORUM_MIN_POST_LENGTH: int = 10
    FORUM_MAX_POST_LENGTH: int = 50000

    # Upload ayarlari
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "zip", "rar", "cfg", "txt"]
    UPLOAD_PATH: str = "/var/www/agtrmerkezi/uploads"

    # Banka hesaplari
    BANK_ACCOUNTS: List[dict] = [
        {
            "bank": "Ziraat Bankasi",
            "iban": "TR00 0000 0000 0000 0000 0000 00",
            "holder": "AGTR Merkezi",
        },
        {
            "bank": "Garanti BBVA",
            "iban": "TR00 0000 0000 0000 0000 0000 00",
            "holder": "AGTR Merkezi",
        },
    ]


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
