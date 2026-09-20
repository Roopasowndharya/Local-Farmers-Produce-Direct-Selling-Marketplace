from backend.auth import register, login


def test_login_with_invalid_credentials():
    success, user = login(
        "nonexistent@example.com",
        "wrongpassword"
    )

    assert success is False
    assert user is None