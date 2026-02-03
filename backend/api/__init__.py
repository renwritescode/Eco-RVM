"""
API Routes - Eco-RVM
Registro centralizado de todos los blueprints
"""

from backend.api.users import users_bp
from backend.api.transactions import transactions_bp
from backend.api.rewards import rewards_bp
from backend.api.stats import stats_bp


def register_blueprints(app):
    """Registrar todos los blueprints de API en la aplicación Flask"""
    app.register_blueprint(users_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(stats_bp)
    
    return app


__all__ = [
    'users_bp',
    'transactions_bp',
    'rewards_bp',
    'stats_bp',
    'register_blueprints'
]
