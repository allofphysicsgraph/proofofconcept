# https://docs.python.org/3/library/sqlite3.html
import sqlite3

print(sqlite3.version)

db_file = "sqlite.db"

try:
    conn = sqlite3.connect(db_file)
except sqlite3.Error:
    print(sqlite3.Error)

c = conn.cursor()

for row in c.execute('SELECT * FROM stocks ORDER BY price'):
    print(row)

conn.close()