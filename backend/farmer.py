import os
import sqlite3

# Get project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path
DB_PATH = os.path.join(BASE_DIR, "database", "farmers.db")


# =========================================================
# ADD PRODUCT
# =========================================================

def add_product(
    product_name,
    category,
    price,
    quantity,
    unit,
    farmer_id,
    image
):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO products
            (
                product_name,
                category,
                price,
                quantity,
                unit,
                farmer_id,
                image
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product_name,
                category,
                price,
                quantity,
                unit,
                farmer_id,
                image
            )
        )

        connection.commit()

        return True, "Product added successfully!"

    except sqlite3.IntegrityError as e:
        return False, str(e)

    finally:
        connection.close()


# =========================================================
# VIEW ALL PRODUCTS
# =========================================================

def view_products():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            product_id,
            product_name,
            category,
            price,
            quantity,
            unit,
            farmer_id,
            image
        FROM products
    """)

    products = cursor.fetchall()

    connection.close()

    return products


# =========================================================
# VIEW FARMER PRODUCTS
# =========================================================

def view_farmer_products(farmer_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            product_id,
            product_name,
            category,
            price,
            quantity,
            unit,
            farmer_id,
            image
        FROM products
        WHERE farmer_id = ?
    """, (farmer_id,))

    products = cursor.fetchall()

    connection.close()

    return products


# =========================================================
# UPDATE PRODUCT IMAGE
# =========================================================

def update_product_image(product_id, farmer_id, image):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE products
            SET image = ?
            WHERE product_id = ?
            AND farmer_id = ?
        """, (
            image,
            product_id,
            farmer_id
        ))

        connection.commit()

        if cursor.rowcount == 0:
            return False, "Product not found!"

        return True, "Product photo updated successfully!"

    except sqlite3.Error as e:
        return False, str(e)

    finally:
        connection.close()


# =========================================================
# GET ONE PRODUCT BY ID
# =========================================================

def get_product_by_id(product_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            product_id,
            product_name,
            category,
            price,
            quantity,
            unit,
            farmer_id,
            image
        FROM products
        WHERE product_id = ?
    """, (product_id,))

    product = cursor.fetchone()

    connection.close()

    return product