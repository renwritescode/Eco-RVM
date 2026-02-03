"""
Configuración del Backend Eco-RVM
Gestión de configuración por entorno (development, production, testing)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Calcular ruta absoluta de la base de datos una sola vez
_DB_PATH = str(BASE_DIR / 'data' / 'eco_rvm.db').replace('\\', '/')
_DEFAULT_DB_URI = f'sqlite:///{_DB_PATH}'


class Config:
    """Configuración base compartida por todos los entornos"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Directorio de datos  
    DATA_DIR = BASE_DIR / 'data'
    DATA_DIR.mkdir(exist_ok=True)
    
    # Logs
    LOG_DIR = BASE_DIR / 'logs'
    LOG_DIR.mkdir(exist_ok=True)
    LOG_FILE = LOG_DIR / 'eco_rvm.log'
    
    # Sistema de puntos
    POINTS_PER_RECYCLE = int(os.getenv('POINTS_PER_RECYCLE', 10))
    
    # Factores de impacto ambiental
    CO2_PER_PLASTIC_BOTTLE = float(os.getenv('CO2_PER_PLASTIC_BOTTLE', 0.05))
    CO2_PER_METAL_CAN = float(os.getenv('CO2_PER_METAL_CAN', 0.03))
    WEIGHT_PER_PLASTIC_BOTTLE = float(os.getenv('WEIGHT_PER_PLASTIC_BOTTLE', 0.025))
    WEIGHT_PER_METAL_CAN = float(os.getenv('WEIGHT_PER_METAL_CAN', 0.015))


class DevelopmentConfig(Config):
    """Configuración para desarrollo local"""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', _DEFAULT_DB_URI)


class ProductionConfig(Config):
    """Configuración para producción"""
    
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # En producción, SECRET_KEY es obligatorio
    @classmethod
    def init_app(cls, app):
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("SECRET_KEY debe configurarse en producción")


class TestingConfig(Config):
    """Configuración para pruebas automatizadas"""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtener configuración según variable de entorno FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
