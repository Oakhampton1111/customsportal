import sqlite3

# Connect to the database
conn = sqlite3.connect('customs_portal.db')
cursor = conn.cursor()

# Check the structure of tariff_sections table
cursor.execute("PRAGMA table_info(tariff_sections)")
columns = cursor.fetchall()
print("tariff_sections table structure:")
for col in columns:
    print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")

print("\n" + "="*50 + "\n")

# Get a sample of data from tariff_sections
cursor.execute("SELECT * FROM tariff_sections LIMIT 3")
rows = cursor.fetchall()
print("Sample data from tariff_sections:")
for row in rows:
    print(f"  {row}")

print("\n" + "="*50 + "\n")

# Check if there are any foreign key issues
cursor.execute("PRAGMA foreign_key_check(tariff_sections)")
fk_issues = cursor.fetchall()
if fk_issues:
    print("Foreign key issues:")
    for issue in fk_issues:
        print(f"  {issue}")
else:
    print("No foreign key issues found")

conn.close()
