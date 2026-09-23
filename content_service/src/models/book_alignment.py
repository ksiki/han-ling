import uuid

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class BookAlignmentORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "book_alignments"
    __table_args__ = (
        UniqueConstraint(
            "source_chapter_id",
            "target_chapter_id",
            name="uq_book_alignments_source_target_chapter",
        ),
        Index("ix_book_alignments_map_gin", "alignment_map", postgresql_using="gin"),
        Index("ix_book_alignments_target_chapter_id", "target_chapter_id"),
        {
            "comment": "Карты выравнивания предложений (N-to-M) между главами оригинала и перевода для субтитров"
        },
    )

    id: Mapped[uuid_pk] = mapped_column(
        comment="Уникальный идентификатор карты выравнивания"
    )

    source_chapter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("edition_chapters.id", ondelete="CASCADE"),
        comment="Ссылка на конкретную главу оригинала",
    )

    target_chapter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("edition_chapters.id", ondelete="CASCADE"),
        comment="Ссылка на конкретную главу перевода (субтитров)",
    )

    alignment_map: Mapped[list[dict]] = mapped_column(
        JSONB, nullable=False, comment="JSON-карта связей предложений N-to-M"
    )
