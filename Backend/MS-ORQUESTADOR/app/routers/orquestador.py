from typing import List

from fastapi import APIRouter, Depends, status

from app.dependencies import get_orquestador_service
from app.services.orquestador import OrquestadorService
from app.schemas.orquestador import (
    AsignarPedidoRequest,
    AsignarPedidoResponse,
    CompletarPedidoRequest,
    CompletarPedidoResponse,
    ConductorDisponibleResponse,
)

router = APIRouter(prefix="/orquestador", tags=["Orquestador"])


@router.post(
    "/asignar-pedido/",
    response_model=AsignarPedidoResponse,
    status_code=status.HTTP_200_OK,
    summary="Asignar conductor y vehículo a un pedido",
)
async def asignar_pedido(
    data: AsignarPedidoRequest,
    service: OrquestadorService = Depends(get_orquestador_service),
):
    return await service.asignar_pedido(data)


@router.post(
    "/completar-pedido/",
    response_model=CompletarPedidoResponse,
    status_code=status.HTTP_200_OK,
    summary="Marcar pedido como completado y liberar conductor",
)
async def completar_pedido(
    data: CompletarPedidoRequest,
    service: OrquestadorService = Depends(get_orquestador_service),
):
    return await service.completar_pedido(data)


@router.get(
    "/conductores-disponibles/",
    response_model=List[ConductorDisponibleResponse],
    summary="Listar conductores disponibles en MS-FLOTA",
)
async def conductores_disponibles(
    service: OrquestadorService = Depends(get_orquestador_service),
):
    return await service.obtener_conductores_disponibles()
