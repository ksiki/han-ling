import logging
from typing import Any

import bcrypt
import httpx

from src.core.http import http_client
from src.core.settings import config

logger = logging.getLogger(__name__)


def get_password_hash(password: str) -> str:
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


def verify_password(plain_password: str, hashed_password: str) -> bool:
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


async def verify_turnstile_token(
    token: str,
    client_ip: str | None = None,
    idempotency_key: str | None = None,
) -> bool:
    """Верифицирует токен Cloudflare Turnstile через внешний API.

    Args:
        token: Токен ответа капчи, полученный от клиента.
        client_ip: IP-адрес конечного пользователя (опционально).
        idempotency_key: UUID для предотвращения повторной валидации запроса (опционально).

    Returns:
        bool: True, если токен успешно прошел валидацию, иначе False.
    """
    if not token or not token.strip():
        return False

    payload: dict[str, Any] = {
        "secret": config.CLOUDFLARE_SECRET_KEY,
        "response": token,
    }
    if client_ip:
        payload["remoteip"] = client_ip
    if idempotency_key:
        payload["idempotency_key"] = idempotency_key

    try:
        response = await http_client.post(config.CLOUDFLARE_VERIFY_URL, json=payload)
        response.raise_for_status()
        data = response.json()
    except httpx.TimeoutException:
        logger.error("Cloudflare Turnstile timeout")
        return False
    except httpx.RequestError as exc:
        logger.error("Network error with request of Turnstile: %s", exc)
        return False
    except ValueError:
        logger.error("Can't parsed JSON from Cloudflare. Response: %s", response.text)
        return False

    if not data.get("success"):
        logger.warning(
            "Turnstile rejected the captcha: %s", data.get("error-codes", [])
        )
        return False

    return True
