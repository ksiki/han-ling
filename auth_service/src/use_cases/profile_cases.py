import uuid

from shared.contracts import UserUpdateEvent
from shared.db.outbox import OutboxMessageORM
from sqlalchemy.exc import IntegrityError

from src.core.exceptions import NicknameInvalidException
from src.db.unit_of_work import UnitOfWork


class ProfileCases:
    def __init__(self, uow: UnitOfWork) -> None:
        """Инициализирует сценарии управления профилем пользователя с поддержкой Unit of Work.

        Args:
            uow: Экземпляр Unit of Work для управления транзакциями и репозиториями.
        """
        self._uow = uow

    async def change_nickname(self, user_id: uuid.UUID, new_nickname: str) -> None:
        """Обновляет никнейм пользователя с проверкой уникальности в базе данных.

        Args:
            user_id: Идентификатор пользователя.
            new_nickname: Новое строковое значение никнейма.

        Raises:
            NicknameInvalidException: Если указанный никнейм уже занят или нарушает ограничения целостности.
        """
        user = await self._uow.user.get(id=user_id)
        user.nickname = new_nickname

        event = UserUpdateEvent(
            user_id=user.id, nickname=user.nickname, role=user.role.value
        )
        outbox_message = OutboxMessageORM(
            exchange="auth.events",
            routing_key="user.updated",
            payload=event.model_dump(mode="json"),
        )
        await self._uow.outbox.add(outbox_message)

        try:
            await self._uow.flush()
        except IntegrityError:
            raise NicknameInvalidException

        await self._uow.commit()
