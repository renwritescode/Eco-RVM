"""
Modelos de Base de Datos - Eco-RVM
Exportación centralizada de todos los modelos
"""

from backend.models.user import Usuario
from backend.models.transaction import Transaccion
from backend.models.reward import Recompensa, Canje
from backend.models.gamification import Badge, UsuarioBadge, BADGES_PREDEFINIDOS

__all__ = [
    'Usuario',
    'Transaccion',
    'Recompensa',
    'Canje',
    'Badge',
    'UsuarioBadge',
    'BADGES_PREDEFINIDOS'
]
