from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.flota import ConductorService, VehiculoService


def get_conductor_service(db: Session = Depends(get_db)) -> ConductorService:
    return ConductorService(db)


def get_vehiculo_service(db: Session = Depends(get_db)) -> VehiculoService:
    return VehiculoService(db)
