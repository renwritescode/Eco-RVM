"""
Script Principal del Controlador Eco-RVM
Orquesta Arduino, cámara, IA y backend
"""

import sys
import time
from pathlib import Path

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from controller.config import ControllerConfig
from controller.arduino_handler import ArduinoHandler
from controller.vision_system import VisionSystem
from controller.api_client import APIClient
from backend.utils import setup_logger

logger = setup_logger('eco_rvm.main')


class EcoRVMController:
    """
    Controlador principal del sistema Eco-RVM.
    Gestiona el flujo completo de reciclaje.
    """
    
    def __init__(self):
        """Inicializar componentes del controlador"""
        self.config = ControllerConfig
        
        # Componentes
        self.arduino = ArduinoHandler(
            port=self.config.SERIAL_PORT,
            baudrate=self.config.SERIAL_BAUDRATE
        )
        
        self.vision = VisionSystem(
            camera_id=self.config.CAMERA_ID,
            model_path=str(self.config.MODEL_PATH),
            min_confidence=self.config.MIN_CONFIDENCE,
            captures_dir=str(self.config.CAPTURES_DIR)
        )
        
        self.api = APIClient(
            base_url=self.config.API_BASE_URL
        )
        
        # Estado del sistema
        self.current_user = None
        self.running = False
    
    def initialize(self) -> bool:
        """
        Inicializar todos los componentes.
        
        Returns:
            bool: True si todo se inicializó correctamente
        """
        logger.info("=" * 60)
        logger.info("ECO-RVM - Inicializando Sistema")
        logger.info("=" * 60)
        
        # Verificar backend
        logger.info("Verificando conexión con backend...")
        if not self.api.health_check():
            logger.error("❌ No se puede conectar al backend")
            logger.error(f"   Asegúrate de que esté corriendo en {self.config.API_BASE_URL}")
            return False
        logger.info("✅ Backend conectado")
        
        # Conectar Arduino
        logger.info(f"Conectando a Arduino en {self.config.SERIAL_PORT}...")
        if not self.arduino.connect():
            logger.error("❌ No se pudo conectar al Arduino")
            return False
        logger.info("✅ Arduino conectado")
        
        # Abrir cámara
        logger.info(f"Abriendo cámara {self.config.CAMERA_ID}...")
        if not self.vision.open_camera():
            logger.error("❌ No se pudo abrir la cámara")
            return False
        logger.info("✅ Cámara abierta")
        
        # Cargar modelo de IA (opcional para pruebas)
        logger.info(f"Cargando modelo de IA...")
        if not self.vision.load_model():
            logger.warning("⚠️  Modelo de IA no disponible")
            logger.warning("   Sistema funcionará en MODO SIMULACIÓN")
            logger.warning("   Todos los objetos serán ACEPTADOS automáticamente")
        else:
            logger.info("✅ Modelo de IA cargado")
        
        logger.info("=" * 60)
        logger.info("Sistema inicializado correctamente")
        logger.info("=" * 60)
        
        return True
    
    def shutdown(self):
        """Apagar todos los componentes"""
        logger.info("Apagando sistema...")
        self.running = False
        self.arduino.disconnect()
        self.vision.close_camera()
        logger.info("Sistema apagado")
    
    def handle_rfid(self, uid: str):
        """
        Manejar lectura de tarjeta RFID.
        
        Args:
            uid: UID de la tarjeta leída
        """
        logger.info(f"Tarjeta RFID detectada: {uid}")
        
        # Verificar usuario
        user = self.api.check_user(uid)
        
        if user:
            self.current_user = user
            logger.info(f"Usuario identificado: {user['nombre_completo']}")
            logger.info(f"Puntos actuales: {user['puntos_totales']}")
            
            # ✅ FIX: Enviar confirmación al Arduino
            nombre_corto = user['nombre'][:16]  # Máx 16 caracteres para LCD
            self.arduino.send_command(f"USER:OK:{nombre_corto}")
        else:
            self.current_user = None
            logger.warning(f"Usuario no registrado: {uid}")
            
            # ✅ FIX: Enviar notificación al Arduino
            self.arduino.send_command("USER:NEW")
    
    def handle_object_detected(self):
        """Manejar detección de objeto en el sensor"""
        logger.info("Objeto detectado por sensor ultrasónico")
        
        if not self.current_user:
            logger.warning("No hay usuario identificado")
            self.arduino.send_rejected()
            return
        
        # Esperar un momento para que el objeto esté en posición
        time.sleep(0.3)
        
        # Capturar y clasificar
        clase, confianza, imagen_path = self.vision.capture_and_classify()
        
        logger.info(f"Clasificación: {clase} ({confianza:.2%})")
        
        if clase == VisionSystem.CLASE_ACEPTADO:
            # Objeto aceptado - agregar puntos
            result = self.api.add_points(
                uid=self.current_user['uid_rfid'],
                puntos=self.config.POINTS_PER_RECYCLE,
                tipo_objeto='plastico_metal',
                resultado_ia=clase,
                confianza_ia=confianza,
                imagen_path=imagen_path
            )
            
            if result:
                logger.info(f"✅ Puntos agregados. Nuevo total: {result['puntos_nuevos']}")
                self.arduino.send_accepted()
                
                # Verificar badges nuevos
                if result.get('badges_nuevos'):
                    for badge in result['badges_nuevos']:
                        logger.info(f"🏆 ¡Nuevo badge obtenido: {badge['nombre']}!")
            else:
                logger.error("Error agregando puntos")
                self.arduino.send_rejected()
        else:
            # Objeto rechazado
            logger.info("❌ Objeto rechazado")
            self.arduino.send_rejected()
    
    def handle_login_keypad(self, codigo: str):
        """
        Manejar autenticación por keypad (ingreso de código virtual).
        
        Args:
            codigo: Código virtual ingresado por keypad (ej: ECO-DEMO001)
        """
        logger.info(f"Login por keypad - Código: {codigo}")
        
        # Buscar usuario por codigo_virtual
        user = self.api.check_user_by_code(codigo)
        
        if user:
            self.current_user = user
            logger.info(f"✅ Login exitoso: {user['nombre_completo']}")
            logger.info(f"   Puntos actuales: {user['puntos_totales']}")
            
            # Enviar confirmación al Arduino
            nombre_corto = user['nombre'][:16]  # Máx 16 caracteres para LCD
            self.arduino.send_command(f"USER:OK:{nombre_corto}")
        else:
            self.current_user = None
            logger.warning(f"❌ Código no válido: {codigo}")
            
            # Enviar error al Arduino
            self.arduino.send_command("USER:ERROR")
    
    def handle_ready(self):
        """Manejar señal de Arduino listo"""
        logger.debug("Arduino listo para siguiente operación")
        self.current_user = None
    
    def run(self):
        """Ejecutar loop principal del controlador"""
        self.running = True
        
        logger.info("Iniciando loop principal...")
        logger.info("Esperando tarjetas RFID...")
        logger.info("Presiona Ctrl+C para detener")
        
        try:
            self.arduino.run_loop(
                on_rfid=self.handle_rfid,
                on_login=self.handle_login_keypad,  # NUEVO: Soporte para login por keypad
                on_object_detected=self.handle_object_detected,
                on_ready=self.handle_ready
            )
        except KeyboardInterrupt:
            logger.info("Interrupción de usuario")
        finally:
            self.shutdown()


def main():
    """Punto de entrada principal"""
    controller = EcoRVMController()
    
    if controller.initialize():
        controller.run()
    else:
        logger.error("Fallo en inicialización. Revise los logs.")
        sys.exit(1)


if __name__ == '__main__':
    main()
