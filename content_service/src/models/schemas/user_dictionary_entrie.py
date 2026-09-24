from pydantic import BaseModel, Field


class GrammarInfo(BaseModel):
    """
    Вложенная схема для описания грамматических характеристик слова.
    Все поля опциональны, так как грамматика сильно зависит от языка.
    """

    part_of_speech: str | None = Field(
        default=None, description="Часть речи (noun, verb, adjective, etc.)"
    )
    tense: str | None = Field(
        default=None, description="Время (Past Simple, Present Perfect, etc.)"
    )
    base_form: str | None = Field(
        default=None, description="Начальная форма слова (инфинитив)"
    )
    reasoning: str | None = Field(
        default=None, description="Объяснение употребления формы в данном контексте"
    )
    transcription: str | None = Field(
        default=None,
        description="Универсальная фонетическая транскрипция (пиньинь, ромадзи, IPA)",
    )


class TranslationContext(BaseModel):
    """
    Схема для конкретного перевода слова и его контекста.
    """

    meaning: str = Field(..., description="Значение слова (перевод)")
    context_translation: str | None = Field(
        default=None, description="Перевод оригинального предложения-контекста"
    )


class Synonym(BaseModel):
    """
    Схема синонима слова.
    """

    word: str = Field(..., description="Слово-синоним")
    level: str | None = Field(
        default=None, description="Языковой уровень синонима (A1, HSK4, etc.)"
    )


class LinguisticData(BaseModel):
    """
    Pydantic-схема для строгой типизации гибкого объекта linguistic_data.
    Включает в себя переводы, грамматику, ассоциации и синонимы.
    """

    translations: list[TranslationContext] = Field(
        default_factory=list, description="Список возможных переводов и их контекстов"
    )
    grammar: GrammarInfo | None = Field(
        default=None, description="Грамматическая информация о слове"
    )
    association: str | None = Field(
        default=None, description="Мнемоническая ассоциация для запоминания слова"
    )
    synonyms: list[Synonym] = Field(
        default_factory=list, description="Список синонимов изучаемого слова"
    )
