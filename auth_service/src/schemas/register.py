from pydantic import BaseModel, EmailStr, Field


class RegisterSendOTPRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    captcha_token: str


class ResendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
