from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class SeriesORM(BaseORM, TimestampMixin):
    __tablename__ = "series"
    __table_args__ = (
        {"comment": "Книжные серии и циклы, объединяющие несколько книг"},
    )

    id: Mapped[uuid_pk] = mapped_column(
        comment="Уникальный идентификатор книжной серии/цикла"
    )

    poster_url: Mapped[str | None] = mapped_column(
        String(length=256),
        nullable=True,
        comment="URL-ссылка на обложку серии во внешнем хранилище S3",
    )
