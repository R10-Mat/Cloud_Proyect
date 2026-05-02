import httpx
import os
import logging
from typing import Any

logger = logging.getLogger("ms-orquestador")

MS_FLOTA_URL = os.getenv("MS_FLOTA_URL", "http://ms_flota_app:8000")
MS_PEDIDOS_URL = os.getenv("MS_PEDIDOS_URL", "http://ms_pedidos_app:8080")
MS_EVENTOS_URL = os.getenv("MS_EVENTOS_URL", "http://ms_eventos_app:3000")

TIMEOUT = httpx.Timeout(10.0)


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
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # ── Conductores ──────────────────────────────────────────────────
        try:
            r_conductores = await client.get(f"{MS_FLOTA_URL}/flota/conductores/")
            r_conductores.raise_for_status()
            conductores = r_conductores.json()
            if not isinstance(conductores, list):
                logger.warning("MS-FLOTA: respuesta inesperada (no es lista): %s", type(conductores))
                conductores = []
        except Exception as e:
            logger.error("Error consultando MS-FLOTA: %s", e)
            conductores = []

        # ── Pedidos ──────────────────────────────────────────────────────
        try:
            r_pedidos = await client.get(f"{MS_PEDIDOS_URL}/api/pedidos")
            logger.info("MS-PEDIDOS respondió status=%s", r_pedidos.status_code)
            r_pedidos.raise_for_status()
            raw = r_pedidos.json()
            logger.info("MS-PEDIDOS respuesta raw type=%s", type(raw))
            pedidos_data = _extraer_lista_pedidos(raw)
        except Exception as e:
            logger.error("Error consultando MS-PEDIDOS: %s", e)
            pedidos_data = []

    return {
        "total_conductores": len(conductores),
        "total_pedidos": len(pedidos_data),
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
