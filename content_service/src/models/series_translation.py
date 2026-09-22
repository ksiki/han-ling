from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class SeriesTranslationORM(BaseORM, TimestampMixin):
    __tablename__ = "series_translations"
    __table_args__ = (
        {
            "comment": "Локализация метаданных книжных серий/циклов (переводы названий и описаний)"
        },
    )

    series_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("series.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на базовую серию",
    )

    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"),
        primary_key=True,
        comment="Язык перевода метаданных (только языки интерфейса)",
    )

    title: Mapped[str] = mapped_column(
        String(length=256), comment="Название серии на выбранном языке интерфейса"
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Описание серии на выбранном языке интерфейса"
    )
