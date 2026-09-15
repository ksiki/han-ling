from pydantic import BaseModel, EmailStr


class SuccessResponse(BaseModel):
    status: str = "success"
    message: str | None = None


class ResendOTPRequest(BaseModel):
    email: EmailStr
