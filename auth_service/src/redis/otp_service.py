import asyncio
import enum
import json
import logging
import random
from typing import Any

from redis.exceptions import RedisError
from shared.interfaces import RedisServiceAbstract

from src.core.exceptions import FailedCreateOTPException, OTPInvalidException
from src.core.settings import config

logger = logging.getLogger(__name__)


class OTPTypeEnum(enum.Enum):
    REG = "reg"
    RESET = "reset"


class OTPService(RedisServiceAbstract):
    def _make_key(self, type: OTPTypeEnum, email: str) -> str:
        """
        Формирует уникальный ключ для хранения OTP в Redis.

        Args:
            type (OTPTypeEnum): Тип операции.
            email (str): Email адрес пользователя.

        Returns:
            str: Сформированный ключ для кэша Redis.
        """
        return f"{type.value}_otp:{email}"

    async def _create_otp(self, key: str, payload: dict[str, Any] | None = None) -> str:
        """
        Генерирует 6-значный OTP код и сохраняет его в Redis вместе с payload.

        К payload автоматически добавляется сгенерированный код и счетчик попыток.

        Args:
            key (str): Ключ для сохранения данных в Redis.
            payload (dict[str, Any] | None, optional): Дополнительные данные для кэширования.

        Returns:
            str: Сгенерированный 6-значный OTP код.

        Raises:
            FailedCreateOTPException: Если произошла ошибка при записи в Redis или истек таймаут ожидания.
        """
        payload = payload or {}
        otp = str(random.randint(100000, 999999))

        payload["otp"] = otp
        payload["attempts"] = 0

        try:

            async def _redis_operations() -> None:
                await self.redis.setex(
                    name=key,
                    time=config.OTP_EXPIRE_MINUTES * 60,
                    value=json.dumps(payload),
                )

            await asyncio.wait_for(_redis_operations(), timeout=0.2)
            return otp

        except (TimeoutError, RedisError) as e:
            logger.error(f"Failed to create otp for password reset of {key}: {e}")
            raise FailedCreateOTPException

    async def _verify_otp_core(
        self, email: str, otp: str, type: OTPTypeEnum
    ) -> dict[str, Any]:
        """
        Извлекает данные из Redis и производит базовую валидацию переданного OTP.

        В случае успешной проверки удаляет ключ из кэша для предотвращения повторного использования кода.

        Args:
            email (str): Email адрес пользователя.
            otp (str): Одноразовый пароль для валидации.
            type (OTPTypeEnum): Тип операции.

        Returns:
            dict[str, Any]: payload из Redis.

        Raises:
            OTPInvalidException: Если ключ не найден, код не совпадает или произошла ошибка чтения кэша.
        """
        key = self._make_key(type=type, email=email)

        try:
            result_bytes = await asyncio.wait_for(
                self.redis.get(key),
                timeout=0.1,
            )
            if not result_bytes:
                raise OTPInvalidException

            payload = json.loads(result_bytes)

            if payload.get("otp") != otp:
                raise OTPInvalidException

            await asyncio.wait_for(
                self.redis.delete(key),
                timeout=0.1,
            )
            return payload

        except (RedisError, json.JSONDecodeError):
            raise OTPInvalidException

    async def get_register_otp(self, email: str, password_hash: str) -> str:
        """
        Создает OTP для процесса регистрации нового пользователя.

        Сохраняет хэш пароля в кэше Redis

        Args:
            email (str): Email адрес регистрируемого пользователя.
            password_hash (str): Хэш пароля пользователя.

        Returns:
            str: Сгенерированный OTP код.
        """
        key = self._make_key(type=OTPTypeEnum.REG, email=email)
        payload = {"pwd_hash": password_hash}
        return await self._create_otp(key=key, payload=payload)

    async def get_reset_otp(self, email: str) -> str:
        """
        Создает OTP для процесса восстановления пароля.

        Args:
            email (str): Email адрес пользователя, запросившего сброс пароля.

        Returns:
            str: Сгенерированный OTP код.
        """
        key = self._make_key(type=OTPTypeEnum.RESET, email=email)
        return await self._create_otp(key=key)

    async def verify_register_otp(self, email: str, otp: str) -> str:
        """
        Проверяет валидность OTP при подтверждении регистрации.

        В случае успеха возвращает закэшированный хэш пароля (`pwd_hash`)

        Args:
            email (str): Email адрес пользователя.
            otp (str): Введенный одноразовый пароль.

        Returns:
            str: Хэш пароля пользователя, извлеченный из Redis.

        Raises:
            OTPInvalidException: Если код неверен или срок его действия истек.
        """
        payload = await self._verify_otp_core(
            email=email, otp=otp, type=OTPTypeEnum.REG
        )
        return payload["pwd_hash"]

    async def verify_reset_otp(self, email: str, otp: str) -> None:
        """
        Проверяет валидность OTP при подтверждении сброса пароля.

        Успешное выполнение метода (отсутствие исключений) означает, что OTP верен

        Args:
            email (str): Email адрес пользователя.
            otp (str): Введенный одноразовый пароль.

        Raises:
            OTPInvalidException: Если код неверен или срок его действия истек.
        """
        await self._verify_otp_core(email=email, otp=otp, type=OTPTypeEnum.RESET)
