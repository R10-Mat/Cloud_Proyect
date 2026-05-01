from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime


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
