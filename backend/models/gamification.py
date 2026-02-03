"""
Modelos de Base de Datos - Sistema de Gamificación
"""

from datetime import datetime
from backend.extensions import db


class Badge(db.Model):
    """
    Definición de badges/logros que los usuarios pueden obtener.
    """
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=True)
    icono = db.Column(db.String(50), default='🏆')
    color = db.Column(db.String(20), default='#FFD700')
    condicion_tipo = db.Column(db.String(50), nullable=False)  # reciclajes, puntos, racha, nivel
    condicion_valor = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    # Relación con usuarios que tienen este badge
    usuarios = db.relationship('UsuarioBadge', backref='badge', lazy='dynamic')
    
    def __repr__(self):
        return f'<Badge {self.nombre}>'
    
    def to_dict(self):
        """Serializar badge a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'color': self.color,
            'condicion_tipo': self.condicion_tipo,
            'condicion_valor': self.condicion_valor
        }
    
    def verificar_condicion(self, usuario) -> bool:
        """
        Verificar si un usuario cumple la condición para este badge.
        
        Args:
            usuario: Instancia del modelo Usuario
        
        Returns:
            bool: True si cumple la condición
        """
        if self.condicion_tipo == 'reciclajes':
            return usuario.transacciones.count() >= self.condicion_valor
        elif self.condicion_tipo == 'puntos':
            return usuario.puntos_totales >= self.condicion_valor
        elif self.condicion_tipo == 'racha':
            return usuario.racha_dias >= self.condicion_valor
        elif self.condicion_tipo == 'nivel':
            return usuario.nivel >= self.condicion_valor
        return False


class UsuarioBadge(db.Model):
    """
    Relación entre usuarios y badges obtenidos.
    """
    __tablename__ = 'usuario_badges'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer, 
        db.ForeignKey('usuarios.id'), 
        nullable=False,
        index=True
    )
    badge_id = db.Column(
        db.Integer, 
        db.ForeignKey('badges.id'), 
        nullable=False
    )
    fecha_obtencion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraint para evitar duplicados
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'badge_id', name='unique_usuario_badge'),
    )
    
    def __repr__(self):
        return f'<UsuarioBadge Usuario:{self.usuario_id} Badge:{self.badge_id}>'
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'badge': self.badge.to_dict() if self.badge else None,
            'fecha_obtencion': self.fecha_obtencion.isoformat()
        }


# Badges predefinidos del sistema
BADGES_PREDEFINIDOS = [
    {
        'nombre': 'Primer Paso',
        'descripcion': 'Realiza tu primer reciclaje',
        'icono': '🌱',
        'color': '#4CAF50',
        'condicion_tipo': 'reciclajes',
        'condicion_valor': 1
    },
    {
        'nombre': 'Reciclador Novato',
        'descripcion': 'Recicla 10 objetos',
        'icono': '♻️',
        'color': '#2196F3',
        'condicion_tipo': 'reciclajes',
        'condicion_valor': 10
    },
    {
        'nombre': 'Reciclador Experto',
        'descripcion': 'Recicla 50 objetos',
        'icono': '🌟',
        'color': '#FF9800',
        'condicion_tipo': 'reciclajes',
        'condicion_valor': 50
    },
    {
        'nombre': 'Reciclador Maestro',
        'descripcion': 'Recicla 100 objetos',
        'icono': '🏆',
        'color': '#FFD700',
        'condicion_tipo': 'reciclajes',
        'condicion_valor': 100
    },
    {
        'nombre': 'Centenario',
        'descripcion': 'Alcanza 100 puntos',
        'icono': '💯',
        'color': '#9C27B0',
        'condicion_tipo': 'puntos',
        'condicion_valor': 100
    },
    {
        'nombre': 'Mil Puntos',
        'descripcion': 'Alcanza 1000 puntos',
        'icono': '💎',
        'color': '#00BCD4',
        'condicion_tipo': 'puntos',
        'condicion_valor': 1000
    },
    {
        'nombre': 'Constante',
        'descripcion': 'Racha de 7 días reciclando',
        'icono': '🔥',
        'color': '#F44336',
        'condicion_tipo': 'racha',
        'condicion_valor': 7
    },
    {
        'nombre': 'Imparable',
        'descripcion': 'Racha de 30 días reciclando',
        'icono': '⚡',
        'color': '#E91E63',
        'condicion_tipo': 'racha',
        'condicion_valor': 30
    },
    {
        'nombre': 'Nivel 5',
        'descripcion': 'Alcanza el nivel 5',
        'icono': '⭐',
        'color': '#673AB7',
        'condicion_tipo': 'nivel',
        'condicion_valor': 5
    },
    {
        'nombre': 'Nivel 10',
        'descripcion': 'Alcanza el nivel 10',
        'icono': '🌙',
        'color': '#3F51B5',
        'condicion_tipo': 'nivel',
        'condicion_valor': 10
    }
]
