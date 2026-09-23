import uuid

from shared.db.models import TimestampMixin
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class CharacterTranslationORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "character_translations"
    __table_args__ = (
        {"comment": "Локализация данных персонажа (перевод имени и истории/биографии)"},
    )

    character_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на персонажа",
    )

    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"),
        primary_key=True,
        comment="Язык профиля персонажа",
    )

    name: Mapped[str] = mapped_column(
        String(length=256), comment="Локализованное имя персонажа"
    )

    bio: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Локализованное описание/история персонажа"
    )
