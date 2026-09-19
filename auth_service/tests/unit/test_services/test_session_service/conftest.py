import pytest


@pytest.fixture
def mock_config(mocker):
    mock_config = mocker.patch("src.services.session_service.config")
    mock_config.REFRESH_TOKEN_EXPIRE_DAYS = 30
    mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 15
    mock_config.SECRET_KEY = "test_secret"
    mock_config.ALGORITHM = "HS256"
    mock_config.MAX_ACTIVE_SESSIONS = 3
    return mock_config
