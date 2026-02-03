"""
Modelos de Base de Datos - Usuario
Con soporte para autenticación Flask-Login
"""

from datetime import datetime
import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from backend.extensions import db


class Usuario(UserMixin, db.Model):
    """
    Modelo de usuario registrado en el sistema Eco-RVM.
    Incluye autenticación con Flask-Login.
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Identificación
    uid_rfid = db.Column(db.String(20), unique=True, nullable=False, index=True)
    codigo_virtual = db.Column(db.String(20), unique=True, nullable=True)  # ECO-XXXX
    
    # Información personal
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # Autenticación
    password_hash = db.Column(db.String(256), nullable=True)
    
    # Puntos y gamificación
    puntos_totales = db.Column(db.Integer, default=0, nullable=False)
    nivel = db.Column(db.Integer, default=1, nullable=False)
    racha_dias = db.Column(db.Integer, default=0, nullable=False)
    
    # Timestamps
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultima_actividad = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    
    # Estado
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    transacciones = db.relationship(
        'Transaccion', 
        backref='usuario', 
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    badges = db.relationship(
        'UsuarioBadge',
        backref='usuario',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    canjes = db.relationship(
        'Canje',
        backref='usuario',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        return f'<Usuario {self.nombre} {self.apellido}>'
    
    # ==================== Autenticación ====================
    
    def set_password(self, password: str):
        """Hashear y guardar contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verificar contraseña"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def generar_codigo_virtual() -> str:
        """
        Generar código virtual compatible con keypad 4x4.
        Solo usa caracteres disponibles en el keypad: 0-9 y A-D
        Formato: 6 caracteres (ej: 4A7B2C)
        """
        # Caracteres disponibles en keypad 4x4
        keypad_chars = '0123456789ABCD'
        codigo = ''.join(secrets.choice(keypad_chars) for _ in range(6))
        return codigo
    
    @staticmethod
    def generar_uid_rfid() -> str:
        """Generar UID RFID simulado para demo (prefijo VIRTUAL-)"""
        uid = ''.join(secrets.choice('0123456789ABCDEF') for _ in range(14))
        return f"VIRTUAL-{uid}"
    
    @property
    def tarjeta_vinculada(self) -> bool:
        """
        Verifica si el usuario tiene una tarjeta RFID física vinculada.
        Las tarjetas virtuales comienzan con 'VIRTUAL-'.
        """
        if not self.uid_rfid:
            return False
        return not self.uid_rfid.startswith('VIRTUAL-')
    
    def vincular_tarjeta(self, uid_fisico: str) -> bool:
        """
        Vincular una tarjeta RFID física al usuario.
        Reemplaza el UID virtual por el físico.
        """
        if not uid_fisico or len(uid_fisico) < 8:
            return False
        self.uid_rfid = uid_fisico.upper().strip()
        return True
    
    # ==================== Serialización ====================
    
    def to_dict(self):
        """Serializar usuario a diccionario"""
        return {
            'id': self.id,
            'uid_rfid': self.uid_rfid,
            'codigo_virtual': self.codigo_virtual,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'nombre_completo': f'{self.nombre} {self.apellido}',
            'email': self.email,
            'puntos_totales': self.puntos_totales,
            'nivel': self.nivel,
            'racha_dias': self.racha_dias,
            'fecha_registro': self.fecha_registro.isoformat(),
            'activo': self.activo
        }
    
    def to_dict_perfil(self):
        """Serialización completa para perfil personal"""
        base = self.to_dict()
        base['total_transacciones'] = self.transacciones.count()
        base['total_badges'] = self.badges.count()
        base['total_canjes'] = self.canjes.count()
        return base
    
    # ==================== Gamificación ====================
    
    def agregar_puntos(self, cantidad: int):
        """Incrementar puntos del usuario y actualizar nivel"""
        self.puntos_totales += cantidad
        self.ultima_actividad = datetime.utcnow()
        self._actualizar_nivel()
    
    def descontar_puntos(self, cantidad: int) -> bool:
        """Descontar puntos si tiene suficientes"""
        if self.puntos_totales >= cantidad:
            self.puntos_totales -= cantidad
            return True
        return False
    
    def _actualizar_nivel(self):
        """Calcular nivel basado en puntos totales"""
        # Cada 100 puntos = 1 nivel
        self.nivel = (self.puntos_totales // 100) + 1
    
    def actualizar_racha(self):
        """Actualizar racha de días consecutivos"""
        from datetime import timedelta
        
        ahora = datetime.utcnow()
        if self.ultima_actividad:
            diferencia = ahora - self.ultima_actividad
            if diferencia.days == 1:
                self.racha_dias += 1
            elif diferencia.days > 1:
                self.racha_dias = 1
        else:
            self.racha_dias = 1
        
        self.ultima_actividad = ahora
    
    def registrar_login(self):
        """Registrar timestamp de login"""
        self.ultimo_login = datetime.utcnow()
