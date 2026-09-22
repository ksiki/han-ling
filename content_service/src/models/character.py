from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class CharacterORM(BaseORM, TimestampMixin):
    __tablename__ = "characters"
    __table_args__ = (
        {
            "comment": "Хранилище универсальных данных о персонажах (независимо от языка)"
        },
    )

    id: Mapped[uuid_pk] = mapped_column(comment="Уникальный идентификатор персонажа")

    photo_url: Mapped[str | None] = mapped_column(
        String(length=256),
        nullable=True,
        comment="URL-ссылка на аватар/изображение персонажа в S3",
    )
