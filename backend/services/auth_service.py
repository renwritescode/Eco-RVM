"""
Servicio de Autenticación - Eco-RVM
Manejo de login, registro y sesiones
"""

from datetime import datetime
from typing import Optional, Tuple
from backend.extensions import db
from backend.models import Usuario
from backend.utils import get_service_logger

logger = get_service_logger()


class AuthService:
    """Servicio para operaciones de autenticación"""
    
    @staticmethod
    def registrar_usuario(
        nombre: str,
        apellido: str,
        email: str,
        password: str
    ) -> Tuple[bool, str, Optional[Usuario]]:
        """
        Registrar nuevo usuario en el sistema.
        
        Args:
            nombre: Nombre del usuario
            apellido: Apellido del usuario
            email: Email único
            password: Contraseña en texto plano
            
        Returns:
            tuple: (exito, mensaje, usuario)
        """
        # Verificar si el email ya existe
        if Usuario.query.filter_by(email=email).first():
            return False, "Este email ya está registrado", None
        
        try:
            # Generar identificadores únicos
            uid_rfid = Usuario.generar_uid_rfid()
            codigo_virtual = Usuario.generar_codigo_virtual()
            
            # Asegurar que sean únicos
            while Usuario.query.filter_by(uid_rfid=uid_rfid).first():
                uid_rfid = Usuario.generar_uid_rfid()
            while Usuario.query.filter_by(codigo_virtual=codigo_virtual).first():
                codigo_virtual = Usuario.generar_codigo_virtual()
            
            # Crear usuario
            usuario = Usuario(
                uid_rfid=uid_rfid,
                codigo_virtual=codigo_virtual,
                nombre=nombre.strip(),
                apellido=apellido.strip(),
                email=email.lower().strip(),
                puntos_totales=50  # Puntos de bienvenida
            )
            usuario.set_password(password)
            
            db.session.add(usuario)
            db.session.commit()
            
            logger.info(f"Usuario registrado: {email} (Código: {codigo_virtual})")
            
            return True, "Registro exitoso. ¡Bienvenido!", usuario
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error en registro: {e}")
            return False, f"Error al registrar: {str(e)}", None
    
    @staticmethod
    def login(email: str, password: str) -> Tuple[bool, str, Optional[Usuario]]:
        """
        Autenticar usuario por email y contraseña.
        
        Returns:
            tuple: (exito, mensaje, usuario)
        """
        usuario = Usuario.query.filter_by(email=email.lower().strip()).first()
        
        if not usuario:
            logger.warning(f"Intento de login fallido: {email} (usuario no existe)")
            return False, "Email o contraseña incorrectos", None
        
        if not usuario.activo:
            return False, "Esta cuenta está desactivada", None
        
        if not usuario.check_password(password):
            logger.warning(f"Intento de login fallido: {email} (contraseña incorrecta)")
            return False, "Email o contraseña incorrectos", None
        
        # Login exitoso
        usuario.registrar_login()
        db.session.commit()
        
        logger.info(f"Login exitoso: {email}")
        return True, "Login exitoso", usuario
    
    @staticmethod
    def buscar_por_codigo(codigo: str) -> Optional[Usuario]:
        """Buscar usuario por código virtual o UID RFID"""
        return Usuario.query.filter(
            (Usuario.codigo_virtual == codigo) | 
            (Usuario.uid_rfid == codigo)
        ).first()
    
    @staticmethod
    def actualizar_password(
        usuario_id: int, 
        password_actual: str, 
        password_nuevo: str
    ) -> Tuple[bool, str]:
        """Cambiar contraseña de usuario"""
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return False, "Usuario no encontrado"
        
        if not usuario.check_password(password_actual):
            return False, "Contraseña actual incorrecta"
        
        try:
            usuario.set_password(password_nuevo)
            db.session.commit()
            logger.info(f"Contraseña actualizada: {usuario.email}")
            return True, "Contraseña actualizada exitosamente"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
