from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class SeriesTranslationORM(BaseORM, TimestampMixin):
    __tablename__ = "series_translations"

    series_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("series.id", ondelete="CASCADE"), primary_key=True
    )
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"), primary_key=True
    )
    title: Mapped[str] = mapped_column(String(length=256))
    description: Mapped[str] = mapped_column(String(length=1024))
