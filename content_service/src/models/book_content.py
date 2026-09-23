import uuid

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class BookContentORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "book_contents"
    __table_args__ = (
        Index("ix_book_contents_content_gin", "content", postgresql_using="gin"),
        {
            "comment": "Структурированный контент глав (токены слов, предложения, медиа-блоки)"
        },
    )

    id: Mapped[uuid_pk] = mapped_column(
        comment="Уникальный идентификатор блока контента"
    )

    chapter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("edition_chapters.id", ondelete="CASCADE"),
        unique=True,
        comment="Жесткая связь с конкретным пунктом оглавления (один документ на главу)",
    )

    content: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Структурированный текст главы (иерархия блоков, предложений и токенов)",
    )
