"""
Script de Verificación del Sistema Eco-RVM v2.0
Verifica que todos los componentes estén configurados correctamente
"""

import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


def print_header():
    print("=" * 60)
    print("   ECO-RVM v2.0 - Verificación del Sistema")
    print("=" * 60)
    print()


def check_python():
    """Verificar versión de Python"""
    print("🐍 Python")
    version = sys.version_info
    print(f"   Versión: {version.major}.{version.minor}.{version.micro}")
    ok = version.major == 3 and version.minor >= 10
    print(f"   Estado: {'✅ OK' if ok else '❌ Requiere 3.10+'}")
    return ok


def check_dependencies():
    """Verificar dependencias instaladas"""
    print("\n📦 Dependencias")
    
    required = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_cors', 'Flask-CORS'),
        ('marshmallow', 'Marshmallow'),
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('serial', 'PySerial'),
        ('requests', 'Requests'),
    ]
    
    optional = [
        ('tensorflow', 'TensorFlow'),
    ]
    
    all_ok = True
    
    for module, name in required:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - No instalado")
            all_ok = False
    
    for module, name in optional:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ⚠️  {name} - No instalado (opcional)")
    
    return all_ok


def check_directories():
    """Verificar estructura de directorios"""
    print("\n📁 Estructura de Directorios")
    
    required_dirs = [
        'backend',
        'backend/api',
        'backend/models',
        'backend/services',
        'controller',
        'frontend/templates',
        'frontend/static',
        'tests',
        'data',
        'logs',
    ]
    
    all_ok = True
    
    for dir_name in required_dirs:
        dir_path = ROOT_DIR / dir_name
        if dir_path.exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ - No existe")
            all_ok = False
    
    return all_ok


def check_config_files():
    """Verificar archivos de configuración"""
    print("\n⚙️  Configuración")
    
    # Verificar .env
    env_file = ROOT_DIR / '.env'
    env_example = ROOT_DIR / '.env.example'
    
    if env_file.exists():
        print("   ✅ .env")
    elif env_example.exists():
        print("   ⚠️  .env no existe, usar .env.example como base")
    else:
        print("   ❌ .env ni .env.example existen")
    
    # Verificar requirements.txt
    req_file = ROOT_DIR / 'requirements.txt'
    print(f"   {'✅' if req_file.exists() else '❌'} requirements.txt")
    
    return True


def check_model():
    """Verificar modelo de IA"""
    print("\n🤖 Modelo de IA")
    
    model_paths = [
        ROOT_DIR / 'ml' / 'models' / 'modelo_reciclaje.h5',
        ROOT_DIR / 'modelo_reciclaje.h5',
    ]
    
    for path in model_paths:
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"   ✅ {path.name} ({size_mb:.1f} MB)")
            return True
    
    print("   ⚠️  Modelo no encontrado")
    print("      Ejecutar: python train_model.py")
    return True  # No es crítico


def check_serial_ports():
    """Verificar puertos seriales disponibles"""
    print("\n🔌 Puertos Seriales")
    
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        if ports:
            for port in ports:
                print(f"   📍 {port.device} - {port.description}")
        else:
            print("   ⚠️  No se encontraron puertos seriales")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def check_camera():
    """Verificar cámara disponible"""
    print("\n📷 Cámara")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                print(f"   ✅ Cámara 0 disponible ({width}x{height})")
            else:
                print("   ⚠️  Cámara 0 abierta pero no lee frames")
            cap.release()
            return True
        else:
            print("   ⚠️  Cámara 0 no disponible")
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def check_backend():
    """Verificar que el backend pueda iniciarse"""
    print("\n🚀 Backend")
    
    try:
        from backend.app import create_app
        from backend.config import TestingConfig
        
        app = create_app(TestingConfig)
        print("   ✅ Backend Flask cargado correctamente")
        return True
    except Exception as e:
        print(f"   ❌ Error cargando backend: {e}")
        return False


def main():
    """Ejecutar todas las verificaciones"""
    print_header()
    
    checks = [
        ("Python", check_python),
        ("Dependencias", check_dependencies),
        ("Directorios", check_directories),
        ("Configuración", check_config_files),
        ("Modelo IA", check_model),
        ("Puertos Serial", check_serial_ports),
        ("Cámara", check_camera),
        ("Backend", check_backend),
    ]
    
    results = []
    for name, func in checks:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append((name, False))
    
    # Resumen
    print()
    print("=" * 60)
    print("   RESUMEN")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
    
    print()
    print(f"   Resultado: {passed}/{total} verificaciones exitosas")
    
    if passed == total:
        print("\n   🎉 ¡Sistema listo para usar!")
    else:
        print("\n   ⚠️  Revisa los errores anteriores")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
