import os
import sys
import uuid

# Get the project root
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, BASE_DIR)

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.utils import secure_filename
from supabase import create_client

from backend.auth import register, login

from backend.farmer import (
    add_product,
    view_products,
    view_farmer_products,
    update_product_image,
    get_product_by_id,
    get_farmer_orders,
    update_order_status
)

from backend.customer import (
    create_order,
    get_customer_orders,
    get_order_items
)

from database.database import create_tables


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

create_tables()


# Secret key for session
app.secret_key = "local_farmers_marketplace_secret_key"


# =========================================================
# SUPABASE STORAGE CONFIGURATION
# =========================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL environment variable is not set."
    )

if not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_KEY environment variable is not set."
    )


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

STORAGE_BUCKET = "product-images"


# =========================================================
# ALLOWED IMAGE FILE TYPES
# =========================================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# SUPABASE IMAGE UPLOAD
# =========================================================

def upload_product_image(image):
    """
    Upload a product image to Supabase Storage.

    Returns:
        (True, public_url)
        or
        (False, error_message)
    """

    if not image or image.filename == "":
        return False, "Please select a product image!"

    if not allowed_file(image.filename):
        return (
            False,
            "Invalid image type! "
            "Use JPG, JPEG, PNG or WEBP."
        )

    try:

        # Secure the original filename
        original_filename = secure_filename(
            image.filename
        )

        # Get file extension
        extension = original_filename.rsplit(
            ".",
            1
        )[1].lower()

        # Create a unique filename
        unique_filename = (
            str(uuid.uuid4())
            + "."
            + extension
        )

        # Read image into memory
        image_bytes = image.read()

        if not image_bytes:
            return False, "The selected image is empty."

        # Upload to Supabase Storage
        supabase.storage.from_(
            STORAGE_BUCKET
        ).upload(
            path=unique_filename,
            file=image_bytes,
            file_options={
                "content-type": image.content_type
                or "application/octet-stream",
                "cache-control": "3600",
                "upsert": "false"
            }
        )

        # Generate public URL
        public_url = (
            supabase.storage
            .from_(STORAGE_BUCKET)
            .get_public_url(
                unique_filename
            )
        )

        return True, public_url

    except Exception as error:

        return (
            False,
            f"Image upload failed: {error}"
        )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# REGISTER PAGE
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register_page():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        success, message = register(
            name,
            email,
            password,
            role
        )

        if success:
            return render_template(
                "registration_success.html"
            )

        return message

    return render_template("register.html")


# =========================================================
# LOGIN PAGE
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login_page():

    error = None

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        success, user = login(
            email,
            password
        )

        if success:

            session["user_id"] = user[0]
            session["name"] = user[1]
            session["role"] = user[4]

            # Create empty cart for the user
            if "cart" not in session:
                session["cart"] = {}

            return redirect(
                url_for("dashboard")
            )

        error = (
            "Invalid email or password. "
            "Please try again."
        )

    return render_template(
        "login.html",
        error=error
    )


# =========================================================
# DASHBOARD PAGE
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    return render_template(
        "dashboard.html",
        name=session["name"],
        role=session["role"]
    )


# =========================================================
# ADD PRODUCT PAGE
# =========================================================

@app.route("/add-product", methods=["GET", "POST"])
def add_product_page():

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    # Only farmers can add products
    if session["role"].lower() != "farmer":
        return "Only farmers can add products."

    if request.method == "POST":

        product_name = request.form["product_name"]
        category = request.form["category"]

        price = float(
            request.form["price"]
        )

        quantity = int(
            request.form["quantity"]
        )

        unit = request.form["unit"]

        image = request.files.get("image")

        # Upload image to Supabase Storage
        success, image_result = upload_product_image(
            image
        )

        if not success:
            return image_result

        # image_result is now the Supabase public URL
        image_url = image_result

        # Farmer ID comes automatically
        # from the logged-in user
        farmer_id = session["user_id"]

        success, message = add_product(
            product_name,
            category,
            price,
            quantity,
            unit,
            farmer_id,
            image_url
        )

        if success:
            return redirect(
                url_for("products_page")
            )

        return message

    return render_template(
        "add_product.html"
    )


