import sqlite3
connection=sqlite3.connect("database/farmers.db")
cursor=connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, name TEXT, email TEXT UNNIQUE, password TEXT, role TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS products(product_id INTEGER PRIMARY KEY, product_name TEXT, category TEXT, price REAL, quantity INTEGER, farmer_id INTEGER)""")
print("Database and tables created successfully")
connection.commit()
connection.close()