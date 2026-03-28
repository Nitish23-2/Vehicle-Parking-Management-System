import sqlite3

conn= sqlite3.connect("instance/vehicle-parking.db")
cursor= conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
for row in cursor.fetchall():
    print(row[0])

