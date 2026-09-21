import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    """
    Create and return a PostgreSQL connection using
    the DATABASE_URL environment variable.
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    connection = psycopg2.connect(database_url)

    return connection


def create_tables():
    """
    Tables are already created in Supabase.
    This function is kept so existing imports in the
    Flask application do not break.
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