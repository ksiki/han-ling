import asyncio
import enum
import json
import logging
import random
from typing import Any

from redis.exceptions import RedisError
from shared.interfaces import RedisServiceAbstract

from src.core.exceptions import (
    FailedCreateOTPException,
    OTPAttemptsExceededException,
    OTPInvalidException,
)
from src.core.security import get_password_hash
from src.core.settings import config

logger = logging.getLogger(__name__)


class OTPTypeEnum(enum.Enum):
    REG = "reg"
    RESET = "reset"


class OTPService(RedisServiceAbstract):
    def _make_key(self, type: OTPTypeEnum, email: str) -> str:
        """Формирует уникальный ключ для хранения OTP в Redis.

        Args:
            type: Тип операции.
            email: Email адрес пользователя.

        Returns:
            str: Сформированный ключ для кэша Redis.
        """
        return f"{type.value}_otp:{email}"

    async def _create_otp(self, key: str, payload: dict[str, Any] | None = None) -> str:
        """Генерирует 6-значный OTP код и сохраняет его в Redis вместе с payload.

        К payload автоматически добавляется сгенерированный код и счетчик попыток.

        Args:
            key: Ключ для сохранения данных в Redis.
            payload: Дополнительные данные для кэширования.

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
            await asyncio.wait_for(
                await self.redis.set(
                    name=key,
                    value=json.dumps(payload),
                    ex=config.OTP_EXPIRE_MINUTES * 60,
                ),
                timeout=0.2,
            )
            return otp

        except (TimeoutError, RedisError) as e:
            logger.error(f"Failed to create otp for password reset of {key}: {e}")
            raise FailedCreateOTPException

    async def _get_payload(self, key: str) -> dict[str, Any]:
        """Извлекает и десериализует данные из Redis по заданному ключу.

        Args:
            key: Ключ записи в Redis.

        Returns:
            dict[str, Any]: Десериализованные данные из хранилища.

        Raises:
            OTPInvalidException: Если ключ отсутствует или истек таймаут ожидания.
        """
        result_bytes = await asyncio.wait_for(
            self.redis.get(key),
            timeout=0.1,
        )
        if not result_bytes:
            raise OTPInvalidException

        payload = json.loads(result_bytes)
        return payload

    async def _verify_otp(
        self, email: str, otp: str, type: OTPTypeEnum
    ) -> dict[str, Any]:
        """Извлекает данные из Redis и выполняет валидацию переданного OTP с подсчетом попыток.

        В случае несовпадения кода увеличивает счетчик попыток или удаляет ключ при превышении лимита.
        При успешной проверке удаляет запись из кэша для предотвращения повторного использования.

        Args:
            email: Email адрес пользователя.
            otp: Одноразовый проверочный код для валидации.
            type: Тип выполняемой операции (регистрация или сброс пароля).

        Returns:
            dict[str, Any]: Десериализованные данные сессии из Redis.

        Raises:
            OTPAttemptsExceededException: Если превышено максимальное количество попыток ввода кода.
            OTPInvalidException: Если код неверен, ключ не найден, истек TTL или произошла ошибка Redis/десериализации.
        """
        key = self._make_key(type=type, email=email)

        try:
            payload = await self._get_payload(key=key)

            if payload.get("otp") != otp:
                current_attempts = payload.get("attempts", 0) + 1
                payload["attempts"] = current_attempts

                if current_attempts >= config.MAX_OTP_ATTEMPTS:
                    await asyncio.wait_for(
                        self.redis.delete(key),
                        timeout=0.1,
                    )
                    raise OTPAttemptsExceededException

                ttl = await asyncio.wait_for(
                    self.redis.ttl(key),
                    timeout=0.1,
                )
                if ttl > 0:
                    await asyncio.wait_for(
                        self.redis.set(key, json.dumps(payload), ex=ttl),
                        timeout=0.1,
                    )
                raise OTPInvalidException

            await asyncio.wait_for(
                self.redis.delete(key),
                timeout=0.1,
            )
            return payload

        except (RedisError, json.JSONDecodeError):
            raise OTPInvalidException

    async def create_registration_state(self, email: str, password: str) -> str:
        """Создает OTP для процесса регистрации нового пользователя.

        Сохраняет хэш пароля в кэше Redis.

        Args:
            email: Email адрес регистрируемого пользователя.
            password: Пароль пользователя для вычисления хэша и кэширования.

        Returns:
            str: Сгенерированный OTP код.
        """
        key = self._make_key(type=OTPTypeEnum.REG, email=email)
        password_hash = get_password_hash(password=password)
        payload = {"pwd_hash": password_hash}
        return await self._create_otp(key=key, payload=payload)

    async def create_reset_state(self, email: str) -> str:
        """Создает OTP для процесса восстановления пароля.

        Args:
            email: Email адрес пользователя, запросившего сброс пароля.

        Returns:
            str: Сгенерированный OTP код.
        """
        key = self._make_key(type=OTPTypeEnum.RESET, email=email)
        return await self._create_otp(key=key)

    async def verify_registration_otp(self, email: str, otp: str) -> str:
        """Проверяет валидность OTP при подтверждении регистрации.

        В случае успеха возвращает закэшированный хэш пароля (`pwd_hash`).

        Args:
            email: Email адрес пользователя.
            otp: Введенный одноразовый пароль.

        Returns:
            str: Хэш пароля пользователя, извлеченный из Redis.

        Raises:
            OTPInvalidException: Если код неверен или срок его действия истек.
        """
        payload = await self._verify_otp(email=email, otp=otp, type=OTPTypeEnum.REG)
        return payload["pwd_hash"]

    async def verify_reset_otp(self, email: str, otp: str) -> None:
        """Проверяет валидность OTP при подтверждении сброса пароля.

        Успешное выполнение метода (отсутствие исключений) означает, что OTP верен.

        Args:
            email: Email адрес пользователя.
            otp: Введенный одноразовый пароль.

        Raises:
            OTPInvalidException: Если код неверен или срок его действия истек.
        """
        await self._verify_otp(email=email, otp=otp, type=OTPTypeEnum.RESET)

    async def update_state(self, email: str, type: OTPTypeEnum) -> str:
        """Обновляет OTP код для существующего состояния сессии.

        Args:
            email: Email адрес пользователя.
            type: Тип операции.

        Returns:
            str: Новый сгенерированный OTP код.

        Raises:
            OTPInvalidException: Если предыдущее состояние не найдено.
            FailedCreateOTPException: Если произошла ошибка сохранения нового кода в Redis.
        """
        key = self._make_key(type=type, email=email)
        payload = await self._get_payload(key=key)
        new_otp = await self._create_otp(key=key, payload=payload)
        return new_otp
