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
    FRONTEND_URLS: list[str] = ["http://hanling.local", "https://hanling.local"]

    # ---------------------------------------------
    # Безопастность
    # ---------------------------------------------
    SECRET_KEY: str = "localhost_secret_key"
    ALGORITHM: str = "HS256"

    # ---------------------------------------------
    # Базовые переменные для подключения
    # ---------------------------------------------
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "database"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DRIVER: str = "asyncpg"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: str = "6379"
    REDIS_DB: str = "0"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+{self.POSTGRES_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "deploy" / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )
