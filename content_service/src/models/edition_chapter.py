from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class EditionChapterORM(BaseORM, TimestampMixin):
    __tablename__ = "edition_chapters"

    id: Mapped[uuid_pk]
    edition_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("book_editions.id", ondelete="CASCADE")
    )
    parent_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("edition_chapters.id", ondelete="CASCADE"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(length=256))
    display_number: Mapped[str] = mapped_column(String(length=16))

    sort_order: Mapped[int]
