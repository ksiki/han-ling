async def test_resend_otp_success(
    unit_client, mock_registration_cases, mock_send_email
) -> None:
    payload = {
        "email": "test@example.com",
    }

    response = await unit_client.post("/register/resend-otp", json=payload)

    assert response.status_code == 200

    mock_registration_cases.resend_otp.assert_awaited_once_with(email=payload["email"])

    mock_send_email.assert_called_once_with(
        email_to=payload["email"],
        otp_code="654321",
    )


async def test_resend_otp_invalid_email(
    unit_client, mock_registration_cases, mock_send_email
) -> None:
    payload = {
        "email": "invalid-email-format",
    }

    response = await unit_client.post("/register/resend-otp", json=payload)

    assert response.status_code == 422

    mock_registration_cases.resend_otp.assert_not_awaited()
    mock_send_email.assert_not_called()
