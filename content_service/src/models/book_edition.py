import uuid

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class BookEditionORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "book_editions"
    __table_args__ = (
        UniqueConstraint(
            "book_id",
            "language_code",
            "vocabulary_level_id",
            name="uq_book_id_language_code_vocabulary_level_id",
        ),
        Index("ix_book_editions_book_id", "book_id"),
        {
            "comment": "Конкретные издания/версии текста книги с учетом языка и уровня лексики"
        },
    )

    id: Mapped[uuid_pk] = mapped_column(
        comment="Уникальный идентификатор конкретного издания/версии текста"
    )

    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        comment="Ссылка на родительскую книгу",
    )

    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"),
        comment="Язык текста самого издания",
    )

    vocabulary_level_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vocabulary_levels.id", ondelete="SET NULL"),
        nullable=True,
        comment="Ссылка на конкретный уровень лексики, учитывающий язык",
    )

    pages_count: Mapped[int | None] = mapped_column(
        nullable=True, comment="Количество страниц в данном издании"
    )

    chapters_count: Mapped[int | None] = mapped_column(
        nullable=True, comment="Количество глав в данном издании"
    )
