import pytest

# Замените на ваши реальные пути импортов
from shared.exceptions import InvalidTokenException

from src.api.dependencies import token_payload_verifier


def dummy_getter() -> None:
    """
    Фиктивная функция для передачи в фабрику.
    В юнит-тесте FastAPI не вызывает этот геттер, поэтому его реализация не важна.
    """


async def test_token_payload_verifier_success(mocker) -> None:
    expected_payload = {"sub": "12345", "jti": "fake-uuid"}
    expected_type = "access"
    test_token = "ey...valid_token...signature"

    mock_verify = mocker.patch("src.api.dependencies.verify_token")
    mock_verify.return_value = expected_payload

    verifier_dependency = token_payload_verifier(
        token_getter=dummy_getter, expected_type=expected_type
    )

    result_payload = await verifier_dependency(raw_token=test_token)

    assert result_payload == expected_payload

    mock_verify.assert_called_once_with(token=test_token, expected_type=expected_type)


async def test_token_payload_verifier_invalid_token(mocker) -> None:
    expected_type = "refresh"
    test_token = "invalid_or_expired_token_string"

    mock_verify = mocker.patch("src.api.dependencies.verify_token")
    mock_verify.side_effect = InvalidTokenException()

    verifier_dependency = token_payload_verifier(
        token_getter=dummy_getter, expected_type=expected_type
    )

    with pytest.raises(InvalidTokenException):
        await verifier_dependency(raw_token=test_token)

    mock_verify.assert_called_once_with(token=test_token, expected_type=expected_type)
