import os
import psycopg2


def get_connection():
    """
    Create and return a PostgreSQL connection using
    the DATABASE_URL environment variable.
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set."
        )

    connection = psycopg2.connect(
        database_url,
        connect_timeout=10
    )

    return connection


def create_tables():
    """
    Verify that the Supabase PostgreSQL database
    is reachable.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")

        connection.commit()

        print("Supabase PostgreSQL connection successful!")

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()