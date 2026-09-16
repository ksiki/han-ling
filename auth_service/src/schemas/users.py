import datetime
import uuid

from pydantic import BaseModel, EmailStr

from src.models import RoleEnum


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: RoleEnum
    registed_at: datetime.datetime


class SessionItemResponse(BaseModel):
    id: uuid.UUID
    ip_address: str | None
    user_agent: str | None
    created_at: datetime.datetime
    is_current: bool


class SessionsListResponse(BaseModel):
    sessions: list[SessionItemResponse]
