from unittest.mock import ANY


async def test_verify_success(
    unit_client, mock_registration_cases, mock_set_auth_cookies_registration
) -> None:
    payload = {
        "email": "test@example.com",
        "otp": "123456",
    }
    headers = {
        "X-Forwarded-For": "203.0.113.195",
        "User-Agent": "My-Test-Agent/1.0",
    }

    response = await unit_client.post("/register/verify", json=payload, headers=headers)

    assert response.status_code == 201

    mock_registration_cases.finish_registration.assert_awaited_once_with(
        email=payload["email"],
        otp=payload["otp"],
        ip="203.0.113.195",
        user_agent="My-Test-Agent/1.0",
    )

    mock_set_auth_cookies_registration.assert_called_once_with(
        response=ANY,
        access_token="access_token_template",
        refresh_token="refresh_token_template",
    )


async def test_verify_invalid_email(
    unit_client, mock_registration_cases, mock_set_auth_cookies_registration
) -> None:
    payload = {
        "email": "test-example.com",
        "otp": "12345",
    }

    response = await unit_client.post("/register/verify", json=payload)

    assert response.status_code == 422

    mock_registration_cases.begin_registration.assert_not_awaited()
    mock_set_auth_cookies_registration.assert_not_called()
