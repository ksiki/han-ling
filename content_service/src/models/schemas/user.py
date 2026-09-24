from pydantic import BaseModel, Field


class ReaderSettings(BaseModel):
    """
    Pydantic-схема для строгой типизации и валидации настроек читалки пользователя.
    Позже ты сможешь вынести её в слой схем (например, src/schemas/user.py).
    """

    font_family: str = Field(
        default="sans-serif", description="Семейство шрифтов для текста книги"
    )
    font_size: int = Field(
        default=16, ge=8, le=72, description="Размер шрифта в пикселях"
    )
    line_height: float = Field(
        default=1.5,
        ge=1.0,
        le=3.0,
        description="Межстрочный интервал для комфортного чтения",
    )
    subtitles_enabled: bool = Field(
        default=True,
        description="Флаг отображения перевода (субтитров) под оригинальным текстом",
    )
    transcription_enabled: bool = Field(
        default=True,
        description="Флаг отображения фонетической транскрипции (пиньинь, ромадзи, IPA и т.д.) в зависимости от языка",
    )

    voice_actor: str | None = Field(
        default="Li Ming",
        description="Идентификатор или имя выбранного голоса для озвучки текста",
    )
    playback_speed: float = Field(
        default=1.0,
        ge=0.25,
        le=3.0,
        description="Множитель скорости воспроизведения аудио",
    )
    dictionary_language: str = Field(
        min_length=2,
        max_length=2,
        description="Код языка, на который будут переводиться слова по умолчанию",
    )
