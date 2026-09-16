from redis.asyncio import Redis

from src.core.exceptions import CaptchaInvalidException
from src.core.security import verify_turnstile_token
from src.db import UnitOfWork
from src.services import OTPService, OTPTypeEnum, RecoveryService, SessionService


class PasswordResetCaces:
    def __init__(self, uow: UnitOfWork, redis_client: Redis) -> None:
        """Инициализирует сценарии восстановленяи пароля с необходимыми сервисами.

        Args:
            uow: Экземпляр Unit of Work для управления транзакциями.
            redis_client: Асинхронный клиент Redis для работы сервиса OTP.
        """
        self._uow = uow
        self._otp_service = OTPService(redis_client=redis_client)
        self._recovery_service = RecoveryService(uow=self._uow)
        self._session_service = SessionService(uow=self._uow)

    async def begin_password_recovery(self, captcha_token: str, email: str) -> str:
        """Запускает сценарий восстановления пароля с проверкой капчи и генерацией OTP.

        Args:
            captcha_token: Токен проверки капчи Cloudflare Turnstile.
            email: Email адрес пользователя, запросившего сброс пароля.

        Returns:
            str: Сгенерированный OTP код для подтверждения сброса пароля.

        Raises:
            CaptchaInvalidException: Если проверка капчи не пройдена.
        """
        if not await verify_turnstile_token(token=captcha_token):
            raise CaptchaInvalidException

        otp = await self._otp_service.create_reset_state(email=email)
        return otp

    async def resend_otp(self, email: str) -> str:
        """Повторно генерирует и сохраняет OTP код для восстановления пароля.

        Args:
            email: Email адрес пользователя для повторной генерации кода.

        Returns:
            str: Новый сгенерированный OTP код.

        Raises:
            OTPInvalidException: Если предыдущее состояние регистрации отсутствует.
        """
        otp = await self._otp_service.update_state(email=email, type=OTPTypeEnum.RESET)
        return otp

    async def finish_password_recovery(
        self, email: str, otp: str, new_password: str, ip: str, user_agent: str
    ) -> tuple[str, str]:
        """Завершает сброс пароля, обновляет пароль пользователя и создает новую сессию.

        Args:
            email: Email адрес пользователя.
            otp: Одноразовый проверочный код из хранилища.
            new_password: Новый пароль пользователя.
            ip: IP-адрес клиентского устройства.
            user_agent: Данные заголовка User-Agent клиента.

        Returns:
            tuple[str, str]: Пара токенов (access_token, refresh_token).

        Raises:
            OTPInvalidException: Если переданный OTP код неверен или истек.
            UserNotFoundException: Если пользователь с указанным email не найден.
        """
        await self._otp_service.verify_reset_otp(email=email, otp=otp)

        user = await self._recovery_service.change_password_by_email(
            email=email, new_password=new_password
        )
        tokens = await self._session_service.create_session(
            user=user, ip=ip, user_agent=user_agent
        )

        await self._uow.commit()
        return tokens
