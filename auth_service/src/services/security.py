from datetime import UTC, datetime, timedelta
from typing import Any, Final

import jwt
from passlib.context import CryptContext

from src.core.settings import config


class SecurityService:
    PWD_CONTEXT: Final[CryptContext] = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
    )

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """
        Метод для хеширования пароля

        Принимает:
            - пароль для хеширования: str

        Возвращает:
            - хеш пароля: str
        """

        return cls.PWD_CONTEXT.hash(
            secret=password,
        )

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Метод верификации пароля

        Принимает:
            - пароль который нужно верифицировать: str
            - хеш настоящего пароля: str

        Возвращает:
            - да/нет: bool
        """

        return cls.PWD_CONTEXT.verify(
            secret=plain_password,
            hash=hashed_password,
        )

    @classmethod
    def create_access_token(cls, data: dict[str, Any]) -> str:
        """
        Генерация access token

        Принимает:
            - данные, которые нужно вшить в token: dictp[str, Any]

        Возвращает:
            - token с вшитыми данными из data[str, Any] + время действия и тип токена: str
        """

        to_encode = data.copy()

        expire = datetime.now(UTC) + timedelta(
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

    @classmethod
    def create_refresh_token(cls, data: dict[str, Any]) -> str:
        """
        Генерация refresh token

        Принимает:
            - данные, которые нужно вшить в token: dict[str, Any]

        Возвращает:
            - token с вшитыми данными из data[str, Any] + время действия и тип токена: str
        """

        to_encode = data.copy()

        expire = datetime.now(UTC) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
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

    @classmethod
    def create_pair_tokens(cls, data: dict[str, Any]) -> tuple[str]:
        """
        Генерация пары access и refresh токенов

        Принимает:
            - данные, которые нужно вшить в token: dict[str, Any]

        Возвращает:
            - кортеж из access и refresh токенов: tuple[str]
        """

        access_token = SecurityService.create_access_token(data=data)
        refresh_token = SecurityService.create_refresh_token(data=data)
        return access_token, refresh_token
