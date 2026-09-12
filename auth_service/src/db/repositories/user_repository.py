from typing import Any

from shared.db import SQLAclchemyRepository
from sqlalchemy import select

from src.models.user import UserORM


class UserRepository(SQLAclchemyRepository[UserORM]):
    async def get_by_email(self, email: str) -> UserORM | None:
        query = select(UserORM).filter_by(email=email)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_token_payload(self, payload: dict[str, Any]) -> UserORM | None:
        user_id = payload.get("sub")
        return await self.get(id=user_id)

    @staticmethod
    def to_token_payload(user: UserORM) -> dict[str, Any]:
        return {
            "sub": str(user.id),
        }
