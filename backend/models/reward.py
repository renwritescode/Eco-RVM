"""
Modelos de Base de Datos - Sistema de Recompensas
"""

from datetime import datetime
from backend.extensions import db


class Recompensa(db.Model):
    """
    Catálogo de recompensas canjeables con puntos.
    """
    __tablename__ = 'recompensas'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    puntos_requeridos = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    imagen_url = db.Column(db.String(255), nullable=True)
    categoria = db.Column(db.String(50), default='general')
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con canjes
    canjes = db.relationship('Canje', backref='recompensa', lazy='dynamic')
    
    def __repr__(self):
        return f'<Recompensa {self.nombre} - {self.puntos_requeridos} pts>'
    
    def to_dict(self):
        """Serializar recompensa a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'puntos_requeridos': self.puntos_requeridos,
            'stock': self.stock,
            'imagen_url': self.imagen_url,
            'categoria': self.categoria,
            'activo': self.activo,
            'disponible': self.stock > 0 and self.activo
        }
    
    def puede_canjearse(self, puntos_usuario: int) -> tuple:
        """
        Verificar si la recompensa puede canjearse.
        
        Returns:
            tuple: (puede_canjear: bool, mensaje: str)
        """
        if not self.activo:
            return False, "Recompensa no disponible"
        if self.stock <= 0:
            return False, "Sin stock disponible"
        if puntos_usuario < self.puntos_requeridos:
            return False, f"Puntos insuficientes (necesitas {self.puntos_requeridos})"
        return True, "OK"


class Canje(db.Model):
    """
    Registro de canjes de recompensas realizados por usuarios.
    """
    __tablename__ = 'canjes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer, 
        db.ForeignKey('usuarios.id'), 
        nullable=False,
        index=True
    )
    recompensa_id = db.Column(
        db.Integer, 
        db.ForeignKey('recompensas.id'), 
        nullable=False
    )
    puntos_gastados = db.Column(db.Integer, nullable=False)
    fecha_canje = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, entregado, cancelado
    codigo_canje = db.Column(db.String(20), unique=True, nullable=True)
    
    def __repr__(self):
        return f'<Canje {self.id} - Usuario {self.usuario_id}>'
    
    def to_dict(self):
        """Serializar canje a diccionario"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'recompensa_id': self.recompensa_id,
            'recompensa_nombre': self.recompensa.nombre if self.recompensa else None,
            'puntos_gastados': self.puntos_gastados,
            'fecha_canje': self.fecha_canje.isoformat(),
            'estado': self.estado,
            'codigo_canje': self.codigo_canje
        }
    
    @staticmethod
    def generar_codigo():
        """Generar código único de canje"""
        import secrets
        return f"ECO-{secrets.token_hex(4).upper()}"
