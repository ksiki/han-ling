import uuid

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM
from .types.types import book_creator_role


class BookCreatorORM(BaseORM):
    __tablename__ = "book_creators"
    __table_args__ = (
        Index("ix_book_creators_author_id", "author_id"),
        {
            "comment": "Связующая таблица создателей книги с указанием их роли (Many-to-Many)"
        },
    )

    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на книгу",
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на создателя",
    )

    role: Mapped[book_creator_role] = mapped_column(
        primary_key=True,
        comment="Роль создателя в этой книге (writer, illustrator, translator)",
    )
