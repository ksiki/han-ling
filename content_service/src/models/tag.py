from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class TagORM(BaseORM, TimestampMixin):
    __tablename__ = "tags"

    id: Mapped[uuid_pk]
    slug: Mapped[str] = mapped_column(String(length=128), unique=True)
