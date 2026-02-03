"""
Configuración del Controlador Eco-RVM
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


class ControllerConfig:
    """Configuración para el controlador de hardware"""
    
    # Comunicación Serial (Arduino)
    SERIAL_PORT = os.getenv('SERIAL_PORT', 'COM3')
    SERIAL_BAUDRATE = int(os.getenv('SERIAL_BAUDRATE', 9600))
    SERIAL_TIMEOUT = int(os.getenv('SERIAL_TIMEOUT', 1))
    
    # Cámara
    CAMERA_ID = int(os.getenv('CAMERA_ID', 0))
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    
    # API Backend
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
    API_TIMEOUT = 10  # segundos
    
    # Modelo de IA
    MODEL_PATH = BASE_DIR / os.getenv('MODEL_PATH', 'ml/models/modelo_reciclaje.h5')
    MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', 0.70))
    
    # Sistema de Puntos
    POINTS_PER_RECYCLE = int(os.getenv('POINTS_PER_RECYCLE', 10))
    
    # Capturas
    CAPTURES_DIR = BASE_DIR / 'capturas'
    CAPTURES_DIR.mkdir(exist_ok=True)
    
    # Logs
    LOG_DIR = BASE_DIR / 'logs'
    LOG_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def to_dict(cls):
        """Retorna configuración como diccionario"""
        return {
            'serial_port': cls.SERIAL_PORT,
            'serial_baudrate': cls.SERIAL_BAUDRATE,
            'camera_id': cls.CAMERA_ID,
            'api_url': cls.API_BASE_URL,
            'model_path': str(cls.MODEL_PATH),
            'min_confidence': cls.MIN_CONFIDENCE
        }
    
    @classmethod
    def validate(cls) -> list:
        """Validar configuración, retorna lista de errores"""
        errors = []
        
        if not cls.MODEL_PATH.exists():
            errors.append(f"Modelo no encontrado: {cls.MODEL_PATH}")
        
        return errors
