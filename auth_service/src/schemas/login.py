import datetime
import uuid

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    captcha_token: str


class GoogleLoginRequest(BaseModel):
    id_token: str


class SessionItemResponse(BaseModel):
    id: uuid.UUID
    ip_address: str | None
    user_agent: str | None
    created_at: datetime.datetime
    is_current: bool


class SessionsListResponse(BaseModel):
    sessions: list[SessionItemResponse]
