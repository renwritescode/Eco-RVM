"""
Sistema de Visión - Cámara y Clasificación por IA
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
from backend.utils import setup_logger

logger = setup_logger('eco_rvm.vision')


class VisionSystem:
    """
    Sistema de visión artificial para captura y clasificación de objetos.
    """
    
    # Clases de clasificación binaria
    CLASE_ACEPTADO = "Aceptado"
    CLASE_RECHAZADO = "Rechazado"
    
    def __init__(
        self,
        camera_id: int = 0,
        model_path: str = None,
        min_confidence: float = 0.70,
        captures_dir: str = "capturas"
    ):
        """
        Inicializar sistema de visión.
        
        Args:
            camera_id: ID de la cámara (default: 0)
            model_path: Ruta al modelo de IA (.h5)
            min_confidence: Confianza mínima para aceptar clasificación
            captures_dir: Directorio para guardar capturas
        """
        self.camera_id = camera_id
        self.model_path = Path(model_path) if model_path else None
        self.min_confidence = min_confidence
        self.captures_dir = Path(captures_dir)
        self.captures_dir.mkdir(exist_ok=True)
        
        self.camera = None
        self.model = None
        self._model_loaded = False
    
    def load_model(self) -> bool:
        """
        Cargar modelo de TensorFlow/Keras.
        
        Returns:
            bool: True si se cargó correctamente
        """
        if not self.model_path or not self.model_path.exists():
            logger.error(f"Modelo no encontrado: {self.model_path}")
            return False
        
        try:
            # Importar TensorFlow solo cuando se necesita
            import tensorflow as tf
            
            # Suprimir logs de TensorFlow
            tf.get_logger().setLevel('ERROR')
            
            self.model = tf.keras.models.load_model(str(self.model_path))
            self._model_loaded = True
            logger.info(f"Modelo cargado: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return False
    
    def open_camera(self) -> bool:
        """
        Abrir conexión con la cámara.
        
        Returns:
            bool: True si se abrió correctamente
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            
            if not self.camera.isOpened():
                logger.error(f"No se pudo abrir la cámara {self.camera_id}")
                return False
            
            # Configurar resolución
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            logger.info(f"Cámara {self.camera_id} abierta")
            return True
            
        except Exception as e:
            logger.error(f"Error abriendo cámara: {e}")
            return False
    
    def close_camera(self):
        """Cerrar conexión con la cámara"""
        if self.camera:
            self.camera.release()
            logger.info("Cámara cerrada")
    
    @property
    def is_camera_ready(self) -> bool:
        """Verificar si la cámara está lista"""
        return self.camera is not None and self.camera.isOpened()
    
    @property
    def is_model_ready(self) -> bool:
        """Verificar si el modelo está cargado"""
        return self._model_loaded and self.model is not None
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capturar un frame de la cámara.
        
        Returns:
            np.ndarray o None: Imagen capturada o None si hay error
        """
        if not self.is_camera_ready:
            logger.warning("Cámara no está lista")
            return None
        
        ret, frame = self.camera.read()
        
        if not ret:
            logger.error("Error capturando frame")
            return None
        
        return frame
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocesar imagen para el modelo.
        
        Args:
            image: Imagen BGR de OpenCV
        
        Returns:
            np.ndarray: Imagen preprocesada
        """
        # Redimensionar a tamaño esperado por el modelo
        resized = cv2.resize(image, (224, 224))
        
        # Convertir BGR a RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalizar a rango [0, 1]
        normalized = rgb.astype(np.float32) / 255.0
        
        # Agregar dimensión de batch
        batched = np.expand_dims(normalized, axis=0)
        
        return batched
    
    def classify(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Clasificar una imagen.
        
        Args:
            image: Imagen BGR de OpenCV
        
        Returns:
            tuple: (clase, confianza)
        """
        if not self.is_model_ready:
            logger.error("Modelo no cargado")
            return self.CLASE_RECHAZADO, 0.0
        
        try:
            # Preprocesar
            preprocessed = self.preprocess_image(image)
            
            # Predecir
            prediction = self.model.predict(preprocessed, verbose=0)[0]
            
            # El modelo binario retorna probabilidad de clase positiva (Aceptado)
            if len(prediction) == 1:
                # Salida sigmoid (clasificación binaria con 1 neurona)
                prob_aceptado = float(prediction[0])
            else:
                # Salida softmax (2 neuronas: [rechazado, aceptado])
                prob_aceptado = float(prediction[1])
            
            # Determinar clase
            if prob_aceptado >= self.min_confidence:
                clase = self.CLASE_ACEPTADO
                confianza = prob_aceptado
            else:
                clase = self.CLASE_RECHAZADO
                confianza = 1.0 - prob_aceptado
            
            logger.info(f"Clasificación: {clase} ({confianza:.2%})")
            return clase, confianza
            
        except Exception as e:
            logger.error(f"Error en clasificación: {e}")
            return self.CLASE_RECHAZADO, 0.0
    
    def capture_and_classify(self) -> Tuple[str, float, Optional[str]]:
        """
        Capturar imagen y clasificarla.
        
        Returns:
            tuple: (clase, confianza, ruta_imagen o None)
        """
        frame = self.capture_frame()
        if frame is None:
            return self.CLASE_RECHAZADO, 0.0, None
        
        clase, confianza = self.classify(frame)
        
        # Guardar captura
        imagen_path = self.save_capture(frame, clase)
        
        return clase, confianza, imagen_path
    
    def save_capture(self, image: np.ndarray, clase: str) -> str:
        """
        Guardar captura de imagen.
        
        Args:
            image: Imagen a guardar
            clase: Clase de clasificación
        
        Returns:
            str: Ruta del archivo guardado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{clase.lower()}_{timestamp}.jpg"
        filepath = self.captures_dir / filename
        
        cv2.imwrite(str(filepath), image)
        logger.debug(f"Captura guardada: {filepath}")
        
        return str(filepath)
    
    def show_preview(self, window_name: str = "Eco-RVM Camera"):
        """
        Mostrar vista previa de la cámara en una ventana.
        Presionar 'q' para cerrar.
        """
        if not self.is_camera_ready:
            logger.error("Cámara no lista para preview")
            return
        
        logger.info("Mostrando preview de cámara. Presiona 'q' para salir.")
        
        try:
            while True:
                frame = self.capture_frame()
                if frame is None:
                    break
                
                # Agregar texto informativo
                cv2.putText(
                    frame, 
                    "Eco-RVM - Presiona 'c' para clasificar, 'q' para salir",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )
                
                cv2.imshow(window_name, frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    # Clasificar frame actual
                    clase, conf = self.classify(frame)
                    print(f"\nResultado: {clase} ({conf:.2%})")
                    
        finally:
            cv2.destroyAllWindows()
