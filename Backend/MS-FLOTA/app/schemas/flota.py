from typing import List, Optional
from pydantic import BaseModel


class VehiculoBase(BaseModel):
    placa: str
    marca: str
    capacidad_kg: float
    conductor_id: int


class VehiculoCreate(VehiculoBase):
    pass


class VehiculoUpdate(BaseModel):
    placa: Optional[str] = None
    marca: Optional[str] = None
    capacidad_kg: Optional[float] = None
    conductor_id: Optional[int] = None


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


class ConductorUpdate(BaseModel):
    nombre: Optional[str] = None
    licencia: Optional[str] = None
    telefono: Optional[str] = None
    estado: Optional[str] = None


class ConductorResponse(ConductorBase):
    id: int
    vehiculos: List[VehiculoResponse] = []

    class Config:
        from_attributes = True
