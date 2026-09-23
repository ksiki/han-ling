import uuid

from shared.db.models import TimestampMixin
from sqlalchemy import ARRAY, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class BookTranslationORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "book_translations"
    __table_args__ = (
        Index(
            "ix_book_translations_alt_titles_gin",
            "alternative_titles",
            postgresql_using="gin",
        ),
        {
            "comment": "Локализация метаданных книги (название, описание, альтернативные названия для поиска)"
        },
    )

    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на базовую книгу",
    )

    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"),
        primary_key=True,
        comment="Язык локализации интерфейса",
    )

    localized_title: Mapped[str] = mapped_column(
        String(length=256), comment="Название книги для текущего языка интерфейса"
    )

    alternative_titles: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(length=256)),
        nullable=True,
        comment="Массив альтернативных названий для улучшения глобального поиска",
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Синопсис/аннотация на языке интерфейса"
    )
