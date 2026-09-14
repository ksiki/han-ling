import enum

from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_orm import BaseORM


class ProviderEnum(enum.Enum):
    GOOGLE = "GOOGLE"


class UserProviderORM(BaseORM):
    __tablename__ = "user_providers"

    id: Mapped[uuid_pk]

    user_id: Mapped[uuid_pk] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    provider: Mapped[ProviderEnum]
    provider_id: Mapped[str] = mapped_column(String(length=255), unique=True)
