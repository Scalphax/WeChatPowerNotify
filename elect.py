import sqlite3 as sql

conn = sql.connect("elect.db")
curser = conn.cursor()

a = set()

curser.execute("SELECT * FROM kv")
all_rows = curser.fetchall()

for row in all_rows:
    a.update([row[2]])
print(a)