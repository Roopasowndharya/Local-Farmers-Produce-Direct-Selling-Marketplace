from database.database import get_connection


def view_products():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
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

        return products

    finally:
        connection.close()


def search_product(search_name):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
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
                WHERE product_name ILIKE %s
            """, (f"%{search_name}%",))

            products = cursor.fetchall()

        return products

    finally:
        connection.close()


def create_order(customer_id, cart_items):
    """
    Creates an order from the customer's cart.

    cart_items format:
    [
        {
            "product_id": 1,
            "quantity": 2
        }
    ]
    """

    if not cart_items:
        return False, "Your cart is empty!", None

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            total_amount = 0
            verified_items = []

            for item in cart_items:

                product_id = item["product_id"]
                requested_quantity = item["quantity"]

                cursor.execute("""
                    SELECT
                        product_id,
                        product_name,
                        price,
                        quantity,
                        farmer_id
                    FROM products
                    WHERE product_id = %s
                """, (product_id,))

                product = cursor.fetchone()

                if not product:
                    connection.rollback()
                    return (
                        False,
                        "One of the products is no longer available.",
                        None
                    )

                available_quantity = product[3]

                if requested_quantity <= 0:
                    connection.rollback()
                    return False, "Invalid product quantity.", None

                if requested_quantity > available_quantity:
                    connection.rollback()
                    return (
                        False,
                        f"Not enough stock available for {product[1]}.",
                        None
                    )

                subtotal = product[2] * requested_quantity
                total_amount += subtotal

                verified_items.append({
                    "product_id": product[0],
                    "quantity": requested_quantity,
                    "price": product[2]
                })

            cursor.execute("""
                INSERT INTO orders
                (
                    customer_id,
                    total_amount,
                    status
                )
                VALUES (%s, %s, %s)
                RETURNING id
            """, (customer_id, total_amount, "Pending"))

            order_id = cursor.fetchone()[0]

            for item in verified_items:

                cursor.execute("""
                    INSERT INTO order_items
                    (
                        order_id,
                        product_id,
                        quantity,
                        price
                    )
                    VALUES (%s, %s, %s, %s)
                """, (
                    order_id,
                    item["product_id"],
                    item["quantity"],
                    item["price"]
                ))

                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity - %s
                    WHERE product_id = %s
                """, (
                    item["quantity"],
                    item["product_id"]
                ))

        connection.commit()

        return True, "Order placed successfully!", order_id

    except Exception as error:
        connection.rollback()
        return False, str(error), None

    finally:
        connection.close()


def get_customer_orders(customer_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    total_amount,
                    status,
                    created_at
                FROM orders
                WHERE customer_id = %s
                ORDER BY id DESC
            """, (customer_id,))

            orders = cursor.fetchall()

        return orders

    finally:
        connection.close()


def get_order_items(order_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    order_items.id,
                    order_items.product_id,
                    products.product_name,
                    order_items.quantity,
                    order_items.price,
                    products.unit,
                    products.image
                FROM order_items
                JOIN products
                    ON order_items.product_id = products.product_id
                WHERE order_items.order_id = %s
            """, (order_id,))

            items = cursor.fetchall()

        return items

    finally:
        connection.close()