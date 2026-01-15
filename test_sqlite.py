import sqlite3
import os

# Create in-memory DB
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# Create table
cursor.execute("CREATE TABLE test (created_at TEXT)")
# Insert 4:57 UTC
cursor.execute("INSERT INTO test VALUES ('2026-01-15 04:57:54')")

# Test +8 hours
offset = 8
query = f"SELECT datetime(created_at, '+{offset} hours') FROM test"
cursor.execute(query)
res = cursor.fetchone()[0]
print(f"Original: 2026-01-15 04:57:54")
print(f"With +8:  {res}")

assert res == "2026-01-15 12:57:54", f"Expected 12:57:54, got {res}"
