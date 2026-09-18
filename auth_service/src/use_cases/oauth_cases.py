from src.core.exceptions import (
    PasswordOrEmailInvalidException,
    ProviderLinkNotFoundException,
)
from src.db.unit_of_work import UnitOfWork
from src.models import ProviderEnum
from src.services import AuthService, OAuthService, RegistrationService, SessionService


class OAuthCases:
    def __init__(self, uow: UnitOfWork) -> None:
        """Инициализирует сценарии OAuth-аутентификации с необходимыми сервисами.

        Args:
            uow: Экземпляр Unit of Work для управления транзакциями и репозиториями.
        """
        self._uow = uow
        self._oauth_service = OAuthService(uow=self._uow)
        self._auth_service = AuthService(uow=self._uow)
        self._registration_service = RegistrationService(uow=self._uow)
        self._session_service = SessionService(uow=self._uow)

    async def login_by_google(
        self, id_token: str, ip: str, user_agent: str
    ) -> tuple[str, str]:
        """Выполняет аутентификацию или регистрацию пользователя через Google ID Token с созданием сессии.

        Args:
            id_token: Токен идентификации Google (ID Token).
            ip: IP-адрес клиентского устройства.
            user_agent: Данные заголовка User-Agent клиента.

        Returns:
            tuple[str, str]: Пара токенов (access_token, refresh_token).

        Raises:
            OAuthTokenInvalidException: Если переданный Google ID Token не прошел валидацию.
        """
        token_payload = self._oauth_service.check_google_token(token=id_token)

        google_sub = token_payload.get("sub", "")
        try:
            await self._oauth_service.get_provider(
                provider_id=google_sub, type=ProviderEnum.GOOGLE
            )
        except ProviderLinkNotFoundException:
            user_email = token_payload.get("email", "")
            try:
                user = await self._auth_service.authenticate(
                    email=user_email, password=None
                )
            except PasswordOrEmailInvalidException:
                user = await self._registration_service.create_user(
                    email=user_email, password_hash=None
                )

            await self._oauth_service.create_provider(
                user_id=user.id,
                provider_id=google_sub,
                type=ProviderEnum.GOOGLE,
            )

        tokens = await self._session_service.create_session(
            user=user, ip=ip, user_agent=user_agent
        )
        await self._uow.commit()
        return tokens
