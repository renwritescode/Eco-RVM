"""
Script de Setup - Inicialización del Proyecto Eco-RVM
"""

import sys
import subprocess
from pathlib import Path


def print_header():
    """Mostrar encabezado"""
    print("=" * 60)
    print("   ECO-RVM - Script de Configuración Inicial")
    print("=" * 60)
    print()


def check_python_version():
    """Verificar versión de Python"""
    print("🔍 Verificando versión de Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} no soportado")
        print("   Se requiere Python 3.10 o superior")
        return False


def create_env_file():
    """Crear archivo .env desde template"""
    print("\n🔍 Configurando variables de entorno...")
    
    root_dir = Path(__file__).resolve().parent.parent
    env_example = root_dir / '.env.example'
    env_file = root_dir / '.env'
    
    if env_file.exists():
        print("   ⚠️  .env ya existe, omitiendo...")
        return True
    
    if not env_example.exists():
        print("   ❌ .env.example no encontrado")
        return False
    
    # Copiar template
    env_file.write_text(env_example.read_text())
    print("   ✅ .env creado desde template")
    print("   ⚠️  Revisa y ajusta las variables en .env")
    return True


def create_directories():
    """Crear directorios necesarios"""
    print("\n🔍 Creando directorios...")
    
    root_dir = Path(__file__).resolve().parent.parent
    dirs = ['data', 'logs', 'capturas', 'ml/models']
    
    for dir_name in dirs:
        dir_path = root_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_name}/")
    
    return True


def install_dependencies():
    """Instalar dependencias de Python"""
    print("\n🔍 Instalando dependencias...")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], stdout=subprocess.DEVNULL)
        print("   ✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError:
        print("   ❌ Error instalando dependencias")
        return False


def verify_model():
    """Verificar existencia del modelo de IA"""
    print("\n🔍 Verificando modelo de IA...")
    
    root_dir = Path(__file__).resolve().parent.parent
    model_paths = [
        root_dir / 'ml' / 'models' / 'modelo_reciclaje.h5',
        root_dir / 'modelo_reciclaje.h5'  # Ubicación antigua
    ]
    
    for model_path in model_paths:
        if model_path.exists():
            print(f"   ✅ Modelo encontrado: {model_path.name}")
            return True
    
    print("   ⚠️  Modelo no encontrado")
    print("   Ejecuta train_model.py para entrenar el modelo")
    return True  # No es un error crítico


def main():
    """Ejecutar setup completo"""
    print_header()
    
    steps = [
        ("Python", check_python_version),
        ("Entorno", create_env_file),
        ("Directorios", create_directories),
        ("Dependencias", install_dependencies),
        ("Modelo IA", verify_model),
    ]
    
    all_ok = True
    for name, func in steps:
        if not func():
            all_ok = False
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("   ✅ Setup completado exitosamente!")
        print()
        print("   Próximos pasos:")
        print("   1. Revisa y configura el archivo .env")
        print("   2. Ejecuta: python scripts/run_backend.py")
        print("   3. Abre: http://localhost:5000")
    else:
        print("   ⚠️  Setup completado con advertencias")
        print("   Revisa los mensajes anteriores")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
