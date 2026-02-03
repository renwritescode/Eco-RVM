"""
Manejador de Arduino - Comunicación Serial
"""

import serial
import time
from typing import Optional, Callable
from backend.utils import setup_logger

logger = setup_logger('eco_rvm.arduino')


class ArduinoHandler:
    """
    Clase para manejar la comunicación serial con Arduino.
    Implementa el protocolo de comunicación definido para Eco-RVM.
    """
    
    # Comandos del protocolo
    CMD_READY = "READY"
    CMD_OBJECT_DETECTED = "OBJ_DETECTED"
    CMD_ACCEPTED = "ACCEPTED"
    CMD_REJECTED = "REJECTED"
    CMD_RFID_SCANNED = "RFID:"
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: int = 1):
        """
        Inicializar conexión serial.
        
        Args:
            port: Puerto serial (ej: COM3, /dev/ttyUSB0)
            baudrate: Velocidad de comunicación
            timeout: Timeout de lectura en segundos
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial: Optional[serial.Serial] = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Establecer conexión con Arduino.
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # Esperar inicialización de Arduino
            self._connected = True
            logger.info(f"Conectado a Arduino en {self.port}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Error conectando a Arduino: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """Cerrar conexión serial"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self._connected = False
            logger.info("Desconectado de Arduino")
    
    @property
    def is_connected(self) -> bool:
        """Verificar si está conectado"""
        return self._connected and self.serial and self.serial.is_open
    
    def send_command(self, command: str) -> bool:
        """
        Enviar comando a Arduino.
        
        Args:
            command: Comando a enviar
        
        Returns:
            bool: True si se envió correctamente
        """
        if not self.is_connected:
            logger.warning("No hay conexión con Arduino")
            return False
        
        try:
            message = f"{command}\n".encode('utf-8')
            self.serial.write(message)
            self.serial.flush()
            logger.debug(f"Enviado: {command}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Error enviando comando: {e}")
            return False
    
    def read_line(self) -> Optional[str]:
        """
        Leer una línea del Arduino.
        
        Returns:
            str o None: Línea leída o None si no hay datos
        """
        if not self.is_connected:
            return None
        
        try:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode('utf-8').strip()
                if line:
                    logger.debug(f"Recibido: {line}")
                    return line
        except Exception as e:
            logger.error(f"Error leyendo: {e}")
        
        return None
    
    def wait_for_message(self, timeout: float = 5.0) -> Optional[str]:
        """
        Esperar un mensaje del Arduino.
        
        Args:
            timeout: Tiempo máximo de espera en segundos
        
        Returns:
            str o None: Mensaje recibido o None si hay timeout
        """
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            message = self.read_line()
            if message:
                return message
            time.sleep(0.1)
        
        return None
    
    def send_accepted(self):
        """Notificar al Arduino que el objeto fue aceptado"""
        return self.send_command(self.CMD_ACCEPTED)
    
    def send_rejected(self):
        """Notificar al Arduino que el objeto fue rechazado"""
        return self.send_command(self.CMD_REJECTED)
    
    def parse_rfid(self, message: str) -> Optional[str]:
        """
        Extraer UID de RFID de un mensaje.
        
        Args:
            message: Mensaje recibido
        
        Returns:
            str o None: UID extraído o None si no es un mensaje RFID
        """
        if message.startswith(self.CMD_RFID_SCANNED):
            return message[len(self.CMD_RFID_SCANNED):].strip()
        return None
    
    def run_loop(
        self,
        on_rfid: Callable[[str], None] = None,
        on_object_detected: Callable[[], None] = None,
        on_ready: Callable[[], None] = None
    ):
        """
        Ejecutar loop principal de comunicación.
        
        Args:
            on_rfid: Callback cuando se detecta una tarjeta RFID
            on_object_detected: Callback cuando se detecta un objeto
            on_ready: Callback cuando Arduino está listo
        """
        logger.info("Iniciando loop de comunicación con Arduino")
        
        try:
            while True:
                message = self.read_line()
                
                if message:
                    # Detectar tipo de mensaje
                    if message == self.CMD_READY:
                        if on_ready:
                            on_ready()
                    
                    elif message == self.CMD_OBJECT_DETECTED:
                        if on_object_detected:
                            on_object_detected()
                    
                    elif message.startswith(self.CMD_RFID_SCANNED):
                        uid = self.parse_rfid(message)
                        if uid and on_rfid:
                            on_rfid(uid)
                
                time.sleep(0.05)  # Pequeña pausa para no saturar CPU
                
        except KeyboardInterrupt:
            logger.info("Loop interrumpido por usuario")
        finally:
            self.disconnect()
