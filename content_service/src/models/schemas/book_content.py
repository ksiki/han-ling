from typing import Annotated, Literal

from pydantic import BaseModel, Field, HttpUrl


class TokenSchema(BaseModel):
    id: str
    w: str
    type: Literal["word", "punct"]
    pinyin: str | None = None


class SentenceSchema(BaseModel):
    id: str
    text: str
    tokens: list[TokenSchema] = Field(default_factory=list)


class ParagraphBlockSchema(BaseModel):
    type: Literal["paragraph"]
    id: str
    sentences: list[SentenceSchema]


class ImageBlockSchema(BaseModel):
    type: Literal["image"]
    id: str
    url: HttpUrl
    alt_text: str | None = None


ContentBlock = Annotated[
    ParagraphBlockSchema | ImageBlockSchema, Field(discriminator="type")
]


class ChapterContentSchema(BaseModel):
    blocks: list[ContentBlock]
