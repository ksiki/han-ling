import uuid

from src.core.exceptions import CaptchaInvalidException, PasswordOrEmailInvalidException
from src.core.security import verify_turnstile_token
from src.db.unit_of_work import UnitOfWork
from src.services import AuthService, SessionService


class AuthCases:
    def __init__(self, uow: UnitOfWork) -> None:
        """Инициализирует сценарии аутентификации с необходимыми сервисами.

        Args:
            uow: Экземпляр Unit of Work для управления транзакциями и репозиториями.
        """
        self._uow = uow
        self._login_service = AuthService(uow=self._uow)
        self._session_service = SessionService(uow=self._uow)

    async def login_by_email(
        self, captcha_token: str, email: str, password: str, ip: str, user_agent: str
    ) -> tuple[str, str]:
        """Выполняет аутентификацию по email и паролю с созданием новой сессии.

        Args:
            captcha_token: Токен проверки капчи Cloudflare Turnstile.
            email: Email адрес пользователя.
            password: Пароль пользователя в открытом виде.
            ip: IP-адрес клиентского устройства.
            user_agent: Данные заголовка User-Agent клиента.

        Returns:
            tuple[str, str]: Пара токенов (access_token, refresh_token).

        Raises:
            CaptchaInvalidException: Если проверка капчи не пройдена.
            PasswordOrEmailInvalidException: Если передан пустой пароль или неверные учетные данные.
        """
        if not await verify_turnstile_token(token=captcha_token):
            raise CaptchaInvalidException
        if password is None or password.strip() == "":
            raise PasswordOrEmailInvalidException

        user = await self._login_service.authenticate(email=email, password=password)
        tokens = await self._session_service.create_session(
            user=user, ip=ip, user_agent=user_agent
        )

        await self._uow.commit()
        return tokens

    async def update_access_token(
        self, user_id: uuid.UUID, user_role: str, refresh_jti: uuid.UUID
    ) -> str:
        """Создает новый access-токен на основе активной сессии, связанной с refresh-токеном.

        Args:
            user_id: Идентификатор пользователя.
            user_role: Строковое представление роли пользователя.
            refresh_jti: Уникальный идентификатор (jti) связанного refresh-токена.

        Returns:
            str: Сгенерированный access-токен.

        Raises:
            InvalidTokenException: Если сессия по переданному jti не найдена.
        """
        session = await self._uow.user_session.get_by_jti(jti=refresh_jti)
        return self._session_service.create_access_token(
            user_id=user_id, session_id=session.id, user_role=user_role
        )
