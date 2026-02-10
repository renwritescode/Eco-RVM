import sqlite3
import os

db_path = os.path.join('data', 'eco_rvm.db')

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        for table in tables:
            t = table[0]
            if t != 'alembic_version':
                cursor.execute(f"SELECT COUNT(*) FROM {t}")
                count = cursor.fetchone()[0]
                print(f"Table {t}: {count} rows")
                
        conn.close()
    except Exception as e:
        print(f"Error reading DB: {e}")
else:
    print("No local database found.")
