"""
API Routes - Transacciones y Puntos
Endpoints para gestión de puntos y transacciones de reciclaje
"""

from flask import Blueprint, request, jsonify
from backend.services import PointsService, UserService
from backend.utils import get_api_logger

logger = get_api_logger()

transactions_bp = Blueprint('transactions', __name__, url_prefix='/api')


@transactions_bp.route('/add_points', methods=['POST'])
def agregar_puntos():
    """
    Agregar puntos a un usuario y registrar transacción.
    
    Request JSON:
        {
            "uid": "04A1B2C3D4E5F6",
            "puntos": 10,
            "tipo_objeto": "botella",
            "resultado_ia": "Botella PET",
            "confianza_ia": 0.95
        }
    
    Response JSON:
        {
            "exito": true,
            "puntos_nuevos": 50,
            "transaccion_id": 123,
            "impacto": {...},
            "badges_nuevos": [...]
        }
    """
    try:
        datos = request.get_json()
        
        # Validar parámetros requeridos
        if not datos or 'uid' not in datos or 'puntos' not in datos:
            return jsonify({
                'error': 'Faltan parámetros requeridos: uid, puntos'
            }), 400
        
        exito, mensaje, resultado = PointsService.agregar_puntos(
            uid_rfid=datos['uid'],
            puntos=int(datos['puntos']),
            tipo_objeto=datos.get('tipo_objeto', 'desconocido'),
            resultado_ia=datos.get('resultado_ia'),
            confianza_ia=datos.get('confianza_ia'),
            imagen_path=datos.get('imagen_path')
        )
        
        if exito:
            return jsonify({
                'exito': True,
                'mensaje': mensaje,
                **resultado
            }), 200
        else:
            return jsonify({
                'error': mensaje
            }), 400
            
    except ValueError as e:
        return jsonify({
            'error': 'El valor de puntos debe ser un número entero'
        }), 400
    except Exception as e:
        logger.error(f"Error en agregar_puntos: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@transactions_bp.route('/transacciones/<int:usuario_id>', methods=['GET'])
def obtener_transacciones(usuario_id):
    """
    Obtener historial de transacciones de un usuario.
    
    Query params:
        limite (int): Número de transacciones a retornar (default: 50)
    """
    try:
        usuario = UserService.obtener_por_id(usuario_id)
        if not usuario:
            return jsonify({
                'error': 'Usuario no encontrado'
            }), 404
        
        limite = request.args.get('limite', 50, type=int)
        transacciones = PointsService.obtener_transacciones_usuario(
            usuario_id, 
            limite
        )
        
        return jsonify({
            'total': len(transacciones),
            'usuario': usuario.to_dict(),
            'transacciones': transacciones
        }), 200
        
    except Exception as e:
        logger.error(f"Error en obtener_transacciones: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@transactions_bp.route('/transacciones/recientes', methods=['GET'])
def transacciones_recientes():
    """
    Obtener transacciones más recientes del sistema.
    
    Query params:
        limite (int): Número de transacciones (default: 20)
    """
    try:
        limite = request.args.get('limite', 20, type=int)
        transacciones = PointsService.obtener_transacciones_recientes(limite)
        
        return jsonify({
            'total': len(transacciones),
            'transacciones': transacciones
        }), 200
        
    except Exception as e:
        logger.error(f"Error en transacciones_recientes: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500
