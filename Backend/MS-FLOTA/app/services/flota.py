from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.flota import Conductor, Vehiculo
from app.schemas.flota import ConductorCreate, ConductorUpdate, VehiculoCreate, VehiculoUpdate


class ConductorService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Conductor]:
        return self.db.query(Conductor).all()

    def get_by_id(self, conductor_id: int) -> Conductor:
        conductor = self.db.query(Conductor).filter(Conductor.id == conductor_id).first()
        if not conductor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conductor con id {conductor_id} no encontrado.",
            )
        return conductor

    def create(self, data: ConductorCreate) -> Conductor:
        if self.db.query(Conductor).filter(Conductor.licencia == data.licencia).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un conductor con la licencia '{data.licencia}'.",
            )
        conductor = Conductor(**data.model_dump())
        self.db.add(conductor)
        self.db.commit()
        self.db.refresh(conductor)
        return conductor

    def update(self, conductor_id: int, data: ConductorUpdate) -> Conductor:
        conductor = self.get_by_id(conductor_id)
        cambios = data.model_dump(exclude_unset=True)
        if "licencia" in cambios and cambios["licencia"] != conductor.licencia:
            if self.db.query(Conductor).filter(Conductor.licencia == cambios["licencia"]).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un conductor con la licencia '{cambios['licencia']}'.",
                )
        for key, value in cambios.items():
            setattr(conductor, key, value)
        self.db.commit()
        self.db.refresh(conductor)
        return conductor

    def delete(self, conductor_id: int) -> None:
        conductor = self.get_by_id(conductor_id)
        self.db.delete(conductor)
        self.db.commit()


class VehiculoService:
    def __init__(self, db: Session):
        self.db = db

    def _validar_conductor(self, conductor_id: int) -> None:
        if not self.db.query(Conductor).filter(Conductor.id == conductor_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe un conductor con id {conductor_id}.",
            )

    def get_all(self) -> list[Vehiculo]:
        return self.db.query(Vehiculo).all()

    def get_by_id(self, vehiculo_id: int) -> Vehiculo:
        vehiculo = self.db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehículo con id {vehiculo_id} no encontrado.",
            )
        return vehiculo

    def create(self, data: VehiculoCreate) -> Vehiculo:
        self._validar_conductor(data.conductor_id)
        vehiculo = Vehiculo(**data.model_dump())
        self.db.add(vehiculo)
        self.db.commit()
        self.db.refresh(vehiculo)
        return vehiculo

    def update(self, vehiculo_id: int, data: VehiculoUpdate) -> Vehiculo:
        vehiculo = self.get_by_id(vehiculo_id)
        cambios = data.model_dump(exclude_unset=True)
        if "conductor_id" in cambios:
            self._validar_conductor(cambios["conductor_id"])
        for key, value in cambios.items():
            setattr(vehiculo, key, value)
        self.db.commit()
        self.db.refresh(vehiculo)
        return vehiculo

    def delete(self, vehiculo_id: int) -> None:
        vehiculo = self.get_by_id(vehiculo_id)
        self.db.delete(vehiculo)
        self.db.commit()
