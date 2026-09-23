import uuid

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class EditionChapterORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "edition_chapters"
    __table_args__ = (
        Index("ix_edition_chapters_edition_sort", "edition_id", "sort_order"),
        Index("ix_edition_chapters_parent_id", "parent_id"),
        {
            "comment": "Иерархическое оглавление издания книги (дерево частей, томов и глав)"
        },
    )

    id: Mapped[uuid_pk] = mapped_column(
        comment="Уникальный идентификатор пункта оглавления (выступает единой точкой истины для связей)"
    )

    edition_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("book_editions.id", ondelete="CASCADE"),
        comment="Ссылка на конкретную версию (издание)",
    )

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("edition_chapters.id", ondelete="CASCADE"),
        nullable=True,
        comment="Ссылка на родителя для вложенности (например, Том -> Глава). NULL для корня",
    )

    title: Mapped[str] = mapped_column(
        String(length=256),
        comment="Название главы или части на языке данного издания ('Глава 1', 'Эпилог')",
    )

    display_number: Mapped[str | None] = mapped_column(
        String(length=16),
        nullable=True,
        comment="Опциональный визуальный номер для фронтенда ('1', '1.2', 'VII')",
    )

    sort_order: Mapped[int] = mapped_column(
        Integer, comment="Порядок отображения пункта в меню оглавления (1, 2, 3...)"
    )
