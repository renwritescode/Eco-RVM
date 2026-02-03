"""
Validadores con Marshmallow - Eco-RVM
Schemas para validación de datos de entrada
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


class UsuarioSchema(Schema):
    """Schema para validación de datos de usuario"""
    
    uid = fields.String(
        required=True,
        validate=validate.Length(min=8, max=20),
        error_messages={'required': 'El UID es requerido'}
    )
    nombre = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'El nombre es requerido'}
    )
    apellido = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={'required': 'El apellido es requerido'}
    )
    email = fields.Email(
        required=True,
        error_messages={
            'required': 'El email es requerido',
            'invalid': 'Email inválido'
        }
    )


class PuntosSchema(Schema):
    """Schema para validación de agregar puntos"""
    
    uid = fields.String(
        required=True,
        validate=validate.Length(min=8, max=20)
    )
    puntos = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=1000)
    )
    tipo_objeto = fields.String(
        load_default='desconocido',
        validate=validate.Length(max=50)
    )
    resultado_ia = fields.String(
        load_default=None,
        validate=validate.Length(max=100)
    )
    confianza_ia = fields.Float(
        load_default=None,
        validate=validate.Range(min=0, max=1)
    )
    imagen_path = fields.String(load_default=None)


class CanjeSchema(Schema):
    """Schema para validación de canje de recompensa"""
    
    usuario_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )
    recompensa_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )


class RecompensaSchema(Schema):
    """Schema para validación de crear recompensa"""
    
    nombre = fields.String(
        required=True,
        validate=validate.Length(min=3, max=100)
    )
    descripcion = fields.String(
        required=True,
        validate=validate.Length(min=10, max=500)
    )
    puntos_requeridos = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=100000)
    )
    stock = fields.Integer(
        load_default=10,
        validate=validate.Range(min=0)
    )
    categoria = fields.String(
        load_default='general',
        validate=validate.Length(max=50)
    )
    imagen_url = fields.URL(
        load_default=None,
        allow_none=True
    )


# Instancias de schemas para uso directo
usuario_schema = UsuarioSchema()
puntos_schema = PuntosSchema()
canje_schema = CanjeSchema()
recompensa_schema = RecompensaSchema()


def validar_datos(schema: Schema, datos: dict) -> tuple:
    """
    Validar datos con un schema de Marshmallow.
    
    Args:
        schema: Instancia del schema a usar
        datos: Diccionario con los datos a validar
    
    Returns:
        tuple: (datos_validados, errores)
    """
    try:
        datos_validados = schema.load(datos)
        return datos_validados, None
    except ValidationError as e:
        return None, e.messages
