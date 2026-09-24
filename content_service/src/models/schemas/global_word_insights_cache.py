from pydantic import BaseModel, Field


class GeneralSynonym(BaseModel):
    """
    Вложенная схема для синонима в глобальном кэше слов.
    """

    word: str = Field(..., description="Слово-синоним")
    level: str | None = Field(
        default=None, description="Языковой уровень синонима (например, B2, HSK4)"
    )


class InsightsData(BaseModel):
    """
    Pydantic-схема для строгой типизации поля insights_data.
    Хранит глобальные лингвистические инсайты от LLM, которые переиспользуются между пользователями.
    """

    association: str | None = Field(
        default=None, description="Мнемоника или ассоциация для запоминания слова"
    )
    general_synonyms: list[GeneralSynonym] = Field(
        default_factory=list,
        description="Список общих синонимов с их уровнями сложности",
    )
    base_translations: list[str] = Field(
        default_factory=list,
        description="Массив базовых и самых популярных вариантов перевода",
    )
