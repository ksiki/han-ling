import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserUpdateEvent(BaseModel):
    user_id: UUID
    nickname: str
    role: str
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
