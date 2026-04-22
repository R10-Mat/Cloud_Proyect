from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.flota import Conductor, Vehiculo
from app.schemas.flota import (
    ConductorCreate,
    ConductorResponse,
    VehiculoCreate,
    VehiculoResponse,
)

router = APIRouter(prefix="/flota", tags=["Flota"])




@router.post(
    "/conductores/",
    response_model=ConductorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un conductor",
)
def crear_conductor(conductor: ConductorCreate, db: Session = Depends(get_db)):
    
    existe = db.query(Conductor).filter(Conductor.licencia == conductor.licencia).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un conductor con la licencia '{conductor.licencia}'.",
        )

    nuevo_conductor = Conductor(**conductor.model_dump())
    db.add(nuevo_conductor)
    db.commit()
    db.refresh(nuevo_conductor)
    return nuevo_conductor


@router.get(
    "/conductores/",
    response_model=List[ConductorResponse],
    summary="Listar todos los conductores",
)
def listar_conductores(db: Session = Depends(get_db)):
    return db.query(Conductor).all()




@router.post(
    "/vehiculos/",
    response_model=VehiculoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un vehículo",
)
def registrar_vehiculo(vehiculo: VehiculoCreate, db: Session = Depends(get_db)):
    
    conductor = db.query(Conductor).filter(Conductor.id == vehiculo.conductor_id).first()
    if not conductor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un conductor con id {vehiculo.conductor_id}.",
        )

    nuevo_vehiculo = Vehiculo(**vehiculo.model_dump())
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo
