import sqlite3

# Connect to the database
conn = sqlite3.connect('customs_portal.db')
cursor = conn.cursor()

# Check the structure of tariff_chapters table
cursor.execute("PRAGMA table_info(tariff_chapters)")
columns = cursor.fetchall()
print("tariff_chapters table structure:")
for col in columns:
    print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")

print("\n" + "="*50 + "\n")

# Get a sample of data from tariff_chapters
cursor.execute("SELECT * FROM tariff_chapters LIMIT 5")
rows = cursor.fetchall()
print("Sample data from tariff_chapters:")
for row in rows:
    print(f"  {row}")

print("\n" + "="*50 + "\n")

# Check if there's a section_id column
cursor.execute("SELECT name FROM pragma_table_info('tariff_chapters') WHERE name LIKE '%section%'")
section_cols = cursor.fetchall()
print("Section-related columns in tariff_chapters:")
for col in section_cols:
    print(f"  {col[0]}")

conn.close()
