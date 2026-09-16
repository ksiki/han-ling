from unittest.mock import ANY

import pytest


async def test_confirm_success(
    unit_client, mock_password_recovery_cases, mock_set_auth_cookies_password_recovery
) -> None:
    payload = {
        "email": "test@example.com",
        "otp": "123456",
        "new_password": "NewStrongPassword",
    }
    headers = {
        "X-Forwarded-For": "203.0.113.195",
        "User-Agent": "My-Test-Agent/1.0",
    }

    response = await unit_client.post(
        "/password-reset/confirm", json=payload, headers=headers
    )

    assert response.status_code == 200

    mock_password_recovery_cases.finish_password_recovery.assert_awaited_once_with(
        email=payload["email"],
        otp=payload["otp"],
        new_password=payload["new_password"],
        ip="203.0.113.195",
        user_agent="My-Test-Agent/1.0",
    )

    mock_set_auth_cookies_password_recovery.assert_called_once_with(
        response=ANY,
        access_token="access_token_template",
        refresh_token="refresh_token_template",
    )


@pytest.mark.parametrize(
    "email, password",
    [
        ("invalid-email", "StrongPassword123!"),
        ("test@example.com", "Strong"),
    ],
)
async def test_verify_invalid_email(
    email,
    password,
    unit_client,
    mock_password_recovery_cases,
    mock_set_auth_cookies_password_recovery,
) -> None:
    payload = {
        "email": email,
        "otp": "12345",
        "new_password": password,
    }

    response = await unit_client.post("/password-reset/confirm", json=payload)

    assert response.status_code == 422

    mock_password_recovery_cases.begin_registration.assert_not_awaited()
    mock_set_auth_cookies_password_recovery.assert_not_called()
