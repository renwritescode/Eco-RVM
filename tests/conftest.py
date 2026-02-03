"""
Configuración de Pytest para Tests de Eco-RVM
"""

import sys
from pathlib import Path
import pytest

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app import create_app
from backend.extensions import db
from backend.config import TestingConfig


@pytest.fixture(scope='session')
def app():
    """Crear aplicación Flask para tests"""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Cliente HTTP para tests"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Sesión de base de datos con rollback automático"""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        yield db.session
        
        transaction.rollback()
        connection.close()


@pytest.fixture
def sample_user(app):
    """Usuario de prueba"""
    from backend.models import Usuario
    
    with app.app_context():
        user = Usuario(
            uid_rfid='04TEST123456',
            nombre='Test',
            apellido='User',
            email='test@test.com',
            puntos_totales=100
        )
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        # Limpiar
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def sample_reward(app):
    """Recompensa de prueba"""
    from backend.models import Recompensa
    
    with app.app_context():
        reward = Recompensa(
            nombre='Test Reward',
            descripcion='Reward for testing',
            puntos_requeridos=50,
            stock=10,
            categoria='test'
        )
        db.session.add(reward)
        db.session.commit()
        
        yield reward
        
        # Limpiar
        db.session.delete(reward)
        db.session.commit()
