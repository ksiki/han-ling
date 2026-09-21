import datetime

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class AuthorORM(BaseORM, TimestampMixin):
    __tablename__ = "authors"

    id: Mapped[uuid_pk]
    country: Mapped[str] = mapped_column(String(length=3))
    birth_date: Mapped[datetime.date]
    photo_url: Mapped[str] = mapped_column(String(length=256))
