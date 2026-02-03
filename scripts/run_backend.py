"""
Script de prueba para iniciar el backend
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

try:
    print("Importando backend.app...")
    from backend.app import create_app
    
    print("Creando aplicación...")
    app = create_app()
    
    print("=" * 60)
    print("ECO-RVM - Backend Iniciado")
    print("=" * 60)
    print(f"Servidor corriendo en: http://localhost:5000")
    print(f"API disponible en: http://localhost:5000/api")
    print("=" * 60)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
