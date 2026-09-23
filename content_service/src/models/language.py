from shared.db.models import TimestampMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class LanguageORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "languages"
    __table_args__ = (
        {"comment": "Справочник доступных языков (для интерфейса и текстов изданий)"},
    )

    code: Mapped[str] = mapped_column(
        String(length=2),
        primary_key=True,
        comment="Строгий ISO 639-1 код языка (например, 'zh', 'en', 'es')",
    )

    system_name: Mapped[str] = mapped_column(
        String(length=32),
        comment="Системное название на английском (например, 'Chinese', 'English')",
    )
