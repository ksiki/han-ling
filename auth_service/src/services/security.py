import datetime
import uuid
from dataclasses import dataclass
from typing import Any

import bcrypt
import jwt
from shared.security import verify_token

from src.core.settings import config


@dataclass
class TokenPairDTO:
    access_token: str
    refresh_token: str
    refresh_jti: str
    refresh_expires_at: datetime.datetime


class SecurityService:
    def get_password_hash(self, password: str) -> str:
        """Хеширует переданный пароль с использованием bcrypt и соли.

        Args:
            password (str): Строка с паролем, который необходимо захешировать.

        Returns:
            str: Захешированный пароль.
        """

        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()

        return bcrypt.hashpw(
            password=pwd_bytes,
            salt=salt,
        ).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Верифицирует пароль путем сравнения исходной строки с хешем.

        Args:
            plain_password (str): Пароль в открытом виде для проверки.
            hashed_password (str): Действительный хеш пароля, с которым идет сравнение.

        Returns:
            bool: True, если пароль совпадает с хешем, иначе False.
        """

        return bcrypt.checkpw(
            password=plain_password.encode("utf-8"),
            hashed_password=hashed_password.encode("utf-8"),
        )

    def verify_token(self, token: str, expected_type: str) -> dict[str, Any]:
        """Верифицирует JWT токен и проверяет его соответствие ожидаемому типу.

        Args:
            token (str): JWT токен для проверки.
            expected_type (str): Ожидаемый тип токена (например, "access" или "refresh").

        Returns:
            dict[str, Any]: Полезная нагрузка (payload) извлеченная из токена.
        """

        return verify_token(
            token=token,
            secret_key=config.SECRET_KEY,
            algorithm=config.ALGORITHM,
            expected_type=expected_type,
        )

    def create_access_token(self, data: dict[str, Any]) -> str:
        """Генерирует access токен.

        Args:
            data (dict[str, Any]): Данные, которые будут включены в payload токена.

        Returns:
            str: Сгенерированный JWT access токен с вшитыми данными, типом "access"
            и датой истечения срока действия.
        """

        to_encode = data.copy()

        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update(
            {
                "exp": expire,
                "type": "access",
            }
        )

        return jwt.encode(
            payload=to_encode,
            key=config.SECRET_KEY,
            algorithm=config.ALGORITHM,
        )

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        """Генерирует refresh токен.

        Args:
            data (dict[str, Any]): Данные, которые будут включены в payload токена.

        Returns:
            str: Сгенерированный JWT refresh токен с вшитыми данными, типом "refresh"
            и датой истечения срока действия.
        """

        to_encode = data.copy()

        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            days=config.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update(
            {
                "exp": expire,
                "type": "refresh",
            }
        )

        return jwt.encode(
            payload=to_encode,
            key=config.SECRET_KEY,
            algorithm=config.ALGORITHM,
        )

    def create_pair_tokens(self, data: dict[str, Any]) -> TokenPairDTO:
        """Генерирует пару из access и refresh токенов.

        Args:
            data (dict[str, Any]): Базовые данные, которые будут зашиты в оба токена.

        Returns:
            TokenPairDTO: Объект передачи данных, содержащий access токен,
            refresh токен, уникальный идентификатор (jti) refresh токена
            и точную дату его истечения.
        """
        refresh_jti = str(uuid.uuid4())
        refresh_payload = data.copy()
        refresh_payload.update({"jti": refresh_jti})

        access_token = SecurityService.create_access_token(data=data)
        refresh_token = SecurityService.create_refresh_token(data=refresh_payload)

        now = datetime.datetime.now(datetime.UTC)
        refresh_expires_at = now + datetime.timedelta(
            days=config.REFRESH_TOKEN_EXPIRE_DAYS
        )

        return TokenPairDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            refresh_jti=refresh_jti,
            refresh_expires_at=refresh_expires_at,
        )
