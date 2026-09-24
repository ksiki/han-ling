import datetime
import uuid
from typing import Any

from shared.db.models import TimestampMixin
from shared.db.types import uuid_pk
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import ContentServiceBaseORM
from .types.types import learning_status as learning_status_type


class UserDictionaryEntrieORM(ContentServiceBaseORM, TimestampMixin):
    __tablename__ = "user_dictionary_entries"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "word",
            "language_code",
            name="uq_user_dictionary_entries_user_id_word_language_code",
        ),
        Index(
            "ix_user_dict_review_date",
            "user_id",
            "next_review_date",
            postgresql_where=("next_review_date IS NOT NULL"),
        ),
        Index("ix_user_dict_language", "user_id", "language_code"),
        Index("ix_user_dict_learning_status", "user_id", "learning_status"),
    )

    id: Mapped[uuid_pk] = mapped_column(
        comment="Уникальный идентификатор словарной карточки"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        comment="Ссылка на владельца карточки",
    )

    word: Mapped[str] = mapped_column(
        String(length=128), comment="Само изучаемое слово или фраза на языке оригинала"
    )

    language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"),
        comment="Язык изучаемого слова (например, 'en', 'zh')",
    )

    translation_language_code: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="RESTRICT"),
        comment="Язык перевода (соответствует языку выбранных субтитров)",
    )

    source_book_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("books.id", ondelete="SET NULL"),
        nullable=True,
        comment="Книга, из которой было добавлено слово (для возврата к контексту)",
    )

    context_sentence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Предложение-контекст, в котором слово было встречено изначально",
    )

    linguistic_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        default=dict,
        comment="Гибкий объект для хранения специфичных для данных (перевод, грамматика, синонимы, ассоциации)",
    )

    learning_status: Mapped[learning_status_type] = mapped_column(
        comment="Текущий статус изучения (NEW, LEARNING, REVIEWING, MASTERED)"
    )

    next_review_date: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Дата следующего повторения (для алгоритма SRS, например SuperMemo 2)",
    )
