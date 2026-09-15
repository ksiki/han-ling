from pydantic import BaseModel


class SuccessResponse(BaseModel):
    status: str = "success"
    message: str | None = None
