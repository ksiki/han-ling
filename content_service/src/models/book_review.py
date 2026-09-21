from shared.db.types import created_at_type, uuid_pk
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class BookReviewORM(BaseORM):
    __tablename__ = "book_reviews"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    book_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
    )

    rating: Mapped[int] = mapped_column(SmallInteger)
    review_text: Mapped[str] = mapped_column(String(length=4096))

    created_at: Mapped[created_at_type]

    __table_args__ = (
        CheckConstraint(
            "rating > -1 and rating < 6",
            name="chk_book_reviews_rating_value",
        ),
        UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_user_id_book_id",
        ),
        Index(
            "idx_book_reviews_book_id_rating",
            "book_id",
            "rating",
        ),
    )
