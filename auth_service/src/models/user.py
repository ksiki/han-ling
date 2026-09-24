import datetime
import secrets

from shared.db.types import uuid_pk
from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import AuthServiceBaseORM
from .types.types import user_role


def _generate_default_nickname() -> str:
    return f"user_{secrets.token_urlsafe(6)}"


class UserORM(AuthServiceBaseORM):
    __tablename__ = "users"

    id: Mapped[uuid_pk]

    email: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        comment="Уникальный адрес электронной почты пользователя",
    )
    password_hash: Mapped[str | None] = mapped_column(
        String(length=255),
        nullable=True,
        comment="Хеш пароля (может отсутствовать при входе через OAuth)",
    )

    nickname: Mapped[str] = mapped_column(
        String(length=25),
        default=_generate_default_nickname,
        unique=True,
        comment="Публичный никнейм пользователя",
    )
    role: Mapped[user_role]

    is_active: Mapped[bool] = mapped_column(
        server_default="true",
        default=True,
        comment="Флаг активности учетной записи",
    )

    is_deleted: Mapped[bool] = mapped_column(
        server_default="false",
        default=False,
        comment="Флаг мягкого удаления (soft delete)",
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=None,
        default=None,
        comment="Временная метка soft delete",
    )

    # TODO: добавить настройки сайта
    # site_settings JSONB NOT NULL DEFAULT '{}'::jsonb,

    __table_args__ = (
        CheckConstraint(
            "nickname ~ '^[a-zA-Z0-9_ .-]+$'",
            name="check_nickname_format",
        ),
        {"comment": "Таблица учетных записей пользователей"},
    )

    @property
    def is_valid(self) -> bool:
        """Проверяет, активна ли учетная запись и не помечена ли она как удаленная."""
        return self.is_active and not self.is_deleted
