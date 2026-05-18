from fastapi import APIRouter, HTTPException
from app.athena_client import ejecutar_query

router = APIRouter(prefix="/analitica", tags=["analitica"])

QUERY_ENTREGAS_POR_MES = """
SELECT
  DATE_FORMAT(fecha_creacion, '%Y-%m') AS mes,
  COUNT(*) AS total_entregas
FROM pedidos
WHERE estado = 'entregado'
GROUP BY DATE_FORMAT(fecha_creacion, '%Y-%m')
ORDER BY mes DESC
LIMIT 12
"""

QUERY_CONDUCTORES_ACTIVIDAD = """
SELECT
  e.conductor_id,
  COUNT(*) AS total_eventos,
  SUM(CASE WHEN e.tipo_evento = 'entregado' THEN 1 ELSE 0 END) AS entregas_exitosas,
  SUM(CASE WHEN e.tipo_evento = 'fallido' THEN 1 ELSE 0 END) AS entregas_fallidas
FROM eventos e
GROUP BY e.conductor_id
ORDER BY total_eventos DESC
LIMIT 20
"""


@router.get(
    "/entregas-por-mes",
    summary="Reportes de entregas por mes",
    description="Obtiene estadísticas de entregas completadas por mes (últimos 12 meses) desde AWS Athena."
)
async def entregas_por_mes():
    """Análisis de entregas por mes.
    
    Ejecuta una consulta en AWS Athena para obtener el total de entregas
    exitosas agrupadas por mes de creación.
    
    Retorna:
    - datos: Lista de registros con mes y total de entregas
    - total_registros: Cantidad de meses con datos
    """
    try:
        resultados = ejecutar_query(QUERY_ENTREGAS_POR_MES)
        return {"datos": resultados, "total_registros": len(resultados)}
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando análisis: {str(e)}")


@router.get(
    "/conductores-actividad",
    summary="Actividad de conductores",
    description="Obtiene métricas de actividad de cada conductor: total eventos, entregas exitosas y fallidas."
)
async def conductores_actividad():
    """Análisis de actividad por conductor.
    
    Ejecuta una consulta en AWS Athena para obtener estadísticas de actividad
    de cada conductor, incluyendo entregas exitosas y fallidas.
    
    Retorna:
    - datos: Lista de conductores con sus estadísticas
    - total_registros: Cantidad de conductores con actividad
    """
    try:
        resultados = ejecutar_query(QUERY_CONDUCTORES_ACTIVIDAD)
        return {"datos": resultados, "total_registros": len(resultados)}
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando análisis: {str(e)}")
