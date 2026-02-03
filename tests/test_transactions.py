"""
Tests de Eco-RVM - Transacciones y Puntos
"""


class TestTransactionsAPI:
    """Tests para endpoints de transacciones"""
    
    def test_add_points_success(self, client, sample_user, app):
        """Agregar puntos exitosamente"""
        from backend.models import Usuario
        from backend.extensions import db
        
        initial_points = sample_user.puntos_totales
        
        response = client.post('/api/add_points', json={
            'uid': sample_user.uid_rfid,
            'puntos': 10,
            'tipo_objeto': 'botella',
            'resultado_ia': 'Aceptado',
            'confianza_ia': 0.95
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['exito'] is True
        assert data['puntos_nuevos'] == initial_points + 10
        assert 'transaccion_id' in data
        assert 'impacto' in data
    
    def test_add_points_user_not_found(self, client):
        """Agregar puntos a usuario inexistente"""
        response = client.post('/api/add_points', json={
            'uid': '04NOEXISTE123',
            'puntos': 10,
            'tipo_objeto': 'botella'
        })
        
        assert response.status_code == 400
    
    def test_add_points_missing_params(self, client):
        """Agregar puntos sin parámetros requeridos"""
        response = client.post('/api/add_points', json={
            'uid': '04TEST123456'
        })
        
        assert response.status_code == 400
    
    def test_add_points_zero(self, client, sample_user):
        """No se pueden agregar 0 puntos"""
        response = client.post('/api/add_points', json={
            'uid': sample_user.uid_rfid,
            'puntos': 0,
            'tipo_objeto': 'test'
        })
        
        assert response.status_code == 400
    
    def test_get_user_transactions(self, client, sample_user):
        """Obtener transacciones de usuario"""
        # Primero agregar una transacción
        client.post('/api/add_points', json={
            'uid': sample_user.uid_rfid,
            'puntos': 5,
            'tipo_objeto': 'lata'
        })
        
        response = client.get(f'/api/transacciones/{sample_user.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'transacciones' in data
        assert len(data['transacciones']) >= 1
    
    def test_get_transactions_user_not_found(self, client):
        """Transacciones de usuario inexistente"""
        response = client.get('/api/transacciones/99999')
        
        assert response.status_code == 404
    
    def test_recent_transactions(self, client, sample_user):
        """Obtener transacciones recientes"""
        response = client.get('/api/transacciones/recientes')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'transacciones' in data
