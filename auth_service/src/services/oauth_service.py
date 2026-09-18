import uuid
from typing import Any

from google.auth.transport import requests
from google.oauth2 import id_token

from src.core.exceptions import (
    GoogleTokenInvalidException,
    ProviderLinkNotFoundException,
)
from src.core.settings import config
from src.db import UnitOfWork
from src.models import ProviderEnum
from src.models.user_provider import UserProviderORM


class OAuthService:
    def __init__(self, uow: UnitOfWork) -> None:
        """Инициализирует сервис OAuth с поддержкой Unit of Work.

        Args:
            uow: Экземпляр Unit of Work для доступа к репозиториям и транзакциям.
        """
        self._uow = uow

    def check_google_token(self, token: str) -> dict[str, Any]:
        """Верифицирует Google ID Token и проверяет подтверждение адреса электронной почты.

        Args:
            token: Строка Google ID Token для проверки.

        Returns:
            dict[str, Any]: Полезная нагрузка верифицированного токена.

        Raises:
            GoogleTokenInvalidException: Если токен невалиден, не содержит email или email не подтвержден.
        """
        try:
            id_info = id_token.verify_oauth2_token(
                token, requests.Request(), config.GOOGLE_CLIENT_ID
            )
        except ValueError:
            raise GoogleTokenInvalidException

        email = id_info.get("email")
        email_verified = id_info.get("email_verified", False)
        if not email or not email_verified:
            raise GoogleTokenInvalidException

        return id_info

    async def get_provider(
        self, provider_id: str, type: ProviderEnum
    ) -> UserProviderORM:
        """Получает запись о привязке внешнего OAuth-провайдера.

        Args:
            provider_id: Уникальный идентификатор пользователя у провайдера (sub).
            type: Тип внешнего провайдера авторизации.

        Returns:
            UserProviderORM: Экземпляр модели связи с провайдером.

        Raises:
            ProviderLinkNotFoundException: Если связь с провайдером не найдена.
        """
        provider_link = await self._uow.user_provider.get_or_none(
            provider_id=provider_id, provider=type
        )
        if not provider_link:
            raise ProviderLinkNotFoundException
        return provider_link

    async def create_provider(
        self, user_id: uuid.UUID, provider_id: str, type: ProviderEnum
    ) -> UserProviderORM:
        """Создает и добавляет в сессию новую привязку внешнего OAuth-провайдера к пользователю.

        Args:
            user_id: Идентификатор пользователя в системе.
            provider_id: Уникальный идентификатор пользователя у провайдера.
            type: Тип внешнего провайдера авторизации.

        Returns:
            UserProviderORM: Созданный экземпляр модели связи с провайдером.
        """
        new_provider = UserProviderORM(
            user_id=user_id, provider_id=provider_id, provider=type
        )
        await self._uow.user_provider.add(new_provider)
        await self._uow.flush()
        return new_provider
