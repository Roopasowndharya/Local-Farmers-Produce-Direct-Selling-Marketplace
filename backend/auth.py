import sqlite3
import os
#Get absolute path to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#Connect to database using absolute path
DB_PATH = os.path.join(BASE_DIR, "database","farmers.db")
connection=sqlite3.connect(DB_PATH)
cursor=connection.cursor()
def register():
    user_id=int(input("Enter User ID:"))
    name=input("Enter Name:")
    email=input("Enter Email:")
    password=input("Enter Password:")
    role=input("Enter Role(farmer/customer):")
    try:
        cursor.execute("INSERT INTO users VALUES(?,?,?,?,?)",(user_id, name, email, password, role))
        connection.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Email already exists!")
def login():
    email=input("Enter Email:")
    password=input("Enter Password:")
    cursor.execute("SELECT*FROM users WHERE email=? AND password=?",(email, password))
    user=cursor.fetchone()
    if user:
        print("Login successful!")
        print("Welcome",user[1])
        print("Role:",user[4])
    else:
        print("Invalid email or password!")
if __name__=="__main__":
    register()
    login()
    connection.close()