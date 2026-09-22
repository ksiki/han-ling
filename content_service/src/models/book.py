import uuid
from decimal import Decimal

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM
from .types.types import book_processing_status, book_publication_status


class BookORM(BaseORM, TimestampMixin):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint(
            "access_model IN ('free', 'premium', 'freemium')",
            name="chk_books_access_model_value",
        ),
        CheckConstraint(
            "free_chapters_count >= 0",
            name="chk_books_free_chapters_count_value",
        ),
        CheckConstraint(
            "release_year >= 1000 AND release_year <= 2100",
            name="chk_books_release_year_range",
        ),
        Index("ix_books_series_id", "series_id"),
        Index("ix_books_publication_status", "publication_status"),
        Index("ix_books_processing_status", "processing_status"),
        {"comment": "Основная таблица книг/манги с универсальными метаданными"},
    )

    id: Mapped[uuid_pk] = mapped_column(comment="Уникальный идентификатор книги/манги")

    original_title: Mapped[str] = mapped_column(
        String(length=128), comment="Исходное название на языке оригинала"
    )
    country_origin: Mapped[str | None] = mapped_column(
        String(length=3),
        nullable=True,
        comment="ISO-код страны происхождения оригинала (например, 'CHN', 'RUS')",
    )

    publisher: Mapped[str | None] = mapped_column(
        String(length=256), nullable=True, comment="Название оригинального издательства"
    )
    release_year: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
        comment="Год оригинального выпуска/публикации произведения",
    )

    is_adult_content: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
        default=False,
        comment="Флаг наличия контента 18+",
    )

    external_rating: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=3, scale=2),
        nullable=True,
        comment="Средний рейтинг из внешних источников",
    )

    poster_url: Mapped[str | None] = mapped_column(
        String(length=256),
        nullable=True,
        comment="URL-ссылка на вертикальный постер высокого качества в S3",
    )

    banner_url: Mapped[str | None] = mapped_column(
        String(length=256),
        nullable=True,
        comment="URL-ссылка на горизонтальный баннер высокого качества в S3",
    )

    series_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("series.id", ondelete="SET NULL"),
        nullable=True,
        comment="Ссылка на серию (если книга является частью цикла)",
    )
    series_order: Mapped[int | None] = mapped_column(
        nullable=True, comment="Порядковый номер книги внутри серии"
    )

    access_model: Mapped[str] = mapped_column(
        String(length=8),
        server_default="freemium",
        default="freemium",
        comment="Модель доступа (бесплатно, только подписка, гибрид)",
    )
    free_chapters_count: Mapped[int] = mapped_column(
        SmallInteger,
        server_default=text("0"),
        default=0,
        comment="Количество бесплатных глав для модели 'freemium' (например, первые 5)",
    )

    processing_status: Mapped[book_processing_status]
    publication_status: Mapped[book_publication_status]
    processing_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Текст ошибки при неудачной фоновой обработке книги",
    )
