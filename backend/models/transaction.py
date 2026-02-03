"""
Modelos de Base de Datos - Transacción
"""

from datetime import datetime
from backend.extensions import db


class Transaccion(db.Model):
    """
    Registro de cada reciclaje realizado.
    Mantiene historial completo de actividad con datos de IA.
    """
    __tablename__ = 'transacciones'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(
        db.Integer, 
        db.ForeignKey('usuarios.id'), 
        nullable=False, 
        index=True
    )
    tipo_objeto = db.Column(db.String(50), nullable=False)
    puntos_otorgados = db.Column(db.Integer, nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resultado_ia = db.Column(db.String(100), nullable=True)
    confianza_ia = db.Column(db.Float, nullable=True)
    
    # Nuevos campos para impacto ambiental
    peso_estimado_kg = db.Column(db.Float, nullable=True)
    co2_evitado_kg = db.Column(db.Float, nullable=True)
    imagen_path = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<Transaccion {self.id} - Usuario {self.usuario_id} - {self.tipo_objeto}>'
    
    def to_dict(self):
        """Serializar transacción a diccionario"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'tipo_objeto': self.tipo_objeto,
            'puntos_otorgados': self.puntos_otorgados,
            'fecha_hora': self.fecha_hora.isoformat(),
            'resultado_ia': self.resultado_ia,
            'confianza_ia': self.confianza_ia,
            'peso_estimado_kg': self.peso_estimado_kg,
            'co2_evitado_kg': self.co2_evitado_kg,
            'imagen_path': self.imagen_path
        }
    
    @staticmethod
    def calcular_impacto(tipo_objeto: str) -> tuple:
        """
        Calcular peso y CO2 evitado según tipo de objeto.
        
        Returns:
            tuple: (peso_kg, co2_kg)
        """
        # Factores de impacto por tipo
        impactos = {
            'plastico_metal': (0.025, 0.05),
            'plastico': (0.025, 0.05),
            'metal': (0.015, 0.03),
            'botella': (0.025, 0.05),
            'lata': (0.015, 0.03),
        }
        return impactos.get(tipo_objeto.lower(), (0.02, 0.04))
