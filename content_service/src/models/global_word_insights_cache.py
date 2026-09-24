from typing import Any

from shared.db.types import created_at_type, uuid_pk
from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class GlobalWordInsightsCacheORM(ContentServiceBaseORM):
    __tablename__ = "global_word_insights_cache"
    __table_args__ = (
        UniqueConstraint(
            "word",
            "source_language_code",
            "target_language_code",
            name="uq_global_word_cache_word_src_tgt",
        ),
        Index(
            "ix_global_word_cache_lookup",
            "word",
            "source_language_code",
            "target_language_code",
        ),
        {
            "comment": "Глобальный кэш инсайтов от LLM для переиспользования данных о словах"
        },
    )

    id: Mapped[uuid_pk] = mapped_column(comment="Уникальный идентификатор записи кэша")

    word: Mapped[str] = mapped_column(
        String(length=128),
        comment='Базовое слово или иероглиф (например, "open", "打开")',
    )

    source_language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"), comment="Код языка оригинала"
    )

    target_language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"), comment="Код языка перевода"
    )

    insights_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        default=dict,
        comment="Глобальные данные от LLM (ассоциации, синонимы, переводы), которые можно переиспользовать",
    )

    created_at: Mapped[created_at_type] = mapped_column(
        comment="Дата и время создания записи (сохранения в кэш)"
    )
