from shared.db.models import TimestampMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class LanguageORM(BaseORM, TimestampMixin):
    __tablename__ = "languages"

    code: Mapped[str] = mapped_column(String(length=2), primary_key=True)
    system_name: Mapped[str] = mapped_column(String(length=16))
