"""
Flask Application Factory - Eco-RVM
Patrón Factory para crear la aplicación Flask con Autenticación
"""

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from backend.config import get_config
from backend.extensions import init_extensions, db
from backend.api import register_blueprints
from backend.utils import setup_logger


def create_app(config_class=None):
    """
    Factory para crear la aplicación Flask.
    
    Args:
        config_class: Clase de configuración a usar (opcional)
    
    Returns:
        Flask: Aplicación Flask configurada
    """
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )
    
    # Cargar configuración
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    init_extensions(app)
    
    # Registrar blueprints de API
    register_blueprints(app)
    
    # Registrar rutas web (templates)
    register_auth_routes(app)
    register_web_routes(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Crear tablas y datos iniciales
    with app.app_context():
        db.create_all()
        seed_initial_data()
    
    return app


def register_auth_routes(app):
    """Registrar rutas de autenticación"""
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Página de login"""
        # Si ya está autenticado, redirigir al dashboard
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            from backend.services import AuthService
            
            email = request.form.get('email', '')
            password = request.form.get('password', '')
            remember = request.form.get('remember', False)
            
            exito, mensaje, usuario = AuthService.login(email, password)
            
            if exito:
                login_user(usuario, remember=bool(remember))
                flash(f'¡Bienvenido, {usuario.nombre}!', 'success')
                
                # Redirigir a la página solicitada o al dashboard
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash(mensaje, 'danger')
        
        return render_template('login.html')
    
    @app.route('/registro', methods=['GET', 'POST'])
    def registro():
        """Página de registro de nuevos usuarios"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            from backend.services import AuthService
            
            nombre = request.form.get('nombre', '')
            apellido = request.form.get('apellido', '')
            email = request.form.get('email', '')
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')
            
            # Validaciones básicas
            if not all([nombre, apellido, email, password]):
                flash('Todos los campos son obligatorios', 'danger')
                return render_template('registro.html')
            
            if password != password_confirm:
                flash('Las contraseñas no coinciden', 'danger')
                return render_template('registro.html')
            
            if len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'danger')
                return render_template('registro.html')
            
            exito, mensaje, usuario = AuthService.registrar_usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                password=password
            )
            
            if exito:
                login_user(usuario)
                flash(f'¡Cuenta creada exitosamente! Tu código virtual es: {usuario.codigo_virtual}', 'success')
                return redirect(url_for('perfil'))
            else:
                flash(mensaje, 'danger')
        
        return render_template('registro.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Cerrar sesión"""
        logout_user()
        flash('Sesión cerrada correctamente', 'info')
        return redirect(url_for('login'))


def register_web_routes(app):
    """Registrar rutas web para renderizar templates"""
    
    @app.route('/')
    @login_required
    def index():
        """Página principal - Dashboard general"""
        from backend.models import Usuario
        from backend.services import StatsService
        
        # Top 10 usuarios
        usuarios = Usuario.query.filter_by(activo=True)\
            .order_by(Usuario.puntos_totales.desc()).limit(10).all()
        
        # Estadísticas generales
        stats = StatsService.obtener_estadisticas_generales()
        impacto = StatsService.obtener_impacto_ambiental()
        
        return render_template(
            'index.html', 
            usuarios=usuarios, 
            stats=stats,
            impacto=impacto
        )
    
    @app.route('/perfil')
    @login_required
    def perfil():
        """Dashboard personal del usuario logueado"""
        from backend.services import UserService, StatsService
        from backend.models import Transaccion
        
        # Obtener datos del usuario actual
        badges = UserService.obtener_badges_usuario(current_user.id)
        impacto = StatsService.obtener_impacto_usuario(current_user.id)
        
        # Obtener transacciones como objetos (no dicts) para el template
        transacciones = Transaccion.query.filter_by(usuario_id=current_user.id)\
            .order_by(Transaccion.fecha_hora.desc()).limit(20).all()
        
        return render_template(
            'perfil.html',
            usuario=current_user,
            badges=badges,
            impacto=impacto,
            transacciones=transacciones
        )
    
    @app.route('/estadisticas')
    @login_required
    def estadisticas():
        """Panel de estadísticas generales del sistema"""
        from backend.services import StatsService, PointsService
        
        stats = StatsService.obtener_estadisticas_generales()
        impacto = StatsService.obtener_impacto_ambiental()
        reciclajes_semana = StatsService.obtener_reciclajes_por_periodo(7)
        transacciones = PointsService.obtener_transacciones_recientes(20)
        
        return render_template(
            'estadisticas.html',
            stats=stats,
            impacto=impacto,
            reciclajes_semana=reciclajes_semana,
            transacciones=transacciones
        )
    
    @app.route('/recompensas')
    @login_required
    def recompensas():
        """Catálogo de recompensas"""
        from backend.services import RewardService
        recompensas_list = RewardService.listar_recompensas()
        return render_template(
            'recompensas.html', 
            recompensas=recompensas_list,
            puntos_usuario=current_user.puntos_totales
        )
    
    @app.route('/canjear/<int:recompensa_id>', methods=['POST'])
    @login_required
    def canjear_recompensa(recompensa_id):
        """Canjear una recompensa (auto-débito del usuario logueado)"""
        from backend.services import RewardService
        
        exito, mensaje, datos = RewardService.canjear_recompensa(
            usuario_id=current_user.id,
            recompensa_id=recompensa_id
        )
        
        if exito:
            flash(f'¡Canje exitoso! Código: {datos["codigo_canje"]}', 'success')
        else:
            flash(mensaje, 'danger')
        
        return redirect(url_for('recompensas'))
    
    # Ruta legacy para compatibilidad
    @app.route('/usuario/<int:usuario_id>')
    @login_required
    def detalle_usuario(usuario_id):
        """Vista detallada de un usuario (admin o perfil propio)"""
        from backend.models import Usuario, Transaccion
        from backend.services import UserService, StatsService
        
        # Solo puede ver su propio perfil o si es admin (futuro)
        if usuario_id != current_user.id:
            flash('No tienes permiso para ver este perfil', 'warning')
            return redirect(url_for('perfil'))
        
        return redirect(url_for('perfil'))


def register_error_handlers(app):
    """Registrar manejadores de errores HTTP"""
    from flask import jsonify
    
    @app.errorhandler(404)
    def no_encontrado(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Recurso no encontrado'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def error_servidor(error):
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    @app.errorhandler(401)
    def no_autorizado(error):
        flash('Debes iniciar sesión para acceder', 'warning')
        return redirect(url_for('login'))


def seed_initial_data():
    """Insertar datos iniciales si la base está vacía"""
    from backend.models import (
        Usuario, Recompensa, Badge, 
        BADGES_PREDEFINIDOS
    )
    
    # Insertar usuarios de prueba
    if Usuario.query.count() == 0:
        usuarios_prueba = [
            {
                'uid_rfid': '04A1B2C3D4E5F6',
                'codigo_virtual': 'ECO-DEMO001',
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'email': 'juan@demo.com',
                'password': 'demo123',
                'puntos_totales': 150
            },
            {
                'uid_rfid': '04F6E5D4C3B2A1',
                'codigo_virtual': 'ECO-DEMO002',
                'nombre': 'María',
                'apellido': 'González',
                'email': 'maria@demo.com',
                'password': 'demo123',
                'puntos_totales': 280
            },
            {
                'uid_rfid': '041234567890AB',
                'codigo_virtual': 'ECO-DEMO003',
                'nombre': 'Carlos',
                'apellido': 'Ramírez',
                'email': 'carlos@demo.com',
                'password': 'demo123',
                'puntos_totales': 75
            }
        ]
        
        for data in usuarios_prueba:
            usuario = Usuario(
                uid_rfid=data['uid_rfid'],
                codigo_virtual=data['codigo_virtual'],
                nombre=data['nombre'],
                apellido=data['apellido'],
                email=data['email'],
                puntos_totales=data['puntos_totales']
            )
            usuario.set_password(data['password'])
            db.session.add(usuario)
        
        print(f"[DB] Se insertaron {len(usuarios_prueba)} usuarios de prueba")
        print("[DB] Credenciales demo: email=juan@demo.com, password=demo123")
    
    # Insertar recompensas de prueba
    if Recompensa.query.count() == 0:
        recompensas = [
            Recompensa(
                nombre='Café Gratis',
                descripcion='Un café de tu elección en la cafetería del campus',
                puntos_requeridos=50,
                stock=20,
                categoria='comida',
                imagen_url='/static/img/rewards/coffee.png'
            ),
            Recompensa(
                nombre='Descuento Librería 10%',
                descripcion='10% de descuento en tu próxima compra en la librería',
                puntos_requeridos=100,
                stock=50,
                categoria='descuentos',
                imagen_url='/static/img/rewards/discount.png'
            ),
            Recompensa(
                nombre='Entrada Cine',
                descripcion='Una entrada para cualquier función en el cine universitario',
                puntos_requeridos=200,
                stock=15,
                categoria='entretenimiento',
                imagen_url='/static/img/rewards/cinema.png'
            ),
            Recompensa(
                nombre='Botella Ecológica',
                descripcion='Botella de agua reutilizable con logo de Eco-RVM',
                puntos_requeridos=300,
                stock=30,
                categoria='productos',
                imagen_url='/static/img/rewards/bottle.png'
            ),
            Recompensa(
                nombre='Donación a ONG Ambiental',
                descripcion='Tus puntos se convierten en una donación para proteger el ambiente',
                puntos_requeridos=500,
                stock=999,
                categoria='donacion',
                imagen_url='/static/img/rewards/donate.png'
            )
        ]
        
        for recompensa in recompensas:
            db.session.add(recompensa)
        
        print(f"[DB] Se insertaron {len(recompensas)} recompensas")
    
    # Insertar badges predefinidos
    if Badge.query.count() == 0:
        for badge_data in BADGES_PREDEFINIDOS:
            badge = Badge(**badge_data)
            db.session.add(badge)
        
        print(f"[DB] Se insertaron {len(BADGES_PREDEFINIDOS)} badges")
    
    db.session.commit()
