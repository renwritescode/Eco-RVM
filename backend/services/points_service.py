"""
Servicio de Puntos y Transacciones - Lógica de Negocio
"""

from typing import Optional, Tuple
from datetime import datetime
from backend.extensions import db
from backend.models import Usuario, Transaccion
from backend.services.user_service import UserService
from backend.utils import get_service_logger

logger = get_service_logger()


class PointsService:
    """Servicio para operaciones de puntos y transacciones"""
    
    @staticmethod
    def agregar_puntos(
        uid_rfid: str,
        puntos: int,
        tipo_objeto: str,
        resultado_ia: str = None,
        confianza_ia: float = None,
        imagen_path: str = None
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        Agregar puntos a un usuario y registrar transacción.
        
        Returns:
            tuple: (exito, mensaje, datos)
        """
        if puntos <= 0:
            return False, "Los puntos deben ser mayores a cero", None
        
        usuario = UserService.obtener_por_uid(uid_rfid)
        if not usuario:
            return False, "Usuario no encontrado", None
        
        try:
            # Calcular impacto ambiental
            peso_kg, co2_kg = Transaccion.calcular_impacto(tipo_objeto)
            
            # Agregar puntos al usuario
            usuario.agregar_puntos(puntos)
            usuario.actualizar_racha()
            
            # Crear transacción
            transaccion = Transaccion(
                usuario_id=usuario.id,
                tipo_objeto=tipo_objeto,
                puntos_otorgados=puntos,
                resultado_ia=resultado_ia,
                confianza_ia=confianza_ia,
                peso_estimado_kg=peso_kg,
                co2_evitado_kg=co2_kg,
                imagen_path=imagen_path,
                fecha_hora=datetime.utcnow()
            )
            
            db.session.add(transaccion)
            db.session.commit()
            
            # Verificar badges nuevos
            badges_nuevos = UserService.verificar_badges(usuario)
            
            logger.info(
                f"Puntos agregados: {puntos} pts a {usuario.nombre} "
                f"(Total: {usuario.puntos_totales})"
            )
            
            return True, f"Se agregaron {puntos} puntos", {
                'puntos_nuevos': usuario.puntos_totales,
                'transaccion_id': transaccion.id,
                'nivel': usuario.nivel,
                'racha_dias': usuario.racha_dias,
                'impacto': {
                    'peso_kg': peso_kg,
                    'co2_evitado_kg': co2_kg
                },
                'badges_nuevos': [b.to_dict() for b in badges_nuevos]
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al agregar puntos: {e}")
            return False, f"Error interno: {str(e)}", None
    
    @staticmethod
    def obtener_transacciones_usuario(
        usuario_id: int, 
        limite: int = 50
    ) -> list:
        """Obtener historial de transacciones de un usuario"""
        transacciones = Transaccion.query\
            .filter_by(usuario_id=usuario_id)\
            .order_by(Transaccion.fecha_hora.desc())\
            .limit(limite)\
            .all()
        
        return [t.to_dict() for t in transacciones]
    
    @staticmethod
    def obtener_transacciones_recientes(limite: int = 20) -> list:
        """Obtener transacciones más recientes del sistema"""
        transacciones = Transaccion.query\
            .order_by(Transaccion.fecha_hora.desc())\
            .limit(limite)\
            .all()
        
        return [t.to_dict() for t in transacciones]
