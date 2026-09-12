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
    # Безопастность
    # ---------------------------------------------
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


config: Final[Config] = Config()
