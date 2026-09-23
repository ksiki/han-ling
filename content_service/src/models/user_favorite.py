import uuid

from shared.db.types import created_at_type
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class UserFavoriteORM(ContentServiceBaseORM):
    __tablename__ = "user_favorites"
    __table_args__ = (
        Index("ix_user_favorites_book_id", "book_id"),
        {"comment": "Книжная полка/избранное пользователя (связь Many-to-Many)"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на пользователя",
    )

    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на добавленную книгу",
    )

    created_at: Mapped[created_at_type] = mapped_column(
        comment="Дата добавления в избранное (для сортировки 'сначала недавние')"
    )
