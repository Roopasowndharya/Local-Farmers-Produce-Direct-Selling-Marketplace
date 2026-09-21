from database.database import get_connection


def register(name, email, password, role):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, password, role)
            )

        connection.commit()
        return True, "Registration successful!"

    except Exception as error:
        connection.rollback()

        if "duplicate key value violates unique constraint" in str(error):
            return False, "Email already exists!"

        return False, str(error)

    finally:
        connection.close()


def login(email, password):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s AND password = %s
                """,
                (email, password)
            )

            user = cursor.fetchone()

        if user:
            return True, user

        return False, None

    finally:
        connection.close()