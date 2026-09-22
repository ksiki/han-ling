import uuid

from shared.db.types import created_at_type, uuid_pk
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    SmallInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class BookReviewORM(BaseORM):
    __tablename__ = "book_reviews"
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="chk_book_reviews_rating_range",
        ),
        UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_book_reviews_user_book",
        ),
        Index(
            "idx_book_reviews_book_id_rating",
            "book_id",
            "rating",
        ),
        Index(
            "ix_book_reviews_book_id_created_at",
            "book_id",
            "created_at",
        ),
        {"comment": "Отзывы и пользовательские оценки книг платформы"},
    )

    id: Mapped[uuid_pk] = mapped_column(comment="Уникальный идентификатор отзыва")

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Автор отзыва"
    )

    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        comment="Книга, на которую оставлен отзыв",
    )

    rating: Mapped[int] = mapped_column(
        SmallInteger, comment="Внутренняя оценка пользователя (от 1 до 5 звезд)"
    )

    review_text: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Текстовое содержимое рецензии"
    )

    created_at: Mapped[created_at_type] = mapped_column(
        comment="Дата и время публикации отзыва"
    )
