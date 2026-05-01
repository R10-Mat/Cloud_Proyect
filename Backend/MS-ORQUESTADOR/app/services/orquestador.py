import httpx
import os
from typing import Any

MS_FLOTA_URL = os.getenv("MS_FLOTA_URL", "http://ms_flota_app:8000")
MS_PEDIDOS_URL = os.getenv("MS_PEDIDOS_URL", "http://ms_pedidos_app:8080")
MS_EVENTOS_URL = os.getenv("MS_EVENTOS_URL", "http://ms_eventos_app:3000")

TIMEOUT = httpx.Timeout(10.0)


async def obtener_resumen() -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            r_conductores = await client.get(f"{MS_FLOTA_URL}/flota/conductores/")
            conductores = r_conductores.json() if r_conductores.status_code == 200 else []
        except Exception:
            conductores = []

        try:
            r_pedidos = await client.get(f"{MS_PEDIDOS_URL}/api/pedidos")
            pedidos_data = r_pedidos.json() if r_pedidos.status_code == 200 else []
            if isinstance(pedidos_data, dict):
                pedidos_data = pedidos_data.get("content", pedidos_data.get("pedidos", []))
        except Exception:
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
