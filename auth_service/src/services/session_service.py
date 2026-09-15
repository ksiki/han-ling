import datetime
import uuid

import jwt

from src.core.settings import config
from src.db import UnitOfWork
from src.models import UserORM, UserSessionORM


class SessionService:
    def __init__(self, uow: UnitOfWork) -> None:
        """Инициализирует сервис сессий.

        Args:
            uow: Экземпляр Unit of Work для управления транзакциями и доступа к репозиториям.
        """
        self._uow = uow

    def _create_refresh_token(
        self, user_id: uuid.UUID
    ) -> tuple[str, uuid.UUID, datetime.datetime]:
        """Генерирует JWT refresh токен с уникальным идентификатором jti и сроком действия.

        Args:
            user_id: Идентификатор пользователя, для которого выпускается токен.

        Returns:
            tuple[str, uuid.UUID, datetime.datetime]: Кортеж, содержащий закодированный токен,
                его уникальный идентификатор (jti) и дату истечения срока действия.
        """
        jti = uuid.uuid4()
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            days=config.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode = {
            "sub": str(user_id),
            "jti": str(jti),
            "exp": expire,
            "type": "refresh",
        }
        token = jwt.encode(
            payload=to_encode, key=config.SECRET_KEY, algorithm=config.ALGORITHM
        )
        return token, jti, expire

    def _create_access_token(
        self, user_id: uuid.UUID, session_id: uuid.UUID, user_role: str
    ) -> str:
        """Создает JWT access токен с привязкой к сессии и роли пользователя.

        Args:
            user_id: Идентификатор пользователя.
            session_id: Идентификатор связанной сессии пользователя.
            user_role: Роль пользователя в системе.

        Returns:
            str: Закодированный JWT access токен.
        """
        jti = uuid.uuid4()
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {
            "sub": str(user_id),
            "jti": str(jti),
            "session_id": str(session_id),
            "role": user_role,
            "exp": expire,
            "type": "access",
        }
        token = jwt.encode(
            payload=to_encode, key=config.SECRET_KEY, algorithm=config.ALGORITHM
        )
        return token

    async def create_session(
        self, user: UserORM, ip: str, user_agent: str
    ) -> tuple[str, str]:
        """Создает новую сессию пользователя с отзывом старых сессий при превышении лимита.

        Args:
            user_id: Идентификатор пользователя.
            ip: IP-адрес клиента.
            user_agent: Данные User-Agent клиента.

        Returns:
            tuple[str, str]: Пара токенов (access_token, refresh_token).

        Raises:
            UserNotFoundException: Если пользователь с указанным идентификатором не найден.
        """

        active_sessions = await self._uow.user_session.all_active_sessions(
            user_id=user.id
        )
        number_active_sessions = len(active_sessions)
        if number_active_sessions >= config.MAX_ACTIVE_SESSIONS:
            number_sessions_for_revoke = (
                number_active_sessions - config.MAX_ACTIVE_SESSIONS + 1
            )
            sessions_to_revoke = active_sessions[-number_sessions_for_revoke:]
            for active_session in sessions_to_revoke:
                active_session.revoke(reason="exceeding the limit")

        refresh_token, jti, expires_at = self._create_refresh_token(user_id=user.id)

        new_session = UserSessionORM(
            user_id=user.id,
            refresh_token_jti=str(jti),
            user_agent=user_agent,
            ip_address=ip,
            expires_at=expires_at,
        )
        session = await self._uow.user_session.add(new_session)

        access_token = self._create_access_token(
            user_id=user.id, session_id=session.id, user_role=user.role
        )
        return access_token, refresh_token
