from shared.db.types import uuid_pk
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class BookTagORM(BaseORM):
    __tablename__ = "book_tags"

    book_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
