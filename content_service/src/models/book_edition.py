from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class BookEditionORM(BaseORM, TimestampMixin):
    __tablename__ = "book_editions"

    id: Mapped[uuid_pk]
    book_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
    )
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT")
    )
    vocabulary_level_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("vocabulary_levels.id", ondelete="SET NULL")
    )
    pages_count: Mapped[int]
    chapters_count: Mapped[int]

    __table_args__ = (
        UniqueConstraint(
            "book_id",
            "language_code",
            "vocabulary_level_id",
            name="uq_book_id_language_code_vocabulary_level_id",
        ),
    )
