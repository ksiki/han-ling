from typing import Final

from pydantic import Field
from shared.settings import BaseConfig


class Config(BaseConfig):
    # ---------------------------------------------
    # Переопределяемые
    # ---------------------------------------------
    POSTGRES_DB: str = Field(
        alias="CONTENT_SERVICE_POSTGRES_DB",
        default="content_service_db",
    )


config: Final[Config] = Config()
