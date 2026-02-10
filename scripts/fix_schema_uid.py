
import os
import sys
import psycopg2
from urllib.parse import urlparse

# URL de conexión directa a Supabase
# Usamos la misma que está en Vercel
DB_URL = "postgresql://postgres.pjkveurjzylthoargxtw:renejavierdaniel2026@aws-0-us-west-2.pooler.supabase.com:6543/postgres"

def fix_schema():
    print(f"Conectando a la base de datos...")
    
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Ejecutando ALTER TABLE...")
        cursor.execute("ALTER TABLE usuarios ALTER COLUMN uid_rfid TYPE VARCHAR(50);")
        
        print("✅ Columna uid_rfid actualizada correctamente a VARCHAR(50).")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al actualizar esquema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_schema()
