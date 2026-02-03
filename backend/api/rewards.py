"""
API Routes - Recompensas
Endpoints para catálogo de recompensas y canjes
"""

from flask import Blueprint, request, jsonify
from backend.services import RewardService
from backend.utils import get_api_logger

logger = get_api_logger()

rewards_bp = Blueprint('rewards', __name__, url_prefix='/api/rewards')


@rewards_bp.route('', methods=['GET'])
def listar_recompensas():
    """
    Listar todas las recompensas disponibles.
    
    Query params:
        todas (bool): Incluir recompensas inactivas (default: false)
    """
    try:
        incluir_todas = request.args.get('todas', 'false').lower() == 'true'
        recompensas = RewardService.listar_recompensas(
            solo_activas=not incluir_todas
        )
        
        return jsonify({
            'total': len(recompensas),
            'recompensas': recompensas
        }), 200
        
    except Exception as e:
        logger.error(f"Error en listar_recompensas: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@rewards_bp.route('/<int:recompensa_id>', methods=['GET'])
def obtener_recompensa(recompensa_id):
    """Obtener detalle de una recompensa específica"""
    try:
        recompensa = RewardService.obtener_recompensa(recompensa_id)
        
        if not recompensa:
            return jsonify({
                'error': 'Recompensa no encontrada'
            }), 404
        
        return jsonify(recompensa.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error en obtener_recompensa: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@rewards_bp.route('/redeem', methods=['POST'])
def canjear_recompensa():
    """
    Realizar canje de recompensa.
    
    Request JSON:
        {
            "usuario_id": 1,
            "recompensa_id": 5
        }
    
    Response JSON:
        {
            "exito": true,
            "codigo_canje": "ECO-A1B2C3D4",
            "puntos_restantes": 150
        }
    """
    try:
        datos = request.get_json()
        
        if not datos or 'usuario_id' not in datos or 'recompensa_id' not in datos:
            return jsonify({
                'error': 'Faltan parámetros: usuario_id, recompensa_id'
            }), 400
        
        exito, mensaje, resultado = RewardService.canjear_recompensa(
            usuario_id=datos['usuario_id'],
            recompensa_id=datos['recompensa_id']
        )
        
        if exito:
            return jsonify({
                'exito': True,
                'mensaje': mensaje,
                **resultado
            }), 200
        else:
            return jsonify({
                'exito': False,
                'error': mensaje
            }), 400
            
    except Exception as e:
        logger.error(f"Error en canjear_recompensa: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@rewards_bp.route('/history/<int:usuario_id>', methods=['GET'])
def historial_canjes(usuario_id):
    """Obtener historial de canjes de un usuario"""
    try:
        canjes = RewardService.obtener_historial_canjes(usuario_id)
        
        return jsonify({
            'total': len(canjes),
            'canjes': canjes
        }), 200
        
    except Exception as e:
        logger.error(f"Error en historial_canjes: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@rewards_bp.route('/canje/<int:canje_id>/estado', methods=['PUT'])
def actualizar_estado_canje(canje_id):
    """
    Actualizar estado de un canje.
    
    Request JSON:
        {"estado": "entregado"}
    
    Estados válidos: pendiente, entregado, cancelado
    """
    try:
        datos = request.get_json()
        
        if not datos or 'estado' not in datos:
            return jsonify({
                'error': 'Falta parámetro estado'
            }), 400
        
        exito, mensaje = RewardService.actualizar_estado_canje(
            canje_id, 
            datos['estado']
        )
        
        if exito:
            return jsonify({
                'exito': True,
                'mensaje': mensaje
            }), 200
        else:
            return jsonify({
                'error': mensaje
            }), 400
            
    except Exception as e:
        logger.error(f"Error en actualizar_estado_canje: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@rewards_bp.route('', methods=['POST'])
def crear_recompensa():
    """
    Crear nueva recompensa (admin).
    
    Request JSON:
        {
            "nombre": "Café gratis",
            "descripcion": "Un café en la cafetería",
            "puntos_requeridos": 50,
            "stock": 20,
            "categoria": "comida"
        }
    """
    try:
        datos = request.get_json()
        
        campos_requeridos = ['nombre', 'descripcion', 'puntos_requeridos']
        if not all(k in datos for k in campos_requeridos):
            return jsonify({
                'error': 'Faltan parámetros requeridos'
            }), 400
        
        exito, mensaje, recompensa = RewardService.crear_recompensa(
            nombre=datos['nombre'],
            descripcion=datos['descripcion'],
            puntos_requeridos=int(datos['puntos_requeridos']),
            stock=datos.get('stock', 10),
            categoria=datos.get('categoria', 'general'),
            imagen_url=datos.get('imagen_url')
        )
        
        if exito:
            return jsonify({
                'exito': True,
                'recompensa': recompensa.to_dict()
            }), 201
        else:
            return jsonify({
                'error': mensaje
            }), 400
            
    except Exception as e:
        logger.error(f"Error en crear_recompensa: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500
