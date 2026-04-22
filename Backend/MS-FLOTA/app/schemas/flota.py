from typing import List, Optional
from pydantic import BaseModel




class VehiculoBase(BaseModel):
    placa: str
    marca: str
    capacidad_kg: float
    conductor_id: int


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoResponse(VehiculoBase):
    id: int

    class Config:
        from_attributes = True




class ConductorBase(BaseModel):
    nombre: str
    licencia: str
    telefono: str
    estado: Optional[str] = "disponible"


class ConductorCreate(ConductorBase):
    pass


class ConductorResponse(ConductorBase):
    id: int
    vehiculos: List[VehiculoResponse] = []

    class Config:
        from_attributes = True
