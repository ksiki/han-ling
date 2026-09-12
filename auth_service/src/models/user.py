from shared.db.types import uuid_pk
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base_orm import BaseORM


class UserORM(BaseORM):
    __tablename__ = "users"

    id: Mapped[uuid_pk]

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(length=255))
