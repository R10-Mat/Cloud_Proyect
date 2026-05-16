import httpx
import os
import logging
from typing import Any

logger = logging.getLogger("ms-orquestador")

MS_FLOTA_URL = os.getenv("MS_FLOTA_URL", "http://ms_flota_app:8000")
MS_PEDIDOS_URL = os.getenv("MS_PEDIDOS_URL", "http://ms_pedidos_app:8080")
MS_EVENTOS_URL = os.getenv("MS_EVENTOS_URL", "http://ms_eventos_app:3000")

TIMEOUT = httpx.Timeout(80.0)


def _extraer_lista_pedidos(data) -> list:
    """Extrae la lista de pedidos sin importar el formato de respuesta de Spring Boot."""
    # Caso 1: ya es una lista directa → [{ ... }, { ... }]
    if isinstance(data, list):
        return data
    # Caso 2: Spring Boot devolvió un dict paginado o envuelto
    if isinstance(data, dict):
        # Paginación estándar de Spring: {"content": [...], "totalElements": N, ...}
        if "content" in data:
            return data["content"]
        # Posible wrapper personalizado: {"pedidos": [...]}
        if "pedidos" in data:
            return data["pedidos"]
    # Cualquier otro caso → lista vacía
    return []


async def obtener_resumen() -> dict[str, Any]:
    """Obtiene conteos sin cargar todos los registros (usa page=0&size=1)."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # ── Conductores (solo totalElements) ──────────────────────────
        try:
            r_conductores = await client.get(
                f"{MS_FLOTA_URL}/flota/conductores/",
                params={"page": 0, "size": 1},
            )
            r_conductores.raise_for_status()
            data = r_conductores.json()
            total_conductores = data.get("totalElements", 0)
        except Exception as e:
            logger.error("Error consultando MS-FLOTA: %s", e)
            total_conductores = 0

        # ── Pedidos (solo totalElements) ─────────────────────────────
        try:
            r_pedidos = await client.get(
                f"{MS_PEDIDOS_URL}/api/pedidos",
                params={"page": 0, "size": 1},
            )
            r_pedidos.raise_for_status()
            data = r_pedidos.json()
            total_pedidos = data.get("totalElements", 0)
        except Exception as e:
            logger.error("Error consultando MS-PEDIDOS: %s", e)
            total_pedidos = 0

    return {
        "total_conductores": total_conductores,
        "total_pedidos": total_pedidos,
    }


async def obtener_detalle_envio(pedido_id: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r_pedido = await client.get(f"{MS_PEDIDOS_URL}/api/pedidos/{pedido_id}")
            if r_pedido.status_code == 404:
                return None
            pedido = r_pedido.json()
        except Exception:
            pedido = {}

        try:
            r_eventos = await client.get(f"{MS_EVENTOS_URL}/eventos/pedido/{pedido_id}")
            eventos_data = r_eventos.json() if r_eventos.status_code == 200 else {}
            eventos = eventos_data.get("eventos", []) if isinstance(eventos_data, dict) else []
        except Exception:
            eventos = []

    linea_tiempo = [
        {
            "tipo_evento": e.get("tipo_evento"),
            "timestamp": e.get("timestamp"),
            "descripcion": e.get("descripcion"),
            "coordenadas": e.get("coordenadas"),
        }
        for e in eventos
    ]

    return {"pedido": pedido, "linea_tiempo": linea_tiempo}


async def registrar_evento_logistico(pedido_id: int, tipo_evento: str, descripcion: str, conductor_id: int = 0) -> None:
    """Registra un evento en MS-EVENTOS sin interrumpir el flujo principal."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        payload = {
            "pedido_id": pedido_id,
            "conductor_id": conductor_id,
            "tipo_evento": tipo_evento,
            "descripcion": descripcion,
            "coordenadas": {"lat": 0.0, "lng": 0.0}
        }
        try:
            r = await client.post(f"{MS_EVENTOS_URL}/eventos/", json=payload)
            r.raise_for_status()
            logger.info("MS-EVENTOS: Evento registrado para pedido %s", pedido_id)
        except httpx.HTTPStatusError as exc:
            logger.error(
                "MS-EVENTOS respondió %s para pedido %s: %s",
                exc.response.status_code, pedido_id, exc.response.text,
            )
        except Exception as e:
            logger.error("Error de conexión con MS-EVENTOS para pedido %s: %s", pedido_id, e)


