"""
Servicio de Recompensas - Lógica de Negocio
"""

from typing import Optional, Tuple, List
from backend.extensions import db
from backend.models import Usuario, Recompensa, Canje
from backend.utils import get_service_logger

logger = get_service_logger()


class RewardService:
    """Servicio para operaciones de recompensas y canjes"""
    
    @staticmethod
    def listar_recompensas(solo_activas: bool = True) -> List[dict]:
        """Listar todas las recompensas disponibles"""
        query = Recompensa.query
        if solo_activas:
            query = query.filter_by(activo=True)
        
        recompensas = query.order_by(Recompensa.puntos_requeridos.asc()).all()
        return [r.to_dict() for r in recompensas]
    
    @staticmethod
    def obtener_recompensa(recompensa_id: int) -> Optional[Recompensa]:
        """Obtener recompensa por ID"""
        return Recompensa.query.get(recompensa_id)
    
    @staticmethod
    def canjear_recompensa(
        usuario_id: int,
        recompensa_id: int
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        Realizar canje de recompensa.
        
        Returns:
            tuple: (exito, mensaje, datos_canje)
        """
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False, "Usuario no encontrado", None
        
        recompensa = Recompensa.query.get(recompensa_id)
        if not recompensa:
            return False, "Recompensa no encontrada", None
        
        # Verificar si puede canjearse
        puede, mensaje = recompensa.puede_canjearse(usuario.puntos_totales)
        if not puede:
            return False, mensaje, None
        
        try:
            # Descontar puntos
            usuario.puntos_totales -= recompensa.puntos_requeridos
            
            # Descontar stock
            recompensa.stock -= 1
            
            # Crear registro de canje
            canje = Canje(
                usuario_id=usuario_id,
                recompensa_id=recompensa_id,
                puntos_gastados=recompensa.puntos_requeridos,
                estado='pendiente',
                codigo_canje=Canje.generar_codigo()
            )
            
            db.session.add(canje)
            db.session.commit()
            
            logger.info(
                f"Canje realizado: {recompensa.nombre} por {usuario.nombre} "
                f"(Código: {canje.codigo_canje})"
            )
            
            return True, "Canje realizado exitosamente", {
                'canje_id': canje.id,
                'codigo_canje': canje.codigo_canje,
                'recompensa': recompensa.nombre,
                'puntos_restantes': usuario.puntos_totales
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error en canje: {e}")
            return False, f"Error al procesar canje: {str(e)}", None
    
    @staticmethod
    def obtener_historial_canjes(usuario_id: int) -> List[dict]:
        """Obtener historial de canjes de un usuario"""
        canjes = Canje.query\
            .filter_by(usuario_id=usuario_id)\
            .order_by(Canje.fecha_canje.desc())\
            .all()
        
        return [c.to_dict() for c in canjes]
    
    @staticmethod
    def actualizar_estado_canje(
        canje_id: int, 
        nuevo_estado: str
    ) -> Tuple[bool, str]:
        """Actualizar estado de un canje (pendiente, entregado, cancelado)"""
        canje = Canje.query.get(canje_id)
        if not canje:
            return False, "Canje no encontrado"
        
        estados_validos = ['pendiente', 'entregado', 'cancelado']
        if nuevo_estado not in estados_validos:
            return False, f"Estado inválido. Usar: {estados_validos}"
        
        try:
            # Si se cancela, devolver puntos
            if nuevo_estado == 'cancelado' and canje.estado != 'cancelado':
                usuario = Usuario.query.get(canje.usuario_id)
                if usuario:
                    usuario.puntos_totales += canje.puntos_gastados
                    # Restaurar stock
                    canje.recompensa.stock += 1
            
            canje.estado = nuevo_estado
            db.session.commit()
            
            logger.info(f"Canje {canje_id} actualizado a: {nuevo_estado}")
            return True, f"Estado actualizado a: {nuevo_estado}"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando canje: {e}")
            return False, str(e)
    
    @staticmethod
    def crear_recompensa(
        nombre: str,
        descripcion: str,
        puntos_requeridos: int,
        stock: int = 10,
        categoria: str = 'general',
        imagen_url: str = None
    ) -> Tuple[bool, str, Optional[Recompensa]]:
        """Crear nueva recompensa en el catálogo"""
        try:
            recompensa = Recompensa(
                nombre=nombre,
                descripcion=descripcion,
                puntos_requeridos=puntos_requeridos,
                stock=stock,
                categoria=categoria,
                imagen_url=imagen_url,
                activo=True
            )
            
            db.session.add(recompensa)
            db.session.commit()
            
            logger.info(f"Recompensa creada: {nombre}")
            return True, "Recompensa creada", recompensa
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando recompensa: {e}")
            return False, str(e), None
