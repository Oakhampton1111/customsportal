import sqlite3
import os

# Connect to the database
db_path = "customs_portal.db"
if not os.path.exists(db_path):
    print("Database file does not exist!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("All tables in database:")
for table in tables:
    table_name = table[0]
    print(f"- {table_name}")
    
    # Get row count for each table
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  ({count} rows)")

print(f"\nTotal tables: {len(tables)}")

# Check for specific missing tables
expected_tables = [
    'tariff_sections', 'tariff_chapters', 'tariff_codes', 'duty_rates', 
    'fta_rates', 'dumping_duties', 'tcos', 'gst_provisions', 
    'export_codes', 'product_classifications', 'trade_agreements',
    'conversations', 'conversation_messages'
]

missing_tables = []
for expected in expected_tables:
    found = any(table[0] == expected for table in tables)
    if not found:
        missing_tables.append(expected)

if missing_tables:
    print(f"\nMissing tables: {missing_tables}")
else:
    print("\n✅ All expected tables found!")

conn.close()
