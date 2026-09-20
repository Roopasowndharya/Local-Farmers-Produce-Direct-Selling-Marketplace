from backend.auth import register, login
from database.database import create_tables


def test_login_with_invalid_credentials():
    create_tables()

    success, user = login(
        "nonexistent@example.com",
        "wrongpassword"
    )

    assert success is False
    assert user is None