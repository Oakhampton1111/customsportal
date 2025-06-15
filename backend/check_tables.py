import sqlite3

conn = sqlite3.connect('customs_portal.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables created:")
for table in tables:
    print(f"- {table[0]}")

# Check if conversation tables exist
conversation_tables = [t[0] for t in tables if 'conversation' in t[0]]
if conversation_tables:
    print(f"\nConversation tables found: {conversation_tables}")
else:
    print("\nNo conversation tables found - need to recreate migration")

# Check total table count
print(f"\nTotal tables: {len(tables)}")
expected_tables = ['tariff_sections', 'trade_agreements', 'tariff_chapters', 'tariff_codes', 
                  'duty_rates', 'fta_rates', 'dumping_duties', 'tcos', 'gst_provisions', 
                  'export_codes', 'product_classifications', 'conversations', 'conversation_messages']

missing_tables = [t for t in expected_tables if t not in [table[0] for table in tables]]
if missing_tables:
    print(f"Missing tables: {missing_tables}")

conn.close()
