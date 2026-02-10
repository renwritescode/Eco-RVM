import os
import sys
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app import create_app
from backend.extensions import db

app = create_app()

with app.app_context():
    try:
        # Check connection
        db.session.execute(text('SELECT 1'))
        print("Database connection successful.")
        
        # Check tables
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        print(f"Tables found: {tables}")
        
        # Check users if table exists
        if 'users' in tables or 'usuario' in tables:
            # Adjust table name based on your model
            table_name = 'usuario' if 'usuario' in tables else 'users'
            user_count = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"User count: {user_count}")
            
    except Exception as e:
        print(f"Error: {e}")
