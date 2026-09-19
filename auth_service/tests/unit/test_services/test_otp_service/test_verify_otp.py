import json

import pytest
from redis.exceptions import RedisError

from src.core.exceptions import OTPAttemptsExceededException, OTPInvalidException
from src.services import OTPTypeEnum


async def test_verify_otp_success(otp_service, mock_redis, mocker):
    """Тест: Успешная валидация кода, ключ удаляется из Redis."""
    email = "test@example.com"
    otp_type = OTPTypeEnum.REG
    valid_otp = "123456"
    key = otp_service._make_key(otp_type, email)

    payload = {"otp": valid_otp, "attempts": 0, "some_data": "value"}
    mocker.patch.object(otp_service, "_get_payload", return_value=payload)

    result = await otp_service._verify_otp(email=email, otp=valid_otp, type=otp_type)

    assert result == payload
    mock_redis.delete.assert_called_once_with(key)


async def test_verify_otp_invalid_code_increments_attempts(
    otp_service, mock_redis, mocker
):
    """Тест: Неверный код инкрементирует счетчик попыток и обновляет TTL в Redis."""
    email = "test@example.com"
    otp_type = OTPTypeEnum.RESET
    wrong_otp = "000000"
    key = otp_service._make_key(otp_type, email)

    payload = {"otp": "123456", "attempts": 1}
    mocker.patch.object(otp_service, "_get_payload", return_value=payload.copy())

    mock_config = mocker.patch("src.services.otp_service.config")
    mock_config.MAX_OTP_ATTEMPTS = 3

    mock_redis.ttl.return_value = 200

    with pytest.raises(OTPInvalidException):
        await otp_service._verify_otp(email=email, otp=wrong_otp, type=otp_type)

    expected_updated_payload = {"otp": "123456", "attempts": 2}

    mock_redis.ttl.assert_called_once_with(key)
    mock_redis.set.assert_called_once_with(
        key, json.dumps(expected_updated_payload), ex=200
    )


async def test_verify_otp_attempts_exceeded(otp_service, mock_redis, mocker):
    """Тест: Ошибка OTPAttemptsExceededException, если превышен лимит попыток."""
    email = "test@example.com"
    otp_type = OTPTypeEnum.REG
    wrong_otp = "000000"
    key = otp_service._make_key(otp_type, email)

    payload = {"otp": "123456", "attempts": 2}
    mocker.patch.object(otp_service, "_get_payload", return_value=payload)

    mock_config = mocker.patch("src.services.otp_service.config")
    mock_config.MAX_OTP_ATTEMPTS = 3

    with pytest.raises(OTPAttemptsExceededException):
        await otp_service._verify_otp(email=email, otp=wrong_otp, type=otp_type)

    mock_redis.delete.assert_called_once_with(key)
    mock_redis.set.assert_not_called()


async def test_verify_otp_redis_error_handling(otp_service, mock_redis, mocker):
    """Тест: Перехват RedisError и преобразование его в OTPInvalidException."""
    email = "test@example.com"
    otp_type = OTPTypeEnum.REG
    valid_otp = "123456"

    payload = {"otp": valid_otp, "attempts": 0}
    mocker.patch.object(otp_service, "_get_payload", return_value=payload)

    mock_redis.delete.side_effect = RedisError("Connection drops")

    with pytest.raises(OTPInvalidException):
        await otp_service._verify_otp(email=email, otp=valid_otp, type=otp_type)
