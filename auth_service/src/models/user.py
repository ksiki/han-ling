import datetime
import enum
import secrets

from shared.db.types import uuid_pk
from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_orm import BaseORM


def _generate_default_nickname() -> str:
    return f"user_{secrets.token_urlsafe(6)}"


class RoleEnum(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserORM(BaseORM):
    __tablename__ = "users"

    id: Mapped[uuid_pk]

    email: Mapped[str] = mapped_column(String(length=255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(length=255), nullable=True)

    nickname: Mapped[str] = mapped_column(
        String(length=25), default=_generate_default_nickname, unique=True
    )
    role: Mapped[RoleEnum] = mapped_column(
        ENUM(
            RoleEnum,
            name="role_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        server_default=RoleEnum.USER.value,
        default=RoleEnum.USER,
    )

    is_active: Mapped[bool] = mapped_column(server_default="true", default=True)

    is_deleted: Mapped[bool] = mapped_column(server_default="false", default=False)
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=None, default=None
    )

    __table_args__ = (
        CheckConstraint(
            "nickname ~ '^[a-zA-Z0-9_ .-]+$'",
            name="check_nickname_format",
        ),
    )

    @property
    def is_valid(self) -> bool:
        """Проверяет, активна ли учетная запись и не помечена ли она как удаленная.

        Returns:
            bool: True, если пользователь активен и не удален, иначе False.
        """
        return self.is_active and not self.is_deleted
