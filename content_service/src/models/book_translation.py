from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ARRAY, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class BookTranslationORM(BaseORM, TimestampMixin):
    __tablename__ = "book_translations"

    book_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"), primary_key=True
    )
    localized_title: Mapped[str] = mapped_column(String(length=256))
    alternative_titles: Mapped[list[str]] = mapped_column(ARRAY(String(length=256)))
    description: Mapped[str] = mapped_column(String(length=1024))
