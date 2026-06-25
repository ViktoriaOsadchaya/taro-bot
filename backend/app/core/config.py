import logging
import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# Загружаем конфигурацию из .env
load_dotenv()


class DbSettings(BaseModel):
    url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/taro_bot",
    )
    echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"


class Setting(BaseSettings):
    db: DbSettings = DbSettings()
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    INSTANCE_ID: str = os.getenv("INSTANCE_ID", "default")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    # Режим запуска: "dev" (по умолчанию, polling) или "prod" (webhook)
    BOT_ENV: str = os.getenv("BOT_ENV", "dev").lower()
    
    # Настройки Webhook
    WEBHOOK_HOST: str = os.getenv("WEBHOOK_HOST", "https://oraro.ru")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/webhook")
    WEBHOOK_IP: str = os.getenv("WEBHOOK_IP", "")

    
    # Настройки внутреннего сервера (aiogram) для вебхуков
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

    @property
    def WEBHOOK_URL(self) -> str:
        """Полный URL для Telegram Webhook"""
        return f"{self.WEBHOOK_HOST.rstrip('/')}{self.WEBHOOK_PATH}"
    
    @property
    def FRONTEND_MAP_URL(self) -> str:
        """URL для WebApp с картой"""
        return f"{self.FRONTEND_URL}/map" if self.FRONTEND_URL else ""
    
    @property
    def FRONTEND_CHAT_URL(self) -> str:
        """URL для WebApp с конкретным чатом (переписка)"""
        return f"{self.FRONTEND_URL}/chat" if self.FRONTEND_URL else ""
    
    @property
    def FRONTEND_CHATS_LIST_URL(self) -> str:
        """URL для WebApp со списком чатов"""
        return f"{self.FRONTEND_URL}/chat/chats" if self.FRONTEND_URL else ""

    class RedisSettings(BaseModel):
        url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        decode_responses: bool = True  # Автоматическая декодировка строк
        socket_connect_timeout: int = int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))
        socket_timeout: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
        retry_on_timeout: bool = True
        health_check_interval: int = int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30"))

    redis: RedisSettings = RedisSettings()

    class EmailSettings(BaseModel):
        """Настройки отправки писем"""
        host: str = os.getenv("SMTP_HOST", "localhost")
        port: int = int(os.getenv("SMTP_PORT", "465"))
        username: str = os.getenv("SMTP_USERNAME", "")
        password: str = os.getenv("SMTP_PASSWORD", "")
        from_email: str = os.getenv("SMTP_FROM_EMAIL", "")
        use_tls: bool = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
        email_confirm_base_url: str = os.getenv("EMAIL_CONFIRM_BASE_URL", "http://localhost:3000/confirm-email")
        test_email_to: Optional[str] = os.getenv("TEST_EMAIL_TO")

    email: EmailSettings = EmailSettings()

    class LLMSettings(BaseModel):
        api_url: str = Field(
            default_factory=lambda: os.getenv("LLM_API_URL")
            or os.getenv("PROXYAPI_BASE_URL", "")
        )
        api_key: str = Field(
            default_factory=lambda: os.getenv("LLM_API_KEY")
            or os.getenv("PROXYAPI_API_KEY", "")
        )
        model: str = Field(
            default_factory=lambda: os.getenv("LLM_MODEL")
            or os.getenv("PROXYAPI_MODEL", "gpt-4o-mini")
        )
        timeout: int = int(os.getenv("NEURAL_API_TIMEOUT", "30"))
        retry_count: int = int(os.getenv("NEURAL_API_RETRY_COUNT", "2"))
        retry_delay: float = float(os.getenv("NEURAL_API_RETRY_DELAY", "1.0"))
        step1_debug_enabled: bool = (
            os.getenv("LLM_STEP1_DEBUG_ENABLED", "false").lower() == "true"
        )

        @property
        def is_configured(self) -> bool:
            return bool(self.api_url and self.api_key and self.model)

    llm: LLMSettings = LLMSettings()


settings = Setting()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logging.getLogger("watchfiles").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