# =========================================================
# BROWSE PRODUCTS PAGE
# =========================================================

@app.route("/products")
def products_page():

    products = view_products()

    return render_template(
        "products.html",
        products=products
    )


# =========================================================
# PRODUCT DETAILS PAGE
# =========================================================

@app.route("/product/<int:product_id>")
def product_details(product_id):

    product = get_product_by_id(
        product_id
    )

    if not product:
        return "Product not found!", 404

    return render_template(
        "product_details.html",
        product=product
    )


# =========================================================
# ADD TO CART
# =========================================================

@app.route(
    "/add-to-cart/<int:product_id>",
    methods=["POST"]
)
def add_to_cart(product_id):

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    if session["role"].lower() != "customer":
        return "Only customers can add products to cart."

    product = get_product_by_id(
        product_id
    )

    if not product:
        return "Product not found!", 404

    if product[4] <= 0:
        return "This product is currently out of stock."

    cart = session.get(
        "cart",
        {}
    )

    product_key = str(product_id)

    current_quantity = cart.get(
        product_key,
        0
    )

    if current_quantity >= product[4]:
        return (
            "You cannot add more than the "
            "available quantity."
        )

    cart[product_key] = current_quantity + 1

    session["cart"] = cart
    session.modified = True

    return redirect(
        url_for("cart_page")
    )


# =========================================================
# INCREASE CART QUANTITY
# =========================================================

@app.route(
    "/increase-cart/<int:product_id>",
    methods=["POST"]
)
def increase_cart(product_id):

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    if session["role"].lower() != "customer":
        return "Only customers can manage the cart."

    product = get_product_by_id(
        product_id
    )

    if not product:
        return "Product not found!", 404

    cart = session.get(
        "cart",
        {}
    )

    product_key = str(product_id)

    current_quantity = cart.get(
        product_key,
        0
    )

    if current_quantity >= product[4]:
        return (
            "You cannot add more than the "
            "available quantity."
        )

    cart[product_key] = current_quantity + 1

    session["cart"] = cart
    session.modified = True

    return redirect(
        url_for("cart_page")
    )


# =========================================================
# DECREASE CART QUANTITY
# =========================================================

@app.route(
    "/decrease-cart/<int:product_id>",
    methods=["POST"]
)
def decrease_cart(product_id):

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    if session["role"].lower() != "customer":
        return "Only customers can manage the cart."

    cart = session.get(
        "cart",
        {}
    )

    product_key = str(product_id)

    if product_key not in cart:
        return redirect(
            url_for("cart_page")
        )

    cart[product_key] -= 1

    if cart[product_key] <= 0:
        del cart[product_key]

    session["cart"] = cart
    session.modified = True

    return redirect(
        url_for("cart_page")
    )


# =========================================================
# REMOVE ITEM FROM CART
# =========================================================

@app.route(
    "/remove-from-cart/<int:product_id>",
    methods=["POST"]
)
def remove_from_cart(product_id):

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    if session["role"].lower() != "customer":
        return "Only customers can manage the cart."

    cart = session.get(
        "cart",
        {}
    )

    product_key = str(product_id)

    if product_key in cart:
        del cart[product_key]

    session["cart"] = cart
    session.modified = True

    return redirect(
        url_for("cart_page")
    )


# =========================================================
# CART PAGE
# =========================================================

@app.route("/cart")
def cart_page():

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    if session["role"].lower() != "customer":
        return "Only customers can access the cart."

    cart = session.get(
        "cart",
        {}
    )

    cart_items = []
    total_amount = 0

    for product_id, cart_quantity in cart.items():

        product = get_product_by_id(
            int(product_id)
        )

        if product:

            available_quantity = product[4]

            if cart_quantity > available_quantity:

                cart_quantity = available_quantity
                cart[product_id] = available_quantity

            subtotal = (
                product[3] * cart_quantity
            )

            cart_items.append({
                "product": product,
                "quantity": cart_quantity,
                "subtotal": subtotal
            })

            total_amount += subtotal

    session["cart"] = cart
    session.modified = True

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_amount=total_amount
    )


# =========================================================
# CHECKOUT / PLACE ORDER
# =========================================================

