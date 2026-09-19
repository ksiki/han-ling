import json

import pytest

# Замени на реальные пути импорта
from src.core.exceptions import OTPInvalidException


async def test_get_payload_success(otp_service, mock_redis):
    """Тест: Успешное извлечение и десериализация payload из Redis."""
    key = "reg_otp:test@example.com"
    expected_payload = {"otp": "123456", "attempts": 1}

    mock_redis.get.return_value = json.dumps(expected_payload).encode("utf-8")

    # Act
    result = await otp_service._get_payload(key=key)

    # Assert
    assert result == expected_payload
    mock_redis.get.assert_called_once_with(key)


async def test_get_payload_not_found(otp_service, mock_redis):
    """Тест: Ошибка OTPInvalidException, если по ключу ничего не найдено (Redis вернул None)."""
    key = "reg_otp:unknown@example.com"
    mock_redis.get.return_value = None

    with pytest.raises(OTPInvalidException):
        await otp_service._get_payload(key=key)

    mock_redis.get.assert_called_once_with(key)


async def test_get_payload_timeout_error(otp_service, mock_redis):
    """Тест: Проброс TimeoutError, если Redis не ответил вовремя.

    Примечание: Согласно текущему коду, TimeoutError не перехватывается.
    Если код будет изменен на перехват и выброс OTPInvalidException,
    этот тест нужно будет обновить.
    """
    key = "reg_otp:timeout@example.com"
    mock_redis.get.side_effect = TimeoutError("asyncio timeout")

    with pytest.raises(TimeoutError):
        await otp_service._get_payload(key=key)

    mock_redis.get.assert_called_once_with(key)
