from shared.db.types import created_at_type, uuid_pk
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class UserFavoriteORM(BaseORM):
    __tablename__ = "user_favorites"

    user_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    book_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )

    created_at: Mapped[created_at_type]
