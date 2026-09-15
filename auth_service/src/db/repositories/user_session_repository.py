import uuid

from shared.db import SQLAclchemyRepository
from sqlalchemy import func, select

from src.models import UserSessionORM


class UserSessionRepository(SQLAclchemyRepository[UserSessionORM]):
    def __init__(self, session):
        """Инициализирует репозиторий сессий с моделью UserSessionORM.

        Args:
            session: Асинхронная сессия SQLAlchemy для взаимодействия с базой данных.
        """
        super().__init__(session, model_cls=UserSessionORM)

    async def all_active_sessions(self, user_id: uuid.UUID) -> list[UserSessionORM]:
        """Возвращает список всех активных и неотмененных сессий пользователя.

        Args:
            user_id: Идентификатор пользователя для фильтрации сессий.

        Returns:
            list[UserSessionORM]: Список активных объектов сессий, отсортированных по дате создания.
        """
        query = (
            select(UserSessionORM)
            .where(
                UserSessionORM.user_id == user_id,
                UserSessionORM.is_revoked.is_(False),
                UserSessionORM.expires_at > func.now(),
            )
            .order_by(UserSessionORM.created_at.desc())
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())
