from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM
from .types.types import book_creator_role


class BookCreatorORM(BaseORM):
    __tablename__ = "book_creators"

    book_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    author_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[book_creator_role]
