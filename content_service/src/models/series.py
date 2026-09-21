from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class SeriesORM(BaseORM, TimestampMixin):
    __tablename__ = "series"

    id: Mapped[uuid_pk]
    poster_url: Mapped[str] = mapped_column(String(length=256))
