from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum


class EstadoPedido(str, Enum):
    """Espejo del enum EstadoPedido de MS-PEDIDOS (Java)."""
    PENDIENTE = "PENDIENTE"
    ASIGNADO = "ASIGNADO"
    EN_CAMINO = "EN_CAMINO"
    ENTREGADO = "ENTREGADO"
    FALLIDO = "FALLIDO"
    CANCELADO = "CANCELADO"


class ResumenDashboard(BaseModel):
    total_conductores: int
    total_pedidos: int
    fecha_consulta: datetime


class EventoTimeline(BaseModel):
    tipo_evento: str
    timestamp: str
    descripcion: str
    coordenadas: Optional[Any] = None


class DetalleEnvio(BaseModel):
    pedido: dict
    linea_tiempo: List[EventoTimeline]


class ActualizarEstadoRequest(BaseModel):
    """Body esperado por PATCH /dashboard/pedido/{id}/estado."""
    estado: EstadoPedido
    conductor_id: Optional[int] = None
