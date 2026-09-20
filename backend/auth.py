from database.database import get_connection


def register(name, email, password, role):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, password, role)
        )

        connection.commit()
        return True, "Registration successful!"

    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            return False, "Email already exists!"

        return False, str(error)

    finally:
        connection.close()


def login(email, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ? AND password = ?
        """,
        (email, password)
    )

    user = cursor.fetchone()

    connection.close()

    if user:
        return True, user

    return False, None