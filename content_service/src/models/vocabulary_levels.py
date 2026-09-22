from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class VocabularyLevelORM(BaseORM, TimestampMixin):
    __tablename__ = "vocabulary_levels"
    __table_args__ = (
        UniqueConstraint(
            "language_code", "level_code", name="uq_vocabulary_level_lang_level"
        ),
        Index("ix_vocabulary_levels_lang_sort", "language_code", "sort_order"),
        {
            "comment": "Справочник уровней сложности лексики (HSK, CEFR) с привязкой к языку"
        },
    )

    id: Mapped[uuid_pk] = mapped_column(
        comment="Уникальный идентификатор уровня сложности"
    )

    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="CASCADE"),
        comment="Жесткая привязка уровня к конкретному языку",
    )

    level_code: Mapped[str] = mapped_column(
        String(length=12), comment="Значение уровня (например, 'A1', 'HSK4')"
    )

    description: Mapped[str | None] = mapped_column(
        String(length=64),
        nullable=True,
        comment="Расшифровка уровня (например, 'Beginner', 'Upper-Intermediate')",
    )

    sort_order: Mapped[int] = mapped_column(
        comment="Вес уровня для правильной логической сортировки фильтров от простого к сложному"
    )
