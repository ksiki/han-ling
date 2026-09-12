from typing import Any

import jwt

from .exceptions import InvalidTokenException


def verify_token(
    token: str, secret_key: str, algorithm: str, expected_type: str = "access"
) -> dict[str, Any]:
    """
    Метод для верификации токена без проверки нахождения его в черном спике в Redis

    Принимает:
        - токен: str
        - ключ шифрования: str
        - алгоритм шифрования: str
        - ожидаемый тип токена: str = "access"

    Возвращает:
        - весь payload из токена: dict[str, Any]

    Исключения:
        - токен истек: InvalidTokenException
        - ошибка типа токена: InvalidTokenException
        - иная ошибка токена: InvalidTokenException
    """

    try:
        payload = jwt.decode(jwt=token, key=secret_key, algorithms=[algorithm])
        if payload.get("type") != expected_type:
            raise InvalidTokenException
        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidTokenException()
    except jwt.PyJWTError:
        raise InvalidTokenException()
