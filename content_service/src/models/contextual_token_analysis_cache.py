import uuid
from typing import Any

from shared.db.types import created_at_type, uuid_pk
from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM


class ContextualTokenAnalysisCacheORM(ContentServiceBaseORM):
    __tablename__ = "contextual_token_analysis_cache"
    __table_args__ = (
        UniqueConstraint(
            "chapter_id",
            "sentence_id",
            "token_id",
            "target_language_code",
            name="uq_contextual_token_cache_chapter_sentence_token_tgt",
        ),
        Index(
            "ix_contextual_token_cache_lookup",
            "chapter_id",
            "sentence_id",
            "token_id",
            "target_language_code",
        ),
        {
            "comment": "Кэш контекстного анализа токенов от LLM для быстрой выдачи пользователям"
        },
    )

    id: Mapped[uuid_pk] = mapped_column(
        comment="Уникальный идентификатор записи контекстного кэша"
    )

    chapter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("edition_chapters.id", ondelete="CASCADE"),
        comment="Привязка к главе (каскадное удаление, если глава удалена)",
    )

    sentence_id: Mapped[str] = mapped_column(
        String(length=64), comment="ID предложения (например, 's_zh_001')"
    )

    token_id: Mapped[str] = mapped_column(
        String(length=64), comment="ID токена внутри предложения (например, 't1')"
    )

    target_language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"),
        comment="На какой язык был запрошен перевод и анализ",
    )

    analysis_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        default=dict,
        comment="Контекстные данные от LLM (перевод в контексте, грамматика)",
    )

    created_at: Mapped[created_at_type] = mapped_column(
        comment="Дата и время создания записи (сохранения в кэш)"
    )
