from pydantic import BaseModel


class AsignarPedidoRequest(BaseModel):
    pedido_id: int
    conductor_id: int
    vehiculo_id: int


class AsignarPedidoResponse(BaseModel):
    pedido_id: int
    conductor_id: int
    vehiculo_id: int
    estado: str
    mensaje: str


class CompletarPedidoRequest(BaseModel):
    pedido_id: int
    conductor_id: int


class CompletarPedidoResponse(BaseModel):
    pedido_id: int
    conductor_id: int
    estado: str
    mensaje: str


class ConductorDisponibleResponse(BaseModel):
    id: int
    nombre: str
    licencia: str
    telefono: str
    estado: str
