"""
Cliente API - Comunicación con el Backend
"""

import requests
from typing import Optional, Dict, Any
from backend.utils import setup_logger

logger = setup_logger('eco_rvm.api_client')


class APIClient:
    """
    Cliente HTTP para comunicarse con el backend de Eco-RVM.
    """
    
    def __init__(self, base_url: str = "http://localhost:5000/api", timeout: int = 10):
        """
        Inicializar cliente API.
        
        Args:
            base_url: URL base del API
            timeout: Timeout para requests en segundos
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Dict = None
    ) -> Optional[Dict[str, Any]]:
        """
        Realizar request HTTP.
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint del API
            data: Datos a enviar (para POST/PUT)
        
        Returns:
            dict o None: Respuesta JSON o None si hay error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            logger.error(f"No se pudo conectar al servidor: {url}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Timeout en request: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error en request: {e}")
            return None
    
    def check_user(self, uid: str) -> Optional[Dict]:
        """
        Verificar si un usuario existe por UID de RFID.
        
        Args:
            uid: UID de la tarjeta RFID
        
        Returns:
            dict o None: Datos del usuario si existe
        """
        result = self._request('POST', '/check_user', {'uid': uid})
        
        if result and result.get('existe'):
            logger.info(f"Usuario verificado: {result['usuario']['nombre']}")
            return result['usuario']
        
        logger.warning(f"Usuario no encontrado: {uid}")
        return None
    
    def add_points(
        self,
        uid: str,
        puntos: int,
        tipo_objeto: str,
        resultado_ia: str = None,
        confianza_ia: float = None,
        imagen_path: str = None
    ) -> Optional[Dict]:
        """
        Agregar puntos a un usuario y registrar transacción.
        
        Args:
            uid: UID del usuario
            puntos: Puntos a agregar
            tipo_objeto: Tipo de objeto reciclado
            resultado_ia: Resultado de la clasificación IA
            confianza_ia: Confianza de la clasificación
            imagen_path: Ruta de la imagen capturada
        
        Returns:
            dict o None: Resultado de la operación
        """
        data = {
            'uid': uid,
            'puntos': puntos,
            'tipo_objeto': tipo_objeto,
            'resultado_ia': resultado_ia,
            'confianza_ia': confianza_ia,
            'imagen_path': imagen_path
        }
        
        result = self._request('POST', '/add_points', data)
        
        if result and result.get('exito'):
            logger.info(
                f"Puntos agregados: {puntos} pts. "
                f"Nuevo total: {result.get('puntos_nuevos')}"
            )
            return result
        
        logger.warning(f"Error agregando puntos: {result}")
        return None
    
    def get_ranking(self, limite: int = 10) -> Optional[list]:
        """
        Obtener ranking de usuarios.
        
        Args:
            limite: Número de usuarios a retornar
        
        Returns:
            list o None: Lista de usuarios ordenados por puntos
        """
        result = self._request('GET', f'/ranking?limite={limite}')
        
        if result:
            return result.get('ranking', [])
        
        return None
    
    def get_stats(self) -> Optional[Dict]:
        """
        Obtener estadísticas del sistema.
        
        Returns:
            dict o None: Estadísticas generales
        """
        return self._request('GET', '/stats/general')
    
    def get_environmental_impact(self) -> Optional[Dict]:
        """
        Obtener impacto ambiental.
        
        Returns:
            dict o None: Métricas de impacto ambiental
        """
        return self._request('GET', '/stats/impacto')
    
    def health_check(self) -> bool:
        """
        Verificar si el servidor está disponible.
        
        Returns:
            bool: True si el servidor responde
        """
        try:
            response = self.session.get(
                f"{self.base_url.replace('/api', '')}/",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
