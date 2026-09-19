import datetime
import uuid

import jwt
import pytest

# Замени на реальные пути импорта, если требуется


def test_create_refresh_token_success(session_service, mock_config, mocker):
    """Тест: Успешная генерация refresh токена, правильное формирование payload."""
    user_id = uuid.uuid4()

    mock_jwt_encode = mocker.patch(
        "src.services.session_service.jwt.encode", return_value="mocked.jwt.token"
    )

    token, jti, expire = session_service._create_refresh_token(user_id=user_id)

    assert token == "mocked.jwt.token"
    assert isinstance(jti, uuid.UUID)
    assert isinstance(expire, datetime.datetime)

    expected_payload = {
        "sub": str(user_id),
        "jti": str(jti),
        "exp": expire,
        "type": "refresh",
    }
    mock_jwt_encode.assert_called_once_with(
        payload=expected_payload,
        key=mock_config.SECRET_KEY,
        algorithm=mock_config.ALGORITHM,
    )


def test_create_refresh_token_encoding_error(session_service, mock_config, mocker):
    """Тест: Провал при ошибке кодирования (например, если передан невалидный секрет).
    Метод не должен проглатывать ошибку библиотеки.
    """
    user_id = uuid.uuid4()

    mocker.patch(
        "src.services.session_service.jwt.encode",
        side_effect=jwt.PyJWTError("Encoding failed"),
    )

    with pytest.raises(jwt.PyJWTError):
        session_service._create_refresh_token(user_id=user_id)
