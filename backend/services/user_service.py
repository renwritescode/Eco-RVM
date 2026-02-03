"""
Servicio de Usuarios - Lógica de Negocio
"""

from typing import Optional, Tuple
from backend.extensions import db
from backend.models import Usuario, Badge, UsuarioBadge
from backend.utils import get_service_logger

logger = get_service_logger()


class UserService:
    """Servicio para operaciones de usuarios"""
    
    @staticmethod
    def verificar_usuario(uid_rfid: str) -> Tuple[bool, Optional[dict]]:
        """
        Verificar si un usuario existe por UID de RFID.
        
        Args:
            uid_rfid: UID de la tarjeta RFID
        
        Returns:
            tuple: (existe: bool, datos_usuario: dict o None)
        """
        uid_rfid = uid_rfid.upper().strip()
        usuario = Usuario.query.filter_by(uid_rfid=uid_rfid, activo=True).first()
        
        if usuario:
            logger.info(f"Usuario verificado: {usuario.nombre} {usuario.apellido}")
            return True, usuario.to_dict()
        
        logger.warning(f"Usuario no encontrado: {uid_rfid}")
        return False, None
    
    @staticmethod
    def obtener_por_id(usuario_id: int) -> Optional[Usuario]:
        """Obtener usuario por ID"""
        return Usuario.query.get(usuario_id)
    
    @staticmethod
    def obtener_por_uid(uid_rfid: str) -> Optional[Usuario]:
        """Obtener usuario por UID RFID"""
        return Usuario.query.filter_by(
            uid_rfid=uid_rfid.upper().strip(), 
            activo=True
        ).first()
    
    @staticmethod
    def listar_usuarios(solo_activos: bool = True) -> list:
        """Listar todos los usuarios ordenados por puntos"""
        query = Usuario.query
        if solo_activos:
            query = query.filter_by(activo=True)
        return query.order_by(Usuario.puntos_totales.desc()).all()
    
    @staticmethod
    def registrar_usuario(
        uid_rfid: str,
        nombre: str,
        apellido: str,
        email: str
    ) -> Tuple[bool, str, Optional[Usuario]]:
        """
        Registrar un nuevo usuario.
        
        Returns:
            tuple: (exito, mensaje, usuario)
        """
        uid_rfid = uid_rfid.upper().strip()
        
        # Validar UID único
        if Usuario.query.filter_by(uid_rfid=uid_rfid).first():
            return False, "UID ya registrado en el sistema", None
        
        # Validar email único
        if Usuario.query.filter_by(email=email).first():
            return False, "Email ya registrado en el sistema", None
        
        try:
            nuevo_usuario = Usuario(
                uid_rfid=uid_rfid,
                nombre=nombre,
                apellido=apellido,
                email=email,
                puntos_totales=0,
                nivel=1,
                activo=True
            )
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            logger.info(f"Usuario registrado: {nombre} {apellido} ({uid_rfid})")
            return True, "Usuario registrado exitosamente", nuevo_usuario
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al registrar usuario: {e}")
            return False, f"Error al registrar: {str(e)}", None
    
    @staticmethod
    def obtener_ranking(limite: int = 10) -> list:
        """Obtener ranking de usuarios por puntos"""
        usuarios = Usuario.query.filter_by(activo=True)\
            .order_by(Usuario.puntos_totales.desc())\
            .limit(limite)\
            .all()
        
        ranking = []
        for i, usuario in enumerate(usuarios, 1):
            datos = usuario.to_dict()
            datos['posicion'] = i
            ranking.append(datos)
        
        return ranking
    
    @staticmethod
    def verificar_badges(usuario: Usuario) -> list:
        """
        Verificar y otorgar badges pendientes a un usuario.
        
        Returns:
            list: Badges nuevos otorgados
        """
        badges_nuevos = []
        
        # Obtener IDs de badges que ya tiene
        badges_existentes = {ub.badge_id for ub in usuario.badges.all()}
        
        # Verificar cada badge activo
        for badge in Badge.query.filter_by(activo=True).all():
            if badge.id in badges_existentes:
                continue
            
            if badge.verificar_condicion(usuario):
                # Otorgar badge
                usuario_badge = UsuarioBadge(
                    usuario_id=usuario.id,
                    badge_id=badge.id
                )
                db.session.add(usuario_badge)
                badges_nuevos.append(badge)
                logger.info(f"Badge otorgado: {badge.nombre} a {usuario.nombre}")
        
        if badges_nuevos:
            db.session.commit()
        
        return badges_nuevos
    
    @staticmethod
    def obtener_badges_usuario(usuario_id: int) -> list:
        """Obtener todos los badges de un usuario"""
        usuario_badges = UsuarioBadge.query.filter_by(usuario_id=usuario_id).all()
        return [ub.to_dict() for ub in usuario_badges]
