from redis.asyncio import Redis

from src.core.exceptions import CaptchaInvalidException
from src.core.security import verify_turnstile_token
from src.db import UnitOfWork
from src.services import OTPService, OTPTypeEnum, RegistrationService, SessionService


class RegistrationCases:
    def __init__(self, uow: UnitOfWork, redis_client: Redis) -> None:
        """Инициализирует сценарии регистрации с необходимыми сервисами.

        Args:
            uow: Экземпляр Unit of Work для управления транзакциями.
            redis_client: Асинхронный клиент Redis для работы сервиса OTP.
        """
        self._uow = uow
        self._otp_service = OTPService(redis_client=redis_client)
        self._registration_service = RegistrationService(uow=self._uow)
        self._session_service = SessionService(uow=self._uow)

    async def begin_registration(
        self, captcha_token: str, email: str, password: str
    ) -> str:
        """Начинает сценарий регистрации, проверяя email, капчу и формируя OTP.

        Args:
            captcha_token: Токен проверки капчи Cloudflare Turnstile.
            email: Email адрес регистрируемого пользователя.
            password: Пароль пользователя для создания хэша.

        Returns:
            str: Сгенерированный OTP код для подтверждения регистрации.

        Raises:
            UserAlreadyExistsException: Если пользователь с указанным email уже существует.
            CaptchaInvalidException: Если капча не прошла валидацию.
        """
        await self._registration_service.check_email(email=email)

        if not await verify_turnstile_token(token=captcha_token):
            raise CaptchaInvalidException

        otp = await self._otp_service.create_registration_state(
            email=email, password=password
        )
        return otp

    async def resend_otp(self, email: str) -> str:
        """Повторно генерирует и сохраняет OTP код для регистрации пользователя.

        Args:
            email: Email адрес пользователя для повторной генерации кода.

        Returns:
            str: Новый сгенерированный OTP код.

        Raises:
            OTPInvalidException: Если предыдущее состояние регистрации отсутствует.
        """
        otp = await self._otp_service.update_state(email=email, type=OTPTypeEnum.REG)
        return otp

    async def finish_registration(
        self, email: str, otp: str, ip: str, user_agent: str
    ) -> tuple[str, str]:
        """Завершает регистрацию, создавая пользователя и открывая новую сессию.

        Args:
            email: Email адрес регистрируемого пользователя.
            otp: Одноразовый проверочный код.
            ip: IP-адрес клиента.
            user_agent: Данные User-Agent клиентского устройства.

        Returns:
            tuple[str, str]: Пара токенов (access_token, refresh_token).

        Raises:
            OTPInvalidException: Если код подтверждения неверен или истек.
        """
        password_hash = await self._otp_service.verify_registration_otp(
            email=email, otp=otp
        )

        user = await self._registration_service.create_user(
            email=email, password_hash=password_hash
        )

        tokens = await self._session_service.create_session(
            user=user, ip=ip, user_agent=user_agent
        )

        await self._uow.commit()
        return tokens
