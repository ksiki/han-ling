from typing import Literal

from pydantic import BaseModel, Field, model_validator


class AlignmentBlockSchema(BaseModel):
    type: Literal["1-to-1", "1-to-N", "N-to-1", "N-to-M", "1-to-0", "0-to-1"]

    src: list[str] = Field(default_factory=list, description="ID original sentence")
    tgt: list[str] = Field(default_factory=list, description="ID translation sentence")

    @model_validator(mode="after")
    def validate_logical_lengths(self) -> "AlignmentBlockSchema":
        t = self.type
        src_len = len(self.src)
        tgt_len = len(self.tgt)

        if t == "1-to-1" and (src_len != 1 or tgt_len != 1):
            raise ValueError("Type 1-to-1 requires exactly 1 src and 1 tgt ID")
        elif t == "1-to-N" and (src_len != 1 or tgt_len < 2):
            raise ValueError(
                "The 1-to-N type requires 1 src and a minimum of 2 tgt IDs"
            )
        elif t == "N-to-1" and (src_len < 2 or tgt_len != 1):
            raise ValueError("Type N-to-1 requires at least 2 src and 1 tgt ID")
        elif t == "1-to-0" and (src_len != 1 or tgt_len != 0):
            raise ValueError("Type 1-to-0 requires 1 src and an empty array of tgt")
        elif t == "0-to-1" and (src_len != 0 or tgt_len != 1):
            raise ValueError("Type 0-to-1 requires an empty array of src and 1 tgt ID")

        return self


class ChapterAlignmentSchema(BaseModel):
    alignment_map: list[AlignmentBlockSchema]
