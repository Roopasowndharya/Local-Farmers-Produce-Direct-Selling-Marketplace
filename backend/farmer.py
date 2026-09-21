from database.database import get_connection


def add_product(product_name, category, price, quantity, unit, farmer_id, image):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
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
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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

    except Exception as error:
        connection.rollback()
        return False, str(error)

    finally:
        connection.close()


def view_products():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
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

        return products

    finally:
        connection.close()


def view_farmer_products(farmer_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
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
                WHERE farmer_id = %s
                """,
                (farmer_id,)
            )

            products = cursor.fetchall()

        return products

    finally:
        connection.close()


def update_product_image(product_id, farmer_id, image):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE products
                SET image = %s
                WHERE product_id = %s
                AND farmer_id = %s
                """,
                (
                    image,
                    product_id,
                    farmer_id
                )
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return False, "Product not found!"

        connection.commit()
        return True, "Product photo updated successfully!"

    except Exception as error:
        connection.rollback()
        return False, str(error)

    finally:
        connection.close()


def get_product_by_id(product_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
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
                WHERE product_id = %s
                """,
                (product_id,)
            )

            product = cursor.fetchone()

        return product

    finally:
        connection.close()


def get_farmer_orders(farmer_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
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
                WHERE products.farmer_id = %s
                ORDER BY orders.id DESC
                """,
                (farmer_id,)
            )

            orders = cursor.fetchall()

        return orders

    finally:
        connection.close()


def update_order_status(order_id, farmer_id, status):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE orders
                SET status = %s
                WHERE id = %s
                AND EXISTS (
                    SELECT 1
                    FROM order_items
                    JOIN products
                        ON order_items.product_id = products.product_id
                    WHERE order_items.order_id = orders.id
                    AND products.farmer_id = %s
                )
                """,
                (
                    status,
                    order_id,
                    farmer_id
                )
            )

            if cursor.rowcount == 0:
                connection.rollback()
                return False, "Order not found!"

        connection.commit()
        return True, "Order status updated successfully!"

    except Exception as error:
        connection.rollback()
        return False, str(error)

    finally:
        connection.close()