from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class BookContentORM(BaseORM, TimestampMixin):
    __tablename__ = "book_contents"

    id: Mapped[uuid_pk]
    chapter_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("edition_chapters.id", ondelete="CASCADE"), unique=True
    )

    content: Mapped  # TODO: JSONB
