from typing import Final

from pydantic import Field
from shared.settings import BaseConfig


class Config(BaseConfig):
    # ---------------------------------------------
    # Переопределяемые
    # ---------------------------------------------
    POSTGRES_DB: str = Field(
        alias="AUTH_SERVICE_POSTGRES_DB",
        default="auth_service_db",
    )
    RADIS_DB: str = Field(
        alias="AUTH_SERVICE_REDIS_DB",
        default="0",
    )

    # ---------------------------------------------
    # Токены
    # ---------------------------------------------
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_DAYS: int = 15

    # ---------------------------------------------
    # Капча
    # ---------------------------------------------
    CLOUDFLARE_SECRET_KEY: str
    CLOUDFLARE_VERIFY_URL: str = (
        "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    )

    # ---------------------------------------------
    # Сессии
    # ---------------------------------------------
    MAX_ACTIVE_SESSIONS: int = 2

    # ---------------------------------------------
    # OTP
    # ---------------------------------------------
    OTP_EXPIRE_MINUTES: int = 15


config: Final[Config] = Config()
