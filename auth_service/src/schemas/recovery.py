from pydantic import BaseModel, EmailStr, Field


class PasswordResetSendRequest(BaseModel):
    email: EmailStr
    captcha_token: str


class PasswordResetConfirmRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)
