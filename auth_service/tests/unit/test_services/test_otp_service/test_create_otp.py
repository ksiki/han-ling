import json

import pytest
from redis.exceptions import RedisError

from src.core.exceptions import FailedCreateOTPException


async def test_create_otp_success_with_payload(otp_service, mock_redis, mocker):
    """Тест: Успешная генерация OTP и сохранение в Redis с переданным payload."""
    key = "otp:reset:test@example.com"
    payload = {"email": "test@example.com"}

    mocker.patch("src.services.otp_service.random.randint", return_value=123456)

    mock_config = mocker.patch("src.services.otp_service.config")
    mock_config.OTP_EXPIRE_MINUTES = 5

    result = await otp_service._create_otp(key=key, payload=payload.copy())

    assert result == "123456"

    expected_payload = {"email": "test@example.com", "otp": "123456", "attempts": 0}
    mock_redis.set.assert_called_once_with(
        name=key,
        value=json.dumps(expected_payload),
        ex=300,
    )


async def test_create_otp_success_without_payload(otp_service, mock_redis, mocker):
    """Тест: Успешная генерация OTP без передачи payload (создается пустой словарь)."""
    key = "otp:reg:test@example.com"
    mocker.patch("src.services.otp_service.random.randint", return_value=654321)
    mock_config = mocker.patch("src.services.otp_service.config")
    mock_config.OTP_EXPIRE_MINUTES = 10

    result = await otp_service._create_otp(key=key)

    assert result == "654321"

    expected_payload = {"otp": "654321", "attempts": 0}
    mock_redis.set.assert_called_once_with(
        name=key, value=json.dumps(expected_payload), ex=600
    )


@pytest.mark.parametrize(
    "exception", [TimeoutError("asyncio timeout"), RedisError("Redis connection lost")]
)
async def test_create_otp_redis_or_timeout_error(otp_service, mock_redis, exception):
    """Тест: Ошибка FailedCreateOTPException при таймауте или проблемах с Redis."""
    key = "otp:fail"

    mock_redis.set.side_effect = exception

    with pytest.raises(FailedCreateOTPException):
        await otp_service._create_otp(key=key)
