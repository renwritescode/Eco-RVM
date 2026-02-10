"""
API Routes - Usuarios
Endpoints para gestión de usuarios y verificación RFID
"""

from flask import Blueprint, request, jsonify
from backend.services import UserService
from backend.utils import get_api_logger

logger = get_api_logger()

users_bp = Blueprint('users', __name__, url_prefix='/api')


@users_bp.route('/check_user', methods=['POST'])
def verificar_usuario():
    """
    Verificar si un usuario existe por UID de RFID.
    
    Request JSON:
        {"uid": "04A1B2C3D4E5F6"}
    
    Response JSON:
        {"existe": true, "usuario": {...}}
    """
    try:
        datos = request.get_json()
        
        if not datos or 'uid' not in datos:
            return jsonify({
                'error': 'Falta parámetro uid en el request'
            }), 400
        
        existe, usuario = UserService.verificar_usuario(datos['uid'])
        
        if existe:
            return jsonify({
                'existe': True,
                'usuario': usuario
            }), 200
        else:
            return jsonify({
                'existe': False,
                'mensaje': 'Usuario no encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error en verificar_usuario: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@users_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """
    Obtener lista completa de usuarios.
    
    Response JSON:
        {"total": 3, "usuarios": [...]}
    """
    try:
        usuarios = UserService.listar_usuarios()
        
        return jsonify({
            'total': len(usuarios),
            'usuarios': [u.to_dict() for u in usuarios]
        }), 200
        
    except Exception as e:
        logger.error(f"Error en listar_usuarios: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@users_bp.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    """
    Registrar un nuevo usuario en el sistema.
    
    Request JSON:
        {
            "uid": "04AABBCCDDEE",
            "nombre": "Pedro",
            "apellido": "Martinez",
            "email": "pedro@universidad.edu"
        }
    """
    try:
        datos = request.get_json()
        
        campos_requeridos = ['uid', 'nombre', 'apellido', 'email']
        if not all(k in datos for k in campos_requeridos):
            return jsonify({
                'error': 'Faltan parámetros requeridos'
            }), 400
        
        exito, mensaje, usuario = UserService.registrar_usuario(
            uid_rfid=datos['uid'],
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            email=datos['email']
        )
        
        if exito:
            return jsonify({
                'exito': True,
                'usuario': usuario.to_dict(),
                'mensaje': mensaje
            }), 201
        else:
            return jsonify({
                'error': mensaje
            }), 409
            
    except Exception as e:
        logger.error(f"Error en registrar_usuario: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@users_bp.route('/ranking', methods=['GET'])
def obtener_ranking():
    """
    Obtener ranking de usuarios por puntos.
    
    Query params:
        limite (int): Número de usuarios a retornar (default: 10)
    """
    try:
        limite = request.args.get('limite', 10, type=int)
        ranking = UserService.obtener_ranking(limite)
        
        return jsonify({
            'total': len(ranking),
            'ranking': ranking
        }), 200
        
    except Exception as e:
        logger.error(f"Error en obtener_ranking: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@users_bp.route('/usuario/<int:usuario_id>/badges', methods=['GET'])
def obtener_badges_usuario(usuario_id):
    """Obtener badges de un usuario específico"""
    try:
        badges = UserService.obtener_badges_usuario(usuario_id)
        return jsonify({
            'total': len(badges),
            'badges': badges
        }), 200
        
    except Exception as e:
        logger.error(f"Error en obtener_badges_usuario: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@users_bp.route('/vincular_tarjeta', methods=['POST'])
def vincular_tarjeta():
    """
    Vincular tarjeta RFID física a cuenta existente.
    Usado por Arduino cuando detecta tarjeta nueva y usuario ingresa código.
    
    Request JSON:
        {
            "uid_fisico": "04A1B2C3D4E5F6",  // UID leído por el lector RFID
            "codigo_virtual": "4A7B2C"        // Código ingresado por keypad
        }
    
    Response JSON (éxito):
        {
            "exito": true,
            "mensaje": "Tarjeta vinculada exitosamente",
            "usuario": {...}
        }
    
    Response JSON (error):
        {
            "exito": false,
            "error": "Código no encontrado"
        }
    """
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({
                'exito': False,
                'error': 'No se recibieron datos'
            }), 400
        
        uid_fisico = datos.get('uid_fisico', '').upper().strip()
        codigo_virtual = datos.get('codigo_virtual', '').upper().strip()
        
        if not uid_fisico or len(uid_fisico) < 8:
            return jsonify({
                'exito': False,
                'error': 'UID de tarjeta inválido'
            }), 400
        
        if not codigo_virtual or len(codigo_virtual) != 6:
            return jsonify({
                'exito': False,
                'error': 'Código debe tener 6 caracteres'
            }), 400
        
        # Buscar usuario por código virtual
        from backend.models import Usuario
        from backend.extensions import db
        
        usuario = Usuario.query.filter_by(codigo_virtual=codigo_virtual).first()
        
        if not usuario:
            logger.warning(f"Intento de vincular con código inexistente: {codigo_virtual}")
            return jsonify({
                'exito': False,
                'error': 'Código no encontrado'
            }), 404
        
        # Verificar que la tarjeta no esté ya vinculada a otra cuenta
        tarjeta_existente = Usuario.query.filter_by(uid_rfid=uid_fisico).first()
        if tarjeta_existente:
            return jsonify({
                'exito': False,
                'error': 'Esta tarjeta ya está vinculada a otra cuenta'
            }), 409
        
        # Vincular tarjeta
        if usuario.vincular_tarjeta(uid_fisico):
            db.session.commit()
            logger.info(f"Tarjeta vinculada: {uid_fisico} -> {usuario.email}")
            return jsonify({
                'exito': True,
                'mensaje': 'Tarjeta vinculada exitosamente',
                'usuario': usuario.to_dict()
            }), 200
        else:
            return jsonify({
                'exito': False,
                'error': 'Error al vincular tarjeta'
            }), 500
            
    except Exception as e:
        logger.error(f"Error en vincular_tarjeta: {e}")
        return jsonify({
            'exito': False,
            'error': f'Error en el servidor: {str(e)}'
        }), 500


@users_bp.route('/login_codigo/<string:codigo>', methods=['GET'])
def login_por_codigo(codigo):
    """
    Autenticar usuario por código virtual (para login por keypad).
    Usa el campo codigo_virtual existente en lugar de ID numérico.
    
    Args:
        codigo: Código virtual del usuario (ej: ECO-DEMO001, 33A40A)
    
    Response JSON (éxito):
        {
            "existe": true,
            "usuario": {
                "id": 1,
                "nombre": "Juan",
                "apellido": "Perez",
                "codigo_virtual": "ECO-DEMO001",
                "email": "juan@universidad.edu",
                "puntos_totales": 150,
                ...
            }
        }
    
    Response JSON (error):
        {
            "existe": false,
            "mensaje": "Código no encontrado"
        }
    """
    try:
        from backend.models import Usuario
        
        # Buscar por codigo_virtual (campo existente)
        codigo_upper = codigo.upper().strip()
        usuario = Usuario.query.filter_by(codigo_virtual=codigo_upper).first()
        
        if usuario and usuario.activo:
            nombre_completo = f"{usuario.nombre} {usuario.apellido}"
            logger.info(f"Login por código: {nombre_completo} ({codigo_upper})")
            return jsonify({
                'existe': True,
                'usuario': usuario.to_dict()
            }), 200
        else:
            logger.warning(f"Código no encontrado: {codigo}")
            return jsonify({
                'existe': False,
                'mensaje': 'Código no encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error en login_por_codigo: {e}")
        return jsonify({
            'error': f'Error en el servidor: {str(e)}'
        }), 500
