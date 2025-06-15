#!/usr/bin/env python3
"""Check tariff_rulings table structure."""

import sqlite3

conn = sqlite3.connect('customs_portal.db')
cursor = conn.cursor()

print("Table structure:")
cursor.execute('PRAGMA table_info(tariff_rulings)')
for row in cursor.fetchall():
    print(row)

print("\nTable creation SQL:")
cursor.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="tariff_rulings"')
print(cursor.fetchone()[0])

print("\nExisting data:")
cursor.execute('SELECT * FROM tariff_rulings LIMIT 3')
for row in cursor.fetchall():
    print(row)

conn.close()
