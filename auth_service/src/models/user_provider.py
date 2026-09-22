from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base.base_orm import BaseORM

from .types.types import provider_type


class UserProviderORM(BaseORM):
    __tablename__ = "user_providers"

    id: Mapped[uuid_pk]

    user_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        comment="Идентификатор пользователя-владельца провайдера",
    )

    provider: Mapped[provider_type]
    provider_id: Mapped[str] = mapped_column(
        String(length=255),
        comment="Уникальный идентификатор пользователя внутри сервиса провайдера",
    )

    __table_args__ = (
        Index("ix_user_providers_user_id", "user_id"),
        UniqueConstraint(
            "provider",
            "provider_id",
            name="uq_user_providers_provider_provider_id",
        ),
        {"comment": "Связи аккаунтов пользователей с внешними OAuth-провайдерами"},
    )
