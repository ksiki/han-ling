import uuid

from shared.db.models import TimestampMixin
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class AuthorTranslationORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "author_translations"
    __table_args__ = (
        {"comment": "Локализация профиля автора (перевод имени и биографии)"},
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на базового автора",
    )

    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"),
        primary_key=True,
        comment="Язык перевода профиля",
    )

    name: Mapped[str] = mapped_column(
        String(length=256), comment="Локализованное имя автора"
    )

    bio: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Локализованная биография автора"
    )
