"""Minimal test with file-based error output"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Redirect stdout and stderr to file
log_file = ROOT_DIR / "debug_output.txt"

with open(log_file, 'w', encoding='utf-8') as f:
    try:
        f.write("Step 1: Importing config...\n")
        from backend.config import get_config
        config = get_config()
        f.write(f"  Database URI: {config.SQLALCHEMY_DATABASE_URI}\n")

        f.write("\nStep 2: Importing Flask...\n")
        from flask import Flask
        app = Flask(__name__)
        app.config.from_object(config)

        f.write("\nStep 3: Initializing SQLAlchemy...\n")
        from backend.extensions import db
        db.init_app(app)

        f.write("\nStep 4: Creating tables...\n")
        with app.app_context():
            f.write("  Creating all tables...\n")
            db.create_all()
            f.write("  Tables created successfully!\n")
            
            # Count existing data
            from backend.models import Usuario, Transaccion
            num_usuarios = Usuario.query.count()
            num_transacciones = Transaccion.query.count()
            
            f.write(f"\n[OK] Database connected successfully!\n")
            f.write(f"[OK] Usuarios in DB: {num_usuarios}\n")
            f.write(f"[OK] Transacciones: {num_transacciones}\n")
        
    except Exception as e:
        import traceback
        f.write(f"\n[ERROR] {type(e).__name__}: {e}\n\n")
        f.write("Full traceback:\n")
        f.write(traceback.format_exc())

print(f"Output written to: {log_file}")
