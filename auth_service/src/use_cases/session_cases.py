import uuid

from src.core.exceptions import SessionInvalidException
from src.db.unit_of_work import UnitOfWork
from src.schemas.login import SessionItemResponse


class SessionCases:
    def __init__(self, uow: UnitOfWork) -> None:
        """Инициализирует сценарии работы с сессиями с поддержкой Unit of Work.

        Args:
            uow: Экземпляр Unit of Work для управления транзакциями и репозиториями.
        """
        self._uow = uow

    async def revoke_session_by_id(
        self, session_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> None:
        """Отзывает сессию по ее идентификатору с опциональной проверкой принадлежности пользователю.

        Args:
            session_id: Уникальный идентификатор отзываемой сессии.
            user_id: Идентификатор пользователя для проверки прав на отзыв (опционально).

        Raises:
            SessionInvalidException: Если сессия не найдена или принадлежит другому пользователю.
        """
        session = await self._uow.user_session.get_or_none(id=session_id)

        if not session:
            raise SessionInvalidException
        if user_id and user_id != session.user_id:
            raise SessionInvalidException

        reason = "revoke from another session" if user_id else "logout"
        session.revoke(reason=reason)
        await self._uow.commit()

    async def all_active_sessions(
        self, currents_session_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[SessionItemResponse]:
        """Возвращает список всех активных сессий пользователя с отметкой текущей сессии.

        Args:
            currents_session_id: Идентификатор текущей активной сессии клиента.
            user_id: Идентификатор пользователя, чьи сессии запрашиваются.

        Returns:
            list[SessionItemResponse]: Список DTO-моделей активных сессий пользователя.
        """
        sessions = await self._uow.user_session.all_active_sessions(user_id=user_id)

        return [
            SessionItemResponse(
                id=session.id,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                created_at=session.created_at,
                is_current=str(session.id) == currents_session_id,
            )
            for session in sessions
        ]
