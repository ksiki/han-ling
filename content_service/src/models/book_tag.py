from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class BookTagORM(BaseORM):
    __tablename__ = "book_tags"
    __table_args__ = (
        Index("ix_book_tags_tag_id", "tag_id"),
        {"comment": "Связующая таблица книг и тегов/жанров (Many-to-Many)"},
    )

    book_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на книгу",
    )

    tag_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на тег",
    )
