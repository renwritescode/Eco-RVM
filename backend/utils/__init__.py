"""
Sistema de Logging para Eco-RVM
Configuración profesional con rotación de archivos
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str, log_file: Path = None, level: int = logging.INFO):
    """
    Configurar logger con formato profesional y rotación de archivos.
    
    Args:
        name: Nombre del logger
        log_file: Ruta al archivo de log (opcional)
        level: Nivel de logging (default: INFO)
    
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Formato del log
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (si se especifica)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Loggers pre-configurados para cada módulo
def get_api_logger():
    """Logger para el módulo API"""
    from backend.config import Config
    return setup_logger('eco_rvm.api', Config.LOG_FILE)


def get_service_logger():
    """Logger para servicios de negocio"""
    from backend.config import Config
    return setup_logger('eco_rvm.service', Config.LOG_FILE)


def get_controller_logger():
    """Logger para el controlador de hardware"""
    from backend.config import Config
    return setup_logger('eco_rvm.controller', Config.LOG_FILE)
