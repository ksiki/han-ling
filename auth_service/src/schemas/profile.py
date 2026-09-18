import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field

from src.models import RoleEnum


class ProfileResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    nickname: str
    role: RoleEnum
    registed_at: datetime.datetime


class ChangeNicknameRequest(BaseModel):
    nickname: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_ .-]+$",
        min_length=1,
        max_length=25,
        description="Никнейм может содержать латинские буквы, цифры, дефис, подчеркивание, точку и пробел",
    )
