import sqlite3
connection=sqlite3.connect("database/farmers.db")
cursor=connection.cursor()
def view_products():
    cursor.execute("SELECT*FROM products")
    products=cursor.fetchall()
    if len(products)==0:
        print("No products available!")
    else:
        print("\n-----Available Products-----")
        for product in products:
            print("Product ID:",product[0])
            print("Product Name:",product[1])
            print("Category:",product[2])
            print("Price:",product[3])
            print("Quantity:",product[4])
            print("Farmer ID:",product[5])
            print("-------------------------")
def search_product():
    search_name=input("Enter product name to search:")
    cursor.execute("SELECT*FROM products WHERE product_name LIKE ?",('%'+search_name+'%',))
    products=cursor.fetchall()
    if len(products)==0:
        print("No matching products found!")
    else:
        print("\n-----Search Result-----")
        for product in products:
            print("Product ID:",product[0])
            print("Product Name:",product[1])
            print("Category:",product[2])
            print("Price:",product[3])
            print("Quantity:",product[4])
            print("Farmer ID:",product[5])
            print("-------------------------")
def search_product():
    search_name=input("Enter product name to search:")
    cursor.execute("SELECT*FROM products WHERE product_name LIKE ?",('%'+search_name+'%',))
    products=cursor.fetchall()
    if len(products)==0:
        print("No matching products found!")
    else:
        print("\n-----Search Result-----")
        for product in products:
            print("Product ID:",product[0])
            print("Product Name:",product[1])
            print("Category:",product[2])
            print("Price:",product[3])
            print("Quantity:",product[4])
            print("Farmer ID:",product[5])
            print("-------------------------")
view_products()
search_product()
connection.close()