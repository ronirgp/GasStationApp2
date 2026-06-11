import sqlite3

conn = sqlite3.connect("data/gas_station.db")
cursor = conn.cursor()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
)

tables = cursor.fetchall()

for table in tables:
    print(table)

conn.close()