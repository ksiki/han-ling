from decimal import Decimal

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class BookORM(BaseORM, TimestampMixin):
    __tablename__ = "books"

    id: Mapped[uuid_pk]

    original_title: Mapped[str] = mapped_column(String(length=128))
    country_origin: Mapped[str] = mapped_column(String(length=3))

    publisher: Mapped[str] = mapped_column(String(length=256))
    is_adult_content: Mapped[str] = mapped_column(server_default="false", default=False)

    external_rating: Mapped[Decimal] = mapped_column(Numeric(precision=3, scale=2))

    poster_url: Mapped[str] = mapped_column(String(length=256))

    series_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("series.id", ondelete="SET NULL")
    )
    series_order: Mapped[int]

    access_model: Mapped[str] = mapped_column(
        String(length=8), server_default="freemium", default="freemium"
    )
    free_chapters_count: Mapped[int] = mapped_column(
        SmallInteger, server_default=0, default=0
    )

    __table_args__ = (
        CheckConstraint(
            "access_model IN ('free', 'premium', 'freemium')",
            name="chk_books_access_model_value",
        ),
        CheckConstraint(
            "free_chapters_count > 0",
            name="chk_books_free_chapters_count_value",
        ),
    )
