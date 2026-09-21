from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM
from .types.types import book_character_role


class BookCharacterORM(BaseORM):
    __tablename__ = "book_characters"

    book_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    character_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[book_character_role]
