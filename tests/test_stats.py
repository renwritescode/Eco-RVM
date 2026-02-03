"""
Tests de Eco-RVM - Estadísticas e Impacto Ambiental
"""


class TestStatsAPI:
    """Tests para endpoints de estadísticas"""
    
    def test_general_stats(self, client, sample_user):
        """Obtener estadísticas generales"""
        response = client.get('/api/stats/general')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_usuarios' in data
        assert 'total_transacciones' in data
        assert 'total_puntos_sistema' in data
        assert 'promedio_puntos_usuario' in data
    
    def test_environmental_impact(self, client):
        """Obtener impacto ambiental"""
        response = client.get('/api/stats/impacto')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'peso_reciclado_kg' in data
        assert 'co2_evitado_kg' in data
        assert 'total_reciclajes' in data
        assert 'equivalencias' in data
        assert 'arboles_plantados' in data['equivalencias']
    
    def test_user_impact(self, client, sample_user):
        """Obtener impacto de usuario específico"""
        response = client.get(f'/api/stats/impacto/{sample_user.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'peso_reciclado_kg' in data
        assert 'co2_evitado_kg' in data
    
    def test_recycling_by_period(self, client):
        """Obtener reciclajes por período"""
        response = client.get('/api/stats/reciclajes/periodo?dias=7')
        
        assert response.status_code == 200
        data = response.get_json()
        # Debería ser un diccionario con fechas como claves
        assert isinstance(data, dict)
    
    def test_top_recyclers(self, client, sample_user):
        """Obtener top recicladores"""
        response = client.get('/api/stats/top-recicladores?limite=3')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'top_recicladores' in data
    
    def test_dashboard_complete(self, client, sample_user):
        """Obtener dashboard completo"""
        response = client.get('/api/stats/dashboard')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'estadisticas' in data
        assert 'impacto_ambiental' in data
        assert 'reciclajes_semana' in data
        assert 'top_recicladores' in data
