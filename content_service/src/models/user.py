import datetime

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.types.types import user_role

from .base import BaseORM


class UserORM(BaseORM, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid_pk]

    nickname: Mapped[str] = mapped_column(
        String(length=25),
    )
    role: Mapped[user_role]
    subscribe_exp: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=None, default=None
    )

    @property
    def is_subscriber(self) -> bool:
        return (
            self.subscribe_exp is not None
            and self.subscribe_exp > datetime.datetime.now(datetime.UTC)
        )
