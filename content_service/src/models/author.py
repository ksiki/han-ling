import datetime

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class AuthorORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "authors"
    __table_args__ = (
        {"comment": "Создатели контента (авторы, иллюстраторы, переводчики)"},
    )

    id: Mapped[uuid_pk] = mapped_column(comment="Уникальный идентификатор создателя")

    country: Mapped[str | None] = mapped_column(
        String(length=3), nullable=True, comment="ISO-код страны рождения/проживания"
    )

    birth_date: Mapped[datetime.date | None] = mapped_column(
        Date, nullable=True, comment="Дата рождения создателя"
    )

    photo_url: Mapped[str | None] = mapped_column(
        String(length=256),
        nullable=True,
        comment="URL-ссылка на фотографию автора в S3",
    )
