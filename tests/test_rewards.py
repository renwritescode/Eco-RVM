"""
Tests de Eco-RVM - Recompensas
"""


class TestRewardsAPI:
    """Tests para endpoints de recompensas"""
    
    def test_list_rewards(self, client, sample_reward):
        """Listar recompensas"""
        response = client.get('/api/rewards')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'recompensas' in data
        assert data['total'] >= 1
    
    def test_get_reward_detail(self, client, sample_reward):
        """Obtener detalle de recompensa"""
        response = client.get(f'/api/rewards/{sample_reward.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['nombre'] == 'Test Reward'
        assert data['puntos_requeridos'] == 50
    
    def test_get_reward_not_found(self, client):
        """Recompensa inexistente"""
        response = client.get('/api/rewards/99999')
        
        assert response.status_code == 404
    
    def test_redeem_reward_success(self, client, sample_user, sample_reward, app):
        """Canjear recompensa exitosamente"""
        from backend.models import Usuario
        from backend.extensions import db
        
        response = client.post('/api/rewards/redeem', json={
            'usuario_id': sample_user.id,
            'recompensa_id': sample_reward.id
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['exito'] is True
        assert 'codigo_canje' in data
        assert data['puntos_restantes'] == 50  # 100 - 50
    
    def test_redeem_insufficient_points(self, client, sample_reward, app):
        """Canjear sin puntos suficientes"""
        from backend.models import Usuario
        from backend.extensions import db
        
        # Crear usuario con pocos puntos
        with app.app_context():
            poor_user = Usuario(
                uid_rfid='04POORUSER123',
                nombre='Poor',
                apellido='User',
                email='poor@test.com',
                puntos_totales=10  # Menos de 50 requeridos
            )
            db.session.add(poor_user)
            db.session.commit()
            user_id = poor_user.id
        
        response = client.post('/api/rewards/redeem', json={
            'usuario_id': user_id,
            'recompensa_id': sample_reward.id
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['exito'] is False
        
        # Limpiar
        with app.app_context():
            user = Usuario.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
    
    def test_redeem_missing_params(self, client):
        """Canjear sin parámetros"""
        response = client.post('/api/rewards/redeem', json={})
        
        assert response.status_code == 400
    
    def test_user_redemption_history(self, client, sample_user):
        """Historial de canjes de usuario"""
        response = client.get(f'/api/rewards/history/{sample_user.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'canjes' in data
    
    def test_create_reward(self, client, app):
        """Crear nueva recompensa"""
        from backend.models import Recompensa
        from backend.extensions import db
        
        response = client.post('/api/rewards', json={
            'nombre': 'Nueva Recompensa',
            'descripcion': 'Descripcion de prueba para la recompensa',
            'puntos_requeridos': 100,
            'stock': 5,
            'categoria': 'test'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['exito'] is True
        
        # Limpiar
        with app.app_context():
            reward = Recompensa.query.filter_by(nombre='Nueva Recompensa').first()
            if reward:
                db.session.delete(reward)
                db.session.commit()
