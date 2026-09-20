import os
import sys
import uuid

# Get the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from backend.auth import register, login
from backend.farmer import (
    add_product,
    view_products,
    view_farmer_products,
    update_product_image,
    get_product_by_id
)
from database.database import create_tables


app = Flask(__name__)


# Secret key for session
app.secret_key = "local_farmers_marketplace_secret_key"


# Product image upload folder
UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "Frontend",
    "static",
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Allowed image file types
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
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


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

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN PAGE
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login_page():

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

        return "Invalid email or password!"

    return render_template(
        "login.html"
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

        # Get selected unit
        unit = request.form["unit"]

        # Get uploaded image
        image = request.files.get("image")

        # Check image
        if not image or image.filename == "":

            return "Please select a product image!"

        # Check image type
        if not allowed_file(image.filename):

            return (
                "Invalid image type! "
                "Use JPG, JPEG, PNG or WEBP."
            )

        # Create uploads folder
        os.makedirs(
            app.config["UPLOAD_FOLDER"],
            exist_ok=True
        )

        # Make filename safe
        original_filename = secure_filename(
            image.filename
        )

        extension = original_filename.rsplit(
            ".",
            1
        )[1].lower()

        # Create unique filename
        unique_filename = (
            str(uuid.uuid4())
            + "."
            + extension
        )

        # Save image
        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            unique_filename
        )

        image.save(
            image_path
        )

        # Farmer ID comes automatically
        # from the logged-in user
        farmer_id = session["user_id"]

        # Save product
        success, message = add_product(
            product_name,
            category,
            price,
            quantity,
            unit,
            farmer_id,
            unique_filename
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

    # User must be logged in
    if "user_id" not in session:

        return redirect(
            url_for("login_page")
        )

    # Only customers can add products
    if session["role"].lower() != "customer":

        return "Only customers can add products to cart."

    # Check product
    product = get_product_by_id(
        product_id
    )

    if not product:

        return "Product not found!", 404

    # Product positions:
    # product[4] = quantity
    # product[5] = unit
    # product[6] = farmer_id
    # product[7] = image

    # Check stock
    if product[4] <= 0:

        return "This product is currently out of stock."

    # Get current cart
    cart = session.get(
        "cart",
        {}
    )

    product_key = str(product_id)

    # Current quantity already in cart
    current_quantity = cart.get(
        product_key,
        0
    )

    # Prevent adding more than available stock
    if current_quantity >= product[4]:

        return (
            "You cannot add more than the "
            "available quantity."
        )

    # Add one quantity
    cart[product_key] = current_quantity + 1

    # Save cart
    session["cart"] = cart
    session.modified = True

    # Go directly to Cart page
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

    # User must be logged in
    if "user_id" not in session:

        return redirect(
            url_for("login_page")
        )

    # Only customers
    if session["role"].lower() != "customer":

        return "Only customers can manage the cart."

    # Get product
    product = get_product_by_id(
        product_id
    )

    if not product:

        return "Product not found!", 404

    # Get cart
    cart = session.get(
        "cart",
        {}
    )

    product_key = str(product_id)

    current_quantity = cart.get(
        product_key,
        0
    )

    # Check stock limit
    if current_quantity >= product[4]:

        return (
            "You cannot add more than the "
            "available quantity."
        )

    # Increase quantity
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

    # User must be logged in
    if "user_id" not in session:

        return redirect(
            url_for("login_page")
        )

    # Only customers
    if session["role"].lower() != "customer":

        return "Only customers can manage the cart."

    cart = session.get(
        "cart",
        {}
    )

    product_key = str(product_id)

    # Check whether product exists in cart
    if product_key not in cart:

        return redirect(
            url_for("cart_page")
        )

    # Decrease quantity
    cart[product_key] -= 1

    # Remove product when quantity reaches zero
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

    # User must be logged in
    if "user_id" not in session:

        return redirect(
            url_for("login_page")
        )

    # Only customers
    if session["role"].lower() != "customer":

        return "Only customers can manage the cart."

    cart = session.get(
        "cart",
        {}
    )

    product_key = str(product_id)

    # Remove product
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

    # User must be logged in
    if "user_id" not in session:

        return redirect(
            url_for("login_page")
        )

    # Only customers
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

            # Product positions:
            # product[3] = price
            # product[4] = quantity
            # product[5] = unit
            # product[7] = image

            # Prevent cart quantity from exceeding stock
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

    # Save corrected cart
    session["cart"] = cart
    session.modified = True

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total_amount=total_amount
    )


# =========================================================
# MY PRODUCTS PAGE
# =========================================================

@app.route("/my-products")
def my_products_page():

    # User must be logged in
    if "user_id" not in session:

        return redirect(
            url_for("login_page")
        )

    # Only farmers
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

    # User must be logged in
    if "user_id" not in session:

        return redirect(
            url_for("login_page")
        )

    # Only farmers
    if session["role"].lower() != "farmer":

        return "Only farmers can update product photos."

    if request.method == "POST":

        image = request.files.get("image")

        if not image or image.filename == "":

            return "Please select a product image!"

        if not allowed_file(image.filename):

            return (
                "Invalid image type! "
                "Use JPG, JPEG, PNG or WEBP."
            )

        os.makedirs(
            app.config["UPLOAD_FOLDER"],
            exist_ok=True
        )

        original_filename = secure_filename(
            image.filename
        )

        extension = original_filename.rsplit(
            ".",
            1
        )[1].lower()

        unique_filename = (
            str(uuid.uuid4())
            + "."
            + extension
        )

        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            unique_filename
        )

        image.save(
            image_path
        )

        farmer_id = session["user_id"]

        success, message = update_product_image(
            product_id,
            farmer_id,
            unique_filename
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

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )

    app.run(
        debug=True
    )