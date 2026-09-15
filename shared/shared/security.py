from typing import Any

import jwt

from .exceptions import InvalidTokenException


def verify_token(
    token: str, secret_key: str, algorithm: str, expected_type
) -> dict[str, Any]:
    """Верифицирует токен без проверки его нахождения в черном списке (Redis).

    Декодирует JWT токен, проверяет срок его действия, валидность
    и соответствие ожидаемому типу.

    Args:
        token (str): JWT токен для проверки.
        secret_key (str): Секретный ключ, использованный для подписи токена.
        algorithm (str): Алгоритм шифрования токена.
        expected_type (str): Ожидаемый тип токена (например, "access" или "refresh").

    Returns:
        dict[str, Any]: Полезная нагрузка (payload) токена.

    Raises:
        InvalidTokenException: Если токен отсутствует (None), у него истек срок
            действия, не совпадает тип (`expected_type`), или возникла любая
            другая ошибка при его расшифровке библиотекой PyJWT.
    """

    if token is None:
        raise InvalidTokenException

    try:
        payload = jwt.decode(jwt=token, key=secret_key, algorithms=[algorithm])
        if payload.get("type") != expected_type:
            raise InvalidTokenException
        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidTokenException
    except jwt.PyJWTError:
        raise InvalidTokenException
