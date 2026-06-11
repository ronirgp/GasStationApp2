import json
import sqlite3

conn = sqlite3.connect("data/gas_station.db")
cursor = conn.cursor()

with open("data/json/users.json", "r") as f:
    users = json.load(f)

for user in users:
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user["username"], user["password"])
    )

conn.commit()

print("Users imported successfully!")

conn.close()