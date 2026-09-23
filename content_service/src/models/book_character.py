import uuid

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM
from .types.types import book_character_role


class BookCharacterORM(ContentServiceBaseORM):
    __tablename__ = "book_characters"
    __table_args__ = (
        Index("ix_book_characters_character_id", "character_id"),
        {
            "comment": "Связь персонажа со вселенной/книгой с указанием его значимости для сюжета"
        },
    )

    book_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на книгу",
    )

    character_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на персонажа",
    )

    role: Mapped[book_character_role] = mapped_column(
        comment="Значимость персонажа в сюжете (main, secondary, cameo)"
    )