@app.route(
    "/checkout",
    methods=["POST"]
)
def checkout():

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    if session["role"].lower() != "customer":
        return "Only customers can place orders."

    cart = session.get(
        "cart",
        {}
    )

    if not cart:
        return "Your cart is empty!"

    cart_items = []

    for product_id, quantity in cart.items():

        cart_items.append({
            "product_id": int(product_id),
            "quantity": int(quantity)
        })

    success, message, order_id = create_order(
        session["user_id"],
        cart_items
    )

    if not success:
        return message

    session["cart"] = {}
    session.modified = True

    return render_template(
        "order_success.html",
        order_id=order_id,
        message=message
    )


# =========================================================
# CUSTOMER ORDERS
# =========================================================

@app.route("/orders")
def orders_page():

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    if session["role"].lower() != "customer":
        return "Only customers can view orders."

    customer_id = session["user_id"]

    orders = get_customer_orders(
        customer_id
    )

    return render_template(
        "orders.html",
        orders=orders
    )


# =========================================================
# ORDER DETAILS
# =========================================================

@app.route("/order/<int:order_id>")
def order_details(order_id):

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    if session["role"].lower() != "customer":
        return "Only customers can view order details."

    customer_id = session["user_id"]

    orders = get_customer_orders(
        customer_id
    )

    customer_order_ids = [
        order[0]
        for order in orders
    ]

    if order_id not in customer_order_ids:
        return "Order not found!", 404

    items = get_order_items(
        order_id
    )

    selected_order = None

    for order in orders:

        if order[0] == order_id:
            selected_order = order
            break

    return render_template(
        "order_details.html",
        order=selected_order,
        items=items
    )


# =========================================================
# FARMER ORDERS
# =========================================================

@app.route("/farmer-orders")
def farmer_orders_page():

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    # Only farmers can view farmer orders
    if session["role"].lower() != "farmer":
        return "Only farmers can view farmer orders."

    farmer_id = session["user_id"]

    orders = get_farmer_orders(
        farmer_id
    )

    return render_template(
        "farmer_orders.html",
        orders=orders
    )


# =========================================================
# UPDATE FARMER ORDER STATUS
# =========================================================

@app.route(
    "/update-order-status/<int:order_id>",
    methods=["POST"]
)
def update_farmer_order_status(order_id):

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    # Only farmers can update order status
    if session["role"].lower() != "farmer":
        return "Only farmers can update order status."

    status = request.form.get("status")

    allowed_statuses = {
        "Pending",
        "Accepted",
        "Ready",
        "Completed"
    }

    if status not in allowed_statuses:
        return "Invalid order status."

    farmer_id = session["user_id"]

    success, message = update_order_status(
        order_id,
        farmer_id,
        status
    )

    if not success:
        return message, 404

    return redirect(
        url_for("farmer_orders_page")
    )


# =========================================================
# MY PRODUCTS PAGE
# =========================================================

@app.route("/my-products")
def my_products_page():

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    if session["role"].lower() != "farmer":
        return "Only farmers can manage products."

    farmer_id = session["user_id"]

    products = view_farmer_products(
        farmer_id
    )

    return render_template(
        "my_products.html",
        products=products
    )


# =========================================================
# UPDATE PRODUCT PHOTO
# =========================================================

@app.route(
    "/update-product-photo/<int:product_id>",
    methods=["GET", "POST"]
)
def update_product_photo(product_id):

    if "user_id" not in session:
        return redirect(
            url_for("login_page")
        )

    if session["role"].lower() != "farmer":
        return "Only farmers can update product photos."

    if request.method == "POST":

        image = request.files.get("image")

        # Upload image to Supabase Storage
        success, image_result = upload_product_image(
            image
        )

        if not success:
            return image_result

        # image_result is the Supabase public URL
        image_url = image_result

        farmer_id = session["user_id"]

        success, message = update_product_image(
            product_id,
            farmer_id,
            image_url
        )

        if success:
            return redirect(
                url_for("my_products_page")
            )

        return message

    return render_template(
        "update_product_photo.html",
        product_id=product_id
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# START FLASK APPLICATION
# =========================================================

if __name__ == "__main__":

    create_tables()

    app.run(
        debug=True
    )