from src.core.exceptions import (
    PasswordOrEmailInvalidException,
    ProviderLinkNotFoundException,
)
from src.db.unit_of_work import UnitOfWork
from src.models import ProviderEnum
from src.models.user import UserORM
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

    async def _check_provider_exists(self, google_sub: str) -> bool:
        """Проверяет существование привязки провайдера Google к учетной записи.

        Args:
            google_sub: Уникальный идентификатор субъекта Google (sub).

        Returns:
            bool: True, если привязка существует, иначе False.
        """
        try:
            await self._oauth_service.get_provider(
                provider_id=google_sub, type=ProviderEnum.GOOGLE
            )
            return True
        except ProviderLinkNotFoundException:
            return False

    async def _get_or_create_user(self, email: str) -> UserORM:
        """Получает существующего пользователя по email или создает новую учетную запись без пароля.

        Args:
            email: Адрес электронной почты пользователя.

        Returns:
            UserORM: Экземпляр существующего или вновь созданного пользователя.
        """
        try:
            return await self._auth_service.authenticate(email=email, password=None)
        except PasswordOrEmailInvalidException:
            return await self._registration_service.create_user(
                email=email, password_hash=None
            )

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
        user_email = token_payload.get("email", "")
        google_sub = token_payload.get("sub", "")

        provider_exists = await self._check_provider_exists(google_sub)
        user = await self._get_or_create_user(user_email)

        if not provider_exists:
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
