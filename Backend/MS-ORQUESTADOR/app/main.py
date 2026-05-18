import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
import httpx
from datetime import datetime, timezone

from app.schemas import ActualizarEstadoRequest
from app.services.orquestador import (
    obtener_resumen,
    obtener_detalle_envio,
    crear_pedido,
    actualizar_estado_pedido,
    procesar_pedidos_bulk,
    listar_conductores,
    listar_vehiculos,
    listar_pedidos,
)

app = FastAPI(
    title="MS-ORQUESTADOR",
    description="BFF - Orquestador de microservicios Last Mile Delivery",
    version="1.0.0",
)

# ── CORS delegado al API Gateway (no se usa CORSMiddleware) ──────────────────

# ── Estado de tareas en background (in-memory) ──────────────────────────────
tareas_estado: dict[str, dict] = {}


# ── Health / Root ────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"mensaje": "MS-ORQUESTADOR - Last Mile Delivery", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok", "servicio": "ms-orquestador"}


# ── Dashboard: resumen ───────────────────────────────────────────────────────

@app.get(
    "/dashboard/resumen",
    summary="Resumen del dashboard",
    description="Obtiene un resumen general del sistema: total de conductores y pedidos."
)
async def dashboard_resumen():
    """Obtiene el resumen general del sistema.
    
    Retorna:
    - total_conductores: Total de conductores registrados
    - total_pedidos: Total de pedidos en el sistema
    - fecha_consulta: Timestamp de la consulta
    """
    datos = await obtener_resumen()
    return {
        "total_conductores": datos["total_conductores"],
        "total_pedidos": datos["total_pedidos"],
        "fecha_consulta": datetime.now(timezone.utc).isoformat(),
    }


# ── Dashboard: detalle de envío ──────────────────────────────────────────────

@app.get(
    "/dashboard/envio/{pedido_id}",
    summary="Obtener detalle de envío",
    description="Obtiene información completa de un pedido específico incluyendo conductor, vehículo y estado."
)
async def dashboard_envio(pedido_id: int):
    """Obtiene detalles completos de un pedido/envío.
    
    Parámetros:
    - pedido_id: ID del pedido
    
    Retorna:
    - Información completa del pedido con detalles de conductor y vehículo
    """
    detalle = await obtener_detalle_envio(pedido_id)
    if detalle is None:
        raise HTTPException(status_code=404, detail=f"Pedido {pedido_id} no encontrado")
    return detalle


# ── Dashboard: crear pedido (individual) ─────────────────────────────────────

@app.post(
    "/dashboard/pedido",
    status_code=201,
    summary="Crear un nuevo pedido",
    description="Registra un nuevo pedido en el sistema. Coordina con MS-PEDIDOS para la persistencia."
)
async def dashboard_crear_pedido(datos_pedido: dict):
    """Crea un nuevo pedido.
    
    Parámetros:
    - datos_pedido: Datos del pedido a crear
    
    Retorna:
    - Pedido creado con ID asignado
    """
    try:
        resultado = await crear_pedido(datos_pedido)
        return resultado
    except httpx.HTTPStatusError as exc:
        # Re-raise la excepción del backend de pedidos con su mismo código y detalle
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error en MS-PEDIDOS: {exc.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Dashboard: crear pedidos masivamente (bulk) ──────────────────────────────

@app.post(
    "/dashboard/pedidos/bulk",
    status_code=202,
    summary="Crear pedidos en lote",
    description="Procesa múltiples pedidos de manera asincrónica. Retorna inmediatamente con task_id para seguimiento."
)
async def dashboard_crear_pedidos_bulk(
    lista_pedidos: list[dict],
    background_tasks: BackgroundTasks,
):
    """Crea múltiples pedidos en lote de forma asincrónica.
    
    Acepta una lista de pedidos y los procesa en background.
    Retorna 202 Accepted inmediatamente con un task_id para polling.
    
    Parámetros:
    - lista_pedidos: Lista de pedidos a crear
    
    Retorna:
    - task_id: ID para hacer seguimiento del procesamiento
    - total: Cantidad de pedidos a procesar
    """
    task_id = str(uuid.uuid4())
    tareas_estado[task_id] = {
        "estado": "procesando",
        "total": len(lista_pedidos),
        "procesados": 0,
        "errores": [],
    }
    background_tasks.add_task(procesar_pedidos_bulk, task_id, lista_pedidos, tareas_estado)
    return {"task_id": task_id, "mensaje": "Procesamiento iniciado", "total": len(lista_pedidos)}


# ── Dashboard: consultar estado de tarea bulk ────────────────────────────────

@app.get(
    "/dashboard/tarea/{task_id}",
    summary="Consultar estado de tarea",
    description="Consulta el estado del procesamiento de una carga masiva de pedidos."
)
async def consultar_tarea(task_id: str):
    """Permite al frontend hacer polling del progreso de una carga masiva.
    
    Parámetros:
    - task_id: ID de la tarea devuelto al crear pedidos en lote
    
    Retorna:
    - estado: estado actual (procesando, completado, etc)
    - total: total de pedidos
    - procesados: cantidad procesada
    - errores: lista de errores encontrados
    """
    tarea = tareas_estado.get(task_id)
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


# ── Dashboard: actualizar estado de pedido ───────────────────────────────────

@app.patch(
    "/dashboard/pedido/{pedido_id}/estado",
    summary="Actualizar estado de pedido",
    description="Actualiza el estado de un pedido y registra el evento correspondiente."
)
async def dashboard_actualizar_estado(pedido_id: int, request: ActualizarEstadoRequest):
    """Actualiza el estado de un pedido.
    
    Actualiza el estado de un pedido:
    1. PATCH a MS-PEDIDOS
    2. Registra el evento en MS-EVENTOS
    
    Parámetros:
    - pedido_id: ID del pedido
    - request: Nuevo estado y conductor_id
    
    Retorna:
    - Pedido actualizado
    """
    try:
        resultado = await actualizar_estado_pedido(
            pedido_id=pedido_id,
            nuevo_estado=request.estado.value,
            conductor_id=request.conductor_id,
        )
        return resultado
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error en MS-PEDIDOS: {exc.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ── Proxy paginado: conductores ──────────────────────────────────────────────

@app.get(
    "/dashboard/conductores",
    summary="Listar conductores",
    description="Obtiene un listado paginado de conductores desde MS-FLOTA."
)
async def dashboard_conductores(
    page: int = Query(0, ge=0, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Registros por página"),
):
    """Proxy a MS-FLOTA: conductores paginados."""
    try:
        return await listar_conductores(page, size)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Proxy paginado: vehículos ────────────────────────────────────────────────

@app.get(
    "/dashboard/vehiculos",
    summary="Listar vehículos",
    description="Obtiene un listado paginado de vehículos desde MS-FLOTA."
)
async def dashboard_vehiculos(
    page: int = Query(0, ge=0, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Registros por página"),
):
    """Proxy a MS-FLOTA: vehículos paginados."""
    try:
        return await listar_vehiculos(page, size)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Proxy paginado: pedidos ──────────────────────────────────────────────────

@app.get(
    "/dashboard/pedidos",
    summary="Listar pedidos",
    description="Obtiene un listado paginado de pedidos desde MS-PEDIDOS con filtrado opcional por estado."
)
async def dashboard_pedidos(
    page: int = Query(0, ge=0, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Registros por página"),
    estado: str = Query(None, description="Filtrar por estado del pedido"),
):
    """Proxy a MS-PEDIDOS: pedidos paginados."""
    try:
        return await listar_pedidos(page, size, estado)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

