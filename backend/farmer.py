import sqlite3


DB_PATH = "database/farmers.db"


def add_product(product_name, category, price, quantity, unit, farmer_id, image):
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


def view_products():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
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
        """
    )

    products = cursor.fetchall()
    connection.close()

    return products


def view_farmer_products(farmer_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
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
        """,
        (farmer_id,)
    )

    products = cursor.fetchall()
    connection.close()

    return products


def update_product_image(product_id, farmer_id, image):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE products
            SET image = ?
            WHERE product_id = ?
            AND farmer_id = ?
            """,
            (
                image,
                product_id,
                farmer_id
            )
        )

        connection.commit()

        if cursor.rowcount == 0:
            return False, "Product not found!"

        return True, "Product photo updated successfully!"

    except sqlite3.Error as e:
        return False, str(e)

    finally:
        connection.close()


def get_product_by_id(product_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
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
        """,
        (product_id,)
    )

    product = cursor.fetchone()
    connection.close()

    return product


def get_farmer_orders(farmer_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            orders.id,
            users.name,
            users.email,
            products.product_name,
            order_items.quantity,
            order_items.price,
            products.unit,
            (order_items.quantity * order_items.price) AS farmer_product_total,
            orders.status,
            orders.created_at,
            products.image
        FROM orders
        JOIN users
            ON orders.customer_id = users.id
        JOIN order_items
            ON orders.id = order_items.order_id
        JOIN products
            ON order_items.product_id = products.product_id
        WHERE products.farmer_id = ?
        ORDER BY orders.id DESC
        """,
        (farmer_id,)
    )

    orders = cursor.fetchall()
    connection.close()

    return orders


def update_order_status(order_id, farmer_id, status):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE orders
            SET status = ?
            WHERE id = ?
            AND EXISTS (
                SELECT 1
                FROM order_items
                JOIN products
                    ON order_items.product_id = products.product_id
                WHERE order_items.order_id = orders.id
                AND products.farmer_id = ?
            )
            """,
            (
                status,
                order_id,
                farmer_id
            )
        )

        connection.commit()

        if cursor.rowcount == 0:
            return False, "Order not found!"

        return True, "Order status updated successfully!"

    except sqlite3.Error as e:
        connection.rollback()
        return False, str(e)

    finally:
        connection.close()