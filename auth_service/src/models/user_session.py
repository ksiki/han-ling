import datetime

from shared.db.types import uuid_pk
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_orm import BaseORM


class UserSessionORM(BaseORM):
    __tablename__ = "user_sessions"

    id: Mapped[uuid_pk]

    user_id: Mapped[uuid_pk] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    refresh_token_jti: Mapped[str] = mapped_column(
        String(length=255), index=True, unique=True
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(length=512), nullable=True, server_default=None, default=None
    )
    ip_address: Mapped[str] = mapped_column(
        String(length=45), nullable=True, server_default=None, default=None
    )

    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    is_revoked: Mapped[bool] = mapped_column(server_default="false", default=False)
    revoked_reason: Mapped[str] = mapped_column(
        String(512), nullable=True, server_default=None, default=None
    )
    revoked_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=None, default=None
    )

    def revoke(self, reason: str, revoked_at: datetime.datetime | None = None) -> None:
        self.is_revoked = True
        self.revoked_reason = reason
        self.revoked_at = (
            revoked_at if revoked_at else datetime.datetime.now(datetime.UTC)
        )

    @property
    def is_active(self) -> bool:
        return not self.is_revoked and self.expires_at > datetime.datetime.now(
            datetime.UTC
        )
