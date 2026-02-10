"""
Script para actualizar códigos virtuales a formato compatible con keypad 4x4.
Solo usa caracteres disponibles: 0-9, A, B, C, D
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app import create_app
from backend.extensions import db
from backend.models import Usuario

def main():
    """Actualizar códigos virtuales a formato compatible con keypad"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Actualizando códigos virtuales a formato compatible con keypad...")
        print()
        
        # Códigos compatibles con keypad 4x4 (0-9, A-D)
        nuevos_codigos = [
            (1, '1A4B2C'),   # Juan
            (2, 'D3C1A0'),   # María  
            (3, 'B2D4A1'),   # Carlos
            (4, '33A40A'),   # René (ya es compatible)
        ]
        
        for user_id, codigo_nuevo in nuevos_codigos:
            user = Usuario.query.get(user_id)
            
            if user:
                codigo_anterior = user.codigo_virtual
                user.codigo_virtual = codigo_nuevo
                
                nombre_completo = f"{user.nombre} {user.apellido}"
                print(f"✅ {nombre_completo:20} | {codigo_anterior:15} → {codigo_nuevo}")
            else:
                print(f"⚠️  Usuario ID {user_id} no encontrado")
        
        # Guardar cambios
        db.session.commit()
        
        print()
        print("✅ Códigos actualizados correctamente en la base de datos")
        print()
        print("📝 Nuevos códigos para usar en keypad:")
        print("-" * 50)
        
        usuarios = Usuario.query.all()
        for u in usuarios:
            print(f"   {u.nombre:15} → {u.codigo_virtual}")
        
        print()

if __name__ == '__main__':
    main()
