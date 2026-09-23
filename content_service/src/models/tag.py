from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class TagORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "tags"
    __table_args__ = ({"comment": "Системный рубрикатор тегов/жанров"},)

    id: Mapped[uuid_pk] = mapped_column(comment="Уникальный идентификатор тега/жанра")

    slug: Mapped[str] = mapped_column(
        String(length=128),
        unique=True,
        comment="Системное уникальное имя для URL и поиска",
    )
