from typing import List

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_conductor_service, get_vehiculo_service
from app.services.flota import ConductorService, VehiculoService
from app.schemas.flota import (
    ConductorCreate,
    ConductorUpdate,
    ConductorResponse,
    PaginatedConductorResponse,
    VehiculoCreate,
    VehiculoUpdate,
    VehiculoResponse,
    PaginatedVehiculoResponse,
)

router = APIRouter(prefix="/flota", tags=["Flota"])



@router.post(
    "/conductores/",
    response_model=ConductorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un conductor",
)
def crear_conductor(
    conductor: ConductorCreate,
    service: ConductorService = Depends(get_conductor_service),
):
    return service.create(conductor)


@router.get(
    "/conductores/",
    response_model=PaginatedConductorResponse,
    summary="Listar conductores (paginado)",
)
def listar_conductores(
    page: int = Query(0, ge=0, description="Número de página (0-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Registros por página"),
    service: ConductorService = Depends(get_conductor_service),
):
    return service.get_all(page, size)


@router.get(
    "/conductores/{conductor_id}",
    response_model=ConductorResponse,
    summary="Obtener un conductor por ID",
)
def obtener_conductor(
    conductor_id: int,
    service: ConductorService = Depends(get_conductor_service),
):
    return service.get_by_id(conductor_id)


@router.patch(
    "/conductores/{conductor_id}",
    response_model=ConductorResponse,
    summary="Actualizar un conductor",
)
def actualizar_conductor(
    conductor_id: int,
    conductor: ConductorUpdate,
    service: ConductorService = Depends(get_conductor_service),
):
    return service.update(conductor_id, conductor)


@router.delete(
    "/conductores/{conductor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un conductor",
)
def eliminar_conductor(
    conductor_id: int,
    service: ConductorService = Depends(get_conductor_service),
):
    service.delete(conductor_id)




@router.post(
    "/vehiculos/",
    response_model=VehiculoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un vehículo",
)
def registrar_vehiculo(
    vehiculo: VehiculoCreate,
    service: VehiculoService = Depends(get_vehiculo_service),
):
    return service.create(vehiculo)


@router.get(
    "/vehiculos/",
    response_model=PaginatedVehiculoResponse,
    summary="Listar vehículos (paginado)",
)
def listar_vehiculos(
    page: int = Query(0, ge=0, description="Número de página (0-indexed)"),
    size: int = Query(20, ge=1, le=100, description="Registros por página"),
    service: VehiculoService = Depends(get_vehiculo_service),
):
    return service.get_all(page, size)


@router.get(
    "/vehiculos/{vehiculo_id}",
    response_model=VehiculoResponse,
    summary="Obtener un vehículo por ID",
)
def obtener_vehiculo(
    vehiculo_id: int,
    service: VehiculoService = Depends(get_vehiculo_service),
):
    return service.get_by_id(vehiculo_id)


@router.patch(
    "/vehiculos/{vehiculo_id}",
    response_model=VehiculoResponse,
    summary="Actualizar un vehículo",
)
def actualizar_vehiculo(
    vehiculo_id: int,
    vehiculo: VehiculoUpdate,
    service: VehiculoService = Depends(get_vehiculo_service),
):
    return service.update(vehiculo_id, vehiculo)


@router.delete(
    "/vehiculos/{vehiculo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un vehículo",
)
def eliminar_vehiculo(
    vehiculo_id: int,
    service: VehiculoService = Depends(get_vehiculo_service),
):
    service.delete(vehiculo_id)
