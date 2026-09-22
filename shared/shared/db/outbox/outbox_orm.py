import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import BaseORM
from shared.db.models import ReprMixin
from shared.db.types import created_at_type


class OutboxStatus(enum.Enum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class OutboxMessageORM(BaseORM, ReprMixin):
    __tablename__ = "outbox_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    exchange: Mapped[str] = mapped_column(String(255))

    routing_key: Mapped[str] = mapped_column(String(255))

    payload: Mapped[dict] = mapped_column(JSONB)

    status: Mapped[OutboxStatus] = mapped_column(
        Enum(OutboxStatus, name="outbox_status_enum"),
        default=OutboxStatus.PENDING,
    )

    created_at: Mapped[created_at_type]

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    retries: Mapped[int] = mapped_column(Integer, default=0)

    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_outbox_messages_status_created_at", "status", "created_at"),
    )
