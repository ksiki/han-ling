from pydantic import BaseModel


class UserRegisterRequest(BaseModel):
    email: str
    password: str
    password_replay: str
