"""
Script de Seed - Poblar base de datos con datos de ejemplo
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app import create_app
from backend.extensions import db
from backend.models import (
    Usuario, Transaccion, Recompensa, Badge, 
    UsuarioBadge, BADGES_PREDEFINIDOS
)
from datetime import datetime, timedelta
import random


def seed_users(num_users=10):
    """Crear usuarios de prueba"""
    print("\n🧑 Creando usuarios...")
    
    nombres = ['Juan', 'María', 'Carlos', 'Ana', 'Pedro', 'Laura', 'Diego', 'Sofía', 'Miguel', 'Valentina']
    apellidos = ['García', 'Rodríguez', 'Martínez', 'López', 'González', 'Hernández', 'Pérez', 'Sánchez', 'Ramírez', 'Torres']
    
    users_created = 0
    for i in range(num_users):
        uid = f"04{''.join(random.choices('0123456789ABCDEF', k=12))}"
        
        # Verificar que no exista
        if Usuario.query.filter_by(uid_rfid=uid).first():
            continue
        
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        
        usuario = Usuario(
            uid_rfid=uid,
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}{i}@universidad.edu",
            puntos_totales=random.randint(0, 500),
            nivel=random.randint(1, 5),
            racha_dias=random.randint(0, 30),
            fecha_registro=datetime.utcnow() - timedelta(days=random.randint(1, 90))
        )
        
        db.session.add(usuario)
        users_created += 1
    
    db.session.commit()
    print(f"   ✅ {users_created} usuarios creados")


def seed_transactions():
    """Crear transacciones de ejemplo"""
    print("\n📝 Creando transacciones...")
    
    usuarios = Usuario.query.all()
    if not usuarios:
        print("   ⚠️  No hay usuarios, omitiendo...")
        return
    
    tipos = ['botella', 'lata', 'plastico', 'metal']
    resultados = ['Botella PET', 'Lata Aluminio', 'Plástico Reciclable', 'Metal Reciclable']
    
    trans_created = 0
    for usuario in usuarios:
        # Crear entre 5 y 20 transacciones por usuario
        num_trans = random.randint(5, 20)
        
        for _ in range(num_trans):
            tipo = random.choice(tipos)
            resultado = random.choice(resultados)
            
            trans = Transaccion(
                usuario_id=usuario.id,
                tipo_objeto=tipo,
                puntos_otorgados=10,
                resultado_ia=resultado,
                confianza_ia=random.uniform(0.75, 0.99),
                peso_estimado_kg=random.uniform(0.01, 0.05),
                co2_evitado_kg=random.uniform(0.03, 0.07),
                fecha_hora=datetime.utcnow() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23)
                )
            )
            
            db.session.add(trans)
            trans_created += 1
    
    db.session.commit()
    print(f"   ✅ {trans_created} transacciones creadas")


def seed_rewards():
    """Crear recompensas de ejemplo"""
    print("\n🎁 Creando recompensas...")
    
    if Recompensa.query.count() > 0:
        print("   ⚠️  Ya existen recompensas, omitiendo...")
        return
    
    recompensas = [
        ('Café Gratis', 'Un café de tu elección en la cafetería', 50, 20, 'comida'),
        ('Descuento 10% Librería', '10% de descuento en librería', 100, 50, 'descuentos'),
        ('Entrada Cine', 'Una entrada de cine', 200, 15, 'entretenimiento'),
        ('Botella Ecológica', 'Botella reutilizable Eco-RVM', 300, 30, 'productos'),
        ('Almuerzo Gratis', 'Un almuerzo en el comedor', 150, 10, 'comida'),
        ('USB 16GB', 'Memoria USB con logo Eco-RVM', 400, 8, 'productos'),
        ('Descuento 20% Tienda', '20% en cualquier compra', 250, 25, 'descuentos'),
        ('Donación ONG Ambiental', 'Tus puntos donan a causa ambiental', 500, 999, 'donacion'),
    ]
    
    for nombre, desc, puntos, stock, cat in recompensas:
        r = Recompensa(
            nombre=nombre,
            descripcion=desc,
            puntos_requeridos=puntos,
            stock=stock,
            categoria=cat
        )
        db.session.add(r)
    
    db.session.commit()
    print(f"   ✅ {len(recompensas)} recompensas creadas")


def seed_badges():
    """Crear badges del sistema"""
    print("\n🏆 Creando badges...")
    
    if Badge.query.count() > 0:
        print("   ⚠️  Ya existen badges, omitiendo...")
        return
    
    for badge_data in BADGES_PREDEFINIDOS:
        badge = Badge(**badge_data)
        db.session.add(badge)
    
    db.session.commit()
    print(f"   ✅ {len(BADGES_PREDEFINIDOS)} badges creados")


def assign_badges():
    """Asignar badges a usuarios según sus logros"""
    print("\n🎖️  Asignando badges...")
    
    usuarios = Usuario.query.all()
    badges = Badge.query.all()
    
    assigned = 0
    for usuario in usuarios:
        for badge in badges:
            # Verificar si ya tiene el badge
            existing = UsuarioBadge.query.filter_by(
                usuario_id=usuario.id,
                badge_id=badge.id
            ).first()
            
            if existing:
                continue
            
            # Verificar condición
            if badge.verificar_condicion(usuario):
                ub = UsuarioBadge(
                    usuario_id=usuario.id,
                    badge_id=badge.id,
                    fecha_obtencion=datetime.utcnow() - timedelta(
                        days=random.randint(0, 30)
                    )
                )
                db.session.add(ub)
                assigned += 1
    
    db.session.commit()
    print(f"   ✅ {assigned} badges asignados")


def main():
    """Ejecutar seed completo"""
    print("=" * 60)
    print("   ECO-RVM - Seed de Base de Datos")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        print("\n🔧 Creando tablas...")
        db.create_all()
        print("   ✅ Tablas creadas")
        
        seed_badges()
        seed_rewards()
        seed_users(10)
        seed_transactions()
        assign_badges()
        
        print()
        print("=" * 60)
        print("   ✅ Seed completado!")
        print(f"   Usuarios: {Usuario.query.count()}")
        print(f"   Transacciones: {Transaccion.query.count()}")
        print(f"   Recompensas: {Recompensa.query.count()}")
        print(f"   Badges: {Badge.query.count()}")
        print("=" * 60)


if __name__ == '__main__':
    main()
