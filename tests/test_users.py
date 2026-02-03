"""
Tests de Eco-RVM - Usuarios
"""


class TestUserAPI:
    """Tests para endpoints de usuarios"""
    
    def test_check_user_exists(self, client, sample_user):
        """Verificar usuario existente"""
        response = client.post('/api/check_user', json={
            'uid': sample_user.uid_rfid
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['existe'] is True
        assert data['usuario']['nombre'] == 'Test'
    
    def test_check_user_not_found(self, client):
        """Verificar usuario inexistente"""
        response = client.post('/api/check_user', json={
            'uid': '04NOEXISTE123'
        })
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['existe'] is False
    
    def test_check_user_missing_uid(self, client):
        """Verificar error sin UID"""
        response = client.post('/api/check_user', json={})
        
        assert response.status_code == 400
    
    def test_register_user_success(self, client, app):
        """Registrar usuario nuevo"""
        from backend.models import Usuario
        from backend.extensions import db
        
        response = client.post('/api/registrar_usuario', json={
            'uid': '04NEWUSER1234',
            'nombre': 'Nuevo',
            'apellido': 'Usuario',
            'email': 'nuevo@test.com'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['exito'] is True
        assert data['usuario']['nombre'] == 'Nuevo'
        
        # Limpiar
        with app.app_context():
            user = Usuario.query.filter_by(uid_rfid='04NEWUSER1234').first()
            if user:
                db.session.delete(user)
                db.session.commit()
    
    def test_register_user_duplicate_uid(self, client, sample_user):
        """Registrar usuario con UID duplicado"""
        response = client.post('/api/registrar_usuario', json={
            'uid': sample_user.uid_rfid,
            'nombre': 'Otro',
            'apellido': 'Usuario',
            'email': 'otro@test.com'
        })
        
        assert response.status_code == 409
    
    def test_list_users(self, client, sample_user):
        """Listar usuarios"""
        response = client.get('/api/usuarios')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] >= 1
        assert isinstance(data['usuarios'], list)
    
    def test_ranking(self, client, sample_user):
        """Obtener ranking"""
        response = client.get('/api/ranking?limite=5')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'ranking' in data