async def crear_pedido(datos_pedido: dict) -> dict[str, Any]:
    """Crea un pedido en MS-PEDIDOS y registra el evento inicial."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # 1. Crear el pedido en MS-PEDIDOS
        r_pedido = await client.post(f"{MS_PEDIDOS_URL}/api/pedidos", json=datos_pedido)
        
        # Si falla, lanzamos excepción para que el orquestador retorne error (por ejemplo 400 o 500)
        r_pedido.raise_for_status()
        
        pedido_creado = r_pedido.json()
        pedido_id = pedido_creado.get("id")

        if pedido_id:
            # 2. Registrar el evento logístico (falla de forma segura por el try/except interno)
            await registrar_evento_logistico(
                pedido_id=pedido_id,
                tipo_evento="creado",
                descripcion="Pedido creado desde el Orquestador"
            )

        return pedido_creado


async def actualizar_estado_pedido(pedido_id: int, nuevo_estado: str, conductor_id: int = None) -> dict[str, Any]:
    """Actualiza el estado en MS-PEDIDOS y registra el evento en MS-EVENTOS."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # 1. PATCH a MS-PEDIDOS
        payload: dict[str, Any] = {"estado": nuevo_estado}
        if conductor_id is not None:
            payload["conductorId"] = conductor_id

        r = await client.patch(
            f"{MS_PEDIDOS_URL}/api/pedidos/{pedido_id}/estado",
            json=payload,
        )
        r.raise_for_status()
        pedido_actualizado = r.json()

        # 2. Registrar evento en MS-EVENTOS (en minúsculas para Mongoose)
        await registrar_evento_logistico(
            pedido_id=pedido_id,
            tipo_evento=nuevo_estado.lower(),
            descripcion=f"Estado actualizado a {nuevo_estado}",
            conductor_id=conductor_id or 0,
        )

        return pedido_actualizado


async def procesar_pedidos_bulk(task_id: str, lista_pedidos: list[dict], tareas_estado: dict) -> None:
    """Procesa una lista de pedidos en lote. Se ejecuta como BackgroundTask."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for i, pedido in enumerate(lista_pedidos):
            try:
                r = await client.post(f"{MS_PEDIDOS_URL}/api/pedidos", json=pedido)
                r.raise_for_status()
                pedido_creado = r.json()
                pedido_id = pedido_creado.get("id")
                if pedido_id:
                    await registrar_evento_logistico(
                        pedido_id=pedido_id,
                        tipo_evento="creado",
                        descripcion="Pedido creado (carga masiva)",
                    )
            except Exception as e:
                logger.error("Bulk pedido #%d falló: %s", i, e)
                tareas_estado[task_id]["errores"].append(
                    {"index": i, "error": str(e)}
                )
            tareas_estado[task_id]["procesados"] = i + 1

    tareas_estado[task_id]["estado"] = "completado"
    logger.info("Bulk task %s completada: %d/%d", task_id, tareas_estado[task_id]["procesados"], tareas_estado[task_id]["total"])


# ── Proxy pass-through paginados ────────────────────────────────────────────

async def listar_conductores(page: int = 0, size: int = 20) -> dict:
    """Proxy a MS-FLOTA: conductores paginados."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(
            f"{MS_FLOTA_URL}/flota/conductores/",
            params={"page": page, "size": size},
        )
        r.raise_for_status()
        return r.json()


async def listar_vehiculos(page: int = 0, size: int = 20) -> dict:
    """Proxy a MS-FLOTA: vehículos paginados."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(
            f"{MS_FLOTA_URL}/flota/vehiculos/",
            params={"page": page, "size": size},
        )
        r.raise_for_status()
        return r.json()


async def listar_pedidos(page: int = 0, size: int = 20, estado: str = None) -> dict:
    """Proxy a MS-PEDIDOS: pedidos paginados con filtro opcional por estado."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        params: dict[str, Any] = {"page": page, "size": size}
        if estado:
            params["estado"] = estado
        r = await client.get(
            f"{MS_PEDIDOS_URL}/api/pedidos",
            params=params,
        )
        r.raise_for_status()
        return r.json()

