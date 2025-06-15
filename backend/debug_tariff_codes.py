import sqlite3

# Connect to the database
conn = sqlite3.connect('customs_portal.db')
cursor = conn.cursor()

# Check the structure of tariff_codes table
cursor.execute("PRAGMA table_info(tariff_codes)")
columns = cursor.fetchall()
print("tariff_codes table structure:")
for col in columns:
    print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")

print("\n" + "="*50 + "\n")

# Check foreign key constraints
cursor.execute("PRAGMA foreign_key_list(tariff_codes)")
fks = cursor.fetchall()
print("Foreign key constraints:")
for fk in fks:
    print(f"  {fk}")

print("\n" + "="*50 + "\n")

# Get a sample of data to see parent_code usage
cursor.execute("SELECT hs_code, parent_code, description FROM tariff_codes WHERE parent_code IS NOT NULL LIMIT 5")
rows = cursor.fetchall()
print("Sample data with parent_code:")
for row in rows:
    print(f"  HS: {row[0]}, Parent: {row[1]}, Desc: {row[2][:50]}...")

conn.close()
