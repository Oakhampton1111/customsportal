#!/usr/bin/env python3
"""Check regulatory_updates table structure."""

import sqlite3

conn = sqlite3.connect('customs_portal.db')
cursor = conn.cursor()

print("Table structure:")
cursor.execute('PRAGMA table_info(regulatory_updates)')
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]}) - Required: {bool(row[3])}")

print("\nSample data:")
cursor.execute('SELECT * FROM regulatory_updates LIMIT 1')
sample = cursor.fetchone()
if sample:
    cursor.execute('SELECT * FROM regulatory_updates LIMIT 1')
    columns = [desc[0] for desc in cursor.description]
    for i, col in enumerate(columns):
        value = sample[i] if i < len(sample) else 'NULL'
        print(f"  {col}: {value}")

conn.close()
