import sqlite3
conn = sqlite3.connect('customs_portal.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print('All tables:', tables)
conn.close()
