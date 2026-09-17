import uuid

import pytest
import uuid6
from shared.exceptions import InvalidTokenException

from src.api.dependencies import _safe_extract_uuid


@pytest.mark.parametrize(
    "raw_value",
    [
        pytest.param(str(uuid.uuid4()), id="uuid.uuid4"),
        pytest.param(str(uuid6.uuid7()), id="uuid6.uuid7"),
    ],
)
def test_safe_extract_uuid_success(raw_value) -> None:
    payload = {"sub": raw_value}

    cast_uuid = _safe_extract_uuid(payload=payload, key="sub")

    assert isinstance(cast_uuid, uuid.UUID)
    assert str(cast_uuid) == raw_value


@pytest.mark.parametrize(
    "payload, expected_key",
    [
        pytest.param({"sub": "invalid-uuid-string"}, "sub", id="bad_format"),
        pytest.param({"sub": ""}, "sub", id="empty_string"),
        pytest.param({"sub": 12345}, "sub", id="wrong_type"),
        pytest.param({"other_key": str(uuid.uuid4())}, "sub", id="missing_key"),
    ],
)
def test_safe_extract_uuid_failed(payload, expected_key) -> None:
    with pytest.raises(InvalidTokenException):
        _safe_extract_uuid(payload=payload, key=expected_key)
