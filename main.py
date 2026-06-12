import os
import sqlite3
import hashlib
from datetime import datetime

DATA_DIR = "data"
RECEIPTS_DIR = os.path.join(DATA_DIR, "receipts")
DB_PATH = os.path.join(DATA_DIR, "gas_station.db")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def read_float(prompt, minimum=None, minimum_message=None):
    while True:
        raw_value = input(prompt).strip()

        try:
            value = float(raw_value)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if minimum is not None and value < minimum:
            print(minimum_message)
            continue

        return value


os.makedirs(RECEIPTS_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    amount REAL
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS cash (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    quantity REAL
)
""")

conn.commit()

cursor.execute("SELECT COUNT(*) FROM cash")

if cursor.fetchone()[0] == 0:
    cursor.execute(
        "INSERT INTO cash (amount) VALUES (?)",
        (0,)
    )
    conn.commit()

print("Welcome to Gas Station System v1")
conn.commit()

print("\nLOGIN")

username = input("Username: ").strip()
password = input("Password: ").strip()
hashed_password = hash_password(password)
logged_in = False

cursor.execute(
    "SELECT * FROM users WHERE username = ? AND password = ?",
    (username, hashed_password)
)

user = cursor.fetchone()

if user:
    logged_in = True
else:
    print("Invalid username or password.")
    exit()

print("\n====================================")
print("Login successful!")
print("Welcome to Gas Station POS")
print("====================================")

while True:
    print("\n====================================")
    print("      GAS STATION POS SYSTEM")
    print("====================================")
    print(f"Logged in as: {username}")
    print("====================================")
    print("1. Add Sale")
    print("2. Show Sales")
    print("3. Show Total Cash")
    print("4. Refund Sale")
    print("5. Create Cashier Account")
    print("6. Delete Employee Account")
    print("7. Manager Panel")
    print("8. Logout")
    print("9. Exit")
    print("10. Add Inventory")
    print("11. Show Inventory")
    print("12. Low Stock Report")
    print("13. Search Inventory")
    print("====================================")

    choice = input("Choose: ")

    if choice == "1":
        product = input("Product: ").strip()

        if not product:
            print("Product name is required.")
            continue

        amount = read_float(
            "Amount ($): ",
            minimum=0.01,
            minimum_message="Amount must be greater than 0."
        )

        cursor.execute(
            "INSERT INTO sales (product, amount) VALUES (?, ?)",
            (product, amount)
        )

        conn.commit()
        
        receipt_id = cursor.lastrowid
        
        cursor.execute(
            "UPDATE cash SET amount = amount + ? WHERE id = 1",
            (amount,)
        )

        conn.commit()
        
        current_datetime = datetime.now()

        date = current_datetime.strftime("%Y-%m-%d")
        time = current_datetime.strftime("%H:%M:%S")
        
        receipt_path = os.path.join(RECEIPTS_DIR, "receipt.txt")

        with open(receipt_path, "w") as f:
            f.write("===== RECEIPT =====\n")
            f.write(f"Receipt #: {receipt_id}\n")
            f.write(f"Date: {date}\n")
            f.write(f"Time: {time}\n")
            f.write(f"Product: {product}\n")
            f.write(f"Amount: ${amount:.2f}\n")
            f.write("===================\n")

            print("Sale added!")

    elif choice == "2":
        print("\nSALES HISTORY:")

        cursor.execute("SELECT product, amount FROM sales")

        sales_data = cursor.fetchall()

        if len(sales_data) == 0:
            print("No sales yet.")
        else:
            for sale in sales_data:
                print(f"{sale[0]} - ${sale[1]:.2f}")
                
    elif choice == "3":
        cursor.execute("SELECT amount FROM cash WHERE id = 1")

        cash_amount = cursor.fetchone()[0]

        print(f"Total Cash: ${cash_amount:.2f}")

    
    
    elif choice == "4":

        amount = read_float(
            "Refund Amount: ",
            minimum=0.01,
            minimum_message="Refund amount must be greater than 0."
        )

        cursor.execute("SELECT amount FROM cash WHERE id = 1")
        cash_amount = cursor.fetchone()[0]

        if amount <= cash_amount:

            cursor.execute(
                "UPDATE cash SET amount = amount - ? WHERE id = 1",
                (amount,)
            )

            conn.commit()

            print("Refund successful.")

        else:

            print("Refund exceeds available cash.")
            
    elif choice == "5":
        if username != "admin":
            print("Access denied. Admin only.")
            continue

        new_user = input("New Cashier Username: ").strip()
        new_password = input("New Cashier Password: ").strip()

        if not new_user:
            print("Username is required.")
            continue

        if not new_password:
            print("Password is required.")
            continue

        cursor.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (new_user,)
        )

        if cursor.fetchone():
            print("That username already exists.")
            continue

        hashed_password = hash_password(new_password)

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (new_user, hashed_password)
        )

        conn.commit()

        print("Cashier account created successfully!")
        
    elif choice == "6":

        if username != "admin":
            print("Access denied. Admin only.")
            continue

        delete_user = input("Employee username to delete: ").strip()

        if not delete_user:
            print("Username is required.")
            continue

        if delete_user == "admin":
            print("The admin account cannot be deleted.")
            continue

        cursor.execute(
            "DELETE FROM users WHERE username = ?",
            (delete_user,)
        )

        conn.commit()

        if cursor.rowcount == 0:
            print("Employee account not found.")
        else:
            print("Employee account deleted.")

    elif choice == "7":

        if username != "admin":
            print("Access denied. Admin only.")
            continue

        print("\n===== MANAGER PANEL =====")
        print("\nEmployees:")

        cursor.execute("SELECT username FROM users")

        users = cursor.fetchall()

        for user in users:
            print("-", user[0])
            
        cursor.execute("SELECT amount FROM cash WHERE id = 1")
        cash_amount = cursor.fetchone()[0]

        print("\nCash Register Total:")
        print(f"${cash_amount:.2f}")
        
        print("\nTotal Sales Recorded:")
        cursor.execute("SELECT COUNT(*) FROM sales")
        total_sales = cursor.fetchone()[0]

        print(total_sales)
    
    elif choice == "10":

        product = input("Product Name: ").strip()

        if not product:
            print("Product name is required.")
            continue

        quantity = read_float(
            "Quantity: ",
            minimum=0,
            minimum_message="Quantity cannot be negative."
        )

        cursor.execute(
            "INSERT INTO inventory (product, quantity) VALUES (?, ?)",
            (product, quantity)
        )

        conn.commit()

        print("Inventory added successfully!")   
        
    elif choice == "11":

        print("\nINVENTORY")

        cursor.execute(
            "SELECT product, quantity FROM inventory"
        )

        inventory_items = cursor.fetchall()

        if len(inventory_items) == 0:
            print("No inventory found.")
        else:
            for item in inventory_items:
                print(f"{item[0]} - {item[1]}")   
    elif choice == "12":

        print("\nLOW STOCK REPORT")

        cursor.execute(
            "SELECT product, quantity FROM inventory WHERE quantity < 20"
        )

        low_stock_items = cursor.fetchall()

        if len(low_stock_items) == 0:
            print("No low stock items.")
        else:
            for item in low_stock_items:
                print(f"{item[0]} - {item[1]} units remaining")
                
    elif choice == "13":

        product_name = input("Product Name: ").strip()

        cursor.execute(
            "SELECT product, quantity FROM inventory WHERE product = ?",
            (product_name,)
        )

        item = cursor.fetchone()

        if item:
            print("\nFOUND:")
            print(f"{item[0]} - {item[1]}")
        else:
            print("Product not found.")            
                
        
        
    elif choice == "8":
        print("Logging out...")
        break
    
        
    elif choice == "9":
        print("Goodbye")
        break
            

    else:
        print("Invalid option")

conn.close()
