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


tareas_estado: dict[str, dict] = {}



@app.get("/")
def root():
    return {"mensaje": "MS-ORQUESTADOR - Last Mile Delivery", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok", "servicio": "ms-orquestador"}



@app.get("/dashboard/resumen")
async def dashboard_resumen():
    datos = await obtener_resumen()
    return {
        "total_conductores": datos["total_conductores"],
        "total_pedidos": datos["total_pedidos"],
        "fecha_consulta": datetime.now(timezone.utc).isoformat(),
    }



@app.get("/dashboard/envio/{pedido_id}")
async def dashboard_envio(pedido_id: int):
    detalle = await obtener_detalle_envio(pedido_id)
    if detalle is None:
        raise HTTPException(status_code=404, detail=f"Pedido {pedido_id} no encontrado")
    return detalle



@app.post("/dashboard/pedido", status_code=201)
async def dashboard_crear_pedido(datos_pedido: dict):
    try:
        resultado = await crear_pedido(datos_pedido)
        return resultado
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error en MS-PEDIDOS: {exc.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/dashboard/pedidos/bulk", status_code=202)
async def dashboard_crear_pedidos_bulk(
    lista_pedidos: list[dict],
    background_tasks: BackgroundTasks,
):
    """
    Acepta una lista de pedidos y los procesa en background.
    Retorna 202 Accepted inmediatamente con un task_id para polling.
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



@app.get("/dashboard/tarea/{task_id}")
async def consultar_tarea(task_id: str):
    """Permite al frontend hacer polling del progreso de una carga masiva."""
    tarea = tareas_estado.get(task_id)
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea



@app.patch("/dashboard/pedido/{pedido_id}/estado")
async def dashboard_actualizar_estado(pedido_id: int, request: ActualizarEstadoRequest):
    """
    Actualiza el estado de un pedido:
    1. PATCH a MS-PEDIDOS
    2. Registra el evento en MS-EVENTOS
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



@app.get("/dashboard/conductores")
async def dashboard_conductores(
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1, le=100),
):
    """Proxy pass-through a MS-FLOTA: conductores paginados."""
    try:
        return await listar_conductores(page, size)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))



@app.get("/dashboard/vehiculos")
async def dashboard_vehiculos(
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1, le=100),
):
    """Proxy pass-through a MS-FLOTA: vehículos paginados."""
    try:
        return await listar_vehiculos(page, size)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))



@app.get("/dashboard/pedidos")
async def dashboard_pedidos(
    page: int = Query(0, ge=0),
    size: int = Query(20, ge=1, le=100),
    estado: str = Query(None),
):
    """Proxy pass-through a MS-PEDIDOS: pedidos paginados."""
    try:
        return await listar_pedidos(page, size, estado)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

