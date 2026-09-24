import uuid

from shared.db.models import TimestampMixin
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class TagTranslationORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "tag_translations"
    __table_args__ = (
        {"comment": "Локализация названий тегов/жанров на языки интерфейса"},
    )

    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на системный тег",
    )

    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"),
        primary_key=True,
        comment="Язык локализации тега",
    )

    name: Mapped[str] = mapped_column(
        String(length=128), comment="Человекочитаемое название тега на выбранном языке"
    )
