"""
API Routes - Estadísticas
Endpoints para estadísticas e impacto ambiental
"""

from flask import Blueprint, request, jsonify
from backend.services import StatsService
from backend.utils import get_api_logger

logger = get_api_logger()

stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats')


@stats_bp.route('/general', methods=['GET'])
def estadisticas_generales():
    """
    Obtener estadísticas generales del sistema.
    
    Response JSON:
        {
            "total_usuarios": 50,
            "total_transacciones": 1200,
            "total_puntos_sistema": 12000,
            "promedio_puntos_usuario": 240
        }
    """
    try:
        stats = StatsService.obtener_estadisticas_generales()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error en estadisticas_generales: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@stats_bp.route('/impacto', methods=['GET'])
def impacto_ambiental():
    """
    Obtener métricas de impacto ambiental.
    
    Response JSON:
        {
            "peso_reciclado_kg": 45.5,
            "co2_evitado_kg": 91.0,
            "total_reciclajes": 1820,
            "equivalencias": {
                "arboles_plantados": 4.13,
                "litros_agua_ahorrados": 5460,
                "kwh_energia_ahorrada": 72.8
            }
        }
    """
    try:
        impacto = StatsService.obtener_impacto_ambiental()
        return jsonify(impacto), 200
        
    except Exception as e:
        logger.error(f"Error en impacto_ambiental: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@stats_bp.route('/impacto/<int:usuario_id>', methods=['GET'])
def impacto_usuario(usuario_id):
    """Obtener impacto ambiental de un usuario específico"""
    try:
        impacto = StatsService.obtener_impacto_usuario(usuario_id)
        return jsonify(impacto), 200
        
    except Exception as e:
        logger.error(f"Error en impacto_usuario: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@stats_bp.route('/reciclajes/periodo', methods=['GET'])
def reciclajes_por_periodo():
    """
    Obtener reciclajes por día en los últimos N días.
    
    Query params:
        dias (int): Número de días a consultar (default: 7)
    
    Response JSON:
        {
            "2026-01-30": 15,
            "2026-01-31": 22,
            "2026-02-01": 18
        }
    """
    try:
        dias = request.args.get('dias', 7, type=int)
        datos = StatsService.obtener_reciclajes_por_periodo(dias)
        return jsonify(datos), 200
        
    except Exception as e:
        logger.error(f"Error en reciclajes_por_periodo: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@stats_bp.route('/top-recicladores', methods=['GET'])
def top_recicladores():
    """
    Obtener usuarios con más reciclajes en el mes actual.
    
    Query params:
        limite (int): Número de usuarios (default: 5)
    """
    try:
        limite = request.args.get('limite', 5, type=int)
        top = StatsService.obtener_top_recicladores(limite)
        
        return jsonify({
            'total': len(top),
            'top_recicladores': top
        }), 200
        
    except Exception as e:
        logger.error(f"Error en top_recicladores: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@stats_bp.route('/dashboard', methods=['GET'])
def dashboard_completo():
    """
    Obtener todos los datos para el dashboard en una sola llamada.
    
    Response JSON:
        {
            "estadisticas": {...},
            "impacto_ambiental": {...},
            "reciclajes_semana": {...},
            "top_recicladores": [...]
        }
    """
    try:
        return jsonify({
            'estadisticas': StatsService.obtener_estadisticas_generales(),
            'impacto_ambiental': StatsService.obtener_impacto_ambiental(),
            'reciclajes_semana': StatsService.obtener_reciclajes_por_periodo(7),
            'top_recicladores': StatsService.obtener_top_recicladores(5)
        }), 200
        
    except Exception as e:
        logger.error(f"Error en dashboard_completo: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500
