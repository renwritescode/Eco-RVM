"""
Extensiones Flask para Eco-RVM
Inicialización centralizada de extensiones
"""

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager

# Instancias de extensiones (sin inicializar)
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
login_manager = LoginManager()

# Configuración de Flask-Login
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    """Callback para cargar usuario desde la sesión"""
    from backend.models import Usuario
    return Usuario.query.get(int(user_id))


def init_extensions(app):
    """Inicializar todas las extensiones con la aplicación Flask"""
    db.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    return app
