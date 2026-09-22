import datetime

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.types.types import user_role

from .base import BaseORM


class UserORM(BaseORM, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        {
            "comment": "Локальная изолированная копия профилей пользователей для Core Content Service"
        },
    )

    id: Mapped[uuid_pk] = mapped_column(
        comment="Уникальный идентификатор пользователя (локальная изолированная копия для сервиса контента)"
    )

    nickname: Mapped[str] = mapped_column(
        String(length=25), comment="Отображаемое имя пользователя на платформе"
    )

    role: Mapped[user_role] = mapped_column(
        comment="Уровень прав доступа пользователя (user / admin)"
    )

    subscribe_exp: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=None,
        default=None,
        comment="Время окончания премиум-подписки (обновляется асинхронно через брокер сообщений Redis)",
    )

    @property
    def is_subscriber(self) -> bool:
        return (
            self.subscribe_exp is not None
            and self.subscribe_exp > datetime.datetime.now(datetime.UTC)
        )
