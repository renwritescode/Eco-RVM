"""
Controlador Principal de Eco-RVM
Orquesta la comunicación entre Arduino, visión artificial y API
"""

from controller.config import ControllerConfig
from controller.arduino_handler import ArduinoHandler
from controller.vision_system import VisionSystem
from controller.api_client import APIClient
from backend.utils import get_controller_logger

__all__ = [
    'ControllerConfig',
    'ArduinoHandler', 
    'VisionSystem',
    'APIClient'
]
