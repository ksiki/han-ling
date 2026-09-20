from pathlib import Path
from typing import Final

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent.parent


class BaseConfig(BaseSettings):
    # ---------------------------------------------
    # Общие значения
    # ---------------------------------------------
    DEBUG: bool = True
    PRODUCT_NAME: str = "HanLIng"  # TODO: поменять имя
    DOMAIN: str = "hanling.local"  # TODO: поменять домен

    # ---------------------------------------------
    # Безопастность
    # ---------------------------------------------
    SECRET_KEY: str = "localhost_secret_key"
    ALGORITHM: str = "HS256"

    # ---------------------------------------------
    # EMAIL
    # ---------------------------------------------
    RESEND_URL: str = "https://api.resend.com/emails"
    RESEND_API_KEY: str = "resend_api_key"

    # ---------------------------------------------
    # OpenTelemetry & Centry
    # --------------------------------------------
    OTLP_ENDPOINT: str = "http://alloy:4317"
    SENTRY_DSN: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.05

    # ---------------------------------------------
    # Базовые переменные для подключения
    # ---------------------------------------------
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "admin"
    POSTGRES_DB: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DRIVER: str = "asyncpg"

    REDIS_HOST: str = "redis"
    REDIS_PORT: str = "6379"
    REDIS_DB: str = "1"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+{self.POSTGRES_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @computed_field
    @property
    def ENVIRONMENT(self) -> str:
        return "development" if self.DEBUG else "production"

    @computed_field
    @property
    def SENDER_EMAIL(self) -> str:
        return f"noreply@{self.DOMAIN}"

    @computed_field
    @property
    def FRONTEND_URLS(self) -> list[str]:
        return [
            f"http://{self.DOMAIN}",
            f"https://{self.DOMAIN}",
        ]

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "deploy" / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )
