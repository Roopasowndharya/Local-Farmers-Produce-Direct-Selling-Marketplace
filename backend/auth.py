import sqlite3
import os

# Get absolute path to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path
DB_PATH = os.path.join(BASE_DIR, "database", "farmers.db")


def register(user_id, name, email, password, role):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (user_id, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, email, password, role)
        )

        connection.commit()
        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return False, "Email or User ID already exists!"

    finally:
        connection.close()


def login(email, password):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, password)
    )

    user = cursor.fetchone()
    connection.close()

    if user:
        return True, user

    return False, None