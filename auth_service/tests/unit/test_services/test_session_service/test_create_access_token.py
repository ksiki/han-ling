import datetime
import uuid

import jwt
import pytest


def test_create_access_token_success(session_service, mock_config, mocker):
    """Тест: Успешная генерация access токена, правильное формирование payload."""
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    user_role = "admin"

    mock_jwt_encode = mocker.patch(
        "src.services.session_service.jwt.encode", return_value="mocked.access.token"
    )

    token = session_service.create_access_token(
        user_id=user_id, session_id=session_id, user_role=user_role
    )

    assert token == "mocked.access.token"
    mock_jwt_encode.assert_called_once()

    called_kwargs = mock_jwt_encode.call_args.kwargs
    payload = called_kwargs["payload"]

    assert called_kwargs["key"] == mock_config.SECRET_KEY
    assert called_kwargs["algorithm"] == mock_config.ALGORITHM
    assert payload["sub"] == str(user_id)
    assert payload["session_id"] == str(session_id)
    assert payload["role"] == user_role
    assert payload["type"] == "access"

    assert isinstance(payload["exp"], datetime.datetime)
    assert isinstance(uuid.UUID(payload["jti"]), uuid.UUID)


def test_create_access_token_encoding_error(session_service, mock_config, mocker):
    """Тест: Ошибка при кодировании токена пробрасывается наверх."""

    mocker.patch(
        "src.services.session_service.jwt.encode",
        side_effect=jwt.PyJWTError("Access token encoding failed"),
    )

    with pytest.raises(jwt.PyJWTError) as exc_info:
        session_service.create_access_token(
            user_id=uuid.uuid4(), session_id=uuid.uuid4(), user_role="user"
        )

    assert str(exc_info.value) == "Access token encoding failed"
