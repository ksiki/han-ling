from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class CharacterORM(BaseORM, TimestampMixin):
    __tablename__ = "characters"

    id: Mapped[uuid_pk]
    photo_url: Mapped[str] = mapped_column(String(length=256))
