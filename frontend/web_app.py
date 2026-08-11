import os
import sys

# Get the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, request
from backend.auth import register, login
from backend.farmer import add_product, view_products

app = Flask(__name__)


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Register Page
@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        user_id = int(request.form["user_id"])
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        success, message = register(
            user_id,
            name,
            email,
            password,
            role
        )

        return message

    return render_template("register.html")


# Login Page
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        success, user = login(email, password)

        if success:
            return f"Login successful! Welcome {user[1]}"

        return "Invalid email or password!"

    return render_template("login.html")


# Add Product Page
@app.route("/add-product", methods=["GET", "POST"])
def add_product_page():
    if request.method == "POST":
        product_id = int(request.form["product_id"])
        product_name = request.form["product_name"]
        category = request.form["category"]
        price = float(request.form["price"])
        quantity = int(request.form["quantity"])
        farmer_id = int(request.form["farmer_id"])

        success, message = add_product(
            product_id,
            product_name,
            category,
            price,
            quantity,
            farmer_id
        )

        return message

    return render_template("add_product.html")


# Browse Products Page
@app.route("/products")
def products_page():
    products = view_products()
    return render_template("products.html", products=products)


# Start Flask application
if __name__ == "__main__":
    app.run(debug=True)