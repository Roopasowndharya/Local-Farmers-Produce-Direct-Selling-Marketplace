import os
import sqlite3

# Get project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path
DB_PATH = os.path.join(BASE_DIR, "database", "farmers.db")


def add_product(product_id, product_name, category, price, quantity, farmer_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO products
            (product_id, product_name, category, price, quantity, farmer_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                product_id,
                product_name,
                category,
                price,
                quantity,
                farmer_id
            )
        )

        connection.commit()
        return True, "Product added successfully!"

    except sqlite3.IntegrityError:
        return False, "Product ID already exists!"

    finally:
        connection.close()


def view_products():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    connection.close()

    return products