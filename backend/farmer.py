from math import prod
from operator import add
import sqlite3
connection=sqlite3.connect("database/farmers.db")
cursor=connection.cursor()
def add_product():
    product_id=int(input("Enter Product ID:"))
    product_name=input("Enter Product Name:")
    category=input("Enter Category:")
    price=float(input("Enter Price:"))
    quantity=int(input("Enter Quantity:"))
    farmer_id=int(input("Enter Farmer ID:"))
    cursor.execute("INSERT INTO products VALUES(?,?,?,?,?,?)",(product_id, product_name, category, price, quantity, farmer_id))
    connection.commit()
    print("Product added successfully!")
def view_products():
    cursor.execute("SELECT*FROM products")
    products=cursor.fetchall()
    if len(products)==0:
        print("No products found!")
    else:
        print("\n-----Product List-----")
        for product in products:
            print("Product ID:",product[0])
            print("Product Name:",product[1])
            print("Category:",product[2])
            print("Price:",product[3])
            print("Quantity:",product[4])
            print("Farmer ID:",product[5])
            print("-------------------------")
add_product()
view_products()
connection.close()