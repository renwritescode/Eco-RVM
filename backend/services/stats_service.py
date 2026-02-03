"""
Servicio de Estadísticas - Cálculos de Impacto Ambiental
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func
from backend.extensions import db
from backend.models import Usuario, Transaccion
from backend.utils import get_service_logger

logger = get_service_logger()


class StatsService:
    """Servicio para estadísticas e impacto ambiental"""
    
    @staticmethod
    def obtener_estadisticas_generales() -> Dict[str, Any]:
        """Obtener estadísticas generales del sistema"""
        total_usuarios = Usuario.query.filter_by(activo=True).count()
        total_transacciones = Transaccion.query.count()
        total_puntos = db.session.query(
            func.sum(Usuario.puntos_totales)
        ).scalar() or 0
        
        promedio = round(total_puntos / total_usuarios, 2) if total_usuarios > 0 else 0
        
        return {
            'total_usuarios': total_usuarios,
            'total_transacciones': total_transacciones,
            'total_puntos_sistema': total_puntos,
            'promedio_puntos_usuario': promedio
        }
    
    @staticmethod
    def obtener_impacto_ambiental() -> Dict[str, Any]:
        """
        Calcular impacto ambiental total del sistema.
        
        Returns:
            dict con métricas de impacto ambiental
        """
        # Sumar totales de impacto
        resultado = db.session.query(
            func.sum(Transaccion.peso_estimado_kg).label('peso_total'),
            func.sum(Transaccion.co2_evitado_kg).label('co2_total'),
            func.count(Transaccion.id).label('total_reciclajes')
        ).first()
        
        peso_total = resultado.peso_total or 0
        co2_total = resultado.co2_total or 0
        total_reciclajes = resultado.total_reciclajes or 0
        
        # Calcular equivalencias
        # 1 árbol absorbe ~22 kg CO2/año
        arboles_equivalentes = round(co2_total / 22, 2)
        
        # 1 botella plástica requiere ~3 litros de agua para producir
        litros_agua_ahorrados = round(total_reciclajes * 3, 0)
        
        # Energía: ~0.04 kWh por botella reciclada vs nueva
        kwh_ahorrados = round(total_reciclajes * 0.04, 2)
        
        return {
            'peso_reciclado_kg': round(peso_total, 3),
            'co2_evitado_kg': round(co2_total, 3),
            'total_reciclajes': total_reciclajes,
            'equivalencias': {
                'arboles_plantados': arboles_equivalentes,
                'litros_agua_ahorrados': litros_agua_ahorrados,
                'kwh_energia_ahorrada': kwh_ahorrados
            }
        }
    
    @staticmethod
    def obtener_impacto_usuario(usuario_id: int) -> Dict[str, Any]:
        """Calcular impacto ambiental de un usuario específico"""
        resultado = db.session.query(
            func.sum(Transaccion.peso_estimado_kg).label('peso_total'),
            func.sum(Transaccion.co2_evitado_kg).label('co2_total'),
            func.count(Transaccion.id).label('total_reciclajes')
        ).filter(Transaccion.usuario_id == usuario_id).first()
        
        peso_total = resultado.peso_total or 0
        co2_total = resultado.co2_total or 0
        total_reciclajes = resultado.total_reciclajes or 0
        
        # Contar por tipo de objeto
        botellas = Transaccion.query.filter(
            Transaccion.usuario_id == usuario_id,
            Transaccion.tipo_objeto == 'botella_plastico'
        ).count()
        
        latas = Transaccion.query.filter(
            Transaccion.usuario_id == usuario_id,
            Transaccion.tipo_objeto == 'lata_metal'
        ).count()
        
        return {
            'kg_reciclado': round(peso_total, 3),
            'co2_evitado': round(co2_total, 3),
            'total_reciclajes': total_reciclajes,
            'botellas_plastico': botellas,
            'latas_metal': latas
        }
    
    @staticmethod
    def obtener_reciclajes_por_periodo(dias: int = 7) -> Dict[str, int]:
        """
        Obtener cantidad de reciclajes por día en los últimos N días.
        
        Returns:
            dict: {fecha_str: cantidad}
        """
        fecha_inicio = datetime.utcnow() - timedelta(days=dias)
        
        # Agrupar transacciones por fecha
        resultados = db.session.query(
            func.date(Transaccion.fecha_hora).label('fecha'),
            func.count(Transaccion.id).label('cantidad')
        ).filter(
            Transaccion.fecha_hora >= fecha_inicio
        ).group_by(
            func.date(Transaccion.fecha_hora)
        ).all()
        
        # Convertir a diccionario
        datos = {}
        for r in resultados:
            fecha_str = r.fecha.strftime('%Y-%m-%d') if hasattr(r.fecha, 'strftime') else str(r.fecha)
            datos[fecha_str] = r.cantidad
        
        # Rellenar días sin datos
        for i in range(dias):
            fecha = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            if fecha not in datos:
                datos[fecha] = 0
        
        # Ordenar por fecha
        return dict(sorted(datos.items()))
    
    @staticmethod
    def obtener_top_recicladores(limite: int = 5) -> list:
        """Obtener usuarios con más reciclajes en el mes actual"""
        inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        
        resultados = db.session.query(
            Transaccion.usuario_id,
            func.count(Transaccion.id).label('reciclajes'),
            func.sum(Transaccion.puntos_otorgados).label('puntos_mes')
        ).filter(
            Transaccion.fecha_hora >= inicio_mes
        ).group_by(
            Transaccion.usuario_id
        ).order_by(
            func.count(Transaccion.id).desc()
        ).limit(limite).all()
        
        top = []
        for i, r in enumerate(resultados, 1):
            usuario = Usuario.query.get(r.usuario_id)
            if usuario:
                top.append({
                    'posicion': i,
                    'usuario': usuario.to_dict(),
                    'reciclajes_mes': r.reciclajes,
                    'puntos_mes': r.puntos_mes
                })
        
        return top
