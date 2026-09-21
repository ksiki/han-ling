from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class BookAlignmentORM(BaseORM, TimestampMixin):
    __tablename__ = "book_alignments"

    id: Mapped[uuid_pk]
    source_chapter_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("edition_chapters.id", ondelete="CASCADE")
    )
    target_chapter_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("edition_chapters.id", ondelete="CASCADE")
    )

    alignment_map: Mapped  # TODO: JSONB

    __table_args__ = (
        UniqueConstraint(
            "source_chapter_id",
            "target_chapter_id",
            name="uq_source_edition_id_target_edition_id",
        ),
    )
