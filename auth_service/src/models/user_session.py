import datetime

from shared.db.types import uuid_pk
from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import AuthServiceBaseORM


class UserSessionORM(AuthServiceBaseORM):
    __tablename__ = "user_sessions"

    id: Mapped[uuid_pk]

    user_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        comment="Идентификатор пользователя, которому принадлежит сессия",
    )

    refresh_token_jti: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        comment="Уникальный JWT ID (JTI) refresh-токена",
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(length=512),
        nullable=True,
        server_default=None,
        default=None,
        comment="User-Agent клиентского устройства",
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(length=45),
        nullable=True,
        server_default=None,
        default=None,
        comment="IP-адрес клиента (IPv4 или IPv6)",
    )

    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        comment="Временная метка истечения срока действия сессии",
    )

    is_revoked: Mapped[bool] = mapped_column(
        server_default="false",
        default=False,
        comment="Флаг принудительного отзыва сессии",
    )
    revoked_reason: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        server_default=None,
        default=None,
        comment="Причина отзыва сессии",
    )
    revoked_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=None,
        default=None,
        comment="Временная метка отзыва сессии",
    )

    __table_args__ = (
        Index("ix_user_sessions_user_id", "user_id"),
        Index("ix_user_sessions_expires_at", "expires_at"),
        {"comment": "Активные и архивные сессии пользователей (Refresh токены)"},
    )

    def revoke(self, reason: str, revoked_at: datetime.datetime | None = None) -> None:
        """Озывает текущую сессию с указанием причины и времени отзыва."""
        self.is_revoked = True
        self.revoked_reason = reason
        self.revoked_at = (
            revoked_at if revoked_at else datetime.datetime.now(datetime.UTC)
        )

    @property
    def is_active(self) -> bool:
        """Проверяет активность сессии по статусу отзыва и сроку действия."""
        return not self.is_revoked and self.expires_at > datetime.datetime.now(
            datetime.UTC
        )
