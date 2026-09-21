from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class AuthorTranslationORM(BaseORM, TimestampMixin):
    __tablename__ = "author_translations"

    author_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True
    )
    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"), primary_key=True
    )
    name: Mapped[str] = mapped_column[String(length=256)]
    bio: Mapped[str] = mapped_column[String(length=2048)]
