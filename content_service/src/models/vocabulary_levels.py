from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class VocabularyLevelORM(BaseORM, TimestampMixin):
    __tablename__ = "vocabulary_levels"

    id: Mapped[uuid_pk]
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="CASCADE"), primary_key=True
    )
    level_code: Mapped[str] = mapped_column(String(length=8))
    description: Mapped[str] = mapped_column(String(length=32))
    sort_order: Mapped[int]

    __table_args__ = (
        UniqueConstraint(
            "language_code", "level_code", name="uq_vocabulary_level_lang_level"
        ),
    )
