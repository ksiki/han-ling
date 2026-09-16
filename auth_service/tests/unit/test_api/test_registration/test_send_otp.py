async def test_send_otp_success(
    unit_client, mock_registration_cases, mock_send_email
) -> None:
    payload = {
        "email": "test@example.com",
        "password": "StrongPassword123!",
        "captcha_token": "valid_turnstile_token",
    }

    response = await unit_client.post("/register/send-otp", json=payload)

    assert response.status_code == 200

    mock_registration_cases.begin_registration.assert_awaited_once_with(
        captcha_token=payload["captcha_token"],
        email=payload["email"],
        password=payload["password"],
    )

    mock_send_email.assert_called_once_with(
        email_to=payload["email"],
        otp_code="123456",
    )


async def test_send_otp_invalid_email(
    unit_client, mock_registration_cases, mock_send_email
) -> None:
    payload = {
        "email": "invalid-email-format",
        "password": "StrongPassword123!",
        "captcha_token": "valid_token",
    }

    response = await unit_client.post("/register/send-otp", json=payload)

    assert response.status_code == 422

    mock_registration_cases.begin_registration.assert_not_awaited()
    mock_send_email.assert_not_called()
