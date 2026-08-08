import sqlite3
connection=sqlite3.connect("database/farmers.db")
cursor=connection.cursor()
def view_users():
    cursor.execute("SELECT*FROM users")
    users=cursor.fetchall()
    if not users:
        print("No users found!")
    else:
        print("\n-----All Users-----")
        for user in users:
            print("User ID:",user[0])
            print("Name:",user[1])
            print("Email:",user[2])
            print("Role:",user[4])
            print("------------------")
def view_products():
    cursor.execute("SELECT*FROM products")
    products=cursor.fetchall()
    if not products:
        print("No products found!")
    else:
        print("\n-----All Products-----")
        for product in products:
            print("Product ID:",product[0])
            print("Product Name:",product[1])
            print("Category:",product[2])
            print("Price:",product[3])
            print("Quantity:",product[4])
            print("Farmer ID:",product[5])
            print("------------------------")
view_users()
view_products()

connection.close()